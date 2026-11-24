import logging
from pathlib import Path

# Raiz do projeto calculada a partir deste arquivo (src/config.py -> raiz)
RAIZ = Path(__file__).resolve().parent.parent

# Camadas do Lakehouse Medalhao
BRONZE = RAIZ / "dados" / "bronze"
PRATA = RAIZ / "dados" / "prata"
OURO = RAIZ / "dados" / "ouro"

# Subpastas da Bronze
BRONZE_PIX = BRONZE / "pix_bruto" / "Pix_DadosAbertos"
BRONZE_MPV = BRONZE / "meios_pagamento" / "MPV_DadosAbertos"
BRONZE_MACRO_SGS = BRONZE / "macro_bruto" / "sgs"
BRONZE_MACRO_SELIC_OP = BRONZE / "macro_bruto" / "selic_operacoes" / "OperacoesEmUmMes"

# Subpastas da Prata
PRATA_PIX = PRATA / "pix_limpo"
PRATA_MPV = PRATA / "meios_pagamento"
PRATA_MACRO = PRATA / "macro_limpo"
PRATA_ENRIQUECIDO = PRATA / "enriquecido"

# Camada Ouro (DuckDB + dbt)
BANCO_OURO = OURO / "projeto.duckdb"
PASTA_DBT = RAIZ / "ecox14_pix"

# Parametros de ingestao
DATA_INICIAL_SGS = "01/01/2020"
ANO_INICIO_PIX = 2020
MES_INICIO_PIX = 11

# Logging centralizado (tela + arquivo)
ARQUIVO_LOG = RAIZ / "pipeline.log"


def configurar_log(nivel=logging.INFO):
    """Configura logging para console e arquivo pipeline.log."""
    logging.basicConfig(
        level=nivel,
        format="%(asctime)s | %(levelname)-7s | %(name)-20s | %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(ARQUIVO_LOG, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


def criar_pastas():
    """Garante que os diretorios das camadas existam antes de rodar o pipeline."""
    for pasta in (
        BRONZE_PIX,
        BRONZE_MPV,
        BRONZE_MACRO_SGS,
        BRONZE_MACRO_SELIC_OP,
        PRATA_PIX,
        PRATA_MPV,
        PRATA_MACRO,
        PRATA_ENRIQUECIDO,
        OURO,
    ):
        pasta.mkdir(parents=True, exist_ok=True)
