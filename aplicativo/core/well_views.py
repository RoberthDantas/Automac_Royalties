import io
import json
import zipfile
from pathlib import Path
from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import Well, WellProduction, CollectionJob
from .wells import UF_NAMES, PRODUCTION_URL, PRODUCTION_PAGE, import_production


def filtered_wells(request):
    qs=Well.objects.select_related('snapshot__job')
    q=request.GET.get('q','').strip()
    if q:qs=qs.filter(Q(name__icontains=q)|Q(registration__icontains=q)|Q(field__icontains=q)|Q(operator__icontains=q))
    for param,field in [('uf','uf'),('ambiente','environment'),('situacao','situation')]:
        value=request.GET.get(param,'').strip()
        if value:qs=qs.filter(**{field:value})
    return qs


def feature_collection(qs):
    features=[]
    for well in qs.iterator():
        geometry=None if well.longitude is None or well.latitude is None else {'type':'Point','coordinates':[well.longitude,well.latitude]}
        features.append({'type':'Feature','id':well.pk,'geometry':geometry,'properties':{
            'cadastro':well.registration,'poco':well.name,'uf':well.uf,'ambiente':well.environment,
            'situacao':well.situation,'operador':well.operator,'bacia':well.basin,'campo':well.field,
            'datum_original':well.original_datum,'coordenadas_exportadas':'WGS84 / EPSG:4326 via WFS ANP',
            'fonte':well.snapshot.url,'fonte_sha256':well.snapshot.sha256,
            'referencia_da_copia':'2026-09-18' if well.snapshot.job.source=='pocos_referencia' else well.snapshot.created_at.isoformat(),
            'importado_em':well.snapshot.created_at.isoformat()}})
    return {'type':'FeatureCollection','name':'Pocos_ANP_PB_RN_CE_SE_AL','features':features}

@login_required
def wells_page(request):
    qs=filtered_wells(request)
    args=request.GET.copy();args.pop('page',None)
    return render(request,'core/wells.html',{'title':'Poços e cartografia','records':Paginator(qs,40).get_page(request.GET.get('page')),
        'count':qs.count(),'states':UF_NAMES,'situations':Well.objects.order_by('situation').values_list('situation',flat=True).distinct(),
        'filters':args.urlencode(),'stats':Well.objects.values('uf').annotate(n=Count('pk')).order_by('uf'),
        'latest':CollectionJob.objects.filter(source__in=['pocos','pocos_referencia']).first()})

@login_required
def well_detail(request,registration):
    well=get_object_or_404(Well.objects.select_related('snapshot'),pk=registration)
    matches=Well.objects.filter(uf=well.uf,name_key=well.name_key).count()
    production=WellProduction.objects.filter(uf=well.uf,name_key=well.name_key).select_related('snapshot') if matches==1 else WellProduction.objects.none()
    return render(request,'core/well_detail.html',{'title':well.name,'well':well,'production':production[:60],
        'ambiguous':matches!=1,'properties':sorted(well.properties.items()),
        'duplicate_registration':Well.objects.filter(registration=well.registration).exclude(pk=well.pk).count()})

@login_required
def well_geojson(request):
    response=JsonResponse(feature_collection(filtered_wells(request)),json_dumps_params={'ensure_ascii':False,'allow_nan':False})
    response['Content-Disposition']='attachment; filename="pocos_anp.geojson"'
    return response

@login_required
def well_map(request):
    return render(request,'core/well_map.html',{'title':'Mapa dos poços','filters':request.GET.urlencode()})

@login_required
def cartography_package(request):
    data=feature_collection(filtered_wells(request))
    # A self-contained map: points, state outlines, library, sources and GIS data.
    root=Path(settings.STATIC_ROOT)
    page=(root/'pocos_mapa_offline.html').read_text(encoding='utf-8')
    inline=json.dumps(data,ensure_ascii=False,allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    outlines=json.loads((root/'pocos_ufs.geojson').read_text(encoding='utf-8'))
    page=page.replace('__WELLS_DATA__',inline).replace('__OUTLINES_DATA__',json.dumps(outlines,ensure_ascii=False).replace('<','\\u003c'))
    municipalities=json.loads((root/'municipios_ibge.geojson').read_text(encoding='utf-8'))
    lines=json.loads((root/'linhas_lbr.geojson').read_text(encoding='utf-8'))
    safe=lambda obj: json.dumps(obj,ensure_ascii=False,allow_nan=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    page=page.replace('__MUNICIPALITIES_DATA__',safe(municipalities)).replace('__LINES_DATA__',safe(lines))
    buffer=io.BytesIO()
    with zipfile.ZipFile(buffer,'w',zipfile.ZIP_DEFLATED) as z:
        z.writestr('pocos_anp.geojson',json.dumps(data,ensure_ascii=False,allow_nan=False))
        z.writestr('mapa.html',page)
        z.write(root/'pocos_ufs.geojson','limites_estaduais_ibge.geojson')
        for name in ('leaflet.js','leaflet.css','LICENSE'):z.write(root/'leaflet'/name,'leaflet/'+name)
        z.write(root/'pocos_map.js','pocos_map.js')
        z.write(root/'territorio_map.js','territorio_map.js')
        z.write(root/'municipios_ibge.geojson','municipios_ibge.geojson')
        z.write(root/'linhas_lbr.geojson','linhas_lbr.geojson')
        z.write(settings.BASE_DIR/'referencias/planejamento_20260921/LBR_corrigida_Brasil.zip','LBR_original_SIRGAS2000.zip')
        z.write(settings.BASE_DIR/'referencias/planejamento_20260921/metadados.json','metadados_territorio.json')
        z.write(settings.BASE_DIR/'referencias/cartografia_20260921/fontes.json','fontes_municipios.json')
        z.writestr('LEIA_ME.txt','Abra mapa.html no navegador. O mapa funciona offline.\nNo QGIS: arraste os arquivos GeoJSON para o projeto. Inclui municípios IBGE simplificados e 279 linhas LBR fornecidas, apenas para uso interno, sem comprovação de oficialidade. LBR original EPSG:4674; GeoJSON de visualização EPSG:4326. Nenhum direito ou vínculo municipal é inferido. Os filtros de poços são preservados; as camadas territoriais são exportadas completas (751 municípios, 279 linhas).\nCoordenadas dos poços: WGS84 / EPSG:4326, solicitadas ao WFS da ANP.\nLimites estaduais IBGE simplificados: contexto visual; não são linhas de confrontação marítima.\nA situação é cadastral conforme ANP. Produção mensal e vinculação de royalties não são inferidas do mapa.\nAs fontes e datas de coleta acompanham os arquivos GeoJSON.\n')
    response=HttpResponse(buffer.getvalue(),content_type='application/zip')
    response['Content-Disposition']='attachment; filename="cartografia_pocos.zip"'
    return response

class ProductionForm(forms.Form):
    file=forms.FileField(label='CSV original exportado do CDP/ANP')
    environment=forms.ChoiceField(label='Ambiente selecionado na consulta',choices=[('Terra','Terra'),('Mar','Mar'),('Pré-sal','Pré-sal — subconjunto de Mar')])
    def clean_file(self):
        file=self.cleaned_data['file']
        if not file.name.lower().endswith('.csv') or file.size>25*1024*1024:raise forms.ValidationError('Envie CSV de até 25 MB, sem converter no Excel.')
        return file

@login_required
def production_page(request):
    form=ProductionForm(request.POST or None,request.FILES or None)
    if request.method=='POST' and form.is_valid():
        from launch import local_lock
        try:lock=local_lock('collection.lock')
        except SystemExit:messages.error(request,'Há outra coleta em andamento. Aguarde antes de importar o CSV.')
        else:
            try:
                job=import_production(form.cleaned_data['file'].read(),Path(form.cleaned_data['file'].name).name,form.cleaned_data['environment'])
            finally:lock.close()
            return redirect('job_detail',pk=job.pk)
    return render(request,'core/well_production.html',{'title':'Produção mensal por poço','form':form,
        'cdp_url':PRODUCTION_URL,'source_page':PRODUCTION_PAGE,
        'periods':WellProduction.objects.values('period','environment').annotate(n=Count('id')).order_by('-period'),
        'jobs':CollectionJob.objects.filter(source='producao_pocos')[:12]})


@login_required
def wells_xlsx(request):
    """0.4.2: planilha dos poços do filtro atual, com resumo por UF e produção marítima ativa."""
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from django.utils import timezone
    qs=filtered_wells(request).order_by('uf','field','name')
    wb=Workbook();summary=wb.active;summary.title='Resumo por UF'
    bold=Font(bold=True)
    summary.append(['Cadastro de poços ANP — Automac_Royalties',None]);summary['A1'].font=Font(bold=True,size=13)
    latest=CollectionJob.objects.filter(source__in=['pocos','pocos_referencia'],status__in=['ok','partial']).first()
    summary.append(['Coleta de origem',f'#{latest.pk} em {timezone.localtime(latest.created_at):%d/%m/%Y %H:%M}' if latest else 'não identificada'])
    summary.append(['Planilha gerada em',timezone.localtime().strftime('%d/%m/%Y %H:%M')])
    summary.append([])
    header=['UF','Total','Marítimos','Produzindo','Injetando','Marítimos produzindo','Marítimos injetando']
    summary.append(header)
    for c in summary[summary.max_row]:c.font=bold
    for uf in sorted(set(qs.values_list('uf',flat=True))):
        u=qs.filter(uf=uf)
        summary.append([uf,u.count(),u.filter(environment='Mar').count(),u.filter(situation='PRODUZINDO').count(),u.filter(situation='INJETANDO').count(),
                        u.filter(environment='Mar',situation='PRODUZINDO').count(),u.filter(environment='Mar',situation='INJETANDO').count()])
    summary.append([])
    summary.append(['Produção marítima ativa por campo']);summary[summary.max_row][0].font=bold
    summary.append(['UF','Campo','Operador','Poços produzindo'])
    for c in summary[summary.max_row]:c.font=bold
    for r in qs.filter(environment='Mar',situation='PRODUZINDO').values('uf','field','operator').annotate(n=Count('pk')).order_by('uf','-n'):
        summary.append([r['uf'],r['field'],r['operator'],r['n']])
    summary.append([])
    summary.append(['Situação conforme o cadastro da ANP na data da coleta; não equivale à produção mensal nem atribui direito a royalties.'])
    for col,width in zip('ABCDEFG',[14,26,24,14,12,20,20]):summary.column_dimensions[col].width=width
    sheet=wb.create_sheet('Poços')
    sheet.append(['Cadastro','Poço','UF','Bacia','Campo','Operador','Ambiente','Situação','Latitude','Longitude','Datum original'])
    for c in sheet[1]:c.font=bold
    for w in qs.iterator():
        sheet.append([w.registration,w.name,w.uf,w.basin,w.field,w.operator,w.environment,w.situation,w.latitude,w.longitude,w.original_datum])
    sheet.freeze_panes='A2';sheet.auto_filter.ref=sheet.dimensions
    for col,width in zip('ABCDEFGHIJK',[14,18,5,14,24,22,9,40,11,11,12]):sheet.column_dimensions[col].width=width
    stream=io.BytesIO();wb.save(stream)
    response=HttpResponse(stream.getvalue(),content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition']=f'attachment; filename="pocos_anp_{timezone.localdate():%Y%m%d}.xlsx"'
    return response
