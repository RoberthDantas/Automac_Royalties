@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe goto fail
echo Agenda local ativa. Mantenha esta janela aberta. Ctrl+C para encerrar.
:loop
.venv\Scripts\python.exe manage.py executar_agenda --wait
timeout /t 30 /nobreak >nul
goto loop
:fail
echo Execute INSTALAR.bat antes.
pause
