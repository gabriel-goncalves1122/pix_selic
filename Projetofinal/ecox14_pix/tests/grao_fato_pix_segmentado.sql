-- Passa quando devolve ZERO linhas: garante grao unico por (ano_mes, natureza_id, pag_pfpj, rec_pfpj)
select
    ano_mes,
    natureza_id,
    pag_pfpj,
    rec_pfpj,
    count(*) as ocorrencias
from {{ ref('fato_pix_segmentado_mensal') }}
group by ano_mes, natureza_id, pag_pfpj, rec_pfpj
having count(*) > 1
