"""Graficos da Aba 2: Pix vs. Cartoes & Meios Tradicionais."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from fmt_brasil import PALETA, br, escalar_serie
from graficos.comum import aplicar_layout_padrao


def grafico_share_meios_empilhado(df: pd.DataFrame) -> go.Figure:
    """Area empilhada 100% da participacao de quantidade entre Pix e Cartoes (Pix na base)."""
    fig = px.area(
        df,
        x="ano_trimestre",
        y="share_qtd_pct",
        color="meio_pagamento",
        category_orders={"meio_pagamento": ["Pix", "Débito", "Crédito", "Pré-Pago"]},
        color_discrete_map={
            "Pix": PALETA["azul"],
            "Débito": PALETA["verde"],
            "Crédito": PALETA["laranja"],
            "Pré-Pago": PALETA["roxo"],
        },
    )
    fig.update_traces(hovertemplate="%{fullData.name}: %{y:,.1f}%<extra></extra>")
    aplicar_layout_padrao(fig, titulo_y="Participação (%)")
    fig.update_yaxes(range=[0, 100], ticksuffix="%")
    return fig


def grafico_comparativo_cartoes_volume(df_ultimo: pd.DataFrame) -> go.Figure:
    """Barras horizontais do ultimo trimestre comparando Volume (R$ Tri) e Ticket Medio."""
    ordenado = df_ultimo.sort_values("vl_transacoes", ascending=True).copy()
    ordenado["vl_tri"] = escalar_serie(ordenado["vl_transacoes"], 1e12)
    ordenado["rotulo"] = [
        f"R$ {br(v, 2, 1.0, ' tri')}  |  Ticket: R$ {br(t, 2)}"
        for v, t in zip(ordenado["vl_tri"], ordenado["ticket_medio"])
    ]

    fig = go.Figure(
        go.Bar(
            x=ordenado["vl_tri"],
            y=ordenado["meio_pagamento"],
            orientation="h",
            marker_color=PALETA["azul_claro"],
            text=ordenado["rotulo"],
            textposition="auto",
            customdata=ordenado[["ticket_medio", "share_vl_pct"]],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Volume: R$ %{x:,.2f} tri<br>"
                "Ticket Médio: R$ %{customdata[0]:,.2f}<br>"
                "Share Volume: %{customdata[1]:,.1f}%<extra></extra>"
            ),
        )
    )
    aplicar_layout_padrao(fig, titulo_y="", hovermode="closest")
    fig.update_xaxes(title_text="Volume Financeiro (R$ Trilhões)", tickprefix="R$ ", ticksuffix=" tri")
    return fig


def grafico_meios_tradicionais(df: pd.DataFrame, escala_log: bool = True) -> go.Figure:
    """Evolucao mensal dos meios tradicionais (TED, Boleto, Cheque, DOC) em R$ Bilhoes."""
    series = [
        ("vl_ted", "TED", PALETA["azul"]),
        ("vl_boleto", "Boleto", PALETA["laranja"]),
        ("vl_cheque", "Cheque", PALETA["roxo"]),
        ("vl_doc", "DOC", PALETA["cinza"]),
    ]
    fig = go.Figure()
    for col, nome, cor in series:
        valores_bi = escalar_serie(df[col], 1e9)
        if escala_log:
            valores_bi = valores_bi.where(valores_bi > 0)
        fig.add_trace(
            go.Scatter(
                x=df["periodo_label"],
                y=valores_bi,
                name=nome,
                mode="lines",
                line=dict(color=cor, width=2.2),
                hovertemplate=f"{nome}: R$ %{{y:,.2f}} bi<extra></extra>",
            )
        )

    aplicar_layout_padrao(fig, titulo_y="Volume (R$ Bilhões)")
    fig.update_yaxes(
        type="log" if escala_log else "linear",
        tickprefix="R$ ",
        ticksuffix=" bi",
    )
    return fig


def grafico_natureza_pix(df: pd.DataFrame) -> go.Figure:
    """Barras horizontais ordenadas do volume por natureza economica do Pix."""
    top = df.head(8).sort_values("vl_transacoes", ascending=True).copy()
    total = df["vl_transacoes"].sum()
    top["vl_tri"] = escalar_serie(top["vl_transacoes"], 1e12)
    top["pct"] = (top["vl_transacoes"] / total * 100) if total else 0.0
    top["rotulo"] = [
        f"R$ {br(v, 2, 1.0, ' tri')} ({br(p, 1, 1.0, '%')})"
        for v, p in zip(top["vl_tri"], top["pct"])
    ]

    fig = go.Figure(
        go.Bar(
            x=top["vl_tri"],
            y=top["natureza"],
            orientation="h",
            marker_color=PALETA["laranja"],
            text=top["rotulo"],
            textposition="auto",
            customdata=top["pct"],
            hovertemplate=(
                "<b>%{y}</b><br>"
                "Volume: R$ %{x:,.2f} tri (%{customdata:,.1f}%)<extra></extra>"
            ),
        )
    )
    aplicar_layout_padrao(fig, titulo_y="", hovermode="closest")
    fig.update_xaxes(title_text="Volume (R$ Trilhões)", tickprefix="R$ ", ticksuffix=" tri")
    return fig
