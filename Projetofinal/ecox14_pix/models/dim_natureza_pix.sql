-- Dimensao Natureza e Finalidade do Pix
select distinct
    md5(
        coalesce(natureza, '') || '|' ||
        coalesce(finalidade, '') || '|' ||
        coalesce(formainiciacao, '')
    ) as natureza_id,
    natureza,
    finalidade,
    formainiciacao as forma_iniciacao
from {{ source('prata', 'transacoes_pix') }}
where natureza is not null
