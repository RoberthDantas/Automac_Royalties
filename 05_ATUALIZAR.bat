@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo CARTOGEO - ATUALIZAR UMA INSTALACAO EXISTENTE
echo.
echo Use este arquivo de dentro do pacote NOVO, extraido em uma pasta separada.
echo Os dados (oportunidades, contatos, historico) nao sao alterados; o banco ganha uma copia antes.
echo Feche o app antes de continuar.
echo.
set "DESTINO=C:\CartoGeo"
set /p "DESTINO=Pasta da instalacao [C:\CartoGeo]: "
if not exist "%DESTINO%\aplicativo\.venv\Scripts\python.exe" (
  echo Nao encontrei uma instalacao concluida em "%DESTINO%".
  pause
  exit /b 1
)
"%DESTINO%\aplicativo\.venv\Scripts\python.exe" "%~dp0aplicativo\atualizar_instalacao.py" "%DESTINO%"
pause
