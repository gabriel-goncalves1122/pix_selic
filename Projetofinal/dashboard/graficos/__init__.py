"""Pacote de construtores de graficos Plotly organizados por dominio."""
from graficos.geo import (
    grafico_mapa_calor_etario,
    grafico_regional_pago_recebido,
    grafico_saldo_liquido_regional,
)
from graficos.macro import (
    grafico_dispersao_macro,
    grafico_politica_monetaria,
    grafico_volume_nominal_vs_real,
)
from graficos.med import (
    grafico_causas_nao_devolucao,
    grafico_efetividade_vs_laranjas,
    grafico_funil_med,
)
from graficos.meios import (
    grafico_comparativo_cartoes_volume,
    grafico_meios_tradicionais,
    grafico_natureza_pix,
    grafico_share_meios_empilhado,
)

__all__ = [
    "grafico_causas_nao_devolucao",
    "grafico_comparativo_cartoes_volume",
    "grafico_dispersao_macro",
    "grafico_efetividade_vs_laranjas",
    "grafico_funil_med",
    "grafico_mapa_calor_etario",
    "grafico_meios_tradicionais",
    "grafico_natureza_pix",
    "grafico_politica_monetaria",
    "grafico_regional_pago_recebido",
    "grafico_saldo_liquido_regional",
    "grafico_share_meios_empilhado",
    "grafico_volume_nominal_vs_real",
]
