import logging
import sys
from datetime import date
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from utils_ingestao import fazer_request, salvar, registrar

log = logging.getLogger(__name__)

INDICADORES = {
    '432': 'Selic_Meta_Diaria',
    '433': 'IPCA_Mensal',
    '11': 'Selic_Realizada_Diaria'
}


def extrair():
    log.info("INGESTAO MACRO - Contexto: SGS (Realizado)")

    base_raw_path = Path(__file__).parent.parent.parent / "dados" / "bronze" / "macro_bruto" / "sgs"

    for codigo, nome in INDICADORES.items():
        data_final = date.today().strftime("%d/%m/%Y")
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=csv&dataInicial=01/01/2020&dataFinal={data_final}"

        res = fazer_request(url)

        if res is None:
            log.error("FALHA apos 5 tentativas (%s). URL: %s", nome, url)
            continue

        if res.status_code == 200:
            texto_csv = res.text
            qtd_linhas = texto_csv.strip().count('\n')

            if not texto_csv.strip() or qtd_linhas == 0 or "<html" in texto_csv[:200].lower():
                log.warning("Resposta invalida ou vazia (%s). URL: %s", nome, url)
                continue

            destino_arquivo = salvar(texto_csv, base_raw_path, nome)
            registrar(base_raw_path, destino_arquivo, url, qtd_linhas)
            log.info("%s: %s registros -> %s", nome, qtd_linhas, destino_arquivo.name)
        else:
            log.error("HTTP %s (%s). URL: %s", res.status_code, nome, url)

if __name__ == "__main__":
    extrair()
