# Decisões de Tratamento e Atributos Derivados (Camada Prata)

Este documento registra as decisões de qualidade de dados aplicadas na transformação da Camada Bronze para a Camada Prata, bem como a definição e justificativa de cada atributo derivado.

---

## 1. Decisões de Tratamento por Fonte

### Transações Pix (`estatisticas_transacoes_pix.parquet`)
- **Bypass de duplicação em escada:** leitura exclusiva do arquivo `EstatisticasTransacoesPix_202011.csv`, que contém toda a série histórica consolidada (**768.106** registros). Ver detalhes em [`CASE_GRANULARIDADE_PIX.md`](CASE_GRANULARIDADE_PIX.md).
- **Conversão monetária:** valores financeiros no formato brasileiro (`"9552,71"`) convertidos para `float64`.
- **Padronização:** colunas renomeadas para `snake_case` e criação de `ano_mes_dt` (`YYYY-MM-01`).

### Fraudes Pix — MED (`estatisticas_fraudes_pix.parquet`)
- **Série histórica:** **57** meses consolidados.
- **Ausentes no cruzamento (`how="left"`):** os **15** meses iniciais do Pix (`202011` a `202201`) antecedem a criação do Mecanismo Especial de Devolução (MED) pelo Banco Central. Foram **mantidos** na tabela enriquecida e sinalizados via `WARNING` no `pipeline.log` (ausência legítima de domínio).

### Cadastro de Usuários DICT (`usuarios_dict_mensal.parquet`)
- **Agregação de estoque:** mantido o último registro de cada mês (`72` meses, 100% de cobertura com a série de transações).

### Taxa Selic e IPCA (`taxa_selic_mensal.parquet`, `taxa_ipca_mensal.parquet`)
- **Formato e tipagem:** datas convertidas com `format="%d/%m/%Y"` explícito e valores numéricos convertidos de vírgula decimal para `float64`.
- **Anualização:** Selic realizada diária (SGS 11) anualizada na base de 252 dias úteis.

### Valores Extremos (IQR e Z-Score)
- Picos sazonais (como dezembro) e oscilações de contestação são sinalizados em colunas `*_extremo_iqr` e `*_extremo_z` em `enriquecer.py`, **sem exclusão**, pois representam comportamento econômico legítimo.

---

## 2. Atributos Derivados

### `ticket_medio_pix`
Valor médio por transação Pix no mês (`vl_transacoes_total / qtd_transacoes_total`). Serve para diferenciar o crescimento por volume de micropagamentos do uso para transações de maior valor.

### `pct_valor_pj` e `pct_qtd_pj`
Participação percentual de pagadores Pessoa Jurídica no valor e na quantidade total de transações. Mede a adoção corporativa do Pix frente ao varejo Pessoa Física.

### `variacao_vl_pix_pct`, `variacao_qtd_pix_pct` e `variacao_usuarios_pct`
Variação percentual mensal em relação ao mês anterior (`pct_change()` após ordenação por `ano_mes`). Fica ausente (`NaN`) no primeiro mês da série por definição.

### `selic_realizada_anualizada_pct`
Taxa Selic diária (SGS 11) anualizada na base de 252 dias úteis (`((1 + taxa_dia/100)^252 - 1) * 100`), permitindo comparação direta com a Selic Meta (`% a.a.`).

### `ipca_acumulado_12m_pct`
Inflação acumulada em janela móvel de 12 meses via juros compostos sobre o IPCA mensal (SGS 433). Fica ausente (`NaN`) nos primeiros 11 meses da série por não haver janela completa de 12 meses.
