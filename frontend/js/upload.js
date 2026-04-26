/* upload.js — File upload logic */

let selectedFile = null;
let parsedRows   = [];

/* ── Boot ───────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const token = requireAuth();
  if (!token) return;
  const username = localStorage.getItem('username') || 'User';
  const el = document.getElementById('nav-username');
  if (el) el.textContent = username;
});

/* ── Drag-and-drop handlers ─────────────────────────────────── */
function onDragOver(e) {
  e.preventDefault();
  document.getElementById('drop-zone').classList.add('drag-over');
}
function onDragLeave(e) {
  document.getElementById('drop-zone').classList.remove('drag-over');
}
function onDrop(e) {
  e.preventDefault();
  document.getElementById('drop-zone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) processFile(file);
}
function onFileSelected(e) {
  const file = e.target.files[0];
  if (file) processFile(file);
}

/* ── Process uploaded file ──────────────────────────────────── */
function processFile(file) {
  selectedFile = file;
  clearAlert();
  hide('preview-section');
  hide('success-state');

  const allowedExt = ['.csv', '.xlsx', '.xls'];
  const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
  if (!allowedExt.includes(ext)) {
    showAlert('Only CSV and Excel (.xlsx/.xls) files are supported.', 'error');
    return;
  }

  if (ext === '.csv') {
    readCSV(file);
  } else {
    showAlert('Excel files will be processed by the server. Click "Inject to Database" to continue.', 'info');
    parsedRows = [];
    document.getElementById('preview-desc').textContent = `"${file.name}" — ready to inject.`;
    document.getElementById('preview-table').innerHTML = '';
    show('preview-section');
  }
}

function readCSV(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    try {
      const text = e.target.result;
      const rows = parseCSV(text);
      if (rows.length === 0) {
        showAlert('The CSV file appears to be empty.', 'error');
        return;
      }
      const required = ['Date','Order_ID','Product_Name','Category','Quantity','Unit_Price','Discount','Region'];
      const missing  = required.filter(c => !rows[0].hasOwnProperty(c));
      if (missing.length > 0) {
        showAlert(`❌ Invalid format! Missing columns: ${missing.join(', ')}. Please use the demo template.`, 'error');
        return;
      }
      parsedRows = rows;
      const desc = document.getElementById('preview-desc');
      if (desc) desc.textContent = `Showing the first 10 rows of "${file.name}" (${rows.length} total rows detected).`;
      renderPreview(rows.slice(0, 10));
      show('preview-section');
    } catch (err) {
      showAlert(`Failed to parse CSV: ${err.message}`, 'error');
    }
  };
  reader.readAsText(file);
}

/* Simple CSV parser (handles quoted fields) */
function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length < 2) return [];
  const headers = splitCSVLine(lines[0]);
  return lines.slice(1).map(line => {
    const values = splitCSVLine(line);
    const obj = {};
    headers.forEach((h, i) => obj[h.trim()] = (values[i] || '').trim());
    return obj;
  });
}

function splitCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;
  for (let i = 0; i < line.length; i++) {
    if (line[i] === '"') { inQuotes = !inQuotes; }
    else if (line[i] === ',' && !inQuotes) { result.push(current); current = ''; }
    else { current += line[i]; }
  }
  result.push(current);
  return result;
}

/* ── Preview table ──────────────────────────────────────────── */
function renderPreview(rows) {
  if (!rows || rows.length === 0) return;
  const cols = Object.keys(rows[0]);
  const wrap = document.getElementById('preview-table');
  wrap.innerHTML = `
    <table class="data-table">
      <thead><tr>${cols.map(c=>`<th>${c}</th>`).join('')}</tr></thead>
      <tbody>${rows.map(r=>`<tr>${cols.map(c=>`<td>${r[c]??'—'}</td>`).join('')}</tr>`).join('')}</tbody>
    </table>`;
}

/* ── Inject to DB ───────────────────────────────────────────── */
async function injectData() {
  if (!selectedFile) return;
  clearAlert();

  const btn = document.getElementById('inject-btn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner-sm" style="border-top-color:#fff;"></span> Processing…';

  try {
    const formData = new FormData();
    formData.append('file', selectedFile);

    const token = localStorage.getItem('auth_token');
    const res = await fetch('/api/upload', {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData,
    });

    if (res.status === 401) {
      localStorage.clear();
      window.location.href = '/index.html';
      return;
    }

    const data = await res.json();
    if (!res.ok) {
      showAlert(data.detail || 'Upload failed.', 'error');
      return;
    }

    // Show success
    hide('preview-section');
    const msg = document.getElementById('success-msg');
    if (msg) msg.textContent = `${data.inserted.toLocaleString()} records injected successfully. ${data.skipped > 0 ? `(${data.skipped} rows skipped due to errors)` : ''}`;
    show('success-state');

  } catch (err) {
    showAlert(`Upload failed: ${err.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = '🚀 Inject to Database';
  }
}

/* ── Download demo dataset ──────────────────────────────────── */
function downloadDemo() {
  const products = [
    { name: 'Wireless Mouse',     cat: 'Electronics', price: 25.99, qty: [15,35] },
    { name: 'Mechanical Keyboard', cat: 'Electronics', price: 89.50, qty: [2,12]  },
    { name: 'Gaming Monitor',     cat: 'Electronics', price: 299.99,qty: [0,5]   },
  ];
  const regions = ['North','South','East','West'];
  const rows = ['Date,Order_ID,Product_Name,Category,Quantity,Unit_Price,Discount,Region'];

  const start = new Date('2026-01-01');
  for (let i = 0; i < 30; i++) {
    const d = new Date(start); d.setDate(d.getDate() + i);
    const dateStr = d.toISOString().slice(0,10);
    products.forEach((p, pi) => {
      const qty = Math.floor(Math.random() * (p.qty[1] - p.qty[0] + 1)) + p.qty[0];
      const disc = pi === 2 ? 15 : pi === 1 ? 5 : 0;
      const region = regions[pi % regions.length];
      rows.push(`${dateStr},ORD-${i*10+pi+100},${p.name},${p.cat},${qty},${p.price},${disc},${region}`);
    });
  }

  const csv = rows.join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const url  = URL.createObjectURL(blob);
  const a    = document.createElement('a');
  a.href = url; a.download = 'Smart_Retail_AI_Demo_Data.csv';
  document.body.appendChild(a); a.click();
  document.body.removeChild(a); URL.revokeObjectURL(url);
}

/* ── Reset upload ───────────────────────────────────────────── */
function resetUpload() {
  selectedFile = null;
  parsedRows   = [];
  document.getElementById('file-input').value = '';
  hide('preview-section');
  hide('success-state');
  clearAlert();
}

/* ── Alert helpers ──────────────────────────────────────────── */
function showAlert(msg, type='error') {
  const box = document.getElementById('main-alert');
  if (!box) return;
  const icons = { error:'❌', success:'✅', info:'ℹ️', warn:'⚠️' };
  box.className = `alert alert-${type} animate-fade-in`;
  box.innerHTML = `<span>${icons[type]||'•'}</span><span>${msg}</span>`;
  box.style.display = 'flex';
}
function clearAlert() {
  const box = document.getElementById('main-alert');
  if (box) box.style.display = 'none';
}
function show(id) { const el=document.getElementById(id); if(el) el.style.display=''; }
function hide(id) { const el=document.getElementById(id); if(el) el.style.display='none'; }
