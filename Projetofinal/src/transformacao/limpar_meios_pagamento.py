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


def transformar_meios_pagamento(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Funcao pura: limpa MeiosdePagamentosMensalDA, descarta TEC e padroniza para R$ e unidades."""
    df = df_bruto.copy()
    df["ano_mes"] = pd.to_numeric(df["AnoMes"], errors="coerce").astype("int64")
    df["ano_mes_dt"] = pd.to_datetime(df["ano_mes"].astype(str) + "01", format="%Y%m%d")

    # API MPV publica quantidades em milhares e valores em R$ milhoes; convertemos para absoluto
    # Colunas TEC descartadas (zeradas no periodo recente)
    mapa_qtd = {
        "quantidadePix": "qtd_pix_mpv",
        "quantidadeTED": "qtd_ted",
        "quantidadeBoleto": "qtd_boleto",
        "quantidadeCheque": "qtd_cheque",
        "quantidadeDOC": "qtd_doc",
    }
    mapa_vl = {
        "valorPix": "vl_pix_mpv",
        "valorTED": "vl_ted",
        "valorBoleto": "vl_boleto",
        "valorCheque": "vl_cheque",
        "valorDOC": "vl_doc",
    }

    out = pd.DataFrame({"ano_mes": df["ano_mes"], "ano_mes_dt": df["ano_mes_dt"]})
    for orig, dest in mapa_qtd.items():
        out[dest] = (converter_numero_br(df[orig]).fillna(0) * 1_000).round(0).astype("int64")
    for orig, dest in mapa_vl.items():
        out[dest] = (converter_numero_br(df[orig]).fillna(0) * 1_000_000).round(2)

    out = out.sort_values("ano_mes").reset_index(drop=True)

    total_qtd = out[["qtd_pix_mpv", "qtd_ted", "qtd_boleto", "qtd_cheque", "qtd_doc"]].sum(axis=1)
    total_vl = out[["vl_pix_mpv", "vl_ted", "vl_boleto", "vl_cheque", "vl_doc"]].sum(axis=1)

    out["participacao_pix_qtd_pct"] = (out["qtd_pix_mpv"] / total_qtd * 100.0).round(2)
    out["participacao_pix_vl_pct"] = (out["vl_pix_mpv"] / total_vl * 100.0).round(2)
    return out


def main():
    arq_bruto = (
        config.BRONZE_MPV
        / "MeiosdePagamentosMensalDA"
        / "MeiosdePagamentosMensalDA_202011.csv"
    )
    if not arq_bruto.exists():
        raise FileNotFoundError(f"Arquivo Bronze nao encontrado: {arq_bruto}")

    df_bruto = pd.read_csv(arq_bruto)
    df_limpo = transformar_meios_pagamento(df_bruto)

    destino = config.PRATA_MPV / "meios_pagamento_mensal.parquet"
    salvar_prata(df_limpo, destino, gerar_csv=False)
    registrar_proveniencia(
        origem=arq_bruto.name,
        destino=destino,
        linhas_antes=len(df_bruto),
        linhas_depois=len(df_limpo),
        decisoes=[
            "descartadas colunas TEC (zeradas)",
            "padronizacao de milhares/milhoes para unidades absolutas (qtd e R$)",
            "calculo de participacao_pix_qtd_pct e participacao_pix_vl_pct",
        ],
    )


if __name__ == "__main__":
    config.configurar_log()
    main()
