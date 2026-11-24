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

log = logging.getLogger(__name__)


def transformar_selic(df_meta_bruto: pd.DataFrame, df_real_bruto: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Funcao pura: limpa series diarias da Selic (432 e 11) e agrega visao mensal."""
    df_meta = pd.DataFrame({
        "data_dt": pd.to_datetime(df_meta_bruto["data"], format="%d/%m/%Y", errors="coerce"),
        "selic_meta_aa": converter_numero_br(df_meta_bruto["valor"]),
    }).dropna(subset=["data_dt"])

    selic_dia = converter_numero_br(df_real_bruto["valor"])
    df_real = pd.DataFrame({
        "data_dt": pd.to_datetime(df_real_bruto["data"], format="%d/%m/%Y", errors="coerce"),
        "selic_realizada_dia_pct": selic_dia,
        "selic_realizada_anualizada_pct": (((1.0 + selic_dia / 100.0) ** 252 - 1.0) * 100.0).round(4),
    }).dropna(subset=["data_dt"])

    df_diario = pd.merge(df_meta, df_real, on="data_dt", how="outer").sort_values("data_dt").reset_index(drop=True)
    df_diario["ano_mes"] = df_diario["data_dt"].dt.strftime("%Y%m").astype(int)
    df_diario["ano_mes_dt"] = pd.to_datetime(df_diario["ano_mes"].astype(str) + "01", format="%Y%m%d")

    cols_diario = [
        "data_dt", "ano_mes", "ano_mes_dt",
        "selic_meta_aa", "selic_realizada_dia_pct", "selic_realizada_anualizada_pct",
    ]
    df_diario = df_diario[cols_diario]

    df_mensal = (
        df_diario.groupby(["ano_mes", "ano_mes_dt"], as_index=False)
        .agg(
            selic_meta_fim_mes=("selic_meta_aa", "last"),
            selic_meta_media_mes=("selic_meta_aa", "mean"),
            selic_realizada_media_mes=("selic_realizada_anualizada_pct", "mean"),
            dias_uteis=("selic_realizada_dia_pct", "count"),
        )
    )
    for col in ("selic_meta_fim_mes", "selic_meta_media_mes", "selic_realizada_media_mes"):
        df_mensal[col] = df_mensal[col].round(2)

    return df_diario, df_mensal


def limpar_taxa_selic():
    arq_meta = config.BRONZE_MACRO_SGS / "Selic_Meta_Diaria.csv"
    arq_real = config.BRONZE_MACRO_SGS / "Selic_Realizada_Diaria.csv"

    df_meta = pd.read_csv(arq_meta, sep=";", quotechar='"')
    df_real = pd.read_csv(arq_real, sep=";", quotechar='"')
    df_diario, df_mensal = transformar_selic(df_meta, df_real)

    dest_diario = config.PRATA_MACRO / "taxa_selic_diaria.parquet"
    dest_mensal = config.PRATA_MACRO / "taxa_selic_mensal.parquet"
    salvar_prata(df_diario, dest_diario, gerar_csv=False)
    salvar_prata(df_mensal, dest_mensal, gerar_csv=False)

    registrar_proveniencia(
        origem=f"{arq_meta.name} + {arq_real.name}",
        destino=dest_mensal,
        linhas_antes=len(df_meta),
        linhas_depois=len(df_mensal),
        decisoes=[
            "datas convertidas com format=%d/%m/%Y",
            "selic realizada anualizada base 252 dias uteis",
            "consolidacao mensal (fim de mes e media)",
        ],
    )


if __name__ == "__main__":
    config.configurar_log()
    limpar_taxa_selic()
