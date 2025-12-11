# Claude Monitor

Get instant Chrome notifications when Claude Code is waiting for your input. Never miss a prompt again.

## Features

- **Instant Notifications** - Get notified when Claude Code needs your attention
- **Visual Badge Counter** - See unread count on extension icon
- **Priority Levels** - Success (green), Error (red), Warning (orange), Info (blue)
- **Notification History** - Review last 100 notifications in popup

## Quick Start

### 1. Install Extension

```bash
git clone https://github.com/yourusername/claude-monitor-extension
cd claude-monitor-extension
```

Load in Chrome:
1. Open `chrome://extensions`
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select the `extension` folder
5. Copy the Extension ID

### 2. Run Installation

```bash
./install.sh
```

Paste your Extension ID when prompted.

### 3. Test It Works

```bash
python3 notify.py "Test" "Hello from Claude Monitor!" "success"
```

### 4. Configure Claude Code Hook

Add to your Claude Code settings to get notified when Claude is waiting:

**Project-level:** `.claude/settings.json`
**User-level (all projects):** `~/.claude/settings.json`

```json
{
  "hooks": {
    "Notification": [
      {
        "matcher": "idle_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/claude-monitor-extension/notify.py 'Claude Code' 'Waiting for your input' 'info'"
          }
        ]
      },
      {
        "matcher": "permission_prompt",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /path/to/claude-monitor-extension/notify.py 'Claude Code' 'Permission required' 'warning'"
          }
        ]
      }
    ]
  }
}
```

**Replace `/path/to/claude-monitor-extension`** with your actual installation path.

Or copy the example file:
```bash
cp .claude/settings.json.example ~/.claude/settings.json
```

## Available Notification Matchers

| Matcher | When it triggers |
|---------|------------------|
| `idle_prompt` | Claude has been idle 60+ seconds waiting for input |
| `permission_prompt` | Claude needs permission to proceed |
| `auth_success` | Authentication completed |
| `elicitation_dialog` | User input dialog shown |
| `` (empty) | All notification events |

## Managing Hooks

Use Claude Code's built-in hook manager:
```bash
/hooks
```

For more details on Claude Code hooks, see the official documentation:
https://docs.anthropic.com/en/docs/claude-code/hooks

## Priority Levels

| Priority  | Color  | Use Case |
|-----------|--------|----------|
| `success` | Green  | Task completed |
| `error`   | Red    | Errors, failures |
| `warning` | Orange | Permission needed |
| `info`    | Blue   | General info |

## Badge Counter

- **Orange number** - Unread notifications
- **No badge** - All caught up
- **Red circle (○)** - Extension disconnected

Click the extension icon to view history and clear the badge.

## Troubleshooting

### "Native host not running" error

1. Check extension is loaded at `chrome://extensions`
2. Click "service worker" link to check for errors
3. Verify manifest exists:
   ```bash
   ls ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/
   ```
4. Reinstall: `./install.sh`

### Notifications not appearing

1. Check macOS: System Preferences → Notifications → Google Chrome → Allow
2. Check Chrome: `chrome://settings/content/notifications` → Allow
3. Test manually: `python3 notify.py "Test" "Hello" "info"`

## Requirements

- Python 3
- Google Chrome 88+
- macOS or Linux

## Uninstall

```bash
# Remove native messaging host
rm ~/Library/Application\ Support/Google/Chrome/NativeMessagingHosts/com.claude.monitor.json

# Remove extension from chrome://extensions

# Clean up socket
rm /tmp/claude_monitor.sock
```

## License

MIT
