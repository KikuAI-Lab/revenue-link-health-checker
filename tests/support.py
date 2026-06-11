from __future__ import annotations

from contextlib import AbstractContextManager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import ClassVar
from urllib.parse import urlsplit


class FixtureHandler(BaseHTTPRequestHandler):
    routes: ClassVar[dict[str, tuple[int, dict[str, str], bytes]]] = {}

    def do_GET(self) -> None:
        route = self.routes.get(self.path)
        if route is None:
            route = self.routes.get(urlsplit(self.path).path)
        status, headers, body = route or (404, {"Content-Type": "text/plain"}, b"missing")
        self.send_response(status)
        for name, value in headers.items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:
        return


class FixtureServer(AbstractContextManager["FixtureServer"]):
    def __init__(self, routes: dict[str, tuple[int, dict[str, str], bytes]]) -> None:
        FixtureHandler.routes = routes
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
        self.thread = Thread(target=self.server.serve_forever, daemon=True)

    @property
    def base_url(self) -> str:
        host, port = self.server.server_address
        return f"http://{host}:{port}"

    def __enter__(self) -> "FixtureServer":
        self.thread.start()
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.server.shutdown()
        self.thread.join(timeout=2)
        self.server.server_close()
