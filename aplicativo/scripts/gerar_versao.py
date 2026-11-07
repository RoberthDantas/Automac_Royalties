"""Gera uma versão nova da CartoGeo: confere, testa e empacota.

Uso (de dentro da pasta aplicativo, com o Python do .venv):
    .venv\\Scripts\\python.exe scripts\\gerar_versao.py 0.6.1
    .venv\\Scripts\\python.exe scripts\\gerar_versao.py 0.6.1 --com-dados C:\\CartoGeo\\aplicativo\\dados

Passos:
 1. confere o número (X.Y.Z) e se existe documentacao/NOTAS_X.Y.Z.md;
 2. avisa se há alterações sem commit no Git;
 3. grava o número em settings.py, 01_INSTALAR.bat e COMECE_AQUI.txt;
 4. roda todos os testes (para se algum falhar);
 5. gera em dist/:
    - CartoGeo_X.Y.Z_atualizacao.zip  -> só o programa; serve para 05_ATUALIZAR.bat
    - CartoGeo_X.Y.Z_completo.zip     -> programa + uma cópia da base (só com --com-dados), para instalar do zero
    - o SHA-256 de cada ZIP.
 Depois: git commit, git tag vX.Y.Z e git push (o script mostra os comandos).
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
ROOT = APP.parent
SKIP_DIRS = {'.venv', '__pycache__', '.git', 'dist', 'dados'}
SKIP_FILES = {'.gitignore', '.gitattributes'}
# Na cópia da base: nunca a chave secreta, travas, logs ou backups da máquina de origem.
DATA_SKIP = {'secret.key', 'runtime.lock', 'collection.lock', 'scheduler.lock', 'dispatch.lock'}
DATA_SKIP_DIRS = {'logs', 'backups'}


def set_version(version):
    edits = [
        (APP / 'cartogeo' / 'settings.py', r"VERSION = '[^']+'", f"VERSION = '{version}'"),
        (ROOT / '01_INSTALAR.bat', r'CARTOGEO [0-9.]+ - INSTALACAO', f'CARTOGEO {version} - INSTALACAO'),
        (ROOT / 'COMECE_AQUI.txt', r'CARTOGEO [0-9.]+ — COMECE AQUI', f'CARTOGEO {version} — COMECE AQUI'),
    ]
    for path, pattern, repl in edits:
        raw = path.read_bytes()
        text = raw.decode('utf-8')
        new, n = re.subn(pattern, repl, text, count=1)
        if n != 1:
            raise SystemExit(f'Não achei o número da versão em {path.name}.')
        path.write_bytes(new.encode('utf-8'))


def program_files():
    for folder, dirs, files in os.walk(ROOT):
        rel = Path(folder).relative_to(ROOT)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not (rel == Path('.') and d == 'dist'))
        for name in sorted(files):
            if name in SKIP_FILES or name.endswith('.pyc'):
                continue
            yield Path(folder) / name, Path('CartoGeo') / rel / name


def data_files(data_dir):
    for folder, dirs, files in os.walk(data_dir):
        rel = Path(folder).relative_to(data_dir)
        dirs[:] = sorted(d for d in dirs if not (rel == Path('.') and d in DATA_SKIP_DIRS))
        for name in sorted(files):
            if name in DATA_SKIP or name.endswith(('-wal', '-shm', '-journal')):
                continue
            yield Path(folder) / name, Path('CartoGeo/aplicativo/dados') / rel / name


def write_zip(target, entries):
    target.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for src, arc in entries:
            z.write(src, arc.as_posix())
            n += 1
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    target.with_suffix('.zip.sha256').write_text(f'{digest}  {target.name}\n', encoding='ascii')
    return n, digest


def git(*args):
    try:
        return subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, check=False).stdout.strip()
    except FileNotFoundError:
        return None


def main():
    ap = argparse.ArgumentParser(description='Gera uma versão nova da CartoGeo.')
    ap.add_argument('versao', help='Número no formato X.Y.Z, ex.: 0.6.1')
    ap.add_argument('--com-dados', metavar='PASTA', help='Pasta dados de uma instalação, para gerar também o pacote completo.')
    ap.add_argument('--sem-testes', action='store_true', help='Pula os testes (não recomendado).')
    a = ap.parse_args()
    if not re.fullmatch(r'\d+\.\d+\.\d+', a.versao):
        raise SystemExit('Use o formato X.Y.Z, ex.: 0.6.1')
    notes = APP / 'documentacao' / f'NOTAS_{a.versao}.md'
    if not notes.exists():
        raise SystemExit(f'Escreva antes as notas da versão em {notes.relative_to(ROOT)} (o que mudou e como atualizar).')
    status = git('status', '--porcelain')
    if status:
        print('Aviso: há alterações sem commit no Git. Elas entram no pacote:\n' + status + '\n')

    set_version(a.versao)
    print(f'[1/3] Versão {a.versao} gravada em settings.py, 01_INSTALAR.bat e COMECE_AQUI.txt.')

    if not a.sem_testes:
        env = dict(os.environ, PYTHONUTF8='1')
        result = subprocess.run([sys.executable, 'manage.py', 'test', 'core', '-v', '1'], cwd=APP, env=env)
        if result.returncode:
            raise SystemExit('Testes falharam. Nada foi empacotado.')
    print('[2/3] Testes aprovados.' if not a.sem_testes else '[2/3] Testes pulados.')

    dist = ROOT / 'dist'
    up = dist / f'CartoGeo_{a.versao}_atualizacao.zip'
    n, digest = write_zip(up, program_files())
    print(f'[3/3] {up.relative_to(ROOT)}: {n} arquivos · SHA-256 {digest}')
    if a.com_dados:
        data_dir = Path(a.com_dados).resolve()
        if not (data_dir / 'cartogeo.sqlite3').exists():
            raise SystemExit(f'Não achei cartogeo.sqlite3 em {data_dir}.')
        full = dist / f'CartoGeo_{a.versao}_completo.zip'
        n, digest = write_zip(full, list(program_files()) + list(data_files(data_dir)))
        print(f'      {full.relative_to(ROOT)}: {n} arquivos · SHA-256 {digest}')
        print('      Atenção: o pacote completo leva contatos e histórico. Guarde e envie só por canal restrito.')
    print(f'\nPróximos passos:\n  git add -A\n  git commit -m "CartoGeo {a.versao}"\n  git tag v{a.versao}\n  git push --follow-tags')


if __name__ == '__main__':
    main()
