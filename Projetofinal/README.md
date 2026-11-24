# Projeto Final — Engenharia de Dados (ECOX14)

## Tema

**Análise do "Custo Brasil" financeiro através da evolução e adoção do Pix cruzada com indicadores macroeconômicos (Selic e IPCA) e segurança (MED).**

### Pergunta Norteadora

> Como a adoção em massa do Pix evoluiu entre Pessoa Física e Pessoa Jurídica e qual é a relação dessa dinâmica com a inflação (IPCA), a taxa básica de juros (Selic) e os indicadores de fraude/contestação (MED)?

---

## Modelagem Dimensional — Camada Ouro (Esquema Estrela)

1. **Tabelas no schema `ouro` (`dados/ouro/projeto.duckdb`):**
   - `dim_tempo` — calendário mensal (`ano_mes`, `data_mes`, `ano`, `mes`, `trimestre`, `ano_trimestre`, `periodo_label`).
   - `dim_natureza_pix` — combinações de `natureza`, `finalidade` e `formainiciacao` (`natureza_id`).
   - `dim_regiao` — regiões geográficas pagadoras/recebedoras (`regiao_id`).
   - `dim_faixa_etaria` — faixas etárias ordenadas (`idade_id`, `ordem_etaria`).
   - `dim_funcao_cartao` — meios de pagamento trimestrais (`Pix`, `Crédito`, `Débito`, `Pré-Pago`).
   - `fato_pix_macro_mensal` — fato principal consolidando Pix (nominal e deflacionado), Meios Tradicionais (TED, Boleto, Cheque, DOC), Funil MED completo, Contas Laranjas, DICT, Selic, IPCA e Juro Real.
   - `fato_pix_segmentado_mensal` — fato detalhada por segmento econômico e perfil PF/PJ.
   - `fato_pix_regional_mensal` — matriz mensal de fluxos pagador → recebedor por região.
   - `fato_pix_etario_mensal` — adoção mensal do Pix por faixa etária.
   - `fato_cartoes_vs_pix_trimestral` — comparação trimestral direta entre Pix, Crédito, Débito e Pré-Pago.
   - Views analíticas: `vw_pix_macro_completo`, `vw_pix_regional_fluxo`, `vw_pix_etario`, `vw_cartoes_vs_pix_trimestral`.

2. **Declaração do Grão:**
   - **`fato_pix_macro_mensal`:** *Uma linha é um mês de referência (`ano_mes`).*
   - **`fato_pix_segmentado_mensal`:** *Uma linha é `(ano_mes, natureza_id, pag_pfpj, rec_pfpj)`.*
   - **`fato_pix_regional_mensal`:** *Uma linha é `(ano_mes, pag_regiao_id, rec_regiao_id)`.*
   - **`fato_pix_etario_mensal`:** *Uma linha é `(ano_mes, idade_id)`.*
   - **`fato_cartoes_vs_pix_trimestral`:** *Uma linha é `(trimestre, funcao_id)`.*

3. **Relacionamentos:**
   - Todas as fatos mensais ligam-se a `dim_tempo.ano_mes`; `fato_pix_segmentado_mensal` liga-se a `dim_natureza_pix`; `fato_pix_regional_mensal` liga-se a `dim_regiao` (pagador/recebedor); `fato_pix_etario_mensal` liga-se a `dim_faixa_etaria`; `fato_cartoes_vs_pix_trimestral` liga-se a `dim_funcao_cartao`.

---

## Arquitetura do Projeto

```text
Projetofinal/
├── src/                # Pipeline Python (config.py, pipeline.py, carga.py, ingestao/, transformacao/)
├── dados/              # Dados locais: bronze/, prata/ e ouro/projeto.duckdb
├── ecox14_pix/         # Projeto dbt (modelos SQL, schema.yml, testes singulares)
├── dashboard/          # Painel Streamlit (consultas.py read_only=True + painel.py)
├── tests/              # Testes unitários Python (pytest)
├── analises/           # Profiling, scripts R e gráficos exploratórios
├── apresentacao/       # Slides Reveal.js da apresentação final
└── docs/               # Documentação técnica (arquitetura/, fontes/, entregas/, scripts/)
```

---

## Como Rodar

```bash
# 1. Sincronizar ambiente com uv
uv sync --link-mode=copy

# 2. Rodar o pipeline completo (Ingestão -> Prata -> Enriquecimento -> DuckDB -> dbt run & test)
uv run python src/pipeline.py

# Ou retomar a partir de uma etapa específica:
uv run python src/pipeline.py transformacao

# 3. Rodar testes unitários Python
uv run pytest -v

# 4. Abrir documentação viva do dbt
cd ecox14_pix && uv run dbt docs serve

# 5. Abrir o Dashboard Streamlit
uv run streamlit run dashboard/painel.py
```

---

## Documentação Técnica (`docs/`)

- **Arquitetura e Qualidade:**
  - [Decisões de Tratamento e Atributos Derivados](docs/arquitetura/decisoes_tratamento.md)
  - [Estudo de Caso: Granularidade e Duplicação em Escada no Pix](docs/arquitetura/CASE_GRANULARIDADE_PIX.md)
- **Fontes de Dados (Banco Central):**
  - [Catálogo Olinda API](docs/fontes/catalogo_olinda.md)
  - [Relatório Datasets SGS](docs/fontes/datasets_sgs_bcb.md)
- **Entregas Formais:** [Documento Inicial (PDF)](docs/entregas/DocumentoInicial.pdf)
