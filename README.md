# Gerador Automático de Listas de Viagens (PDF para Word .docx)

Aplicativo para Windows desenvolvido para ler arquivos PDF de **Mapa de Viagem** (sistema CIS NORTE / PAGE Saúde) e preencher automaticamente o modelo oficial da **Prefeitura Municipal de Ubaí** em formato Word (.docx).

---

## 🚀 Funcionalidades

1. **Leitura e Extração Automática do PDF**:
   - **Destino** (ex: Montes Claros);
   - **Data da Viagem** (ex: `04/09/2026`);
   - **Dia da Semana em Português** (calculado automaticamente, ex: `SEXTA-FEIRA`);
   - **Horário de Saída** (ex: `05:00 HRS DO POSTO DE SAUDE`);
   - **Lista Completa de Passageiros** (com tratamento de passageiros e acompanhantes);
   - **Identificação de Retorno**: Caso haja passageiros cadastrados somente na volta, a palavra `VOLTA` é inserida na coluna CONTATO.

2. **Preenchimento do Modelo Word (.docx)**:
   - Mantém integralmente o **cabeçalho oficial**, o **brasão/logo da prefeitura** e o **rodapé** com endereço;
   - Título formatado: `VIAGEM  DE MONTES CLAROS DD/MM/YYYY  [DIA-DA-SEMANA]`;
   - Subtítulo formatado: `SAÍDA - HH:MM HRS DO POSTO DE SAUDE`;
   - Tabela única com colunas oficiais:
     - **N**: Número do assento do passageiro;
     - **HRS**: Horário do atendimento / procedimento;
     - **PACIENTE**: Nome do paciente ou `ACOMP. [NOME]` quando for acompanhante (ou apenas `ACOMP.` quando sem nome);
     - **CONTATO**: Em branco (ou `VOLTA` para retorno);
     - **CLINICA**: Nome do estabelecimento/hospital/clínica;
     - **PROCEDIMENTO**: Em branco para preenchimento manual;
     - **C**: Em branco para preenchimento manual;
     - **LOCAL**: Em branco para preenchimento manual.
   - Adiciona linhas extras em branco no final para anotações manuais.

3. **Nomeação Automática do Arquivo Gerado**:
   - O arquivo gerado recebe o nome no padrão:  
     `VIAGEM MONTES CLAROS DD-MM-YYYY.docx` (ex: `VIAGEM MONTES CLAROS 04-09-2026.docx`).

---

## 🖥️ Como Usar no Windows

### Opção 1: Executar Diretamente via Python
1. Certifique-se de ter o Python instalado no Windows ([python.org](https://www.python.org/downloads/)). Marque a opção *"Add Python to PATH"* ao instalar.
2. Dê dois cliques no arquivo **`iniciar_programa.bat`**.
3. O programa abrirá uma janela moderna:
   - Clique em **"Selecionar PDF..."** e escolha o arquivo `mapa-viagem.pdf`;
   - O aplicativo mostrará o resumo dos dados identificados (data, destino, total de passageiros);
   - Clique no botão azul **"Gerar Documento Word (.docx)"**;
   - Pronto! O arquivo Word será gerado e você pode abri-lo diretamente com o botão **"Abrir Documento Word"**.

---

### Opção 2: Gerar um Executável Único (.exe)
Se preferir usar o programa como um `.exe` que não precisa abrir prompt ou pode ser distribuído:
1. Dê dois cliques no arquivo **`gerar_executavel.bat`**.
2. O script instalará o PyInstaller e compilará o programa.
3. Ao finalizar, o executável estará pronto na pasta:
   `dist\GeradorViagensWord.exe`
4. Você pode mover o executável `GeradorViagensWord.exe` para a sua Área de Trabalho e usá-lo quando quiser!

---

### Opção 3: Atualizar o Aplicativo pelo Repositório do GitHub
O aplicativo possui suporte a auto-atualização tanto no executável `.exe` quanto no script Python:
- **Pela Interface Gráfica**: Clique no botão **"🔄 Atualizar pelo GitHub"** localizado no canto superior direito do cabeçalho. O aplicativo verificará a versão mais recente no GitHub, baixará a atualização e reiniciará o aplicativo automaticamente no mesmo local!
- **Pelo Prompt / Script**: Dê dois cliques no arquivo **`atualizar_programa.bat`** ou execute `python app.py --atualizar`.

---

### Opção 4: Uso por Linha de Comando (CLI / Terminal)
Você também pode executar diretamente via terminal:
```bash
python app.py "caminho\para\mapa-viagem.pdf"
```
Ou especificando a pasta de saída:
```bash
python app.py "caminho\para\mapa-viagem.pdf" "C:\MinhasViagens"
```

---

## 📁 Estrutura do Projeto

```
Viagens_moc/
├── app.py                  # Interface gráfica (GUI) e ponto de entrada CLI
├── modelo_base.docx        # Template Word com cabeçalho, logo, rodapé e tabela
├── requirements.txt        # Dependências do Python (pypdf, python-docx, pyinstaller)
├── iniciar_programa.bat    # Atalho para iniciar no Windows
├── atualizar_programa.bat  # Script para atualizar pelo GitHub no Windows
├── gerar_executavel.bat    # Script para compilar o .exe para Windows
├── README.md               # Instruções detalhadas de uso
├── .github/workflows/
│   └── release.yml         # Compilação e publicação automática do .exe no GitHub
└── core/
    ├── __init__.py
    ├── updater.py          # Gerenciador de atualização pelo GitHub e auto-reinício
    ├── viagem_parser.py    # Leitor e extrator de dados do PDF
    └── word_generator.py   # Gerador do arquivo docx formatado
```
