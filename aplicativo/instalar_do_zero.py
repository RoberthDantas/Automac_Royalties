"""Instalação nova sem importar arquivos de instalações anteriores."""
from pathlib import Path
import os,subprocess,sys,traceback
ROOT=Path(__file__).resolve().parent

def main():
    if not (3,12)<=sys.version_info[:2]<=(3,14):raise RuntimeError('Use Python 3.12, 3.13 ou 3.14.')
    os.chdir(ROOT)
    # Data always belongs to this extracted folder, regardless of previous setup.
    os.environ['AUTOMAC_DATA_DIR']=str(ROOT/'dados')
    python=ROOT/'.venv'/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    print('\n[1/4] Preparando o Python local...',flush=True)
    if not python.is_file():subprocess.run([sys.executable,'-m','venv',str(ROOT/'.venv')],check=True)
    print('\n[2/4] Instalando dependências. Aguarde; precisa de internet.',flush=True)
    subprocess.run([str(python),'-m','pip','install','-r',str(ROOT/'requirements.txt')],check=True)
    print('\n[3/4] Preparando a base de dados (pode levar alguns minutos).',flush=True)
    subprocess.run([str(python),'launch.py','--setup'],check=True)
    print('\n[4/4] Conta de acesso.',flush=True)
    subprocess.run([str(python),'manage.py','criar_usuario','--opcional'],check=True)
    print('\nINSTALAÇÃO CONCLUÍDA. Feche esta janela e abra 02_ABRIR.bat na pasta principal.',flush=True)

if __name__=='__main__':
    try:main()
    except (Exception,KeyboardInterrupt):
        error=traceback.format_exc();(ROOT.parent/'ERRO_INSTALACAO.txt').write_text(error,encoding='utf-8')
        print('\nA instalação foi interrompida. Envie a foto desta janela e ERRO_INSTALACAO.txt.\n'+error)
        print('Você pode executar 01_INSTALAR.bat novamente para continuar. Não apague arquivos.')
        sys.exit(1)
