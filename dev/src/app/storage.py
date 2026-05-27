"""Storage layer — in-memory dict with JSON file persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable


class TaskStorage:
    """Manage tasks in memory and persist to a JSON file."""

    def __init__(self, data_path: Path | None = None) -> None:
        if data_path is None:
            data_path = Path(__file__).parent / "data" / "tasks.json"
        self._path = data_path
        self._tasks: dict[str, dict] = {}
        self._load()

    # -- public API ----------------------------------------------------------

    def get_all(self) -> list[dict]:
        """Return all tasks as a list."""
        return list(self._tasks.values())

    def get(self, task_id: str) -> dict | None:
        """Return a single task or None."""
        return self._tasks.get(task_id)

    def save(self, task: dict) -> dict:
        """Upsert a task and flush to disk."""
        self._tasks[task["id"]] = task
        self._flush()
        return task

    def remove(self, task_id: str) -> bool:
        """Delete a task by ID. Return True if found, False otherwise."""
        if task_id not in self._tasks:
            return False
        del self._tasks[task_id]
        self._flush()
        return True

    def remove_where(self, predicate: Callable[[dict], bool]) -> None:
        """Remove all tasks matching *predicate* and flush."""
        to_remove = [tid for tid, t in self._tasks.items() if predicate(t)]
        for tid in to_remove:
            del self._tasks[tid]
        if to_remove:
            self._flush()

    # -- internals -----------------------------------------------------------

    def _load(self) -> None:
        """Load tasks from the JSON file (if it exists)."""
        if not self._path.exists():
            return
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            for task in data.get("tasks", []):
                self._tasks[task["id"]] = task
        except (json.JSONDecodeError, KeyError):
            # Corrupt or empty file — start fresh.
            self._tasks = {}

    def _flush(self) -> None:
        """Write the full task collection to the JSON file."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"tasks": list(self._tasks.values())}
        self._path.write_text(
            json.dumps(payload, indent=2) + "\n", encoding="utf-8"
        )
