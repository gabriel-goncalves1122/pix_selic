"""Graficos da Aba 3: Geografia & Faixa Etaria."""
import pandas as pd
import plotly.graph_objects as go

from fmt_brasil import PALETA, br, escalar_serie
from graficos.comum import aplicar_layout_padrao


def grafico_regional_pago_recebido(df: pd.DataFrame) -> go.Figure:
    """Barras agrupadas em ordem crescente comparando Volume Pago vs. Recebido por regiao."""
    ordenado = df.sort_values("vl_recebido", ascending=True).copy()
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=ordenado["regiao"],
            y=escalar_serie(ordenado["vl_pago"], 1e12),
            name="Volume Pago",
            marker_color=PALETA["azul_claro"],
            hovertemplate="Pago: R$ %{y:,.2f} tri<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=ordenado["regiao"],
            y=escalar_serie(ordenado["vl_recebido"], 1e12),
            name="Volume Recebido",
            marker_color=PALETA["azul"],
            hovertemplate="Recebido: R$ %{y:,.2f} tri<extra></extra>",
        )
    )
    aplicar_layout_padrao(fig, titulo_y="Volume (R$ Trilhões)")
    fig.update_layout(barmode="group")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" tri")
    return fig


def grafico_saldo_liquido_regional(df: pd.DataFrame) -> go.Figure:
    """Barras divergentes em ordem crescente do Saldo Liquido Interestadual em R$ Bilhoes."""
    ordenado = df.sort_values("saldo_liquido", ascending=True).copy()
    saldo_bi = escalar_serie(ordenado["saldo_liquido"], 1e9)
    cores = [PALETA["verde"] if v >= 0 else PALETA["vermelho"] for v in saldo_bi]
    rotulos = [f"R$ {br(v, 1, 1.0, ' bi')}" for v in saldo_bi]

    fig = go.Figure(
        go.Bar(
            x=ordenado["regiao"],
            y=saldo_bi,
            marker_color=cores,
            text=rotulos,
            textposition="outside",
            hovertemplate="<b>%{x}</b><br>Saldo Líquido: R$ %{y:,.1f} bi<extra></extra>",
        )
    )
    fig.add_hline(y=0, line_color=PALETA["cinza"], line_width=1)
    aplicar_layout_padrao(fig, titulo_y="Saldo Líquido (R$ Bilhões)", hovermode="closest")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" bi")
    return fig


def grafico_mapa_calor_etario(df: pd.DataFrame) -> go.Figure:
    """Mapa de calor (Heatmap) da quantidade de transacoes (Bi) por Faixa Etaria."""
    ordem = (
        df[["faixa_etaria", "ordem_etaria"]]
        .drop_duplicates()
        .sort_values("ordem_etaria")["faixa_etaria"]
        .tolist()
    )
    piv = df.pivot(index="faixa_etaria", columns="periodo_label", values="qtd_transacoes")
    piv = piv.reindex(ordem) / 1e9

    fig = go.Figure(
        go.Heatmap(
            z=piv.values,
            x=piv.columns.tolist(),
            y=piv.index.tolist(),
            colorscale="Blues",
            colorbar=dict(title="Transações (bi)"),
            hovertemplate=(
                "Período: %{x}<br>"
                "Faixa Etária: %{y}<br>"
                "Quantidade: %{z:,.2f} bi<extra></extra>"
            ),
        )
    )
    aplicar_layout_padrao(fig, titulo_y="Faixa Etária", altura=400, hovermode="closest")
    return fig
