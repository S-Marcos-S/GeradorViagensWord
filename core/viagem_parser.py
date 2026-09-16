import re
import datetime
from typing import Dict, List, Any
import pypdf

DIAS_SEMANA = {
    0: "SEGUNDA-FEIRA",
    1: "TERÇA-FEIRA",
    2: "QUARTA-FEIRA",
    3: "QUINTA-FEIRA",
    4: "SEXTA-FEIRA",
    5: "SÁBADO",
    6: "DOMINGO"
}

def extrair_dados_pdf(pdf_path: str) -> Dict[str, Any]:
    """
    Lê o PDF 'mapa-viagem' e extrai todas as informações da viagem e lista de passageiros.
    """
    reader = pypdf.PdfReader(pdf_path)
    full_text = "\n".join([page.extract_text() or "" for page in reader.pages])

    # 1. Informações de Motorista e Rota
    motorista = ""
    motorista_match = re.search(r"Motorista\s+(.*?)\s+(\(\d{2}\)\s*[\d-]+|-)", full_text)
    if motorista_match:
        motorista = motorista_match.group(1).strip()

    veiculo = ""
    data_viagem = ""
    hora_saida = "05:00"
    destino = "MONTES CLAROS"

    # Rota e Data/Hora
    route_match = re.search(r"Rota\s+Data e Hora ida\s+Data e Hora Volta\s+Veículo\s*\n(.*?)\n", full_text)
    if route_match:
        route_line = route_match.group(1).strip()
        # Data e Hora de Ida
        dt_match = re.search(r"(\d{2}/\d{2}/\d{4})\s*-\s*(\d{2}:\d{2})", route_line)
        if dt_match:
            data_viagem = dt_match.group(1)
            hora_saida = dt_match.group(2)
        
        # Destino
        if "/" in route_line:
            parts = route_line.split("/")[1].split("-")[0].strip()
            if parts:
                destino = parts.upper()
        
        # Veículo
        veic_match = re.search(r"([A-Z0-9]{7})$", route_line)
        if veic_match:
            veiculo = veic_match.group(1)

    # Se a data não foi encontrada na linha de rota, busca no texto
    if not data_viagem:
        dt_any = re.search(r"(\d{2}/\d{2}/\d{4})", full_text)
        if dt_any:
            data_viagem = dt_any.group(1)
        else:
            data_viagem = datetime.date.today().strftime("%d/%m/%Y")

    # Calcula o dia da semana correspondente
    try:
        dt_obj = datetime.datetime.strptime(data_viagem, "%d/%m/%Y")
        dia_semana = DIAS_SEMANA.get(dt_obj.weekday(), "SEGUNDA-FEIRA")
        data_arquivo = dt_obj.strftime("%d-%m-%Y")
    except Exception:
        dia_semana = "SEXTA-FEIRA"
        data_arquivo = data_viagem.replace("/", "-")

    # Nome de arquivo sugerido seguindo o modelo: VIAGEM MONTES CLAROS DD-MM-YYYY.docx
    filename_sugerido = f"VIAGEM {destino} {data_arquivo}.docx"

    # 2. Limpeza do texto para parsing de passageiros
    clean_text = re.sub(r"Data de emissão:.*?\nhttps://pagesaude\.com\.br", "", full_text, flags=re.DOTALL)
    clean_text = re.sub(r"Assento Tipo Nome Documento Estabelecimento Hora\s*Atendimento", "", clean_text)

    parts = re.split(r"INFORMAÇÕES DE PASSAGEIROS (IDA|VOLTA)\s*-\s*TOTAL:\s*(\d+)", clean_text)

    def parse_passenger_block(block_text: str) -> List[Dict[str, Any]]:
        pattern = r"(?m)^(\d+)\s+(Paciente|Acompanhante)\s+(.*?)\s*Observação:\s*(.*?)(?=(?:^\d+\s+(?:Paciente|Acompanhante))|\Z)"
        matches = re.findall(pattern, block_text, re.DOTALL)
        passengers = []
        for seat, tipo, body, obs in matches:
            body = " ".join(body.split())
            doc_match = re.search(r"(XXX\.\d{3}\.\d{3}-XX|-)", body)
            if doc_match:
                nome = body[:doc_match.start()].strip()
                after_doc = body[doc_match.end():].strip()
                time_match = re.search(r"(\d{1,2}:\d{2}|-)$", after_doc)
                if time_match:
                    hora = time_match.group(1)
                    estabel = after_doc[:time_match.start()].strip()
                else:
                    hora = ""
                    estabel = after_doc
            else:
                nome = body
                estabel = ""
                hora = ""
            
            if hora == "-":
                hora = ""
            if estabel == "-":
                estabel = ""

            passengers.append({
                "seat": seat.strip(),
                "tipo": tipo.strip(),
                "nome": nome.strip(),
                "estabelecimento": estabel.strip(),
                "hora": hora.strip(),
                "is_volta_only": False
            })
        return passengers

    ida_passengers = parse_passenger_block(parts[3]) if len(parts) > 3 else []
    volta_passengers = parse_passenger_block(parts[6]) if len(parts) > 6 else []

    # Identifica passageiros que estão exclusivamente na volta
    ida_nomes = {p["nome"].strip().upper() for p in ida_passengers if p["nome"].strip()}
    volta_only = []
    for vp in volta_passengers:
        nome_clean = vp["nome"].strip().upper()
        if nome_clean and nome_clean != "ACOMPANHANTE" and nome_clean not in ida_nomes:
            vp["is_volta_only"] = True
            volta_only.append(vp)

    all_passengers = ida_passengers + volta_only

    return {
        "destino": destino,
        "data_viagem": data_viagem,
        "dia_semana": dia_semana,
        "hora_saida": hora_saida,
        "motorista": motorista,
        "veiculo": veiculo,
        "total_passageiros": len(all_passengers),
        "passageiros": all_passengers,
        "filename_sugerido": filename_sugerido
    }
