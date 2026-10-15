import sys
from pathlib import Path

# Adiciona a pasta src/utils ao PATH do Python para importar utils_ingestao
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from utils_ingestao import fazer_request, salvar, registrar

# ==============================================================================
# Ingestão — Contexto: SGS (Realizado)
# ==============================================================================

INDICADORES = {
    '432': 'Selic_Meta_Diaria',
    '433': 'IPCA_Mensal',
    '11': 'Selic_Realizada_Diaria'
}

def extrair():
    print("=" * 60)
    print("INGESTÃO MACRO — Contexto: SGS (Realizado)")
    print("=" * 60)

    base_raw_path = Path(__file__).parent.parent.parent.parent / "data" / "macro_bruto" / "sgs"

    for codigo, nome in INDICADORES.items():
        print(f"\n  → {nome} (Série {codigo})")
        
        # Como o SGS é uma série contínua, sempre vamos baixar e sobrescrever para ter a data mais recente.
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados?formato=csv&dataInicial=01/01/2020"
        
        res = fazer_request(url)

        if res is None:
            print(f"FALHA após {5} tentativas. URL: {url}")
            continue

        if res.status_code == 200:
            texto_csv = res.text
            
            qtd_linhas = texto_csv.strip().count('\n')

            if not texto_csv.strip() or qtd_linhas == 0:
                print(f"Vazio (0 registros).")
                continue

            destino_arquivo = salvar(texto_csv, base_raw_path, nome)
            registrar(base_raw_path, destino_arquivo, url, qtd_linhas)
            print(f"✅ {qtd_linhas} registros → {destino_arquivo.name}")
        else:
            print(f"❌ HTTP {res.status_code}. URL: {url}")

if __name__ == "__main__":
    extrair()
