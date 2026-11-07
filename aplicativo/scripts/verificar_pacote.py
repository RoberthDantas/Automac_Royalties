"""python verificar_pacote.py caminho/do/pacote.zip -- checks integrity, not authenticity."""
import sys,json,hashlib,zipfile
from pathlib import PurePosixPath

def verify(path):
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if len(names)!=len(set(names)):raise ValueError('Entradas duplicadas no ZIP.')
        raw=z.read('MANIFESTO.json');expected=z.read('MANIFESTO.sha256').decode().split()[0]
        if hashlib.sha256(raw).hexdigest()!=expected:raise ValueError('Manifesto divergente.')
        records=json.loads(raw)['files'];listed=[x['path'] for x in records]
        if len(listed)!=len(set(listed)):raise ValueError('Manifesto com caminhos duplicados.')
        if set(names)!=set(listed)|{'MANIFESTO.json','MANIFESTO.sha256'}:raise ValueError('Arquivo extra ou ausente.')
        for item in records:
            p=PurePosixPath(item['path'])
            if p.is_absolute() or '..' in p.parts:raise ValueError('Caminho inseguro.')
            content=z.read(item['path'])
            if len(content)!=item['size'] or hashlib.sha256(content).hexdigest()!=item['sha256']:raise ValueError('Integridade divergente: '+item['path'])
    return len(records)
if __name__=='__main__':
    try:print(f'Integridade conferida: {verify(sys.argv[1])} arquivos. Não comprova autoria, data original nem veracidade da fonte.')
    except Exception as e:print('FALHA:',e);sys.exit(1)
