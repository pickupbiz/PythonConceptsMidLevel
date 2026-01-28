### Mid-level Python Interview – Q&A (Project-Based)

This file contains **interview-style questions and answers** based on the `PythonConceptsMidLevel` project. Use it to practise explaining real code and design decisions.

---

### 1. Overall Design & Architecture

**Q1.1 – Why is the project split into `models`, `storage`, `services`, and `cli` instead of using a single script?**  
**A**: This follows separation of concerns and layered architecture:
- `models.py` holds only domain data structures (e.g. `Task`, `TaskStatus`).
- `storage.py` is responsible for persistence (JSON file I/O).
- `services.py` contains business logic and rules (create, update, validate tasks).
- `cli.py` handles user interaction and argument parsing.  
This structure makes the project more testable, easier to extend (e.g. new storage backend), and closer to real-world applications.

**Q1.2 – How does the dependency flow between modules work?**  
**A**: The flow is one-directional:
- `models` has no project-internal dependencies.
- `storage` depends on `models`.
- `services` depends on both `models` and `storage`.
- `cli` depends on `services` (and indirectly on `storage` and `models`).  
Higher layers never depend on lower-level implementation details directly (e.g. CLI does not work with JSON or files).

---

### 2. Dataclasses & Enums

**Q2.1 – What advantages does `@dataclass` provide for the `Task` model?**  
**A**: `@dataclass` automatically generates boilerplate like `__init__`, `__repr__`, and `__eq__`, while supporting type hints and default values. This is ideal for simple “data holder” classes like `Task`, which mainly store attributes such as `title`, `description`, `status`, and timestamps. It keeps the code concise and easier to maintain.

**Q2.2 – Why is `Task` defined with `slots=True` and what are the trade-offs?**  
**A**: `slots=True`:
- Reduces memory usage by avoiding per-instance `__dict__`.
- Speeds up attribute access.
- Prevents adding new attributes dynamically, which can catch some bugs early.  
Trade-offs include slightly more complexity (e.g. less dynamic flexibility) and some limitations around inheritance and certain libraries that expect a `__dict__`.

**Q2.3 – Why does `TaskStatus` inherit from both `str` and `Enum`?**  
**A**: Inheriting from `str` and `Enum` gives:
- Type-safe enum semantics (limited set of valid values).
- String behaviour for interoperability: values can be easily serialized to JSON and used as CLI choices.  
This is useful here because statuses are stored in JSON and passed via string-based CLI arguments.

---

### 3. Type Hints & Static Analysis

**Q3.1 – How do type hints improve this codebase, even though Python doesn’t enforce them at runtime?**  
**A**: Type hints:
- Clarify function signatures and expected types, improving readability.
- Help IDEs provide better autocomplete and inline documentation.
- Allow static analysis tools (like mypy or Pyright) to catch type mismatches early.  
For example, `list_tasks(self, status: Optional[TaskStatus] = None) -> List[Task]` documents exactly what callers can pass and what they receive.

**Q3.2 – How would you introduce static type checking (like mypy) into this project?**  
**A**: Steps might include:
- Add `mypy` to dependencies (e.g. in `requirements-dev.txt`).
- Configure `mypy.ini` or `pyproject.toml` to point at the `app` package.
- Run `mypy app` as part of CI or a pre-commit hook.  
Because the code already uses type hints, adoption would be relatively straightforward.

---

### 4. Error Handling & Custom Exceptions

**Q4.1 – Why define custom exceptions such as `StorageError` and `TaskNotFoundError`?**  
**A**: Custom exceptions provide:
- A clearer domain language for failures (e.g. “task not found” vs. generic `ValueError`).
- Better separation between layers: storage wraps low-level I/O/JSON problems in `StorageError`, and services translate repository issues into domain-level `TaskNotFoundError`.  
This allows the CLI to catch and display user-friendly messages without needing to know low-level details.

**Q4.2 – How does the CLI layer handle different error types?**  
**A**: In `cli.py`, the `main` function:
- Wraps command handling in `try/except` blocks.
- Catches `TaskNotFoundError`, `StorageError`, and `ValueError`.
- Prints descriptive, color-coded error messages using `rich`.  
This keeps error presentation separate from both business logic and storage logic.

---

### 5. Repository Pattern & Persistence

**Q5.1 – What is the repository pattern, and how is it implemented here?**  
**A**: The repository pattern abstracts data access behind a consistent API. Here:
- `JsonFileTaskRepository` in `storage.py` exposes methods like `list_tasks`, `get_by_id`, `add`, `update`, and `delete`.
- The repository hides details such as JSON serialization, filesystem access, and error handling.  
`TaskService` relies only on this API and does not care whether data comes from a file, database, or external service.

**Q5.2 – How could you swap JSON storage for a database without changing the CLI?**  
**A**: You would:
- Implement a new repository class (e.g. `SqlTaskRepository`) with the same method signatures.
- Change `build_service` in `cli.py` (or configuration) to construct the new repository instead of `JsonFileTaskRepository`.  
Because the CLI talks only to `TaskService` and `TaskService` talks to an abstract repository interface, no other layers need modification.

---

### 6. Dependency Injection & Testability

**Q6.1 – How is dependency injection used in `TaskService`?**  
**A**: `TaskService` accepts its repository via the constructor (`__init__(self, repository)`), instead of constructing it internally. This means:
- The concrete repository can be decided in one place (`build_service`).
- Tests can inject a fake or in-memory repository to exercise logic without touching the filesystem.

**Q6.2 – How would you unit test `TaskService` methods like `create_task` or `change_status`?**  
**A**: Typical approach:
- Create a fake repository class with an in-memory list of `Task` objects, implementing `add`, `list_tasks`, etc.
- Inject this fake repository into `TaskService`.
- Call `create_task` and assert tasks were added correctly (e.g. non-empty title, default status).
- Call `change_status` and assert the status changed and timestamps updated.  
No real files or JSON parsing are needed, which makes tests fast and reliable.

---

### 7. Context Managers & Filesystem

**Q7.1 – What problem does the `_locked_file` context manager in `storage.py` solve?**  
**A**: `_locked_file`:
- Ensures the parent directory exists before writing.
- Serves as a single place to manage file access pre/post conditions (and could later add real locking or logging).  
It demonstrates how to encapsulate resource management using `@contextmanager`, making the rest of the code cleaner (`with _locked_file(path) as fp:`).

**Q7.2 – Why is `pathlib.Path` preferred over string paths in this project?**  
**A**: `Path`:
- Provides OS-independent behaviour.
- Offers convenient methods like `read_text`, `write_text`, `mkdir`, and operator `/` for path joining.
- Makes code more readable and less error-prone than manual string concatenation.

---

### 8. CLI with `argparse` and `rich`

**Q8.1 – How does the CLI map subcommands to business operations?**  
**A**: `_parse_args` in `cli.py`:
- Creates subparsers for commands: `create`, `list`, `status`, `delete`.
- Each subparser defines its own arguments.  
`main` then checks `args.command` and calls corresponding `TaskService` methods (`create_task`, `list_tasks`, `change_status`, `delete_task`), keeping CLI logic thin and delegating real work to the service layer.

**Q8.2 – What benefits does `rich` bring to the CLI, and why might this matter in an interview?**  
**A**: `rich`:
- Produces colored, nicely formatted output (e.g. tables for `list`).
- Improves UX and demonstrates familiarity with third-party libraries and their integration.
- Encourages clean separation between data (from services) and presentation (tables, colors).  
In interviews, it shows attention to developer and user experience, not just “making it work”.

---

### 9. Immutability & Data Updates

**Q9.1 – What does `dataclasses.replace` do in `update_details`, and why use it?**  
**A**: `dataclasses.replace(task, title=..., description=...)`:
- Creates a new `Task` instance copying all fields from `task`, except those explicitly overridden.
- Encourages an immutable-update style (don’t mutate in place), which can reduce bugs when data is shared across components or cached.

**Q9.2 – When would you choose immutable-style updates in production systems?**  
**A**: Scenarios include:
- Functional or event-sourced architectures where state changes are tracked over time.
- Concurrency-heavy code where shared mutable state can cause race conditions.
- Systems where you want to easily roll back, compare versions, or cache results.  
In such systems, immutability makes reasoning about state transitions simpler.

---

### 10. Entry Points & Packaging

**Q10.1 – What is the role of `app/main.py`, and how is it used with `python -m`?**  
**A**: `app/main.py` provides:
- `run()` as a single entry point.
- An `if __name__ == "__main__": run()` block.  
Running `python -m app` executes the package as a module and ultimately calls `run()`, which invokes the CLI `main` function and exits with the appropriate code.

**Q10.2 – How would you expose this CLI as a `console_script` in a real package?**  
**A**: In `pyproject.toml` or `setup.cfg`, you’d define something like:
- `console_scripts = {"taskmgr": "app.main:run"}`  
After installing the package (`pip install .`), users could simply run `taskmgr` from any shell, without needing `python -m`.

---

### 11. Behaviour & Extensions

**Q11.1 – If you wanted to add a priority field to `Task`, what layers would you need to change?**  
**A**: You’d:
- Add `priority` to `Task` in `models.py`.
- Update serialization/deserialization logic in `storage.py` (`_task_to_dict`, `_task_from_dict`).
- Potentially extend `TaskService` methods to validate or default priority.
- Update `cli.py` to allow specifying priority via CLI arguments and display it in the table.  
Because of the layered design, changes are localized and predictable.

**Q11.2 – How could you extend this app to support tags or due dates, and what would you focus on when designing that?**  
**A**: Similar steps: update the model, storage, services, and CLI. Design-wise:
- Decide data structures (e.g. list of strings for tags, `datetime` for due dates).
- Ensure backward compatibility for existing JSON (e.g. provide defaults if fields are missing).
- Provide clear CLI options (e.g. `--tag`, `--due`) and consistent filtering behaviour.  
This shows the ability to extend an existing design without breaking it.

