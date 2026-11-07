@echo off
cd /d "%~dp0"
powershell.exe -NoProfile -File "%~dp0agenda_windows.ps1" -Remover
pause
