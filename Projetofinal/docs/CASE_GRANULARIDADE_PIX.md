# Case Study: Granularidade e Agregação de Dados no Pix

**Data do Veredito**: 30 de Setembro de 2026  
**Contexto**: Análise volumétrica da tabela `EstatisticasTransacoesPix` extraída via API Olinda do BCB.

## 1. O Paradoxo do Volume de Transações
Durante o processo de exploração de dados (Data Profiling) na **Camada Bronze**, deparamo-nos com uma discrepância aparente:
O Pix processa *bilhões* de transações mensalmente em território nacional. No entanto, o arquivo extraído (`EstatisticasTransacoesPix_202011.csv`) continha toda a série histórica em apenas **~741.000 linhas**.

Uma base de transações individuais (microdados) contendo bilhões de linhas por mês geraria petabytes de dados e comprometeria o sigilo bancário dos usuários (LGPD/PII). 

## 2. A Descoberta: Data Mart e Agregação Multidimensional (Cubo OLAP)
Através de auditoria documental (Swagger OData da API Olinda) e scripts forenses executados em DuckDB, comprovamos matematicamente que o dataset **NÃO é um log transacional**, mas sim uma **Tabela de Agregação (Cubo OLAP)**.

A API do Banco Central devolve os dados pré-agregados (via `GROUP BY` interno) usando "Baldes Estatísticos" (Buckets). Cada linha do CSV representa a combinação exata das seguintes dimensões para um determinado mês:
- `AnoMes`: Safra da transação.
- `PAG_PFPJ` / `REC_PFPJ`: Natureza jurídica (PF vs PJ).
- `PAG_REGIAO` / `REC_REGIAO`: Região geográfica.
- `PAG_IDADE` / `REC_IDADE`: Faixas etárias.
- `FORMAINICIACAO`: Como o Pix foi iniciado (QR Code, Manual, etc).
- `NATUREZA` / `FINALIDADE`: Tipo da transferência.

## 3. As Métricas Finais (`QUANTIDADE` e `VALOR`)
A granularidade da tabela reside na combinação dimensional acima. Para quantificar as operações, a tabela possui duas colunas de métricas finais:
1. **`QUANTIDADE`**: Representa a contagem pura (`COUNT`) de quantas transações idênticas caíram naquele balde demográfico. 
   - *Fórmula OLAP*: `SUM(QUANTIDADE)` retorna o número total de transações Pix do país.
2. **`VALOR`**: Representa o somatório financeiro (`SUM`) de todas as transações daquele balde.
   - *Fórmula OLAP*: `SUM(VALOR)` retorna o Produto Interno transacionado.

## 4. Impacto na Arquitetura (Engenharia de Dados)
A utilização desta granularidade agregada provida pela API OData permitiu que o nosso pipeline na Camada Bronze fosse extremamente leve e eficiente. Em vez de lidar com clusters de Big Data caríssimos para ingerir petabytes de logs de microdados, a arquitetura extrai o histórico completo do país de forma compactada (aprox. 50 MB na Camada Prata). 

Essa eficiência é o pilar da nossa solução analítica e demonstra o domínio técnico sobre modelagem de dados multidimensionais (Modelagem Dimensional e OLAP).
