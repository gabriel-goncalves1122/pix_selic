import logging
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
for pasta in (RAIZ / "src", Path(__file__).resolve().parent):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

import config
from comum import converter_numero_br, registrar_proveniencia, salvar_prata

log = logging.getLogger(__name__)


def transformar_ipca(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Funcao pura: limpa e calcula IPCA mensal e acumulado 12m (vetorizado via log-soma)."""
    df = pd.DataFrame({
        "data_dt": pd.to_datetime(df_bruto["data"], format="%d/%m/%Y", errors="coerce"),
        "ipca_mensal_pct": converter_numero_br(df_bruto["valor"]),
    }).dropna(subset=["data_dt", "ipca_mensal_pct"]).sort_values("data_dt").reset_index(drop=True)

    df["ano_mes"] = df["data_dt"].dt.strftime("%Y%m").astype(int)
    df["ano_mes_dt"] = pd.to_datetime(df["ano_mes"].astype(str) + "01", format="%Y%m%d")

    # Vetorizado em C/NumPy: prod(1 + r) = exp(sum(log(1 + r))) sem callback Python
    log_fator = np.log1p(df["ipca_mensal_pct"] / 100.0)
    df["ipca_acumulado_12m_pct"] = (
        np.expm1(log_fator.rolling(window=12, min_periods=12).sum()) * 100.0
    ).round(2)

    return df[["ano_mes", "ano_mes_dt", "ipca_mensal_pct", "ipca_acumulado_12m_pct"]]


def main():
    arq_bruto = config.BRONZE_MACRO_SGS / "IPCA_Mensal.csv"
    if not arq_bruto.exists():
        raise FileNotFoundError(f"Arquivo Bronze nao encontrado: {arq_bruto}")

    df_bruto = pd.read_csv(arq_bruto, sep=";", quotechar='"')
    df_limpo = transformar_ipca(df_bruto)

    destino = config.PRATA_MACRO / "taxa_ipca_mensal.parquet"
    salvar_prata(df_limpo, destino, gerar_csv=False)
    registrar_proveniencia(
        origem=arq_bruto.name,
        destino=destino,
        linhas_antes=len(df_bruto),
        linhas_depois=len(df_limpo),
        decisoes=[
            "datas convertidas com format=%d/%m/%Y",
            "ipca_acumulado_12m_pct calculado de forma vetorizada via log1p/expm1",
        ],
    )


if __name__ == "__main__":
    config.configurar_log()
    main()
