-- Dimensao Meio / Funcao de Pagamento para comparacao trimestral (Pix vs Cartoes)
with funcoes as (
    select 'Pix' as nome_funcao
    union all
    select distinct nome_funcao from {{ source('prata', 'cartoes_trimestral') }}
)
select
    md5(nome_funcao) as funcao_id,
    nome_funcao
from funcoes
order by nome_funcao
