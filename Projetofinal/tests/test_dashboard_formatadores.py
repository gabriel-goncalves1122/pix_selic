import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "dashboard"))

from fmt_brasil import (
    br,
    escalar_serie,
    formatar_coluna_br,
    preparar_tabela_cartoes,
    preparar_tabela_macro,
    preparar_tabela_regional,
)
from notas import (
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


def test_br_formata_padrao_brasileiro_e_trata_nulos():
    assert br(1234567.89, casas=2) == "1.234.567,89"
    assert br(2.5e12, casas=2, escala=1e12, sufixo=" tri") == "2,50 tri"
    assert br(-15.3, casas=1, sufixo="%") == "-15,3%"
    assert br(None) == "sem dado"
    assert br(float("nan")) == "sem dado"
    assert br(float("inf")) == "sem dado"


def test_escalar_serie_e_formatar_coluna_br():
    s = pd.Series([1e9, 2.5e9, None])
    escalada = escalar_serie(s, 1e9)
    assert escalada.iloc[0] == pytest.approx(1.0)
    assert escalada.iloc[1] == pytest.approx(2.5)
    assert pd.isna(escalada.iloc[2])

    fmt = formatar_coluna_br(s, casas=1, escala=1e9, prefixo="R$ ", sufixo=" bi")
    assert fmt.tolist() == ["R$ 1,0 bi", "R$ 2,5 bi", "sem dado"]


def test_preparar_tabelas_formatam_colunas_em_ptbr():
    df_macro = pd.DataFrame({
        "periodo_label": ["2024-01"],
        "qtd_transacoes_total": [4.5e9],
        "vl_transacoes_total": [2.0e12],
        "vl_pix_real_deflacionado": [1.8e12],
        "ticket_medio_pix": [444.44],
        "pct_valor_pj": [55.5],
        "selic_meta_fim_mes": [11.75],
        "ipca_acumulado_12m_pct": [4.51],
        "juro_real_ex_post_pct": [6.93],
    })
    tab_macro = preparar_tabela_macro(df_macro)
    assert tab_macro["Volume Nominal"].iloc[0] == "R$ 2,00 tri"
    assert tab_macro["Ticket Médio"].iloc[0] == "R$ 444,44"
    assert tab_macro["Selic Meta"].iloc[0] == "11,75%"

    df_cartoes = pd.DataFrame({
        "ano_trimestre": ["2024T1"],
        "meio_pagamento": ["Pix"],
        "qtd_transacoes": [1.2e10],
        "vl_transacoes": [5.5e12],
        "ticket_medio": [458.33],
        "share_qtd_pct": [48.2],
        "share_vl_pct": [62.7],
    })
    tab_cartoes = preparar_tabela_cartoes(df_cartoes)
    assert tab_cartoes["Volume Financeiro"].iloc[0] == "R$ 5,50 tri"
    assert tab_cartoes["Share Qtd."].iloc[0] == "48,2%"

    df_reg = pd.DataFrame({
        "regiao": ["Sudeste"],
        "vl_pago": [3.0e12],
        "vl_recebido": [3.2e12],
        "saldo_liquido": [200e9],
        "qtd_paga": [5.0e9],
    })
    tab_reg = preparar_tabela_regional(df_reg)
    assert tab_reg["Saldo Líquido"].iloc[0] == "R$ 200,0 bi"


def test_construtores_de_graficos_retornam_figuras_plotly_ptbr():
    df_macro = pd.DataFrame({
        "periodo_label": ["2024-01", "2024-02"],
        "ano": [2024, 2024],
        "vl_transacoes_total": [2.0e12, 2.2e12],
        "vl_pix_real_deflacionado": [1.8e12, 1.95e12],
        "ticket_medio_pix": [400.0, 410.0],
        "juro_real_ex_post_pct": [6.5, -0.5],
        "selic_meta_fim_mes": [11.25, 11.25],
        "ipca_acumulado_12m_pct": [4.5, 4.6],
        "vl_ted": [3.0e12, 3.1e12],
        "vl_boleto": [5.0e11, 5.1e11],
        "vl_cheque": [4.0e10, 3.8e10],
        "vl_doc": [1.0e9, 0.0],
        "valor_pix_contestados_aceitos": [100e6, 120e6],
        "valor_devolvido_integral_med": [10e6, 12e6],
        "valor_devolvido_parcial_med": [5e6, 6e6],
        "custo_fraude_nao_devolvido": [85e6, 102e6],
        "taxa_efetividade_med_pct": [15.0, 15.0],
        "razao_chaves_usuario_fraude": [1.8, 1.9],
        "valor_nao_devolvido_saldo_insuficiente": [70e6, 85e6],
        "valor_nao_devolvido_conta_encerrada": [15e6, 17e6],
    })
    df_cartoes = pd.DataFrame({
        "ano_trimestre": ["2024T1", "2024T1"],
        "meio_pagamento": ["Pix", "Crédito"],
        "qtd_transacoes": [10e9, 5e9],
        "vl_transacoes": [5e12, 1e12],
        "ticket_medio": [500.0, 200.0],
        "share_qtd_pct": [66.7, 33.3],
        "share_vl_pct": [83.3, 16.7],
    })
    df_nat = pd.DataFrame({
        "natureza": ["P2P", "P2B"],
        "vl_transacoes": [1.5e12, 1.0e12],
    })
    df_reg = pd.DataFrame({
        "regiao": ["Sudeste", "Nordeste"],
        "vl_pago": [3e12, 1e12],
        "vl_recebido": [3.2e12, 0.8e12],
        "saldo_liquido": [200e9, -200e9],
    })
    df_idade = pd.DataFrame({
        "periodo_label": ["2024-01", "2024-01"],
        "faixa_etaria": ["20 a 29 anos", "30 a 39 anos"],
        "ordem_etaria": [2, 3],
        "qtd_transacoes": [1.2e9, 1.5e9],
    })

    figuras = [
        grafico_volume_nominal_vs_real(df_macro),
        grafico_politica_monetaria(df_macro),
        grafico_dispersao_macro(df_macro),
        grafico_share_meios_empilhado(df_cartoes),
        grafico_comparativo_cartoes_volume(df_cartoes),
        grafico_meios_tradicionais(df_macro, escala_log=True),
        grafico_natureza_pix(df_nat),
        grafico_regional_pago_recebido(df_reg),
        grafico_saldo_liquido_regional(df_reg),
        grafico_mapa_calor_etario(df_idade),
        grafico_funil_med(df_macro),
        grafico_efetividade_vs_laranjas(df_macro),
        grafico_causas_nao_devolucao(df_macro),
    ]

    for fig in figuras:
        assert isinstance(fig, go.Figure)
        assert fig.layout.separators == ",."
        assert len(fig.data) >= 1

    # Pix deve ser a primeira serie (base) no grafico de area empilhada
    fig_share = grafico_share_meios_empilhado(df_cartoes)
    assert fig_share.data[0].name == "Pix"

    # Graficos de barras regionais em ordem crescente
    fig_reg = grafico_regional_pago_recebido(df_reg)
    assert list(fig_reg.data[1].x) == ["Nordeste", "Sudeste"]
    fig_saldo = grafico_saldo_liquido_regional(df_reg)
    assert list(fig_saldo.data[0].x) == ["Nordeste", "Sudeste"]

    # Subtitulos e rodapes analiticos
    notas = [
        nota_volume_nominal_real(df_macro),
        nota_politica_monetaria(df_macro),
        nota_dispersao_macro(df_macro),
        nota_share_meios(df_cartoes),
        nota_comparativo_cartoes(df_cartoes),
        nota_meios_tradicionais(df_macro),
        nota_natureza_pix(df_nat),
        nota_regional_fluxo(df_reg),
        nota_saldo_liquido(df_reg),
        nota_etario(df_idade),
        nota_funil_med(df_macro),
        nota_efetividade_laranjas(df_macro),
        nota_causas_nao_devolucao(df_macro),
    ]
    for sub, rodape in notas:
        assert isinstance(sub, str) and len(sub) > 10
        assert isinstance(rodape, str) and len(rodape) > 10
