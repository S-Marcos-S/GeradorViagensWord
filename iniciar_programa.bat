@echo off
chcp 65001 >nul
title Gerador de Listas de Viagens
cd /d "%~dp0"

echo ========================================================
echo  Iniciando o Gerador de Listas de Viagens...
echo ========================================================
echo.

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
    echo ====================================================================
    echo [AVISO] O Python ainda nao esta instalado no seu computador!
    echo ====================================================================
    echo.
    echo Para instalar em 1 minuto, faca uma das opcoes abaixo:
    echo.
    echo OPCAO 1 (Mais facil - Microsoft Store):
    echo   1. Abra o Menu Iniciar e digite: cmd
    echo   2. Na tela preta, digite: python
    echo   3. A loja da Microsoft (Microsoft Store) vai abrir sozinha na pagina
    echo      do Python. Basta clicar no botao "Obter" ou "Instalar".
    echo.
    echo OPCAO 2 (Site oficial):
    echo   1. Acesse: https://www.python.org/downloads/
    echo   2. Baixe o instalador do Python.
    echo   3. ATENCAO: Na primeira tela da instalacao, marque a caixinha:
    echo      [X] "Add python.exe to PATH"  (Adicionar Python ao PATH)
    echo   4. Clique em "Install Now".
    echo.
    echo Depois de instalar, e so abrir este arquivo novamente!
    echo ====================================================================
    echo.
    pause
    exit /b 1
)

echo Python localizado com sucesso: "%PYTHON_CMD%"
echo.
echo Verificando dependencias necessarias...
"%PYTHON_CMD%" -m pip install -r requirements.txt >nul 2>&1

echo Abrindo o aplicativo...
"%PYTHON_CMD%" app.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Ocorreu um erro ao executar o aplicativo.
    pause
)
