@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo CARTOGEO 0.6.0 - INSTALACAO
echo Execute somente depois de extrair o ZIP para uma pasta nova.
py -3.14 -c "import sys;print('CGOK' if sys.version_info[:2]==(3,14) else 'NAO')" 2>nul | findstr CGOK >nul
if not errorlevel 1 goto py314
py -3.13 -c "import sys;print('CGOK' if sys.version_info[:2]==(3,13) else 'NAO')" 2>nul | findstr CGOK >nul
if not errorlevel 1 goto py313
py -3.12 -c "import sys;print('CGOK' if sys.version_info[:2]==(3,12) else 'NAO')" 2>nul | findstr CGOK >nul
if not errorlevel 1 goto py312
python -c "import sys;print('CGOK' if (3,12)<=sys.version_info[:2]<=(3,14) else 'NAO')" 2>nul | findstr CGOK >nul
if errorlevel 1 goto missing
python aplicativo\instalar_do_zero.py
goto end
:py314
py -3.14 aplicativo\instalar_do_zero.py
goto end
:py313
py -3.13 aplicativo\instalar_do_zero.py
goto end
:py312
py -3.12 aplicativo\instalar_do_zero.py
goto end
:missing
echo Python 3.12, 3.13 ou 3.14 nao encontrado.
echo Pythons encontrados neste computador:
python --version 2>&1
py list 2>nul
echo Instale o Python ou envie uma foto desta janela para orientacao.
:end
pause
