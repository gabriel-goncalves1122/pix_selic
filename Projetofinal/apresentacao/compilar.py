#!/usr/bin/env python3
"""
compilar.py
Concatena os arquivos modulares de slides/*.html no index.html final.
Permite editar cada slide separadamente e abrir o index.html via file:// sem travas de CORS.
"""
from pathlib import Path

DIR = Path(__file__).parent
SLIDES_DIR = DIR / "slides"
OUTPUT_FILE = DIR / "index.html"

HTML_TEMPLATE = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pix × Custo Brasil — Projeto Final ECOX14</title>
  <link rel="stylesheet" href="vendor/reveal.js/dist/reset.css">
  <link rel="stylesheet" href="vendor/reveal.js/dist/reveal.css">
  <link rel="stylesheet" href="vendor/reveal.js/dist/theme/white.css">
  <link rel="stylesheet" href="css/custom.css">
</head>
<body>
<div class="reveal"><div class="slides">

{SLIDES_CONTENT}

</div></div>

<script src="vendor/reveal.js/dist/reveal.js"></script>
<script src="vendor/reveal.js/plugin/notes/notes.js"></script>
<script src="vendor/chart.umd.min.js"></script>
<script src="data/metricas.js"></script>
<script>
  Reveal.initialize({
    hash: true,
    slideNumber: 'c/t',
    width: 1280,
    height: 720,
    margin: 0.05,
    transition: 'fade',
    plugins: [RevealNotes]
  });
</script>
<script src="js/graficos.js"></script>
</body>
</html>
"""


def compilar():
    slide_files = sorted(SLIDES_DIR.glob("*.html"))
    if not slide_files:
        print("Nenhum slide encontrado em slides/")
        return

    print(f"Compilando {len(slide_files)} slides...")
    conteudos = []
    for sf in slide_files:
        print(f" -> Incluindo: {sf.name}")
        conteudos.append(f"  <!-- {sf.name} -->\n" + sf.read_text(encoding="utf-8").strip())

    slides_content = "\n\n".join(conteudos)
    final_html = HTML_TEMPLATE.replace("{SLIDES_CONTENT}", slides_content)

    OUTPUT_FILE.write_text(final_html, encoding="utf-8")
    print(f"\n✓ Sucesso! Arquivo compilado em: {OUTPUT_FILE.name}")


if __name__ == "__main__":
    compilar()
