# Engenharia da Camada Bronze — Guia Geral (API Olinda)

Este documento descreve as decisões de arquitetura de dados e as regras universais de extração aplicadas ao longo de toda a **Camada Bronze**, em especial no consumo da API OData do Banco Central do Brasil (Projeto Olinda).

---

## 1. O Motor de Ingestão (`utils_ingestao.py`)

Em vez de cada script de contexto (Pix, Macro, etc.) implementar lógicas de rede próprias, consolidamos o coração da ingestão no módulo `/utils/utils_ingestao.py`. Ele atua como um escudo protetor para garantir resiliência contra as instabilidades do Banco Central.

### 1.1 Resiliência e "Heavy Retry"
O BCB frequentemente impõe *rate-limits* através de bloqueios temporários de resolução DNS. Para mitigar:
- Adotamos um sistema de **tentativas infinitas até 5 retries** com um *backoff* de espera progressivo longo (`[15s, 30s, 60s, 120s]`).
- Toleramos explicitamente erros da família 5xx (ex: `504 Gateway Timeout` ou `500 Erro Desconhecido`), pausando a execução e repetindo a mesma URL em seguida.

### 1.2 Checkpoint Inteligente
O pipeline jamais faz o mesmo trabalho duas vezes. Antes de disparar qualquer requisição, a arquitetura verifica se o arquivo final `.csv` já existe na pasta `raw/`. Isso permite interromper scripts no meio da madrugada e recomeçar exatamente do ponto onde parou.

---

## 2. Regras Universais do OData (BCB)

Qualquer novo módulo (Pix, Macro, Crédito) construído sobre a API Olinda OData deve respeitar rigorosamente as seguintes premissas:

### Regra de Ouro: Proibição de Paginação
O Banco Central configurou todas as tabelas pesadas com a flag `"naoPaginavel": true`.
- ❌ Enviar `$top=1000` ou `$skip=1000` causará erro imediato de **HTTP 500**. 
- ✅ O correto é solicitar a página completa filtrando uma dimensão menor (ex: filtrando por mês na URL).

### Otimização de Formato: Migração para CSV
Por padrão, APIs OData respondem em JSON (`$format=json`). No entanto, algumas chamadas do BCB devolvem até 750.000 registros por bloco.
- O JSON repete o nome de todas as colunas para todas as linhas, gerando um payload massivo e estourando o *Timeout* do Banco Central.
- Adotamos forçosamente a instrução `?$format=text/csv` no motor. O payload encolhe drasticamente e soluciona os erros `504`. Toda a pasta `/raw/` armazena exclusivamente `.csv`.

---

## 3. Navegação por Contextos Específicos

Os metadados das tabelas (os Catálogos) estão segmentados por área de negócio. Para acessar os links do Swagger e regras de negócio de uma API específica, acesse:

- 🟩 **[Contexto Pix](pix/README_01_PIX.md)**: Dados de Transações, Chaves, Usuários e SPI.
- 🟦 **[Contexto Macro](macro/README_02_MACRO.md)**: Indicadores IPCA, Selic Realizada, e Expectativas de Mercado (Focus).
