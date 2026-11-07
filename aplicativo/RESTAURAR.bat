@echo off
chcp 65001 >nul
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe restore.py
pause
exit /b
:missing
echo Execute 01_INSTALAR.bat (pasta principal) primeiro.
pause
