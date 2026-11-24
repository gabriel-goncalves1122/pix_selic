-- Fato regional: matriz de fluxos Pix por mes, regiao pagadora e regiao recebedora
-- Grao: uma linha por (ano_mes, pag_regiao_id, rec_regiao_id)
select
    t.ano_mes,
    rp.regiao_id as pag_regiao_id,
    rr.regiao_id as rec_regiao_id,
    sum(t.quantidade) as qtd_transacoes,
    sum(t.valor) as vl_transacoes
from {{ source('prata', 'transacoes_pix') }} t
join {{ ref('dim_regiao') }} rp
    on coalesce(t.pag_regiao, 'Nao informado') = rp.regiao
join {{ ref('dim_regiao') }} rr
    on coalesce(t.rec_regiao, 'Nao informado') = rr.regiao
where t.ano_mes is not null
group by
    t.ano_mes,
    rp.regiao_id,
    rr.regiao_id
