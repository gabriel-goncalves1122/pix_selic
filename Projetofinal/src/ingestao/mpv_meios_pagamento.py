import logging
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
for pasta in (RAIZ / "src", Path(__file__).resolve().parent):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

import config
from utils_ingestao import extrair_tabela

log = logging.getLogger(__name__)

SERVICO = "MPV_DadosAbertos"


def extrair():
    log.info("INGESTAO MPV - Meios de Pagamento Mensais e Cartoes Trimestrais")
    extrair_tabela(
        SERVICO,
        "MeiosdePagamentosMensalDA",
        config.BRONZE_MPV / "MeiosdePagamentosMensalDA",
        "AnoMes",
        ["202011"],
    )
    extrair_tabela(
        SERVICO,
        "Quantidadeetransacoesdecartoes",
        config.BRONZE_MPV / "Quantidadeetransacoesdecartoes",
        "trimestre",
        ["20201"],
    )


if __name__ == "__main__":
    config.configurar_log()
    extrair()
