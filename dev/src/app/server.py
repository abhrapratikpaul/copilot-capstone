"""HTTP Server — serves the REST API and static files."""

from __future__ import annotations

import mimetypes
import signal
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Any

from app.routes import route_request
from app.service import TaskService

STATIC_DIR = Path(__file__).parent / "static"


class _RequestHandler(BaseHTTPRequestHandler):
    """Dispatch API requests and serve static files."""

    service: TaskService  # set at class level before server starts

    # -- HTTP verb handlers -------------------------------------------------

    def do_GET(self) -> None:
        self._dispatch()

    def do_POST(self) -> None:
        self._dispatch()

    def do_PATCH(self) -> None:
        self._dispatch()

    def do_DELETE(self) -> None:
        self._dispatch()

    # -- core dispatch ------------------------------------------------------

    def _dispatch(self) -> None:
        if self.path.startswith("/api/"):
            self._handle_api()
        else:
            self._serve_static()

    def _handle_api(self) -> None:
        # Strip query string if present
        path = self.path.split("?", 1)[0]
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8") if content_length else ""

        headers = {
            "Content-Type": self.headers.get("Content-Type", ""),
        }

        status, resp_headers, resp_body = route_request(
            method=self.command,
            path=path,
            headers=headers,
            body=body,
            service=self.service,
        )

        self.send_response(status)
        for key, value in resp_headers.items():
            self.send_header(key, value)
        self.end_headers()
        if resp_body:
            self.wfile.write(resp_body.encode("utf-8"))

    def _serve_static(self) -> None:
        # Map / → /index.html
        rel = self.path.lstrip("/") or "index.html"

        # Block path traversal
        if ".." in rel:
            self.send_error(403, "Forbidden")
            return

        file_path = STATIC_DIR / rel
        if not file_path.is_file():
            self.send_error(404, "Not found")
            return

        content_type, _ = mimetypes.guess_type(str(file_path))
        content_type = content_type or "application/octet-stream"

        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # Suppress default per-request log lines
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass


class TaskHTTPServer:
    """Thin wrapper around HTTPServer for easy start/stop."""

    def __init__(
        self,
        service: TaskService,
        host: str = "127.0.0.1",
        port: int = 8080,
    ) -> None:
        self._host = host
        self._port = port
        _RequestHandler.service = service
        self._httpd = HTTPServer((host, port), _RequestHandler)

    def serve(self) -> None:
        """Start the server (blocking). Handles SIGINT for graceful shutdown."""
        # Windows doesn't support SIGINT in all cases, so we wrap in try/except
        try:
            signal.signal(signal.SIGINT, self._shutdown_handler)
        except (OSError, ValueError):
            pass

        print(f"Server running at http://{self._host}:{self._port}/")
        try:
            self._httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self._httpd.server_close()
            print("\nServer stopped.")

    def _shutdown_handler(self, signum: int, frame: Any) -> None:
        """Handle SIGINT for graceful shutdown."""
        sys.stderr.write("\nShutting down…\n")
        self._httpd.shutdown()
