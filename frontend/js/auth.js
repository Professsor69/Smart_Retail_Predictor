/* auth.js — Login, Register, Google OAuth logic */

const API = '';

/* ── Shared helpers ─────────────────────────────────────────── */
function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  if (loading) {
    btn.disabled = true;
    btn.dataset.orig = btn.innerHTML;
    btn.innerHTML = '<div class="spinner-sm"></div>';
  } else {
    btn.disabled = false;
    btn.innerHTML = btn.dataset.orig || btn.innerHTML;
  }
}

function showAlert(form, message, type = 'error') {
  const box = document.getElementById(form === 'login' ? 'alert-box' : 'reg-alert-box');
  if (!box) return;
  const icons = { error: '❌', success: '✅', info: 'ℹ️', warn: '⚠️' };
  box.className = `alert alert-${type} animate-fade-in`;
  box.innerHTML = `<span>${icons[type] || '•'}</span><span>${message}</span>`;
  box.style.display = 'flex';
}

function clearAlert(form) {
  const box = document.getElementById(form === 'login' ? 'alert-box' : 'reg-alert-box');
  if (box) box.style.display = 'none';
}

/* ── Tab switching ──────────────────────────────────────────── */
function showLogin() {
  document.getElementById('login-form').style.display = 'block';
  document.getElementById('register-form').style.display = 'none';
  clearAlert('login');
}

function showRegister() {
  document.getElementById('login-form').style.display = 'none';
  document.getElementById('register-form').style.display = 'block';
  clearAlert('reg');
}

/* ── Login ──────────────────────────────────────────────────── */
async function handleLogin() {
  const username = document.getElementById('login-username').value.trim();
  const password = document.getElementById('login-password').value;
  clearAlert('login');

  if (!username || !password) {
    showAlert('login', 'Please enter both username and password.', 'error');
    return;
  }

  setLoading('login-btn', true);
  try {
    const res = await fetch(`${API}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();

    if (!res.ok) {
      showAlert('login', data.detail || 'Login failed.', 'error');
      return;
    }

    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('username', data.username);
    localStorage.setItem('user_id', data.user_id);
    window.location.href = '/dashboard.html';

  } catch (err) {
    showAlert('login', 'Cannot reach the server. Is the API running?', 'error');
  } finally {
    setLoading('login-btn', false);
  }
}

/* ── Register ───────────────────────────────────────────────── */
async function handleRegister() {
  const username = document.getElementById('reg-username').value.trim();
  const password = document.getElementById('reg-password').value;
  clearAlert('reg');

  if (!username || !password) {
    showAlert('reg', 'Please fill in all fields.', 'error');
    return;
  }

  setLoading('reg-btn', true);
  try {
    const res = await fetch(`${API}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    const data = await res.json();

    if (!res.ok) {
      showAlert('reg', data.detail || 'Registration failed.', 'error');
      return;
    }

    localStorage.setItem('auth_token', data.token);
    localStorage.setItem('username', data.username);
    localStorage.setItem('user_id', data.user_id);
    showAlert('reg', 'Account created! Redirecting...', 'success');
    setTimeout(() => { window.location.href = '/dashboard.html'; }, 800);

  } catch (err) {
    showAlert('reg', 'Cannot reach the server. Is the API running?', 'error');
  } finally {
    setLoading('reg-btn', false);
  }
}


/* ── Logout (used on inner pages) ───────────────────────────── */
async function logout() {
  const token = localStorage.getItem('auth_token');
  if (token) {
    try {
      await fetch(`${API}/api/auth/logout`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
    } catch { /* non-critical */ }
  }
  localStorage.clear();
  window.location.href = '/index.html';
}

/* ── Auth guard (call on protected pages) ───────────────────── */
function requireAuth() {
  const token = localStorage.getItem('auth_token');
  if (!token) {
    window.location.href = '/index.html';
    return null;
  }
  return token;
}

/* ── Shared API fetch with auth header ──────────────────────── */
async function apiFetch(path, options = {}) {
  const token = localStorage.getItem('auth_token');
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (res.status === 401) {
    localStorage.clear();
    window.location.href = '/index.html';
    return null;
  }
  return res;
}
