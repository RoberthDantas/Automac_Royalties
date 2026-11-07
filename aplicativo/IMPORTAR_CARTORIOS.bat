@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist manage.py goto missing
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe importar_cartorios_cnj.py
if errorlevel 1 goto fail
echo.
echo Voce pode abrir 02_ABRIR.bat e consultar Organizacoes e Contatos.
pause
exit /b 0
:missing
echo Copie o CONTEUDO deste pacote para a pasta aplicativo (a que contem manage.py).
echo Este pacote complementa o aplicativo ja instalado; nao e um instalador completo.
pause
exit /b 1
:fail
echo Copie ou fotografe o erro acima e envie para analise.
pause
exit /b 1
