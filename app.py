import os
import sys
import subprocess
from typing import Optional

# Adiciona o diretório atual ao path para importar core
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from core.viagem_parser import extrair_dados_pdf
from core.word_generator import gerar_documento_word

def get_resource_path(relative_path: str) -> str:
    """
    Retorna o caminho absoluto para recursos, funcionando tanto em desenvolvimento
    quanto quando empacotado como executável (.exe) pelo PyInstaller.
    """
    if hasattr(sys, "_MEIPASS"):
        # Executável gerado pelo PyInstaller
        base_path = getattr(sys, "_MEIPASS")
    else:
        base_path = CURRENT_DIR
    return os.path.join(base_path, relative_path)

def processar_arquivo(pdf_path: str, output_dir: Optional[str] = None, template_path: Optional[str] = None) -> str:
    """
    Função principal de processamento de um PDF para gerar o Word.
    """
    if not os.path.isfile(pdf_path):
        raise FileNotFoundError(f"Arquivo PDF não encontrado: {pdf_path}")

    if not template_path:
        template_path = get_resource_path("modelo_base.docx")

    if not os.path.isfile(template_path):
        # Tenta procurar na pasta do script
        alt_path = os.path.join(CURRENT_DIR, "modelo_base.docx")
        if os.path.isfile(alt_path):
            template_path = alt_path
        else:
            raise FileNotFoundError(f"Arquivo modelo base não encontrado: {template_path}")

    # Extrai os dados do PDF
    dados = extrair_dados_pdf(pdf_path)

    # Determina o diretório de saída
    if not output_dir:
        output_dir = os.path.dirname(os.path.abspath(pdf_path))

    output_filename = dados["filename_sugerido"]
    output_path = os.path.join(output_dir, output_filename)

    # Gera o documento Word
    gerar_documento_word(dados, template_path, output_path)
    return output_path

# ==========================================
# INTERFACE GRÁFICA (DESKTOP GUI PARA WINDOWS)
# ==========================================
def iniciar_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox

    root = tk.Tk()
    root.title("Gerador de Listas de Viagens - Word")
    root.geometry("680x620")
    root.minsize(600, 550)

    # Cores e Estilo
    bg_color = "#f4f6f9"
    card_bg = "#ffffff"
    primary_color = "#1e3a8a"
    accent_color = "#0284c7"
    text_color = "#1f2937"
    muted_color = "#6b7280"

    root.configure(bg=bg_color)

    style = ttk.Style()
    style.theme_use("clam")

    # Configuração de estilos TTK
    style.configure("TLabel", background=bg_color, foreground=text_color, font=("Segoe UI", 10))
    style.configure("Card.TFrame", background=card_bg, relief="flat")
    style.configure("Title.TLabel", background=bg_color, foreground=primary_color, font=("Segoe UI", 16, "bold"))
    style.configure("Subtitle.TLabel", background=bg_color, foreground=muted_color, font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", background=card_bg, foreground=primary_color, font=("Segoe UI", 11, "bold"))
    style.configure("CardBody.TLabel", background=card_bg, foreground=text_color, font=("Segoe UI", 10))
    style.configure("InfoVal.TLabel", background=card_bg, foreground="#0369a1", font=("Segoe UI", 10, "bold"))

    style.configure("Action.TButton", font=("Segoe UI", 11, "bold"), background=primary_color, foreground="white", borderwidth=0, padding=10)
    style.map("Action.TButton", background=[("active", "#1e40af"), ("disabled", "#9ca3af")])

    style.configure("Secondary.TButton", font=("Segoe UI", 9), background="#e2e8f0", foreground=text_color, padding=5)
    style.map("Secondary.TButton", background=[("active", "#cbd5e1")])

    style.configure("Update.TButton", font=("Segoe UI", 9, "bold"), background="#0284c7", foreground="white", borderwidth=0, padding=6)
    style.map("Update.TButton", background=[("active", "#0369a1"), ("disabled", "#9ca3af")])

    # Variáveis da interface
    pdf_path_var = tk.StringVar(value="")
    output_dir_var = tk.StringVar(value="")
    status_var = tk.StringVar(value="Selecione um arquivo PDF de mapa de viagem para começar.")
    extracted_data = {}
    last_generated_file = {"path": ""}

    # Layout Principal
    main_frame = tk.Frame(root, bg=bg_color, padx=20, pady=20)
    main_frame.pack(fill="both", expand=True)

    # Cabeçalho do App
    header_frame = tk.Frame(main_frame, bg=bg_color)
    header_frame.pack(fill="x", pady=(0, 15))

    header_text_frame = tk.Frame(header_frame, bg=bg_color)
    header_text_frame.pack(side="left", fill="x", expand=True)

    lbl_title = ttk.Label(header_text_frame, text="Gerador de Listas de Viagens", style="Title.TLabel")
    lbl_title.pack(anchor="w")

    lbl_sub = ttk.Label(
        header_text_frame,
        text="Converte automaticamente o PDF Mapa de Viagem para o modelo oficial em Word (.docx)",
        style="Subtitle.TLabel"
    )
    lbl_sub.pack(anchor="w")

    def abrir_janela_atualizacao():
        import threading
        from core.updater import executar_atualizacao, is_frozen, GITHUB_REPO

        modal = tk.Toplevel(root)
        modal.title("Atualização do Aplicativo")
        modal.geometry("480x230")
        modal.resizable(False, False)
        modal.configure(bg=bg_color)
        modal.transient(root)
        modal.grab_set()

        try:
            root_x = root.winfo_rootx()
            root_y = root.winfo_rooty()
            root_w = root.winfo_width()
            root_h = root.winfo_height()
            modal.geometry(f"+{root_x + max(0, (root_w - 480) // 2)}+{root_y + max(0, (root_h - 230) // 2)}")
        except Exception:
            pass

        frame_m = tk.Frame(modal, bg=bg_color, padx=20, pady=20)
        frame_m.pack(fill="both", expand=True)

        lbl_m_title = ttk.Label(frame_m, text="Atualizar pelo GitHub", style="Title.TLabel", font=("Segoe UI", 12, "bold"))
        lbl_m_title.pack(anchor="w", pady=(0, 4))

        tipo_str = "Executável (.exe)" if is_frozen() else "Código-Fonte / Script"
        lbl_m_info = ttk.Label(
            frame_m,
            text=f"Modo: {tipo_str} | Repositório: {GITHUB_REPO}",
            style="Subtitle.TLabel",
            font=("Segoe UI", 9)
        )
        lbl_m_info.pack(anchor="w", pady=(0, 12))

        lbl_m_status = ttk.Label(
            frame_m,
            text="Clique em 'Atualizar Agora' para buscar e instalar a versão mais recente.",
            style="CardBody.TLabel",
            wraplength=430
        )
        lbl_m_status.pack(anchor="w", pady=(0, 10))

        prog_bar = ttk.Progressbar(frame_m, mode="indeterminate", length=430)
        prog_bar.pack(fill="x", pady=(0, 15))

        btn_modal_box = tk.Frame(frame_m, bg=bg_color)
        btn_modal_box.pack(fill="x")

        def atualizar_ui(msg, pct):
            def _apply():
                lbl_m_status.config(text=msg)
                if pct >= 0:
                    prog_bar.config(mode="determinate", value=pct)
                else:
                    prog_bar.config(mode="indeterminate")
                    prog_bar.start(10)
            modal.after(0, _apply)

        def iniciar_atualizacao():
            btn_iniciar.config(state="disabled")
            btn_fechar.config(state="disabled")
            prog_bar.config(mode="indeterminate")
            prog_bar.start(10)

            def worker():
                sucesso, msg = executar_atualizacao(atualizar_ui)
                def _done():
                    prog_bar.stop()
                    lbl_m_status.config(text=msg)
                    btn_fechar.config(state="normal")
                    if not sucesso:
                        btn_iniciar.config(state="normal", text="Tentar Novamente")
                modal.after(0, _done)

            threading.Thread(target=worker, daemon=True).start()

        btn_iniciar = ttk.Button(btn_modal_box, text="Atualizar Agora", command=iniciar_atualizacao, style="Action.TButton")
        btn_iniciar.pack(side="left", padx=(0, 10))

        btn_fechar = ttk.Button(btn_modal_box, text="Fechar", command=modal.destroy, style="Secondary.TButton")
        btn_fechar.pack(side="right")

    btn_update_app = ttk.Button(
        header_frame,
        text="🔄 Atualizar pelo GitHub",
        command=abrir_janela_atualizacao,
        style="Update.TButton"
    )
    btn_update_app.pack(side="right", anchor="ne", padx=(10, 0), pady=4)

    # Card 1: Seleção de Arquivo PDF
    card_pdf = tk.LabelFrame(main_frame, text=" 1. Arquivo PDF de Origem ", bg=card_bg, fg=primary_color, font=("Segoe UI", 10, "bold"), padx=15, pady=12)
    card_pdf.pack(fill="x", pady=(0, 10))

    pdf_entry_frame = tk.Frame(card_pdf, bg=card_bg)
    pdf_entry_frame.pack(fill="x")

    pdf_entry = tk.Entry(pdf_entry_frame, textvariable=pdf_path_var, font=("Segoe UI", 10), state="readonly", bg="#f8fafc")
    pdf_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)

    def selecionar_pdf():
        caminho = filedialog.askopenfilename(
            title="Selecionar Mapa de Viagem PDF",
            filetypes=[("Arquivos PDF", "*.pdf"), ("Todos os Arquivos", "*.*")]
        )
        if caminho:
            pdf_path_var.set(caminho)
            # Define o diretório de saída padrão como a pasta do próprio PDF
            if not output_dir_var.get():
                output_dir_var.set(os.path.dirname(caminho))
            carregar_preview(caminho)

    btn_browse_pdf = ttk.Button(pdf_entry_frame, text="Selecionar PDF...", command=selecionar_pdf, style="Secondary.TButton")
    btn_browse_pdf.pack(side="right")

    # Card 2: Pasta de Saída
    card_out = tk.LabelFrame(main_frame, text=" 2. Pasta de Destino do Arquivo Word ", bg=card_bg, fg=primary_color, font=("Segoe UI", 10, "bold"), padx=15, pady=12)
    card_out.pack(fill="x", pady=(0, 10))

    out_entry_frame = tk.Frame(card_out, bg=card_bg)
    out_entry_frame.pack(fill="x")

    out_entry = tk.Entry(out_entry_frame, textvariable=output_dir_var, font=("Segoe UI", 10), state="readonly", bg="#f8fafc")
    out_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=4)

    def selecionar_pasta():
        pasta = filedialog.askdirectory(title="Selecionar Pasta de Destino")
        if pasta:
            output_dir_var.set(pasta)

    btn_browse_out = ttk.Button(out_entry_frame, text="Alterar Pasta...", command=selecionar_pasta, style="Secondary.TButton")
    btn_browse_out.pack(side="right")

    # Card 3: Informações Detectadas da Viagem (Preview)
    card_preview = tk.LabelFrame(main_frame, text=" 3. Dados Detectados da Viagem ", bg=card_bg, fg=primary_color, font=("Segoe UI", 10, "bold"), padx=15, pady=12)
    card_preview.pack(fill="both", expand=True, pady=(0, 15))

    info_grid = tk.Frame(card_preview, bg=card_bg)
    info_grid.pack(fill="both", expand=True)

    lbl_dest_t = ttk.Label(info_grid, text="Destino:", style="CardBody.TLabel")
    lbl_dest_t.grid(row=0, column=0, sticky="w", pady=3)
    lbl_dest_v = ttk.Label(info_grid, text="-", style="InfoVal.TLabel")
    lbl_dest_v.grid(row=0, column=1, sticky="w", padx=10, pady=3)

    lbl_data_t = ttk.Label(info_grid, text="Data da Viagem:", style="CardBody.TLabel")
    lbl_data_t.grid(row=1, column=0, sticky="w", pady=3)
    lbl_data_v = ttk.Label(info_grid, text="-", style="InfoVal.TLabel")
    lbl_data_v.grid(row=1, column=1, sticky="w", padx=10, pady=3)

    lbl_saida_t = ttk.Label(info_grid, text="Horário de Saída:", style="CardBody.TLabel")
    lbl_saida_t.grid(row=2, column=0, sticky="w", pady=3)
    lbl_saida_v = ttk.Label(info_grid, text="-", style="InfoVal.TLabel")
    lbl_saida_v.grid(row=2, column=1, sticky="w", padx=10, pady=3)

    lbl_total_t = ttk.Label(info_grid, text="Total de Passageiros:", style="CardBody.TLabel")
    lbl_total_t.grid(row=3, column=0, sticky="w", pady=3)
    lbl_total_v = ttk.Label(info_grid, text="-", style="InfoVal.TLabel")
    lbl_total_v.grid(row=3, column=1, sticky="w", padx=10, pady=3)

    lbl_nome_arq_t = ttk.Label(info_grid, text="Nome do Arquivo Word:", style="CardBody.TLabel")
    lbl_nome_arq_t.grid(row=4, column=0, sticky="w", pady=3)
    lbl_nome_arq_v = ttk.Label(info_grid, text="-", style="InfoVal.TLabel")
    lbl_nome_arq_v.grid(row=4, column=1, sticky="w", padx=10, pady=3)

    def carregar_preview(caminho_pdf):
        try:
            dados = extrair_dados_pdf(caminho_pdf)
            extracted_data.clear()
            extracted_data.update(dados)

            lbl_dest_v.config(text=dados["destino"])
            lbl_data_v.config(text=f"{dados['data_viagem']} ({dados['dia_semana']})")
            lbl_saida_v.config(text=f"{dados['hora_saida']} HRS")
            lbl_total_v.config(text=f"{dados['total_passageiros']} passageiros")
            lbl_nome_arq_v.config(text=dados["filename_sugerido"])

            btn_gerar.config(state="normal")
            status_var.set("Arquivo analisado com sucesso! Clique em 'Gerar Documento Word'.")
        except Exception as e:
            messagebox.showerror("Erro ao ler PDF", f"Não foi possível ler as informações do PDF:\n{e}")
            status_var.set("Erro ao analisar o arquivo selecionado.")

    # Ações e Botão de Gerar
    btn_frame = tk.Frame(main_frame, bg=bg_color)
    btn_frame.pack(fill="x", pady=(0, 10))

    def acao_gerar():
        caminho_pdf = pdf_path_var.get()
        pasta_saida = output_dir_var.get()
        if not caminho_pdf:
            messagebox.showwarning("Atenção", "Por favor, selecione primeiro um arquivo PDF.")
            return
        if not pasta_saida:
            messagebox.showwarning("Atenção", "Por favor, selecione a pasta de destino.")
            return

        try:
            btn_gerar.config(state="disabled")
            status_var.set("Gerando documento Word...")
            root.update_idletasks()

            output_file = processar_arquivo(caminho_pdf, output_dir=pasta_saida)
            last_generated_file["path"] = output_file

            status_var.set(f"Sucesso! Arquivo gerado: {os.path.basename(output_file)}")
            btn_abrir_arq.pack(side="left", padx=(0, 10))
            btn_abrir_pasta.pack(side="left")

            messagebox.showinfo(
                "Documento Gerado!",
                f"O arquivo Word foi criado com sucesso com as informações do mapa de viagem:\n\n{output_file}"
            )
        except Exception as e:
            messagebox.showerror("Erro ao Gerar Documento", f"Ocorreu um erro ao gerar o arquivo Word:\n{e}")
            status_var.set("Erro ao gerar o documento.")
        finally:
            btn_gerar.config(state="normal")

    btn_gerar = ttk.Button(btn_frame, text="Gerar Documento Word (.docx)", command=acao_gerar, style="Action.TButton", state="disabled")
    btn_gerar.pack(fill="x", ipady=4)

    # Botões auxiliares pós-geração
    pos_frame = tk.Frame(main_frame, bg=bg_color)
    pos_frame.pack(fill="x", pady=(0, 10))

    def abrir_arquivo_gerado():
        caminho = last_generated_file.get("path")
        if caminho and os.path.exists(caminho):
            if sys.platform.startswith("win"):
                os.startfile(caminho)
            elif sys.platform.startswith("darwin"):
                subprocess.call(["open", caminho])
            else:
                subprocess.call(["xdg-open", caminho])

    def abrir_pasta_gerada():
        caminho = last_generated_file.get("path")
        if caminho and os.path.exists(caminho):
            pasta = os.path.dirname(caminho)
            if sys.platform.startswith("win"):
                os.startfile(pasta)
            elif sys.platform.startswith("darwin"):
                subprocess.call(["open", pasta])
            else:
                subprocess.call(["xdg-open", pasta])

    btn_abrir_arq = ttk.Button(pos_frame, text="Abrir Documento Word", command=abrir_arquivo_gerado, style="Secondary.TButton")
    btn_abrir_pasta = ttk.Button(pos_frame, text="Abrir Pasta de Destino", command=abrir_pasta_gerada, style="Secondary.TButton")

    # Barra de Status inferior
    lbl_status = tk.Label(main_frame, textvariable=status_var, bg=bg_color, fg=muted_color, font=("Segoe UI", 9, "italic"), anchor="w")
    lbl_status.pack(fill="x", side="bottom")

    root.mainloop()

# ==========================================
# EXECUÇÃO VIA TERMINAL OU GUI
# ==========================================
def main():
    if len(sys.argv) > 1:
        if sys.argv[1] in ("--atualizar", "--update", "-u"):
            from core.updater import executar_atualizacao_cli
            sys.exit(executar_atualizacao_cli())

        # Modo linha de comando (CLI)
        pdf_arg = sys.argv[1]
        out_arg = sys.argv[2] if len(sys.argv) > 2 else None
        print(f"Processando arquivo: {pdf_arg}")
        try:
            out_file = processar_arquivo(pdf_arg, output_dir=out_arg)
            print(f"Sucesso! Arquivo gerado em: {out_file}")
        except Exception as e:
            print(f"Erro: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Modo gráfico (GUI)
        iniciar_gui()

if __name__ == "__main__":
    main()
