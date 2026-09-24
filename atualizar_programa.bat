@echo off
title Atualizar Gerador de Viagens pelo GitHub
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PIP_PROGRESS_BAR=off

echo ========================================================
echo   Atualizacao do Gerador de Listas de Viagens
echo   Repositorio: S-Marcos-S/GeradorViagensWord
echo ========================================================
echo.

set PYTHON_CMD=

:: Localiza Python no sistema
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 set PYTHON_CMD=py
if "%PYTHON_CMD%"=="" (
    where python >nul 2>&1
    if %ERRORLEVEL% EQU 0 set PYTHON_CMD=python
)
if "%PYTHON_CMD%"=="" (
    if exist "%LocalAppData%\Programs\Python\Python38-32\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python38-32\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python38\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python38\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python39\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python39\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python310\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python311\python.exe"
    if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python312\python.exe"
    if exist "C:\Python38\python.exe" set "PYTHON_CMD=C:\Python38\python.exe"
    if exist "C:\Python39\python.exe" set "PYTHON_CMD=C:\Python39\python.exe"
    if exist "C:\Python310\python.exe" set "PYTHON_CMD=C:\Python310\python.exe"
    if exist "C:\Python311\python.exe" set "PYTHON_CMD=C:\Python311\python.exe"
    if exist "C:\Python312\python.exe" set "PYTHON_CMD=C:\Python312\python.exe"
)

:: 1. Tenta atualizar via Git se o git estiver instalado e for repo git
where git >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    if exist ".git" (
        echo [1/2] Verificando e atualizando via Git...
        git fetch --all
        git pull origin main
        if %ERRORLEVEL% EQU 0 (
            echo.
            echo ========================================================
            echo  Aplicativo atualizado com sucesso via Git!
            echo ========================================================
            goto :concluido
        )
    )
)

:: 2. Se nao tem git ou git falhou, usa o updater do Python
if not "%PYTHON_CMD%"=="" (
    echo [2/2] Atualizando arquivos do repositorio via script Python...
    "%PYTHON_CMD%" -c "import sys; from core.updater import executar_atualizacao_cli; sys.exit(executar_atualizacao_cli())"
    if %ERRORLEVEL% EQU 0 goto :concluido
)

echo.
echo ========================================================
echo [AVISO] Falha ao atualizar. Verifique sua conexao a internet.
echo ========================================================
pause
exit /b 1

:concluido
echo.
echo O aplicativo esta atualizado e pronto para uso!
echo Voce ja pode abrir o programa normalmente.
echo ========================================================
pause
