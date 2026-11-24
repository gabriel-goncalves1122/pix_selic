{{ config(materialized='view') }}

-- View etaria mensal ordenada por faixa etaria
select
    f.ano_mes,
    t.ano,
    t.periodo_label,
    i.faixa_etaria,
    i.ordem_etaria,
    f.qtd_transacoes,
    f.vl_transacoes
from {{ ref('fato_pix_etario_mensal') }} f
join {{ ref('dim_tempo') }} t using (ano_mes)
join {{ ref('dim_faixa_etaria') }} i using (idade_id)
order by f.ano_mes, i.ordem_etaria
