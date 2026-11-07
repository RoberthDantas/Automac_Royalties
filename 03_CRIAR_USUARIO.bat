@echo off
chcp 65001 >nul
cd /d "%~dp0aplicativo"
set "CARTOGEO_DATA_DIR=%CD%\dados"
if not exist .venv\Scripts\python.exe goto missing
echo CARTOGEO - CRIAR CONTA DE ACESSO
echo.
.venv\Scripts\python.exe manage.py criar_usuario
echo.
pause
exit /b
:missing
echo Execute 01_INSTALAR.bat primeiro, na pasta principal.
pause
