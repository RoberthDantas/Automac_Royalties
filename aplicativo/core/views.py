import csv
import hashlib
import io
import json
import re
from datetime import date,timedelta
from decimal import Decimal
from pathlib import Path
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Q,Sum,Count,Max
from django.http import HttpResponse,FileResponse,Http404
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import *
from .forms import *
from .collectors import start_job,TJPB_URL,ANP_URL

def page(request,qs,n=30):return Paginator(qs,n).get_page(request.GET.get('page'))

@login_required
def dashboard(request):
    today=timezone.localdate();month=today.replace(day=1)
    active=Opportunity.objects.exclude(stage__in=['perdida','concluida','suspensa'])
    received=CashEntry.objects.filter(status='realizada',received_date__gte=month,received_date__lte=today)
    gross=received.exclude(kind='despesa').aggregate(n=Sum('amount'))['n'] or Decimal(0)
    expenses=received.filter(kind='despesa').aggregate(n=Sum('amount'))['n'] or Decimal(0)
    return render(request,'core/dashboard.html',{'title':'Sua central de inteligência.',
       'signals':Signal.objects.filter(status='novo').count(),'active_count':active.count(),
       'tasks':active.filter(next_date__lte=today).select_related('organization')[:12],
       # 0.5.3: o painel mostrava len(tasks), limitado às 12 linhas exibidas; o total real vem da contagem.
       'tasks_total':active.filter(next_date__lte=today).count(),
       'no_date':active.filter(next_date=None).count(),'upcoming':active.filter(next_date__gt=today).select_related('organization')[:6],
       'net':gross-expenses,'gross':gross,'expenses':expenses,'today':today,
       'has_base':Municipality.objects.exists(),'jobs':CollectionJob.objects.all()[:5],
       'notary_count':Organization.objects.filter(kind='cartorio').count(),
       'new_today':Signal.objects.filter(collected_at__gte=timezone.now()-timedelta(hours=24)).count(),
       'closing':Signal.objects.filter(status='novo',deadline__gte=timezone.now(),deadline__lte=timezone.now()+timedelta(days=7)).count(),
       'latest_signals':Signal.objects.filter(status='novo').select_related('municipality').order_by('-collected_at')[:5],
       'internal_tasks':InternalPlan.objects.exclude(status__in=['concluido','suspenso']).order_by('due_date')[:5],
       'schedules':CollectionSchedule.objects.filter(enabled=True).order_by('next_run')[:4],
       'prospect':__import__('core.commercial',fromlist=['quarter_metrics']).quarter_metrics(today),
       'hot_pending':Opportunity.objects.filter(front='royalties',stage='identificada').count()})

@login_required
def listing(request,entity):
    if entity not in EDITORS:raise Http404
    model,_,label=EDITORS[entity]
    qs=model.objects.all();q=request.GET.get('q','').strip()
    if entity=='organizacoes':
        qs=qs.select_related('municipality')
        if q:qs=qs.filter(Q(name__icontains=q)|Q(municipality__name__icontains=q))
    elif entity=='contatos':
        qs=qs.select_related('organization')
        if q:qs=qs.filter(Q(name__icontains=q)|Q(organization__name__icontains=q)|Q(email__icontains=q))
    elif entity=='oportunidades':
        qs=qs.select_related('organization')
        if q:qs=qs.filter(Q(title__icontains=q)|Q(organization__name__icontains=q))
        if request.GET.get('front'):qs=qs.filter(front=request.GET['front'])
        if request.GET.get('stage'):qs=qs.filter(stage=request.GET['stage'])
    elif entity=='planos':
        qs=qs.select_related('municipality')
        if q:qs=qs.filter(municipality__name__icontains=q)
    elif entity=='financeiro':
        qs=qs.select_related('opportunity')
        if q:qs=qs.filter(Q(description__icontains=q)|Q(opportunity__title__icontains=q))
    elif entity=='paginas' and q:qs=qs.filter(title__icontains=q)
    titles={'organizacoes':'Organizações','contatos':'Contatos','oportunidades':'Oportunidades','planos':'Planos diretores','financeiro':'Recebimentos e despesas','paginas':'Páginas monitoradas'}
    return render(request,'core/list.html',{'title':titles[entity],'entity':entity,'records':page(request,qs),'q':q,'fronts':FRONTS,'stages':STAGES,'label':label,'today':date.today()})

@login_required
def edit(request,entity,pk=None):
    if entity not in EDITORS:raise Http404
    model,form_class,label=EDITORS[entity]
    obj=get_object_or_404(model,pk=pk) if pk else None
    initial={}
    for field in ('organization','opportunity','municipality'):
        if request.GET.get(field):initial[field]=request.GET[field]
    form=form_class(request.POST or None,instance=obj,initial=initial)
    if request.method=='POST' and form.is_valid():
        with transaction.atomic():
            saved=form.save()
            if entity=='oportunidades':
                Activity.objects.create(opportunity=saved,kind='sistema',author=request.user.username,text=('Criada oportunidade.' if not pk else 'Campos alterados: '+', '.join(form.fields[x].label or x for x in form.changed_data)))
        messages.success(request,'Registro salvo.')
        return redirect('opportunity_detail',pk=saved.pk) if entity=='oportunidades' else redirect('listing',entity=entity)
    return render(request,'core/form.html',{'title':('Editar ' if pk else 'Cadastrar ')+label.lower(),'form':form,'back':f'/{entity}/',
                  'delete_url':f'/{entity}/{pk}/excluir/' if pk else ''})

@login_required
def opportunity_detail(request,pk):
    obj=get_object_or_404(Opportunity.objects.select_related('organization','signal'),pk=pk)
    return render(request,'core/opportunity.html',{'title':obj.title,'o':obj,'activity_form':ActivityForm(),'attachment_form':AttachmentForm()})

@login_required
@require_POST
def add_activity(request,pk):
    obj=get_object_or_404(Opportunity,pk=pk);form=ActivityForm(request.POST)
    if form.is_valid():
        a=form.save(commit=False);a.opportunity=obj;a.author=request.user.username;a.save()
        from .commercial import apply_followup
        changes=apply_followup(a)
        messages.success(request,'Histórico atualizado.'+(' Cadência: '+'; '.join(changes)+'.' if changes else ''))
    else:messages.error(request,'Informe o tipo e o texto do registro.')
    return redirect('opportunity_detail',pk=pk)

@login_required
@require_POST
def add_attachment(request,pk):
    obj=get_object_or_404(Opportunity,pk=pk);form=AttachmentForm(request.POST,request.FILES)
    if form.is_valid():
        a=form.save(commit=False);a.opportunity=obj;a.save();messages.success(request,'Documento associado à oportunidade.')
    else:messages.error(request,str(form.errors.as_text()))
    return redirect('opportunity_detail',pk=pk)

@login_required
def attachment_download(request,pk):
    obj=get_object_or_404(Attachment,pk=pk)
    return FileResponse(obj.file.open('rb'),as_attachment=True,filename=obj.title+Path(obj.file.name).suffix)

@login_required
def signals(request):
    qs=Signal.objects.select_related('municipality').all()
    state=request.GET.get('status','novo')
    if state:qs=qs.filter(status=state)
    if request.GET.get('kind'):qs=qs.filter(kind=request.GET['kind'])
    q=request.GET.get('q','').strip()
    if q:qs=qs.filter(Q(title__icontains=q)|Q(reason__icontains=q))
    return render(request,'core/signals.html',{'title':'Radar e revisão','records':page(request,qs),'kinds':SIGNAL_KINDS,'q':q,'status':state})

@login_required
def signal_detail(request,pk):
    s=get_object_or_404(Signal.objects.select_related('municipality'),pk=pk)
    initial={'title':s.title[:240],'problem':s.reason+'\nFonte: '+s.source_url,'front':'royalties' if s.kind=='royalties' else 'urbano' if s.kind in ('plano','fundiaria','cadastral') else 'apoio','next_action':'Conferir demanda, interlocutor e capacidade de entrega','next_date':date.today()+timedelta(days=2)}
    form=OpportunityForm(request.POST or None,initial=initial)
    if request.method=='POST':
        if request.POST.get('action')=='discard':
            note=request.POST.get('note','').strip()
            if not note:messages.error(request,'Informe o motivo do descarte.')
            elif s.status=='convertido':messages.error(request,'Este sinal já está vinculado a uma oportunidade.')
            else:s.status='descartado';s.review_note=note;s.save();return redirect('signals')
        elif request.POST.get('action')=='reopen':
            if s.status!='convertido':s.status='novo';s.save()
            return redirect('signal_detail',pk=pk)
        elif form.is_valid():
            with transaction.atomic():
                existing=Opportunity.objects.filter(signal=s).first()
                if existing:return redirect('opportunity_detail',pk=existing.pk)
                o=form.save(commit=False);o.signal=s;o.save()
                Activity.objects.create(opportunity=o,kind='nota',author=request.user.username,text='Sinal revisado e convertido em oportunidade. Fonte: '+s.source_url)
                s.status='convertido';s.save()
            return redirect('opportunity_detail',pk=o.pk)
    return render(request,'core/signal.html',{'title':'Revisar sinal','s':s,'form':form,'payload':json.dumps(s.payload,ensure_ascii=False,indent=2)})

@login_required
def assisted_signal(request):
    form=AssistedSignalForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        d=form.cleaned_data
        key='assistido:'+hashlib.sha256((d['url']+d['title']).encode()).hexdigest()
        obj,created=Signal.objects.get_or_create(external_key=key,defaults={'title':d['title'],'kind':d['kind'],'source_url':d['url'],
            'reason':d['text'],'payload':{'registrado_por':request.user.username,'origem':'Consulta assistida; revisão pendente'}})
        messages.success(request,'Sinal registrado para revisão.' if created else 'Este sinal já está cadastrado; o registro anterior foi preservado.')
        return redirect('signal_detail',pk=obj.pk)
    return render(request,'core/form.html',{'title':'Registrar evidência de consulta pública','form':form,'back':'/sinais/','intro':'Use para cartórios, legislação municipal e fontes sem integração disponível. Cole o trecho consultado e preserve o endereço de origem.'})

@login_required
def royalties(request):
    qs=Royalty.objects.select_related('municipality').all()
    years=list(qs.values_list('year',flat=True).distinct().order_by('-year'))
    year=request.GET.get('year') or (str(years[0]) if years else '')
    if year and year.isdigit():qs=qs.filter(year=int(year))
    uf=request.GET.get('uf','')
    if uf:qs=qs.filter(municipality__uf=uf)
    q=request.GET.get('q','')
    if q:qs=qs.filter(municipality__name__icontains=q)
    aggregate=list(qs.values('municipality_id','municipality__name','municipality__uf').annotate(minimum=Sum('minimum'),excess=Sum('excess'),total=Sum('total'),months=Count('month',distinct=True)).order_by('-excess'))
    for r in aggregate:r['percent']=r['excess']/r['total']*100 if r['total'] else None
    return render(request,'core/royalties.html',{'title':'Inteligência de royalties','records':page(request,aggregate),'years':years,'year':year,'q':q,'ufs':UF_CODES,'uf':uf,'months':list(qs.values_list('month',flat=True).distinct().order_by('month'))})

@login_required
def municipality_detail(request,code):
    m=get_object_or_404(Municipality,pk=code)
    return render(request,'core/municipality.html',{'title':str(m),'m':m,'records':page(request,Royalty.objects.filter(municipality=m)),'organizations':Organization.objects.filter(municipality=m),'plan':DirectorPlan.objects.filter(municipality=m).first()})

@login_required
@require_POST
def municipality_signal(request,code):
    m=get_object_or_404(Municipality,pk=code)
    key='municipio:'+code
    s,_=Signal.objects.get_or_create(external_key=key,defaults={'title':'Investigar oportunidade de royalties — '+str(m),'kind':'royalties','municipality':m,'source_url':ANP_URL,
         'reason':'Município selecionado pelo usuário para investigação. Os recebimentos não comprovam direito a revisão nem receita recuperável.'})
    return redirect('signal_detail',pk=s.pk)

@login_required
def sources(request):
    form=CollectionForm(request.POST or None,initial={'year':date.today().year})
    if request.method=='POST' and form.is_valid():
        d=form.cleaned_data
        try:
            j=start_job(d['source'],{k:v for k,v in d.items() if k!='source' and v is not None})
            return redirect('job_detail',pk=j.pk)
        except ValueError as exc:messages.error(request,str(exc))
    return render(request,'core/sources.html',{'title':'Fontes e coletas','form':form,'jobs':page(request,CollectionJob.objects.all(),15),'tjpb_url':TJPB_URL,'watches':WatchedPage.objects.filter(active=True).count()})

@login_required
def job_detail(request,pk):
    j=get_object_or_404(CollectionJob,pk=pk)
    return render(request,'core/job.html',{'title':f'Coleta {j.pk} · {j.source.upper()}','job':j,'refresh':j.status in ('queued','running')})

@login_required
def snapshot_download(request,pk):
    snap=get_object_or_404(Snapshot,pk=pk)
    path=settings.DATA_DIR/'fontes'/str(snap.job_id)/snap.filename
    if not path.is_file():raise Http404
    return FileResponse(path.open('rb'),as_attachment=True,filename=snap.filename)

@login_required
def backup_page(request):
    return render(request,'core/backup.html',{'title':'Backup e exportação'})

@login_required
@require_POST
def download_backup(request):
    if CollectionJob.objects.filter(status__in=['queued','running']).exists():
        messages.error(request,'Aguarde o fim da coleta antes de criar o backup.');return redirect('backup')
    from .backup import create_backup
    path=create_backup()
    return FileResponse(path.open('rb'),as_attachment=True,filename=path.name)

@login_required
def export_csv(request):
    stream=io.StringIO();w=csv.writer(stream,delimiter=';')
    w.writerow(['Oportunidade','Organização','Frente','Etapa','Responsável','Próxima ação','Prazo','Valor proposto','Primeiro recebimento previsto'])
    def safe(v):
        t='' if v is None else str(v)
        return "'"+t if t.startswith(('=','+','-','@','\t','\r')) else t
    for o in Opportunity.objects.select_related('organization'):
        w.writerow([safe(v) for v in [o.title,o.organization.name,o.get_front_display(),o.get_stage_display(),o.owner,o.next_action,o.next_date,o.expected_value,o.expected_receipt]])
    response=HttpResponse('\ufeff'+stream.getvalue(),content_type='text/csv; charset=utf-8')
    response['Content-Disposition']='attachment; filename="oportunidades.csv"';return response

@login_required
def help_page(request):return render(request,'core/help.html',{'title':'Guia de uso da CartoGeo'})

@login_required
def briefing(request,pk):
    o=get_object_or_404(Opportunity.objects.select_related('organization'),pk=pk)
    text=f'''BRIEFING INTERNO — {o.title}
Organização: {o.organization.name}
Frente: {o.get_front_display()}
Etapa: {o.get_stage_display()}
Responsável: {o.owner}

Problema e evidências
{o.problem or 'A identificar'}

Escopo em discussão
{o.scope or 'A definir com avaliação técnica'}

O que falta para avançar
{o.blockers or 'Conferir demanda, decisor, capacidade de entrega e condições comerciais.'}

Próxima ação
{o.next_action} — {o.next_date or 'Sem data'}

Perguntas para a conversa
1. Qual problema concreto precisa ser resolvido e em qual prazo?
2. Quem avalia o trabalho e quem decide a contratação?
3. Quais documentos já estão disponíveis?
4. Como são definidos orçamento e pagamento?

Uso interno. Educar o problema, nunca o método. Nenhum mapa indicativo em material comercial. Não usar PMRR Bayeux. Não prometer resultados administrativos ou judiciais.
'''
    return HttpResponse(text,content_type='text/plain; charset=utf-8')
