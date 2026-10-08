@echo off
chcp 65001 >nul
cd /d "%~dp0"
py -3 --version >nul 2>nul && (py -3 server.py & goto fim)
python --version >nul 2>nul && (python server.py & goto fim)
echo.
echo Python nao foi encontrado neste computador.
echo Instale em https://www.python.org/downloads/ marcando a opcao "Add python.exe to PATH" e abra este arquivo de novo.
:fim
echo.
pause
