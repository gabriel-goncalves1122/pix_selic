"""Aba 4: Seguranca & Funil MED."""
import streamlit as st

from abas.comum import exibir_grafico
from graficos.med import (
    grafico_causas_nao_devolucao,
    grafico_efetividade_vs_laranjas,
    grafico_funil_med,
)
from notas import (
    nota_causas_nao_devolucao,
    nota_efetividade_laranjas,
    nota_funil_med,
)


def renderizar_aba_med(dados) -> None:
    """Renderiza os graficos de seguranca e efetividade do MED."""
    med_df = dados.dropna(subset=["qtd_pix_contestados"])
    if med_df.empty:
        st.info("Não há registros do MED (criado em 2022) para o período selecionado.")
        return

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        exibir_grafico(
            "Funil Financeiro MED Agregado (R$ Milhões)",
            grafico_funil_med(med_df),
            nota_funil_med(med_df),
        )
    with col_f2:
        exibir_grafico(
            "Efetividade do MED (%) vs. Chaves/Usuário (Laranjas)",
            grafico_efetividade_vs_laranjas(med_df),
            nota_efetividade_laranjas(med_df),
        )

    exibir_grafico(
        "Causas de Não Devolução no MED (R$ Milhões)",
        grafico_causas_nao_devolucao(med_df),
        nota_causas_nao_devolucao(med_df),
    )
