"""Unit tests for the API Router."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.storage import TaskStorage
from app.service import TaskService
from app.routes import route_request


@pytest.fixture()
def service(tmp_path: Path) -> TaskService:
    storage = TaskStorage(data_path=tmp_path / "tasks.json")
    return TaskService(storage)


def _req(
    method: str,
    path: str,
    body: dict | str = "",
    service: TaskService | None = None,
    content_type: str = "application/json",
) -> tuple[int, dict[str, str], str]:
    if isinstance(body, dict):
        body = json.dumps(body)
    headers = {"Content-Type": content_type}
    assert service is not None
    return route_request(method, path, headers, body, service)


# -- GET /api/tasks ---------------------------------------------------------

def test_get_tasks_empty(service: TaskService) -> None:
    status, _, body = _req("GET", "/api/tasks", service=service)
    assert status == 200
    assert json.loads(body) == []


def test_get_tasks_returns_list(service: TaskService) -> None:
    service.create_task("A")
    status, headers, body = _req("GET", "/api/tasks", service=service)
    assert status == 200
    assert headers["Content-Type"] == "application/json"
    data = json.loads(body)
    assert len(data) == 1
    assert data[0]["name"] == "A"


# -- POST /api/tasks --------------------------------------------------------

def test_post_task_valid(service: TaskService) -> None:
    status, _, body = _req("POST", "/api/tasks", {"name": "Buy milk"}, service=service)
    assert status == 201
    task = json.loads(body)
    assert task["name"] == "Buy milk"
    assert task["completed"] is False


def test_post_task_empty_name(service: TaskService) -> None:
    status, _, body = _req("POST", "/api/tasks", {"name": ""}, service=service)
    assert status == 400
    assert json.loads(body)["error"] == "Task name is required"


def test_post_task_exceeds_max_length(service: TaskService) -> None:
    status, _, body = _req("POST", "/api/tasks", {"name": "x" * 201}, service=service)
    assert status == 400
    assert json.loads(body)["error"] == "Task name exceeds maximum length"


def test_post_task_invalid_json(service: TaskService) -> None:
    status, _, body = _req("POST", "/api/tasks", "not json", service=service)
    assert status == 400
    assert json.loads(body)["error"] == "Invalid JSON"


def test_post_task_wrong_content_type(service: TaskService) -> None:
    status, _, body = _req(
        "POST", "/api/tasks", '{"name": "A"}', service=service, content_type="text/plain"
    )
    assert status == 400
    assert json.loads(body)["error"] == "Content-Type must be application/json"


def test_post_task_non_string_name(service: TaskService) -> None:
    status, _, body = _req("POST", "/api/tasks", {"name": 123}, service=service)
    assert status == 400
    assert json.loads(body)["error"] == "Task name is required"


# -- PATCH /api/tasks/{id} --------------------------------------------------

def test_patch_task(service: TaskService) -> None:
    t = service.create_task("A")
    status, _, body = _req("PATCH", f"/api/tasks/{t['id']}", {"completed": True}, service=service)
    assert status == 200
    assert json.loads(body)["completed"] is True


def test_patch_task_ignores_extra_fields(service: TaskService) -> None:
    """DR-1: PATCH extracts only 'completed'; extra fields are silently ignored."""
    t = service.create_task("Original")
    status, _, body = _req(
        "PATCH",
        f"/api/tasks/{t['id']}",
        {"completed": True, "name": "hacked"},
        service=service,
    )
    assert status == 200
    assert json.loads(body)["name"] == "Original"


def test_patch_nonexistent(service: TaskService) -> None:
    status, _, body = _req("PATCH", "/api/tasks/nonexistent", {"completed": True}, service=service)
    assert status == 404
    assert json.loads(body)["error"] == "Task not found"


def test_patch_missing_completed_field(service: TaskService) -> None:
    t = service.create_task("A")
    status, _, body = _req("PATCH", f"/api/tasks/{t['id']}", {"other": "field"}, service=service)
    assert status == 400
    assert json.loads(body)["error"] == "Missing 'completed' field"


def test_patch_invalid_json(service: TaskService) -> None:
    t = service.create_task("A")
    status, _, body = _req("PATCH", f"/api/tasks/{t['id']}", "not json", service=service)
    assert status == 400
    assert json.loads(body)["error"] == "Invalid JSON"


def test_patch_wrong_content_type(service: TaskService) -> None:
    t = service.create_task("A")
    status, _, body = _req(
        "PATCH", f"/api/tasks/{t['id']}", '{"completed": true}',
        service=service, content_type="text/plain",
    )
    assert status == 400
    assert json.loads(body)["error"] == "Content-Type must be application/json"


# -- DELETE /api/tasks/{id} -------------------------------------------------

def test_delete_task(service: TaskService) -> None:
    t = service.create_task("A")
    status, _, body = _req("DELETE", f"/api/tasks/{t['id']}", service=service)
    assert status == 204
    assert body == ""


def test_delete_nonexistent(service: TaskService) -> None:
    status, _, body = _req("DELETE", "/api/tasks/nonexistent", service=service)
    assert status == 404


# -- DELETE /api/tasks/completed (DR-3) -------------------------------------

def test_delete_completed(service: TaskService) -> None:
    """DR-3: literal /completed matches before /{id}."""
    t = service.create_task("A")
    service.update_task(t["id"], completed=True)
    status, _, body = _req("DELETE", "/api/tasks/completed", service=service)
    assert status == 204
    assert service.list_tasks() == []


# -- 405 catch-all (DR-4) --------------------------------------------------

def test_put_returns_405(service: TaskService) -> None:
    status, _, body = _req("PUT", "/api/tasks", service=service)
    assert status == 405
    assert json.loads(body)["error"] == "Method not allowed"


def test_patch_on_collection_returns_405(service: TaskService) -> None:
    status, _, body = _req("PATCH", "/api/tasks", service=service)
    assert status == 405


# -- Content-Type on responses ----------------------------------------------

def test_response_content_type(service: TaskService) -> None:
    status, headers, _ = _req("GET", "/api/tasks", service=service)
    assert headers.get("Content-Type") == "application/json"
