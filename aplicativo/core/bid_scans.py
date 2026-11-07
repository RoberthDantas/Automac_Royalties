"""Resumable public PNCP triage. Matching does not establish eligibility."""
import json,time,urllib.error,urllib.parse
from copy import deepcopy
from datetime import timedelta
from django.utils import timezone
from .models import Signal

CAPABILITIES={
 'ambiental':{'label':'Estudos ambientais e licenciamento','terms':'licenciamento ambiental, estudos ambientais, relatório ambiental, plano de controle ambiental, diagnóstico ambiental, diagnóstico socioambiental, diagnósticos socioambientais, estudo de viabilidade técnica ambiental, monitoramento ambiental, plano de gestão ambiental, planos de gestão ambiental','review':'Conferir equipe multidisciplinar, responsabilidades e escopo antes de participar.'},
 'fundiaria':{'label':'Regularização fundiária e cadastro','terms':'regularização fundiária, regularizacao fundiaria, reurb, cadastro territorial, cadastro imobiliário, cadastro multifinalitário, georreferenciamento rural, sigef','review':'Confirmar atribuições, credenciamento exigido e responsabilidade técnica.'},
 'levantamentos':{'label':'Levantamentos e aerofotogrametria','terms':'topografia, topográficos, topográfico, levantamento planialtimétrico, levantamentos planialtimétricos, aerofotogrametria, aerolevantamento, ortofoto, ortofotos, fotogrametria, gnss','review':'Conferir precisão e equipamentos exigidos. Disponibilidade informada: DJI Air 3 e ALTUS APS-3; não presume RTK no drone, LiDAR ou habilitação.'},
 'geodados':{'label':'Geoprocessamento e cartografia','terms':'geoprocessamento, georreferenciamento, cartografia, cartográfico, cartográficos, sensoriamento remoto, sistema de informação geográfica, sistema de informações geográficas, banco de dados geográficos, sig, webgis, geoportal, base cartográfica','review':'Confirmar volume, formatos, equipe e produtos exigidos.'},
 'planejamento':{'label':'Planejamento territorial e apoio técnico','terms':'plano diretor, planos diretores, mapeamento de risco, erosão costeira, diagnóstico territorial, royalties de petróleo, controle da erosão, controle de erosão, contenção de erosão, processos erosivos','review':'Conferir especialidades complementares e escopo. Não incluir o PMRR de Bayeux em material comercial.'}
}

# 0.5.3: o PNCP responde HTTP 429 quando recebe páginas seguidas sem intervalo. A varredura agora espera entre
# páginas, tenta de novo respeitando o Retry-After da fonte e, se a pausa continuar, encerra a rodada sem consultar
# as demais UFs (que também seriam recusadas). A próxima execução retoma de onde parou.
PAGE_PAUSE_SECONDS=1.5

def rate_limited(exc):
    cause=exc
    while cause is not None:
        if isinstance(cause,urllib.error.HTTPError) and cause.code==429:return True
        cause=cause.__cause__
    return 'HTTP 429' in str(exc)

def default_parameters(profiles=None,ufs=None,pages=40):
    profiles=profiles or list(CAPABILITIES)
    return {'profiles':profiles,'ufs':ufs or ['PB','RN','CE','SE','AL'],'pages':pages,'budget_seconds':300,
        'end_date':(timezone.localdate()+timedelta(days=30)).strftime('%Y%m%d'),'mode':'abertas','progress':{},'method_version':'0.4.0'}

def collect_capabilities(job):
    from .collectors import fetch,pncp_signal,matched_terms,excluded_terms
    p=job.parameters
    profiles=p.get('profiles',list(CAPABILITIES));ufs=p.get('ufs',['PB','RN','CE','SE','AL'])
    if not profiles or any(x not in CAPABILITIES for x in profiles):raise ValueError('Perfil de capacidade inválido.')
    if not ufs or any(x not in ['PB','RN','CE','SE','AL'] for x in ufs):raise ValueError('UF inválida.')
    terms=', '.join(CAPABILITIES[x]['terms'] for x in profiles)
    if p.get('extra_terms'):terms+=', '+p['extra_terms']
    p.setdefault('end_date',(timezone.localdate()+timedelta(days=30)).strftime('%Y%m%d'))
    progress=p.setdefault('progress',{})
    budget=min(max(int(p.get('budget_seconds',300)),10),600);limit=time.monotonic()+budget
    cap=min(max(int(p.get('pages',40)),1),40)
    throttled=False;requests_made=0
    for uf in ufs:
        if throttled:break
        state=progress.setdefault(uf,{'next_page':1,'pages':0,'scanned':0,'new':0,'matches':0,'done':False})
        if state['done']:continue
        state.pop('error',None);state.pop('pause',None)
        pages_this_run=0
        while not state['done']:
            if pages_this_run>=cap or time.monotonic()>=limit:
                state['pause']='Limite de páginas/tempo nesta execução; retomar para continuar.';break
            page=state['next_page']
            params={'uf':uf,'pagina':page,'tamanhoPagina':50,'dataFinal':p['end_date']}
            url='https://pncp.gov.br/api/consulta/v1/contratacoes/proposta?'+urllib.parse.urlencode(params)
            if requests_made:time.sleep(PAGE_PAUSE_SECONDS)
            requests_made+=1
            try:
                raw,snap=fetch(url,job,'json',timeout=min(int(p.get('timeout',20)),20),attempts=3,
                     progress=f'Varredura {uf}, página {page}.')
                data=json.loads(raw) if raw else {'data':[],'totalPaginas':0,'empty':True}
                if not isinstance(data,dict) or not isinstance(data.get('data'),list):raise ValueError('Resposta PNCP inesperada.')
                rows=data['data'];new=matches=0
                for item in rows:
                    hits=matched_terms(item.get('objetoCompra',''),terms)
                    if not hits:continue
                    if excluded_terms(item.get('objetoCompra',''),p.get('exclude_terms','')):
                        state['excluded']=state.get('excluded',0)+1;continue
                    created=pncp_signal(item,job,terms);new+=bool(created);matches+=1
                    signal=Signal.objects.get(external_key='pncp:'+str(item['numeroControlePNCP']))
                    signal.payload.update({'perfis':[CAPABILITIES[x]['label'] for x in profiles if matched_terms(item.get('objetoCompra',''),CAPABILITIES[x]['terms'])],
                        'pagina_snapshot_id':snap.pk if snap else None,'pagina_sha256':snap.sha256 if snap else None,
                        'habilitacao':'Não avaliada; revisar edital, anexos, prazo e requisitos.'})
                    signal.save(update_fields=['payload'])
                state.update(next_page=page+1,pages=state['pages']+1,scanned=state['scanned']+len(rows),new=state['new']+new,matches=state['matches']+matches,
                    done=bool(data.get('empty') or not rows or page>=int(data.get('totalPaginas') or 1)),last_url=url)
                pages_this_run+=1
                job.parameters=p;job.save(update_fields=['parameters'])
            except Exception as exc:
                state['error']=f'{type(exc).__name__}: {str(exc)[:500]}'
                if rate_limited(exc):
                    throttled=True
                    state['pause']='O PNCP pediu pausa (HTTP 429). As UFs seguintes ficam para a próxima execução, que retoma desta página.'
                break
        job.parameters=p;job.save(update_fields=['parameters'])
    partial=any(not progress.get(uf,{}).get('done') for uf in ufs)
    failures=[uf+': '+progress[uf]['error'] for uf in ufs if progress.get(uf,{}).get('error')]
    if failures and not any(progress.get(uf,{}).get('pages') for uf in ufs):
        raise ValueError('Nenhuma UF consultada com sucesso. '+'; '.join(failures))
    summary='; '.join(f"{uf}: {progress.get(uf,{}).get('scanned',0)} examinados, {progress.get(uf,{}).get('matches',0)} correspondências, {progress.get(uf,{}).get('excluded',0)} descartadas pelo filtro, "+('concluído' if progress.get(uf,{}).get('done') else 'pendente/parcial') for uf in ufs)
    pause_note='Rodada encerrada porque o PNCP pediu pausa (HTTP 429); a próxima execução retoma as UFs pendentes. ' if throttled else ''
    return summary+'. Propostas abertas no recorte até '+p['end_date']+'. Correspondência por objeto, sem avaliação de habilitação. Contagens acumuladas no ciclo; paginação da fonte é dinâmica. '+pause_note+('; '.join(failures) if failures else ''),partial
