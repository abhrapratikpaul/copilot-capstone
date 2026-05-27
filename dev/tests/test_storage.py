"""Unit tests for the Storage Layer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.storage import TaskStorage


@pytest.fixture()
def tmp_json(tmp_path: Path) -> Path:
    return tmp_path / "data" / "tasks.json"


@pytest.fixture()
def storage(tmp_json: Path) -> TaskStorage:
    return TaskStorage(data_path=tmp_json)


def _task(tid: str = "1", name: str = "Buy milk", completed: bool = False) -> dict:
    return {"id": tid, "name": name, "completed": completed}


# -- save / get_all ---------------------------------------------------------

def test_save_and_get_all(storage: TaskStorage) -> None:
    t = _task()
    storage.save(t)
    assert storage.get_all() == [t]


def test_save_multiple(storage: TaskStorage) -> None:
    t1 = _task("1")
    t2 = _task("2", "Walk dog")
    storage.save(t1)
    storage.save(t2)
    assert len(storage.get_all()) == 2


# -- get --------------------------------------------------------------------

def test_get_existing(storage: TaskStorage) -> None:
    t = _task()
    storage.save(t)
    assert storage.get("1") == t


def test_get_nonexistent(storage: TaskStorage) -> None:
    assert storage.get("nope") is None


# -- remove -----------------------------------------------------------------

def test_remove_existing(storage: TaskStorage) -> None:
    storage.save(_task())
    assert storage.remove("1") is True
    assert storage.get_all() == []


def test_remove_nonexistent(storage: TaskStorage) -> None:
    assert storage.remove("nope") is False


# -- remove_where -----------------------------------------------------------

def test_remove_where(storage: TaskStorage) -> None:
    storage.save(_task("1", completed=False))
    storage.save(_task("2", completed=True))
    storage.save(_task("3", completed=True))
    storage.remove_where(lambda t: t["completed"])
    remaining = storage.get_all()
    assert len(remaining) == 1
    assert remaining[0]["id"] == "1"


# -- JSON persistence -------------------------------------------------------

def test_json_file_created_on_save(storage: TaskStorage, tmp_json: Path) -> None:
    storage.save(_task())
    assert tmp_json.exists()
    data = json.loads(tmp_json.read_text(encoding="utf-8"))
    assert len(data["tasks"]) == 1


def test_persistence_across_instances(tmp_json: Path) -> None:
    s1 = TaskStorage(data_path=tmp_json)
    s1.save(_task("1", "Buy milk"))
    s1.save(_task("2", "Walk dog"))

    s2 = TaskStorage(data_path=tmp_json)
    assert len(s2.get_all()) == 2


def test_missing_file_starts_empty(tmp_json: Path) -> None:
    s = TaskStorage(data_path=tmp_json)
    assert s.get_all() == []


def test_empty_file_starts_empty(tmp_json: Path) -> None:
    tmp_json.parent.mkdir(parents=True, exist_ok=True)
    tmp_json.write_text("", encoding="utf-8")
    s = TaskStorage(data_path=tmp_json)
    assert s.get_all() == []


# -- DR-6: auto-create data/ directory -------------------------------------

def test_auto_creates_data_directory(tmp_path: Path) -> None:
    data_path = tmp_path / "nested" / "dir" / "tasks.json"
    s = TaskStorage(data_path=data_path)
    s.save(_task())
    assert data_path.exists()
