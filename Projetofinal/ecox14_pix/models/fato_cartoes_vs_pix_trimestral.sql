-- Fato comparativa trimestral: Pix vs Cartao de Credito vs Debito vs Pre-Pago
-- Grao: uma linha por (trimestre, funcao_id) considerando trimestres completos (2021-T1 em diante)
with limite as (
    select max(trimestre) as max_trimestre
    from {{ source('prata', 'cartoes_trimestral') }}
),
pix_trimestral as (
    select
        dt.trimestre,
        dt.ano_trimestre,
        'Pix' as nome_funcao,
        sum(f.qtd_transacoes_total) as qtd_transacoes,
        sum(f.vl_transacoes_total) as vl_transacoes
    from {{ ref('fato_pix_macro_mensal') }} f
    join {{ ref('dim_tempo') }} dt using (ano_mes)
    cross join limite l
    where dt.trimestre between 20211 and l.max_trimestre
    group by dt.trimestre, dt.ano_trimestre
),
cartoes_trimestral as (
    select
        c.trimestre,
        c.ano_trimestre,
        c.nome_funcao,
        sum(c.qtd_transacoes_total) as qtd_transacoes,
        sum(c.valor_transacoes_total) as vl_transacoes
    from {{ source('prata', 'cartoes_trimestral') }} c
    where c.trimestre >= 20211
    group by c.trimestre, c.ano_trimestre, c.nome_funcao
),
unificado as (
    select * from pix_trimestral
    union all
    select * from cartoes_trimestral
)
select
    u.trimestre,
    u.ano_trimestre,
    df.funcao_id,
    u.qtd_transacoes,
    u.vl_transacoes,
    round(u.vl_transacoes / nullif(u.qtd_transacoes, 0), 2) as ticket_medio
from unificado u
join {{ ref('dim_funcao_cartao') }} df
    on u.nome_funcao = df.nome_funcao
order by u.trimestre, u.nome_funcao
