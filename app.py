"""
BikeFit Studio: main application entry point.

Run directly with:
    python app.py
"""
import argparse
import socket
import threading
import time
import webbrowser
import uvicorn


def open_when_ready(url, host, port, timeout=60):
    """Open the browser once the server accepts connections; loading the pose libraries takes a few seconds."""
    host = '127.0.0.1' if host == '0.0.0.0' else host
    end = time.time() + timeout
    while time.time() < end:
        try:
            socket.create_connection((host, port), timeout=1).close()
            break
        except OSError:
            time.sleep(0.2)
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="BikeFit: open-source video bike fitting")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8501, help="Port to bind (default: 8501)")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open the browser")
    parser.add_argument("--reload", action="store_true", help="Enable live auto-reload for development")
    args = parser.parse_args()

    url = f"http://{args.host}:{args.port}"
    print(f"\n  BikeFit 2.0 is running at {url}")
    print("  Press Ctrl+C to stop.\n")

    if not args.no_browser:
        threading.Thread(target=open_when_ready, args=(url, args.host, args.port), daemon=True).start()

    uvicorn.run("src.web.app:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
