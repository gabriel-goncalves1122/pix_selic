-- Passa quando devolve ZERO linhas: soma regional por mes deve bater com a fato macro (tolerancia R$ 1)
with reg as (
    select ano_mes, sum(vl_transacoes) as vl_reg
    from {{ ref('fato_pix_regional_mensal') }}
    group by ano_mes
)
select
    m.ano_mes,
    m.vl_transacoes_total,
    r.vl_reg
from {{ ref('fato_pix_macro_mensal') }} m
join reg r using (ano_mes)
where abs(m.vl_transacoes_total - r.vl_reg) > 1.0
