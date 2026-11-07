import platform
from django import get_version
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.migrations.executor import MigrationExecutor
from django.db import connection
from core.models import Municipality,Well,Signal,InternalPlan,CollectionJob

class Command(BaseCommand):
    help='Resumo técnico curto, sem contatos, senhas ou dados financeiros.'
    def handle(self,*args,**kwargs):
        self.stdout.write(f'CartoGeo {settings.VERSION} | Python {platform.python_version()} | Django {get_version()}')
        executor=MigrationExecutor(connection)
        pending=executor.migration_plan(executor.loader.graph.leaf_nodes())
        self.stdout.write('Migrações pendentes: '+str(len(pending)))
        if pending:
            self.stdout.write('Abra 02_ABRIR.bat (pasta principal) para aplicar a atualização antes de consultar os totais.');return
        for model,label in [(Municipality,'Municípios'),(Well,'Poços'),(Signal,'Sinais'),(InternalPlan,'Ações internas')]:
            self.stdout.write(f'{label}: {model.objects.count()}')
        for job in CollectionJob.objects.order_by('-pk')[:3]:
            self.stdout.write(f'Coleta #{job.pk}: {job.source} | {job.status}')
        self.stdout.write('Para retomar: anexar este diagnóstico e o resumo em Planejamento interno. Em caso de falha, incluir o erro da janela do aplicativo.')
