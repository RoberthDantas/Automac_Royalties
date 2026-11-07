from django.core.management.base import BaseCommand,CommandError
from core.monitoring import build_bundle
from core.models import CollectionJob
class Command(BaseCommand):
    help='Gera pacote de acompanhamento ou dossiê local para revisão e envio manual ao chat.'
    def add_arguments(self,parser):parser.add_argument('--dossie',action='store_true')
    def handle(self,*args,**options):
        from launch import local_lock
        lock=local_lock('collection.lock')
        try:
            if CollectionJob.objects.filter(status__in=['queued','running']).exists():raise CommandError('Aguarde a coleta terminar.')
            self.stdout.write(str(build_bundle(evidence=options['dossie'])))
        finally:lock.close()
