### PythonConceptsMidLevel – Concept Guide

This document explains the **mid-level Python concepts** demonstrated in this project and points you to concrete examples in the code.

---

### 1. Project structure & modular design

- **Concept**: Splitting code into small, focused modules and packages instead of one big script.
- **Where**:
  - `app/__init__.py` – defines the package and documents its purpose.
  - `app/models.py` – domain objects only.
  - `app/storage.py` – persistence / I/O only.
  - `app/services.py` – business rules and orchestration.
  - `app/cli.py` – user interface and argument parsing.
- **Key idea**: Each module has a single responsibility; higher-level layers depend on lower ones (CLI → service → storage → filesystem).

---

### 2. Dataclasses and `slots`

- **Concept**: Using `@dataclass` to reduce boilerplate for simple data-carrying classes.
- **Where**:
  - `app/models.py` – `Task` is declared as:
    - `@dataclass(slots=True)` – `slots` saves memory and speeds attribute access.
- **Key ideas**:
  - Automatic `__init__`, `__repr__`, `__eq__`.
  - Default values and `default_factory` for timestamps.
  - `slots=True` prevents adding new attributes dynamically and uses a more compact layout.

---

### 3. Enums for limited choices

- **Concept**: `Enum` restricts values to a fixed set, making code safer and more self-documenting.
- **Where**:
  - `app/models.py` – `TaskStatus(str, Enum)` with values `todo`, `in_progress`, `done`.
  - `app/cli.py` – CLI arguments (`--status`) use these enum values so the user can only pass valid status strings.
- **Key ideas**:
  - `str, Enum` mixin lets enum values behave like strings (useful in JSON, CLI).
  - Central place for allowed values instead of scattered string literals.

---

### 4. Type hints and static thinking

- **Concept**: Adding type hints for better readability, editor support, and static analysis.
- **Where**:
  - All modules use type hints: `Optional`, `List`, custom types (`Task`, `TaskStatus`), and return types.
  - `app/services.py` – explicit return types for `create_task`, `list_tasks`, `change_status`, etc.
- **Key ideas**:
  - Type hints do not change runtime behaviour, but they:
    - Make contracts clear.
    - Help tools (pylance, mypy, IDEs) catch mistakes earlier.

---

### 5. Custom exceptions and error translation

- **Concept**: Raise **domain-specific** exceptions instead of letting low-level errors leak.
- **Where**:
  - `app/storage.py` – `StorageError` wraps I/O and JSON errors.
  - `app/services.py` – `TaskNotFoundError` raised when an ID cannot be found.
  - `app/cli.py` – catches `StorageError`, `TaskNotFoundError`, `ValueError` and prints friendly messages.
- **Key ideas**:
  - Storage layer hides file/JSON details and exposes a simple error type.
  - Service converts “not found in repo” into a business-level `TaskNotFoundError`.
  - CLI is the only layer that formats text for users.

---

### 6. Repository pattern & separation of concerns

- **Concept**: A repository acts as an abstraction around persistence (e.g. file, database, API).
- **Where**:
  - `app/storage.py` – `JsonFileTaskRepository` with methods `list_tasks`, `get_by_id`, `add`, `update`, `delete`.
  - `app/services.py` – `TaskService` uses the repository, without caring how tasks are actually stored.
- **Key ideas**:
  - You can later swap `JsonFileTaskRepository` for a DB-backed repository without changing business logic.
  - Service layer talks to an interface-like object (the repository), not to JSON or files directly.

---

### 7. Dependency injection / composition

- **Concept**: Passing dependencies in from the outside instead of creating them inside classes.
- **Where**:
  - `app/services.py` – `TaskService.__init__(self, repository)`.
  - `app/cli.py` – `build_service` function constructs `JsonFileTaskRepository` and passes it to `TaskService`.
- **Key ideas**:
  - Easier to test (you can pass a fake or in-memory repo).
  - More flexible – configuration is centralized in one place (`build_service`).

---

### 8. Context managers with `@contextmanager`

- **Concept**: Managing resource lifecycle with `with` blocks.
- **Where**:
  - `app/storage.py` – `_locked_file` is a custom context manager using `@contextmanager`.
- **Key ideas**:
  - Ensures parent directory exists before reading/writing.
  - Demonstrates where you would acquire and release locks or handles in a real app.
  - Encapsulates setup/teardown logic so callers just use `with _locked_file(path) as fp:`.

---

### 9. Working with `pathlib` and the filesystem

- **Concept**: Using `pathlib.Path` instead of raw strings for file paths.
- **Where**:
  - `app/storage.py` – reads and writes JSON via `Path.read_text` / `write_text`.
  - `app/cli.py` – `build_service` creates a default path like `Path.cwd() / "data" / "tasks.json"`.
- **Key ideas**:
  - `Path` makes path operations clearer and OS-independent.
  - Globally-configurable `--db` argument shows how to make file paths configurable.

---

### 10. Immutable updates with `dataclasses.replace`

- **Concept**: Creating modified copies instead of mutating objects in-place.
- **Where**:
  - `app/services.py` – `update_details` uses `replace(task, title=..., description=...)`.
- **Key ideas**:
  - Promotes a more functional style (original object stays untouched).
  - Helps avoid accidental sharing/mutation bugs in larger systems.

---

### 11. CLI design with `argparse`

- **Concept**: Building a structured command-line interface.
- **Where**:
  - `app/cli.py` – `_parse_args` creates:
    - Global `--db` option.
    - Subcommands: `create`, `list`, `status`, `delete`.
- **Key ideas**:
  - Subparsers provide a “git-like” multi-command interface.
  - Each subcommand has its own arguments.
  - Parsed arguments map directly to service-layer method calls.

---

### 12. Rich terminal output

- **Concept**: Using third-party libraries to improve UX.
- **Where**:
  - `app/cli.py` – uses `rich.Console` and `rich.Table` for colored, tabular output.
- **Key ideas**:
  - Encourages separating **data** (from services) from **presentation** (tables, colors).
  - Makes the CLI feel more like a real-world tool.

---

### 13. Entry points and `python -m` usage

- **Concept**: Running a package as a module.
- **Where**:
  - `app/main.py` – defines `run()` and `if __name__ == "__main__": run()`.
  - Used via `python -m app ...` from the project root.
- **Key ideas**:
  - `-m` finds the package on `PYTHONPATH` and runs its `__main__` logic.
  - Keeps a clear separation between “library code” and “entry point” code.

---

### 14. Suggested extensions for practice

To deepen your understanding, try adding:

- **New fields**: priority, due date, tags on `Task`.
- **Filtering & sorting**: list tasks by priority or due date.
- **Another storage backend**: e.g. SQLite-based repository implementing the same interface.
- **Unit tests**: for `TaskService` using an in-memory fake repository.
- **Decorators or logging**: e.g. a decorator that logs service calls.

As you implement these, keep the same structure: models → storage → services → CLI. This will train you to think in **layers and modules**, which is a core mid-level Python skill.

