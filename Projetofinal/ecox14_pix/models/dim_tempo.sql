-- Dimensao Tempo (grao: um mes de referencia)
select distinct
    ano_mes,
    cast(ano_mes_dt as date) as data_mes,
    cast(ano_mes // 100 as integer) as ano,
    cast(ano_mes % 100 as integer) as mes,
    cast(((ano_mes % 100) - 1) // 3 + 1 as integer) as trimestre_num,
    cast((ano_mes // 100) * 10 + (((ano_mes % 100) - 1) // 3 + 1) as integer) as trimestre,
    cast(ano_mes // 100 as varchar) || '-T' || cast(((ano_mes % 100) - 1) // 3 + 1 as varchar) as ano_trimestre,
    strftime(cast(ano_mes_dt as date), '%Y-%m') as periodo_label
from {{ source('prata', 'pix_macro_enriquecido') }}
where ano_mes is not null
order by ano_mes
