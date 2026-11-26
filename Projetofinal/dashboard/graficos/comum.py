"""Utilitario de layout padrao para todos os graficos Plotly do dashboard."""
import plotly.graph_objects as go


def aplicar_layout_padrao(
    fig: go.Figure,
    titulo_y: str = "",
    altura: int = 380,
    hovermode: str = "x unified",
) -> go.Figure:
    """Aplica tema limpo, separadores pt-BR (',.') e legenda horizontal padronizada."""
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
