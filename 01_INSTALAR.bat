@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo CARTOGEO 0.5.3 - INSTALACAO
echo Execute somente depois de extrair o ZIP para uma pasta nova.
py -3.14 --version >nul 2>&1
if not errorlevel 1 goto py314
py -3.13 --version >nul 2>&1
if not errorlevel 1 goto py313
py -3.12 --version >nul 2>&1
if not errorlevel 1 goto py312
python -c "import sys;sys.exit(0 if (3,12)<=sys.version_info[:2]<=(3,14) else 1)" >nul 2>&1
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
echo Instale o Python ou envie uma foto desta janela para orientacao.
:end
pause
