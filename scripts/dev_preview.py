#!/usr/bin/env python3
"""
dev_preview.py
--------------
Local dev loop for iterating on the dashboard without touching the Pi.

Watches src/**/*.py for changes; on each change it re-renders the dashboard
(via `python src/run.py --preview`) and serves an auto-refreshing page so you
can watch the result update live in a browser tab.

Usage:
    python scripts/dev_preview.py
"""

import http.server
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SRC_DIR = REPO_ROOT / "src"
RUN_SCRIPT = SRC_DIR / "run.py"
PORT = 8642

PAGE = b"""<!doctype html>
<title>Dashboard preview</title>
<style>
body { margin:0; background:#222; display:flex; justify-content:center;
       align-items:center; height:100vh; }
img { max-width:100%; border:1px solid #444; }
</style>
<img id="p" src="dashboard_preview.png">
<script>
setInterval(() => {
  document.getElementById('p').src = 'dashboard_preview.png?t=' + Date.now();
}, 1000);
</script>
"""


def render_once():
    subprocess.run([sys.executable, str(RUN_SCRIPT), "--preview"], cwd=REPO_ROOT)


def watch_and_render():
    mtimes = {f: f.stat().st_mtime for f in SRC_DIR.rglob("*.py")}
    render_once()
    while True:
        time.sleep(0.5)
        changed = False
        seen = set()
        for f in SRC_DIR.rglob("*.py"):
            seen.add(f)
            m = f.stat().st_mtime
            if mtimes.get(f) != m:
                mtimes[f] = m
                changed = True
        for f in list(mtimes):
            if f not in seen:
                del mtimes[f]
                changed = True
        if changed:
            print("Change detected — re-rendering…")
            render_once()


class Server(socketserver.TCPServer):
    allow_reuse_address = True


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(PAGE)
        else:
            super().do_GET()

    def log_message(self, format, *args):
        pass


def main():
    threading.Thread(target=watch_and_render, daemon=True).start()
    with Server(("", PORT), Handler) as httpd:
        url = f"http://localhost:{PORT}/"
        print(f"Serving live preview at {url}  (Ctrl+C to stop)")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
