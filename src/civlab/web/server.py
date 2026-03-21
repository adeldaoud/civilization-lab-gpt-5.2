"""Local static server for the browser dashboard."""

from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import webbrowser


def serve_dashboard(root: Path, host: str = "127.0.0.1", port: int = 8000, open_browser: bool = False) -> None:
    root = root.resolve()
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    url = f"http://{host}:{port}/web/index.html"
    with ThreadingHTTPServer((host, port), handler) as server:
        print(url)
        if open_browser:
            webbrowser.open(url)
        server.serve_forever()
