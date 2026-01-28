from __future__ import annotations

from dataclasses import replace
from typing import List, Optional

from .models import Task, TaskStatus
from .storage import JsonFileTaskRepository, StorageError


class TaskNotFoundError(LookupError):
    """Raised when a task cannot be found for a given identifier."""


class TaskService:
    """
    Orchestrates business rules around tasks.

    Demonstrates:
    - dependency injection (repository is passed in)
    - separation between business logic and persistence
    - use of custom exceptions for clearer error handling
    """

    def __init__(self, repository: JsonFileTaskRepository) -> None:
        self._repo = repository

    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]:
        tasks = self._repo.list_tasks()
        if status is not None:
            return [t for t in tasks if t.status == status]
        return tasks

    def create_task(self, title: str, description: str = "") -> Task:
        if not title.strip():
            raise ValueError("Title must not be empty.")

        task = Task(title=title.strip(), description=description.strip())
        return self._repo.add(task)

    def change_status(self, task_id: int, new_status: TaskStatus) -> Task:
        task = self._require_task(task_id)
        task.update_status(new_status)
        return self._repo.update(task)

    def update_details(self, task_id: int, *, title: Optional[str] = None, description: Optional[str] = None) -> Task:
        task = self._require_task(task_id)

        new_title = task.title if title is None else title.strip()
        new_description = task.description if description is None else description.strip()

        updated = replace(task, title=new_title, description=new_description)
        return self._repo.update(updated)

    def delete_task(self, task_id: int) -> None:
        try:
            self._repo.delete(task_id)
        except StorageError as exc:
            raise TaskNotFoundError(str(exc)) from exc

    def _require_task(self, task_id: int) -> Task:
        task = self._repo.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task with id={task_id} was not found.")
        return task


__all__ = ["TaskService", "TaskNotFoundError"]

