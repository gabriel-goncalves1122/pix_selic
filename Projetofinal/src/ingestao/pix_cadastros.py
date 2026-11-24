import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from utils_ingestao import extrair_tabela

log = logging.getLogger(__name__)

SERVICO = 'Pix_DadosAbertos'

TABELAS = {
    'sem_parametro': [
        'PixUsuariosCadastradosDICT',
    ]
}


def extrair():
    log.info("INGESTAO PIX - Contexto: Cadastros")
    base_raw_path = Path(__file__).parent.parent.parent / "dados" / "bronze" / "pix_bruto"

    for tabela in TABELAS.get('sem_parametro', []):
        log.info("Extraindo %s (sem parametro de data)", tabela)
        pasta = base_raw_path / SERVICO / tabela
        extrair_tabela(SERVICO, tabela, pasta)

    log.info("Ingestao Cadastros concluida")

if __name__ == '__main__':
    extrair()
