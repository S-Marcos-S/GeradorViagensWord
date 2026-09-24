import os
import sys
import re
import json
import shutil
import tempfile
import zipfile
import subprocess
import ssl
import datetime
import urllib.request
import urllib.error
from typing import Tuple, Optional, Callable

from core.version import VERSION as LOCAL_VERSION, COMMIT_SHA as LOCAL_COMMIT_SHA

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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent = os.path.dirname(current_dir)
        if os.path.isfile(os.path.join(parent, "app.py")):
            return parent
        return current_dir

def parse_version(v_str: str) -> tuple:
    """Converte string de versão '1.1.0' ou 'v1.2.3' para tupla comparável (1, 1, 0)."""
    if not v_str:
        return (0, 0, 0)
    v_clean = v_str.strip().lstrip("vV")
    parts = []
    for part in re.split(r'[.-]', v_clean):
        if part.isdigit():
            parts.append(int(part))
        else:
            break
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])

def obter_versao_local() -> str:
    """Retorna a versão local cadastrada."""
    return LOCAL_VERSION

def obter_commit_local() -> str:
    """Retorna o commit SHA local via Git ou do fallback em version.py."""
    project_dir = get_project_dir()
    git_dir = os.path.join(project_dir, ".git")
    if os.path.isdir(git_dir):
        try:
            res = subprocess.run(["git", "rev-parse", "HEAD"], cwd=project_dir, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        except Exception:
            pass
    return LOCAL_COMMIT_SHA

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

def verificar_se_tem_atualizacao(progress_callback: Optional[Callable[[str, float], None]] = None) -> Tuple[bool, str, Optional[str]]:
    """
    Verifica se o repositório no GitHub possui uma versão mais recente que a local.
    Retorna:
      (tem_atualizacao: bool, mensagem_explicativa: str, url_download_ou_info: Optional[str])
    """
    if progress_callback:
        progress_callback("Consultando GitHub para verificar versão...", 10)

    if is_frozen():
        # Modo EXECUTÁVEL (.exe)
        try:
            with _abrir_url(GITHUB_API_LATEST_RELEASE, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").strip()
                published_at = data.get("published_at", "")
                assets = data.get("assets", [])

                exe_asset = None
                for asset in assets:
                    if asset.get("name", "").lower().endswith(".exe"):
                        exe_asset = asset
                        break

                if not exe_asset:
                    return False, f"Nenhum executável (.exe) publicado nas Releases do GitHub.", None

                download_url = exe_asset.get("browser_download_url")
                asset_date_str = exe_asset.get("updated_at") or published_at

                # 1. Comparação de versão semântica da tag
                v_remote = parse_version(tag_name)
                v_local = parse_version(LOCAL_VERSION)
                if v_remote > v_local:
                    return True, f"Nova versão encontrada: {tag_name} (versão atual: v{LOCAL_VERSION})", download_url

                # 2. Se as versões forem iguais ou tag genérica, compara data de modificação
                if asset_date_str:
                    try:
                        clean_dt = asset_date_str.replace("Z", "+00:00")
                        remote_ts = datetime.datetime.fromisoformat(clean_dt).timestamp()
                        local_mtime = os.path.getmtime(sys.executable)
                        if remote_ts > (local_mtime + 60):
                            return True, f"Nova compilação do executável disponível no GitHub!", download_url
                    except Exception:
                        pass

                return False, f"O executável já está na versão mais recente (v{LOCAL_VERSION})!", None

        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False, f"Nenhuma Release publicada no GitHub ainda (versão local: v{LOCAL_VERSION}).", None
            return False, f"Erro ao consultar GitHub Releases: HTTP {e.code}", None
        except Exception as e:
            return False, f"Não foi possível verificar no GitHub: {e}", None

    else:
        # Modo PROGRAMA PYTHON / CÓDIGO-FONTE
        commit_url = f"https://api.github.com/repos/{GITHUB_REPO}/commits/{GITHUB_BRANCH}"
        try:
            with _abrir_url(commit_url, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                remote_sha = data.get("sha", "").strip()
                remote_msg = data.get("commit", {}).get("message", "").splitlines()[0]
                local_sha = obter_commit_local().strip()

                if local_sha and remote_sha:
                    if local_sha.lower() == remote_sha.lower() or \
                       local_sha.lower().startswith(remote_sha[:7].lower()) or \
                       remote_sha.lower().startswith(local_sha[:7].lower()):
                        return False, f"O aplicativo já está na versão mais recente (v{LOCAL_VERSION} - commit {local_sha[:7]})!", None
                    else:
                        return True, f"Nova atualização disponível no GitHub ({remote_sha[:7]}): {remote_msg}", None
        except Exception:
            # Fallback se a API de commits falhar: compara versão no version.py remoto
            try:
                raw_url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{GITHUB_BRANCH}/core/version.py"
                with _abrir_url(raw_url, timeout=15) as resp:
                    raw_content = resp.read().decode("utf-8")
                    v_match = re.search(r'VERSION\s*=\s*["\']([^"\']+)["\']', raw_content)
                    if v_match:
                        remote_ver = v_match.group(1).strip()
                        if parse_version(remote_ver) > parse_version(LOCAL_VERSION):
                            return True, f"Nova versão encontrada: v{remote_ver} (versão atual: v{LOCAL_VERSION})", None
                        else:
                            return False, f"O aplicativo já está na versão mais recente (v{LOCAL_VERSION})!", None
            except Exception:
                pass

        # Fallback local via Git fetch se repositório git estiver configurado
        project_dir = get_project_dir()
        if os.path.isdir(os.path.join(project_dir, ".git")):
            try:
                subprocess.run(["git", "fetch", "origin", GITHUB_BRANCH], cwd=project_dir, capture_output=True, text=True)
                res_local = subprocess.run(["git", "rev-parse", "HEAD"], cwd=project_dir, capture_output=True, text=True)
                res_remote = subprocess.run(["git", "rev-parse", f"origin/{GITHUB_BRANCH}"], cwd=project_dir, capture_output=True, text=True)
                if res_local.returncode == 0 and res_remote.returncode == 0:
                    l_sha = res_local.stdout.strip()
                    r_sha = res_remote.stdout.strip()
                    if l_sha == r_sha:
                        return False, f"O aplicativo já está na versão mais recente (commit {l_sha[:7]})!", None
                    else:
                        return True, f"Nova versão disponível no repositório Git (commit {r_sha[:7]})!", None
            except Exception:
                pass

        return True, "Atualização disponível no GitHub.", None

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

        CREATE_NO_WINDOW = 0x08000000
        subprocess.Popen(["cmd.exe", "/c", updater_bat], creationflags=CREATE_NO_WINDOW)
        sys.exit(0)
    else:
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
        subprocess.Popen([sys.executable, app_script] + sys.argv[1:], cwd=project_dir)
        sys.exit(0)
    else:
        os.execv(sys.executable, [sys.executable, app_script] + sys.argv[1:])

def executar_atualizacao(progress_callback: Optional[Callable[[str, float], None]] = None) -> Tuple[bool, str]:
    """
    Função principal de atualização chamada pela GUI ou CLI.
    Primeiro verifica se realmente a versão do GitHub é uma atualização da versão atual.
    Se já estiver na versão mais recente, informa o usuário e não faz download.
    Se houver nova versão, realiza a atualização e reinicia.
    """
    tem_atualizacao, msg_verif, url_down = verificar_se_tem_atualizacao(progress_callback)

    if not tem_atualizacao:
        # Não é uma versão mais nova, o usuário já está com a versão atualizada
        return True, msg_verif

    # Há realmente uma nova versão!
    if is_frozen():
        if url_down:
            return aplicar_atualizacao_executavel(url_down, progress_callback)
        else:
            return False, msg_verif
    else:
        if progress_callback:
            progress_callback("Baixando atualização do GitHub...", 20)
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
    print(f" Versao Local: {LOCAL_VERSION}")
    print("========================================================")
    def cli_progress(msg, pct):
        print(f"[*] {msg}")
    sucesso, msg = executar_atualizacao(cli_progress)
    print(f"\nResultado: {msg}")
    return 0 if sucesso else 1

if __name__ == "__main__":
    sys.exit(executar_atualizacao_cli())
