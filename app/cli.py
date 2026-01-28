from __future__ import annotations

import argparse
from enum import Enum
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from .models import TaskStatus
from .services import TaskNotFoundError, TaskService
from .storage import JsonFileTaskRepository, StorageError

console = Console()


class ExitCode(int, Enum):
    OK = 0
    ERROR = 1


def build_service(db_path: Optional[str] = None) -> TaskService:
    """
    Factory for TaskService with a JSON-file repository.

    Using a function like this makes it easy to:
    - swap out implementations (e.g. use a DB later)
    - configure per-environment behaviour (different paths for tests)
    """

    base = Path(db_path) if db_path is not None else Path.cwd() / "data" / "tasks.json"
    repo = JsonFileTaskRepository(base)
    return TaskService(repo)


def _parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple modular task manager demo.")
    parser.add_argument(
        "--db",
        help="Path to the JSON file used for storage (default: ./data/tasks.json)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # create
    p_create = subparsers.add_parser("create", help="Create a new task.")
    p_create.add_argument("title", help="Short title for the task.")
    p_create.add_argument("-d", "--description", default="", help="Optional description.")

    # list
    p_list = subparsers.add_parser("list", help="List existing tasks.")
    p_list.add_argument(
        "--status",
        choices=[s.value for s in TaskStatus],
        help="Filter by task status.",
    )

    # update status
    p_status = subparsers.add_parser("status", help="Change the status of a task.")
    p_status.add_argument("id", type=int, help="Task identifier.")
    p_status.add_argument(
        "status",
        choices=[s.value for s in TaskStatus],
        help="New status for the task.",
    )

    # delete
    p_delete = subparsers.add_parser("delete", help="Delete a task.")
    p_delete.add_argument("id", type=int, help="Task identifier.")

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> ExitCode:
    args = _parse_args(argv)
    service = build_service(args.db)

    try:
        if args.command == "create":
            task = service.create_task(args.title, args.description)
            console.print(f"[green]Created task[/green] with id={task.id}")
            return ExitCode.OK

        if args.command == "list":
            status = TaskStatus(args.status) if args.status else None
            tasks = service.list_tasks(status=status)

            if not tasks:
                console.print("[yellow]No tasks found.[/yellow]")
                return ExitCode.OK

            table = Table(title="Tasks")
            table.add_column("ID", justify="right")
            table.add_column("Title")
            table.add_column("Status")
            table.add_column("Created")
            table.add_column("Updated")

            for task in tasks:
                table.add_row(
                    str(task.id or "-"),
                    task.title,
                    task.status.value,
                    task.created_at.strftime("%Y-%m-%d %H:%M"),
                    task.updated_at.strftime("%Y-%m-%d %H:%M"),
                )

            console.print(table)
            return ExitCode.OK

        if args.command == "status":
            new_status = TaskStatus(args.status)
            task = service.change_status(args.id, new_status)
            console.print(
                f"[green]Updated task[/green] id={task.id} to status [bold]{task.status.value}[/bold]."
            )
            return ExitCode.OK

        if args.command == "delete":
            service.delete_task(args.id)
            console.print(f"[green]Deleted task[/green] with id={args.id}")
            return ExitCode.OK

    except TaskNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        return ExitCode.ERROR
    except StorageError as exc:
        console.print(f"[red]Storage error:[/red] {exc}")
        return ExitCode.ERROR
    except ValueError as exc:
        console.print(f"[red]Validation error:[/red] {exc}")
        return ExitCode.ERROR

    return ExitCode.ERROR


__all__ = ["main", "build_service", "ExitCode"]

