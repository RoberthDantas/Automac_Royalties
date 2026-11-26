"""Offline restore with validation, rollback, and no archive path traversal."""
import shutil
import sqlite3
from contextlib import closing
import tempfile
import zipfile
from pathlib import Path
from launch import local_lock
from django.conf import settings
from core.backup import create_backup


def restore(path):
    root=settings.DATA_DIR
    with tempfile.TemporaryDirectory(dir=root.parent) as tmp:
        staging=Path(tmp)/'validated';staging.mkdir()
        with zipfile.ZipFile(path) as z:
            if sum(i.file_size for i in z.infolist())>5*1024**3:
                raise ValueError('Backup excede o limite de 5 GB.')
            for i in z.infolist():
                dest=(staging/i.filename).resolve()
                if not dest.is_relative_to(staging.resolve()) or '\\' in i.filename or ':' in i.filename or (i.external_attr >> 16)&0o170000==0o120000:
                    raise ValueError('Caminho inseguro no arquivo.')
                if i.is_dir():dest.mkdir(parents=True,exist_ok=True)
                else:
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(i) as src,dest.open('wb') as out:shutil.copyfileobj(src,out)
        db=staging/'automac.sqlite3'
        if not db.exists() or not (staging/'secret.key').is_file():raise ValueError('Backup incompleto.')
        with closing(sqlite3.connect(db)) as conn:
            if conn.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Banco corrompido.')
            tables={r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            if not {'core_opportunity','auth_user','django_migrations'}<=tables:raise ValueError('Banco incompatível.')
        previous=create_backup()
        from django.db import connections
        connections.close_all()
        rollback=Path(tmp)/'old';rollback.mkdir()
        moved=[];installed=[]
        try:
            for child in root.iterdir():
                if child.name not in ('backups','logs') and child.suffix!='.lock':
                    shutil.move(str(child),str(rollback/child.name));moved.append(child.name)
            for child in staging.iterdir():
                if child.name in ('backups','logs') or child.suffix=='.lock':continue
                shutil.move(str(child),str(root/child.name));installed.append(child.name)
        except Exception:
            for name in installed:
                dest=root/name
                if dest.is_dir():shutil.rmtree(dest)
                else:dest.unlink(missing_ok=True)
            for name in moved:shutil.move(str(rollback/name),str(root/name))
            raise
        return previous

if __name__=='__main__':
    lock=local_lock()
    collection_lock=local_lock('collection.lock')
    path=Path(input('Caminho completo do backup ZIP: ').strip().strip('"'))
    if input('Substituir a base atual pelo backup? Digite RESTAURAR: ').strip()!='RESTAURAR':raise SystemExit('Cancelado.')
    print('Restaurado. Cópia anterior preservada em:',restore(path))
