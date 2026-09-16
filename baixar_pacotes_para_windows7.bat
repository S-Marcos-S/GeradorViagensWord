@echo off
title Baixar Pacotes Offline para Windows 7 (Python 3.8 32-bit)
cd /d "%~dp0"

echo ========================================================
echo  Baixando pacotes para instalacao offline no Windows 7
echo ========================================================
echo.
echo Este script deve ser executado no computador com internet (ex: Windows 11).
echo Ele vai baixar os instaladores (.whl) compativeis com Python 3.8 32-bit
echo para a pasta 'wheels'.
echo.
echo Depois, basta copiar a pasta do projeto (com a pasta 'wheels')
echo no pendrive para o Windows 7!
echo.

if not exist "wheels" mkdir wheels

where py >nul 2>&1 && set "PY_CMD=py"
if "%PY_CMD%"=="" where python >nul 2>&1 && set "PY_CMD=python"
if "%PY_CMD%"=="" (
    echo [ERRO] Python nao encontrado neste computador!
    pause
    exit /b 1
)

echo Baixando dependencias para a pasta 'wheels'...
"%PY_CMD%" -m pip download -d wheels --platform win32 --python-version 38 --implementation cp --abi cp38 --only-binary=:all: pypdf python-docx pyinstaller lxml typing-extensions --trusted-host pypi.org --trusted-host files.pythonhosted.org

echo.
echo ========================================================
echo Concluido! Os pacotes estao salvos na pasta 'wheels'.
echo Agora copie a pasta do projeto para o Windows 7 e execute
echo 'iniciar_programa.bat' ou 'gerar_executavel.bat'.
echo ========================================================
pause
