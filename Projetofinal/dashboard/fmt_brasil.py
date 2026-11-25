"""
Funcoes puras de formatacao brasileira (pt-BR) e preparacao de tabelas para o dashboard.
Camada de apresentacao (FCIS): sem estado e sem efeitos colaterais.
"""
import math
import pandas as pd

PALETA = {
    "azul": "#1B3A5F",
    "azul_claro": "#3A7CA5",
    "laranja": "#D96F2C",
    "verde": "#2E8B57",
    "vermelho": "#C0392B",
    "roxo": "#6C5B7B",
    "dourado": "#D4AC0D",
    "cinza": "#7F8C8D",
}


def br(valor, casas: int = 1, escala: float = 1.0, sufixo: str = "") -> str:
    """Formata numero escalar no padrao brasileiro, tratando None e NaN com seguranca."""
    if valor is None:
        return "sem dado"
    try:
        num = float(valor)
    except (TypeError, ValueError):
        return "sem dado"
    if math.isnan(num) or math.isinf(num):
        return "sem dado"

    texto = f"{(num / escala):,.{casas}f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".") + sufixo


def escalar_serie(serie: pd.Series, escala: float) -> pd.Series:
    """Converte serie numerica para a escala visual desejada (ex.: 1e9 para bilhoes)."""
    if escala == 0:
        raise ValueError("Escala nao pode ser zero.")
    return pd.to_numeric(serie, errors="coerce") / escala


def formatar_coluna_br(
    serie: pd.Series,
    casas: int = 1,
    escala: float = 1.0,
    prefixo: str = "",
    sufixo: str = "",
) -> pd.Series:
    """Aplica formatacao brasileira em uma Series do pandas para exibicao em tabelas."""
    def _fmt(val):
        texto = br(val, casas=casas, escala=escala, sufixo=sufixo)
        if texto == "sem dado":
            return texto
        return f"{prefixo}{texto}"

    return serie.apply(_fmt)


def preparar_tabela_macro(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara tabela mensal consolidada com colunas legiveis e valores em pt-BR."""
    return pd.DataFrame({
        "Período": df["periodo_label"],
        "Qtd. Pix (bi)": formatar_coluna_br(df["qtd_transacoes_total"], casas=2, escala=1e9, sufixo=" bi"),
        "Volume Nominal": formatar_coluna_br(df["vl_transacoes_total"], casas=2, escala=1e12, prefixo="R$ ", sufixo=" tri"),
        "Volume Real (IPCA)": formatar_coluna_br(df["vl_pix_real_deflacionado"], casas=2, escala=1e12, prefixo="R$ ", sufixo=" tri"),
        "Ticket Médio": formatar_coluna_br(df["ticket_medio_pix"], casas=2, escala=1.0, prefixo="R$ "),
        "% Valor PJ": formatar_coluna_br(df["pct_valor_pj"], casas=1, escala=1.0, sufixo="%"),
        "Selic Meta": formatar_coluna_br(df["selic_meta_fim_mes"], casas=2, escala=1.0, sufixo="%"),
        "IPCA 12m": formatar_coluna_br(df["ipca_acumulado_12m_pct"], casas=2, escala=1.0, sufixo="%"),
        "Juro Real": formatar_coluna_br(df["juro_real_ex_post_pct"], casas=2, escala=1.0, sufixo="%"),
    })


def preparar_tabela_cartoes(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara tabela comparativa entre Pix e Cartoes com valores em pt-BR."""
    return pd.DataFrame({
        "Trimestre": df["ano_trimestre"],
        "Meio de Pagamento": df["meio_pagamento"],
        "Qtd. Transações": formatar_coluna_br(df["qtd_transacoes"], casas=2, escala=1e9, sufixo=" bi"),
        "Volume Financeiro": formatar_coluna_br(df["vl_transacoes"], casas=2, escala=1e12, prefixo="R$ ", sufixo=" tri"),
        "Ticket Médio": formatar_coluna_br(df["ticket_medio"], casas=2, escala=1.0, prefixo="R$ "),
        "Share Qtd.": formatar_coluna_br(df["share_qtd_pct"], casas=1, escala=1.0, sufixo="%"),
        "Share Volume": formatar_coluna_br(df["share_vl_pct"], casas=1, escala=1.0, sufixo="%"),
    })


def preparar_tabela_regional(df: pd.DataFrame) -> pd.DataFrame:
    """Prepara tabela de fluxo regional (Pago vs. Recebido) com valores em pt-BR."""
    return pd.DataFrame({
        "Região": df["regiao"],
        "Volume Pago": formatar_coluna_br(df["vl_pago"], casas=2, escala=1e12, prefixo="R$ ", sufixo=" tri"),
        "Volume Recebido": formatar_coluna_br(df["vl_recebido"], casas=2, escala=1e12, prefixo="R$ ", sufixo=" tri"),
        "Saldo Líquido": formatar_coluna_br(df["saldo_liquido"], casas=1, escala=1e9, prefixo="R$ ", sufixo=" bi"),
        "Qtd. Paga": formatar_coluna_br(df["qtd_paga"], casas=2, escala=1e9, sufixo=" bi"),
    })


def nota_volume_nominal_real(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Volume Nominal vs Real."""
    ult = df.dropna(subset=["vl_transacoes_total", "vl_pix_real_deflacionado"]).iloc[-1]
    sub = (
        f"Em {ult['periodo_label']}, o volume real foi de R$ {br(ult['vl_pix_real_deflacionado'], 2, 1e12, ' tri')} "
        f"frente a R$ {br(ult['vl_transacoes_total'], 2, 1e12, ' tri')} nominais."
    )
    rodape = "Obs.: A área sombreada evidencia a erosão inflacionária acumulada pelo IPCA no período."
    return sub, rodape


def nota_politica_monetaria(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Politica Monetaria."""
    juro_medio = df["juro_real_ex_post_pct"].mean()
    selic_max = df["selic_meta_fim_mes"].max()
    n_neg = int((df["juro_real_ex_post_pct"] < 0).sum())
    sub = (
        f"Juro real médio de {br(juro_medio, 2, 1.0, '% a.a.')}, com pico da Selic em "
        f"{br(selic_max, 2, 1.0, '% a.a.')} e {n_neg} meses em terreno negativo."
    )
    rodape = "Obs.: Juro real ex-post calculado pela equação de Fisher entre Selic Meta e IPCA 12m."
    return sub, rodape


def nota_dispersao_macro(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Dispersao Macro."""
    base = df.dropna(subset=["juro_real_ex_post_pct", "vl_pix_real_deflacionado"])
    corr = base["juro_real_ex_post_pct"].corr(base["vl_pix_real_deflacionado"]) if len(base) > 2 else float("nan")
    sub = (
        f"O Pix manteve expansão em ciclos de juro negativo e positivo (correlação linear r = {br(corr, 2)})."
    )
    rodape = "Obs.: O tamanho das bolhas é proporcional ao ticket médio mensal do Pix (R$)."
    return sub, rodape


def nota_share_meios(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Share de Quantidade Pix vs Cartoes."""
    ult_t = df["ano_trimestre"].iloc[-1]
    ult = df[df["ano_trimestre"] == ult_t].set_index("meio_pagamento")["share_qtd_pct"]
    pix = br(ult.get("Pix"), 1, 1.0, "%")
    cred = br(ult.get("Crédito"), 1, 1.0, "%")
    deb = br(ult.get("Débito"), 1, 1.0, "%")
    sub = f"Em {ult_t}, o Pix alcançou {pix} das transações, contra {cred} no Crédito e {deb} no Débito."
    rodape = "Obs.: O Pix posicionado na base do gráfico destaca seu ganho contínuo de participação."
    return sub, rodape


def nota_comparativo_cartoes(df_ultimo: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Volume e Ticket Medio do ultimo trimestre."""
    top_vol = df_ultimo.sort_values("vl_transacoes", ascending=False).iloc[0]
    top_tkt = df_ultimo.sort_values("ticket_medio", ascending=False).iloc[0]
    sub = (
        f"{top_vol['meio_pagamento']} lidera em volume (R$ {br(top_vol['vl_transacoes'], 2, 1e12, ' tri')}), "
        f"enquanto {top_tkt['meio_pagamento']} tem o maior ticket médio (R$ {br(top_tkt['ticket_medio'], 2)})."
    )
    rodape = "Obs.: Barras ordenadas em ordem crescente de volume financeiro no trimestre."
    return sub, rodape


def nota_meios_tradicionais(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Meios Tradicionais."""
    ult = df.iloc[-1]
    sub = (
        f"Em {ult['periodo_label']}, a TED movimentou R$ {br(ult['vl_ted'], 1, 1e9, ' bi')} "
        f"e o Boleto R$ {br(ult['vl_boleto'], 1, 1e9, ' bi')}, com DOC e Cheque em declínio."
    )
    rodape = "Obs.: Na escala logarítmica, meses zerados após o fim do DOC são omitidos automaticamente."
    return sub, rodape


def nota_natureza_pix(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Natureza Economica do Pix."""
    total = df["vl_transacoes"].sum()
    top = df.sort_values("vl_transacoes", ascending=False).iloc[0]
    pct = (top["vl_transacoes"] / total * 100) if total else 0.0
    sub = (
        f"{top['natureza']} concentra {br(pct, 1, 1.0, '%')} do volume financeiro "
        f"(R$ {br(top['vl_transacoes'], 2, 1e12, ' tri')})."
    )
    rodape = "Obs.: Transações empresariais (B2B/P2B) têm ticket muito superior ao P2P."
    return sub, rodape


def nota_regional_fluxo(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Volume Pago vs Recebido por Regiao."""
    top = df.sort_values("vl_recebido", ascending=False).iloc[0]
    sub = (
        f"A região {top['regiao']} concentra o maior fluxo: R$ {br(top['vl_recebido'], 2, 1e12, ' tri')} "
        f"recebidos e R$ {br(top['vl_pago'], 2, 1e12, ' tri')} pagos."
    )
    rodape = "Obs.: Regiões ordenadas em ordem crescente de volume recebido; UFs não informadas foram excluídas."
    return sub, rodape


def nota_saldo_liquido(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Saldo Liquido Regional."""
    ord_df = df.sort_values("saldo_liquido", ascending=False)
    maior = ord_df.iloc[0]
    menor = ord_df.iloc[-1]
    sub = (
        f"Maior superávit em {maior['regiao']} (R$ {br(maior['saldo_liquido'], 1, 1e9, ' bi')}) "
        f"e maior déficit em {menor['regiao']} (R$ {br(menor['saldo_liquido'], 1, 1e9, ' bi')})."
    )
    rodape = "Obs.: Saldos positivos indicam entrada líquida de recursos interestaduais via Pix."
    return sub, rodape


def nota_etario(df: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Mapa de Calor Etario."""
    totais = df.groupby("faixa_etaria")["qtd_transacoes"].sum().sort_values(ascending=False)
    top_faixa = totais.index[0]
    sub = f"A faixa de {top_faixa} lidera o uso do Pix com {br(totais.iloc[0], 1, 1e9, ' bi')} de transações no período."
    rodape = "Obs.: Faixas acima de 50 anos mostram intensificação gradual ao longo dos meses."
    return sub, rodape


def nota_funil_med(df_med: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Funil Financeiro MED."""
    aceito = df_med["valor_pix_contestados_aceitos"].sum()
    dev = df_med["valor_devolvido_integral_med"].fillna(0).sum() + df_med["valor_devolvido_parcial_med"].fillna(0).sum()
    pct_dev = (dev / aceito * 100) if aceito else 0.0
    sub = (
        f"De R$ {br(aceito, 1, 1e6, ' mi')} contestados e aceitos, {br(pct_dev, 1, 1.0, '%')} "
        f"(R$ {br(dev, 1, 1e6, ' mi')}) foram devolvidos."
    )
    rodape = "Obs.: Série do MED disponível a partir de 2022."
    return sub, rodape


def nota_efetividade_laranjas(df_med: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Efetividade MED vs Laranjas."""
    efet = df_med["taxa_efetividade_med_pct"].mean()
    lar = df_med["razao_chaves_usuario_fraude"].mean()
    sub = f"Efetividade média de {br(efet, 1, 1.0, '%')} frente a {br(lar, 2, 1.0, 'x')} chaves marcadas por usuário fraudador."
    rodape = "Obs.: O eixo duplo separa o percentual de devolução (esquerda) da razão de chaves por usuário (direita)."
    return sub, rodape


def nota_causas_nao_devolucao(df_med: pd.DataFrame) -> tuple[str, str]:
    """Subtitulo (resposta) e rodape para Causas de Nao Devolucao no MED."""
    insuf = df_med["valor_nao_devolvido_saldo_insuficiente"].fillna(0).sum()
    enc = df_med["valor_nao_devolvido_conta_encerrada"].fillna(0).sum()
    tot = insuf + enc
    pct_insuf = (insuf / tot * 100) if tot else 0.0
    sub = f"Saldo insuficiente responde por {br(pct_insuf, 1, 1.0, '%')} das perdas não devolvidas no período."
    rodape = "Obs.: A rápida dispersão para contas laranjas explica a predominância de saldo insuficiente."
    return sub, rodape
