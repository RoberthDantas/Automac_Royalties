import sqlite3
from contextlib import closing
import tempfile
import zipfile
from pathlib import Path
from datetime import datetime
from django.conf import settings

def create_backup():
    # Travas (*.lock) ficam de fora: no Windows o próprio app as mantém bloqueadas e a leitura falha (0.6.0).
    root=settings.DATA_DIR
    folder=root/'backups';folder.mkdir(exist_ok=True)
    dest=folder/('cartogeo-'+datetime.now().strftime('%Y%m%d-%H%M%S-%f')+'.zip')
    with tempfile.TemporaryDirectory() as tmp:
        db=Path(tmp)/'cartogeo.sqlite3'
        # sqlite3's transaction context does not close connections. Windows needs
        # both handles closed before archiving and removing the temporary file.
        with closing(sqlite3.connect(root/'cartogeo.sqlite3')) as source, closing(sqlite3.connect(db)) as target:
            source.backup(target)
        with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as z:
            z.write(db,'cartogeo.sqlite3')
            for path in root.rglob('*'):
                relative=path.relative_to(root)
                if path.is_file() and not path.is_symlink() and relative.parts[0] not in ('backups','logs') and path.name not in ('cartogeo.sqlite3','cartogeo.sqlite3-wal','cartogeo.sqlite3-shm','cartogeo.sqlite3-journal') and path.suffix!='.lock':
                    z.write(path,str(relative))
    return dest
