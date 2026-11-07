"""Auditable discovery: public documents are signals, never automatic sales leads."""
import hashlib
import io
import json
import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import timedelta
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
from django.db import transaction
from django.utils import timezone
from django.utils.dateparse import parse_date, parse_datetime
from .models import Signal, Municipality, WatchedPage, WellProduction

TOPICS = {
 'reurb': ('REURB e fundiário', 'reurb, regularização fundiária, regularizacao fundiaria, titulação, titulação de imóveis, usucapião, retificação de área'),
 'planos': ('Planos diretores', 'plano diretor, planos diretores, revisão do plano diretor, ordenamento territorial, zoneamento urbano'),
 'cadastro': ('Cadastro e geodados', 'cadastro territorial, cadastro imobiliário, cadastro multifinalitário, geoprocessamento, cartografia, georreferenciamento, sigef'),
 'levantamentos': ('Levantamentos', 'topografia, topográfico, topográficos, planialtimétrico, planialtimétricos, aerofotogrametria, aerolevantamento, ortofoto, fotogrametria, batimetria, gnss'),
 'ambiental': ('Ambiental e risco', 'licenciamento ambiental, estudo ambiental, estudos ambientais, relatório ambiental, plano de controle ambiental, erosão, mapeamento de risco, recuperação de áreas degradadas'),
 'royalties': ('Royalties', 'royalties, confrontação, confrontantes, petróleo, geodésia'),
 'privado': ('Expansão e obras', 'loteamento, empreendimento habitacional, condomínio, expansão industrial, incorporação imobiliária'),
}
ALL_TERMS = ', '.join(v[1] for v in TOPICS.values())
QD_BASE = 'https://api.queridodiario.ok.org.br'

def text_only(value):
    return BeautifulSoup(str(value or ''), 'html.parser').get_text(' ', strip=True)

def topics_for(text):
    from .collectors import matched_terms
    return [key for key, (_, terms) in TOPICS.items() if matched_terms(text, terms)]

def publication(value):
    value = str(value or '')
    d = parse_date(value[:10])
    if d: return d
    try: return parsedate_to_datetime(value).date()
    except (ValueError, TypeError, IndexError): return None

def save_signal(key, defaults):
    """Recollection updates last_seen, not the date of a genuinely changed signal."""
    payload = defaults.get('payload', {})
    topics = topics_for(defaults.get('title', '') + ' ' + str(payload.get('trecho') or payload.get('objeto') or ''))
    payload['temas'] = topics
    payload['triagem'] = 'Correspondência textual. Demanda, habilitação e disponibilidade não confirmadas.'
    defaults['payload'] = payload
    defaults['relevance'] = min(95, 20 + len(topics)*12 + (20 if defaults.get('source_type') == 'pncp' else 0))
    defaults['last_seen_at'] = timezone.now()
    obj = Signal.objects.filter(external_key=key).first()
    if obj is None:
        return Signal.objects.create(external_key=key, **defaults), True
    changed = []
    for name, value in defaults.items():
        if getattr(obj, name) != value:
            setattr(obj, name, value); changed.append(name)
    if changed:
        meaningful = set(changed) - {'job','last_seen_at'}
        obj.save(update_fields=changed + (['updated_at'] if meaningful else []))
    return obj, False

def parse_feed(raw, base_url):
    root = ET.fromstring(raw)
    def local(tag): return tag.split('}')[-1]
    if local(root.tag) not in ('rss','feed','RDF'):
        raise ValueError('A fonte não retornou RSS/Atom reconhecido.')
    result = []
    for item in root.iter():
        if local(item.tag) not in ('item','entry'): continue
        values = {}; url = ''
        for child in item:
            tag = local(child.tag)
            values[tag] = ''.join(child.itertext())
            if tag == 'link' and (not child.attrib.get('rel') or child.attrib['rel']=='alternate'):
                url = child.attrib.get('href') or child.text or url
        link = urllib.parse.urljoin(base_url, url.strip())
        if urllib.parse.urlsplit(link).scheme not in ('http','https'): continue
        result.append({'title':text_only(values.get('title')), 'url':link,
            'body':text_only(values.get('description') or values.get('summary') or values.get('content'))[:12000],
            'date':publication(values.get('pubDate') or values.get('published') or values.get('updated'))})
    return result[:200]

def collect_sources(job):
    from .collectors import fetch, matched_terms, html_candidates
    watches = WatchedPage.objects.filter(active=True).order_by('last_checked','pk')
    if job.parameters.get('watch_id'): watches = watches.filter(pk=job.parameters['watch_id'])
    watches = list(watches[:20])
    if not watches: raise ValueError('Nenhuma fonte ativa. Cadastre uma página, feed ou PDF.')
    count = checked = 0; errors = []; limited = False
    until = time.monotonic()+240
    for w in watches:
        if time.monotonic()>until: limited=True; break
        w.last_checked=timezone.now()
        try:
            raw, snap = fetch(w.url,job,w.format,timeout=15,attempts=1,progress=w.title)
            terms = w.keywords or ALL_TERMS
            if w.format=='rss':
                rows=parse_feed(raw,w.url); body=' '.join(r['title']+r['body'] for r in rows)
            elif w.format=='pdf':
                from pypdf import PdfReader
                reader=PdfReader(io.BytesIO(raw))
                body='\n'.join((p.extract_text() or '') for p in reader.pages[:80])
                if not body.strip(): raise ValueError('PDF sem texto extraível; exige leitura/OCR assistido.')
                if len(reader.pages)>80: limited=True
                digest=hashlib.sha256(raw).hexdigest()
                rows=[{'title':w.title,'url':w.url,'body':body[:200000],'date':None,'key':digest}]
            else:
                if raw.startswith(b'%PDF'): raise ValueError('A fonte é PDF. Edite o formato desta fonte.')
                candidates,body=html_candidates(raw,w.url,w.kind,terms)
                rows=[{'title':title,'url':url,'body':title,'date':None} for title,url,_ in candidates]
                if not rows and matched_terms(body,terms):
                    rows=[{'title':w.title+' — conteúdo para revisar','url':w.url,'body':body[:200000],'date':None,
                           'key':hashlib.sha256(body.encode()).hexdigest()}]
            for r in rows:
                matches=matched_terms(r['title']+' '+r['body'],terms)
                if not matches: continue
                digest=hashlib.sha256((r.get('key') or r['url']).encode()).hexdigest()
                key=f'fonte:{w.pk}:{digest}'
                excerpt=r['body'][:4000]
                # Keep the matching passage, rather than an irrelevant start of a long PDF.
                if w.format=='pdf':
                    for term in matches:
                        pos=r['body'].lower().find(term.lower())
                        if pos>=0: excerpt=r['body'][max(0,pos-300):pos+3700]; break
                _,created=save_signal(key,{'title':r['title'][:500], 'kind':w.kind,'municipality':w.municipality,
                    'source_url':r['url'],'source_type':'privada' if w.audience=='privada' else 'pagina',
                    'publication_date':r['date'],'reason':'Fonte monitorada: '+w.title+'. Termos: '+', '.join(matches)+'. Confirmar contexto e possível demanda.',
                    'payload':{'trecho':excerpt,'termos':matches,'pagina_origem':w.url,'formato':w.format,
                               'origem':w.get_audience_display()},'job':job})
                count+=created
            w.last_hash=hashlib.sha256(body.encode()).hexdigest(); w.last_success_at=timezone.now()
            w.last_status='ok'; w.last_error=''; checked+=1
        except Exception as exc:
            w.last_status='error';w.last_error=f'{type(exc).__name__}: {str(exc)[:450]}'
            errors.append(w.title+': '+w.last_error)
        w.save()
    if not checked and errors: raise ValueError('Nenhuma fonte respondeu. '+'; '.join(errors))
    return f'{checked} fontes consultadas; {count} sinais novos. '+('Limite de tempo/páginas atingido. ' if limited else '')+'; '.join(errors),bool(errors or limited)

def collect_diaries(job):
    """Querido Diário is an index, not a guarantee of coverage of 751 municipalities."""
    from .collectors import fetch, UF_CODES
    p=job.parameters; selected=p.get('ufs',list(UF_CODES))
    since=(timezone.localdate()-timedelta(days=14)).isoformat()
    queries=['"regularização fundiária" OR reurb OR "plano diretor"',
             'georreferenciamento OR topografia OR "cadastro imobiliário" OR aerofotogrametria',
             '"licenciamento ambiental" OR "empreendimento habitacional" OR "estudo ambiental"']
    progress=p.setdefault('progress',{}); new=scanned=0; errors=[]; complete=0
    until=time.monotonic()+180
    for i,query in enumerate(queries):
        state=progress.setdefault(str(i),{'offset':0,'done':False})
        if state['done']: complete+=1;continue
        for _ in range(3):
            if time.monotonic()>until: break
            params={'querystring':query,'published_since':p.setdefault('since',since),'published_until':p.setdefault('until',timezone.localdate().isoformat()),
                    'excerpt_size':1500,'number_of_excerpts':2,'size':100,'offset':state['offset'],'sort_by':'descending_date'}
            url=QD_BASE+'/gazettes?'+urllib.parse.urlencode(params)
            try:
                raw,snap=fetch(url,job,'json',timeout=15,attempts=1)
                data=json.loads(raw); rows=data.get('gazettes')
                if not isinstance(rows,list):raise ValueError('Leiaute do índice de diários não reconhecido.')
                for r in rows:
                    code=str(r.get('territory_id') or '')
                    if code[:2] not in [UF_CODES[u] for u in selected]:continue
                    scanned+=1
                    excerpts=r.get('excerpts') or []
                    body=' '.join(text_only(e.get('excerpt') or e.get('text') or '') if isinstance(e,dict) else text_only(e) for e in excerpts)
                    target=r.get('url') or r.get('file_url')
                    if not target or urllib.parse.urlsplit(target).scheme not in ('http','https'):continue
                    date=publication(r.get('date'))
                    topics=topics_for(body)
                    kind='plano' if 'planos' in topics else 'fundiaria' if 'reurb' in topics else 'outro'
                    key='diario:'+hashlib.sha256((str(r.get('id') or target)+query).encode()).hexdigest()
                    _,created=save_signal(key,{'title':f"{r.get('territory_name') or code} · diário de {r.get('date') or 'data não informada'} · {', '.join(TOPICS[x][0] for x in topics) or 'trecho para revisar'}"[:500],
                       'kind':kind,'municipality':Municipality.objects.filter(pk=code).first(),'source_url':target,'source_type':'diario',
                       'publication_date':date,'reason':'Trecho indexado pelo Querido Diário. Conferir a edição original: publicação não comprova contratação aberta.',
                       'payload':{'trecho':body[:5000],'indexador':QD_BASE,'query':query,'original_url':r.get('original_url'),'edicao':r.get('edition'),'uf':r.get('state_code')},'job':job})
                    new+=created
                state['offset']+=len(rows)
                state['done']=not rows or len(rows)<100 or state['offset']>=int(data.get('total_gazettes') or data.get('total') or 10**9)
                job.parameters=p;job.save(update_fields=['parameters'])
                if state['done']:complete+=1;break
            except Exception as exc:errors.append(str(exc)[:300]);break
    if not scanned and errors:raise ValueError('Índice de diários indisponível; cobertura não verificada. '+'; '.join(errors))
    return f'{scanned} edições no recorte PB/RN/CE/SE/AL; {new} sinais novos. {complete}/3 consultas concluídas. Cobertura depende dos municípios indexados. '+'; '.join(errors),bool(errors or complete<3)

def collect_production_url(job):
    from collections import Counter
    from .models import Well
    from .collectors import fetch, validate_remote
    from .wells import parse_production
    url=job.parameters.get('url',''); environment=job.parameters.get('environment','Terra')
    validate_remote(url)
    raw,snap=fetch(url,job,'csv',timeout=30,attempts=1)
    rows,outside=parse_production(raw,environment)
    counts=Counter(Well.objects.values_list('uf','name_key'))
    environments={(w.uf,w.name_key):w.environment for w in Well.objects.only('uf','name_key','environment') if counts[(w.uf,w.name_key)]==1}
    for row in rows:
        registered=environments.get((row['uf'],row['name_key']))
        if registered in ('Terra','Mar') and registered!=row['environment']:
            raise ValueError('Ambiente diverge do cadastro ANP; confira a seleção Terra/Mar. Arquivo preservado.')
    unmatched=sum(counts[(r['uf'],r['name_key'])]!=1 for r in rows)
    added=0
    with transaction.atomic():
        for r in rows:
            key={k:r[k] for k in ('uf','name_key','period')}
            old=WellProduction.objects.filter(**key).first()
            if old and old.environment != r['environment']: raise ValueError('Ambiente divergente da série existente; arquivo preservado para revisão.')
            _,created=WellProduction.objects.update_or_create(**key,defaults={**{k:v for k,v in r.items() if k not in key},'snapshot':snap})
            added+=created
    return f'{len(rows)} registros validados; {added} novos; {outside} fora das UFs selecionadas; {unmatched} sem vínculo único com o cadastro. CSV da URL configurada; leiaute e duplicidades validados.',bool(unmatched)
