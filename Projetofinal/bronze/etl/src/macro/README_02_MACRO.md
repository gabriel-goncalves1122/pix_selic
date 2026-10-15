# Documentação da Camada Bronze — API Macroeconômica

Esta documentação centraliza todos os detalhes técnicos das APIs do Banco Central utilizadas para a extração do contexto macroeconômico e bancário (o "Custo Brasil").

Para construir um *dashboard* profundo e premiado sobre o Custo Brasil, extraímos dados de duas grandes fontes oficiais do Banco Central, cada uma servindo um propósito analítico.

---

## 1. Fonte A: Sistema Gerenciador de Séries Temporais (SGS)

O SGS é a fonte mais direta para dados históricos "Realizados". Ele entrega séries temporais limpas, onde cada resposta contém basicamente a `[Data]` e o `[Valor]`.

### Base URL (SGS)
```
https://api.bcb.gov.br/dados/serie/bcdata.sgs.{CODIGO}/dados?formato=csv
```

### Indicadores (Códigos Ativos)
| Código | Título | Periodicidade | Unidade | 
|---|---|---|---|
| **432** | Taxa Selic (Meta COPOM) | Diária | % a.a |
| **11** | Taxa Selic (Realizada) | Diária | % a.d. |
| **433** | IPCA (Índice Nac. de Preços ao Consumidor Amplo) | Mensal | % ao mês |

*Nota técnica:* O SGS não possui limitação impeditiva de rate-limit e pode ser consumido baixando o histórico completo (do início até a data atual).

### Documentação Oficial (Swagger)
| Serviço | Swagger |
|---|---|
| **Expectativas (Focus)** | [Swagger UI](https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/swagger-ui3#/) |
| **selic_operacoes** | [Swagger UI](https://olinda.bcb.gov.br/olinda/servico/selic_operacoes/versao/v1/swagger-ui3#/) |
| **IFDATA** | [Swagger UI](https://olinda.bcb.gov.br/olinda/servico/IFDATA/versao/v1/swagger-ui3#/) |

---

> [!NOTE]
> **Para regras estruturais do protocolo OData (Paginação proibida, Formato CSV, Rate Limiting), consulte o [Guia Central de Engenharia](../README_00_MOTOR_OLINDA.md).**

## 2. Fonte B: OData (Sistema Olinda)

Enquanto o SGS entrega a linha do tempo "seca", a API Olinda entrega bancos de dados ricos, estruturados em OData v4. É aqui que moram os detalhes de **Custo do Crédito**, **Balanço dos Bancos** e **Expectativas**.

### Regras Específicas do Contexto Macro
1. **SGS vs Olinda:** A API SGS não utiliza o protocolo OData. Em vez de usar `$format=text/csv`, passamos o parâmetro de query string `?formato=csv`.
2. **Filtros Inteligentes Obrigatórios:** Use `$filter` rigorosamente no Boletim Focus (Expectativas). Essa tabela mistura dezenas de indicadores. Faremos sempre: `$filter=Indicador eq 'IPCA' or Indicador eq 'Selic'`.

### Catálogo de Ouro (Mapeamento de Valor para "Custo Brasil")

#### B.1. Serviço: `Expectativas` (Boletim Focus)
Contém as apostas do mercado financeiro para os indicadores.
- **Tabela Mestre:** `ExpectativaMercadoMensal`
- **Por que usar:** Mostra a evolução das expectativas mês a mês.
- **Colunas-chave:**
  - `Indicador`: IPCA ou Selic.
  - `DataReferencia`: O mês/ano que o mercado tentava prever.
  - `Data`: A data em que a previsão foi consolidada.
  - `Media` / `Mediana`: O consenso geral dos bancos.
  - `Minimo` / `Maximo`: Os pontos fora da curva (extremos).

#### B.2. Serviço: `selic_operacoes`
Extrato de como os players compram/vendem títulos indexados à Selic. Revela **o volume astronômico de dinheiro** rolando no sistema sem risco.
- **Tabela Mestre:** `OperacoesEmUmMes`
- **Por que usar:** A visão diária explodiria o processamento; a visão mensal nos dá o "Volume de Bilhões" exato por categoria de título.
- **Colunas-chave:**
  - `Mes`: Safra da operação (MM/YYYY).
  - `Categoria`: Categoria da operação (ex: Compromissadas).
  - `QuantidadeAcumulada`: Quantidade de negócios.
  - `ValorAcumulado`: Volume financeiro total no mês.

#### B.3. Serviço: `IFDATA` (Instituições Financeiras)
Contabilidade e balanço de lucros dos bancos no Brasil.
- **Tabela Mestre:** `TipoIfValores` (e `TipoIfDataCadastro` para o nome do banco).
- **Por que usar:** Provar se as altas taxas do "Custo Brasil" se revertem em margens de lucros recordes.
- **Colunas-chave (`TipoIfValores`):**
  - `AnoMes`: Safra do balanço (YYYYMM).
  - `CodInst`: Código identificador do banco.
  - `NomeRelatorio`: Agrupamento do relatório.
  - `NomeColuna`: O indicador contábil (Ex: "Lucro Líquido", "ROE").
  - `Saldo`: O valor apurado em Reais/Percentual.

---

## 3. Orquestração e Integração no Pipeline
Todos os scripts para a ingestão deste módulo residem na mesma pasta (`src/macro/`) e importam as funções de resiliência (retry, timeout, checkpoint) de `src/utils/utils_ingestao.py`. 

- Para executar as extrações (SGS e Focus):
  ```bash
  ./rodar_ingestao_macro.sh
  ```
