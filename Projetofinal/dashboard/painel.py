"""
Painel analitico da Camada Ouro (Streamlit + Plotly).

Como executar a partir da raiz do projeto:
    uv run streamlit run dashboard/painel.py
"""
import streamlit as st

import consultas
from abas import (
    renderizar_aba_geo,
    renderizar_aba_macro,
    renderizar_aba_med,
    renderizar_aba_meios,
)
from fmt_brasil import br

st.set_page_config(
    page_title="Pix, Cartoes & Macroeconomia (ECOX14)",
    page_icon="📊",
    layout="wide",
)

st.title("Ecossistema Pix vs. Meios Tradicionais, Macroeconomia e Segurança")
st.caption("Camada Ouro (DuckDB + dbt) — Projeto Final ECOX14 (UNIFEI)")

if not consultas.banco_existe():
    st.error(
        "Banco Ouro não encontrado.\n\n"
        "Rode o pipeline antes:  `uv run python src/pipeline.py`"
    )
    st.stop()

anos_df = consultas.anos()
if anos_df.empty:
    st.warning("Nenhum dado disponível na camada Ouro.")
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
    st.warning("O ano inicial não pode ser maior que o ano final.")
    st.stop()

dados = consultas.serie_pix_macro(ano_inicio, ano_fim)
if dados.empty:
    st.warning("Nenhum registro encontrado para o período selecionado.")
    st.stop()

resumo = consultas.resumo_periodo(ano_inicio, ano_fim).iloc[0]

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Transações Pix", br(resumo["total_transacoes"], 1, 1e9, " bi"))
c2.metric("Volume Financeiro Pix", "R$ " + br(resumo["total_valor"], 2, 1e12, " tri"))
c3.metric("Selic Meta Média", br(resumo["selic_media"], 2, 1.0, "% a.a."))
c4.metric("Juro Real Médio", br(resumo["juro_real_medio"], 2, 1.0, "% a.a."))
perda_med = br(resumo["custo_fraude_total"], 2, 1e9, " bi")
c5.metric("Perda MED (Não Devolvido)", ("R$ " + perda_med) if perda_med != "sem dado" else "sem dado")

st.divider()

tab_macro, tab_meios, tab_geo, tab_med = st.tabs([
    "1. Macro & Juro Real",
    "2. Pix vs. Cartões & Tradicionais",
    "3. Geografia & Faixa Etária",
    "4. Segurança & Funil MED",
])

with tab_macro:
    renderizar_aba_macro(dados, ano_inicio, ano_fim)

with tab_meios:
    renderizar_aba_meios(dados, ano_inicio, ano_fim)

with tab_geo:
    renderizar_aba_geo(ano_inicio, ano_fim)

with tab_med:
    renderizar_aba_med(dados)

st.caption(
    f"Fonte: Banco Central do Brasil (APIs Olinda Pix_DadosAbertos, MPV_DadosAbertos e SGS Séries 432/433/11). "
    f"{len(dados)} meses exibidos. Dado tratado, modelado em dbt e validado por testes automatizados."
)
