# Apresentação do Projeto Final: Pix × Custo Brasil (ECOX14)

Apresentação desenvolvida com **reveal.js** e **Chart.js** nativos, utilizando o tema **Clean Tech Claro** de alto contraste para máxima legibilidade em projetores e monitores.

---

## 📁 Estrutura Modular de Slides

Os slides foram separados individualmente para facilitar a manutenção e edição:

```text
Projetofinal/apresentacao/
├── slides/
│   ├── 01_capa.html                # Capa institucional com badges BCB e Pix
│   ├── 02_ideia_central.html       # Pergunta norteadora e eixos conceituais
│   ├── 03_arquitetura.html         # Fluxo Medalhão (Bronze ➔ Prata ➔ Ouro) metálico
│   ├── 04_problemas_bronze.html    # Diagnóstico da Bronze e Case Staircase Duplication
│   ├── 05_tabela_depara.html       # Matriz De/Para com exemplos práticos e funções
│   ├── 06_metricas_parquet.html    # Gráficos Chart.js e KPIs de compressão Parquet
│   ├── 07_resultados_nativos.html  # Curva Pix (SVG) e Funil do MED (CSS)
│   ├── 08_macro_selic.html         # Resultados Macroeconômicos: Taxa Selic & Mercado Aberto
│   └── 09_roadmap_ouro.html        # Modelagem relacional da Camada Ouro e Checklist
├── compilar.py                     # Script Python para empacotar index_offline.html (modo offline)
├── ROTEIRO_APRESENTACAO.md         # Guia completo do apresentador e respostas para a banca
├── css/
│   └── custom.css                  # Estilos do tema Clean Tech Claro
├── js/
│   └── graficos.js                 # Inicialização dos gráficos no tema claro
├── data/
│   ├── metricas.json
│   └── metricas.js
├── index.html                      # Carregador dinâmico modular (Live Server / HTTP)
└── index_offline.html              # Apresentação consolidada para duplo clique (file://)
```

---

## ⚡ Como Apresentar e Editar

### Modo Principal: Live Server (Sem precisar compilar!)
Como você usa a extensão **Live Server** no VS Code:
1. Abra a pasta no VS Code.
2. Clique com o botão direito em `index.html` $\rightarrow$ **"Open with Live Server"** (ou clique no botão **"Go Live"** no rodapé).
3. Qualquer alteração salva em qualquer arquivo da pasta `slides/*.html` é **recarregada automaticamente no navegador**, sem precisar rodar nenhum comando!

### Modo Portátil / Offline (Duplo clique sem servidor):
Se precisar levar a apresentação em um pendrive ou abrir sem Live Server:
1. Execute:
   ```bash
   py Projetofinal/apresentacao/compilar.py
   ```
2. Um arquivo `index_offline.html` monolítico será gerado, pronto para ser aberto diretamente com duplo clique (`file://`).


---

## ⌨️ Atalhos de Apresentação

| Tecla | Ação |
|---|---|
| `→` ou `Espaço` | Avançar para o próximo slide |
| `←` | Voltar para o slide anterior |
| `S` | Modo apresentador (com cronômetro e notas) |
| `F` | Alternar modo tela cheia |
| `Esc` | Visão geral de todos os slides |

**Exportação para PDF:** Abra `index.html?print-pdf` no Google Chrome $\rightarrow$ `Ctrl + P` $\rightarrow$ Salvar como PDF.
