import csv
import io
import json
from datetime import timedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from .models import *
from .views import page
from .central_forms import ScheduleForm
from .scheduling import next_occurrence, schedule_parameters
from .intelligence import TOPICS

def safe_cell(value):
    text='' if value is None else str(value)
    return "'"+text if text.lstrip().startswith(('=','+','-','@')) or text.startswith(('\t','\r','\n')) else text

def notaries_query(request):
    qs=Organization.objects.filter(kind='cartorio').select_related('municipality').prefetch_related('contacts')
    q=request.GET.get('q','').strip()
    if q:qs=qs.filter(Q(name__icontains=q)|Q(cnpj__icontains=q)|Q(address__icontains=q)|Q(municipality__name__icontains=q)|Q(contacts__email__icontains=q)).distinct()
    if request.GET.get('uf'):qs=qs.filter(municipality__uf=request.GET['uf'])
    if request.GET.get('imoveis')=='1':qs=qs.filter(Q(attributes__icontains='Registro de Imóveis')|Q(notes__icontains='Registro de Imóveis'))
    if request.GET.get('email')=='1':qs=qs.filter(contacts__do_not_contact=False,contacts__email__gt='').distinct()
    return qs

@login_required
def notaries(request):
    qs=notaries_query(request)
    emails=sorted({c.email for o in qs for c in o.contacts.all() if c.email and not c.do_not_contact})
    return render(request,'core/notaries.html',{'title':'Central de cartórios','records':page(request,qs,25),'total':qs.count(),
        'emails':'; '.join(emails),'email_count':len(emails),'ufs':['PB','RN','CE','SE','AL'],'filter_query':request.GET.urlencode()})

@login_required
def notaries_export(request):
    stream=io.StringIO();writer=csv.writer(stream,delimiter=';')
    writer.writerow(['Cartório','CNS','Município','UF','Endereço','Atribuições','Contato','E-mail','Telefone','Não contatar','Fonte','Data do cadastro consultado'])
    for org in notaries_query(request):
        for c in list(org.contacts.all()) or [None]:
            writer.writerow([safe_cell(v) for v in [org.name,org.cnpj,org.municipality.name if org.municipality else '',org.municipality.uf if org.municipality else '',org.address,org.attributes,
                c.name if c else '',c.email if c else '',c.phone if c else '', 'SIM' if c and c.do_not_contact else 'NÃO',c.source_url if c and c.source_url else org.source_url,c.verified_on if c else org.verified_on]])
    r=HttpResponse('\ufeff'+stream.getvalue(),content_type='text/csv; charset=utf-8');r['Content-Disposition']='attachment; filename="cartorios.csv"';return r

@login_required
def agenda(request):
    schedules=CollectionSchedule.objects.select_related('last_job')
    state=SchedulerState.objects.filter(pk='local').first()
    alive=bool(state and state.heartbeat and state.heartbeat>timezone.now()-timedelta(minutes=6))
    today=timezone.localdate()
    return render(request,'core/agenda.html',{'title':'Agenda e automações','schedules':schedules,'state':state,'alive':alive,'today':today,
        'tasks':InternalPlan.objects.exclude(status__in=['concluido','suspenso']).order_by('due_date','pk')[:30],
        'op_tasks':Opportunity.objects.exclude(stage__in=['concluida','perdida','suspensa']).order_by('next_date','pk')[:20]})

@login_required
def schedule_edit(request,pk=None):
    obj=get_object_or_404(CollectionSchedule,pk=pk) if pk else None
    form=ScheduleForm(request.POST or None,instance=obj)
    if request.method=='POST' and form.is_valid():
        s=form.save(commit=False)
        if any(k in form.changed_data for k in ('source','ufs','url','environment')):s.last_job=None
        s.parameters={k:form.cleaned_data[k] for k in ('ufs','url','environment') if form.cleaned_data.get(k)}
        s.next_run=next_occurrence(s);s.save()
        messages.success(request,'Rotina salva. A agenda executa neste computador quando o aplicativo ou o Agendador do Windows estiver ativo.')
        return redirect('agenda')
    return render(request,'core/form.html',{'title':'Editar rotina' if obj else 'Nova rotina','form':form,'back':'/agenda/',
        'intro':'Ao voltar de um período desligado, executa uma coleta pendente e avança para o próximo horário. Não acumula dezenas de execuções antigas.'})

@login_required
@require_POST
def schedule_action(request,pk):
    s=get_object_or_404(CollectionSchedule,pk=pk)
    if request.POST.get('action')=='toggle':
        s.enabled=not s.enabled
        if s.enabled:s.next_run=timezone.now()
        s.save();messages.success(request,'Rotina ativada.' if s.enabled else 'Rotina pausada.')
    elif request.POST.get('action')=='run':
        from .collectors import start_job
        try:
            job=start_job(s.source,schedule_parameters(s));s.last_job=job;s.last_run=timezone.now();s.next_run=next_occurrence(s);s.save()
            return redirect('job_detail',pk=job.pk)
        except ValueError as e:messages.warning(request,str(e))
    return redirect('agenda')

@login_required
def radar(request):
    qs=Signal.objects.select_related('municipality','job')
    q=request.GET.get('q','').strip();status=request.GET.get('status','novo')
    if q:qs=qs.filter(Q(title__icontains=q)|Q(reason__icontains=q)|Q(payload__icontains=q))
    if status:qs=qs.filter(status=status)
    if request.GET.get('origin'):qs=qs.filter(source_type=request.GET['origin'])
    if request.GET.get('topic') in TOPICS:qs=qs.filter(payload__temas__icontains=request.GET['topic'])
    if request.GET.get('uf'):qs=qs.filter(municipality__uf=request.GET['uf'])
    if request.GET.get('deadline')=='open':qs=qs.filter(deadline__gte=timezone.now())
    elif request.GET.get('deadline')=='week':qs=qs.filter(deadline__gte=timezone.now(),deadline__lte=timezone.now()+timedelta(days=7))
    elif request.GET.get('deadline')=='unknown':qs=qs.filter(deadline__isnull=True)
    if request.GET.get('days') in ('1','7','30'):qs=qs.filter(collected_at__gte=timezone.now()-timedelta(days=int(request.GET['days'])))
    order=request.GET.get('order','recent')
    qs=qs.order_by('-relevance','-publication_date','-collected_at') if order=='score' else qs.order_by('-collected_at')
    return render(request,'core/radar.html',{'title':'Radar de oportunidades','records':page(request,qs,24),'total':qs.count(),
      'topics':[(k,v[0]) for k,v in TOPICS.items()],'ufs':['PB','RN','CE','SE','AL'],'status':status,
      'origins':[('pncp','PNCP'),('diario','Diários indexados'),('pagina','Fontes públicas'),('privada','Fontes privadas'),('manual','Registro manual')],
      'fresh_count':Signal.objects.filter(collected_at__gte=timezone.now()-timedelta(days=1)).count(),
      'closing_count':Signal.objects.filter(deadline__gte=timezone.now(),deadline__lte=timezone.now()+timedelta(days=7),status='novo').count(),
      'jobs':CollectionJob.objects.all()[:5]})

@login_required
def source_health(request):
    return render(request,'core/source_health.html',{'title':'Fontes e cobertura','watches':WatchedPage.objects.select_related('municipality'),
       'schedules':CollectionSchedule.objects.select_related('last_job'),'jobs':CollectionJob.objects.all()[:15]})

@login_required
@require_POST
def source_run(request,pk):
    w=get_object_or_404(WatchedPage,pk=pk)
    from .collectors import start_job
    try:return redirect('job_detail',pk=start_job('paginas',{'watch_id':w.pk}).pk)
    except ValueError as exc:messages.warning(request,str(exc));return redirect('source_health')

@login_required
def pulse(request):
    state=SchedulerState.objects.filter(pk='local').first()
    job=CollectionJob.objects.first()
    return JsonResponse({'signals':Signal.objects.filter(status='novo').count(),
        'scheduler_alive':bool(state and state.heartbeat and state.heartbeat>timezone.now()-timedelta(minutes=6)),
        'job':{'id':job.pk,'status':job.get_status_display(),'source':job.source} if job else None})

@login_required
def daily_brief(request):
    today=timezone.localdate();signals=Signal.objects.filter(status='novo').select_related('municipality').order_by('-relevance','-collected_at')[:30]
    lines=[f'# Automac_Royalties — briefing interno de {today}', '', 'Sinais de triagem; confirmar demanda e habilitação. Não enviar contatos automaticamente.', '', '## Sinais prioritários']
    for s in signals:
        lines+=['',f'### {s.title}',f'- Origem: {s.source_type}; publicação: {s.publication_date or "não identificada"}; primeira coleta: {s.collected_at.isoformat()}',
                f'- Fonte: {s.source_url}',f'- Prazo: {s.deadline or "não identificado"}; revisão: {s.get_status_display()}',f'- Motivo: {s.reason}']
    lines+=['','## Tarefas pendentes']
    for p in InternalPlan.objects.exclude(status__in=['concluido','suspenso']):lines.append(f'- {p.title}: {p.next_action} — {p.owner}, {p.due_date or "sem prazo"}. Pendências: {p.blockers}')
    lines+=['','## Últimas coletas']
    for j in CollectionJob.objects.all()[:10]:lines.append(f'- {j.source}: {j.get_status_display()} — {j.summary}')
    r=HttpResponse('\n'.join(lines),content_type='text/markdown; charset=utf-8');r['Content-Disposition']=f'attachment; filename="Automac_Royalties_Briefing_{today}.md"';return r
