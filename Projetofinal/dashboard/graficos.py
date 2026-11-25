"""
Construtores puros de graficos interativos (Plotly) para o dashboard da Camada Ouro.
Todos os graficos utilizam separadores brasileiros (',.') e tooltips formatados em pt-BR.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from fmt_brasil import PALETA, br, escalar_serie


def _aplicar_layout_padrao(
    fig: go.Figure,
    titulo_y: str = "",
    altura: int = 380,
    hovermode: str = "x unified",
) -> go.Figure:
    """Aplica tema limpo, separadores pt-BR e legenda horizontal padronizada."""
    fig.update_layout(
        template="plotly_white",
        separators=",.",
        height=altura,
        hovermode=hovermode,
        margin=dict(l=20, r=20, t=35, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            title_text="",
        ),
        yaxis_title=titulo_y,
        xaxis_title="",
    )
    return fig


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
    _aplicar_layout_padrao(fig, titulo_y="Volume (R$ Trilhões)")
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
    _aplicar_layout_padrao(fig, titulo_y="Taxa (% a.a.)")
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
    _aplicar_layout_padrao(fig, titulo_y="Volume Real (R$ Trilhões)", hovermode="closest")
    fig.update_xaxes(title_text="Juro Real Ex-Post (% a.a.)", ticksuffix="%")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" tri")
    return fig


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
    _aplicar_layout_padrao(fig, titulo_y="Participação (%)")
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
    _aplicar_layout_padrao(fig, titulo_y="", hovermode="closest")
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

    _aplicar_layout_padrao(fig, titulo_y="Volume (R$ Bilhões)")
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
    _aplicar_layout_padrao(fig, titulo_y="", hovermode="closest")
    fig.update_xaxes(title_text="Volume (R$ Trilhões)", tickprefix="R$ ", ticksuffix=" tri")
    return fig


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
    _aplicar_layout_padrao(fig, titulo_y="Volume (R$ Trilhões)")
    fig.update_layout(barmode="group")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" tri")
    return fig


def grafico_saldo_liquido_regional(df: pd.DataFrame) -> go.Figure:
    """Barras divergentes em ordem crescente do Saldo Liquido Interestadual (Recebido - Pago) em R$ Bilhoes."""
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
    _aplicar_layout_padrao(fig, titulo_y="Saldo Líquido (R$ Bilhões)", hovermode="closest")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" bi")
    return fig


def grafico_mapa_calor_etario(df: pd.DataFrame) -> go.Figure:
    """Mapa de calor (Heatmap) da quantidade de transacoes (Bi) por Faixa Etaria ao longo do tempo."""
    ordem = (
        df[["faixa_etaria", "ordem_etaria"]]
        .drop_duplicates()
        .sort_values("ordem_etaria")["faixa_etaria"]
        .tolist()
    )
    piv = df.pivot(index="faixa_etaria", columns="periodo_label", values="qtd_transacoes")
    piv = piv.reindex(ordem) / 1e9  # em bilhoes

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
    _aplicar_layout_padrao(fig, titulo_y="Faixa Etária", altura=400, hovermode="closest")
    return fig


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
    _aplicar_layout_padrao(fig, titulo_y="", hovermode="closest")
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
    _aplicar_layout_padrao(fig)
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
    _aplicar_layout_padrao(fig, titulo_y="Valor (R$ Milhões)")
    fig.update_layout(barmode="stack")
    fig.update_yaxes(tickprefix="R$ ", ticksuffix=" mi")
    return fig
