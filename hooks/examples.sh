#!/bin/bash
# Hook Examples - Test different notification types using notify.py

# Get the project directory (parent of hooks directory)
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "Sending test notifications..."
echo ""

# Success notification
echo "1. Success notification..."
python3 "$PROJECT_DIR/notify.py" \
  "Build Successful" \
  "Your project built successfully in 3.2s" \
  "success"

sleep 1

# Error notification
echo "2. Error notification..."
python3 "$PROJECT_DIR/notify.py" \
  "Build Failed" \
  "TypeError on line 42 in app.js" \
  "error"

sleep 1

# Warning notification
echo "3. Warning notification..."
python3 "$PROJECT_DIR/notify.py" \
  "Deprecated API" \
  "Using deprecated function loadUser()" \
  "warning"

sleep 1

# Info notification
echo "4. Info notification..."
python3 "$PROJECT_DIR/notify.py" \
  "File Saved" \
  "index.html saved successfully" \
  "info"

echo ""
echo "✅ All test notifications sent!"
echo "Check your Chrome extension popup"
