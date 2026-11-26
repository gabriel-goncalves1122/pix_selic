"""Aba 2: Pix vs. Cartoes & Meios Tradicionais."""
import streamlit as st

import consultas
from abas.comum import exibir_grafico
from fmt_brasil import preparar_tabela_cartoes
from graficos.meios import (
    grafico_comparativo_cartoes_volume,
    grafico_meios_tradicionais,
    grafico_natureza_pix,
    grafico_share_meios_empilhado,
)
from notas import (
    nota_comparativo_cartoes,
    nota_meios_tradicionais,
    nota_natureza_pix,
    nota_share_meios,
)


def renderizar_aba_meios(dados, ano_inicio: int, ano_fim: int) -> None:
    """Renderiza os graficos comparativos entre Pix, Cartoes e Meios Tradicionais."""
    cartoes_df = consultas.cartoes_vs_pix_trimestral(ano_inicio, ano_fim)
    if not cartoes_df.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            exibir_grafico(
                "Share de Quantidade (%): Pix vs. Cartões (Trimestral)",
                grafico_share_meios_empilhado(cartoes_df),
                nota_share_meios(cartoes_df),
            )
        with col_c2:
            ultimo_t = cartoes_df["ano_trimestre"].iloc[-1]
            df_ultimo = cartoes_df[cartoes_df["ano_trimestre"] == ultimo_t]
            exibir_grafico(
                f"Volume e Ticket Médio ({ultimo_t})",
                grafico_comparativo_cartoes_volume(df_ultimo),
                nota_comparativo_cartoes(df_ultimo),
            )

        st.subheader(f"Detalhamento por Meio de Pagamento ({ultimo_t})")
        st.dataframe(preparar_tabela_cartoes(df_ultimo), hide_index=True, width="stretch")

    st.divider()
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        sub_trad, rod_trad = nota_meios_tradicionais(dados)
        st.subheader("Meios Tradicionais Mensais: TED, Boleto, Cheque e DOC")
        st.caption(sub_trad)
        escala_log = st.toggle(
            "Usar escala logarítmica (evidencia Cheque e DOC)",
            value=True,
            key="toggle_log_tradicionais",
        )
        st.plotly_chart(grafico_meios_tradicionais(dados, escala_log=escala_log), width="stretch")
        st.caption(rod_trad)
    with col_m2:
        nat_df = consultas.volume_por_natureza(ano_inicio, ano_fim)
        exibir_grafico(
            "Volume Pix por Natureza Econômica (P2P, P2B, B2B, B2P)",
            grafico_natureza_pix(nat_df),
            nota_natureza_pix(nat_df),
        )
