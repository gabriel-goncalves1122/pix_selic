-- Fato etaria: adocao do Pix por mes e faixa etaria do pagador
-- Grao: uma linha por (ano_mes, idade_id)
select
    t.ano_mes,
    i.idade_id,
    sum(t.quantidade) as qtd_transacoes,
    sum(t.valor) as vl_transacoes
from {{ source('prata', 'transacoes_pix') }} t
join {{ ref('dim_faixa_etaria') }} i
    on coalesce(t.pag_idade, 'Nao informado') = i.faixa_etaria
where t.ano_mes is not null
group by
    t.ano_mes,
    i.idade_id
