@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe manage.py diagnostico > DIAGNOSTICO_AUTOMAC.txt 2>&1
type DIAGNOSTICO_AUTOMAC.txt
pause
exit /b
:missing
echo Ambiente local nao encontrado. Execute 01_INSTALAR.bat (pasta principal) na primeira instalacao.
pause
