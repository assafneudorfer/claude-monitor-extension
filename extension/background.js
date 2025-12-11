/**
 * Claude Monitor - Background Service Worker
 * Connects to native messaging host for push notifications
 */

const HOST_NAME = 'com.claude.monitor';

let nativePort = null;
let notificationHistory = [];
let isConnected = false;
let reconnectTimer = null;
let unreadCount = 0;

// Initialize
async function initialize() {
  try {
    // Load notification history and unread count from storage
    const stored = await chrome.storage.local.get(['notificationHistory', 'unreadCount']);
    notificationHistory = stored.notificationHistory || [];
    unreadCount = stored.unreadCount || 0;

    // Update badge with unread count
    updateBadgeCount();

    // Connect to native messaging host
    connectToNativeHost();
  } catch (error) {
    console.error('Initialization error:', error);
  }
}

function connectToNativeHost() {
  try {
    console.log(`Connecting to native host: ${HOST_NAME}`);

    nativePort = chrome.runtime.connectNative(HOST_NAME);

    nativePort.onMessage.addListener((message) => {
      handleNativeMessage(message);
    });

    nativePort.onDisconnect.addListener(() => {
      console.error('Native host disconnected:', chrome.runtime.lastError?.message);
      isConnected = false;
      updateBadge('offline');

      // Try to reconnect after 5 seconds
      if (!reconnectTimer) {
        reconnectTimer = setTimeout(() => {
          reconnectTimer = null;
          connectToNativeHost();
        }, 5000);
      }
    });

    // Send initial ping
    nativePort.postMessage({ type: 'ping' });

    isConnected = true;
    updateBadge('online');
    console.log('Connected to native host');

  } catch (error) {
    console.error('Error connecting to native host:', error);
    isConnected = false;
    updateBadge('offline');
  }
}

function handleNativeMessage(message) {
  try {
    console.log('Received from native host:', message);

    if (message.type === 'notification') {
      handleNotification(message.data);
    } else if (message.type === 'pong') {
      // Connection confirmed
      console.log('Native host is alive');
    }
  } catch (error) {
    console.error('Error handling native message:', error);
  }
}

async function handleNotification(notification) {
  try {
    // Add to history
    notificationHistory.unshift(notification);
    if (notificationHistory.length > 100) {
      notificationHistory = notificationHistory.slice(0, 100);
    }

    // Increment unread count
    unreadCount++;

    // Save to storage
    await chrome.storage.local.set({
      notificationHistory,
      unreadCount
    });

    // Update badge to show count
    updateBadgeCount();

    // Show notification
    await showNotification(notification);
  } catch (error) {
    console.error('Error handling notification:', error);
  }
}

async function showNotification(data) {
  try {
    const { title, message, priority = 'info' } = data;

    const iconMap = {
      success: 'icons/success.png',
      error: 'icons/error.png',
      warning: 'icons/warning.png',
      info: 'icons/info.png'
    };

    const options = {
      type: 'basic',
      iconUrl: iconMap[priority] || 'icons/icon128.png',
      title: title || 'Claude Monitor',
      message: message || 'Notification from Claude Code',
      priority: priority === 'error' ? 2 : (priority === 'warning' ? 1 : 0),
      requireInteraction: priority === 'error'
    };

    await chrome.notifications.create(`claude-${data.id}`, options);
  } catch (error) {
    console.error('Error showing notification:', error);
  }
}

function updateBadge(status) {
  try {
    // This function is called on connect/disconnect
    // If we have unread messages, don't override with connection status
    if (unreadCount > 0) {
      updateBadgeCount();
    } else {
      const config = {
        online: { text: '', color: '#4CAF50' },  // No badge when connected with no unread
        offline: { text: '○', color: '#F44336' }
      };

      const badge = config[status] || config.offline;
      chrome.action.setBadgeText({ text: badge.text });
      chrome.action.setBadgeBackgroundColor({ color: badge.color });
    }
  } catch (error) {
    console.error('Error updating badge:', error);
  }
}

function updateBadgeCount() {
  try {
    if (unreadCount > 0) {
      // Show count badge
      const text = unreadCount > 99 ? '99+' : unreadCount.toString();
      chrome.action.setBadgeText({ text });
      chrome.action.setBadgeBackgroundColor({ color: '#D97706' });  // Orange (Claude color)
    } else {
      // No unread messages
      if (isConnected) {
        chrome.action.setBadgeText({ text: '' });
      } else {
        chrome.action.setBadgeText({ text: '○' });
        chrome.action.setBadgeBackgroundColor({ color: '#F44336' });
      }
    }
  } catch (error) {
    console.error('Error updating badge count:', error);
  }
}

// Handle messages from popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  try {
    if (message.type === 'getStatus') {
      sendResponse({
        serverOnline: isConnected,
        serverUrl: 'Native Messaging',
        notificationHistory: notificationHistory,
        unreadCount: unreadCount
      });
      return true;
    }

    if (message.type === 'testNotification') {
      showNotification({
        id: Date.now(),
        title: 'Test Notification',
        message: 'This is a test from Claude Monitor',
        priority: 'info'
      });
      sendResponse({ success: true });
      return true;
    }

    if (message.type === 'clearHistory') {
      notificationHistory = [];
      unreadCount = 0;
      chrome.storage.local.set({ notificationHistory: [], unreadCount: 0 });
      updateBadgeCount();
      sendResponse({ success: true });
      return true;
    }

    if (message.type === 'deleteNotification') {
      const notificationId = message.notificationId;
      const index = notificationHistory.findIndex(n => n.id === notificationId);

      if (index !== -1) {
        notificationHistory.splice(index, 1);

        // Decrease unread count if there are unread notifications
        if (unreadCount > 0) {
          unreadCount--;
        }

        chrome.storage.local.set({ notificationHistory, unreadCount });
        updateBadgeCount();
        sendResponse({ success: true });
      } else {
        sendResponse({ success: false, error: 'Notification not found' });
      }
      return true;
    }

    if (message.type === 'markAsRead') {
      unreadCount = 0;
      chrome.storage.local.set({ unreadCount: 0 });
      updateBadgeCount();
      sendResponse({ success: true });
      return true;
    }
  } catch (error) {
    console.error('Error handling message:', error);
    sendResponse({ success: false, error: error.message });
  }

  return true;
});

// Handle notification clicks
chrome.notifications.onClicked.addListener((notificationId) => {
  chrome.notifications.clear(notificationId);
});

// Start
initialize();
