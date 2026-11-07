import time
from datetime import datetime
from zoneinfo import ZoneInfo
from copy import deepcopy
from django.core.management.base import BaseCommand
from core.models import CollectionJob
from core.bid_scans import default_parameters
from core.collectors import execute_job
from core.monitoring import build_bundle

class Command(BaseCommand):
    help='Executa varredura local. --ate-14h repete no máximo a cada hora, somente até 14h de hoje em America/Fortaleza.'
    def add_arguments(self,parser):
        parser.add_argument('--ate-14h',action='store_true')
        parser.add_argument('--continuo',action='store_true',help='Repetir a cada hora até Ctrl+C; exige computador ligado.')
    def handle(self,*args,**options):
        from launch import local_lock
        tz=ZoneInfo('America/Fortaleza');stop=datetime.now(tz).replace(hour=14,minute=0,second=0,microsecond=0)
        prior=None
        while True:
            if options['ate_14h'] and datetime.now(tz)>=stop:
                self.stdout.write('Janela encerrada. Nenhuma varredura adicional iniciada.');return
            try:lock=local_lock('collection.lock')
            except SystemExit:
                self.stdout.write('Outra coleta está em execução. Aguarde e execute novamente.');return
            try:
                if CollectionJob.objects.filter(status__in=['queued','running']).exists():
                    self.stdout.write('Há uma coleta ativa ou interrompida registrada. Abra o app para conferir.');return
                p=deepcopy(prior.parameters) if prior and prior.status=='partial' else default_parameters(pages=20)
                if prior and prior.status=='partial':p['resumed_from']=prior.pk
                j=CollectionJob.objects.create(source='pncp_capacidades',parameters=p)
                execute_job(j.pk);j.refresh_from_db();prior=j
                self.stdout.write(j.summary)
                self.stdout.write('Pacote de acompanhamento: '+str(build_bundle()))
            finally:lock.close()
            if not options['ate_14h'] and not options['continuo']:return
            seconds=3600 if options['continuo'] else min(3600,max(0,(stop-datetime.now(tz)).total_seconds()))
            self.stdout.write('Aguardando próxima rodada. Ctrl+C para encerrar.');time.sleep(seconds)
