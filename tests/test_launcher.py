"""app.py must not open the browser before the server accepts connections."""
import os
import socket
import sys
import threading
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app  # noqa: E402


def test_browser_opens_only_once_the_server_listens(monkeypatch):
    opened = []
    monkeypatch.setattr(app.webbrowser, 'open', opened.append)
    server = socket.socket()
    server.bind(('127.0.0.1', 0))  # port reserved, but not accepting yet
    port = server.getsockname()[1]
    waiter = threading.Thread(target=app.open_when_ready, args=('url', '127.0.0.1', port), daemon=True)
    waiter.start()
    try:
        time.sleep(1.5)
        assert opened == []
        server.listen()
        waiter.join(10)
        assert opened == ['url']
    finally:
        server.close()
