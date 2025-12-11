# Quick Start - 2 Minutes to Working Notifications

## Step 1: Start Server (30 seconds)

Open Terminal:

```bash
cd /Users/Assaf/vibe_apps/claude-monitor-extension
python3 server/server.py
```

✅ You should see: "Server running on http://127.0.0.1:8765"

## Step 2: Load Extension (30 seconds)

1. Open Chrome
2. Go to `chrome://extensions`
3. Enable "Developer mode" (toggle top-right)
4. Click "Load unpacked"
5. Select folder: `/Users/Assaf/vibe_apps/claude-monitor-extension/extension`

✅ You should see "Claude Monitor" extension with a badge

## Step 3: Test (1 minute)

Open new Terminal window:

```bash
cd /Users/Assaf/vibe_apps/claude-monitor-extension/hooks
./examples.sh
```

✅ You should see 4 Chrome notifications pop up!

## Done! 🎉

Now you can send notifications from anywhere:

```bash
curl -X POST http://127.0.0.1:8765 \
  -H "Content-Type: application/json" \
  -d '{"title":"Hello","message":"From Claude Code","priority":"success"}'
```

## Next Steps

- Click extension icon to see notification history
- Use the hook scripts in your Claude Code workflows
- Read README.md for advanced usage

## Troubleshooting

**Server won't start?**
- Check Python 3 is installed: `python3 --version`

**Extension shows "Server Offline"?**
- Make sure server is running in Terminal
- Check: `curl http://127.0.0.1:8765` should return `[]`

**No notifications appearing?**
- Check Chrome notification permissions
- Look at extension badge - should be green dot

That's it - super simple!
