import sys
from pathlib import Path

# Adiciona a pasta src/utils ao PATH do Python para importar utils_ingestao
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from utils_ingestao import extrair_tabela, gerar_periodos_mensais

# ==============================================================================
# Ingestão — Contexto: SPI
# Tabelas relativas a liquidações do Sistema de Pagamentos Instantâneos.
# ==============================================================================

SERVICO = 'SPI'

TABELAS = {
    'sem_parametro': [
        'PixLiquidadosAtual',
        'PixRemuneracaoContaPI',
        'PixInterrupcaoSPI',
        'PixLiquidadosIntradia',
        'PixDisponibilidadeSPI',
    ]
}

def extrair():
    print("=" * 60)
    print("INGESTÃO PIX — Contexto: SPI (Liquidações)")
    print("=" * 60)

    # Nova hierarquia: src/pix -> src -> etl -> bronze
    base_raw_path = Path(__file__).parent.parent.parent.parent / "data" / "pix_bruto"

    for tabela in TABELAS['sem_parametro']:
        print(f"\n  → {tabela} (sem parâmetro de data)")
        pasta = base_raw_path / SERVICO / tabela
        extrair_tabela(SERVICO, tabela, pasta)

    print("\nConcluído!")

if __name__ == '__main__':
    extrair()
