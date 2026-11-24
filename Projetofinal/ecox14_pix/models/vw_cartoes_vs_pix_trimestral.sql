{{ config(materialized='view') }}

-- View trimestral comparando Pix vs Cartao de Credito, Debito e Pre-Pago com share de mercado (%)
select
    f.trimestre,
    f.ano_trimestre,
    cast(f.trimestre // 10 as integer) as ano,
    d.nome_funcao as meio_pagamento,
    f.qtd_transacoes,
    f.vl_transacoes,
    f.ticket_medio,
    round(f.qtd_transacoes * 100.0 / sum(f.qtd_transacoes) over (partition by f.trimestre), 2) as share_qtd_pct,
    round(f.vl_transacoes * 100.0 / sum(f.vl_transacoes) over (partition by f.trimestre), 2) as share_vl_pct
from {{ ref('fato_cartoes_vs_pix_trimestral') }} f
join {{ ref('dim_funcao_cartao') }} d using (funcao_id)
order by f.trimestre, d.nome_funcao
