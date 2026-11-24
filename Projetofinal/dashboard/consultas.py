"""
Modulo de consultas SQL do dashboard (somente leitura na Camada Ouro).
"""
from pathlib import Path

import duckdb
import streamlit as st

RAIZ = Path(__file__).resolve().parent.parent
BANCO = RAIZ / "dados" / "ouro" / "projeto.duckdb"


def banco_existe() -> bool:
    return BANCO.exists()


@st.cache_data
def _consultar(sql: str, parametros=None):
    """Executa consulta parametrizada em modo read_only=True."""
    con = duckdb.connect(str(BANCO), read_only=True)
    try:
        return con.execute(sql, parametros or []).df()
    finally:
        con.close()


def anos():
    """Lista de anos disponiveis na dim_tempo."""
    return _consultar("""
        select distinct ano
        from ouro.dim_tempo
        where ano is not null
        order by ano
    """)


def serie_pix_macro(ano_inicio: int, ano_fim: int):
    """Serie mensal consolidada: Pix, Meios Tradicionais, Funil MED, DICT, Selic, IPCA e Juro Real."""
    return _consultar(
        """
        select
            ano_mes,
            periodo_label,
            ano,
            qtd_transacoes_total,
            vl_transacoes_total,
            vl_pix_real_deflacionado,
            vl_pag_pf,
            vl_pag_pj,
            ticket_medio_pix,
            ticket_medio_pix_real,
            pct_valor_pj,
            qtd_ted,
            vl_ted,
            qtd_boleto,
            vl_boleto,
            qtd_cheque,
            vl_cheque,
            qtd_doc,
            vl_doc,
            participacao_pix_qtd_pct,
            participacao_pix_vl_pct,
            qtd_pix_contestados,
            qtd_contestacoes_aceitas,
            taxa_contestacoes_aceitas_por_100mil,
            qtd_usuarios_marcacao_fraude,
            qtd_chaves_marcacao_fraude,
            razao_chaves_usuario_fraude,
            valor_pix_contestados_aceitos,
            valor_devolvido_integral_med,
            valor_devolvido_parcial_med,
            valor_nao_devolvido_saldo_insuficiente,
            valor_nao_devolvido_conta_encerrada,
            custo_fraude_nao_devolvido,
            taxa_efetividade_med_pct,
            percentual_devolucao,
            qtd_usuarios_total,
            selic_meta_fim_mes,
            ipca_mensal_pct,
            ipca_acumulado_12m_pct,
            juro_real_ex_post_pct
        from ouro.vw_pix_macro_completo
        where ano between ? and ?
        order by ano_mes
        """,
        [int(ano_inicio), int(ano_fim)],
    )


def resumo_periodo(ano_inicio: int, ano_fim: int):
    """Indicadores agregados para os cartoes de resumo."""
    return _consultar(
        """
        select
            count(*) as meses,
            sum(qtd_transacoes_total) as total_transacoes,
            sum(vl_transacoes_total) as total_valor,
            avg(ticket_medio_pix) as ticket_medio,
            avg(selic_meta_fim_mes) as selic_media,
            avg(ipca_acumulado_12m_pct) as ipca_12m_medio,
            avg(juro_real_ex_post_pct) as juro_real_medio,
            sum(custo_fraude_nao_devolvido) as custo_fraude_total
        from ouro.vw_pix_macro_completo
        where ano between ? and ?
        """,
        [int(ano_inicio), int(ano_fim)],
    )


def cartoes_vs_pix_trimestral(ano_inicio: int, ano_fim: int):
    """Comparacao trimestral entre Pix e Cartoes (Credito, Debito, Pre-Pago)."""
    return _consultar(
        """
        select
            trimestre,
            ano_trimestre,
            meio_pagamento,
            qtd_transacoes,
            vl_transacoes,
            ticket_medio,
            share_qtd_pct,
            share_vl_pct
        from ouro.vw_cartoes_vs_pix_trimestral
        where ano between ? and ?
        order by trimestre, meio_pagamento
        """,
        [int(ano_inicio), int(ano_fim)],
    )


def volume_por_natureza(ano_inicio: int, ano_fim: int):
    """Volume financeiro e quantidade de transacoes por natureza economica do Pix."""
    return _consultar(
        """
        select
            n.natureza,
            sum(f.qtd_transacoes) as qtd_transacoes,
            sum(f.vl_transacoes) as vl_transacoes
        from ouro.fato_pix_segmentado_mensal f
        join ouro.dim_natureza_pix n using (natureza_id)
        join ouro.dim_tempo t using (ano_mes)
        where t.ano between ? and ?
        group by n.natureza
        order by vl_transacoes desc
        """,
        [int(ano_inicio), int(ano_fim)],
    )


def fluxo_regional(ano_inicio: int, ano_fim: int):
    """Volume pago, recebido e saldo liquido interestadual por regiao."""
    return _consultar(
        """
        with pago as (
            select regiao_pagadora as regiao, sum(vl_transacoes) as vl_pago, sum(qtd_transacoes) as qtd_paga
            from ouro.vw_pix_regional_fluxo
            where ano between ? and ?
            group by 1
        ),
        recebido as (
            select regiao_recebedora as regiao, sum(vl_transacoes) as vl_recebido, sum(qtd_transacoes) as qtd_recebida
            from ouro.vw_pix_regional_fluxo
            where ano between ? and ?
            group by 1
        )
        select
            coalesce(p.regiao, r.regiao) as regiao,
            coalesce(p.vl_pago, 0) as vl_pago,
            coalesce(r.vl_recebido, 0) as vl_recebido,
            coalesce(r.vl_recebido, 0) - coalesce(p.vl_pago, 0) as saldo_liquido,
            coalesce(p.qtd_paga, 0) as qtd_paga
        from pago p
        full outer join recebido r using (regiao)
        where coalesce(p.regiao, r.regiao) <> 'Nao informado'
        order by vl_recebido desc
        """,
        [int(ano_inicio), int(ano_fim), int(ano_inicio), int(ano_fim)],
    )


def adocao_etaria_serie(ano_inicio: int, ano_fim: int):
    """Evolucao mensal de transacoes Pix por faixa etaria."""
    return _consultar(
        """
        select
            periodo_label,
            faixa_etaria,
            ordem_etaria,
            qtd_transacoes,
            vl_transacoes
        from ouro.vw_pix_etario
        where ano between ? and ?
          and faixa_etaria not in ('Nao se aplica', 'Nao informado')
        order by ano_mes, ordem_etaria
        """,
        [int(ano_inicio), int(ano_fim)],
    )
