/* predictor.js — AI Demand Forecasting logic + Chart.js line chart */

Chart.defaults.color = '#8b8b9e';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'DM Sans', sans-serif";

let forecastChart = null;

/* ── Boot ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const token = requireAuth();
  if (!token) return;
  const username = localStorage.getItem('username') || 'User';
  const el = document.getElementById('nav-username');
  if (el) el.textContent = username;
  loadProducts();
});

/* ── Load product list ──────────────────────────────────────── */
async function loadProducts() {
  show('loading-products');
  hide('no-data-state');
  hide('error-state');
  hide('predictor-main');

  try {
    const res = await apiFetch('/api/products');
    if (!res) return;

    if (!res.ok) {
      const err = await res.json();
      showError(err.detail || 'Failed to load products.');
      return;
    }

    const { products } = await res.json();

    if (!products || products.length === 0) {
      hide('loading-products');
      show('no-data-state');
      return;
    }

    // Populate dropdown
    const select = document.getElementById('product-select');
    products.forEach(p => {
      const opt = document.createElement('option');
      opt.value = p; opt.textContent = p;
      select.appendChild(opt);
    });

    hide('loading-products');
    show('predictor-main');

  } catch (err) {
    showError(`Network error: ${err.message}. Is the API server running?`);
  }
}

/* ── Run prediction ─────────────────────────────────────────── */
async function runPrediction() {
  const select  = document.getElementById('product-select');
  const product = select.value;
  if (!product) return;

  show('prediction-content');
  show('loading-prediction');
  hide('prediction-error');
  hide('prediction-results');

  try {
    const res = await apiFetch(`/api/predict?product=${encodeURIComponent(product)}`);
    if (!res) return;

    if (!res.ok) {
      hide('loading-prediction');
      const err = await res.json();
      showPredictionError(err.detail || 'Prediction failed.');
      return;
    }

    const data = await res.json();
    renderResults(data);

    hide('loading-prediction');
    show('prediction-results');

  } catch (err) {
    hide('loading-prediction');
    showPredictionError(`Prediction failed: ${err.message}`);
  }
}

/* ── Render prediction results ──────────────────────────────── */
function renderResults(data) {
  // KPI cards
  document.getElementById('kpi-forecast').textContent = `${Number(data.total_predicted).toLocaleString()} units`;
  document.getElementById('kpi-source').textContent   = data.model_source || 'User Database';

  const trendMap = { up: '📈 Trending Up', down: '📉 Trending Down', flat: '➡️ Stable' };
  const kpiTrend = document.getElementById('kpi-trend');
  kpiTrend.textContent = trendMap[data.trend] || '➡️ Stable';
  kpiTrend.className   = 'metric-value ' + (data.trend === 'up' ? 'teal' : data.trend === 'down' ? '' : 'gold');
  if (data.trend === 'down') kpiTrend.style.color = 'var(--accent-red)';
  else kpiTrend.style.color = '';

  // Stats badges
  document.getElementById('stat-bestday').textContent = data.best_day || 'N/A';
  document.getElementById('stat-mae').textContent     = data.mae?.toFixed(2) ?? 'N/A';
  document.getElementById('stat-r2').textContent      = data.r2_score?.toFixed(4) ?? 'N/A';

  // Chart label
  const chartLabel = document.getElementById('chart-label');
  if (chartLabel) chartLabel.textContent = `📈 30-Day Sales Trajectory — ${data.product}`;

  // Render chart
  renderForecastChart(data);
}

/* ── Chart.js line chart ────────────────────────────────────── */
function renderForecastChart(data) {
  if (forecastChart) forecastChart.destroy();

  const ctx = document.getElementById('forecast-chart').getContext('2d');

  const hist    = data.historical;
  const forecast= data.forecast;

  // Build datasets
  // The last historical point connects to first forecast point for visual continuity
  const bridgeDate = hist.dates[hist.dates.length - 1];
  const bridgeQty  = hist.qty[hist.qty.length - 1];

  forecastChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [...hist.dates, ...forecast.dates],
      datasets: [
        // Confidence band (filled area)
        {
          label: 'Upper Band',
          data: [...Array(hist.dates.length).fill(null), ...forecast.qty.map((v,i) => forecast.upper[i])],
          borderColor: 'rgba(56,232,197,0)',
          backgroundColor: 'rgba(56,232,197,0.08)',
          fill: true,
          pointRadius: 0,
          tension: 0.4,
          order: 3,
        },
        {
          label: 'Lower Band',
          data: [...Array(hist.dates.length).fill(null), ...forecast.qty.map((v,i) => forecast.lower[i])],
          borderColor: 'rgba(56,232,197,0)',
          backgroundColor: 'rgba(56,232,197,0.08)',
          fill: '-1',
          pointRadius: 0,
          tension: 0.4,
          order: 3,
        },
        // Historical actuals (purple)
        {
          label: 'Your DB Sales',
          data: [...hist.qty, null],
          borderColor: '#7c6dfa',
          backgroundColor: 'rgba(124,109,250,0.1)',
          borderWidth: 2.5,
          pointRadius: 4,
          pointBackgroundColor: '#7c6dfa',
          pointBorderColor: 'rgba(124,109,250,0.3)',
          pointBorderWidth: 4,
          tension: 0.3,
          order: 1,
        },
        // AI Forecast (teal dashed)
        {
          label: 'AI Forecast',
          data: [...Array(hist.dates.length - 1).fill(null), bridgeQty, ...forecast.qty],
          borderColor: '#38e8c5',
          backgroundColor: 'rgba(56,232,197,0.05)',
          borderWidth: 2.5,
          borderDash: [6, 4],
          pointRadius: 4,
          pointBackgroundColor: '#38e8c5',
          pointBorderColor: 'rgba(56,232,197,0.3)',
          pointBorderWidth: 4,
          tension: 0.3,
          fill: false,
          order: 2,
        },
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            padding: 16,
            usePointStyle: true,
            filter: item => !['Upper Band','Lower Band'].includes(item.text),
          }
        },
        tooltip: {
          backgroundColor: 'rgba(3,4,10,0.92)',
          borderColor: 'rgba(255,255,255,.1)',
          borderWidth: 1,
          padding: 12,
          filter: item => !['Upper Band','Lower Band'].includes(item.dataset.label),
          callbacks: {
            label: ctx => {
              if (['Upper Band','Lower Band'].includes(ctx.dataset.label)) return null;
              return ` ${ctx.dataset.label}: ${ctx.raw !== null ? Number(ctx.raw).toLocaleString() + ' units' : 'N/A'}`;
            }
          }
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: {
            maxTicksLimit: 12,
            maxRotation: 30,
          }
        },
        y: {
          grid: { color: 'rgba(255,255,255,0.04)' },
          ticks: { callback: v => Number(v).toLocaleString() },
          title: { display: true, text: 'Quantity Sold', color: '#555567' }
        }
      }
    }
  });
}

/* ── Utility ────────────────────────────────────────────────── */
function show(id) { const el=document.getElementById(id); if(el) el.style.display=''; }
function hide(id) { const el=document.getElementById(id); if(el) el.style.display='none'; }

function showError(msg) {
  hide('loading-products');
  const el = document.getElementById('error-msg');
  if (el) el.textContent = msg;
  show('error-state');
}

function showPredictionError(msg) {
  const el = document.getElementById('prediction-error');
  if (!el) return;
  el.innerHTML = `❌ ${msg}`;
  el.style.display = 'flex';
}
