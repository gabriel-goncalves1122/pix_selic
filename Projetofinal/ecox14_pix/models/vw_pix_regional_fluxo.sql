{{ config(materialized='view') }}

-- View de fluxo regional mensal (pagador -> recebedor) para consumo no dashboard
select
    f.ano_mes,
    t.ano,
    t.periodo_label,
    rp.regiao as regiao_pagadora,
    rr.regiao as regiao_recebedora,
    f.qtd_transacoes,
    f.vl_transacoes
from {{ ref('fato_pix_regional_mensal') }} f
join {{ ref('dim_tempo') }} t using (ano_mes)
join {{ ref('dim_regiao') }} rp on f.pag_regiao_id = rp.regiao_id
join {{ ref('dim_regiao') }} rr on f.rec_regiao_id = rr.regiao_id
