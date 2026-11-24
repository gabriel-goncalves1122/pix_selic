{{ config(materialized='view') }}

-- View analitica pronta para consumo pelo dashboard Streamlit
select
    f.*,
    t.data_mes,
    t.ano,
    t.mes,
    t.trimestre,
    t.periodo_label
from {{ ref('fato_pix_macro_mensal') }} f
join {{ ref('dim_tempo') }} t using (ano_mes)
order by f.ano_mes
