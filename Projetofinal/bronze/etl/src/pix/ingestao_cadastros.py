import sys
from pathlib import Path

# Adiciona a pasta src/utils ao PATH do Python para importar utils_ingestao
sys.path.append(str(Path(__file__).parent.parent / "utils"))
from utils_ingestao import extrair_tabela

# ==============================================================================
# Ingestão — Contexto: Cadastros
# Tabelas relativas a estoque de usuários DICT. (Tabela ChavesPix removida).
# ==============================================================================

SERVICO = 'Pix_DadosAbertos'

TABELAS = {
    'sem_parametro': [
        'PixUsuariosCadastradosDICT',
    ]
}

def extrair():
    print("=" * 60)
    print("INGESTÃO PIX — Contexto: Cadastros")
    print("=" * 60)

    # Nova hierarquia: src/pix -> src -> etl -> bronze
    base_raw_path = Path(__file__).parent.parent.parent.parent / "data" / "pix_bruto"

    # Tabelas sem parâmetro
    for tabela in TABELAS.get('sem_parametro', []):
        print(f"\n  → {tabela} (sem parâmetro de data)")
        pasta = base_raw_path / SERVICO / tabela
        extrair_tabela(SERVICO, tabela, pasta)

    print("\nConcluído!")

if __name__ == '__main__':
    extrair()
