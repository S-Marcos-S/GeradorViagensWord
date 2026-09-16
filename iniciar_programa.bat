@echo off
title Gerador de Listas de Viagens
cd /d "%~dp0"

:: Configura encoding e desliga barra de progresso do pip
set PYTHONIOENCODING=utf-8
set PIP_PROGRESS_BAR=off

echo ========================================================
echo  Iniciando o Gerador de Listas de Viagens...
echo ========================================================
echo.

set PYTHON_CMD=

:: 1. Tenta encontrar no PATH do Windows
where py >nul 2>&1
if %ERRORLEVEL% EQU 0 set PYTHON_CMD=py

if not "%PYTHON_CMD%"=="" goto :python_found

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 set PYTHON_CMD=python

if not "%PYTHON_CMD%"=="" goto :python_found

:: 2. Tenta encontrar nos caminhos padroes de instalacao
if exist "%LocalAppData%\Programs\Python\Python38-32\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python38-32\python.exe" & goto :python_found
if exist "%LocalAppData%\Programs\Python\Python38\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python38\python.exe" & goto :python_found
if exist "%LocalAppData%\Programs\Python\Python39\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python39\python.exe" & goto :python_found
if exist "%LocalAppData%\Programs\Python\Python310\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python310\python.exe" & goto :python_found
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python311\python.exe" & goto :python_found
if exist "%LocalAppData%\Programs\Python\Python312\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python312\python.exe" & goto :python_found
if exist "%LocalAppData%\Programs\Python\Python313\python.exe" set "PYTHON_CMD=%LocalAppData%\Programs\Python\Python313\python.exe" & goto :python_found

if exist "C:\Python38\python.exe" set "PYTHON_CMD=C:\Python38\python.exe" & goto :python_found
if exist "C:\Python39\python.exe" set "PYTHON_CMD=C:\Python39\python.exe" & goto :python_found
if exist "C:\Python310\python.exe" set "PYTHON_CMD=C:\Python310\python.exe" & goto :python_found
if exist "C:\Python311\python.exe" set "PYTHON_CMD=C:\Python311\python.exe" & goto :python_found
if exist "C:\Python312\python.exe" set "PYTHON_CMD=C:\Python312\python.exe" & goto :python_found

if exist "%ProgramFiles%\Python38\python.exe" set "PYTHON_CMD=%ProgramFiles%\Python38\python.exe" & goto :python_found
if exist "%ProgramFiles%\Python39\python.exe" set "PYTHON_CMD=%ProgramFiles%\Python39\python.exe" & goto :python_found
if exist "%ProgramFiles%\Python310\python.exe" set "PYTHON_CMD=%ProgramFiles%\Python310\python.exe" & goto :python_found
if exist "%ProgramFiles%\Python311\python.exe" set "PYTHON_CMD=%ProgramFiles%\Python311\python.exe" & goto :python_found
if exist "%ProgramFiles%\Python312\python.exe" set "PYTHON_CMD=%ProgramFiles%\Python312\python.exe" & goto :python_found

if exist "%LocalAppData%\Microsoft\WindowsApps\python.exe" set "PYTHON_CMD=%LocalAppData%\Microsoft\WindowsApps\python.exe" & goto :python_found

:: Se nao encontrou o Python
echo ====================================================================
echo [AVISO] O Python ainda nao esta instalado no seu computador!
echo ====================================================================
echo.
echo Para Windows 7:
echo   1. Acesse: https://www.python.org/downloads/release/python-3810/
echo   2. Baixe o instalador do Python 3.8.10
echo   3. ATENCAO: Na primeira tela da instalacao, marque a opcao:
echo      Add Python to PATH
echo   4. Clique em Install Now
echo.
echo Para Windows 10 ou 11:
echo   1. Acesse: https://www.python.org/downloads/
echo   2. Baixe a versao mais recente e marque Add Python to PATH
echo.
echo Depois de instalar, e so abrir este arquivo novamente!
echo ====================================================================
echo.
pause
exit /b 1

:python_found
echo Python localizado com sucesso: "%PYTHON_CMD%"
"%PYTHON_CMD%" --version
echo.

:: Verifica se as dependencias ja estao instaladas
"%PYTHON_CMD%" -c "import pypdf, docx" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto :launch_app

echo Instalando dependencias necessarias (pypdf, python-docx)...
if exist "wheels" goto :install_offline

:: Instalacao online com trusted-host
"%PYTHON_CMD%" -m pip install -r requirements.txt --progress-bar off --trusted-host pypi.org --trusted-host files.pythonhosted.org
goto :check_install

:install_offline
echo Instalando pacotes da pasta local 'wheels' (Modo Offline)...
"%PYTHON_CMD%" -m pip install --no-index --find-links=wheels -r requirements.txt --progress-bar off

:check_install
if %ERRORLEVEL% EQU 0 goto :launch_app

echo.
echo ========================================================
echo [ERRO] Nao foi possivel instalar as dependencias!
echo Se este computador nao tiver internet, utilize o script
echo 'baixar_pacotes_para_windows7.bat' no Windows 11 para
echo gerar a pasta 'wheels' e copiar para este computador.
echo ========================================================
pause
exit /b 1

:launch_app
echo Abrindo o aplicativo...
"%PYTHON_CMD%" app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo Ocorreu um erro ao executar o aplicativo.
    echo ========================================================
    pause
)
