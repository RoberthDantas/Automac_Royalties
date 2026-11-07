import json
from copy import deepcopy
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import FileResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.views.decorators.http import require_POST
from .models import CollectionJob,Signal
from .bid_scans import CAPABILITIES,default_parameters
from .monitoring import state_report,build_bundle
from .collectors import start_job

class ScanForm(forms.Form):
    profiles=forms.MultipleChoiceField(label='Capacidades a pesquisar',choices=[(k,v['label']) for k,v in CAPABILITIES.items()],widget=forms.CheckboxSelectMultiple,initial=list(CAPABILITIES))
    ufs=forms.MultipleChoiceField(label='Estados',choices=[(x,x) for x in ['PB','RN','CE','SE','AL']],widget=forms.CheckboxSelectMultiple,initial=['PB','RN','CE','SE','AL'])
    pages=forms.IntegerField(label='Máximo de páginas por UF nesta rodada',min_value=1,max_value=40,initial=20)
    extra_terms=forms.CharField(label='Termos adicionais separados por vírgula',required=False,max_length=1500)

@login_required
def monitor(request):
    form=ScanForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        d=form.cleaned_data;p=default_parameters(d['profiles'],d['ufs'],d['pages']);p['extra_terms']=d['extra_terms']
        try:j=start_job('pncp_capacidades',p)
        except ValueError as exc:messages.error(request,str(exc))
        else:return redirect('job_detail',pk=j.pk)
    report=state_report()
    runs=list(CollectionJob.objects.filter(source='pncp_capacidades')[:10])
    for j in runs:j.coverage=[dict(uf=uf,**j.parameters.get('progress',{}).get(uf,{})) for uf in j.parameters.get('ufs',[])]
    prior=settings.BASE_DIR/'referencias/varredura_20260921.json'
    reference=json.loads(prior.read_text(encoding='utf-8')) if prior.exists() else None
    return render(request,'core/monitor.html',{'title':'Acompanhamento e editais','report':report,'form':form,'runs':runs,'capabilities':CAPABILITIES.values(),
        'reference_scan':reference,'bid_signals':Signal.objects.filter(kind='edital').order_by('-updated_at')[:30]})

@login_required
@require_POST
def resume_scan(request,pk):
    old=get_object_or_404(CollectionJob,pk=pk,source='pncp_capacidades')
    if old.status not in ['partial','error']:
        messages.error(request,'Esta coleta não está pendente. Inicie nova varredura para atualizar a fonte.');return redirect('monitor')
    p=deepcopy(old.parameters);p['resumed_from']=old.pk
    try:j=start_job('pncp_capacidades',p)
    except ValueError as exc:messages.error(request,str(exc));return redirect('monitor')
    return redirect('job_detail',pk=j.pk)

@login_required
@require_POST
def export_bundle(request,kind):
    if kind not in ['acompanhamento','dossie']:return redirect('monitor')
    from launch import local_lock
    try:lock=local_lock('collection.lock')
    except SystemExit:messages.error(request,'Aguarde a coleta terminar antes de consolidar o pacote.');return redirect('monitor')
    try:
        if CollectionJob.objects.filter(status__in=['queued','running']).exists():
            messages.error(request,'Há coleta ativa; aguarde para consolidar os resultados.');return redirect('monitor')
        with transaction.atomic():path=build_bundle(evidence=kind=='dossie')
    except (ValueError,OSError) as exc:
        messages.error(request,str(exc));return redirect('monitor')
    finally:lock.close()
    return FileResponse(path.open('rb'),as_attachment=True,filename=path.name)
