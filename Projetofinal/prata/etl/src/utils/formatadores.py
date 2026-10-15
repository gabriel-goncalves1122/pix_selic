import pandas as pd
import re

def to_snake_case(name):
    """
    Converte uma string (como nome de coluna) para snake_case limpo.
    Ex: 'AnoMes' -> 'ano_mes', 'VL_PagadorPF' -> 'vl_pagador_pf'
    """
    # Adiciona underscore antes de letras maiúsculas que vêm depois de minúsculas
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Adiciona underscore antes de letras maiúsculas precedidas por letras minúsculas ou números
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    # Remove caracteres especiais e espaços, converte para minúsculo
    limpo = re.sub(r'[^a-zA-Z0-9_]', '', s2).lower()
    return limpo

def limpar_nomes_colunas(df):
    """Aplica snake_case em todas as colunas do DataFrame."""
    df.columns = [to_snake_case(col) for col in df.columns]
    return df

def tratar_valor_financeiro(serie_pandas):
    """
    Converte uma série pandas (string) de valor monetário (ex: '9552,71') para Float real (9552.71).
    """
    # Substitui a vírgula por ponto e converte para float. Trata nulos caso existam.
    return serie_pandas.astype(str).str.replace(',', '.').astype(float)
