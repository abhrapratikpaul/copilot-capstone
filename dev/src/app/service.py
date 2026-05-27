"""Task Service — business logic for CRUD, validation, and sorting."""

from __future__ import annotations

import uuid

from app.storage import TaskStorage

MAX_NAME_LENGTH = 200


class TaskService:
    """Business-logic layer above the storage backend."""

    def __init__(self, storage: TaskStorage) -> None:
        self._storage = storage

    # -- public API ----------------------------------------------------------

    def create_task(self, name: str) -> dict:
        """Create a new task after validating *name*."""
        name = name.strip()
        if not name:
            raise ValueError("Task name is required")
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError("Task name exceeds maximum length")
        task = {
            "id": str(uuid.uuid4()),
            "name": name,
            "completed": False,
        }
        return self._storage.save(task)

    def list_tasks(self) -> list[dict]:
        """Return all tasks, incomplete first, completed last."""
        tasks = self._storage.get_all()
        tasks.sort(key=lambda t: t.get("completed", False))
        return tasks

    def update_task(self, task_id: str, completed: bool) -> dict | None:
        """Toggle the *completed* flag. Return the task or None."""
        task = self._storage.get(task_id)
        if task is None:
            return None
        task["completed"] = completed
        return self._storage.save(task)

    def delete_task(self, task_id: str) -> bool:
        """Remove a task by ID. Return True if found."""
        return self._storage.remove(task_id)

    def clear_completed(self) -> None:
        """Remove every task whose completed flag is True."""
        self._storage.remove_where(lambda t: t.get("completed", False))
