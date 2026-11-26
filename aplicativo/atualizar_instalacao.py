"""Aplica este pacote como atualização sobre uma instalação existente do Automac_Royalties, sem tocar nos dados.

Uso (pelo 05_ATUALIZAR.bat da pasta principal deste pacote):
    python atualizar_instalacao.py "C:\\Automac_Royalties"

O que faz, em ordem:
 1. confere que o destino é uma instalação do Automac_Royalties e que o app está fechado;
 2. copia o banco atual para dados\\backups\\antes_da_atualizacao_<versão>_<data>.sqlite3;
 3. copia os arquivos do programa por cima (nunca a pasta dados nem o .venv);
 4. atualiza as dependências e roda o preparo (migrações), que faz outro backup se o banco mudar.
"""
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SOURCE = Path(__file__).resolve().parent.parent          # pasta principal deste pacote
SKIP_DIRS = {'dados', '.venv', '__pycache__', '.git', 'dist'}


def version_of(root):
    try:
        text = (root / 'aplicativo' / 'automac' / 'settings.py').read_text(encoding='utf-8')
        return re.search(r"VERSION = '([^']+)'", text).group(1)
    except (OSError, AttributeError):
        return '?'


def app_is_open(data_dir):
    lock = data_dir / 'runtime.lock'
    if not lock.exists():
        return False
    try:
        handle = lock.open('a+b')
    except OSError:
        return True
    try:
        handle.seek(0)
        if os.name == 'nt':
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            fcntl.flock(handle, fcntl.LOCK_UN)
        return False
    except OSError:
        return True
    finally:
        handle.close()


def copy_program(src, dst):
    count = 0
    for folder, dirs, files in os.walk(src):
        rel = Path(folder).relative_to(src)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        (dst / rel).mkdir(parents=True, exist_ok=True)
        for name in files:
            if name.endswith('.pyc'):
                continue
            shutil.copy2(Path(folder) / name, dst / rel / name)
            count += 1
    return count


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Informe a pasta da instalação (a que tem 02_ABRIR.bat).')
    dest = Path(sys.argv[1].strip().strip('"')).resolve()
    if dest == SOURCE:
        raise SystemExit('Esta já é a pasta instalada. Extraia o pacote de atualização em outra pasta e rode 05_ATUALIZAR.bat de lá.')
    app = dest / 'aplicativo'
    python = app / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if not (dest / '02_ABRIR.bat').exists() or not (app / 'manage.py').exists():
        raise SystemExit(f'Não encontrei uma instalação do Automac_Royalties em {dest}.')
    if not python.exists():
        raise SystemExit('Essa instalação ainda não foi concluída. Rode 01_INSTALAR.bat nela primeiro.')
    data_dir = app / 'dados'
    if app_is_open(data_dir):
        raise SystemExit('O app está aberto. Feche a janela preta do 02_ABRIR.bat (Ctrl+C) e rode de novo.')
    old, new = version_of(dest), version_of(SOURCE)
    print(f'Atualizando {dest}\n  de {old} para {new}')

    db = data_dir / 'automac.sqlite3'
    if db.exists():
        backups = data_dir / 'backups'
        backups.mkdir(parents=True, exist_ok=True)
        target = backups / f'antes_da_atualizacao_{new}_{datetime.now():%Y%m%d_%H%M%S}.sqlite3'
        shutil.copy2(db, target)
        print(f'[1/3] Cópia do banco: {target}')
    else:
        print('[1/3] Banco ainda não existe; nada a copiar.')

    n = copy_program(SOURCE, dest)
    print(f'[2/3] Programa copiado: {n} arquivos (a pasta dados não foi tocada).')

    env = dict(os.environ, AUTOMAC_DATA_DIR=str(data_dir), PYTHONUTF8='1')
    print('[3/3] Dependências e preparo da base. Precisa de internet.')
    subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check', '-q', '-r', 'requirements.txt'],
                   cwd=app, env=env, check=True)
    subprocess.run([str(python), 'launch.py', '--setup'], cwd=app, env=env, check=True)
    print(f'\nATUALIZAÇÃO CONCLUÍDA ({old} -> {new}). Abra 02_ABRIR.bat na pasta {dest}.')


if __name__ == '__main__':
    try:
        main()
    except subprocess.CalledProcessError as exc:
        raise SystemExit(f'Um passo falhou (código {exc.returncode}). A cópia do banco está em dados\\backups. Nada foi apagado.')
