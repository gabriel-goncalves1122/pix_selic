import sys
from pathlib import Path

# Adiciona a pasta src/utils ao PATH do Python para importar utils_ingestao
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from utils_ingestao import extrair_tabela, gerar_periodos_mensais

# ==============================================================================
# Ingestão — Contexto: Fraudes
# Tabelas relativas a infrações e fraudes do Pix.
# ==============================================================================

SERVICO = 'Pix_DadosAbertos'

TABELAS = {
    # Tabelas que exigem parâmetro Database='YYYYMM'
    'com_database': [
        'EstatisticasFraudesPix',
    ]
}

def extrair():
    print("=" * 60)
    print("INGESTÃO PIX — Contexto: Fraudes")
    print("=" * 60)

    # Nova hierarquia: src/pix -> src -> etl -> bronze
    base_raw_path = Path(__file__).parent.parent.parent.parent / "data" / "pix_bruto"
    periodos_mensais = gerar_periodos_mensais()

    print(f"Períodos a extrair: {periodos_mensais[0]} até {periodos_mensais[-1]}")
    print()

    for tabela in TABELAS['com_database']:
        print(f"\n  → {tabela} (Database='YYYYMM')")
        pasta = base_raw_path / SERVICO / tabela
        extrair_tabela(SERVICO, tabela, pasta, "Database", periodos_mensais)

    print("\nConcluído!")

if __name__ == '__main__':
    extrair()
