import logging
import shutil
import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ / "src") not in sys.path:
    sys.path.insert(0, str(RAIZ / "src"))

import config

log = logging.getLogger("pipeline")


def _garantir_path(caminho: Path):
    if str(caminho) not in sys.path:
        sys.path.insert(0, str(caminho))


def etapa_ingestao():
    """Ingere dados brutos das APIs do BCB (SGS e Olinda Pix/MPV) para a Bronze."""
    _garantir_path(RAIZ / "src" / "ingestao")

    import macro_sgs
    import mpv_meios_pagamento
    import pix_cadastros
    from utils_ingestao import extrair_tabela

    macro_sgs.extrair()
    pix_cadastros.extrair()
    mpv_meios_pagamento.extrair()

    # Bypass da duplicacao em escada: o periodo 202011 ja traz todo o historico
    extrair_tabela(
        "Pix_DadosAbertos",
        "EstatisticasTransacoesPix",
        config.BRONZE_PIX / "EstatisticasTransacoesPix",
        "Database",
        ["202011"],
    )
    extrair_tabela(
        "Pix_DadosAbertos",
        "EstatisticasFraudesPix",
        config.BRONZE_PIX / "EstatisticasFraudesPix",
        "Database",
        ["202011"],
    )


def etapa_transformacao():
    """Limpa e padroniza os datasets da Bronze para Parquet na Prata."""
    _garantir_path(RAIZ / "src" / "transformacao")

    import limpar_transacoes
    import limpar_fraudes
    import limpar_cadastros_dict
    import limpar_selic
    import limpar_ipca
    import limpar_meios_pagamento
    import limpar_cartoes

    limpar_transacoes.processar_transacoes()
    limpar_fraudes.limpar_estatisticas_fraudes()
    limpar_cadastros_dict.main()
    limpar_selic.limpar_taxa_selic()
    limpar_ipca.main()
    limpar_meios_pagamento.main()
    limpar_cartoes.main()


def etapa_enriquecimento():
    """Cruza Pix, Fraudes, DICT, Selic e IPCA e gera atributos derivados na Prata."""
    _garantir_path(RAIZ / "src" / "transformacao")
    import enriquecer

    enriquecer.main()


def etapa_carga():
    """Carrega os Parquets da Prata para o DuckDB (schema prata)."""
    import carga

    carga.main()


def etapa_modelagem():
    """Executa modelos dbt (schema ouro) e testes automatizados de dados."""
    dbt_bin = shutil.which("dbt") or str(Path(sys.executable).parent / "dbt")
    subprocess.run([dbt_bin, "run"], cwd=config.PASTA_DBT, check=True)
    subprocess.run([dbt_bin, "test"], cwd=config.PASTA_DBT, check=True)


ETAPAS = [
    ("ingestao", etapa_ingestao),
    ("transformacao", etapa_transformacao),
    ("enriquecimento", etapa_enriquecimento),
    ("carga", etapa_carga),
    ("modelagem", etapa_modelagem),
]


def executar(nome: str, funcao):
    log.info("etapa %s: inicio", nome)
    comeco = time.perf_counter()
    try:
        funcao()
    except Exception:
        log.exception("etapa %s falhou", nome)
        raise
    duracao = time.perf_counter() - comeco
    log.info("etapa %s: fim em %.1fs", nome, duracao)


def main(a_partir_de=None) -> int:
    config.configurar_log()
    config.criar_pastas()

    nomes = [nome for nome, _ in ETAPAS]
    if a_partir_de and a_partir_de not in nomes:
        log.error("etapa desconhecida: %s", a_partir_de)
        log.error("etapas validas: %s", ", ".join(nomes))
        return 1

    comecou = a_partir_de is None
    for nome, funcao in ETAPAS:
        if nome == a_partir_de:
            comecou = True
        if not comecou:
            log.info("etapa %s: pulada", nome)
            continue
        if funcao is None:
            log.warning("etapa %s: ainda nao implementada", nome)
            continue
        executar(nome, funcao)

    log.info("pipeline concluido")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
