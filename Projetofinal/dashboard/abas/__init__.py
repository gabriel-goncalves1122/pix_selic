"""Pacote de abas do dashboard Streamlit."""
from abas.geo import renderizar_aba_geo
from abas.macro import renderizar_aba_macro
from abas.med import renderizar_aba_med
from abas.meios import renderizar_aba_meios

__all__ = [
    "renderizar_aba_geo",
    "renderizar_aba_macro",
    "renderizar_aba_med",
    "renderizar_aba_meios",
]
