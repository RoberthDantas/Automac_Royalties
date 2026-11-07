@echo off
chcp 65001 >nul
cd /d "%~dp0aplicativo"
set "CARTOGEO_DATA_DIR=%CD%\dados"
if not exist .venv\Scripts\python.exe goto missing
echo CARTOGEO - TROCAR SENHA, NOME OU DESATIVAR CONTA
echo.
.venv\Scripts\python.exe manage.py alterar_usuario
echo.
pause
exit /b
:missing
echo Execute 01_INSTALAR.bat primeiro, na pasta principal.
pause
