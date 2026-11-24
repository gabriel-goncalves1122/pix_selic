-- Passa quando devolve ZERO linhas: garante que nao ha volumes ou quantidades negativas na fato mensal
select
    ano_mes,
    qtd_transacoes_total,
    vl_transacoes_total
from {{ ref('fato_pix_macro_mensal') }}
where qtd_transacoes_total < 0
   or vl_transacoes_total < 0
