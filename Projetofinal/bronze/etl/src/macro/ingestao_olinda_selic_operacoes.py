import sys
from pathlib import Path

# Adiciona a pasta src/utils ao PATH do Python para importar utils_ingestao
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from utils_ingestao import extrair_tabela, gerar_periodos_mensais

# ==============================================================================
# Ingestão — Contexto: Selic Operações (Volume Mensal)
# ==============================================================================

SERVICO = 'selic_operacoes'
TABELA = 'OperacoesEmUmMes'

def extrair():
    print("=" * 60)
    print("INGESTÃO MACRO — Contexto: Selic Operações")
    print("=" * 60)

    base_raw_path = Path(__file__).parent.parent.parent.parent / "data" / "macro_bruto" / "selic_operacoes"

    # Gerar períodos YYYY-MM (com hífen, exigido pela API Olinda)
    periodos_yyyymm = [f"{p[:4]}-{p[4:]}" for p in gerar_periodos_mensais(ano_inicio=2020, mes_inicio=1)]

    print(f"\n  → Extraindo: {TABELA}")
    pasta = base_raw_path / TABELA
    
    extrair_tabela(SERVICO, TABELA, pasta, param_name="Mes", ciclos=periodos_yyyymm)

if __name__ == "__main__":
    extrair()
