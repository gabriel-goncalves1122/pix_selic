"""Graficos da Aba 4: Seguranca & Funil MED."""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fmt_brasil import PALETA, br, escalar_serie
from graficos.comum import aplicar_layout_padrao


def grafico_funil_med(df_med: pd.DataFrame) -> go.Figure:
    """Funil financeiro agregado do MED (Contestado Aceito -> Devolvido -> Perda)."""
    aceito = df_med["valor_pix_contestados_aceitos"].sum() / 1e6
    devolvido = (
        df_med["valor_devolvido_integral_med"].fillna(0).sum()
        + df_med["valor_devolvido_parcial_med"].fillna(0).sum()
    ) / 1e6
    perda = df_med["custo_fraude_nao_devolvido"].sum() / 1e6

    etapas = ["Contestado Aceito", "Devolvido (Integral + Parcial)", "Perda Não Devolvida"]
    valores = [aceito, devolvido, perda]
    textos = [f"R$ {br(v, 1, 1.0, ' mi')}" for v in valores]

    fig = go.Figure(
        go.Funnel(
            y=etapas,
            x=valores,
            text=textos,
            textinfo="text+percent initial",
            marker=dict(color=[PALETA["azul"], PALETA["verde"], PALETA["vermelho"]]),
            hovertemplate="<b>%{y}</b><br>Valor: R$ %{x:,.1f} mi<extra></extra>",
        )
    )
    aplicar_layout_padrao(fig, titulo_y="", hovermode="closest")
    return fig


def grafico_efetividade_vs_laranjas(df_med: pd.DataFrame) -> go.Figure:
    """Eixo duplo: Efetividade do MED (%) vs. Razao Chaves/Usuario em Fraude."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(
            x=df_med["periodo_label"],
            y=df_med["taxa_efetividade_med_pct"],
            name="Efetividade MED (%)",
            mode="lines+markers",
            line=dict(color=PALETA["verde"], width=2.5),
            hovertemplate="Efetividade MED: %{y:,.2f}%<extra></extra>",
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=df_med["periodo_label"],
            y=df_med["razao_chaves_usuario_fraude"],
            name="Razão Chaves/Usuário (Laranjas)",
            mode="lines",
            line=dict(color=PALETA["laranja"], width=2.2, dash="dash"),
            hovertemplate="Chaves/Usuário: %{y:,.2f}x<extra></extra>",
        ),
        secondary_y=True,
    )
    aplicar_layout_padrao(fig)
    fig.update_yaxes(title_text="Efetividade MED (%)", ticksuffix="%", secondary_y=False)
    fig.update_yaxes(title_text="Chaves por Usuário", ticksuffix="x", secondary_y=True)
    return fig


def grafico_causas_nao_devolucao(df_med: pd.DataFrame) -> go.Figure:
    """Barras empilhadas das causas de nao devolucao no MED em R$ Milhoes."""
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=df_med["periodo_label"],
            y=escalar_serie(df_med["valor_nao_devolvido_saldo_insuficiente"], 1e6),
            name="Saldo Insuficiente",
            marker_color=PALETA["vermelho"],
            hovertemplate="Saldo Insuficiente: R$ %{y:,.1f} mi<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=df_med["periodo_label"],
            y=escalar_serie(df_med["valor_nao_devolvido_conta_encerrada"], 1e6),
            name="Conta Encerrada",
            marker_color=PALETA["dourado"],
            hovertemplate="Conta Encerrada: R$ %{y:,.1f} mi<extra></extra>",
        )
    )
    aplicar_layout_padrao(fig, titulo_y="Valor (R$ Milhões)")
    fig.update_layout(barmode="stack")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" mi")
    return fig
