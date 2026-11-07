"""Read-only public-source collectors. Never send prospecting messages."""
import gzip
import hashlib
import http.client
import io
import ipaddress
import json
import re
import socket
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from email.utils import parsedate_to_datetime
from pathlib import Path
from bs4 import BeautifulSoup
from openpyxl import load_workbook
from django.conf import settings
from django.db import transaction, close_old_connections
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from .models import Municipality, CollectionJob, Snapshot, Royalty, Signal, WatchedPage
from .anp_aliases import ANP_ALIASES

ANP_URL='https://www.gov.br/anp/pt-br/assuntos/royalties-e-outras-participacoes/royalties'
TJPB_URL='https://selodigital.tjpb.jus.br/selocgj/paginas/publico/consultarServentias.jsf'
UF_CODES={'PB':'25','RN':'24','CE':'23','SE':'28','AL':'27'}
MAX_BYTES=25*1024*1024
DEFAULT_TERMS='georreferenciamento, regularização fundiária, reurb, topografia, levantamento planialtimétrico, aerofotogrametria, ortofoto, cadastro territorial, plano diretor, cartografia, geodésia, erosão costeira, redução de riscos, batimetria, sensoriamento remoto, sistema de informação geográfica, assistência técnica pericial, royalties'

def normalize(value):
    return ' '.join(re.sub(r'[^a-z0-9 ]',' ',unicodedata.normalize('NFKD',str(value)).encode('ascii','ignore').decode().lower()).split())

def validate_remote(url):
    p=urllib.parse.urlsplit(url)
    if p.scheme not in ('https','http') or not p.hostname or p.username or p.password:
        raise ValueError('Use uma URL pública HTTP ou HTTPS sem credenciais.')
    if p.port not in (None,80,443):raise ValueError('Porta não permitida para coleta pública.')
    host=p.hostname.lower()
    if host in ('localhost','localhost.localdomain') or host.endswith(('.local','.internal')):
        raise ValueError('Endereço local não permitido.')
    for result in socket.getaddrinfo(host,p.port or (443 if p.scheme=='https' else 80),type=socket.SOCK_STREAM):
        if not ipaddress.ip_address(result[4][0]).is_global:
            raise ValueError('A fonte precisa estar na internet pública.')
    return url

class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        validate_remote(newurl)
        return super().redirect_request(req,fp,code,msg,headers,newurl)

class FetchUnavailable(RuntimeError):
    """A public source did not respond after bounded retries."""

def network_retryable(exc):
    if isinstance(exc,urllib.error.HTTPError):
        return exc.code in (408,429,500,502,503,504)
    if isinstance(exc,urllib.error.URLError):
        return network_retryable(exc.reason)
    return isinstance(exc,(TimeoutError,ConnectionError,http.client.IncompleteRead))

def collection_progress(job,text):
    job.summary=text
    job.save(update_fields=['summary'])

def fetch(url,job,extension='bin',*,timeout=35,attempts=3,progress=''):
    validate_remote(url)
    opener=urllib.request.build_opener(PublicRedirect())
    req=urllib.request.Request(url,headers={'User-Agent':'CartoGeoLocal/0.4 (public data research)', 'Accept-Encoding':'gzip'})
    started_at=timezone.now().isoformat()
    for attempt in range(attempts):
        if progress:
            collection_progress(job,f'{progress} Tentativa {attempt+1}/{attempts}; aguardando a fonte (limite de inatividade: {timeout}s).')
        try:
            with opener.open(req,timeout=timeout) as response:
                response_status=response.status
                response_url=response.geturl()
                response_headers={k:response.headers.get(k) for k in ('Content-Type','Content-Encoding','Date','ETag','Last-Modified') if response.headers.get(k)}
                raw=response.read(MAX_BYTES+1)
            break
        except (urllib.error.URLError,TimeoutError,ConnectionError,http.client.IncompleteRead) as exc:
            if not network_retryable(exc):raise
            detail=f'HTTP {exc.code}' if isinstance(exc,urllib.error.HTTPError) else type(exc).__name__
            if attempt+1>=attempts:
                raise FetchUnavailable(f'{progress or "Consulta"} Sem resposta completa após {attempts} tentativas ({detail}). URL: {url}') from exc
            delay=3*(attempt+1)
            # Honour the source's requested pause; never retry earlier.
            retry_after=exc.headers.get('Retry-After') if isinstance(exc,urllib.error.HTTPError) and exc.headers else None
            if retry_after:
                try:delay=max(delay,int(retry_after))
                except ValueError:
                    try:delay=max(delay,parsedate_to_datetime(retry_after).timestamp()-time.time())
                    except (ValueError,TypeError,OverflowError):pass
            if delay>60:
                raise FetchUnavailable(f'{progress or "Consulta"} A fonte solicitou uma pausa de {int(delay)}s. Tente novamente depois desse intervalo. URL: {url}') from exc
            if progress:collection_progress(job,f'{progress} Resposta interrompida ({detail}); nova tentativa em {int(delay)}s.')
            time.sleep(delay)
    if len(raw)>MAX_BYTES:raise ValueError('Arquivo excede o limite de 25 MB por resposta.')
    received_body=raw
    received_at=timezone.now().isoformat()
    if raw[:2]==b'\x1f\x8b':
        with gzip.GzipFile(fileobj=io.BytesIO(raw)) as f:raw=f.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('Conteúdo descompactado excede 25 MB.')
    sha=hashlib.sha256(raw).hexdigest()
    path=settings.DATA_DIR/'fontes'/str(job.pk)
    path.mkdir(parents=True,exist_ok=True)
    body_sha=hashlib.sha256(received_body).hexdigest()
    body_name=body_sha+'.http-body'
    (path/body_name).write_bytes(received_body)
    if raw is received_body or raw==received_body:
        # 0.4.2: sem compressão, o conteúdo é idêntico ao corpo recebido; grava uma única cópia.
        filename=body_name
    else:
        filename=f'{sha[:20]}.{extension}'
        (path/filename).write_bytes(raw)
    provenance={'requested_url':url,'final_url':response_url,'status':response_status,'headers':response_headers,
                'started_at_utc':started_at,'received_at_utc':received_at,'clock':'relógio local, sem carimbo de tempo confiável',
                'received_body_file':body_name,'received_body_sha256':body_sha,'received_body_size':len(received_body),
                'transformation':'gzip descompactado' if received_body[:2]==b'\x1f\x8b' else 'sem transformação',
                'scope':'corpo HTTP recebido, não inclui sessão TLS nem cabeçalhos brutos', 'collector_version':settings.VERSION}
    snap=Snapshot.objects.create(job=job,url=url,filename=filename,sha256=sha,size=len(raw),provenance=provenance)
    return raw,snap

def collect_ibge(job):
    states=job.parameters.get('ufs',list(UF_CODES))
    results=[]
    for uf in states:
        url=f'https://servicodados.ibge.gov.br/api/v1/localidades/estados/{UF_CODES[uf]}/municipios'
        raw,_=fetch(url,job,'json')
        rows=json.loads(raw)
        if not isinstance(rows,list) or not rows:raise ValueError(f'IBGE: resposta vazia ou inesperada para {uf}.')
        with transaction.atomic():
            for r in rows:
                code=str(r['id'])
                if len(code)!=7 or not code.startswith(UF_CODES[uf]):raise ValueError('Código municipal incompatível com a UF solicitada.')
                Municipality.objects.update_or_create(code=code,defaults={'name':r['nome'],'uf':uf,'source_url':url})
        results.append(f'{uf}: {len(rows)} municípios')
    return '; '.join(results)+'. Cadastros oficiais, sem contatos comerciais inventados.',False

def money(value):
    if value is None or value=='':raise ValueError('Valor ausente; não substituído por zero.')
    if isinstance(value,bool):raise ValueError('Valor monetário inválido.')
    text=str(value).strip().replace('R$','').replace(' ','').replace('\xa0','')
    if ',' in text:text=text.replace('.','').replace(',','.')
    try:result=Decimal(text)
    except InvalidOperation as exc:raise ValueError(f'Número inválido: {text[:40]}') from exc
    if not result.is_finite():raise ValueError('Número não finito.')
    return result.quantize(Decimal('.01'))

def parse_anp_xlsx(raw,year,municipalities,*,alias_audit=None):
    """Validated annual TOTAL sheet. Never sums TOTAL with CONCESSAO/PARTILHA."""
    book=load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    try:
        candidates=[n for n in book.sheetnames if normalize(n)=='total']
        if len(candidates)!=1:raise ValueError('Leiaute ANP não reconhecido: exige uma aba TOTAL. Arquivo preservado para revisão.')
        rows=list(book[candidates[0]].iter_rows(values_only=True))
        header=next((r for r in rows[:25] if any('royalties ate 5' in normalize(c) for c in r)),None)
        if header is None or len(header)<38:raise ValueError('Colunas ANP não reconhecidas.')
        text=' '.join(str(c) for r in rows[:6] for c in r if c is not None)
        if str(year) not in text:raise ValueError('Ano solicitado não coincide com o cabeçalho da ANP.')
        for month in range(1,13):
            start=2+(month-1)*3
            if 'royalties ate 5' not in normalize(header[start]) or 'excedentes' not in normalize(header[start+1]):
                raise ValueError('A ordem das colunas ANP mudou; importação interrompida.')
        control=next((r for r in rows[:20] if len(r)>2 and normalize(r[1])=='municipios'),None)
        if control is None:raise ValueError('Linha nacional de controle de publicação não encontrada.')
        months=[m for m in range(1,13) if control[2+(m-1)*3+2] is not None and money(control[2+(m-1)*3+2])!=0 and date(year,m,1)<=date.today()]
        if not months:raise ValueError('Nenhum mês com distribuição publicada foi identificado.')
        output=[];unmatched=[];seen=set()
        for r in rows:
            if len(r)<38 or not isinstance(r[1],str):continue
            uf=str(r[0] or '').strip().upper()
            if uf not in UF_CODES or not r[1].strip().upper().endswith('-'+uf):continue
            key=(uf,normalize(r[1].strip()[:-3]))
            mun=municipalities.get(key)
            if not mun and key in ANP_ALIASES:
                code,current_name=ANP_ALIASES[key]
                if municipalities.get((uf,normalize(current_name)))==code:
                    mun=code
                    if alias_audit is not None:
                        alias_audit.append(f'{r[1]} → {current_name}/{uf} (IBGE {code})')
            if not mun:
                unmatched.append(r[1]);continue
            if mun in seen:raise ValueError(f'Município duplicado na origem: {r[1]}')
            seen.add(mun)
            for month in months:
                start=2+(month-1)*3
                low,high,total=[money(v) for v in r[start:start+3]]
                if abs(low+high-total)>Decimal('.02'):
                    raise ValueError(f'Total inconsistente para {r[1]}, mês {month}. Nenhum valor deste arquivo foi gravado.')
                output.append({'municipality_id':mun,'year':year,'month':month,'minimum':low,'excess':high,'total':total})
        if not output:raise ValueError('Nenhum município conciliado. Carregue primeiro os municípios do IBGE.')
        return output,months,unmatched
    finally:book.close()

def collect_anp(job):
    year=int(job.parameters.get('year',date.today().year))
    if not Municipality.objects.exists():raise ValueError('Carregue primeiro os municípios pelo IBGE.')
    raw,_=fetch(ANP_URL,job,'html')
    soup=BeautifulSoup(raw,'html.parser')
    core=soup.select_one('#content-core') or soup
    urls=[]
    for a in core.select('a[href]'):
        url=urllib.parse.urljoin(ANP_URL,a['href'])
        if 'tabelas-contendo-o-valor-mensal-dos-royalties-dos-beneficiarios' in url and str(year) in url and 'educacao' not in url:
            if url.lower().endswith(('.xlsx','.zip')) and url not in urls:urls.append(url)
    if not urls:raise ValueError(f'Tabela de {year} não encontrada na página oficial. A fonte pode ter mudado.')
    url=urls[0]
    payload,snap=fetch(url,job,'zip' if url.endswith('.zip') else 'xlsx')
    mapping={(m.uf,normalize(m.name)):m.pk for m in Municipality.objects.all()}
    alias_audit=[];member_note=''
    if url.endswith('.zip'):
        # 0.4.2: pacotes anuais (2022, 2024, 2025) trazem várias planilhas. Testa cada uma com a mesma validação
        # rigorosa e usa a única que corresponder ao leiaute municipal. Nada é gravado se nenhuma validar.
        with zipfile.ZipFile(io.BytesIO(payload)) as z:
            members=[f for f in z.infolist() if f.filename.lower().endswith('.xlsx') and f.file_size<=MAX_BYTES and 'educa' not in normalize(f.filename)]
            if not members:raise ValueError('Pacote ANP sem planilhas .xlsx utilizáveis. Fonte preservada para revisão.')
            valid=[];failures=[]
            for member in members:
                try:
                    audit=[]
                    result=parse_anp_xlsx(z.read(member),year,mapping,alias_audit=audit)
                    valid.append((member.filename,result,audit))
                except Exception as exc:failures.append(f'{member.filename}: {str(exc)[:120]}')
            if len(valid)!=1:
                raise ValueError(('Nenhuma' if not valid else 'Mais de uma')+' planilha do pacote corresponde ao leiaute municipal. Fonte preservada. Detalhes: '+'; '.join(failures[:6]+[v[0] for v in valid]))
            member_name,(records,months,unmatched),alias_audit=valid[0]
            member_note=f'Planilha usada do pacote: {member_name}. '
    else:
        records,months,unmatched=parse_anp_xlsx(payload,year,mapping,alias_audit=alias_audit)
    added=changed=0
    # Validate entire file above, then commit atomically. Source snapshots retain previous versions.
    with transaction.atomic():
        for r in records:
            key={k:r[k] for k in ('municipality_id','year','month')}
            defaults={k:r[k] for k in ('minimum','excess','total')}
            defaults.update(source_url=url,snapshot=snap)
            _,created=Royalty.objects.update_or_create(**key,defaults=defaults)
            added+=created;changed+=not created
    summary=member_note+f'{year}: {len(records)} valores mensais; {added} novos e {changed} atualizados. Meses publicados: {", ".join(map(str,months))}. {len(unmatched)} nomes não conciliados. Escopo PB/RN/CE/SE/AL. Participação especial não incluída. '
    if unmatched:summary+='Conferir: '+', '.join(unmatched[:15])+'. '
    if alias_audit:summary+=f'{len(alias_audit)} denominações conciliadas por correspondência explícita: '+'; '.join(alias_audit)+'.'
    return summary,bool(unmatched)

# 0.4.2: objetos que citam termos técnicos, mas são compra de bens ou software — fora do escopo de serviços da CartoGeo.
EXCLUDE_TERMS=('aquisicao de equipamento','aquisicao de equipamentos','aquisicao de instrumento','aquisicao de instrumentos',
 'aquisicao de aparelho','aquisicao de aparelhos','aquisicao de material','aquisicao de materiais','aquisicao de veiculo','aquisicao de veiculos',
 'aquisicao de drone','aquisicao de drones','aquisicao de estacao total','aquisicao de receptor','aquisicao de receptores',
 'aquisicao de software','aquisicao de licenca','aquisicao de computador','aquisicao de computadores','aquisicao de mobiliario',
 'fornecimento de equipamento','fornecimento de equipamentos','fornecimento de material','fornecimento de materiais',
 'locacao de software','licenca de uso','licencas de uso','frota','abastecimento de combustivel','rastreamento veicular',
 'material de consumo','material permanente','generos alimenticios','locacao de veiculo','locacao de veiculos')

def excluded_terms(text,extra=''):
    value=' '+normalize(text)+' '
    terms=list(EXCLUDE_TERMS)+[normalize(t) for t in str(extra or '').split(',') if t.strip()]
    return [t for t in terms if t and ' '+t+' ' in value]

def matched_terms(text,terms):
    value=' '+normalize(text)+' '
    return [term.strip() for term in terms.split(',') if term.strip() and ' '+normalize(term)+' ' in value]

def pncp_signal(item,job,terms):
    description=item.get('objetoCompra') or ''
    matches=matched_terms(description,terms)
    if not matches:return False
    if excluded_terms(description):return False
    key=item.get('numeroControlePNCP')
    if not key:raise ValueError('PNCP retornou contratação sem identificador.')
    org=item.get('orgaoEntidade') or {};unit=item.get('unidadeOrgao') or {}
    cnpj=re.sub(r'\D','',str(org.get('cnpj') or ''))
    seq=item.get('sequencialCompra');year=item.get('anoCompra')
    url=f'https://pncp.gov.br/app/editais/{cnpj}/{year}/{seq}' if cnpj and seq and year else 'https://pncp.gov.br/app/editais'
    deadline=parse_datetime(str(item.get('dataEncerramentoProposta') or ''))
    if deadline and timezone.is_naive(deadline):deadline=timezone.make_aware(deadline)
    code=str(unit.get('codigoIbge') or '')
    mun=Municipality.objects.filter(pk=code).first()
    payload={'objeto':description,'orgao':org.get('razaoSocial'),'cnpj':cnpj,'unidade':unit,
             'valor_estimado':item.get('valorTotalEstimado'),'publicado_em':item.get('dataPublicacaoPncp'),
             'modalidade':item.get('modalidadeNome'),'situacao':item.get('situacaoCompraNome'),'termos':matches,
             'link_sistema_origem':item.get('linkSistemaOrigem')}
    defaults={'title':description[:500],'kind':'edital','source_url':url,'reason':'Termos encontrados no objeto: '+', '.join(matches)+'. Conferir edital, itens, habilitação e prazo antes de abordar ou participar.',
              'payload':payload,'municipality':mun,'deadline':deadline,'job':job}
    from .intelligence import save_signal, publication
    defaults.update(source_type='pncp', publication_date=publication(item.get('dataPublicacaoPncp')))
    _,created=save_signal('pncp:'+str(key),defaults)
    return created

def collect_pncp(job):
    p=job.parameters;uf=p.get('uf','PB');mode=p.get('mode','abertas');terms=p.get('terms',DEFAULT_TERMS)
    cap=min(int(p.get('pages',10)),40);pages=0;scanned=found=0;partial=False
    modalities=[None] if mode=='abertas' else [4,6,8,9,10,12]
    for modality in modalities:
        page=1
        while True:
            if pages>=cap:partial=True;break
            params={'uf':uf,'pagina':page,'tamanhoPagina':50}
            if mode=='abertas':
                endpoint='proposta';params['dataFinal']=(date.today()+timedelta(days=30)).strftime('%Y%m%d')
            else:
                endpoint='publicacao';params.update(dataInicial=(date.today()-timedelta(days=7)).strftime('%Y%m%d'),dataFinal=date.today().strftime('%Y%m%d'),codigoModalidadeContratacao=modality)
            url='https://pncp.gov.br/api/consulta/v1/contratacoes/'+endpoint+'?'+urllib.parse.urlencode(params)
            context=f'PNCP {uf}: página {page}'+(f', modalidade {modality}' if modality else '')+'.'
            context+=f' Concluídas: {pages} páginas, {scanned} publicações examinadas, {found} sinais novos.'
            raw,_=fetch(url,job,'json',timeout=60,attempts=3,progress=context);pages+=1
            if not raw:break
            data=json.loads(raw)
            if not isinstance(data,dict) or not isinstance(data.get('data'),list):raise ValueError('Formato da resposta PNCP inesperado.')
            rows=data['data'];scanned+=len(rows)
            for item in rows:found+=bool(pncp_signal(item,job,terms))
            if data.get('empty') or not rows or page>=int(data.get('totalPaginas') or 1):break
            page+=1
            time.sleep(.2)
        if partial:break
    text=f'{uf}: {pages} páginas, {scanned} publicações examinadas, {found} sinais novos. '
    text+='Consulta de propostas abertas, horizonte de 30 dias.' if mode=='abertas' else 'Publicações dos últimos 7 dias; modalidades 4, 6, 8, 9, 10 e 12.'
    if partial:text+=' COLETA PARCIAL: limite de páginas atingido; aumente o limite ou reduza o recorte. Não representa cobertura integral.'
    return text,partial

def html_candidates(raw,url,kind,terms):
    soup=BeautifulSoup(raw,'html.parser')
    for el in soup(['script','style','nav','header','footer']):el.decompose()
    found=[];seen=set()
    for a in soup.select('a[href]'):
        text=a.get_text(' ',strip=True)
        matches=matched_terms(text,terms)
        link=urllib.parse.urljoin(url,a['href'])
        if matches and link.startswith(('https://','http://')) and link not in seen:
            seen.add(link);found.append((text,link,matches))
    return found[:150],soup.get_text(' ',strip=True)

def collect_watches(job):
    watches=WatchedPage.objects.filter(active=True)
    if job.parameters.get('watch_id'):watches=watches.filter(pk=job.parameters['watch_id'])
    if not watches.exists():raise ValueError('Cadastre uma página oficial em Fontes monitoradas.')
    added=checked=0;errors=[]
    for w in watches:
        try:
            raw,_=fetch(w.url,job,'html')
            if raw.startswith(b'%PDF'):raise ValueError('Cadastre a página de publicações, não o PDF. A leitura jurídica do PDF é assistida.')
            rows,body=html_candidates(raw,w.url,w.kind,w.keywords)
            for title,url,matches in rows:
                key='pagina:'+hashlib.sha256((str(w.pk)+url).encode()).hexdigest()
                _,created=Signal.objects.update_or_create(external_key=key,defaults={'title':title[:500],'kind':w.kind,'municipality':w.municipality,'source_url':url,
                   'reason':'Publicação encontrada por termos: '+', '.join(matches)+'. Requer leitura e confirmação do conteúdo.',
                   'payload':{'pagina_origem':w.url,'termos':matches},'job':job})
                added+=created
            digest=hashlib.sha256(body.encode()).hexdigest()
            if not rows and digest!=w.last_hash and matched_terms(body,w.keywords):
                _,created=Signal.objects.get_or_create(external_key='pagina-corpo:'+hashlib.sha256((str(w.pk)+digest).encode()).hexdigest(),defaults={
                    'title':w.title+' — conteúdo para revisar','kind':w.kind,'municipality':w.municipality,'source_url':w.url,
                    'reason':'A página contém termos de interesse. Conferir manualmente; não foi identificada lei ou prazo automaticamente.',
                    'payload':{'trecho':body[:3000]},'job':job})
                added+=created
            w.last_hash=digest;w.last_checked=timezone.now();w.save();checked+=1
        except Exception as exc:errors.append(f'{w.title}: {type(exc).__name__}: {str(exc)[:200]}')
    return f'{checked} páginas consultadas; {added} sinais novos. '+('Falhas: '+'; '.join(errors) if errors else 'Páginas dinâmicas ou protegidas podem exigir consulta assistida.'),bool(errors)

from .wells import collect_wells,collect_wells_reference
from .bid_scans import collect_capabilities
from .intelligence import collect_sources, collect_diaries, collect_production_url
from .prospect import collect_anp_series
COLLECTORS={'anp_serie':collect_anp_series,'diarios':collect_diaries,'producao_url':collect_production_url,'pncp_capacidades':collect_capabilities,'ibge':collect_ibge,'anp':collect_anp,'pncp':collect_pncp,'paginas':collect_sources,'pocos':collect_wells,'pocos_referencia':collect_wells_reference}

def execute_job(job_id):
    close_old_connections()
    job=CollectionJob.objects.get(pk=job_id)
    job.status='running';job.summary='Coleta iniciada. Dados externos sujeitos à disponibilidade da fonte.';job.save()
    try:
        summary,partial=COLLECTORS[job.source](job)
        job.status='partial' if partial else 'ok';job.summary=summary
    except Exception as exc:
        job.status='error'
        job.summary=f'{type(exc).__name__}: {str(exc)[:1200]}. Os dados válidos anteriores foram preservados; etapas concluídas antes da falha podem permanecer registradas. Consulte as fontes desta execução.'
    finally:
        job.finished_at=timezone.now();job.save();close_old_connections()

def _start_job(source,parameters):
    import subprocess,sys,os
    # One collector process per application. A failed/restarted process is visible, never silently marked successful.
    if CollectionJob.objects.filter(status__in=['queued','running']).exists():
        raise ValueError('Já há uma coleta em andamento. Aguarde terminar; se ela travou, feche e abra o app (02_ABRIR.bat) que a execução interrompida é encerrada sozinha.')
    job=CollectionJob.objects.create(source=source,parameters=parameters)
    log_dir=settings.DATA_DIR/'logs';log_dir.mkdir(exist_ok=True)
    env=os.environ.copy();env['CARTOGEO_DATA_DIR']=str(settings.DATA_DIR)
    try:
        with (log_dir/f'coleta-{job.pk}.log').open('ab') as log:
            subprocess.Popen([sys.executable,str(settings.BASE_DIR/'manage.py'),'collect_job',str(job.pk)],cwd=settings.BASE_DIR,env=env,stdout=log,stderr=log,
                             creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    except Exception:
        job.status='error';job.summary='Não foi possível iniciar o processo local de coleta.';job.save();raise
    return job


def start_job(source, parameters):
    from launch import local_lock
    if source not in COLLECTORS: raise ValueError('Coleta não reconhecida.')
    try: guard=local_lock('dispatch.lock')
    except SystemExit: raise ValueError('Outra solicitação está iniciando uma coleta. Tente novamente.')
    try: return _start_job(source,parameters)
    finally: guard.close()
