/**
 * Claude Monitor - Popup UI
 */

const statusEl = document.getElementById('status');
const statusText = document.getElementById('statusText');
const notificationsEl = document.getElementById('notifications');
const totalCountEl = document.getElementById('totalCount');
const todayCountEl = document.getElementById('todayCount');
const serverUrlEl = document.getElementById('serverUrl');

const testBtn = document.getElementById('testBtn');
const markReadBtn = document.getElementById('markReadBtn');
const clearBtn = document.getElementById('clearBtn');

// Initialize
initialize();

async function initialize() {
  await updateStatus();
  setupEventListeners();

  // Auto-refresh every 3 seconds
  setInterval(updateStatus, 3000);
}

function setupEventListeners() {
  testBtn.addEventListener('click', async () => {
    await chrome.runtime.sendMessage({ type: 'testNotification' });
  });

  markReadBtn.addEventListener('click', async () => {
    await chrome.runtime.sendMessage({ type: 'markAsRead' });
    await updateStatus();
  });

  clearBtn.addEventListener('click', async () => {
    if (confirm('Clear all notification history?')) {
      await chrome.runtime.sendMessage({ type: 'clearHistory' });
      await updateStatus();
    }
  });

  // Event delegation for delete buttons
  notificationsEl.addEventListener('click', async (e) => {
    if (e.target.classList.contains('delete-btn')) {
      const notificationId = parseInt(e.target.dataset.id);
      await chrome.runtime.sendMessage({
        type: 'deleteNotification',
        notificationId: notificationId
      });
      await updateStatus();
    }
  });
}

async function updateStatus() {
  try {
    const response = await chrome.runtime.sendMessage({ type: 'getStatus' });

    if (!response) {
      console.error('No response from background worker');
      statusEl.className = 'status offline';
      statusText.textContent = 'No Response';
      return;
    }

    // Update server status
    if (response.serverOnline) {
      statusEl.className = 'status online';
      statusText.textContent = 'Connected';
    } else {
      statusEl.className = 'status offline';
      statusText.textContent = 'Server Offline';
    }

    // Update server URL
    serverUrlEl.textContent = response.serverUrl;

    // Update stats
    const history = response.notificationHistory || [];
    totalCountEl.textContent = history.length;

    const today = new Date().toDateString();
    const todayCount = history.filter(n => {
      const notifDate = new Date(n.timestamp).toDateString();
      return notifDate === today;
    }).length;
    todayCountEl.textContent = todayCount;

    // Update notification list
    updateNotificationList(history);

  } catch (error) {
    console.error('Error updating status:', error);
    console.error('Error details:', error.message);
    statusEl.className = 'status offline';
    statusText.textContent = 'Error: ' + error.message;
  }
}

function updateNotificationList(history) {
  if (!history || history.length === 0) {
    notificationsEl.innerHTML = '<div class="empty-state">No notifications yet<br><br>Send a notification:<br><code>python3 notify.py "Title" "Message"</code></div>';
    return;
  }

  const html = history.slice(0, 20).map(n => {
    const time = formatTime(n.timestamp);
    const priority = n.priority || 'info';

    return `
      <div class="notification-item ${priority}">
        <div class="notification-header">
          <div class="notification-title">${escapeHtml(n.title)}</div>
          <div class="notification-time">${time}</div>
        </div>
        <div class="notification-message">${escapeHtml(n.message)}</div>
        <div class="notification-actions">
          <button class="delete-btn" data-id="${n.id}">✕ Delete</button>
        </div>
      </div>
    `;
  }).join('');

  notificationsEl.innerHTML = html;
}

function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
  return date.toLocaleDateString();
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
