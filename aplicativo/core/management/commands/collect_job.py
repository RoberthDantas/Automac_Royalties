from django.core.management.base import BaseCommand
from core.collectors import execute_job

class Command(BaseCommand):
    def add_arguments(self,parser):parser.add_argument('job_id',type=int)
    def handle(self,*args,**options):
        from launch import local_lock
        try: lock=local_lock('collection.lock')
        except SystemExit:
            from core.models import CollectionJob
            from django.utils import timezone
            CollectionJob.objects.filter(pk=options['job_id']).update(status='error',summary='Outra coleta detém a trava de execução.',finished_at=timezone.now())
            return
        execute_job(options['job_id'])
