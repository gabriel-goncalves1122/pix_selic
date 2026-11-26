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
