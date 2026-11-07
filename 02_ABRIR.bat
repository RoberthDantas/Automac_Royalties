@echo off
chcp 65001 >nul
cd /d "%~dp0aplicativo"
set "CARTOGEO_DATA_DIR=%CD%\dados"
if not exist .venv\Scripts\python.exe goto missing
.venv\Scripts\python.exe launch.py
pause
exit /b
:missing
echo Volte para a pasta principal e execute 01_INSTALAR.bat primeiro.
pause
