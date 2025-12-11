# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Claude Monitor is a Chrome extension that displays notifications from Claude Code hooks via Chrome Native Messaging. Notifications are pushed instantly to the browser - no polling, no HTTP servers.

**Architecture Flow:**
```
Hook → notify.py → Unix Socket → Native Host → Chrome Extension → Browser Notification
```

## Development Commands

### Installation
```bash
./install.sh
```

The installation script will:
1. Make scripts executable
2. Prompt for Chrome Extension ID
3. Install native messaging host manifest
4. Configure Chrome to communicate with the native host

### Send Notifications
```bash
python3 notify.py "Title" "Message"
python3 notify.py "Title" "Message" "priority"
```

Priorities: `success`, `error`, `warning`, `info` (default)

### Test All Notification Types
```bash
cd hooks
./examples.sh
```

### Load Extension in Chrome
1. Navigate to `chrome://extensions`
2. Enable Developer mode
3. Click "Load unpacked"
4. Select the `extension` folder
5. Copy the Extension ID
6. Run `./install.sh` and paste the Extension ID when prompted

## System Architecture

### Native Messaging Design
The extension uses **Chrome Native Messaging** for instant push notifications:

1. **Chrome starts native host automatically** when extension loads
2. **Native host listens on Unix socket** (`/tmp/claude_monitor.sock`)
3. **notify.py sends to socket** → instant delivery
4. **Native host pushes to Chrome** via stdin/stdout (Native Messaging protocol)
5. **Extension receives push** and displays notification immediately

**Key Benefits:**
- No polling = instant notifications
- No HTTP server to start/manage
- Chrome manages the native host lifecycle
- Bidirectional communication (extension ↔ native host)

### Native Messaging Protocol
Chrome communicates with native hosts using stdin/stdout:
- **Message format**: 4-byte length prefix (little-endian) + JSON payload
- **Extension → Host**: `chrome.runtime.connectNative()` creates persistent connection
- **Host → Extension**: `send_to_extension()` writes to stdout
- **Extension → Host**: `nativePort.postMessage()` writes to stdin

See `server/native_host.py:8-22` for protocol implementation.

### Unread Badge Counter
The extension icon shows a visual badge with unread notification count:
- **Orange badge** (#D97706) shows count: `1`, `2`, `99+`
- **Auto-clears** when user opens popup (marks as read)
- **Red circle** (○) when native host is disconnected
- **No badge** when connected with 0 unread
- Count persists across browser sessions via `chrome.storage.local`

See `background.js:159-178` for badge update logic.

### Service Worker Persistence
- Chrome Manifest V3 requires service workers (not background pages)
- Extension connects to native host on startup (`background.js:27-63`)
- Auto-reconnects after 5 seconds if connection drops (`background.js:42-48`)
- Important: Avoid IIFE syntax at top level - use regular function calls

### Notification Flow
1. **Hook runs**: `python3 notify.py "Title" "Message" "success"`
2. **Socket send**: notify.py connects to Unix socket, sends JSON
3. **Native host receives**: Reads from socket in background thread
4. **Augment data**: Adds `id` (timestamp) and `timestamp` (ISO 8601)
5. **Push to Chrome**: Sends via stdout using Native Messaging protocol
6. **Extension receives**: `nativePort.onMessage` fires immediately
7. **Display**: Chrome Notifications API shows browser notification
8. **Badge update**: Unread count increments, icon shows number
9. **History**: Stores last 100 notifications in `chrome.storage.local`

## File Structure Deep Dive

### `server/native_host.py`
Python native messaging host that Chrome starts automatically:
- **stdin/stdout**: Native Messaging protocol communication with Chrome
- **Unix socket server**: Listens on `/tmp/claude_monitor.sock` for notify.py
- **Thread-safe**: Socket server runs in background thread
- **send_to_extension()**: Writes to stdout with 4-byte length prefix
- **read_from_extension()**: Reads from stdin with length prefix parsing
- **handle_client_connection()**: Receives JSON from notify.py, pushes to Chrome

Chrome starts this process when extension loads and manages its lifecycle.

### `notify.py`
Simple command-line tool to send notifications:
- Connects to Unix socket at `/tmp/claude_monitor.sock`
- Sends JSON payload: `{title, message, priority}`
- Waits for response to confirm delivery
- Exit code 0 = success, 1 = error (native host not running)

### `server/com.claude.monitor.json`
Native messaging host manifest installed to:
- **macOS**: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/`
- **Linux**: `~/.config/google-chrome/NativeMessagingHosts/`

Contains:
- `name`: Host identifier (`com.claude.monitor`)
- `path`: Absolute path to `native_host.py`
- `type`: "stdio" (communicate via stdin/stdout)
- `allowed_origins`: Chrome extension ID (whitelist)

### `extension/background.js`
Service worker that connects to native host:
- `connectToNativeHost()`: Creates persistent connection via `chrome.runtime.connectNative()`
- `handleNativeMessage()`: Processes incoming messages from native host
- `handleNotification()`: Increments unread count, stores history, shows notification
- `updateBadgeCount()`: Updates icon badge with unread count (orange number)
- `markAsRead`: Message handler that clears unread count when popup opens
- Auto-reconnect logic with 5-second delay on disconnect

### `extension/popup/`
- **popup.html**: Inline CSS for self-contained UI (no external stylesheets)
- **popup.js**: Communicates with service worker via `chrome.runtime.sendMessage()`
- **Auto-marks as read**: Sends `markAsRead` message on popup open (clears badge)
- Auto-refreshes every 3 seconds to show live status
- Displays notification history with time formatting (e.g., "5m ago", "2h ago")

### `install.sh`
Installation script that:
1. Makes `native_host.py` and `notify.py` executable
2. Prompts for Chrome Extension ID
3. Creates native messaging host manifest with correct paths and extension ID
4. Installs manifest to Chrome's NativeMessagingHosts directory
5. Verifies Python 3 is available

## Notification Format

### Request (from notify.py/hooks)
```json
{
  "title": "Required: Notification title",
  "message": "Required: Notification message",
  "priority": "Optional: success|error|warning|info (default: info)"
}
```

### Native Host Augmentation
Native host automatically adds:
- `id`: Unix timestamp in milliseconds (for uniqueness)
- `timestamp`: ISO 8601 string (for display formatting)

### Priority Levels
- `success`: Green icon, normal priority (0)
- `error`: Red icon, high priority (2), requires user interaction
- `warning`: Orange icon, medium priority (1)
- `info`: Blue icon, normal priority (0)

## Extension Permissions

`manifest.json` requires:
- `notifications`: Display browser notifications
- `storage`: Persist notification history and unread count
- `nativeMessaging`: Communicate with native messaging host

**Important**: Do NOT add `alarms` permission - causes service worker errors.

## Debugging

### Service Worker Console
1. Go to `chrome://extensions`
2. Find "Claude Monitor"
3. Click "service worker" link (appears when worker is active)
4. Check for connection status and errors

### Native Host Logs
Native host prints to stderr (visible when run manually):
- `📬 Pushed:` when notification sent to Chrome
- `❌ Error:` for JSON parse errors or exceptions
- `🔌 Listening on /tmp/claude_monitor.sock` on startup

To see logs:
```bash
# Find the Chrome-managed process
ps aux | grep native_host.py

# Or run manually (for debugging only - Chrome won't connect)
python3 server/native_host.py
```

### Test notify.py directly
```bash
# This should return "✅ Notification sent"
python3 notify.py "Test" "Hello World" "info"

# If you get "❌ Error: Native host not running":
# 1. Check extension is loaded in Chrome
# 2. Check service worker console for connection errors
# 3. Verify manifest is installed: ls -la ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/
```

### Common Issues

**"Native host not running" error:**
- Extension not loaded in Chrome
- Extension ID mismatch in manifest (run `./install.sh` again)
- Check service worker console for connection errors

**Badge shows red circle (○):**
- Native host disconnected
- Check for errors in service worker console
- Verify native_host.py path in manifest is correct

**Notifications not showing:**
- Check Chrome notification permissions (System Preferences → Notifications → Chrome on macOS)
- Check browser notification settings (chrome://settings/content/notifications)

**Service worker not starting:**
- Check for syntax errors in background.js
- Never add `chrome.alarms` API calls

## Icon Generation

Icons are pre-generated but can be regenerated:
```bash
cd extension/icons
pip3 install Pillow
python3 generate_simple_icons.py
```

Creates PNG icons from code using Claude branding colors (#D97706 orange).

## Hook Integration Patterns

### Simple Command
```bash
python3 /path/to/notify.py "Build Complete" "All tests passed" "success"
```

### In Build Scripts
```bash
#!/bin/bash
npm run build
if [ $? -eq 0 ]; then
  python3 notify.py "Build Success" "Ready to deploy" "success"
else
  python3 notify.py "Build Failed" "Check logs" "error"
fi
```

### Using Hook Templates
The `hooks/` directory contains ready-to-use templates:

```bash
# Task complete
./hooks/task_complete.sh "Deploy to production" "45"

# Task error
./hooks/task_error.sh "Tests" "3 tests failed"

# File changed
./hooks/file_changed.sh "/path/to/file.js" "modified"
```

### Git Hook Example
Create `.git/hooks/post-commit`:
```bash
#!/bin/bash
PROJECT_DIR="/path/to/claude-monitor-extension"
COMMIT_MSG=$(git log -1 --pretty=%B)
python3 "$PROJECT_DIR/notify.py" "Git Commit" "$COMMIT_MSG" "success"
```

Make executable: `chmod +x .git/hooks/post-commit`

### Watch Files (fswatch)
```bash
#!/bin/bash
PROJECT_DIR="/path/to/claude-monitor-extension"
fswatch -0 src/ | while read -d "" event; do
  python3 "$PROJECT_DIR/notify.py" "File Changed" "$(basename $event)" "info"
done
```

## Reinstallation

If you need to reinstall (e.g., moved project directory):

```bash
# Run install script again with updated paths
./install.sh

# Reload extension in Chrome
# Go to chrome://extensions and click reload icon
```

## Uninstallation

```bash
# Remove native messaging host manifest
rm ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.claude.monitor.json  # macOS
rm ~/.config/google-chrome/NativeMessagingHosts/com.claude.monitor.json  # Linux

# Remove extension from Chrome
# Go to chrome://extensions and click "Remove"

# Clean up socket file (if exists)
rm /tmp/claude_monitor.sock
```
