import sys
from pathlib import Path

# Adiciona a pasta src/utils ao PATH do Python para importar utils_ingestao
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from utils_ingestao import extrair_tabela, gerar_periodos_mensais

# ==============================================================================
# Ingestão — Contexto: Macroeconomia (Expectativas Focus - Olinda)
# ==============================================================================

SERVICO = 'Expectativas'

TABELAS = {
    'ExpectativaMercadoMensais': "Indicador eq 'IPCA' or Indicador eq 'Selic'",
    'ExpectativasMercadoAnuais': "Indicador eq 'IPCA' or Indicador eq 'Selic'",
}

def extrair():
    print("=" * 60)
    print("INGESTÃO MACRO — Contexto: Expectativas (Boletim Focus)")
    print("=" * 60)

    base_raw_path = Path(__file__).parent.parent.parent.parent / "data" / "macro_bruto" / "focus"

    for tabela, odata_filter in TABELAS.items():
        print(f"\n  → {tabela} (Filtro: {odata_filter})")
        pasta = base_raw_path / tabela
        # Como o Focus não exige parâmetro particionado, extraímos sem param_name
        extrair_tabela(SERVICO, tabela, pasta, param_name=None, ciclos=[None], odata_filter=odata_filter)

if __name__ == "__main__":
    extrair()
