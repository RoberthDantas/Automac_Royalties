"""Local Windows entrypoint. Never binds to the network."""
import os
import sys
import socket
import threading
import webbrowser
from pathlib import Path
os.environ.setdefault('DJANGO_SETTINGS_MODULE','automac.settings')
import django
django.setup()
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.utils import timezone
from core.models import CollectionJob

def local_lock(name="runtime.lock"):
    handle=(settings.DATA_DIR/name).open('a+b')
    handle.seek(0);handle.write(b'0');handle.flush();handle.seek(0)
    try:
        if os.name=='nt':
            import msvcrt
            msvcrt.locking(handle.fileno(),msvcrt.LK_NBLCK,1)
        else:
            import fcntl
            fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except OSError:
        handle.close()
        raise SystemExit('A aplicacao ou a restauracao ja esta em execucao. Feche-a primeiro.')
    return handle

if __name__=='__main__':
    lock=local_lock()
    # Exclude collection and dispatch during schema changes and initial seeds.
    setup_scheduler_lock=local_lock('scheduler.lock')
    setup_dispatch_lock=local_lock('dispatch.lock')
    setup_collection_lock=local_lock('collection.lock')
    # Keep a recoverable copy before an installed update changes the schema.
    if (settings.DATA_DIR/'automac.sqlite3').exists():
        from django.db import connection
        from django.db.migrations.executor import MigrationExecutor
        executor=MigrationExecutor(connection)
        if executor.migration_plan(executor.loader.graph.leaf_nodes()):
            from core.backup import create_backup
            connection.close()
            print('Backup antes da atualizacao:',create_backup())
    call_command('migrate',interactive=False)
    call_command('check')
    call_command('configurar_territorio')
    call_command('configurar_central')
    call_command('configurar_comercial')
    call_command('importar_pasta')
    setup_collection_lock.close()
    setup_dispatch_lock.close()
    setup_scheduler_lock.close()
    if not get_user_model().objects.exists() and '--setup' not in sys.argv:
        print('\nNenhuma conta de acesso encontrada. Crie a sua agora.\n')
        call_command('criar_usuario')
    if '--setup' in sys.argv:
        print('Instalacao concluida. Abra 02_ABRIR.bat na pasta principal.');sys.exit(0)
    try:
        collection_lock=local_lock('collection.lock')
    except SystemExit:
        print('Uma coleta anterior ainda esta ativa; aguarde sua conclusao.')
    else:
        CollectionJob.objects.filter(status__in=['queued','running']).update(status='error',summary='Execucao interrompida. Inicie uma nova coleta.',finished_at=timezone.now())
        collection_lock.close()
    from core.scheduling import start_scheduler
    start_scheduler()
    from waitress import serve
    from automac.wsgi import application
    print('\nAutomac_Royalties: http://127.0.0.1:8766\nMantenha esta janela aberta. Para encerrar, pressione Ctrl+C.\n')
    threading.Timer(1.5,lambda:webbrowser.open('http://127.0.0.1:8766')).start()
    serve(application,host='127.0.0.1',port=8766,threads=4,max_request_body_size=28*1024*1024)
