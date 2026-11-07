from django.conf import settings

def navigation(request):
    return {'app_version':settings.VERSION,'nav_items':[
      ('/','Central de operação'),('/lista-quente/','Lista quente — Frente 1'),('/lista-quente/paraiba/','Lista quente — Paraíba'),
      ('/metas/','Metas e relatório'),('/oportunidades/','Funil comercial'),('/radar/','Radar de oportunidades'),
      ('/cartorios/','Central de cartórios'),('/planejamento/','Tarefas e decisões'),('/agenda/','Agenda e automações'),
      ('/fontes/','Fontes e coletas'),('/cobertura/','Fontes e cobertura'),('/municipios/','Inteligência territorial'),
      ('/pocos/','Poços e produção'),('/royalties/','Royalties'),('/planos/','Planos diretores'),('/organizacoes/','Organizações'),
      ('/contatos/','Todos os contatos'),('/financeiro/','Financeiro'),('/acompanhamento/','Continuidade e evidências'),('/backup/','Backup'),('/usuarios/','Usuários'),('/ajuda/','Guia de uso') ]}
