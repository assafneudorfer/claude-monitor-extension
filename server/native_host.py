#!/usr/bin/env python3
"""
Claude Monitor Native Messaging Host
Runs in background, receives messages from notify.py and pushes to Chrome extension
"""

import sys
import json
import struct
import socket
import os
import threading
from datetime import datetime
import time

SOCKET_PATH = '/tmp/claude_monitor.sock'

def send_to_extension(message):
    """Send message to Chrome extension via stdout using Native Messaging protocol"""
    try:
        encoded_message = json.dumps(message).encode('utf-8')
        sys.stdout.buffer.write(struct.pack('I', len(encoded_message)))
        sys.stdout.buffer.write(encoded_message)
        sys.stdout.buffer.flush()
        return True
    except Exception as e:
        print(f"❌ Failed to send to extension: {e}", file=sys.stderr)
        return False

def read_from_extension():
    """Read message from Chrome extension via stdin"""
    try:
        raw_length = sys.stdin.buffer.read(4)
        if len(raw_length) == 0:
            return None
        message_length = struct.unpack('I', raw_length)[0]
        message = sys.stdin.buffer.read(message_length).decode('utf-8')
        return json.loads(message)
    except Exception as e:
        print(f"❌ Failed to read from extension: {e}", file=sys.stderr)
        return None

def handle_client_connection(client_socket):
    """Handle incoming notification from notify.py"""
    try:
        # Receive data from notify.py
        data = client_socket.recv(4096).decode('utf-8')
        if not data:
            return

        notification = json.loads(data)

        # Add timestamp and ID
        notification['timestamp'] = datetime.now().isoformat()
        notification['id'] = int(time.time() * 1000)

        # Push to Chrome extension
        success = send_to_extension({
            'type': 'notification',
            'data': notification
        })

        # Send response back to notify.py
        response = {'status': 'ok' if success else 'error'}
        client_socket.sendall(json.dumps(response).encode('utf-8'))

        print(f"📬 Pushed: {notification.get('title', 'Notification')}", file=sys.stderr)

    except Exception as e:
        print(f"❌ Error handling client: {e}", file=sys.stderr)
        try:
            client_socket.sendall(json.dumps({'status': 'error', 'message': str(e)}).encode('utf-8'))
        except:
            pass
    finally:
        client_socket.close()

def run_socket_server():
    """Run Unix socket server to receive messages from notify.py"""
    # Remove existing socket file
    try:
        os.unlink(SOCKET_PATH)
    except OSError:
        if os.path.exists(SOCKET_PATH):
            raise

    # Create Unix socket
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(5)

    print(f"🔌 Listening on {SOCKET_PATH}", file=sys.stderr)

    while True:
        client, _ = server.accept()
        # Handle each connection in a separate thread
        client_thread = threading.Thread(target=handle_client_connection, args=(client,))
        client_thread.start()

def listen_to_extension():
    """Listen for messages from Chrome extension (ping, etc.)"""
    while True:
        message = read_from_extension()
        if message is None:
            print("Extension disconnected", file=sys.stderr)
            sys.exit(0)

        # Respond to ping
        if message.get('type') == 'ping':
            send_to_extension({'type': 'pong'})

def main():
    """Main function"""
    print("╔══════════════════════════════════════╗", file=sys.stderr)
    print("║  Claude Monitor Native Host Started ║", file=sys.stderr)
    print("╚══════════════════════════════════════╝", file=sys.stderr)
    print("", file=sys.stderr)
    print("🔌 Connected to Chrome extension", file=sys.stderr)
    print("", file=sys.stderr)
    print("📝 Send notifications:", file=sys.stderr)
    print(f'   python notify.py "Title" "Message" "priority"', file=sys.stderr)
    print("", file=sys.stderr)

    # Start socket server in background thread
    socket_thread = threading.Thread(target=run_socket_server, daemon=True)
    socket_thread.start()

    # Listen for messages from extension (blocking)
    try:
        listen_to_extension()
    except KeyboardInterrupt:
        print("\n👋 Shutting down", file=sys.stderr)
        try:
            os.unlink(SOCKET_PATH)
        except:
            pass
        sys.exit(0)

if __name__ == '__main__':
    main()
