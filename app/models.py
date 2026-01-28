from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TaskStatus(str, Enum):
    """Enumeration for the lifecycle of a task."""

    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


@dataclass(slots=True)
class Task:
    """
    Domain model for a task.

    Highlights:
    - type hints
    - dataclasses with slots (memory-friendly, faster attribute access)
    - default factories
    """

    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    id: Optional[int] = None

    def update_status(self, new_status: TaskStatus) -> None:
        """Transition to a new status and update the timestamp."""

        if self.status == TaskStatus.DONE and new_status != TaskStatus.DONE:
            raise ValueError("Cannot move a completed task back to a non-completed state.")

        self.status = new_status
        self.updated_at = datetime.utcnow()


__all__ = ["Task", "TaskStatus"]

