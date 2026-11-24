-- Passa quando devolve ZERO linhas: garante grao unico (trimestre, funcao_id)
select
    trimestre,
    funcao_id,
    count(*) as ocorrencias
from {{ ref('fato_cartoes_vs_pix_trimestral') }}
group by trimestre, funcao_id
having count(*) > 1
