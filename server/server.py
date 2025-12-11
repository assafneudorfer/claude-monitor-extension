#!/usr/bin/env python3
"""
Simple HTTP server for Claude Monitor
Receives notifications via curl and serves them to the Chrome extension
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import time
from datetime import datetime
from collections import deque
import threading

# Store notifications in memory (max 100)
notifications = deque(maxlen=100)
notifications_lock = threading.Lock()

class NotificationHandler(BaseHTTPRequestHandler):
    """Handle HTTP requests for notifications"""

    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        """Receive notification from curl"""
        try:
            # Read POST data
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)

            # Parse JSON
            notification = json.loads(post_data.decode('utf-8'))

            # Add timestamp and ID
            notification['timestamp'] = datetime.now().isoformat()
            notification['id'] = int(time.time() * 1000)

            # Store notification
            with notifications_lock:
                notifications.append(notification)

            print(f"📬 Received: {notification.get('title', 'Notification')}")

            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok', 'id': notification['id']}).encode())

        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(400)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'error', 'message': str(e)}).encode())

    def do_GET(self):
        """Send notifications to extension"""
        try:
            # Get query parameters
            query = self.path.split('?')[1] if '?' in self.path else ''
            params = dict(param.split('=') for param in query.split('&') if '=' in param) if query else {}

            # Get since parameter (return only new notifications)
            since = int(params.get('since', 0))

            # Get notifications
            with notifications_lock:
                # Filter notifications newer than 'since' timestamp
                new_notifications = [n for n in notifications if n.get('id', 0) > since]

            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(new_notifications).encode())

        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def run_server(port=8765):
    """Start the HTTP server"""
    server_address = ('127.0.0.1', port)
    httpd = HTTPServer(server_address, NotificationHandler)

    print("╔══════════════════════════════════════╗")
    print("║   Claude Monitor Server Started     ║")
    print("╚══════════════════════════════════════╝")
    print(f"\n🌐 Server running on http://127.0.0.1:{port}")
    print(f"\n📝 Hook examples:")
    print(f"   curl -X POST http://127.0.0.1:{port} \\")
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"title":"Task Complete","message":"Build finished","priority":"success"}}\'')
    print(f"\n✋ Press Ctrl+C to stop\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        httpd.shutdown()


if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    run_server(port)
