-- Dimensao Faixa Etaria ordenada para analise geracional do Pix
with faixas as (
    select distinct coalesce(pag_idade, 'Nao informado') as faixa_etaria
    from {{ source('prata', 'transacoes_pix') }}
)
select
    md5(faixa_etaria) as idade_id,
    faixa_etaria,
    case faixa_etaria
        when 'até 19 anos' then 1
        when 'entre 20 e 29 anos' then 2
        when 'entre 30 e 39 anos' then 3
        when 'entre 40 e 49 anos' then 4
        when 'entre 50 e 59 anos' then 5
        when 'mais de 60 anos' then 6
        when 'Nao se aplica' then 7
        else 8
    end as ordem_etaria
from faixas
order by ordem_etaria
