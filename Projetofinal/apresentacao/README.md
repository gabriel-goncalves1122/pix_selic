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
│   └── 08_roadmap_ouro.html        # Modelagem relacional da Camada Ouro e Checklist
├── compilar.py                     # Script Python para montar o index.html final
├── css/
│   └── custom.css                  # Estilos do tema Clean Tech Claro
├── js/
│   └── graficos.js                 # Inicialização dos gráficos no tema claro
├── data/
│   ├── metricas.json
│   └── metricas.js
└── index.html                      # Apresentação compilada pronta para exibição
```

---

## ⚡ Como Editar e Compilar

1. **Edite o slide desejado:** Modifique diretamente o arquivo correspondente dentro da pasta `slides/` (ex: `slides/05_tabela_depara.html`).
2. **Compile a apresentação:**
   ```bash
   python3 Projetofinal/apresentacao/compilar.py
   ```
3. **Abra no Navegador:**
   - Basta dar **duplo clique** em `Projetofinal/apresentacao/index.html` (funciona 100% offline via `file://`).
   - Ou via servidor local:
     ```bash
     python3 -m http.server -d Projetofinal/apresentacao 8000
     ```

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
