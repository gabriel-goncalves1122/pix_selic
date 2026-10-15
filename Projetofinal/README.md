# Projeto Final — Engenharia de Dados (ECOX14)

## Tema

**Análise do "Custo Brasil" financeiro através da evolução e adoção dos meios de pagamento (Pix vs Cartões) cruzada com indicadores macroeconômicos.**

### Pergunta Norteadora

> Como a adoção em massa do Pix impactou os volumes transacionais de outros meios de pagamento tradicionais e qual é a correlação dessa dinâmica com a inflação (IPCA) e a taxa básica de juros (Selic)?

---

## Arquitetura do Projeto (Medalhão)

```text
Projetofinal/
├── docs/             # Catálogos de APIs e Documentação das Fontes
├── bronze/           # Camada Bronze — Dados brutos
│   ├── analytics/    # Análises exploratórias iniciais dos dados brutos
│   ├── etl/src/      # Scripts modulares de extração (Python)
│   └── raw/          # JSONs extraídos (estoque bruto)
├── prata/            # Camada Silver — Dados limpos e padronizados
├── ouro/             # Camada Gold — Dados agregados para dashboard
└── data/             # Dados e Dicionários auxiliares
```

---

## Fonte de Dados

O projeto consome dados de APIs abertas. A documentação com o catálogo dos endpoints explorados encontra-se na pasta `docs`.

👉 **Documentações Técnicas:** 
- [Catálogo Olinda API](docs/catalogo_olinda.md)
- [Relatório Datasets Banco Central](docs/datasets_sgs_bcb.md)

---

## Como Rodar

Para executar a ingestão sem sobrecarregar o Banco Central, criamos um orquestrador com lógica de _Checkpoint_ e _Heavy Retry_:

```bash
# Ativar o ambiente virtual
source venv/bin/activate

# 1. Rodar orquestrador Pix
bash Projetofinal/bronze/etl/src/pix/orquestrador_pix.sh

# 2. Rodar orquestrador Macro
bash Projetofinal/bronze/etl/src/macro/orquestrador_macro.sh
```

Os dados brutos serão salvos em `Projetofinal/bronze/raw/pix` organizados por serviço, acompanhados de arquivos `proveniencia.json` para rastreabilidade de linhagem.

---

## Pré-requisitos

- Python 3.12+
- `requests` (`pip install requests`)
- `pandas` (`pip install pandas`)
