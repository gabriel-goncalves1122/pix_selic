import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src" / "transformacao"))

from limpar_ipca import transformar_ipca
from limpar_cadastros_dict import transformar_cadastros_dict
from limpar_transacoes import transformar_transacoes
from limpar_meios_pagamento import transformar_meios_pagamento
from limpar_cartoes import transformar_cartoes
from enriquecer import agregar_transacoes_mensal


def test_transformar_ipca_calcula_acumulado_12m():
    df_bruto = pd.DataFrame({
        "data": [f"01/{m:02d}/2024" for m in range(1, 13)],
        "valor": ["1,00"] * 12,
    })
    res = transformar_ipca(df_bruto)
    assert len(res) == 12
    assert res["ano_mes"].iloc[0] == 202401
    assert res["ipca_acumulado_12m_pct"].iloc[-1] == 12.68
    assert pd.isna(res["ipca_acumulado_12m_pct"].iloc[0])


def test_transformar_cadastros_dict_agrega_ultimo_do_mes():
    df_bruto = pd.DataFrame({
        "DataGraficosPix": ["2024-01-05", "2024-01-25", "2024-02-20"],
        "qtdUsuariosPessoaFisica": [100, 120, 150],
        "qtdUsuariosPessoaJuridica": [10, 12, 15],
        "qtdUsuariosCadastradosDICTTotal": [110, 132, 165],
    })
    res = transformar_cadastros_dict(df_bruto)
    assert len(res) == 2
    assert res.loc[res["ano_mes"] == 202401, "qtd_usuarios_total"].iloc[0] == 132
    assert res.loc[res["ano_mes"] == 202402, "variacao_usuarios_pct"].iloc[0] == 25.0


def test_agregar_transacoes_mensal_calcula_ticket_e_pj():
    df_tx = pd.DataFrame({
        "ano_mes": [202401, 202401],
        "ano_mes_dt": pd.to_datetime(["2024-01-01", "2024-01-01"]),
        "pag_pfpj": ["PF", "PJ"],
        "quantidade": [100, 100],
        "valor": [1000.0, 3000.0],
    })
    res = agregar_transacoes_mensal(df_tx)
    assert len(res) == 1
    assert res["qtd_transacoes_total"].iloc[0] == 200
    assert res["vl_transacoes_total"].iloc[0] == 4000.0
    assert res["ticket_medio_pix"].iloc[0] == 20.0
    assert res["pct_valor_pj"].iloc[0] == 75.0


def test_transformar_transacoes_filtra_natureza_nao_disponivel():
    df_bruto = pd.DataFrame({
        "AnoMes": [202401, 202401],
        "NATUREZA": ["P2P", "Nao disponivel"],
        "FINALIDADE": [None, "Pix"],
        "VALOR": ["1.234,50", "10,00"],
        "QUANTIDADE": [10, 1],
    })
    res = transformar_transacoes(df_bruto)
    assert len(res) == 1
    assert res["valor"].iloc[0] == 1234.50
    assert res["finalidade"].iloc[0] == "Nao disponivel"


def test_transformar_meios_pagamento_padroniza_unidades():
    df_bruto = pd.DataFrame({
        "AnoMes": [202401],
        "quantidadePix": ["100,0"],
        "valorPix": ["10,0"],
        "quantidadeTED": ["50,0"],
        "valorTED": ["30,0"],
        "quantidadeBoleto": ["50,0"],
        "valorBoleto": ["10,0"],
        "quantidadeCheque": ["0"],
        "valorCheque": ["0"],
        "quantidadeDOC": ["0"],
        "valorDOC": ["0"],
    })
    res = transformar_meios_pagamento(df_bruto)
    assert res["qtd_pix_mpv"].iloc[0] == 100_000
    assert res["vl_pix_mpv"].iloc[0] == 10_000_000.0
    assert res["participacao_pix_qtd_pct"].iloc[0] == 50.0
    assert res["participacao_pix_vl_pct"].iloc[0] == 20.0


def test_transformar_cartoes_filtra_trimestre_e_zeros():
    df_bruto = pd.DataFrame({
        "trimestre": [20194, 20241, 20241],
        "nomeBandeira": ["VISA", "VISA", "Elo"],
        "nomeFuncao": ["Crédito", "Crédito", "Débito"],
        "modalidade": ["Puro", "Puro", "Híbrido"],
        "qtdCartoesAtivos": [100, 500, 0],
        "qtdTransacoesNacionais": [10, 200, 0],
        "valorTransacoesNacionais": ["100,00", "2.000,50", "0"],
        "qtdTransacoesInternacionais": [0, 10, 0],
        "valorTransacoesInternacionais": ["0", "50,00", "0"],
    })
    res = transformar_cartoes(df_bruto)
    assert len(res) == 1
    assert res["ano_trimestre"].iloc[0] == "2024-T1"
    assert res["qtd_transacoes_total"].iloc[0] == 210
    assert res["valor_transacoes_total"].iloc[0] == 2050.50
