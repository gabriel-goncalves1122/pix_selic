import re

import pandas as pd

from comum import converter_numero_br

_RE_CAMEL_1 = re.compile(r"(.)([A-Z][a-z]+)")
_RE_CAMEL_2 = re.compile(r"([a-z0-9])([A-Z])")
_RE_NAO_ALNUM = re.compile(r"[^a-zA-Z0-9_]")


def to_snake_case(name: str) -> str:
    """Converte uma string para snake_case limpo (ex: 'VL_PagadorPF' -> 'vl_pagador_pf')."""
    s1 = _RE_CAMEL_1.sub(r"\1_\2", name)
    s2 = _RE_CAMEL_2.sub(r"\1_\2", s1)
    return _RE_NAO_ALNUM.sub("", s2).lower()


def limpar_nomes_colunas(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica snake_case em todas as colunas do DataFrame."""
    df.columns = [to_snake_case(col) for col in df.columns]
    return df


def tratar_valor_financeiro(serie_pandas: pd.Series) -> pd.Series:
    """Converte serie numerica PT-BR para float64."""
    return converter_numero_br(serie_pandas)
