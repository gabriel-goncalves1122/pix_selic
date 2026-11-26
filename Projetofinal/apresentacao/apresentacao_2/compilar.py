#!/usr/bin/env python3
"""
compilar.py (Apresentacao 2)
Compila css/slides_v2.css + slides/*.html nos arquivos autocontidos index.html e index_offline.html.
"""
from pathlib import Path
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

DIR = Path(__file__).parent
SLIDES_DIR = DIR / "slides"
CSS_FILE = DIR / "css" / "slides_v2.css"
OUTPUT_FILES = [DIR / "index.html", DIR / "index_offline.html"]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Radiografia do Pix no Brasil — Parte II (ECOX14)</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=JetBrains+Mono:wght@500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
{CSS_CONTENT}
  </style>
</head>
<body>
  <button class="edit-pill" id="editToggle" title="Atalho: tecla E">Editar (E)</button>

  <div class="deck-viewport">
    <main class="deck-stage" id="deckStage">
{SLIDES_CONTENT}
    </main>
  </div>

  <script>
    class SlideDeck {
      constructor() {
        this.slides = Array.from(document.querySelectorAll('.slide'));
        this.stage = document.getElementById('deckStage');
        this.current = 0;
        this.setupScale();
        this.setupNav();
        this.setupTouch();
        this.setupErd();
        this.setupInlineEdit();
        this.showSlide(0);
      }

      setupScale() {
        const update = () => {
          const f = Math.min(window.innerWidth / 1920, window.innerHeight / 1080);
          const x = (window.innerWidth - 1920 * f) / 2;
          const y = (window.innerHeight - 1080 * f) / 2;
          this.stage.style.transform = `translate(${x}px, ${y}px) scale(${f})`;
        };
        update();
        window.addEventListener('resize', update);
      }

      setupNav() {
        window.addEventListener('keydown', (e) => {
          if (document.body.classList.contains('editing') && e.key !== 'Escape') return;
          if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') {
            e.preventDefault();
            this.showSlide(this.current + 1);
          } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
            e.preventDefault();
            this.showSlide(this.current - 1);
          } else if (e.key === 'Home') {
            this.showSlide(0);
          } else if (e.key === 'End') {
            this.showSlide(this.slides.length - 1);
          } else if (e.key.toLowerCase() === 'e') {
            this.toggleEdit();
          }
        });
      }

      setupTouch() {
        let startX = 0;
        window.addEventListener('touchstart', (e) => { startX = e.touches[0].clientX; }, { passive: true });
        window.addEventListener('touchend', (e) => {
          const dx = e.changedTouches[0].clientX - startX;
          if (Math.abs(dx) > 50) this.showSlide(this.current + (dx < 0 ? 1 : -1));
        }, { passive: true });
      }

      setupErd() {
        const erd = document.getElementById('erdStage');
        if (!erd) return;
        const facts = erd.querySelectorAll('.erd-fact');
        const items = erd.querySelectorAll('[data-facts]');
        facts.forEach((f) => {
          const key = f.getAttribute('data-fact');
          f.addEventListener('mouseenter', () => {
            erd.classList.add('has-hover');
            items.forEach((el) => {
              const list = (el.getAttribute('data-facts') || '').split(' ');
              el.classList.toggle('is-active', list.includes(key));
            });
          });
          f.addEventListener('mouseleave', () => {
            erd.classList.remove('has-hover');
            items.forEach((el) => el.classList.remove('is-active'));
          });
        });
      }

      setupInlineEdit() {
        const btn = document.getElementById('editToggle');
        if (btn) btn.addEventListener('click', () => this.toggleEdit());
      }

      toggleEdit() {
        const on = !document.body.classList.contains('editing');
        document.body.classList.toggle('editing', on);
        const btn = document.getElementById('editToggle');
        if (btn) btn.textContent = on ? 'Salvar (Ctrl+S) / Sair (E)' : 'Editar (E)';
        document.querySelectorAll('.slide h1, .slide h2, .slide p, .slide .kpi-num, .slide .kpi-title, .slide .kpi-sub, .slide .topic-title, .slide .topic-desc, .slide .author-name, .slide .author-url, .slide .step-name, .slide .step-desc')
          .forEach((el) => el.setAttribute('contenteditable', on ? 'true' : 'false'));
      }

      showSlide(idx) {
        this.current = Math.max(0, Math.min(idx, this.slides.length - 1));
        this.slides.forEach((s, i) => {
          const active = i === this.current;
          s.classList.toggle('active', active);
          s.classList.toggle('visible', active);
        });
      }
    }

    new SlideDeck();
  </script>
</body>
</html>
"""


def compilar():
    slide_files = sorted(SLIDES_DIR.glob("*.html"))
    if not slide_files:
        print("Nenhum slide encontrado em slides/")
        return

    css_content = CSS_FILE.read_text(encoding="utf-8")
    conteudos = []
    print(f"Compilando {len(slide_files)} slides da Apresentacao 2...")
    for sf in slide_files:
        print(f" -> Incluindo: {sf.name}")
        conteudos.append(sf.read_text(encoding="utf-8").strip())

    final_html = (
        HTML_TEMPLATE.replace("{CSS_CONTENT}", css_content)
        .replace("{SLIDES_CONTENT}", "\n\n".join(conteudos))
    )
    for out in OUTPUT_FILES:
        out.write_text(final_html, encoding="utf-8")
        print(f"✓ Gerado: {out.name}")


if __name__ == "__main__":
    compilar()
