# ECOX14 — Engenharia de Dados (UNIFEI)

Repositório central das atividades, práticas de laboratório e projeto integrador da disciplina **ECOX14 — Engenharia de Dados**, ministrada na **Universidade Federal de Itajubá (UNIFEI)**.

---

## 🏛️ Estrutura do Repositório

O projeto é estruturado em dois grandes módulos:

```text
TRABALHO/
├── Aula/                       # Módulo 1: Laboratórios e Práticas de Sala
│   ├── aulas/                  # Slides e materiais teóricos (PDFs)
│   ├── dados/                  # Data Lake local (Bronze, Prata, Ouro)
│   ├── scripts/                # Scripts de ingestão (Kaggle Spotify & Banco Mundial)
│   ├── requirements.txt        # Dependências específicas dos exercícios de aula
│   └── README.md               # Instruções de execução do módulo de aula
│
├── Projetofinal/               # Módulo 2: Projeto Integrador (Pix × Custo Brasil)
│   ├── docs/                   # Especificações, catálogo de APIs e entregas acadêmicas
│   │   ├── entregas/           # Documentos formais de entrega da disciplina (Word/PDF)
│   │   └── scripts/            # Scripts de exploração e mapeamento de metadados
│   ├── bronze/                 # Camada Bronze: Ingestão de APIs Olinda e SGS (BCB)
│   │   ├── analytics/          # EDA e relatórios de profiling de dados brutos
│   │   └── etl/src/            # Pipelines modulares de ingestão (Pix e Macro)
│   ├── prata/                  # Camada Prata: Higienização, tipagem e exportação Parquet
│   │   ├── analytics/          # Scripts estatísticos em R, relatórios e gráficos
│   │   └── etl/src/            # Pipelines de transformação e enriquecimento
│   ├── ouro/                   # Camada Ouro: Modelagem analítica (Star Schema)
│   ├── apresentacao/           # Deck de slides interativo em Reveal.js + Chart.js
│   │   ├── slides/             # Slides modulares em HTML puro
│   │   ├── ROTEIRO_APRESENTACAO.md  # Guia completo do apresentador e respostas para banca
│   │   ├── index.html          # Apresentação dinâmica via Live Server
│   │   └── index_offline.html  # Apresentação compilada monolítica (duplo clique)
│   ├── requirements.txt        # Dependências completas de produção do projeto
│   └── README.md               # Detalhamento técnico do Projeto Final
│
├── .gitignore                  # Regras de exclusão de dados brutos, caches e credenciais
└── README.md                   # Este guia executivo
```

---

## 🎯 Projeto Final: Pix × "Custo Brasil"

O projeto final investiga como a explosão transacional do **Pix** impactou os meios tradicionais de pagamento e como essa dinâmica se correlaciona com indicadores macroeconômicos brasileiros (Taxa Selic e inflação), utilizando uma **Arquitetura Medalhão** resiliente.

### 🔗 Acessos Rápidos da Apresentação e Documentação
- 📊 **[Slides da Apresentação (Reveal.js)](Projetofinal/apresentacao/README.md)**
- 🎤 **[Roteiro do Apresentador & Guia da Banca](Projetofinal/apresentacao/ROTEIRO_APRESENTACAO.md)**
- 📑 **[Relatório Técnico da Camada Prata](Projetofinal/prata/analytics/RELATORIO_ANALISES_PRATA.md)**
- 🗺️ **[Catálogo de APIs Olinda & SGS](Projetofinal/docs/catalogo_olinda.md)**
- 🎓 **[Entregas Acadêmicas Formais](Projetofinal/docs/entregas/)**

---

## 🛠️ Stack Tecnológica

| Camada / Função | Tecnologias |
|---|---|
| **Linguagens** | Python 3.12+, R 4.x, JavaScript (ES6+), HTML5 / CSS3 |
| **Ingestão & APIs** | `requests`, OData / REST APIs (Banco Central do Brasil, Banco Mundial, Kaggle) |
| **Processamento & Data Lake** | `pandas`, `pyarrow`, `fastparquet` (Formato Apache Parquet com compressão Snappy) |
| **Exploração & Qualidade** | `fg-data-profiling` / `ydata-profiling` |
| **Apresentação & Visualização** | Reveal.js, Chart.js, SVG vetorial responsivo, `ggplot2` (R) |

---

## 🚀 Como Executar

### 1. Criar e Ativar Ambiente Virtual
```bash
python -m venv .venv

# No Windows (PowerShell):
.venv\Scripts\Activate.ps1

# No Linux / macOS:
source .venv/bin/activate
```

### 2. Instalar Dependências do Projeto Final
```bash
pip install -r Projetofinal/requirements.txt
```

### 3. Rodar a Apresentação
- **Modo Recomendado (Live Server):** Abra o VS Code nesta pasta raiz, clique com botão direito em `Projetofinal/apresentacao/index.html` $\rightarrow$ **Open with Live Server**.
- **Modo Portátil (Duplo Clique):** Dê um duplo clique no arquivo compilado `Projetofinal/apresentacao/index_offline.html` para abrir diretamente no navegador sem precisar de servidor.
