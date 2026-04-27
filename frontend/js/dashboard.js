/* dashboard.js — Data fetching, Chart.js charts, DB demo buttons */

/* Chart.js global defaults for dark theme */
Chart.defaults.color = '#8b8b9e';
Chart.defaults.borderColor = 'rgba(255,255,255,0.06)';
Chart.defaults.font.family = "'DM Sans', sans-serif";

let barChart = null;
let pieChart = null;

/* ── Boot ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const token = requireAuth();
  if (!token) return;

  // Set username in navbar
  const username = localStorage.getItem('username') || 'User';
  const el = document.getElementById('nav-username');
  if (el) el.textContent = username;

  loadDashboard();
});

/* ── Load dashboard data ────────────────────────────────────── */
async function loadDashboard() {
  show('loading-state');
  hide('error-state');
  hide('empty-state');
  hide('dashboard-main');

  try {
    const res = await apiFetch('/api/dashboard');
    if (!res) return; // redirected to login
    if (!res.ok) {
      const err = await res.json();
      showErrorState(err.detail || 'Failed to load data.');
      return;
    }
    const payload = await res.json();

    if (!payload.data || payload.data.length === 0) {
      show('empty-state');
      hide('loading-state');
      return;
    }

    populateKPIs(payload.kpis);
    renderBarChart(payload.top_products);
    renderPieChart(payload.category_revenue);
    renderTable(payload.data);

    hide('loading-state');
    show('dashboard-main');

  } catch (err) {
    showErrorState(`Network error: ${err.message}. Is the API server running?`);
  }
}

/* ── KPIs ───────────────────────────────────────────────────── */
function populateKPIs(kpis) {
  document.getElementById('kpi-revenue').textContent  = `$${Number(kpis.total_revenue).toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2})}`;
  document.getElementById('kpi-items').textContent    = Number(kpis.total_items).toLocaleString();
  document.getElementById('kpi-category').textContent = kpis.top_category;
  document.getElementById('kpi-products').textContent = kpis.num_products;
}

/* ── Bar chart — Top 5 Products ─────────────────────────────── */
function renderBarChart(data) {
  if (barChart) barChart.destroy();
  const ctx = document.getElementById('bar-chart').getContext('2d');

  const labels   = data.map(d => d.product_name);
  const values   = data.map(d => d.total_revenue);
  const maxVal   = Math.max(...values);

  barChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: values.map(v => {
          const ratio = v / maxVal;
          return `rgba(${Math.round(91 + (124-91)*ratio)},${Math.round(79 + (109-79)*ratio)},${Math.round(212 + (250-212)*ratio)},0.85)`;
        }),
        borderRadius: 8,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(3,4,10,.9)',
          borderColor: 'rgba(255,255,255,.1)',
          borderWidth: 1,
          padding: 12,
          callbacks: {
            label: ctx => ` $${Number(ctx.raw).toLocaleString('en-US', {minimumFractionDigits:2})}`,
          }
        }
      },
      scales: {
        x: { grid: { display: false }, ticks: { maxRotation: 30 } },
        y: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { callback: v => '$' + Number(v).toLocaleString() }
        }
      }
    }
  });
}

/* ── Pie chart — Revenue by Category ───────────────────────── */
function renderPieChart(data) {
  if (pieChart) pieChart.destroy();
  const ctx = document.getElementById('pie-chart').getContext('2d');

  const PALETTE = ['#7c6dfa','#38e8c5','#f97316','#60a5fa','#a78bfa','#34d399','#fbbf24','#f87171'];

  pieChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: data.map(d => d.category),
      datasets: [{
        data: data.map(d => d.total_revenue),
        backgroundColor: PALETTE.slice(0, data.length),
        borderWidth: 0,
        hoverOffset: 8,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '58%',
      plugins: {
        legend: {
          position: 'right',
          labels: { padding: 14, usePointStyle: true, pointStyleWidth: 10 }
        },
        tooltip: {
          backgroundColor: 'rgba(3,4,10,.9)',
          borderColor: 'rgba(255,255,255,.1)',
          borderWidth: 1,
          padding: 12,
          callbacks: {
            label: ctx => ` $${Number(ctx.raw).toLocaleString('en-US', {minimumFractionDigits:2})}`
          }
        }
      }
    }
  });
}

/* ── Data table ─────────────────────────────────────────────── */
function renderTable(rows) {
  if (!rows || rows.length === 0) return;
  const wrap = document.getElementById('data-table-wrap');
  const cols = Object.keys(rows[0]);
  const fmt  = v => typeof v === 'number' ? Number(v).toLocaleString() : v;

  wrap.innerHTML = `
    <table class="data-table">
      <thead><tr>${cols.map(c => `<th>${c.replace(/_/g,' ')}</th>`).join('')}</tr></thead>
      <tbody>${rows.map(r => `<tr>${cols.map(c => `<td>${fmt(r[c]) ?? '—'}</td>`).join('')}</tr>`).join('')}</tbody>
    </table>`;
}

/* ── DB demo buttons ────────────────────────────────────────── */
async function runDemo(endpoint, btnId, resultId) {
  setDemoLoading(btnId, true);
  clearResult(resultId);
  try {
    const res = await apiFetch(`/api/demo/${endpoint}`);
    if (!res) return;
    const data = await res.json();
    if (!res.ok) {
      showResult(resultId, `<div class="alert alert-error">❌ ${data.detail}</div>`);
      return;
    }
    if (!data.data || data.data.length === 0) {
      showResult(resultId, '<div class="alert alert-warn">⚠️ No results returned.</div>');
      return;
    }
    showResult(resultId, buildMiniTable(data.data));
  } catch (err) {
    showResult(resultId, `<div class="alert alert-error">❌ ${err.message}</div>`);
  } finally {
    setDemoLoading(btnId, false);
  }
}

async function runSafeInsert() {
  setDemoLoading('btn-safe', true);
  clearResult('res-safe');
  try {
    const res = await apiFetch('/api/demo/safe-insert', { method: 'POST' });
    if (!res) return;
    const data = await res.json();
    if (!res.ok) {
      showResult('res-safe', `<div class="alert alert-error">❌ ${data.detail}</div>`);
      return;
    }
    let html = `<div class="alert alert-success" style="margin-bottom:8px;">✅ Transaction Status: ${data.status}</div>`;
    if (data.loyalty && data.loyalty.length > 0) html += buildMiniTable(data.loyalty);
    showResult('res-safe', html);
  } catch (err) {
    showResult('res-safe', `<div class="alert alert-error">❌ ${err.message}</div>`);
  } finally {
    setDemoLoading('btn-safe', false);
  }
}

function buildMiniTable(rows) {
  const cols = Object.keys(rows[0]);
  const fmt  = v => typeof v === 'number' ? Number(v).toLocaleString() : (v ?? '—');
  return `<div class="data-table-wrap animate-fade-in">
    <table class="data-table">
      <thead><tr>${cols.map(c=>`<th>${c.replace(/_/g,' ')}</th>`).join('')}</tr></thead>
      <tbody>${rows.map(r=>`<tr>${cols.map(c=>`<td>${fmt(r[c])}</td>`).join('')}</tr>`).join('')}</tbody>
    </table></div>`;
}

function setDemoLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (loading) {
    btn.disabled = true;
    btn.dataset.orig = btn.innerHTML;
    btn.innerHTML = '<span class="spinner-sm" style="border-top-color:#fff;"></span> Running…';
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.orig;
  }
}

function clearResult(id) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = '';
}
function showResult(id, html) {
  const el = document.getElementById(id);
  if (el) el.innerHTML = html;
}

/* ── Utility ────────────────────────────────────────────────── */
function show(id) { const el=document.getElementById(id); if(el) el.style.display=''; }
function hide(id) { const el=document.getElementById(id); if(el) el.style.display='none'; }
function showErrorState(msg) {
  hide('loading-state');
  const el = document.getElementById('error-msg');
  if (el) el.textContent = msg;
  show('error-state');
}
