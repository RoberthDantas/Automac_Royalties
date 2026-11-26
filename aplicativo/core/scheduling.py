"""Persistent local calendar. No AI calls, email or cloud dependency."""
import calendar
import logging
import threading
from copy import deepcopy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.db import close_old_connections
from django.utils import timezone
from .models import CollectionSchedule, CollectionJob, SchedulerState

LOCAL=ZoneInfo('America/Fortaleza')

def next_occurrence(schedule, after=None):
    now=(after or timezone.now()).astimezone(LOCAL)
    if schedule.frequency=='interval': return now+timedelta(minutes=schedule.interval_minutes)
    at=schedule.at_time
    if isinstance(at,str):at=datetime.strptime(at,'%H:%M').time()
    candidate=datetime.combine(now.date(),at,tzinfo=LOCAL)
    if schedule.frequency=='daily':
        return candidate if candidate>now else candidate+timedelta(days=1)
    if schedule.frequency=='weekly':
        candidate+=timedelta(days=(schedule.weekday-now.weekday())%7)
        return candidate if candidate>now else candidate+timedelta(days=7)
    year,month=now.year,now.month
    for _ in range(2):
        day=min(schedule.monthday,calendar.monthrange(year,month)[1])
        candidate=datetime.combine(now.date().replace(year=year,month=month,day=day),at,tzinfo=LOCAL)
        if candidate>now:return candidate
        month+=1
        if month==13:year+=1;month=1
    raise ValueError('Não foi possível calcular a próxima execução.')

def schedule_parameters(s):
    p=deepcopy(s.parameters or {})
    if s.source=='anp':p['year']=timezone.localdate().year
    if s.source=='pncp_capacidades':
        from .bid_scans import default_parameters
        p={**default_parameters(pages=8),**p,'budget_seconds':180}
    if s.last_job_id and s.source in ('pncp_capacidades','diarios'):
        previous=s.last_job
        if previous.status=='partial' and previous.created_at>timezone.now()-timedelta(days=1):
            p=deepcopy(previous.parameters)
    p['_schedule_id']=s.pk
    return p

def recover_interrupted():
    """An OS collection lock, not an arbitrary timeout, proves no worker is active."""
    from launch import local_lock
    jobs=CollectionJob.objects.filter(status__in=['queued','running'])
    if not jobs.exists() or jobs.filter(created_at__gte=timezone.now()-timedelta(minutes=5)).exists():return
    try:lock=local_lock('collection.lock')
    except SystemExit:return
    try:
        jobs.update(status='error',finished_at=timezone.now(),summary='Processo de coleta interrompido; trava de execução estava livre. Dados anteriores preservados. A agenda tentará novamente na próxima ocorrência.')
    finally:lock.close()

def tick():
    from launch import local_lock
    from .collectors import start_job
    close_old_connections()
    try:lock=local_lock('scheduler.lock')
    except SystemExit:return None
    try:
        recover_interrupted()
        SchedulerState.objects.update_or_create(key='local',defaults={'heartbeat':timezone.now(),'message':'Agenda verificada neste computador.'})
        if CollectionJob.objects.filter(status__in=['queued','running']).exists():return None
        s=CollectionSchedule.objects.filter(enabled=True,next_run__lte=timezone.now()).select_related('last_job').order_by('next_run','pk').first()
        if not s:return None
        try:j=start_job(s.source,schedule_parameters(s))
        except ValueError:return None
        s.last_run=timezone.now();s.last_job=j;s.next_run=next_occurrence(s,s.last_run)
        s.save(update_fields=['last_run','last_job','next_run'])
        return j
    finally:lock.close();close_old_connections()

def start_scheduler():
    def loop():
        while True:
            try:tick()
            except Exception:logging.getLogger(__name__).exception('Falha ao verificar agenda local')
            threading.Event().wait(30)
    threading.Thread(target=loop,name='automac-agenda',daemon=True).start()
