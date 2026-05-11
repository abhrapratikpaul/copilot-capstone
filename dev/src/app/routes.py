"""API Router — dispatch HTTP requests to TaskService methods."""

from __future__ import annotations

import json
from typing import Any

from app.service import TaskService

# Type alias for an HTTP response tuple: (status_code, headers_dict, body_string)
Response = tuple[int, dict[str, str], str]

JSON_CT = {"Content-Type": "application/json"}


def _json_body(obj: Any) -> str:
    return json.dumps(obj)


def _error(status: int, message: str) -> Response:
    return status, JSON_CT, _json_body({"error": message})


def _read_json(body: str) -> dict | None:
    """Parse *body* as JSON, return dict or None on failure."""
    try:
        data = json.loads(body)
        if not isinstance(data, dict):
            return None
        return data
    except (json.JSONDecodeError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Public dispatcher
# ---------------------------------------------------------------------------

def route_request(
    method: str,
    path: str,
    headers: dict[str, str],
    body: str,
    service: TaskService,
) -> Response:
    """Route an API request and return (status, headers, body)."""

    # --- /api/tasks (collection) -------------------------------------------
    if path == "/api/tasks":
        if method == "GET":
            return _handle_list(service)
        if method == "POST":
            return _handle_create(body, headers, service)
        return _error(405, "Method not allowed")

    # --- /api/tasks/completed (literal — must match BEFORE /{id}) ----------
    if path == "/api/tasks/completed":
        if method == "DELETE":
            return _handle_clear_completed(service)
        return _error(405, "Method not allowed")

    # --- /api/tasks/{id} ---------------------------------------------------
    if path.startswith("/api/tasks/"):
        task_id = path[len("/api/tasks/"):]
        if not task_id:
            return _error(400, "Missing task ID")
        if method == "PATCH":
            return _handle_update(task_id, body, headers, service)
        if method == "DELETE":
            return _handle_delete(task_id, service)
        return _error(405, "Method not allowed")

    return _error(404, "Not found")


# ---------------------------------------------------------------------------
# Individual handlers
# ---------------------------------------------------------------------------

def _handle_list(service: TaskService) -> Response:
    tasks = service.list_tasks()
    return 200, JSON_CT, _json_body(tasks)


def _handle_create(
    body: str, headers: dict[str, str], service: TaskService
) -> Response:
    content_type = headers.get("Content-Type", "")
    if "application/json" not in content_type:
        return _error(400, "Content-Type must be application/json")

    data = _read_json(body)
    if data is None:
        return _error(400, "Invalid JSON")

    name = data.get("name", "")
    if not isinstance(name, str):
        return _error(400, "Task name is required")
    try:
        task = service.create_task(name)
    except ValueError as exc:
        return _error(400, str(exc))
    return 201, JSON_CT, _json_body(task)


def _handle_update(
    task_id: str,
    body: str,
    headers: dict[str, str],
    service: TaskService,
) -> Response:
    content_type = headers.get("Content-Type", "")
    if "application/json" not in content_type:
        return _error(400, "Content-Type must be application/json")

    data = _read_json(body)
    if data is None:
        return _error(400, "Invalid JSON")

    if "completed" not in data:
        return _error(400, "Missing 'completed' field")

    completed = bool(data["completed"])
    task = service.update_task(task_id, completed)
    if task is None:
        return _error(404, "Task not found")
    return 200, JSON_CT, _json_body(task)


def _handle_delete(task_id: str, service: TaskService) -> Response:
    if not service.delete_task(task_id):
        return _error(404, "Task not found")
    return 204, {}, ""


def _handle_clear_completed(service: TaskService) -> Response:
    service.clear_completed()
    return 204, {}, ""
