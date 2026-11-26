"""Aba 1: Macro & Juro Real."""
import streamlit as st

from abas.comum import exibir_grafico
from fmt_brasil import preparar_tabela_macro
from graficos.macro import (
    grafico_dispersao_macro,
    grafico_politica_monetaria,
    grafico_volume_nominal_vs_real,
)
from notas import (
    nota_dispersao_macro,
    nota_politica_monetaria,
    nota_volume_nominal_real,
)


def renderizar_aba_macro(dados, ano_inicio: int, ano_fim: int) -> None:
    """Renderiza os graficos e a tabela consolidada da Aba 1."""
    col1, col2 = st.columns(2)
    with col1:
        exibir_grafico(
            "Volume Pix: Nominal vs. Real Deflacionado (IPCA)",
            grafico_volume_nominal_vs_real(dados),
            nota_volume_nominal_real(dados),
        )
    with col2:
        exibir_grafico(
            "Política Monetária: Selic, IPCA 12m e Juro Real (%)",
            grafico_politica_monetaria(dados),
            nota_politica_monetaria(dados),
        )

    exibir_grafico(
        "Relação Macro: Juro Real (%) vs. Volume Real do Pix (R$ Tri)",
        grafico_dispersao_macro(dados),
        nota_dispersao_macro(dados),
    )

    st.subheader(f"Série Mensal Consolidada ({ano_inicio} a {ano_fim})")
    st.dataframe(preparar_tabela_macro(dados), hide_index=True, width="stretch")
