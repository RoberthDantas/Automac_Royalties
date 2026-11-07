"""Executa a agenda da CartoGeo sem abrir janela (usado pelo Agendador de Tarefas do Windows com pythonw.exe).

0.6.0: antes a tarefa usava python.exe e abria uma janela preta a cada 5 minutos. Com pythonw.exe não há
console, então a saída vai para dados\\logs\\agenda_windows.log (os 500 KB mais recentes).
"""
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cartogeo.settings')
data_dir = Path(os.environ.get('CARTOGEO_DATA_DIR', ROOT / 'dados')).resolve()
log_dir = data_dir / 'logs'
log_dir.mkdir(parents=True, exist_ok=True)
log_path = log_dir / 'agenda_windows.log'
if log_path.exists() and log_path.stat().st_size > 500_000:
    log_path.replace(log_dir / 'agenda_windows.anterior.log')
log = open(log_path, 'a', encoding='utf-8', buffering=1)
sys.stdout = sys.stderr = log
print(f'--- {datetime.now():%d/%m/%Y %H:%M:%S}')
try:
    import django
    django.setup()
    from django.core.management import call_command
    call_command('executar_agenda', wait=True)
except SystemExit:
    pass
except Exception:
    traceback.print_exc()
finally:
    log.flush()
