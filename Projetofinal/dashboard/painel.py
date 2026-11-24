"""
Painel analitico da Camada Ouro (Streamlit).

Como executar a partir da raiz do projeto:
    uv run streamlit run dashboard/painel.py
"""
import streamlit as st

import consultas

st.set_page_config(
    page_title="Pix, Cartoes & Macroeconomia (ECOX14)",
    page_icon="📊",
    layout="wide",
)


def br(valor, casas=1, escala=1.0, sufixo=""):
    """Formata numeros no padrao brasileiro, tratando None e NaN com seguranca."""
    if valor is None or valor != valor:  # None ou NaN
        return "sem dado"
    texto = f"{(valor / escala):,.{casas}f}"
    return texto.replace(",", "@").replace(".", ",").replace("@", ".") + sufixo


st.title("Ecossistema Pix vs. Meios Tradicionais, Macroeconomia e Seguranca")
st.caption("Camada Ouro (DuckDB + dbt) — Projeto Final ECOX14 (UNIFEI)")

if not consultas.banco_existe():
    st.error(
        "Banco Ouro nao encontrado.\n\n"
        "Rode o pipeline antes:  `uv run python src/pipeline.py`"
    )
    st.stop()

anos_df = consultas.anos()
if anos_df.empty:
    st.warning("Nenhum dado disponivel na camada Ouro.")
    st.stop()

lista_anos = anos_df["ano"].tolist()

with st.sidebar:
    st.header("Filtros")
    ano_inicio = st.selectbox("Ano inicial", lista_anos, index=0)
    ano_fim = st.selectbox("Ano final", lista_anos, index=len(lista_anos) - 1)
    st.divider()
    st.caption(
        "Consultas parametrizadas em modo somente leitura (read_only=True) "
        "sobre o DuckDB modelado no dbt."
    )

if ano_inicio > ano_fim:
    st.warning("O ano inicial nao pode ser maior que o ano final.")
    st.stop()

dados = consultas.serie_pix_macro(ano_inicio, ano_fim)
if dados.empty:
    st.warning("Nenhum registro encontrado para o periodo selecionado.")
    st.stop()

resumo = consultas.resumo_periodo(ano_inicio, ano_fim).iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Transacoes Pix", br(resumo["total_transacoes"], 1, 1e9, " bi"))
c2.metric("Volume Financeiro Pix", "R$ " + br(resumo["total_valor"], 2, 1e12, " tri"))
c3.metric("Selic Meta Media", br(resumo["selic_media"], 2, 1.0, "% a.a."))
c4.metric("Juro Real Medio", br(resumo["juro_real_medio"], 2, 1.0, "% a.a."))
perda_med = br(resumo["custo_fraude_total"], 2, 1e9, " bi")
c5.metric("Perda MED (Nao Devolvido)", ("R$ " + perda_med) if perda_med != "sem dado" else "sem dado")

st.divider()

tab_macro, tab_meios, tab_geo, tab_med = st.tabs([
    "1. Macro & Juro Real",
    "2. Pix vs. Cartoes & Tradicionais",
    "3. Geografia & Faixa Etaria",
    "4. Seguranca & Funil MED",
])

with tab_macro:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Volume Pix: Nominal vs. Real Deflacionado (IPCA)")
        st.line_chart(
            dados,
            x="periodo_label",
            y=["vl_transacoes_total", "vl_pix_real_deflacionado"],
        )
    with col2:
        st.subheader("Politica Monetaria: Selic, IPCA 12m e Juro Real (%)")
        st.line_chart(
            dados,
            x="periodo_label",
            y=["selic_meta_fim_mes", "ipca_acumulado_12m_pct", "juro_real_ex_post_pct"],
        )

    st.subheader(f"Serie Mensal Consolidada ({ano_inicio} a {ano_fim})")
    st.dataframe(
        dados[[
            "periodo_label", "qtd_transacoes_total", "vl_transacoes_total",
            "vl_pix_real_deflacionado", "ticket_medio_pix", "pct_valor_pj",
            "selic_meta_fim_mes", "ipca_acumulado_12m_pct", "juro_real_ex_post_pct",
        ]],
        hide_index=True,
        width="stretch",
        column_config={
            "periodo_label": st.column_config.TextColumn("Periodo"),
            "qtd_transacoes_total": st.column_config.NumberColumn("Qtd. Pix", format="%d"),
            "vl_transacoes_total": st.column_config.NumberColumn("Volume Nominal (R$)", format="%.0f"),
            "vl_pix_real_deflacionado": st.column_config.NumberColumn("Volume Real (R$)", format="%.0f"),
            "ticket_medio_pix": st.column_config.NumberColumn("Ticket Medio (R$)", format="%.2f"),
            "pct_valor_pj": st.column_config.ProgressColumn("% Valor PJ", format="%.1f%%", min_value=0, max_value=100),
            "selic_meta_fim_mes": st.column_config.NumberColumn("Selic (%)", format="%.2f%%"),
            "ipca_acumulado_12m_pct": st.column_config.NumberColumn("IPCA 12m (%)", format="%.2f%%"),
            "juro_real_ex_post_pct": st.column_config.NumberColumn("Juro Real (%)", format="%.2f%%"),
        },
    )

with tab_meios:
    cartoes_df = consultas.cartoes_vs_pix_trimestral(ano_inicio, ano_fim)
    if not cartoes_df.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            st.subheader("Share de Quantidade (%): Pix vs. Cartoes (Trimestral)")
            piv_qtd = cartoes_df.pivot(index="ano_trimestre", columns="meio_pagamento", values="share_qtd_pct")
            st.line_chart(piv_qtd)
        with col_c2:
            st.subheader("Volume Financeiro Trimestral (R$): Pix vs. Cartoes")
            piv_vl = cartoes_df.pivot(index="ano_trimestre", columns="meio_pagamento", values="vl_transacoes")
            st.line_chart(piv_vl)

        st.subheader("Ticket Medio por Meio de Pagamento (Ultimo Trimestre da Selecao)")
        ultimo_t = cartoes_df["ano_trimestre"].iloc[-1]
        st.dataframe(
            cartoes_df[cartoes_df["ano_trimestre"] == ultimo_t],
            hide_index=True,
            width="stretch",
        )

    st.divider()
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.subheader("Meios Tradicionais Mensais (R$): TED vs. Boleto vs. Cheque vs. DOC")
        st.line_chart(dados, x="periodo_label", y=["vl_ted", "vl_boleto", "vl_cheque", "vl_doc"])
    with col_m2:
        st.subheader("Volume Pix por Natureza Economica (P2P, P2B, B2B, B2P)")
        nat_df = consultas.volume_por_natureza(ano_inicio, ano_fim)
        st.bar_chart(nat_df.head(8), x="natureza", y="vl_transacoes", color="#D96F2C")

with tab_geo:
    reg_df = consultas.fluxo_regional(ano_inicio, ano_fim)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Volume Financeiro Recebido por Regiao (R$)")
        st.bar_chart(reg_df, x="regiao", y="vl_recebido", color="#1B3A5F")
    with col_g2:
        st.subheader("Saldo Liquido Interestadual (Recebido - Pago, R$)")
        st.bar_chart(reg_df, x="regiao", y="saldo_liquido", color="#2E8B57")

    st.subheader("Detalhamento Regional (Pago vs. Recebido)")
    st.dataframe(reg_df, hide_index=True, width="stretch")

    st.divider()
    idade_df = consultas.adocao_etaria_serie(ano_inicio, ano_fim)
    if not idade_df.empty:
        st.subheader("Adocao Geracional: Quantidade de Transacoes por Faixa Etaria")
        piv_idade = idade_df.pivot(index="periodo_label", columns="faixa_etaria", values="qtd_transacoes")
        st.line_chart(piv_idade)

with tab_med:
    med_df = dados.dropna(subset=["qtd_pix_contestados"])
    if med_df.empty:
        st.info("Nao ha registros do MED (criado em 2022) para o periodo selecionado.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.subheader("Funil Financeiro MED: Aceito vs. Devolvido vs. Perda (R$)")
            st.line_chart(
                med_df,
                x="periodo_label",
                y=["valor_pix_contestados_aceitos", "valor_devolvido_integral_med", "custo_fraude_nao_devolvido"],
            )
        with col_f2:
            st.subheader("Efetividade do MED (%) vs. Razao Chaves/Usuario (Laranjas)")
            st.line_chart(
                med_df,
                x="periodo_label",
                y=["taxa_efetividade_med_pct", "razao_chaves_usuario_fraude"],
            )

        st.subheader("Causas de Nao Devolucao no MED (R$)")
        st.bar_chart(
            med_df,
            x="periodo_label",
            y=["valor_nao_devolvido_saldo_insuficiente", "valor_nao_devolvido_conta_encerrada"],
        )

st.caption(
    f"Fonte: Banco Central do Brasil (APIs Olinda Pix_DadosAbertos, MPV_DadosAbertos e SGS Series 432/433/11). "
    f"{len(dados)} meses exibidos. Dado tratado, modelado em dbt e validado por 37 testes."
)
