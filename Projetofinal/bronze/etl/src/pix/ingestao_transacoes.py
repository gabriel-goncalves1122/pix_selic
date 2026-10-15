import sys
from pathlib import Path

# Adiciona a pasta src/utils ao PATH do Python para importar utils_ingestao
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from utils_ingestao import extrair_tabela, gerar_periodos_mensais

# ==============================================================================
# Ingestão — Contexto: Transações Pix
# Tabelas relativas a volumes financeiros, quantidades, perfil e região.
# ==============================================================================

SERVICO = 'Pix_DadosAbertos'

TABELAS = {
    # Tabelas que exigem parâmetro Database='YYYYMM'
    'com_database': [
        'EstatisticasTransacoesPix',
    ],
    # Tabelas que exigem DataBase='YYYYMM' (B maiúsculo)
    'com_DataBase': [
        'TransacoesPixPorMunicipio',
    ]
}

def extrair():
    print("=" * 60)
    print("INGESTÃO PIX — Contexto: Transações")
    print("=" * 60)

    # Nova hierarquia: src/pix -> src -> etl -> bronze
    base_raw_path = Path(__file__).parent.parent.parent.parent / "data" / "pix_bruto"
    periodos_mensais = gerar_periodos_mensais()

    print(f"Períodos a extrair: {periodos_mensais[0]} até {periodos_mensais[-1]}")
    print()

    # Tabelas com Database='YYYYMM'
    for tabela in TABELAS.get('com_database', []):
        print(f"\n  → {tabela} (Database='YYYYMM')")
        pasta = base_raw_path / SERVICO / tabela
        extrair_tabela(SERVICO, tabela, pasta, "Database", periodos_mensais)

    # Tabelas com DataBase='YYYYMM'
    for tabela in TABELAS.get('com_DataBase', []):
        print(f"\n  → {tabela} (DataBase='YYYYMM')")
        pasta = base_raw_path / SERVICO / tabela
        extrair_tabela(SERVICO, tabela, pasta, "DataBase", periodos_mensais)

    print("\nConcluído!")

if __name__ == '__main__':
    extrair()
