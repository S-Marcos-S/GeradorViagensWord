@echo off
title Criando Executavel Windows (.exe) - Gerador de Viagens
cd /d "%~dp0"

:: Configura encoding e desliga barra de progresso do pip para nao travar no Windows 7
set PYTHONIOENCODING=utf-8
set PIP_PROGRESS_BAR=off

echo ========================================================
echo  Localizando instalacao do Python...
echo ========================================================

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
echo [ERRO] O Python nao foi encontrado no seu computador!
echo.
echo Para Windows 7, instale o Python 3.8.10:
echo   https://www.python.org/downloads/release/python-3810/
echo IMPORTANTE: Durante a instalacao, marque a opcao Add Python to PATH.
echo.
pause
exit /b 1

:python_found
echo Python detectado: "%PYTHON_CMD%"
"%PYTHON_CMD%" --version
echo.

echo ========================================================
echo  Instalando dependencias (pypdf, python-docx, pyinstaller)...
echo ========================================================

if exist "wheels" goto :install_offline

:: Instalacao online com trusted-host
"%PYTHON_CMD%" -m pip install -r requirements.txt --progress-bar off --trusted-host pypi.org --trusted-host files.pythonhosted.org
goto :check_pip

:install_offline
echo Instalando pacotes da pasta local 'wheels' (Modo Offline)...
"%PYTHON_CMD%" -m pip install --no-index --find-links=wheels -r requirements.txt --progress-bar off

:check_pip
if %ERRORLEVEL% EQU 0 goto :check_pyinstaller

echo.
echo ========================================================
echo [ERRO] Falha ao instalar as dependencias via pip!
echo ========================================================
echo Possiveis causas no Windows 7:
echo  1. Computador sem internet ou bloqueando conexao ao PyPI.
echo     DICA: Voce pode usar o script 'baixar_pacotes_para_windows7.bat'
echo     no Windows 11 para baixar a pasta 'wheels' e copiar no pendrive!
echo  2. Certificados SSL desatualizados do Windows 7.
echo  3. Falta do Microsoft Visual C++ 2015-2022 (x86).
echo ========================================================
pause
exit /b 1

:check_pyinstaller
"%PYTHON_CMD%" -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto :compile_exe

echo.
echo ========================================================
echo [AVISO] PyInstaller nao detectado. Tentando instalacao direta...
echo ========================================================
"%PYTHON_CMD%" -m pip install pyinstaller --progress-bar off --trusted-host pypi.org --trusted-host files.pythonhosted.org
"%PYTHON_CMD%" -c "import PyInstaller" >nul 2>&1
if %ERRORLEVEL% EQU 0 goto :compile_exe

echo.
echo [ERRO] Nao foi possivel instalar o PyInstaller!
pause
exit /b 1

:compile_exe
echo.
echo ========================================================
echo  Compilando para executavel unico (.exe)...
echo ========================================================
"%PYTHON_CMD%" -m PyInstaller --noconsole --onefile --add-data "modelo_base.docx;." --name "GeradorViagensWord" app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo [ERRO] Ocorreu uma falha durante a compilacao do executavel!
    echo ========================================================
    pause
    exit /b 1
)

if not exist "dist\GeradorViagensWord.exe" (
    echo.
    echo ========================================================
    echo [ERRO] O arquivo dist\GeradorViagensWord.exe nao foi gerado!
    echo ========================================================
    pause
    exit /b 1
)

echo.
echo ========================================================
echo  Processo concluido com sucesso!
echo  O aplicativo executavel esta pronto na pasta:
echo     dist\GeradorViagensWord.exe
echo.
echo  Voce pode copiar o arquivo GeradorViagensWord.exe para
echo  a sua Area de Trabalho ou onde preferir!
echo ========================================================
pause
