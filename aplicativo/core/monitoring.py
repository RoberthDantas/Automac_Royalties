"""Local state and evidence exports. No connection to ChatGPT or automatic transmission."""
import hashlib,json,zipfile,uuid
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from .models import InternalPlan,Opportunity,CollectionJob,Snapshot,CollectionSchedule,WatchedPage,SchedulerState


def json_bytes(obj):
    return json.dumps(obj,ensure_ascii=False,indent=2,cls=DjangoJSONEncoder).encode('utf-8')

def state_report(context='Estado da instalação que gerou este arquivo'):
    today=timezone.localdate()
    plans=[]
    for p in InternalPlan.objects.select_related('municipality','signal').order_by('pk'):
        plans.append({'id':p.pk,'title':p.title,'stage':p.status,'stage_label':p.get_status_display(),'category':p.category,
            'municipality':str(p.municipality) if p.municipality else None,'owner':p.owner,'next_action':p.next_action,
            'due_date':p.due_date,'overdue':bool(p.due_date and p.due_date<today and p.status not in ['concluido','suspenso']),
            'blockers':p.blockers,'notes':p.notes,'updated_at':p.updated_at,'source':p.signal.source_url if p.signal else None,
            'history':list(p.history.values('author','changes','created_at'))})
    opportunities=[{'id':o.pk,'title':o.title,'stage':o.stage,'stage_label':o.get_stage_display(),'front':o.front,
        'owner':o.owner,'next_action':o.next_action,'due_date':o.next_date,'blockers':o.blockers,
        'overdue':bool(o.next_date and o.next_date<today and o.stage not in ['concluida','suspensa','perdida']),
        'updated_at':o.updated_at} for o in Opportunity.objects.order_by('pk')]
    jobs=list(CollectionJob.objects.order_by('-pk')[:30].values('id','source','status','parameters','summary','created_at','finished_at'))
    return {'schema':'cartogeo.acompanhamento.v1','generated_at_utc':timezone.now(),'version':settings.VERSION,'context':context,
        'plans':plans,'opportunities':opportunities,'recent_jobs':jobs,
        'schedules':list(CollectionSchedule.objects.values('name','source','enabled','frequency','next_run','last_run','last_job_id')),
        'watched_sources':list(WatchedPage.objects.values('title','url','active','last_status','last_error','last_success_at')),
        'scheduler':list(SchedulerState.objects.values()),
        'limits':['Não há conexão automática com ChatGPT. Anexar este pacote ao chat para análise.',
                  'Histórico e relógio locais, sem assinatura ou carimbo de tempo confiável.',
                  'O resumo lista até 30 coletas; o dossiê inclui todas as coletas e fontes disponíveis.']}

def report_markdown(report):
    lines=['# CartoGeo acompanhamento',f"Versão {report['version']} | Gerado {report['generated_at_utc']}",report['context'],
        'Uso interno. Anexar ao chat para que o assistente analise o estado atualizado.',
        'Regras: decisões comerciais com a direção; sem mapas em peças comerciais; não reconstruir o método das ortogonais.',
        '\n## Tarefas internas']
    for p in report['plans']:
        lines += [f"- #{p['id']} {p['title']} | {p['stage_label']} | {p['owner']} | prazo {p['due_date'] or 'não definido'}"+(' | ATRASADA' if p['overdue'] else ''),
            '  Próxima: '+p['next_action'],'  Pendências: '+(p['blockers'] or 'não registradas')]
    lines+=['\n## Oportunidades']
    for p in report['opportunities']:
        lines += [f"- #{p['id']} {p['title']} | {p['stage_label']} | prazo {p['due_date'] or 'não definido'}",
            '  Próxima: '+p['next_action'],'  Pendências: '+(p['blockers'] or 'não registradas')]
    lines+=['\n## Últimas coletas']
    for j in report['recent_jobs']:lines.append(f"- #{j['id']} {j['source']} | {j['status']} | {j['summary']}")
    lines+=['\n## Rotinas recorrentes']
    for s in report.get('schedules',[]):lines.append(f"- {s['name']} | ativa: {s['enabled']} | próxima: {s['next_run']} | última: {s['last_run']}")
    lines+=['\n## Cobertura das fontes']
    for s in report.get('watched_sources',[]):lines.append(f"- {s['title']} | {s['last_status']} | último sucesso: {s['last_success_at']} | {s['last_error']}")
    lines+=['\n## Instrução para retomar','Analisar tarefas vencidas, pendências e falhas. Executar apenas o trabalho interno autorizado. Registrar resultados e propor a próxima ação. Não interpretar falha de consulta como ausência de editais.']
    return '\n'.join(lines)


def build_bundle(evidence=False,context='Estado da instalação que gerou este arquivo'):
    report=state_report(context);folder=settings.DATA_DIR/('dossies' if evidence else 'acompanhamento');folder.mkdir(exist_ok=True)
    stamp=timezone.now().strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
    path=folder/(('dossie-' if evidence else 'acompanhamento-')+stamp+'.zip')
    manifest={'schema':'cartogeo.manifesto.v1','generated_at_utc':str(timezone.now()),'app_version':settings.VERSION,
              'purpose':'Rastreabilidade interna; não é autenticação notarial, assinatura digital ou prova jurídica conclusiva.',
              'context':context,'files':[]}
    try:
        with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as z:
            def add(name,data,origin=None):
                z.writestr(name,data);manifest['files'].append({'path':name,'size':len(data),'sha256':hashlib.sha256(data).hexdigest(),'origin':origin})
            def add_file(name,file,origin=None,expected=None):
                digest=hashlib.sha256()
                with file.open('rb') as f:
                    while chunk:=f.read(1024*1024):digest.update(chunk)
                sha=digest.hexdigest()
                if expected and sha!=expected:raise ValueError('Hash divergente na fonte '+name+'. Preserve o arquivo e investigue antes de gerar o dossiê.')
                z.write(file,name);manifest['files'].append({'path':name,'size':file.stat().st_size,'sha256':sha,'origin':origin})
            add('ACOMPANHAMENTO.md',report_markdown(report).encode('utf-8'))
            add('ESTADO.json',json_bytes(report))
            add_file('verificar_pacote.py',settings.BASE_DIR/'scripts/verificar_pacote.py')
            if evidence:
                add('COLETAS.json',json_bytes(list(CollectionJob.objects.order_by('pk').values())))
                index=[];included=set()
                for snap in Snapshot.objects.select_related('job').order_by('pk'):
                    base=settings.DATA_DIR/'fontes'/str(snap.job_id)
                    entries=[(snap.filename,snap.sha256)]
                    if snap.provenance.get('received_body_file'):entries.append((snap.provenance['received_body_file'],snap.provenance['received_body_sha256']))
                    for filename,expected in entries:
                        if Path(filename).name!=filename:raise ValueError('Nome de fonte inválido.')
                        file=base/filename
                        if not file.is_file():raise ValueError(f'Arquivo original ausente: coleta {snap.job_id}, {filename}.')
                        name=f'fontes/{snap.job_id}/{filename}'
                        if name not in included:add_file(name,file,{'url':snap.url,'snapshot':snap.pk},expected);included.add(name)
                    index.append({'id':snap.pk,'job':snap.job_id,'source':snap.job.source,'url':snap.url,'filename':snap.filename,'sha256':snap.sha256,
                        'recorded_at':snap.created_at,'provenance':snap.provenance or {'note':'Metadados HTTP e corpo codificado não capturados nesta versão histórica; registro não retroativamente autenticado.'}})
                add('INDICE_FONTES.json',json_bytes(index))
                for sub in ('referencias','documentacao'):
                    for file in sorted((settings.BASE_DIR/sub).rglob('*')):
                        if file.is_file() and not file.is_symlink():add_file(file.relative_to(settings.BASE_DIR).as_posix(),file,{'type':'referência distribuída; verificar metadados específicos, sem atribuir data original pelo empacotamento'})
                for file in sorted((settings.BASE_DIR/'core').rglob('*.py')):
                    if '__pycache__' not in file.parts:add_file('codigo/'+file.relative_to(settings.BASE_DIR).as_posix(),file)
                for name in ['municipios_ibge.geojson','linhas_lbr.geojson']:
                    add_file('derivados/'+name,settings.STATIC_ROOT/name,{'type':'camada de visualização derivada, uso interno'})
            raw=json_bytes(manifest);z.writestr('MANIFESTO.json',raw)
            z.writestr('MANIFESTO.sha256',hashlib.sha256(raw).hexdigest()+'  MANIFESTO.json\n')
        # Sidecar fingerprint can be anchored independently by the reviewer.
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        path.with_suffix('.zip.sha256').write_text(digest+'  '+path.name+'\n',encoding='utf-8')
        return path
    except Exception:
        path.unlink(missing_ok=True);raise
