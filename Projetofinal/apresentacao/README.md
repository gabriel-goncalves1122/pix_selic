# Apresentações do Projeto (ECOX14)

- **`apresentacao_1/`** — Parte I (Ingestão Bronze, Limpeza Prata e Roadmap Ouro), baseada em Reveal.js (`css/custom.css` e `vendor/`).
- **`apresentacao_2/`** — Parte II / Entrega Final N2 (*Radiografia do Pix no Brasil*), estruturada em palco fixo `1920×1080` com slides modulares:
  - `slides/01_capa.html` a `05_qualidade_e_consumo.html`
  - `css/slides_v2.css`
  - `compilar.py`: gera `index.html` e `index_offline.html` autocontidos.

## Como recompilar a Apresentação 2

```powershell
uv run python apresentacao/apresentacao_2/compilar.py
```
