@echo off
chcp 65001 >nul
cd /d "%~dp0"
powershell.exe -NoProfile -File "%~dp0agenda_windows.ps1"
if errorlevel 1 echo Nao foi possivel ativar. Nao altere politicas de seguranca; use INICIAR.bat ou ROTINA_LOCAL.bat e envie o erro para revisao.
pause
