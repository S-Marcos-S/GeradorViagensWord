@echo off
chcp 65001 >nul
title Criando Executavel Windows (.exe) - Gerador de Viagens
cd /d "%~dp0"

echo ========================================================
echo  Localizando instalacao do Python...
echo ========================================================

set "PYTHON_CMD="

:: 1. Tenta encontrar no PATH do Windows
where py >nul 2>&1 && set "PYTHON_CMD=py"
if "%PYTHON_CMD%"=="" (
    where python >nul 2>&1 && set "PYTHON_CMD=python"
)

:: 2. Tenta encontrar nos caminhos padroes de instalacao do Windows
if "%PYTHON_CMD%"=="" (
    for %%V in (314 313 312 311 310 39 38) do (
        if exist "%LocalAppData%\Programs\Python\Python%%V\python.exe" (
            set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python%%V\python.exe"
            goto :found
        )
        if exist "C:\Python%%V\python.exe" (
            set "PYTHON_CMD=C:\Python%%V\python.exe"
            goto :found
        )
        if exist "%ProgramFiles%\Python%%V\python.exe" (
            set "PYTHON_CMD=%ProgramFiles%\Python%%V\python.exe"
            goto :found
        )
        if exist "%ProgramFiles(x86)%\Python%%V\python.exe" (
            set "PYTHON_CMD=%ProgramFiles(x86)%\Python%%V\python.exe"
            goto :found
        )
    )
    if exist "%LocalAppData%\Microsoft\WindowsApps\python.exe" (
        set "PYTHON_CMD=%LocalAppData%\Microsoft\WindowsApps\python.exe"
        goto :found
    )
)

:found
if "%PYTHON_CMD%"=="" (
    echo [ERRO] O Python nao foi encontrado no seu computador!
    echo.
    echo Por favor, instale o Python em https://www.python.org/downloads/
    echo IMPORTANTE: Durante a instalacao, marque a opcao:
    echo            "Add Python to PATH" ou "Adicionar Python ao PATH"
    echo.
    pause
    exit /b 1
)

echo Python detectado: "%PYTHON_CMD%"
echo.
echo ========================================================
echo  Instalando dependencias (pypdf, python-docx, pyinstaller)...
echo ========================================================
"%PYTHON_CMD%" -m pip install -r requirements.txt

echo.
echo ========================================================
echo  Compilando para executavel unico (.exe)...
echo ========================================================
"%PYTHON_CMD%" -m PyInstaller --noconsole --onefile --add-data "modelo_base.docx;." --name "GeradorViagensWord" app.py

echo.
echo ========================================================
echo  Processo concluido!
echo  O aplicativo executavel esta pronto na pasta:
echo     dist\GeradorViagensWord.exe
echo.
echo  Voce pode copiar o arquivo GeradorViagensWord.exe para
echo  a sua Area de Trabalho ou onde preferir!
echo ========================================================
pause
