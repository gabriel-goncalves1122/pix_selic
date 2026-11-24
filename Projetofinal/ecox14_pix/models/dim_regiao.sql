-- Dimensao Regiao Geografica (Brasil + Nao informado)
with regioes as (
    select distinct pag_regiao as regiao from {{ source('prata', 'transacoes_pix') }}
    union
    select distinct rec_regiao as regiao from {{ source('prata', 'transacoes_pix') }}
)
select
    md5(coalesce(regiao, 'Nao informado')) as regiao_id,
    coalesce(regiao, 'Nao informado') as regiao
from regioes
order by regiao
