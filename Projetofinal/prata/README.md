# Camada Prata — Ecossistema de Pagamentos (PIX)

> **Objetivo:** Transformar os dados brutos da Camada Bronze em tabelas limpas, tipadas e prontas para cruzamento analítico, respondendo à pergunta norteadora do projeto.

---

## 1. Diagnóstico da Bronze (O que temos)

A análise dos JSONs de profiling revelou **4 datasets** com as seguintes características:

### 1.1 `PixUsuariosCadastradosDICT` — Adoção do Pix
| Coluna | Tipo (Bronze) | Nulos | Obs |
|--------|--------------|-------|-----|
| `DataGraficosPix` | DateTime | 0% | ✅ Já é data nativa |
| `qtdUsuariosPessoaFisica` | Numeric | 0% | ✅ Limpo |
| `qtdUsuariosPessoaJuridica` | Numeric | 0% | ✅ Limpo |
| `qtdUsuariosCadastradosDICTTotal` | Numeric | 0% | ✅ Limpo |

**Veredicto:** Dataset perfeito. Precisa apenas de renomeação de colunas para snake_case.

---

### 1.2 `EstatisticasTransacoesPix` — Volume Transacional
| Coluna | Tipo (Bronze) | Nulos | Problema |
|--------|--------------|-------|----------|
| `AnoMes` | Categorical | 0% | ⚠️ Converter para `date` (YYYY-MM-01) |
| `PAG_PFPJ` | Categorical | 0% | ✅ Valores: `PF`, `PJ`, `Nao disponivel` |
| `REC_PFPJ` | Categorical | 0% | ✅ Valores: `PF`, `PJ`, `Nao disponivel` |
| `PAG_REGIAO` | Categorical | 0% | ✅ 5 regiões + `Nao disponivel` |
| `REC_REGIAO` | Categorical | 0% | ✅ 5 regiões + `Nao disponivel` |
| `PAG_IDADE` | Categorical | 0% | ✅ 7 faixas + `Nao se aplica` (PJ) |
| `REC_IDADE` | Categorical | 0% | ✅ 7 faixas + `Nao se aplica` (PJ) |
| `FORMAINICIACAO` | Categorical | 0% | ✅ 8 formas (MANU, DICT, QRDN, QRES...) |
| `NATUREZA` | Categorical | 0% | ✅ 9 naturezas (P2P, P2B, B2P, B2B...) |
| `FINALIDADE` | Categorical | 0% | ✅ Pix, Pix Saque, Pix Troco |
| `VALOR` | **🔴 Text** | 0% | **CRÍTICO: Vírgula decimal brasileira ("9552,71"). Converter para float.** |
| `QUANTIDADE` | Numeric | 0% | ✅ Limpo |

**Veredicto:** O campo `VALOR` está como **texto** por causa da vírgula brasileira. É o problema mais crítico de toda a Bronze. Sem essa conversão, nenhuma soma ou média funciona.

---

### 1.3 `EstatisticasFraudesPix` — Segurança e Fraudes
| Coluna | Tipo (Bronze) | Nulos | Problema |
|--------|--------------|-------|----------|
| `AnoMes` | Numeric | 0% | ⚠️ Converter para `date` |
| `QtdePixcontestados` | Numeric | 0% | ✅ Limpo |
| `Qtdecontestacoesaceitas` | Numeric | 0% | ✅ Limpo |
| `Qtdecontestacoesrejeitadas` | Numeric | 0% | ✅ Limpo |
| `Qtdecontestacoesaceitasacada100mil` | **🔴 Text** | 0% | **Vírgula decimal** |
| `ValorPixcontestadosaceitos` | **🔴 Text** | 0% | **Vírgula decimal** |
| `ValorPixdevolvidosintegralmente` | **🔴 Text** | 0% | **Vírgula decimal** |
| `ValorPixdevolvidosparcialmente` | **🔴 Text** | 0% | **Vírgula decimal** |
| `ValorPixresidualnaodevolvido` | **🔴 Text** | 0% | **Vírgula decimal** |
| `ValorPixnaodevolvidossaldoinsuficiente` | **🔴 Text** | 0% | **Vírgula decimal** |
| `Valornaodevolvidoscontaencerrada` | **🔴 Text** | 0% | **Vírgula decimal** |
| `ValorPixnaodevolvidosmotivosdiversos` | **🔴 Text** | 0% | **Vírgula decimal** |
| `PercentualdeDevolucao` | **🔴 Text** | 0% | **Vírgula decimal** |
| `ValorPixbloqueadoscautelarmenteeliberados` | **🔴 Text** | 0% | **Vírgula decimal** |
| `ValorPixbloqueadoscautelarmenteedevolvidos` | **🔴 Text** | 0% | **Vírgula decimal** |

**Veredicto:** Das 24 colunas, **11 campos monetários/percentuais** estão como texto. Todos precisam de limpeza `str.replace(',', '.').astype(float)`.

**Correlações de Alerta do Profiling:**
- `QtdePixcontestados` ↔ `Qtdecontestacoesrejeitadas`: **0.98** (quase perfeita — faz sentido: quanto mais contestações, mais rejeições)
- `Qtdecontestacoesaceitas` ↔ `Quantidadedenaodevolvidossaldoinsuficiente`: **0.95** (revelador: muitos golpes aceitos não são devolvidos por falta de saldo na conta do fraudador)
- `QtdeUsuarioscommarcacoesdefraude` ↔ `QuantidadedevolvidaparcialmentepormeiodoMED`: **0.87** (o MED funciona parcialmente)

---

### 1.4 `TransacoesPixPorMunicipio` — Granularidade Geográfica
| Coluna | Tipo (Bronze) | Nulos | Problema |
|--------|--------------|-------|----------|
| `AnoMes` | Categorical | 0% | ⚠️ Converter para `date` |
| `Municipio_Ibge` | Numeric | **0.018%** | ⚠️ 1 nulo (linha genérica do BCB) |
| `Municipio` | Text | 0% | ✅ 5.299 municípios distintos |
| `Estado_Ibge` | Numeric | **0.018%** | ⚠️ 1 nulo |
| `Estado` | Categorical | 0% | ✅ 27 UFs + 1 genérico |
| `Sigla_Regiao` | Categorical | **0.018%** | ⚠️ 1 nulo |
| `VL_PagadorPF` | **🔴 Text** | 0% | **Vírgula decimal** |
| `QT_PagadorPF` | Numeric | 0% | ✅ Limpo |
| `VL_PagadorPJ` | **🔴 Text** | 0% | **Vírgula decimal** |
| `QT_PagadorPJ` | Numeric | 0% | ✅ Limpo |
| `VL_RecebedorPF` | **🔴 Text** | 0% | **Vírgula decimal** |
| `QT_RecebedorPF` | Numeric | 0% | ✅ Limpo |
| `VL_RecebedorPJ` | **🔴 Text** | 0% | **Vírgula decimal** |
| `QT_RecebedorPJ` | Numeric | 0% | ✅ Limpo |
| `QT_PES_PagadorPF` | Numeric | 0% | ✅ Limpo |
| `QT_PES_PagadorPJ` | Numeric | 0% | ✅ Limpo |
| `QT_PES_RecebedorPF` | Numeric | 0% | ✅ Limpo |
| `QT_PES_RecebedorPJ` | Numeric | 0% | ✅ Limpo |

**Veredicto:** 4 colunas de valor monetário com vírgula + 3 campos com 1 nulo geográfico (linha "Não Informado" do BCB).

---

## 2. Regras de Limpeza (Bronze → Prata)

### 2.1 Regra Global: Conversão Monetária
Todas as colunas que o Profiling identificou como `Text` mas que representam valores financeiros devem ser convertidas:
```python
df['coluna'] = df['coluna'].str.replace('.', '', regex=False)  # Remove separador de milhar
df['coluna'] = df['coluna'].str.replace(',', '.', regex=False)  # Troca vírgula por ponto
df['coluna'] = df['coluna'].astype(float)
```

### 2.2 Regra Global: Padronização de Datas
O campo `AnoMes` (ex: `202608`) deve ser convertido para `date`:
```python
df['data_referencia'] = pd.to_datetime(df['AnoMes'].astype(str), format='%Y%m')
```

### 2.3 Regra Global: Renomeação snake_case
Todas as colunas devem ser renomeadas para o padrão `snake_case` (letras minúsculas separadas por underscore):
```python
df.columns = [col.lower().replace(' ', '_') for col in df.columns]
```

### 2.4 Regra Específica: Nulos Geográficos (`TransacoesPixPorMunicipio`)
Preencher a linha nula com valores genéricos:
```python
df['municipio_ibge'].fillna(0, inplace=True)
df['estado'].fillna('NAO INFORMADO', inplace=True)
df['sigla_regiao'].fillna('NI', inplace=True)
```

### 2.5 Regra Específica: Filtro de "Não Disponível" (`EstatisticasTransacoesPix`)
As linhas com `Nao disponivel` em `NATUREZA` e `FORMAINICIACAO` (apenas 1 registro cada) devem ser removidas:
```python
df = df[df['natureza'] != 'Nao disponivel']
```

---

## 3. Tabelas da Prata (O que vamos gerar)

Após a limpeza, a Camada Prata terá as seguintes tabelas consolidadas:

| Tabela Prata | Origem Bronze | Granularidade | Volume Estimado |
|--------------|--------------|---------------|-----------------|
| `prata_adocao_pix.csv` | PixUsuariosCadastradosDICT | 1 linha/mês | ~70 linhas |
| `prata_transacoes_pix.csv` | EstatisticasTransacoesPix (todos os meses) | 1 linha/combinação demográfica/mês | ~900 mil linhas |
| `prata_fraudes_pix.csv` | EstatisticasFraudesPix (todos os meses) | 1 linha/mês | ~70 linhas |
| `prata_municipios_pix.csv` | TransacoesPixPorMunicipio (todos os meses) | 1 linha/município/mês | ~390 mil linhas |

---

## 4. Conexões e Perguntas que a Prata Responde

### Eixo 1: Explosão da Adoção
> _"Como a base de usuários do Pix cresceu mês a mês desde 2020?"_

- **Tabela:** `prata_adocao_pix`
- **Análise:** Série temporal de PF vs PJ. Calcular taxa de crescimento mensal `(mês_atual - mês_anterior) / mês_anterior`.

### Eixo 2: Substituição dos Meios de Pagamento
> _"O Pix está substituindo o cartão de débito/crédito no comércio?"_

- **Tabelas:** `prata_transacoes_pix`
- **Análise:** Filtrar por `natureza = 'P2B'` (Pessoa para Empresa = compras no comércio) e comparar a evolução do volume `valor` ao longo dos meses. Se P2B cresce mais rápido que P2P, o Pix está comendo o espaço dos cartões.

### Eixo 3: Perfil Demográfico
> _"Quem mais usa Pix? Jovens ou idosos? Nordeste ou Sudeste?"_

- **Tabelas:** `prata_transacoes_pix`
- **Análise:** Agrupar por `pag_idade` e `pag_regiao`, somar `valor` e `quantidade`. Construir heatmap de Idade × Região.

### Eixo 4: Democratização Financeira
> _"O Pix chegou nos pequenos municípios do interior?"_

- **Tabelas:** `prata_municipios_pix` + `prata_adocao_pix`
- **Análise:** Agrupar por `estado` e `regiao`, calcular o ticket médio (`vl_pagador_pf / qt_pagador_pf`). Comparar a evolução entre capitais e interior.

### Eixo 5: Segurança e Confiança
> _"As fraudes crescem proporcionalmente ao volume de transações?"_

- **Tabelas:** `prata_fraudes_pix` + `prata_transacoes_pix` (agregado mensal)
- **Análise:** Cruzar a soma mensal de `quantidade` em transações com `qtde_pix_contestados` em fraudes. Calcular o `percentual_fraudes = contestados / total_transacoes * 100`. Se o percentual cai ao longo do tempo, o sistema está ficando mais seguro.

### Eixo 6: Eficiência do MED (Mecanismo Especial de Devolução)
> _"O MED está conseguindo devolver o dinheiro das vítimas de golpes?"_

- **Tabela:** `prata_fraudes_pix`
- **Análise:** Calcular `taxa_recuperacao = (valor_devolvido_integralmente + valor_devolvido_parcialmente) / valor_contestado_aceito * 100`. A correlação do profiling (0.95 entre aceitas e não-devolvidas por saldo insuficiente) já nos diz que o dinheiro "some" rápido das contas dos fraudadores.

---

## 5. Estrutura de Diretórios da Camada Prata

```text
Projetofinal/prata/
├── etl/
│   └── src/
│       ├── limpeza_transacoes.py       # Processa estatísticas gerais Pix
│       ├── limpeza_fraudes.py          # Processa dados do MED e fraudes
│       ├── limpeza_taxa_selic.py       # Processa taxas SGS (Meta e Realizada)
│       └── limpeza_operacoes_selic.py  # Consolida operações com títulos públicos
├── data/
│   ├── pix_limpo/
│   │   ├── estatisticas_transacoes_pix.parquet (.csv)
│   │   └── estatisticas_fraudes_pix.parquet (.csv)
│   └── macro_limpo/
│       ├── taxa_selic_diaria.parquet (.csv)
│       ├── taxa_selic_mensal.parquet (.csv)
│       └── operacoes_selic.parquet (.csv)
├── analytics/
│   ├── RELATORIO_ANALISES_PRATA.md     # 📄 Dossiê executivo completo com métricas
│   ├── r_scripts/                      # Scripts em R (arrow + dplyr + ggplot2)
│   │   ├── 01_analise_transacoes.R
│   │   ├── 02_analise_fraudes.R
│   │   ├── 03_graficos_transacoes.R
│   │   ├── 04_graficos_fraudes.R
│   │   └── 05_analise_selic.R
│   └── charts/                         # Gráficos em alta resolução (300 DPI)
│       ├── pix_evolucao_temporal.png
│       ├── pix_volume_pf_pj.png
│       ├── pix_geografia.png
│       ├── fraudes_funil_med.png
│       └── fraudes_contas_laranjas.png
└── README.md
```

---

## 6. Tecnologia e Dossiê Analítico

- **Apache Parquet (Snappy)**: Formato analítico colunar padrão para consumo ultra-rápido via DuckDB e R (`arrow`).
- **CSV Replicas**: Mantidos lado a lado para integração direta com ferramentas de BI legadas.
- **Relatório Executivo de Resultados**: Para visualização detalhada de todos os números, assimetrias PF/PJ, taxas de recuperação do MED e ciclo da Selic, consulte [RELATORIO_ANALISES_PRATA.md](analytics/RELATORIO_ANALISES_PRATA.md).
