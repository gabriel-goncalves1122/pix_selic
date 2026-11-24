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

RENAMES_FRAUDES = {
    "AnoMes": "ano_mes",
    "QtdePixcontestados": "qtd_pix_contestados",
    "Qtdecontestacoesaceitas": "qtd_contestacoes_aceitas",
    "Qtdecontestacoesrejeitadas": "qtd_contestacoes_rejeitadas",
    "Qtdecontestacoesaceitasacada100mil": "taxa_contestacoes_aceitas_por_100mil",
    "QtdeUsuarioscommarcacoesdefraude": "qtd_usuarios_marcacao_fraude",
    "QtdeChavesPixcommarcacoesdefraude": "qtd_chaves_marcacao_fraude",
    "ValorPixcontestadosaceitos": "valor_pix_contestados_aceitos",
    "QuantidadedevolvidaintegralmentepormeiodoMED": "qtd_devolvida_integral_med",
    "ValorPixdevolvidosintegralmente": "valor_devolvido_integral_med",
    "QuantidadedevolvidaparcialmentepormeiodoMED": "qtd_devolvida_parcial_med",
    "ValorPixdevolvidosparcialmente": "valor_devolvido_parcial_med",
    "ValorPixresidualnaodevolvido": "valor_residual_nao_devolvido",
    "Quantidadedenaodevolvidossaldoinsuficiente": "qtd_nao_devolvida_saldo_insuficiente",
    "ValorPixnaodevolvidossaldoinsuficiente": "valor_nao_devolvido_saldo_insuficiente",
    "Quantidadedenaodevolvidoscontaencerrada": "qtd_nao_devolvida_conta_encerrada",
    "Valornaodevolvidoscontaencerrada": "valor_nao_devolvido_conta_encerrada",
    "Quantidadedenaodevolvidosmotivosdiversos": "qtd_nao_devolvida_motivos_diversos",
    "ValorPixnaodevolvidosmotivosdiversos": "valor_nao_devolvido_motivos_diversos",
    "PercentualdeDevolucao": "percentual_devolucao",
    "QtdePixbloqueadoscautelarmenteeliberados": "qtd_bloqueio_cautelar_liberado",
    "ValorPixbloqueadoscautelarmenteeliberados": "valor_bloqueio_cautelar_liberado",
    "QtdePixbloqueadoscautelarmenteedevolvidos": "qtd_bloqueio_cautelar_devolvido",
    "ValorPixbloqueadoscautelarmenteedevolvidos": "valor_bloqueio_cautelar_devolvido",
}


def transformar_fraudes(df_bruto: pd.DataFrame) -> pd.DataFrame:
    """Funcao pura: renomeia colunas MED, tipa e calcula KPIs de eficacia do MED."""
    df = df_bruto.rename(columns=RENAMES_FRAUDES).copy()
    df["ano_mes"] = df["ano_mes"].astype("int64")

    cols_qtd = [c for c in df.columns if c.startswith("qtd_")]
    cols_float = [c for c in df.columns if c not in cols_qtd and c != "ano_mes"]

    for col in cols_qtd:
        df[col] = converter_numero_br(df[col]).fillna(0).astype("int64")
    for col in cols_float:
        df[col] = converter_numero_br(df[col]).astype("float64")

    df["ano_mes_dt"] = pd.to_datetime(df["ano_mes"].astype(str) + "01", format="%Y%m%d", errors="coerce")

    # KPIs derivados do funil MED e contas laranjas
    df["custo_fraude_nao_devolvido"] = (
        df["valor_pix_contestados_aceitos"]
        - df["valor_devolvido_integral_med"].fillna(0)
        - df["valor_devolvido_parcial_med"].fillna(0)
    ).round(2)

    aceitas = df["qtd_contestacoes_aceitas"].replace(0, np.nan)
    df["taxa_efetividade_med_pct"] = (
        (df["qtd_devolvida_integral_med"] + df["qtd_devolvida_parcial_med"]) / aceitas * 100.0
    ).round(2)

    usuarios = df["qtd_usuarios_marcacao_fraude"].replace(0, np.nan)
    df["razao_chaves_usuario_fraude"] = (df["qtd_chaves_marcacao_fraude"] / usuarios).round(2)
    return df


def limpar_estatisticas_fraudes():
    arq_bruto = (
        config.BRONZE_PIX
        / "EstatisticasFraudesPix"
        / "EstatisticasFraudesPix_202011.csv"
    )
    if not arq_bruto.exists():
        raise FileNotFoundError(f"Arquivo Bronze nao encontrado: {arq_bruto}")

    df_bruto = pd.read_csv(arq_bruto)
    df_limpo = transformar_fraudes(df_bruto)

    destino = config.PRATA_PIX / "estatisticas_fraudes_pix.parquet"
    salvar_prata(df_limpo, destino, gerar_csv=False)
    registrar_proveniencia(
        origem=arq_bruto.name,
        destino=destino,
        linhas_antes=len(df_bruto),
        linhas_depois=len(df_limpo),
        decisoes=[
            "bypass staircase duplication via 202011",
            "calculados custo_fraude_nao_devolvido, taxa_efetividade_med_pct e razao_chaves_usuario_fraude",
        ],
    )


if __name__ == "__main__":
    config.configurar_log()
    limpar_estatisticas_fraudes()
