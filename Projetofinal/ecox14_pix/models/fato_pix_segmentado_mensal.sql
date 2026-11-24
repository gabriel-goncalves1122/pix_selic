-- Fato segmentada: volume e valor do Pix por mes, natureza/finalidade e perfil PF/PJ
-- Grao: uma linha por (ano_mes, natureza_id, pag_pfpj, rec_pfpj)
select
    t.ano_mes,
    d.natureza_id,
    t.pag_pfpj,
    t.rec_pfpj,
    sum(t.quantidade) as qtd_transacoes,
    sum(t.valor) as vl_transacoes
from {{ source('prata', 'transacoes_pix') }} t
join {{ ref('dim_natureza_pix') }} d
    on coalesce(t.natureza, '') = coalesce(d.natureza, '')
   and coalesce(t.finalidade, '') = coalesce(d.finalidade, '')
   and coalesce(t.formainiciacao, '') = coalesce(d.forma_iniciacao, '')
where t.ano_mes is not null
group by
    t.ano_mes,
    d.natureza_id,
    t.pag_pfpj,
    t.rec_pfpj
