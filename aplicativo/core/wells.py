"""Official ANP well registry and assisted production CSV ingestion."""
import csv
import hashlib
import io
import json
import math
import re
import urllib.parse
import zipfile
from collections import Counter
from datetime import date
from decimal import Decimal, InvalidOperation
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from .models import Well, WellProduction, Snapshot, CollectionJob

WFS_URL='https://gishub.anp.gov.br/geoserver/ows'
PRODUCTION_URL='https://cdp.anp.gov.br/ords/r/cdp_apex/consulta-dados-publicos-cdp/consulta-produ%C3%A7%C3%A3o-por-po%C3%A7o'
PRODUCTION_PAGE='https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/producao-de-petroleo-e-gas-natural-por-poco'
UF_NAMES={'PB':'Paraíba','RN':'Rio Grande do Norte','CE':'Ceará','SE':'Sergipe','AL':'Alagoas'}

def well_key(value):
    return re.sub(r'[^A-Z0-9]','',str(value).upper())

def wfs_url(start):
    params={'service':'WFS','version':'2.0.0','request':'GetFeature','typeNames':'BD_ANP:POCOS_SIRGAS',
            'count':5000,'startIndex':start,'sortBy':'OGR_FID A','srsName':'EPSG:4326',
            'outputFormat':'application/json','CQL_FILTER':"ESTADO IN ('PB','RN','CE','SE','AL')"}
    return WFS_URL+'?'+urllib.parse.urlencode(params)

def parse_wells(raw):
    data=json.loads(raw)
    if data.get('type')!='FeatureCollection' or not isinstance(data.get('features'),list):
        raise ValueError('Resposta ANP não é uma coleção geográfica reconhecida.')
    crs=data.get('crs',{}).get('properties',{}).get('name','')
    if crs not in ('urn:ogc:def:crs:EPSG::4326','EPSG:4326'):
        raise ValueError('A fonte não confirmou coordenadas WGS84/EPSG:4326. Importação interrompida.')
    total=data.get('numberMatched')
    if isinstance(total,bool) or not isinstance(total,int) or total<0 or total>100000:
        raise ValueError('Contagem de poços ausente ou fora do limite esperado.')
    if data.get('numberReturned')!=len(data['features']):raise ValueError('Contagem da página geográfica inconsistente.')
    records=[]
    for feature in data['features']:
        p=feature.get('properties',{})
        required=('CADASTRO','POCO','ESTADO','TERRA_MAR','SITUACAO')
        if not all(k in p for k in required):raise ValueError('O leiaute do cadastro ANP mudou.')
        reg=str(p.get('CADASTRO') or '').strip();name=str(p.get('POCO') or '').strip();uf=str(p.get('ESTADO') or '').strip()
        if not reg or not name or uf not in UF_NAMES:raise ValueError('Poço sem identificação ou fora das UFs solicitadas.')
        lon=lat=None;geometry=feature.get('geometry')
        if geometry is not None:
            if geometry.get('type')!='Point':raise ValueError('Geometria de poço diferente de ponto.')
            coords=geometry.get('coordinates',[])
            if len(coords)<2 or any(isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) for v in coords[:2]):
                raise ValueError('Coordenadas inválidas na fonte ANP.')
            lon,lat=coords[:2]
            if not (-180<=lon<=180 and -90<=lat<=90):raise ValueError('Coordenadas fora dos limites geográficos.')
        identity=hashlib.sha256((uf+'\0'+reg+'\0'+well_key(name)).encode()).hexdigest()
        records.append(dict(source_id=identity,registration=reg,name=name,name_key=well_key(name),uf=uf,
             operator=str(p.get('OPERADOR') or '').strip(),basin=str(p.get('BACIA') or '').strip(),
             field=str(p.get('CAMPO') or '').strip(),environment={'T':'Terra','M':'Mar'}.get(p.get('TERRA_MAR'),str(p.get('TERRA_MAR') or '')),
             situation=str(p.get('SITUACAO') or '').strip(),longitude=lon,latitude=lat,
             original_datum=str(p.get('DATUM_HORI') or '').strip(),properties=p))
    return records,total

def reference_page(job,start):
    with zipfile.ZipFile(settings.BASE_DIR/'referencias'/'pocos_anp_20260918.zip') as package:
        manifest=json.loads(package.read('manifest.json'))
        info=manifest['pages'][str(start)]
        raw=package.read(info['filename'])
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=info['sha256']:raise ValueError('Arquivo de referência alterado ou incompleto.')
    folder=settings.DATA_DIR/'fontes'/str(job.pk);folder.mkdir(parents=True,exist_ok=True)
    filename=digest[:20]+'.geojson';(folder/filename).write_bytes(raw)
    snap=Snapshot.objects.create(job=job,url=info['url'],filename=filename,sha256=digest,size=len(raw))
    return raw,snap

def collect_wells(job,reference=False):
    from .collectors import fetch,collection_progress
    staged=[];seen=set();expected=None;start=0
    while True:
        if reference:
            collection_progress(job,f'Importando base ANP verificada em 18/09/2026: {start} registros lidos.')
            raw,snapshot=reference_page(job,start)
        else:raw,snapshot=fetch(wfs_url(start),job,'geojson',timeout=60,progress=f'Poços ANP: {start} registros recebidos.')
        rows,total=parse_wells(raw)
        if expected is None:expected=total
        if expected!=total:raise ValueError('A contagem da fonte mudou durante a coleta. Repita para obter um conjunto consistente.')
        if not rows and start<total:raise ValueError('A fonte encerrou a paginação antes do total anunciado.')
        for row in rows:
            if row['source_id'] in seen:raise ValueError('Mesmo poço repetido entre páginas; atualização cancelada.')
            seen.add(row['source_id']);row['snapshot']=snapshot;staged.append(row)
        start+=len(rows)
        if start>=total:break
    if start!=expected or not staged:raise ValueError('Quantidade recebida não corresponde ao cadastro anunciado; base anterior preservada.')
    collection_progress(job,f'Validando e gravando {len(staged)} poços. Aguarde.')
    # The entire collection validates before any existing registry record is updated.
    with transaction.atomic():
        existing=set(Well.objects.filter(pk__in=seen).values_list('pk',flat=True))
        stamp=timezone.now()
        objects=[Well(**r,updated_at=stamp) for r in staged]
        fields=[f.name for f in Well._meta.fields if not f.primary_key]
        Well.objects.bulk_create(objects,update_conflicts=True,unique_fields=['source_id'],update_fields=fields,batch_size=300)
    counts=Counter(r['uf'] for r in staged)
    no_location=sum(r['longitude'] is None for r in staged)
    stale=Well.objects.exclude(pk__in=seen).count()
    duplicated=[reg for reg,n in Counter(r['registration'] for r in staged).items() if n>1]
    summary=f'{len(staged)} poços; {len(seen-existing)} novos e {len(existing)} atualizados. '+ '; '.join(f'{uf}: {counts[uf]}' for uf in UF_NAMES)
    if reference:summary='Base de referência ANP verificada em 18/09/2026. '+summary
    summary+=f'. {no_location} sem coordenadas. Cadastro e situação conforme ANP; produção mensal não incluída nesta coleta.'
    if stale:summary+=f' {stale} registros anteriores não apareceram nesta coleta e foram preservados; consulte a data da fonte.'
    if duplicated:summary+=f' Conferência: {len(duplicated)} números de cadastro aparecem em mais de um poço na fonte; registros preservados separadamente pelo nome e UF. Cadastros: '+', '.join(duplicated[:15])+'.'
    return summary,bool(no_location or stale or duplicated)

def collect_wells_reference(job):
    # Do not overwrite a newer online registry with the bundled historical copy.
    if Well.objects.exists():raise ValueError('A base de referência destina-se à primeira carga. Já existem poços; use a atualização online para preservar a versão mais recente.')
    return collect_wells(job,reference=True)

def decimal_value(value,label):
    text=str(value or '').strip().replace('\xa0','').replace(' ','')
    if not text:return None
    if ',' in text:text=text.replace('.','').replace(',','.')
    try:number=Decimal(text)
    except InvalidOperation as e:raise ValueError(f'Número inválido em {label}: {text[:40]}') from e
    if not number.is_finite() or number<0 or number>=Decimal('1e16') or number.as_tuple().exponent < -8:
        raise ValueError(f'Valor fora dos limites em {label}. Nenhum valor foi arredondado ou substituído por zero.')
    return number

def parse_production(raw,environment):
    from .collectors import normalize
    if environment not in ('Terra','Mar','Pré-sal'):raise ValueError('Escolha o ambiente consultado no CDP.')
    try:text=raw.decode('utf-8-sig')
    except UnicodeDecodeError:text=raw.decode('cp1252')
    if '\x00' in text:raise ValueError('Use CSV UTF-8 ou Windows-1252; não envie XLSX ou UTF-16.')
    rows=list(csv.reader(io.StringIO(text),delimiter=';' if text[:20000].count(';')>text[:20000].count('\t') else '\t'))
    # APEX also offers comma-delimited CSV with quoted Brazilian decimal values.
    if rows and max(len(r) for r in rows[:10])<3:rows=list(csv.reader(io.StringIO(text),delimiter=','))
    needed=['nome poco anp','estado','periodo','petroleo bbl dia','gas natural mm3 dia total']
    header_index=None
    for i,row in enumerate(rows[:10]):
        names=[normalize(c) for c in row]
        if all(n in names for n in needed):header_index=i;break
    if header_index is None:
        raise ValueError('Cabeçalho não reconhecido. Esperado: Nome Poço ANP, Estado, Período, Petróleo (bbl/dia), Gás Natural (Mm³/dia) Total. Preserve o CSV original e envie-o para adaptação do leiaute.')
    headers=rows[header_index];normalized=[normalize(c) for c in headers]
    if len(normalized)!=len(set(normalized)):raise ValueError('CSV com cabeçalhos duplicados; requer revisão.')
    positions={n:normalized.index(n) for n in needed}
    states={normalize(v):k for k,v in UF_NAMES.items()};states.update({k.lower():k for k in UF_NAMES})
    national=['Acre','Alagoas','Amapá','Amazonas','Bahia','Ceará','Distrito Federal','Espírito Santo','Goiás','Maranhão','Mato Grosso','Mato Grosso do Sul','Minas Gerais','Pará','Paraíba','Paraná','Pernambuco','Piauí','Rio de Janeiro','Rio Grande do Norte','Rio Grande do Sul','Rondônia','Roraima','Santa Catarina','São Paulo','Sergipe','Tocantins']
    known={normalize(x) for x in national}|set('ac al ap am ba ce df es go ma mt ms mg pa pb pr pe pi rj rn rs ro rr sc sp se to'.split())
    result=[];seen=set();outside=0
    for line,row in enumerate(rows[header_index+1:],header_index+2):
        if not row or not any(c.strip() for c in row):continue
        if len(row)!=len(headers):raise ValueError(f'Linha {line}: quantidade de colunas inconsistente.')
        values={n:row[pos].strip() for n,pos in positions.items()}
        state=normalize(values['estado'])
        if state not in known:raise ValueError(f'Linha {line}: estado não reconhecido: {values["estado"]}.')
        if state not in states:outside+=1;continue
        uf=states[state];name=values['nome poco anp'];key=well_key(name)
        if not key:raise ValueError(f'Linha {line}: nome do poço ausente.')
        period=values['periodo']
        match=re.fullmatch(r'(\d{4})[/-](\d{1,2})',period)
        if match:year,month=map(int,match.groups())
        else:
            match=re.fullmatch(r'(\d{1,2})[/-](\d{4})',period)
            if not match:raise ValueError(f'Linha {line}: período não reconhecido: {period}.')
            month,year=map(int,match.groups())
        try:period=date(year,month,1)
        except ValueError as e:raise ValueError(f'Linha {line}: mês inválido.') from e
        if year<2005 or period>date.today():raise ValueError(f'Linha {line}: período fora da série histórica esperada.')
        identity=(uf,key,period)
        if identity in seen:raise ValueError(f'Linha {line}: poço e mês duplicados no CSV. Requer conferência, sem somar linhas automaticamente.')
        seen.add(identity)
        result.append(dict(name=name,name_key=key,uf=uf,period=period,environment='Mar' if environment=='Pré-sal' else environment,
            petroleum=decimal_value(values['petroleo bbl dia'],'Petróleo (bbl/dia)'),
            gas=decimal_value(values['gas natural mm3 dia total'],'Gás Natural (Mm³/dia) Total'),raw=dict(zip(headers,row))))
    if not result:raise ValueError('Nenhuma linha de produção de PB/RN/CE/SE/AL encontrada.')
    return result,outside

def import_production(raw,filename,environment):
    job=CollectionJob.objects.create(source='producao_pocos',status='running',parameters={'ambiente':environment,'arquivo':filename})
    # Preserve the original even when the parser cannot recognise the header.
    digest=hashlib.sha256(raw).hexdigest();folder=settings.DATA_DIR/'fontes'/str(job.pk);folder.mkdir(parents=True,exist_ok=True)
    stored=digest[:20]+'.csv';(folder/stored).write_bytes(raw)
    snapshot=Snapshot.objects.create(job=job,url=PRODUCTION_URL,filename=stored,sha256=digest,size=len(raw))
    try:
        rows,outside=parse_production(raw,environment)
        counts=Counter(Well.objects.values_list('uf','name_key'))
        environments={(w.uf,w.name_key):w.environment for w in Well.objects.only('uf','name_key','environment') if counts[(w.uf,w.name_key)]==1}
        for row in rows:
            registered=environments.get((row['uf'],row['name_key']))
            if registered in ('Terra','Mar') and registered!=row['environment']:
                raise ValueError(f'Ambiente escolhido diverge do cadastro ANP para {row["name"]}: cadastrado em {registered}. Confira o CSV e a seleção Terra/Mar.')
        unmatched=sum(counts[(r['uf'],r['name_key'])]!=1 for r in rows)
        added=updated=0
        with transaction.atomic():
            for r in rows:
                identity={k:r[k] for k in ('uf','name_key','period')}
                old=WellProduction.objects.filter(**identity).first()
                if environment=='Pré-sal' and old:
                    if old.petroleum!=r['petroleum'] or old.gas!=r['gas']:
                        raise ValueError('Pré-sal diverge de produção já importada para o mesmo poço/mês. Revise as fontes; nada foi sobrescrito.')
                    continue
                defaults={k:v for k,v in r.items() if k not in identity};defaults['snapshot']=snapshot
                _,created=WellProduction.objects.update_or_create(**identity,defaults=defaults)
                added+=created;updated+=not created
        job.status='partial' if unmatched else 'ok'
        job.summary=f'{len(rows)} linhas no escopo; {added} novas e {updated} atualizadas; {outside} linhas de outras UFs ignoradas. {unmatched} linhas sem vínculo único com o cadastro de poços. Petróleo em bbl/dia; gás com o rótulo original ANP Mm³/dia. Arquivo fornecido pelo usuário como exportação do CDP.'
    except Exception as exc:
        job.status='error';job.summary=f'{exc} Arquivo original preservado; produção anterior mantida.'
    finally:
        job.finished_at=timezone.now();job.save()
    return job
