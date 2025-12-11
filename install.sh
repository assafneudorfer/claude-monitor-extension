#!/bin/bash
# Installation script for Claude Monitor Native Messaging Host

set -e

echo "╔══════════════════════════════════════╗"
echo "║  Claude Monitor Installation        ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Get the absolute path to the project
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
NATIVE_HOST="$PROJECT_DIR/server/native_host.py"
MANIFEST_TEMPLATE="$PROJECT_DIR/server/com.claude.monitor.json"

# Make scripts executable
echo "1. Making scripts executable..."
chmod +x "$NATIVE_HOST"
chmod +x "$PROJECT_DIR/notify.py"
echo "   ✅ Done"
echo ""

# Check for Chrome extension ID
echo "2. Chrome Extension Setup"
echo "   Please follow these steps:"
echo ""
echo "   a) Open Chrome and go to: chrome://extensions"
echo "   b) Enable 'Developer mode' (top right)"
echo "   c) Click 'Load unpacked'"
echo "   d) Select the folder: $PROJECT_DIR/extension"
echo "   e) Copy the Extension ID (looks like: abcdefghijklmnopqrstuvwxyz123456)"
echo ""
read -p "   Enter your Extension ID: " EXTENSION_ID

if [ -z "$EXTENSION_ID" ]; then
  echo "   ❌ Error: Extension ID is required"
  exit 1
fi

echo "   ✅ Extension ID: $EXTENSION_ID"
echo ""

# Create native messaging host manifest
echo "3. Creating native messaging host manifest..."

# Determine the correct directory based on OS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS
  NMH_DIR="$HOME/Library/Application Support/Google/Chrome/NativeMessagingHosts"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux
  NMH_DIR="$HOME/.config/google-chrome/NativeMessagingHosts"
else
  echo "   ❌ Unsupported OS: $OSTYPE"
  exit 1
fi

# Create directory if it doesn't exist
mkdir -p "$NMH_DIR"

# Create the manifest file
MANIFEST_FILE="$NMH_DIR/com.claude.monitor.json"

cat > "$MANIFEST_FILE" << EOF
{
  "name": "com.claude.monitor",
  "description": "Claude Monitor Native Messaging Host",
  "path": "$NATIVE_HOST",
  "type": "stdio",
  "allowed_origins": [
    "chrome-extension://$EXTENSION_ID/"
  ]
}
EOF

echo "   ✅ Manifest installed to: $MANIFEST_FILE"
echo ""

# Test the setup
echo "4. Testing setup..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
  echo "   ❌ Error: python3 not found"
  exit 1
fi

echo "   ✅ Python 3 is available"
echo ""

echo "╔══════════════════════════════════════╗"
echo "║  Installation Complete!              ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo ""
echo "1. Reload the Chrome extension:"
echo "   - Go to chrome://extensions"
echo "   - Click the reload icon on Claude Monitor"
echo ""
echo "2. Check the connection:"
echo "   - Click the Claude Monitor extension icon"
echo "   - You should see a green ● (connected)"
echo ""
echo "3. Test sending a notification:"
echo "   python3 $PROJECT_DIR/notify.py \"Test\" \"Hello from Claude Monitor\""
echo ""
echo "Enjoy! 🚀"
echo ""
