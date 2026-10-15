// Gráficos Antes × Depois a partir de data/metricas.js (Tema Clean Tech Claro)
(function () {
  const M = window.METRICAS;
  if (!M) { console.warn('metricas.js não carregado'); return; }
  
  Chart.defaults.color = '#334155';
  Chart.defaults.font.size = 14;
  Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

  const fmt = (n) => n.toLocaleString('pt-BR');
  document.querySelectorAll('[data-m]').forEach((el) => {
    const v = el.dataset.m.split('.').reduce((o, k) => o?.[k], M);
    if (v !== undefined) el.textContent = typeof v === 'number' ? fmt(v) : v;
  });

  const desenhar = (id, ds) => {
    const d = M.datasets[ds];
    new Chart(document.getElementById(id), {
      type: 'bar',
      data: {
        labels: ['Colunas texto (string)', 'Colunas numéricas (tipadas)'],
        datasets: [
          { label: 'Bronze (Original)', data: [d.bronze.texto, d.bronze.numericas], backgroundColor: '#ef4444', borderRadius: 4 },
          { label: 'Prata (Higienizada)', data: [d.prata.texto, d.prata.numericas], backgroundColor: '#008779', borderRadius: 4 },
        ],
      },
      options: {
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'top', labels: { boxWidth: 12, font: { weight: '600' } } },
          title: {
            display: true,
            text: ds === 'fraudes' ? 'Dataset Fraudes (MED) — 24 Colunas' : 'Dataset Transações — Amostra Demográfica',
            color: '#003366',
            font: { size: 14, weight: '700' }
          }
        },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { color: '#f1f5f9' }, beginAtZero: true }
        }
      },
    });
  };

  let feito = false;
  const checar = () => {
    const s = Reveal.getCurrentSlide();
    if (!feito && s && s.id === 'antes-depois') {
      desenhar('c-fraudes', 'fraudes');
      desenhar('c-trans', 'transacoes');
      feito = true;
    }
  };

  Reveal.on('slidechanged', (e) => {
    if (!feito && e.currentSlide.id === 'antes-depois') {
      desenhar('c-fraudes', 'fraudes');
      desenhar('c-trans', 'transacoes');
      feito = true;
    }
  });

  Reveal.isReady() ? checar() : Reveal.on('ready', checar);
})();
