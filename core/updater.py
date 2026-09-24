import os
import sys
import json
import shutil
import tempfile
import zipfile
import subprocess
import ssl
import urllib.request
import urllib.error
from typing import Tuple, Optional, Callable

GITHUB_REPO = "S-Marcos-S/GeradorViagensWord"
GITHUB_BRANCH = "main"
GITHUB_API_LATEST_RELEASE = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
GITHUB_ZIP_URL = f"https://github.com/{GITHUB_REPO}/archive/refs/heads/{GITHUB_BRANCH}.zip"
APP_NAME = "GeradorViagensWord"

def is_frozen() -> bool:
    """Retorna True se estiver rodando como executável compilado (ex: PyInstaller)."""
    return getattr(sys, "frozen", False)

def get_project_dir() -> str:
    """Retorna o diretório raiz do projeto/executável."""
    if is_frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # Se for script Python, a raiz é o diretório pai de core/ ou o diretório de app.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent = os.path.dirname(current_dir)
        if os.path.isfile(os.path.join(parent, "app.py")):
            return parent
        return current_dir

def _get_ssl_context():
    """Cria contexto SSL com fallback para compatibilidade com certificados de Windows 7."""
    try:
        return ssl.create_default_context()
    except Exception:
        return ssl._create_unverified_context()

def _abrir_url(url: str, headers: Optional[dict] = None, timeout: int = 30):
    """Abre uma requisição HTTP/HTTPS com suporte a headers e fallback de SSL."""
    req_headers = {
        "User-Agent": "GeradorViagensWord-Updater/1.1",
        "Accept": "application/vnd.github.v3+json"
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    try:
        return urllib.request.urlopen(req, context=_get_ssl_context(), timeout=timeout)
    except (ssl.SSLError, urllib.error.URLError):
        unverified_ctx = ssl._create_unverified_context()
        return urllib.request.urlopen(req, context=unverified_ctx, timeout=timeout)

def _download_file(url: str, dest_path: str, progress_callback: Optional[Callable[[str, float], None]] = None) -> bool:
    """Faz download de um arquivo com streaming e relatório de progresso (0.0 a 100.0)."""
    with _abrir_url(url) as response:
        total_size = response.getheader("Content-Length")
        total_bytes = int(total_size) if total_size and total_size.isdigit() else 0
        downloaded = 0
        chunk_size = 64 * 1024

        with open(dest_path, "wb") as out_f:
            while True:
                chunk = response.read(chunk_size)
                if not chunk:
                    break
                out_f.write(chunk)
                downloaded += len(chunk)
                if progress_callback:
                    if total_bytes > 0:
                        pct = (downloaded / total_bytes) * 100.0
                        mb_down = downloaded / (1024 * 1024)
                        mb_tot = total_bytes / (1024 * 1024)
                        progress_callback(f"Baixando: {mb_down:.1f} MB / {mb_tot:.1f} MB ({pct:.0f}%)", pct)
                    else:
                        mb_down = downloaded / (1024 * 1024)
                        progress_callback(f"Baixando: {mb_down:.1f} MB...", -1)
    return True

def verificar_release_executavel() -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Consulta o GitHub Releases para verificar se há executável disponível.
    Retorna (tem_asset, download_url, tag_name).
    """
    try:
        with _abrir_url(GITHUB_API_LATEST_RELEASE, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tag_name = data.get("tag_name", "latest")
            assets = data.get("assets", [])
            for asset in assets:
                name = asset.get("name", "").lower()
                if name.endswith(".exe"):
                    return True, asset.get("browser_download_url"), tag_name
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return False, None, None
    except Exception:
        pass
    return False, None, None

def atualizar_codigo_fonte(progress_callback: Optional[Callable[[str, float], None]] = None) -> Tuple[bool, str]:
    """
    Atualiza o código fonte do programa (quando rodando via Python ou .bat).
    1º Tenta via Git pull.
    2º Se falhar ou não tiver git, baixa o zip da branch main do GitHub e substitui os arquivos.
    """
    project_dir = get_project_dir()
    
    # 1. Tentativa via Git
    git_dir = os.path.join(project_dir, ".git")
    if os.path.isdir(git_dir):
        if progress_callback:
            progress_callback("Atualizando repositório via Git...", 30)
        try:
            res_fetch = subprocess.run(["git", "fetch", "--all"], cwd=project_dir, capture_output=True, text=True)
            if res_fetch.returncode == 0:
                res_pull = subprocess.run(["git", "pull", "origin", GITHUB_BRANCH], cwd=project_dir, capture_output=True, text=True)
                if res_pull.returncode == 0:
                    if progress_callback:
                        progress_callback("Código atualizado com sucesso via Git!", 100)
                    return True, "Repositório atualizado com sucesso via Git!"
        except Exception:
            pass

    # 2. Tentativa via download do ZIP do repositório
    if progress_callback:
        progress_callback("Baixando última versão do GitHub (.zip)...", 10)

    temp_zip = os.path.join(tempfile.gettempdir(), f"gerador_update_{os.getpid()}.zip")
    try:
        _download_file(GITHUB_ZIP_URL, temp_zip, progress_callback)
        if progress_callback:
            progress_callback("Extraindo e atualizando arquivos...", 90)

        with zipfile.ZipFile(temp_zip, "r") as zf:
            root_prefix = None
            for name in zf.namelist():
                if "/" in name and root_prefix is None:
                    root_prefix = name.split("/")[0] + "/"
                    break

            for member in zf.infolist():
                filename = member.filename
                if root_prefix and filename.startswith(root_prefix):
                    rel_path = filename[len(root_prefix):]
                else:
                    rel_path = filename

                if not rel_path or rel_path.startswith(".git"):
                    continue

                target_file = os.path.join(project_dir, rel_path)
                if member.is_dir():
                    os.makedirs(target_file, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_file), exist_ok=True)
                    with zf.open(member) as source, open(target_file, "wb") as target:
                        shutil.copyfileobj(source, target)

        if progress_callback:
            progress_callback("Arquivos atualizados com sucesso!", 100)
        return True, "Arquivos do aplicativo atualizados com sucesso pelo GitHub!"
    except Exception as e:
        return False, f"Falha ao baixar/extrair arquivos: {e}"
    finally:
        if os.path.exists(temp_zip):
            try:
                os.remove(temp_zip)
            except Exception:
                pass

def aplicar_atualizacao_executavel(download_url: str, progress_callback: Optional[Callable[[str, float], None]] = None) -> Tuple[bool, str]:
    """
    Baixa o novo executável e cria script para substituir o .exe em disco no mesmo lugar e reiniciar.
    """
    target_exe = os.path.abspath(sys.executable)
    temp_new_exe = target_exe + ".new"

    if progress_callback:
        progress_callback("Baixando novo executável do GitHub...", 5)

    try:
        _download_file(download_url, temp_new_exe, progress_callback)
    except Exception as e:
        return False, f"Erro ao baixar executável: {e}"

    if not os.path.exists(temp_new_exe) or os.path.getsize(temp_new_exe) == 0:
        return False, "O arquivo do executável baixado está corrompido ou vazio."

    if progress_callback:
        progress_callback("Preparando substituição e reinício...", 98)

    current_pid = os.getpid()

    if sys.platform.startswith("win"):
        # Script batch temporário para aguardar o fechamento do processo atual,
        # substituir o arquivo no mesmo local da memória/disco e reexecutar a nova versão
        updater_bat = os.path.join(tempfile.gettempdir(), f"update_gerador_{current_pid}.bat")
        bat_content = f"""@echo off
chcp 65001 >nul
setlocal
set PID={current_pid}
set NEW_EXE={temp_new_exe}
set TARGET_EXE={target_exe}

:: Aguarda o processo anterior encerrar completamente
timeout /t 1 /nobreak >nul 2>&1

:wait_loop
tasklist /fi "PID eq %PID%" 2>nul | find "%PID%" >nul
if %ERRORLEVEL% EQU 0 (
    timeout /t 1 /nobreak >nul 2>&1
    goto wait_loop
)

timeout /t 1 /nobreak >nul 2>&1

:: Substitui o executavel no mesmo local da memoria/disco
move /y "%NEW_EXE%" "%TARGET_EXE%" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    copy /y "%NEW_EXE%" "%TARGET_EXE%" >nul 2>&1
    del /f /q "%NEW_EXE%" >nul 2>&1
)

:: Inicia a nova versao atualizada
start "" "%TARGET_EXE%"

:: Auto-exclusao do script temporario
del "%~f0" >nul 2>&1 & exit
"""
        with open(updater_bat, "w", encoding="utf-8") as f:
            f.write(bat_content)

        # Dispara o script batch em segundo plano
        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen(["cmd.exe", "/c", updater_bat], creationflags=CREATE_NO_WINDOW)
        # O programa atual encerra para liberar o arquivo para substituição
        sys.exit(0)
    else:
        # Linux / Unix
        try:
            os.replace(temp_new_exe, target_exe)
            os.chmod(target_exe, 0o755)
            os.execv(target_exe, [target_exe] + sys.argv[1:])
        except Exception as e:
            return False, f"Falha ao substituir executável: {e}"

    return True, "Atualização aplicada com sucesso."

def reiniciar_programa():
    """Reinicia o aplicativo no mesmo lugar na memória (para modo script Python)."""
    project_dir = get_project_dir()
    app_script = os.path.join(project_dir, "app.py")
    if sys.platform.startswith("win"):
        # No Windows, abre uma nova instância limpa e encerra a anterior
        subprocess.Popen([sys.executable, app_script] + sys.argv[1:], cwd=project_dir)
        sys.exit(0)
    else:
        os.execv(sys.executable, [sys.executable, app_script] + sys.argv[1:])

def executar_atualizacao(progress_callback: Optional[Callable[[str, float], None]] = None) -> Tuple[bool, str]:
    """
    Função principal de atualização chamada pela GUI ou CLI.
    Identifica automaticamente se é executável ou script e atualiza pelo GitHub.
    """
    if is_frozen():
        # Estamos rodando como EXECUTÁVEL (.exe)
        if progress_callback:
            progress_callback("Consultando versão mais recente no GitHub...", 5)
        tem_exe, url_exe, tag_name = verificar_release_executavel()
        if tem_exe and url_exe:
            return aplicar_atualizacao_executavel(url_exe, progress_callback)
        else:
            # Não encontrou executável nos Releases do GitHub
            return False, (
                "Nenhum executável novo (.exe) foi encontrado nas Releases do repositório GitHub.\n\n"
                f"Repositório: https://github.com/{GITHUB_REPO}\n"
                "Para disponibilizar novas versões do executável, publique uma Release no GitHub."
            )
    else:
        # Estamos rodando como CÓDIGO FONTE / PROGRAMA PYTHON / .BAT
        sucesso, msg = atualizar_codigo_fonte(progress_callback)
        if sucesso:
            if progress_callback:
                progress_callback("Reiniciando aplicativo...", 100)
            reiniciar_programa()
        return sucesso, msg

def executar_atualizacao_cli():
    """Ponto de entrada para atualização via linha de comando ou script .bat."""
    print("========================================================")
    print(" Verificando atualizacoes no GitHub...")
    print(f" Repositorio: {GITHUB_REPO} ({GITHUB_BRANCH})")
    print("========================================================")
    def cli_progress(msg, pct):
        print(f"[*] {msg}")
    sucesso, msg = executar_atualizacao(cli_progress)
    print(f"\nResultado: {msg}")
    return 0 if sucesso else 1

if __name__ == "__main__":
    sys.exit(executar_atualizacao_cli())
