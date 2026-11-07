@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe manage.py diagnostico > DIAGNOSTICO_CARTOGEO.txt 2>&1
type DIAGNOSTICO_CARTOGEO.txt
pause
exit /b
:missing
echo Ambiente local nao encontrado. Execute INSTALAR.bat na primeira instalacao.
pause
