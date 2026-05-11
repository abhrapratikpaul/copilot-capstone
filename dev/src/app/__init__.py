"""Task Manager application."""

from __future__ import annotations


def main(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Wire components and start the HTTP server."""
    from app.storage import TaskStorage
    from app.service import TaskService
    from app.server import TaskHTTPServer

    storage = TaskStorage()
    service = TaskService(storage)
    server = TaskHTTPServer(service, host=host, port=port)
    server.serve()
