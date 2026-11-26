// js/graficos.js — Gráficos Antes × Depois a partir de data/metricas.js (Tema Clean Tech Claro)
window._graficosCharts = window._graficosCharts || {};

window.desenharGraficosSlide6 = function () {
  const M = window.METRICAS;
  if (!M) return;
  if (typeof Chart === 'undefined') return;

  const titulos = {
    pix: 'Ecossistema Pix (Transações + Fraudes)',
    macro: 'Ecossistema Macro (SGS + Operações)'
  };

  const desenhar = (id, ds) => {
    const el = document.getElementById(id);
    if (!el) return;
    const d = (M.datasets && M.datasets[ds]) || M[ds];
    if (!d) return;

    if (window._graficosCharts[id]) {
      window._graficosCharts[id].destroy();
    }

    window._graficosCharts[id] = new Chart(el, {
      type: 'bar',
      data: {
        labels: ['Texto (string)', 'Numéricas (tipadas)'],
        datasets: [
          { label: 'Bronze (Original)', data: [d.bronze.texto, d.bronze.numericas], backgroundColor: '#ef4444', borderRadius: 4 },
          { label: 'Prata (Higienizada)', data: [d.prata.texto, d.prata.numericas], backgroundColor: '#008779', borderRadius: 4 },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: { duration: 300 },
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 8, padding: 4, font: { size: 9, weight: '600' } } },
          title: {
            display: true,
            text: titulos[ds] || ds,
            color: '#003366',
            padding: { top: 0, bottom: 4 },
            font: { size: 11, weight: '700' }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { font: { size: 9 } } },
          y: { grid: { color: '#f1f5f9' }, beginAtZero: true, ticks: { font: { size: 9 } } }
        }
      },
    });
  };

  desenhar('c-pix', 'pix');
  desenhar('c-macro', 'macro');
};

window.iniciarGraficos = function () {
  const M = window.METRICAS;
  if (!M) return;

  if (typeof Chart !== 'undefined') {
    Chart.defaults.color = '#334155';
    Chart.defaults.font.size = 11;
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
  }

  const fmt = (n) => n.toLocaleString('pt-BR');
  document.querySelectorAll('[data-m]').forEach((el) => {
    const v = el.dataset.m.split('.').reduce((o, k) => o?.[k], M);
    if (v !== undefined) el.textContent = typeof v === 'number' ? fmt(v) : v;
  });

  const checarSlide = () => {
    if (typeof Reveal === 'undefined') return;
    const s = Reveal.getCurrentSlide();
    if (s && s.id === 'antes-depois') {
      window.desenharGraficosSlide6();
    }
  };

  if (typeof Reveal !== 'undefined') {
    Reveal.on('slidechanged', (e) => {
      if (e.currentSlide && e.currentSlide.id === 'antes-depois') {
        window.desenharGraficosSlide6();
      }
    });

    if (typeof Reveal.isReady === 'function' && Reveal.isReady()) {
      checarSlide();
    } else {
      Reveal.on('ready', checarSlide);
    }
  }
};

// Executa em múltiplos momentos de ciclo de vida para garantir
window.iniciarGraficos();
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', window.iniciarGraficos);
}
window.addEventListener('load', window.iniciarGraficos);
