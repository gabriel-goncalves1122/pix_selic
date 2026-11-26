"""Aba 3: Geografia & Faixa Etaria."""
import streamlit as st

import consultas
from abas.comum import exibir_grafico
from fmt_brasil import preparar_tabela_regional
from graficos.geo import (
    grafico_mapa_calor_etario,
    grafico_regional_pago_recebido,
    grafico_saldo_liquido_regional,
)
from notas import nota_etario, nota_regional_fluxo, nota_saldo_liquido


def renderizar_aba_geo(ano_inicio: int, ano_fim: int) -> None:
    """Renderiza os graficos regionais e o mapa de calor etario."""
    reg_df = consultas.fluxo_regional(ano_inicio, ano_fim)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        exibir_grafico(
            "Volume Pago vs. Recebido por Região (R$ Tri)",
            grafico_regional_pago_recebido(reg_df),
            nota_regional_fluxo(reg_df),
        )
    with col_g2:
        exibir_grafico(
            "Saldo Líquido Interestadual (Recebido - Pago)",
            grafico_saldo_liquido_regional(reg_df),
            nota_saldo_liquido(reg_df),
        )

    st.subheader("Detalhamento Regional (Pago vs. Recebido)")
    st.dataframe(preparar_tabela_regional(reg_df), hide_index=True, width="stretch")

    st.divider()
    idade_df = consultas.adocao_etaria_serie(ano_inicio, ano_fim)
    if not idade_df.empty:
        exibir_grafico(
            "Adoção Geracional: Transações por Faixa Etária (Bilhões)",
            grafico_mapa_calor_etario(idade_df),
            nota_etario(idade_df),
        )
