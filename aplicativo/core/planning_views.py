import json
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import InternalPlan, InternalPlanLog, Municipality, Well, Signal

class PlanForm(forms.ModelForm):
    class Meta:
        model = InternalPlan
        fields = ['title','municipality','category','status','owner','next_action','due_date','blockers','notes']
        widgets = {'due_date': forms.DateInput(attrs={'type':'date'},format='%Y-%m-%d')}

@login_required
def plans(request):
    qs = InternalPlan.objects.select_related('municipality','signal')
    status = request.GET.get('status','')
    if status: qs = qs.filter(status=status)
    return render(request,'core/planning.html',{'title':'Planejamento interno','plans':qs,
        'statuses':InternalPlan._meta.get_field('status').choices,'selected_status':status})

@login_required
def plan_edit(request, pk=None):
    obj = get_object_or_404(InternalPlan,pk=pk) if pk else None
    form = PlanForm(request.POST or None,instance=obj)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            saved = form.save()
            changes = {k:str(form.cleaned_data[k] or '') for k in form.changed_data}
            InternalPlanLog.objects.create(plan=saved,author=request.user.username,changes=changes)
        messages.success(request,'Planejamento salvo. Nenhuma ação externa foi executada.')
        return redirect('internal_plans')
    return render(request,'core/plan_edit.html',{'title':'Editar ação interna' if pk else 'Nova ação interna',
        'form':form,'plan':obj})

@login_required
def reference(request, name):
    allowed = {'casa_legal_interior.jpeg','casa_legal_capa.jpeg','UFs_Municipios_Censo2010.zip','LBR_corrigida_Brasil.zip','metadados.json'}
    if name not in allowed: raise Http404
    path = settings.BASE_DIR/'referencias/planejamento_20260921'/name
    return FileResponse(path.open('rb'),as_attachment=not name.endswith('.jpeg'),filename=name)

@login_required
def municipalities(request):
    qs = Municipality.objects.all()
    uf = request.GET.get('uf',''); q = request.GET.get('q','').strip()
    if uf: qs = qs.filter(uf=uf)
    if q: qs = qs.filter(Q(name__icontains=q)|Q(code__icontains=q))
    from django.core.paginator import Paginator
    return render(request,'core/municipalities.html',{'title':'Municípios','records':Paginator(qs,40).get_page(request.GET.get('page')),
        'count':qs.count(),'ufs':['PB','RN','CE','SE','AL'],'q':q,'uf':uf})

@login_required
def checkpoint(request):
    # Deliberately compact: no personal contact details, money or raw datasets.
    lines = ['# Automac_Royalties — continuidade local', f'Versão: {settings.VERSION}',
        f'Municípios: {Municipality.objects.count()} | Poços: {Well.objects.count()}',
        'Camadas: municípios IBGE simplificados; 279 linhas LBR fornecidas, validação técnica pendente.',
        'UFs_Municipios.zip: estatísticas históricas do Censo 2010, não malha municipal.',
        'Regras: uso interno; educar o problema; sem mapas em material comercial; decisões comerciais com a direção.',
        'Não recriar o método das ortogonais. Não inferir direitos a royalties da sobreposição.',
        '', '## Ações abertas']
    for p in InternalPlan.objects.exclude(status__in=['concluido','suspenso']).order_by('pk'):
        lines.append(f'- #{p.pk} {p.title} | {p.get_status_display()} | prazo: {p.due_date or "não definido"} | próxima: {p.next_action[:500]}')
    lines += ['', '## Como retomar','Ler este resumo e o ESTADO_PROJETO.md. Consultar apenas os arquivos necessários à próxima tarefa. Enviar diagnóstico curto em caso de erro; não reenviar bases completas sem necessidade.']
    response = HttpResponse('\n'.join(lines),content_type='text/markdown; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="CONTINUIDADE_AUTOMAC.md"'
    return response
