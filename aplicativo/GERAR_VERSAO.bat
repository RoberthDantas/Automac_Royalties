@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo AUTOMAC_ROYALTIES - GERAR NOVA VERSAO (uso do administrador)
echo Antes: escreva documentacao\NOTAS_X.Y.Z.md com o que mudou.
set /p "VER=Numero da nova versao (ex.: 0.6.1): "
".venv\Scripts\python.exe" scripts\gerar_versao.py %VER%
pause
