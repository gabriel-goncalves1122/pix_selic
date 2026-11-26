"""Graficos da Aba 1: Macroeconomia & Juro Real."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from fmt_brasil import PALETA, escalar_serie
from graficos.comum import aplicar_layout_padrao


def grafico_volume_nominal_vs_real(df: pd.DataFrame) -> go.Figure:
    """Volume Pix Nominal vs. Real Deflacionado (R$ Tri) com destaque da erosao inflacionaria."""
    nominal_tri = escalar_serie(df["vl_transacoes_total"], 1e12)
    real_tri = escalar_serie(df["vl_pix_real_deflacionado"], 1e12)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["periodo_label"],
            y=nominal_tri,
            name="Volume Nominal",
            mode="lines",
            line=dict(color=PALETA["azul"], width=2.5),
            hovertemplate="Nominal: R$ %{y:,.2f} tri<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["periodo_label"],
            y=real_tri,
            name="Volume Real (IPCA)",
            mode="lines",
            fill="tonexty",
            fillcolor="rgba(217, 111, 44, 0.15)",
            line=dict(color=PALETA["laranja"], width=2.5),
            hovertemplate="Real (IPCA): R$ %{y:,.2f} tri<extra></extra>",
        )
    )
    aplicar_layout_padrao(fig, titulo_y="Volume (R$ Trilhões)")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" tri")
    return fig


def grafico_politica_monetaria(df: pd.DataFrame) -> go.Figure:
    """Juro Real em barras (positivo/negativo) combinado com linhas de Selic e IPCA 12m."""
    juro_real = df["juro_real_ex_post_pct"].fillna(0)
    cores_juro = [PALETA["verde"] if v >= 0 else PALETA["vermelho"] for v in juro_real]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df["periodo_label"],
            y=df["juro_real_ex_post_pct"],
            name="Juro Real Ex-Post",
            marker_color=cores_juro,
            opacity=0.55,
            hovertemplate="Juro Real: %{y:,.2f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["periodo_label"],
            y=df["selic_meta_fim_mes"],
            name="Selic Meta",
            mode="lines",
            line=dict(color=PALETA["azul"], width=2.5),
            hovertemplate="Selic Meta: %{y:,.2f}%<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df["periodo_label"],
            y=df["ipca_acumulado_12m_pct"],
            name="IPCA 12m",
            mode="lines",
            line=dict(color=PALETA["laranja"], width=2.5, dash="dot"),
            hovertemplate="IPCA 12m: %{y:,.2f}%<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_dash="dash", line_color=PALETA["cinza"], line_width=1)
    aplicar_layout_padrao(fig, titulo_y="Taxa (% a.a.)")
    fig.update_yaxes(ticksuffix="%")
    return fig


def grafico_dispersao_macro(df: pd.DataFrame) -> go.Figure:
    """Dispersao entre Juro Real (%) e Volume Real do Pix (R$ Tri), colorido por Ano."""
    base = df.dropna(subset=["juro_real_ex_post_pct", "vl_pix_real_deflacionado", "ticket_medio_pix"]).copy()
    base["volume_real_tri"] = escalar_serie(base["vl_pix_real_deflacionado"], 1e12)
    base["ano_str"] = base["ano"].astype(str)

    fig = px.scatter(
        base,
        x="juro_real_ex_post_pct",
        y="volume_real_tri",
        color="ano_str",
        size="ticket_medio_pix",
        hover_name="periodo_label",
        custom_data=["ticket_medio_pix"],
        labels={
            "juro_real_ex_post_pct": "Juro Real Ex-Post (% a.a.)",
            "volume_real_tri": "Volume Real Pix (R$ Tri)",
            "ano_str": "Ano",
        },
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{hovertext}</b><br>"
            "Juro Real: %{x:,.2f}%<br>"
            "Volume Real: R$ %{y:,.2f} tri<br>"
            "Ticket Médio: R$ %{customdata[0]:,.2f}<extra></extra>"
        )
    )
    aplicar_layout_padrao(fig, titulo_y="Volume Real (R$ Trilhões)", hovermode="closest")
    fig.update_xaxes(title_text="Juro Real Ex-Post (% a.a.)", ticksuffix="%")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" tri")
    return fig
