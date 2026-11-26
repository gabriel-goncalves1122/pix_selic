"""Componentes compartilhados de renderizacao das abas Streamlit."""
import streamlit as st


def exibir_grafico(titulo: str, fig, notas: tuple[str, str]) -> None:
    """Renderiza titulo, subtitulo discreto (resposta), grafico Plotly e observacao de rodape."""
    subtitulo, rodape = notas
    st.subheader(titulo)
    st.caption(subtitulo)
    st.plotly_chart(fig, width="stretch")
    if rodape:
        st.caption(rodape)
