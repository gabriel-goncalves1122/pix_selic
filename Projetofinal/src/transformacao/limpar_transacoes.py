import logging
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
for pasta in (RAIZ / "src", Path(__file__).resolve().parent):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

import config
from comum import converter_numero_br, registrar_proveniencia, salvar_prata
from formatadores import limpar_nomes_colunas

log = logging.getLogger(__name__)


def transformar_transacoes(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Funcao pura: padroniza colunas, filtra ruido e converte tipos."""
    df = limpar_nomes_colunas(df_bruto.copy())

    if "natureza" in df.columns:
        df = df[df["natureza"] != "Nao disponivel"].copy()

    for col in ("finalidade", "formainiciacao"):
        if col in df.columns:
            df[col] = df[col].fillna("Nao disponivel")

    for col in ("pag_idade", "rec_idade", "pag_regiao", "rec_regiao"):
        if col in df.columns:
            df[col] = df[col].fillna("Nao informado")

    if "valor" in df.columns:
        df["valor"] = converter_numero_br(df["valor"])

    if "ano_mes" in df.columns:
        unicos = df["ano_mes"].dropna().unique()
        mapa_dt = {m: pd.to_datetime(str(int(m)), format="%Y%m") for m in unicos}
        df["ano_mes_dt"] = df["ano_mes"].map(mapa_dt)
    return df


def processar_transacoes():
    arq_bronze = (
        config.BRONZE_PIX
        / "EstatisticasTransacoesPix"
        / "EstatisticasTransacoesPix_202011.csv"
    )
    if not arq_bronze.exists():
        raise FileNotFoundError(f"Arquivo base 202011 nao encontrado na Bronze: {arq_bronze}")

    df_bruto = pd.read_csv(arq_bronze, engine="pyarrow")
    df_limpo = transformar_transacoes(df_bruto)
    removidas = len(df_bruto) - len(df_limpo)
    if removidas:
        log.info("transacoes Pix: %s linhas com natureza='Nao disponivel' removidas", removidas)

    destino = config.PRATA_PIX / "estatisticas_transacoes_pix.parquet"
    salvar_prata(df_limpo, destino, gerar_csv=False)
    registrar_proveniencia(
        origem=arq_bronze.name,
        destino=destino,
        linhas_antes=len(df_bruto),
        linhas_depois=len(df_limpo),
        decisoes=[
            "bypass staircase duplication via 202011",
            f"removidas {removidas} linhas com natureza='Nao disponivel'",
            "padronizacao de nulos em finalidade/formainiciacao/idade/regiao",
            "valor convertido de PT-BR para float64",
        ],
    )


if __name__ == "__main__":
    config.configurar_log()
    processar_transacoes()
