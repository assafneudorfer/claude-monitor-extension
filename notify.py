#!/usr/bin/env python3
"""
Claude Monitor Notification Sender
Send notifications to Chrome extension via native messaging host

Usage:
    python notify.py "Title" "Message"
    python notify.py "Title" "Message" "priority"

Priority: success, error, warning, info (default: info)
"""

import sys
import socket
import json

SOCKET_PATH = '/tmp/claude_monitor.sock'

def send_notification(title, message, priority='info'):
    """Send notification to the native host"""
    try:
        # Create notification payload
        notification = {
            'title': title,
            'message': message,
            'priority': priority
        }

        # Connect to native host
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)

        # Send notification
        client.sendall(json.dumps(notification).encode('utf-8'))

        # Wait for response
        response = client.recv(1024).decode('utf-8')
        result = json.loads(response)

        client.close()

        if result.get('status') == 'ok':
            print(f"✅ Notification sent: {title}")
            return 0
        else:
            print(f"❌ Failed: {result.get('message', 'Unknown error')}")
            return 1

    except FileNotFoundError:
        print("❌ Error: Native host not running")
        print("   Start it with: Open Chrome and ensure extension is loaded")
        return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

def main():
    """Main function"""
    if len(sys.argv) < 3:
        print("Usage: python notify.py \"Title\" \"Message\" [priority]")
        print("")
        print("Priority options:")
        print("  success - Green notification (default)")
        print("  error   - Red notification")
        print("  warning - Orange notification")
        print("  info    - Blue notification")
        print("")
        print("Examples:")
        print('  python notify.py "Build Complete" "All tests passed" "success"')
        print('  python notify.py "Error" "Build failed" "error"')
        print('  python notify.py "Info" "Task started"')
        return 1

    title = sys.argv[1]
    message = sys.argv[2]
    priority = sys.argv[3] if len(sys.argv) > 3 else 'info'

    return send_notification(title, message, priority)

if __name__ == '__main__':
    sys.exit(main())
