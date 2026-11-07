from django.urls import path
from django.contrib.auth import views as auth
from django.views.static import serve
from django.conf import settings
from core import views as v
from core import well_views as w
from core import planning_views as p
from core import monitor_views as m
from core import central_views as c
from core import commercial as cm
from core import prospect as pr

urlpatterns=[
 path('lista-quente/',cm.hot_list,name='hot_list'),
 path('lista-quente/paraiba/',pr.hot_list_pb,name='hot_list_pb'),
 path('contatos/<int:pk>/conferir/',pr.verify_contact,name='verify_contact'),
 path('oportunidade/<int:pk>/mensagem/',pr.opportunity_message,name='opportunity_message'),
 path('royalties/serie/',pr.start_royalty_series,name='royalty_series'),
 path('metas/',cm.goals,name='goals'),
 path('metas/relatorio.md',cm.activity_report,name='activity_report'),
 path('pocos/planilha.xlsx',w.wells_xlsx,name='wells_xlsx'),
 path('cartorios/',c.notaries,name='notaries'),
 path('cartorios/exportar.csv',c.notaries_export,name='notaries_export'),
 path('agenda/',c.agenda,name='agenda'),
 path('agenda/nova/',c.schedule_edit,name='schedule_new'),
 path('agenda/<int:pk>/',c.schedule_edit,name='schedule_edit'),
 path('agenda/<int:pk>/acao/',c.schedule_action,name='schedule_action'),
 path('radar/',c.radar,name='radar'),
 path('cobertura/',c.source_health,name='source_health'),
 path('cobertura/<int:pk>/consultar/',c.source_run,name='source_run'),
 path('central/pulso/',c.pulse,name='pulse'),
 path('central/briefing.md',c.daily_brief,name='daily_brief'),
 path('acompanhamento/',m.monitor,name='monitor'),
 path('acompanhamento/exportar/<str:kind>/',m.export_bundle,name='monitor_export'),
 path('acompanhamento/retomar/<int:pk>/',m.resume_scan,name='resume_scan'),
 path('planejamento/',p.plans,name='internal_plans'),
 path('planejamento/novo/',p.plan_edit,name='new_internal_plan'),
 path('planejamento/<int:pk>/',p.plan_edit,name='internal_plan_edit'),
 path('planejamento/continuidade.md',p.checkpoint,name='continuity'),
 path('referencia-interna/<str:name>/',p.reference,name='internal_reference'),
 path('municipios/',p.municipalities,name='municipalities'),
 path('',v.dashboard,name='dashboard'),
 path('entrar/',auth.LoginView.as_view(template_name='core/login.html'),name='login'),
 path('sair/',auth.LogoutView.as_view(),name='logout'),
 path('sinais/',c.radar,name='signals'),path('sinais/novo/',v.assisted_signal,name='assisted_signal'),
 path('sinais/<int:pk>/',v.signal_detail,name='signal_detail'),
 path('royalties/',v.royalties,name='royalties'),
 path('pocos/',w.wells_page,name='wells'),
 path('pocos/mapa/',w.well_map,name='well_map'),
 path('pocos/exportar.geojson',w.well_geojson,name='well_geojson'),
 path('pocos/cartografia.zip',w.cartography_package,name='cartography_package'),
 path('pocos/producao/',w.production_page,name='well_production'),
 path('pocos/<str:registration>/',w.well_detail,name='well_detail'),
 path('municipios/<str:code>/',v.municipality_detail,name='municipality_detail'),
 path('municipios/<str:code>/sinal/',v.municipality_signal,name='municipality_signal'),
 path('oportunidade/<int:pk>/',v.opportunity_detail,name='opportunity_detail'),
 path('oportunidade/<int:pk>/historico/',v.add_activity,name='add_activity'),
 path('oportunidade/<int:pk>/documento/',v.add_attachment,name='add_attachment'),
 path('oportunidade/<int:pk>/briefing/',v.briefing,name='briefing'),
 path('documento/<int:pk>/',v.attachment_download,name='attachment_download'),
 path('fontes/',v.sources,name='sources'),path('coletas/<int:pk>/',v.job_detail,name='job_detail'),
 path('fonte-arquivo/<int:pk>/',v.snapshot_download,name='snapshot_download'),
 path('backup/',v.backup_page,name='backup'),path('backup/baixar/',v.download_backup,name='download_backup'),
 path('exportar/oportunidades/',v.export_csv,name='export_csv'),path('ajuda/',v.help_page,name='help'),
 path('static/<path:path>',serve,{'document_root':settings.STATIC_ROOT}),
 path('<str:entity>/novo/',v.edit,name='new'),path('<str:entity>/<int:pk>/editar/',v.edit,name='edit'),
 path('<str:entity>/',v.listing,name='listing'),
]
