import logging
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent.parent
for pasta in (RAIZ / "src", Path(__file__).resolve().parent):
    if str(pasta) not in sys.path:
        sys.path.insert(0, str(pasta))

import config
from comum import registrar_proveniencia, salvar_prata

log = logging.getLogger(__name__)


def transformar_cadastros_dict(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Funcao pura: padroniza estoque de usuarios cadastrados no DICT por mes."""
    df = df_bruto.rename(
        columns={
            "DataGraficosPix": "data_referencia",
            "qtdUsuariosPessoaFisica": "qtd_usuarios_pf",
            "qtdUsuariosPessoaJuridica": "qtd_usuarios_pj",
            "qtdUsuariosCadastradosDICTTotal": "qtd_usuarios_total",
        }
    ).copy()

    df["data_referencia"] = pd.to_datetime(df["data_referencia"], errors="coerce")
    df = df.dropna(subset=["data_referencia"]).sort_values("data_referencia")

    for col in ("qtd_usuarios_pf", "qtd_usuarios_pj", "qtd_usuarios_total"):
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype("int64")

    df["ano_mes"] = df["data_referencia"].dt.strftime("%Y%m").astype(int)
    df["ano_mes_dt"] = pd.to_datetime(df["ano_mes"].astype(str) + "01", format="%Y%m%d")

    df_mensal = (
        df.groupby(["ano_mes", "ano_mes_dt"], as_index=False)
        .agg(
            qtd_usuarios_pf=("qtd_usuarios_pf", "last"),
            qtd_usuarios_pj=("qtd_usuarios_pj", "last"),
            qtd_usuarios_total=("qtd_usuarios_total", "last"),
        )
        .sort_values("ano_mes")
        .reset_index(drop=True)
    )
    df_mensal["variacao_usuarios_pct"] = (
        df_mensal["qtd_usuarios_total"].pct_change() * 100.0
    ).round(2)

    return df_mensal


def main():
    arq_bruto = (
        config.BRONZE_PIX
        / "PixUsuariosCadastradosDICT"
        / "PixUsuariosCadastradosDICT.csv"
    )
    if not arq_bruto.exists():
        raise FileNotFoundError(f"Arquivo Bronze nao encontrado: {arq_bruto}")

    df_bruto = pd.read_csv(arq_bruto)
    df_limpo = transformar_cadastros_dict(df_bruto)

    destino = config.PRATA_PIX / "usuarios_dict_mensal.parquet"
    salvar_prata(df_limpo, destino, gerar_csv=False)
    registrar_proveniencia(
        origem=arq_bruto.name,
        destino=destino,
        linhas_antes=len(df_bruto),
        linhas_depois=len(df_limpo),
        decisoes=[
            "agregacao mensal mantendo ultimo estoque do mes",
            "calculo de variacao_usuarios_pct",
        ],
    )


if __name__ == "__main__":
    config.configurar_log()
    main()
