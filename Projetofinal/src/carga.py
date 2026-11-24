import logging
import sys
from pathlib import Path

import duckdb

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

import config

log = logging.getLogger(__name__)

# Tabelas da Prata carregadas diretamente no schema prata do DuckDB
TABELAS_PRATA = {
    "transacoes_pix": config.PRATA_PIX / "estatisticas_transacoes_pix.parquet",
    "fraudes_pix": config.PRATA_PIX / "estatisticas_fraudes_pix.parquet",
    "usuarios_dict": config.PRATA_PIX / "usuarios_dict_mensal.parquet",
    "taxa_selic": config.PRATA_MACRO / "taxa_selic_mensal.parquet",
    "taxa_ipca": config.PRATA_MACRO / "taxa_ipca_mensal.parquet",
    "meios_pagamento": config.PRATA_MPV / "meios_pagamento_mensal.parquet",
    "cartoes_trimestral": config.PRATA_MPV / "cartoes_trimestral.parquet",
    "pix_macro_enriquecido": config.PRATA_ENRIQUECIDO / "pix_macro_mensal_enriquecido.parquet",
}


def um_valor(con, sql: str):
    return con.execute(sql).fetchone()[0]


def conectar():
    config.BANCO_OURO.parent.mkdir(parents=True, exist_ok=True)
    log.info("banco: %s", config.BANCO_OURO)
    return duckdb.connect(str(config.BANCO_OURO))


def criar_esquemas(con):
    con.execute("CREATE SCHEMA IF NOT EXISTS prata")
    con.execute("CREATE SCHEMA IF NOT EXISTS ouro")
    log.info("esquemas prata e ouro prontos")


def carregar_prata(con):
    for tabela, caminho in TABELAS_PRATA.items():
        if not caminho.exists():
            log.warning("prata.%s: arquivo nao encontrado (%s), pulando", tabela, caminho.name)
            continue
        con.execute(f"""
            CREATE OR REPLACE TABLE prata.{tabela} AS
            SELECT * FROM read_parquet('{caminho.as_posix()}')
        """)
        linhas = um_valor(con, f"SELECT COUNT(*) FROM prata.{tabela}")
        log.info("prata.%s: %s linhas carregadas", tabela, linhas)


def main():
    con = conectar()
    try:
        criar_esquemas(con)
        carregar_prata(con)
    finally:
        con.close()
    log.info("carga concluida")


if __name__ == "__main__":
    config.configurar_log()
    main()
