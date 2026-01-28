from __future__ import annotations

import json
from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Optional

from .models import Task, TaskStatus


class StorageError(RuntimeError):
    """Raised when something goes wrong while reading or writing storage."""


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _task_from_dict(raw: Dict) -> Task:
    return Task(
        id=raw.get("id"),
        title=raw["title"],
        description=raw.get("description", ""),
        status=TaskStatus(raw.get("status", TaskStatus.TODO)),
        created_at=_parse_datetime(raw["created_at"]),
        updated_at=_parse_datetime(raw["updated_at"]),
    )


def _task_to_dict(task: Task) -> Dict:
    data = asdict(task)
    data["created_at"] = task.created_at.isoformat()
    data["updated_at"] = task.updated_at.isoformat()
    data["status"] = task.status.value
    return data


@contextmanager
def _locked_file(path: Path) -> Iterator[Path]:
    """
    Context manager that ensures the parent directory exists.

    This is a simplified stand-in for real locking logic. It demonstrates:
    - custom context managers
    - resource lifecycle management
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        yield path
    finally:
        # In a real app, this is where you would release file locks, close handles, etc.
        pass


class JsonFileTaskRepository:
    """
    Repository for tasks backed by a JSON file.

    Demonstrates:
    - a repository pattern
    - separation of concerns (I/O vs. business logic)
    - error translation to domain-specific exceptions
    """

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path

    def _read_raw(self) -> List[Dict]:
        if not self._file_path.exists():
            return []

        try:
            text = self._file_path.read_text(encoding="utf-8")
            if not text.strip():
                return []
            data = json.loads(text)
            if not isinstance(data, list):
                raise StorageError("Storage file contains unexpected data.")
            return data
        except (OSError, json.JSONDecodeError) as exc:
            raise StorageError(f"Failed to read from {self._file_path}") from exc

    def _write_raw(self, rows: Iterable[Dict]) -> None:
        serialized = json.dumps(list(rows), indent=2, ensure_ascii=False)
        try:
            with _locked_file(self._file_path) as fp:
                fp.write_text(serialized, encoding="utf-8")
        except OSError as exc:
            raise StorageError(f"Failed to write to {self._file_path}") from exc

    def list_tasks(self) -> List[Task]:
        return [_task_from_dict(row) for row in self._read_raw()]

    def get_by_id(self, task_id: int) -> Optional[Task]:
        for row in self._read_raw():
            if row.get("id") == task_id:
                return _task_from_dict(row)
        return None

    def add(self, task: Task) -> Task:
        rows = self._read_raw()
        next_id = 1 + max((row.get("id", 0) for row in rows), default=0)
        task.id = next_id
        rows.append(_task_to_dict(task))
        self._write_raw(rows)
        return task

    def update(self, task: Task) -> Task:
        if task.id is None:
            raise ValueError("Cannot update a task without an id.")

        rows = self._read_raw()
        updated: List[Dict] = []
        found = False
        for row in rows:
            if row.get("id") == task.id:
                updated.append(_task_to_dict(task))
                found = True
            else:
                updated.append(row)

        if not found:
            raise StorageError(f"Task with id={task.id} does not exist.")

        self._write_raw(updated)
        return task

    def delete(self, task_id: int) -> None:
        rows = self._read_raw()
        new_rows = [row for row in rows if row.get("id") != task_id]
        if len(new_rows) == len(rows):
            raise StorageError(f"Task with id={task_id} does not exist.")
        self._write_raw(new_rows)


__all__ = ["JsonFileTaskRepository", "StorageError"]

