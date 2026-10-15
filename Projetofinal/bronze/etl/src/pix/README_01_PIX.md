# Documentação da Camada Bronze — API OData BCB (Olinda)

Esta documentação centraliza todos os detalhes técnicos, catálogos de endpoints e regras de extração da API de Dados Abertos do Banco Central (Olinda) referente ao **Pix**.

## Visão Geral

O Banco Central do Brasil disponibiliza dados abertos através do barramento **Olinda**, que implementa o protocolo [OData v4](http://www.odata.org/). Os dados do Pix estão organizados em **dois serviços independentes**, cada um com seu próprio conjunto de endpoints.

### Base URL

```
https://olinda.bcb.gov.br/olinda/servico/{SERVICO}/versao/v1/odata/{ENDPOINT}?$format=text/csv
```

### Documentação Oficial

| Serviço | Swagger | Documentação |
|---|---|---|
| **Pix_DadosAbertos** | [Swagger UI](https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/swagger-ui3#/) | [Documentação](https://olinda.bcb.gov.br/olinda/servico/Pix_DadosAbertos/versao/v1/documentacao) |
| **SPI** | [Swagger UI](https://olinda.bcb.gov.br/olinda/servico/SPI/versao/v1/swagger-ui3#/) | [Documentação](https://olinda.bcb.gov.br/olinda/servico/SPI/versao/v1/documentacao) |

> [!NOTE]
> **Para regras estruturais do protocolo OData (Paginação proibida, Formato CSV, Rate Limiting), consulte o [Guia Central de Engenharia](../README_00_MOTOR_OLINDA.md).**

## ⚠️ Regras Específicas do Contexto Pix

Durante o desenvolvimento do pipeline Pix, algumas anomalias locais precisaram ser tratadas:

### 1. Parâmetros Case-Sensitive (Pegadinhas da API)
O nome do parâmetro para fatiamento de dados varia brutalmente de acordo com a tabela do Pix:
- Tabela `EstatisticasTransacoesPix` exige o parâmetro `Database` (B minúsculo).
- Tabela `TransacoesPixPorMunicipio` exige o parâmetro `DataBase` (B maiúsculo).
- Tabela `ChavesPix` exige o parâmetro `Data` (formato YYYY-MM-DD).

### 2. Timeouts por Altíssima Densidade
Respostas do Pix possuem centenas de milhares de registros por "fatia" (ex: `EstatisticasFraudesPix` é incrivelmente densa). A tabela de municípios é particionada por "meses", devido à cardinalidade gigantesca. O nosso script orquestrador precisa fatiar essas requisições mês a mês rigorosamente para não estourar o Gateway do BCB.

---

## Catálogo de Endpoints

### Serviço 1: `Pix_DadosAbertos`

Estatísticas relativas a chaves Pix cadastradas no DICT, transações liquidadas no SPI e informações enviadas por participantes do Pix.

#### 1.1 `PixUsuariosCadastradosDICT`

- **Descrição:** Estoque do último dia do mês de usuários cadastrados no DICT, por natureza do usuário.
- **Parâmetro obrigatório:** Nenhum.
- **URL de exemplo:**
  ```
  .../odata/PixUsuariosCadastradosDICT?$format=text/csv
  ```
- **Colunas retornadas:**

| Coluna | Tipo | Descrição |
|---|---|---|
| `DataGraficosPix` | data | Data de referência |
| `qtdUsuariosPessoaFisica` | inteiro | Quantidade de pessoas físicas |
| `qtdUsuariosPessoaJuridica` | inteiro | Quantidade de pessoas jurídicas |
| `qtdUsuariosCadastradosDICTTotal` | inteiro | Total de usuários cadastrados no DICT |

#### 1.2 `EstatisticasTransacoesPix`

- **Descrição:** Quantidade e volume financeiro de transações Pix liquidadas mensalmente. Não inclui Pix liquidados nos livros do participante.
- **Parâmetro obrigatório:** `Database` (formato `YYYYMM`, ex: `202301`).
- **URL de exemplo:**
  ```
  .../odata/EstatisticasTransacoesPix(Database='202301')?$format=json
  ```
- **Volume aproximado:** ~542.910 registros por chamada (todos os meses desde o início do Pix).
- **Colunas retornadas:** `AnoMes`, `PAG_PFPJ`, `REC_PFPJ`, `PAG_REGIAO`, `REC_REGIAO`, `PAG_IDADE`, `REC_IDADE`, `FORMAINICIACAO`, `NATUREZA`, `FINALIDADE`, `VALOR`, `QUANTIDADE`.

#### 1.3 `ChavesPix`

- **Descrição:** Estoque de Chaves Pix no último dia do mês, por participante, segmento e tipo de chave.
- **Parâmetro obrigatório:** `Data` (formato `YYYY-MM-DD`, ex: `2023-01-31`).
- **URL de exemplo:**
  ```
  .../odata/ChavesPix(Data='2023-01-31')?$format=json
  ```
- **Colunas retornadas:** `Data`, `ISPB`, `Nome`, `NaturezaUsuario`, `TipoChave`, `qtdChaves`, `Segmento`.

#### 1.4 `CnaePorteRecebedor`

- **Descrição:** Quantidade e volume financeiro de transações Pix na visão do recebedor, por tipo de pessoa, seção CNAE, porte e forma de iniciação.
- **Parâmetro obrigatório:** `Database` (formato `YYYYMM`).
- **Colunas retornadas:** `AnoMes`, `tipopessoa`, `formainic`, `finalidade`, `porte`, `mei`, `cnssecao`, `mesmatit`, `naturezarel`, `qtpagador`, `qtrecebedor`, `qtlanliq`, `vllanliq`, `vlcompra`, `vldinespec`.

#### 1.5 `TransacoesPixPorMunicipio`

- **Descrição:** Transações Pix por município, abertas por PF/PJ na perspectiva de pagador e recebedor.
- **Parâmetro obrigatório:** `DataBase` (formato `YYYYMM`). ⚠️ Note o `B` maiúsculo.
- **Colunas retornadas:** `AnoMes`, `Municipio_Ibge`, `Municipio`, `Estado_Ibge`, `Estado`, `Sigla_Regiao`, `Regiao`, `VL_PagadorPF`, `QT_PagadorPF`, `VL_PagadorPJ`, `QT_PagadorPJ`, `VL_RecebedorPF`, `QT_RecebedorPF`, `VL_RecebedorPJ`, `QT_RecebedorPJ`, `QT_PES_PagadorPF`, `QT_PES_PagadorPJ`, `QT_PES_RecebedorPF`, `QT_PES_RecebedorPJ`.

#### 1.6 `EstatisticasFraudesPix`

- **Descrição:** Transações Pix contestadas via MED (Mecanismo Especial de Devolução). Publicados 30 dias após o término do mês.
- **Parâmetro obrigatório:** `Database` (formato `YYYYMM`).
- **Colunas retornadas:** `AnoMes`, `QtdePixcontestados`, `Qtdecontestacoesaceitas`, `Qtdecontestacoesrejeitadas`, `Qtdecontestacoesaceitasacada100mil`, `QtdeUsuarioscommarcacoesdefraude`, `QtdeChavesPixcommarcacoesdefraude`, `ValorPixcontestadosaceitos`, `PercentualdeDevolucao`, `QtdePixbloqueadoscautelarmenteeliberados`, `QtdePixbloqueadoscautelarmenteedevolvidos`.

---

### Serviço 2: `SPI` (Sistema de Pagamentos Instantâneos)

Estatísticas das movimentações financeiras transitadas no SPI processadas através de lançamentos nas contas PI.

#### 2.1 `PixLiquidadosAtual`

- **Descrição:** Pix liquidados por dia no SPI (transferências PACS008 e devoluções PACS004). Valores em **milhares de R$**.
- **Parâmetro obrigatório:** Nenhum.
- **Colunas retornadas:** `Data`, `Quantidade`, `CanalPrimario`, `CanalSecundario`, `Total`, `Media`.

#### 2.2 `PixLiquidadosIntradia`

- **Descrição:** Distribuição intradia — quantidades e valores médios por intervalo de 30 minutos, nos últimos 30 dias. Valores em **milhares de R$**.
- **Colunas:** `Horario`, `QuantidadeMedia`, `TotalMedio`.

#### 2.3 `PixRemuneracaoContaPI`

- **Descrição:** Remuneração paga pelo BCB às instituições financeiras para manutenção dos saldos em conta PI.
- **Colunas:** `DataBase`, `BaseRemuneracaoIF`, `ValorRemuneradoIF`, `BaseRemuneracaoTotal`, `ValorRemuneradoTotal`, `SelicAnual`.

#### 2.4 `PixDisponibilidadeSPI`

- **Descrição:** Índice de disponibilidade do SPI frente ao mínimo normativo (24h/dia, 365 dias/ano).
- **Colunas:** `DataBase`, `Indice`, `MinimoNormativo`.

#### 2.5 `PixInterrupcaoSPI`

- **Descrição:** Eventos de indisponibilidade do SPI nos últimos 3 meses. Divulgado até o dia 20 de cada mês.
- **Colunas:** `DataHoraInicioInt`, `DataHoraTerminoInt`, `Interrupcao`.
