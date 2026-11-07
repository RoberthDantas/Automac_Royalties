@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe manage.py varrer_editais
pause
exit /b
:missing
echo Instale ou atualize o aplicativo antes de executar este comando.
pause
