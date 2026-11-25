"""
Painel analitico da Camada Ouro (Streamlit + Plotly).

Como executar a partir da raiz do projeto:
    uv run streamlit run dashboard/painel.py
"""
import streamlit as st

import consultas
from fmt_brasil import (
    br,
    nota_causas_nao_devolucao,
    nota_comparativo_cartoes,
    nota_dispersao_macro,
    nota_efetividade_laranjas,
    nota_etario,
    nota_funil_med,
    nota_meios_tradicionais,
    nota_natureza_pix,
    nota_politica_monetaria,
    nota_regional_fluxo,
    nota_saldo_liquido,
    nota_share_meios,
    nota_volume_nominal_real,
    preparar_tabela_cartoes,
    preparar_tabela_macro,
    preparar_tabela_regional,
)
from graficos import (
    grafico_causas_nao_devolucao,
    grafico_comparativo_cartoes_volume,
    grafico_dispersao_macro,
    grafico_efetividade_vs_laranjas,
    grafico_funil_med,
    grafico_mapa_calor_etario,
    grafico_meios_tradicionais,
    grafico_natureza_pix,
    grafico_politica_monetaria,
    grafico_regional_pago_recebido,
    grafico_saldo_liquido_regional,
    grafico_share_meios_empilhado,
    grafico_volume_nominal_vs_real,
)

st.set_page_config(
    page_title="Pix, Cartoes & Macroeconomia (ECOX14)",
    page_icon="📊",
    layout="wide",
)


def _exibir_grafico(titulo: str, fig, notas: tuple[str, str]) -> None:
    """Renderiza titulo, subtitulo discreto (resposta), grafico e observacao de rodape."""
    subtitulo, rodape = notas
    st.subheader(titulo)
    st.caption(subtitulo)
    st.plotly_chart(fig, width="stretch")
    if rodape:
        st.caption(rodape)


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
    col1, col2 = st.columns(2)
    with col1:
        _exibir_grafico(
            "Volume Pix: Nominal vs. Real Deflacionado (IPCA)",
            grafico_volume_nominal_vs_real(dados),
            nota_volume_nominal_real(dados),
        )
    with col2:
        _exibir_grafico(
            "Política Monetária: Selic, IPCA 12m e Juro Real (%)",
            grafico_politica_monetaria(dados),
            nota_politica_monetaria(dados),
        )

    _exibir_grafico(
        "Relação Macro: Juro Real (%) vs. Volume Real do Pix (R$ Tri)",
        grafico_dispersao_macro(dados),
        nota_dispersao_macro(dados),
    )

    st.subheader(f"Série Mensal Consolidada ({ano_inicio} a {ano_fim})")
    st.dataframe(preparar_tabela_macro(dados), hide_index=True, width="stretch")

with tab_meios:
    cartoes_df = consultas.cartoes_vs_pix_trimestral(ano_inicio, ano_fim)
    if not cartoes_df.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            _exibir_grafico(
                "Share de Quantidade (%): Pix vs. Cartões (Trimestral)",
                grafico_share_meios_empilhado(cartoes_df),
                nota_share_meios(cartoes_df),
            )
        with col_c2:
            ultimo_t = cartoes_df["ano_trimestre"].iloc[-1]
            df_ultimo = cartoes_df[cartoes_df["ano_trimestre"] == ultimo_t]
            _exibir_grafico(
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
        _exibir_grafico(
            "Volume Pix por Natureza Econômica (P2P, P2B, B2B, B2P)",
            grafico_natureza_pix(nat_df),
            nota_natureza_pix(nat_df),
        )

with tab_geo:
    reg_df = consultas.fluxo_regional(ano_inicio, ano_fim)
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        _exibir_grafico(
            "Volume Pago vs. Recebido por Região (R$ Tri)",
            grafico_regional_pago_recebido(reg_df),
            nota_regional_fluxo(reg_df),
        )
    with col_g2:
        _exibir_grafico(
            "Saldo Líquido Interestadual (Recebido - Pago)",
            grafico_saldo_liquido_regional(reg_df),
            nota_saldo_liquido(reg_df),
        )

    st.subheader("Detalhamento Regional (Pago vs. Recebido)")
    st.dataframe(preparar_tabela_regional(reg_df), hide_index=True, width="stretch")

    st.divider()
    idade_df = consultas.adocao_etaria_serie(ano_inicio, ano_fim)
    if not idade_df.empty:
        _exibir_grafico(
            "Adoção Geracional: Transações por Faixa Etária (Bilhões)",
            grafico_mapa_calor_etario(idade_df),
            nota_etario(idade_df),
        )

with tab_med:
    med_df = dados.dropna(subset=["qtd_pix_contestados"])
    if med_df.empty:
        st.info("Não há registros do MED (criado em 2022) para o período selecionado.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            _exibir_grafico(
                "Funil Financeiro MED Agregado (R$ Milhões)",
                grafico_funil_med(med_df),
                nota_funil_med(med_df),
            )
        with col_f2:
            _exibir_grafico(
                "Efetividade do MED (%) vs. Chaves/Usuário (Laranjas)",
                grafico_efetividade_vs_laranjas(med_df),
                nota_efetividade_laranjas(med_df),
            )

        _exibir_grafico(
            "Causas de Não Devolução no MED (R$ Milhões)",
            grafico_causas_nao_devolucao(med_df),
            nota_causas_nao_devolucao(med_df),
        )

st.caption(
    f"Fonte: Banco Central do Brasil (APIs Olinda Pix_DadosAbertos, MPV_DadosAbertos e SGS Séries 432/433/11). "
    f"{len(dados)} meses exibidos. Dado tratado, modelado em dbt e validado por testes automatizados."
)
