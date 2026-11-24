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


def conferir_chaves(df_esq: pd.DataFrame, df_dir: pd.DataFrame, chave: str, nome_dir: str) -> int:
    """Verifica cobertura de chaves antes da juncao (padrao Aula 7)."""
    chaves_esq = set(df_esq[chave].dropna())
    chaves_dir = set(df_dir[chave].dropna())
    sem_par = chaves_esq - chaves_dir
    if sem_par:
        log.warning("enriquecimento (%s): %s meses sem par -> %s", nome_dir, len(sem_par), sorted(sem_par)[:5])
    else:
        log.info("enriquecimento (%s): 100%% dos meses casados (%s chaves)", nome_dir, len(chaves_esq))
    return len(sem_par)


def agregar_transacoes_mensal(df_tx: pd.DataFrame) -> pd.DataFrame:
    """Funcao pura: agrega transacoes Pix em 1 unica passagem sobre o DataFrame."""
    piv = (
        df_tx.groupby(["ano_mes", "ano_mes_dt", "pag_pfpj"], observed=True)[["quantidade", "valor"]]
        .sum()
        .unstack("pag_pfpj", fill_value=0)
    )

    qtd_pf = piv["quantidade"].get("PF", 0)
    qtd_pj = piv["quantidade"].get("PJ", 0)
    vl_pf = piv["valor"].get("PF", 0.0)
    vl_pj = piv["valor"].get("PJ", 0.0)

    qtd_total = piv["quantidade"].sum(axis=1)
    vl_total = piv["valor"].sum(axis=1)

    res = pd.DataFrame({
        "ano_mes": piv.index.get_level_values("ano_mes"),
        "ano_mes_dt": piv.index.get_level_values("ano_mes_dt"),
        "qtd_transacoes_total": qtd_total.to_numpy(),
        "vl_transacoes_total": vl_total.to_numpy(),
        "qtd_pag_pf": qtd_pf.to_numpy() if hasattr(qtd_pf, "to_numpy") else qtd_pf,
        "vl_pag_pf": vl_pf.to_numpy() if hasattr(vl_pf, "to_numpy") else vl_pf,
        "qtd_pag_pj": qtd_pj.to_numpy() if hasattr(qtd_pj, "to_numpy") else qtd_pj,
        "vl_pag_pj": vl_pj.to_numpy() if hasattr(vl_pj, "to_numpy") else vl_pj,
    }).sort_values("ano_mes").reset_index(drop=True)

    res["ticket_medio_pix"] = (res["vl_transacoes_total"] / res["qtd_transacoes_total"]).round(2)
    res["pct_valor_pj"] = (res["vl_pag_pj"] / res["vl_transacoes_total"] * 100.0).round(2)
    res["pct_qtd_pj"] = (res["qtd_pag_pj"] / res["qtd_transacoes_total"] * 100.0).round(2)
    res["variacao_vl_pix_pct"] = (res["vl_transacoes_total"].pct_change() * 100.0).round(2)
    res["variacao_qtd_pix_pct"] = (res["qtd_transacoes_total"].pct_change() * 100.0).round(2)
    return res


def marcar_extremos(df: pd.DataFrame, colunas: list[str], limite_z: float = 3.0) -> pd.DataFrame:
    """Funcao pura (Aula 5): marca extremos por IQR e Z-score sem remover registros legitimos."""
    res = df.copy()
    for col in colunas:
        if col not in res.columns:
            continue
        serie = res[col].dropna()
        if serie.empty:
            continue
        q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
        iqr = q3 - q1
        res[f"{col}_extremo_iqr"] = (res[col] < (q1 - 1.5 * iqr)) | (res[col] > (q3 + 1.5 * iqr))

        desvio = serie.std()
        res[f"{col}_extremo_z"] = ((res[col] - serie.mean()) / desvio).abs() > limite_z if desvio > 0 else False
        log.info(
            "extremos (%s): IQR=%s | Z-score>%s=%s",
            col,
            int(res[f"{col}_extremo_iqr"].sum()),
            limite_z,
            int(res[f"{col}_extremo_z"].sum()),
        )
    return res


def enriquecer_pix_macro(
    df_tx_mensal: pd.DataFrame,
    df_fraudes: pd.DataFrame,
    df_dict: pd.DataFrame,
    df_selic: pd.DataFrame,
    df_ipca: pd.DataFrame,
    df_mpv: pd.DataFrame,
) -> pd.DataFrame:
    """Funcao pura: une Pix com Funil MED, DICT, Selic, IPCA e Meios Tradicionais + metricas reais."""
    cols_fraudes = [
        "ano_mes", "qtd_pix_contestados", "qtd_contestacoes_aceitas",
        "taxa_contestacoes_aceitas_por_100mil", "qtd_usuarios_marcacao_fraude",
        "qtd_chaves_marcacao_fraude", "valor_pix_contestados_aceitos",
        "qtd_devolvida_integral_med", "valor_devolvido_integral_med",
        "qtd_devolvida_parcial_med", "valor_devolvido_parcial_med",
        "valor_nao_devolvido_saldo_insuficiente", "valor_nao_devolvido_conta_encerrada",
        "percentual_devolucao", "custo_fraude_nao_devolvido",
        "taxa_efetividade_med_pct", "razao_chaves_usuario_fraude",
    ]
    cols_dict = ["ano_mes", "qtd_usuarios_pf", "qtd_usuarios_pj", "qtd_usuarios_total", "variacao_usuarios_pct"]
    cols_selic = ["ano_mes", "selic_meta_fim_mes", "selic_meta_media_mes", "selic_realizada_media_mes", "dias_uteis"]
    cols_ipca = ["ano_mes", "ipca_mensal_pct", "ipca_acumulado_12m_pct"]
    cols_mpv = [
        "ano_mes", "qtd_ted", "vl_ted", "qtd_boleto", "vl_boleto",
        "qtd_cheque", "vl_cheque", "qtd_doc", "vl_doc",
        "participacao_pix_qtd_pct", "participacao_pix_vl_pct",
    ]

    df = (
        df_tx_mensal
        .merge(df_fraudes[cols_fraudes], on="ano_mes", how="left", validate="one_to_one")
        .merge(df_dict[cols_dict], on="ano_mes", how="left", validate="one_to_one")
        .merge(df_selic[cols_selic], on="ano_mes", how="left", validate="one_to_one")
        .merge(df_ipca[cols_ipca], on="ano_mes", how="left", validate="one_to_one")
        .merge(df_mpv[cols_mpv], on="ano_mes", how="left", validate="one_to_one")
        .sort_values("ano_mes")
        .reset_index(drop=True)
    )

    # Juro real ex-post (Fisher): (1 + Selic) / (1 + IPCA_12m) - 1
    df["juro_real_ex_post_pct"] = (
        ((1.0 + df["selic_meta_fim_mes"] / 100.0) / (1.0 + df["ipca_acumulado_12m_pct"] / 100.0) - 1.0) * 100.0
    ).round(2)

    # Deflacionamento pelo IPCA acumulado (precos constantes do ultimo mes da serie)
    fator_mensal = (1.0 + df["ipca_mensal_pct"].fillna(0.0) / 100.0)
    indice_acum = fator_mensal.cumprod()
    fator_correcao = indice_acum.iloc[-1] / indice_acum
    df["vl_pix_real_deflacionado"] = (df["vl_transacoes_total"] * fator_correcao).round(2)
    df["ticket_medio_pix_real"] = (df["ticket_medio_pix"] * fator_correcao).round(2)

    return marcar_extremos(df, ["vl_transacoes_total", "taxa_contestacoes_aceitas_por_100mil"])


def main():
    df_tx = pd.read_parquet(
        config.PRATA_PIX / "estatisticas_transacoes_pix.parquet",
        columns=["ano_mes", "ano_mes_dt", "pag_pfpj", "quantidade", "valor"],
    )
    df_fraudes = pd.read_parquet(config.PRATA_PIX / "estatisticas_fraudes_pix.parquet")
    df_dict = pd.read_parquet(config.PRATA_PIX / "usuarios_dict_mensal.parquet")
    df_selic = pd.read_parquet(config.PRATA_MACRO / "taxa_selic_mensal.parquet")
    df_ipca = pd.read_parquet(config.PRATA_MACRO / "taxa_ipca_mensal.parquet")
    df_mpv = pd.read_parquet(config.PRATA_MPV / "meios_pagamento_mensal.parquet")

    df_tx_mensal = agregar_transacoes_mensal(df_tx)

    sem_par = {
        "fraudes": conferir_chaves(df_tx_mensal, df_fraudes, "ano_mes", "fraudes"),
        "dict": conferir_chaves(df_tx_mensal, df_dict, "ano_mes", "dict"),
        "selic": conferir_chaves(df_tx_mensal, df_selic, "ano_mes", "selic"),
        "ipca": conferir_chaves(df_tx_mensal, df_ipca, "ano_mes", "ipca"),
        "meios_pagamento": conferir_chaves(df_tx_mensal, df_mpv, "ano_mes", "meios_pagamento"),
    }

    df_enriquecido = enriquecer_pix_macro(df_tx_mensal, df_fraudes, df_dict, df_selic, df_ipca, df_mpv)

    destino = config.PRATA_ENRIQUECIDO / "pix_macro_mensal_enriquecido.parquet"
    salvar_prata(df_enriquecido, destino, gerar_csv=False)
    registrar_proveniencia(
        origem="pix + fraudes_med + dict + selic + ipca + meios_pagamento_mpv",
        destino=destino,
        linhas_antes=len(df_tx_mensal),
        linhas_depois=len(df_enriquecido),
        decisoes=[
            "agregacao mensal em passagem unica via groupby+unstack",
            "merge left com validate=one_to_one em ano_mes",
            "calculo de juro_real_ex_post_pct e vl_pix_real_deflacionado",
            "marcacao de extremos IQR e Z-score sem exclusao",
        ],
        extras={"sem_par_por_fonte": sem_par},
    )


if __name__ == "__main__":
    config.configurar_log()
    main()
