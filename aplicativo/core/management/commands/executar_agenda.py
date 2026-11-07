from django.core.management.base import BaseCommand
from core.scheduling import tick

class Command(BaseCommand):
    help='Verifica a agenda uma vez. Pode ser chamado pelo Agendador de Tarefas do Windows.'
    def add_arguments(self,parser):parser.add_argument('--wait',action='store_true',help='Mantém a tarefa do Windows ativa até a coleta terminar.')
    def handle(self,*args,**options):
        job=tick()
        self.stdout.write(f'Coleta {job.pk} iniciada.' if job else 'Agenda verificada; sem nova coleta neste instante.')
        if job and options['wait']:
            import time
            while True:
                job.refresh_from_db()
                if job.status not in ('queued','running'):break
                time.sleep(2)
