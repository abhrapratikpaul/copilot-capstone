"""Unit tests for the Task Service."""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from app.storage import TaskStorage
from app.service import TaskService


@pytest.fixture()
def service(tmp_path: Path) -> TaskService:
    storage = TaskStorage(data_path=tmp_path / "tasks.json")
    return TaskService(storage)


# -- create_task ------------------------------------------------------------

def test_create_task(service: TaskService) -> None:
    t = service.create_task("Buy milk")
    assert t["name"] == "Buy milk"
    assert t["completed"] is False
    uuid.UUID(t["id"])  # valid UUID4


def test_create_task_strips_whitespace(service: TaskService) -> None:
    t = service.create_task("  Buy milk  ")
    assert t["name"] == "Buy milk"


def test_create_task_empty_raises(service: TaskService) -> None:
    with pytest.raises(ValueError, match="Task name is required"):
        service.create_task("")


def test_create_task_whitespace_only_raises(service: TaskService) -> None:
    with pytest.raises(ValueError, match="Task name is required"):
        service.create_task("   ")


def test_create_task_exceeds_max_length(service: TaskService) -> None:
    with pytest.raises(ValueError, match="Task name exceeds maximum length"):
        service.create_task("x" * 201)


def test_create_task_at_max_length(service: TaskService) -> None:
    t = service.create_task("x" * 200)
    assert len(t["name"]) == 200


# -- list_tasks / sorting ---------------------------------------------------

def test_list_tasks_sorted(service: TaskService) -> None:
    t1 = service.create_task("A")
    service.update_task(t1["id"], completed=True)
    service.create_task("B")

    tasks = service.list_tasks()
    assert tasks[0]["completed"] is False  # incomplete first
    assert tasks[1]["completed"] is True   # completed last


def test_list_tasks_empty(service: TaskService) -> None:
    assert service.list_tasks() == []


# -- update_task ------------------------------------------------------------

def test_update_task(service: TaskService) -> None:
    t = service.create_task("A")
    updated = service.update_task(t["id"], completed=True)
    assert updated is not None
    assert updated["completed"] is True


def test_update_nonexistent(service: TaskService) -> None:
    assert service.update_task("nonexistent", completed=True) is None


# -- delete_task ------------------------------------------------------------

def test_delete_task(service: TaskService) -> None:
    t = service.create_task("A")
    assert service.delete_task(t["id"]) is True
    assert service.list_tasks() == []


def test_delete_nonexistent(service: TaskService) -> None:
    assert service.delete_task("nonexistent") is False


# -- clear_completed --------------------------------------------------------

def test_clear_completed(service: TaskService) -> None:
    t1 = service.create_task("A")
    service.create_task("B")
    service.update_task(t1["id"], completed=True)

    service.clear_completed()
    remaining = service.list_tasks()
    assert len(remaining) == 1
    assert remaining[0]["name"] == "B"


def test_clear_completed_noop_when_none(service: TaskService) -> None:
    service.create_task("A")
    service.clear_completed()  # no error
    assert len(service.list_tasks()) == 1
