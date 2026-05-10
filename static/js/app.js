/* ============================================================
   app.js – Dashboard Logic + WebSocket (Socket.IO)
   ============================================================ */

/* ── In-memory task cache ── */
let allTasks = [];

/* ── WebSocket Setup ── */
const socket    = io();
const wsBadge   = document.getElementById('ws-status');

socket.on('connect', () => {
  wsBadge.textContent = '⚡ Live';
  wsBadge.className   = 'ws-badge connected';
});
socket.on('disconnect', () => {
  wsBadge.textContent = '⚡ Offline';
  wsBadge.className   = 'ws-badge disconnected';
});

/* Real-time events from server */
socket.on('task_added', task => {
  // Only update if the task doesn't already exist (avoid duplicates from own add)
  if (!allTasks.find(t => t.id === task.id)) {
    allTasks.unshift(task);
    renderTasks();
    refreshAnalytics();
    showToast(`📬 New task added: "${task.title}"`);
  }
});
socket.on('task_updated', task => {
  const idx = allTasks.findIndex(t => t.id === task.id);
  if (idx !== -1) { allTasks[idx] = task; renderTasks(); refreshAnalytics(); }
});
socket.on('task_deleted', ({ id }) => {
  allTasks = allTasks.filter(t => t.id !== id);
  renderTasks();
  refreshAnalytics();
});

/* ── On Page Load ── */
document.addEventListener('DOMContentLoaded', () => {
  loadTasks();
  refreshAnalytics();
});

/* ── Load Tasks ── */
async function loadTasks() {
  const res   = await fetch('/api/tasks');
  const data  = await res.json();
  allTasks    = data;
  renderTasks();
}

/* ── Render Tasks ── */
function renderTasks(tasks = allTasks) {
  const list = document.getElementById('taskList');
  if (!tasks.length) {
    list.innerHTML = '<div class="empty">🗂️ No tasks yet. Add your first one above!</div>';
    return;
  }

  list.innerHTML = tasks.map(t => `
    <div class="task-card ${t.status}" data-id="${t.id}">
      <div class="task-icon">${priorityIcon(t.priority)}</div>
      <div class="task-body">
        <div class="task-title">${escHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc">${escHtml(t.description)}</div>` : ''}
        <div class="task-meta">
          <span class="badge badge-${t.priority}">${t.priority.toUpperCase()}</span>
          <span class="badge badge-${t.status}">${statusLabel(t.status)}</span>
          <span class="badge badge-date">📅 ${t.created_at}</span>
        </div>
      </div>
      <div class="task-actions">
        <button class="btn btn-outline btn-sm" onclick="openEdit(${t.id})">✏️ Edit</button>
        <button class="btn btn-danger btn-sm"  onclick="deleteTask(${t.id})">🗑️</button>
      </div>
    </div>`).join('');
}

/* ── Filter / Search ── */
function filterTasks() {
  const q       = document.getElementById('searchInput').value.toLowerCase();
  const filtered = allTasks.filter(t =>
    t.title.toLowerCase().includes(q) ||
    t.description.toLowerCase().includes(q)
  );
  renderTasks(filtered);
}

/* ── Add Task ── */
async function addTask() {
  const title    = document.getElementById('taskTitle').value.trim();
  const desc     = document.getElementById('taskDesc').value.trim();
  const priority = document.getElementById('taskPriority').value;
  const status   = document.getElementById('taskStatus').value;

  if (!title) { showToast('⚠️ Title is required!'); return; }

  const res  = await fetch('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, description: desc, priority, status })
  });
  const data = await res.json();

  if (res.ok) {
    allTasks.unshift(data.task);
    renderTasks();
    refreshAnalytics();
    showToast('✅ Task added!');
    // Reset form
    document.getElementById('taskTitle').value = '';
    document.getElementById('taskDesc').value  = '';
    document.getElementById('taskPriority').value = 'medium';
    document.getElementById('taskStatus').value   = 'pending';
  } else {
    showToast('❌ ' + data.error);
  }
}

/* ── Delete Task ── */
async function deleteTask(id) {
  if (!confirm('Delete this task?')) return;
  const res = await fetch(`/api/tasks/${id}`, { method: 'DELETE' });
  if (res.ok) {
    allTasks   = allTasks.filter(t => t.id !== id);
    renderTasks();
    refreshAnalytics();
    showToast('🗑️ Task deleted.');
  }
}

/* ── Open Edit Modal ── */
function openEdit(id) {
  const t = allTasks.find(t => t.id === id);
  if (!t) return;
  document.getElementById('editId').value       = t.id;
  document.getElementById('editTitle').value    = t.title;
  document.getElementById('editDesc').value     = t.description;
  document.getElementById('editPriority').value = t.priority;
  document.getElementById('editStatus').value   = t.status;
  document.getElementById('editModal').classList.remove('hidden');
}

function closeModal() {
  document.getElementById('editModal').classList.add('hidden');
}

/* ── Save Edit ── */
async function saveEdit() {
  const id       = document.getElementById('editId').value;
  const title    = document.getElementById('editTitle').value.trim();
  const desc     = document.getElementById('editDesc').value.trim();
  const priority = document.getElementById('editPriority').value;
  const status   = document.getElementById('editStatus').value;

  if (!title) { showToast('⚠️ Title is required!'); return; }

  const res  = await fetch(`/api/tasks/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, description: desc, priority, status })
  });
  const data = await res.json();

  if (res.ok) {
    const idx = allTasks.findIndex(t => t.id === parseInt(id));
    if (idx !== -1) allTasks[idx] = data.task;
    renderTasks();
    refreshAnalytics();
    closeModal();
    showToast('✅ Task updated!');
  } else {
    showToast('❌ ' + data.error);
  }
}

/* ── Load Analytics ── */
async function refreshAnalytics() {
  const res  = await fetch('/api/analytics');
  const data = await res.json();

  document.getElementById('statTotal').textContent      = data.total_tasks;
  document.getElementById('statCompleted').textContent  = data.completed_tasks;
  document.getElementById('statPending').textContent    = data.pending_tasks;
  document.getElementById('statInProgress').textContent = data.in_progress_tasks;
  document.getElementById('statPercent').textContent    = data.completion_percentage + '%';
  document.getElementById('statHigh').textContent       = data.priority_breakdown.high;
}

/* ── Logout ── */
async function logout() {
  await fetch('/api/logout', { method: 'POST' });
  window.location.href = '/login';
}

/* ── Toast Notification ── */
let toastTimer;
function showToast(msg) {
  const el       = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.add('hidden'), 3000);
}

/* ── Helpers ── */
function priorityIcon(p) {
  return p === 'high' ? '🔴' : p === 'medium' ? '🟡' : '🟢';
}
function statusLabel(s) {
  return s === 'in_progress' ? '🔄 In Progress' : s === 'completed' ? '✅ Done' : '⏳ Pending';
}
function escHtml(str) {
  return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

/* Close modal on backdrop click */
document.getElementById('editModal').addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});
