### PythonConceptsMidLevel

Small, modular **Task Manager** example for **mid-level Python concepts**, structured like a real project.

### What this project demonstrates

- **Modular design**
  - `app/models.py`: domain models with `dataclass`, `Enum`, type hints.
  - `app/storage.py`: JSON-file repository, context managers, error translation.
  - `app/services.py`: business logic layer, custom exceptions, dependency injection.
  - `app/cli.py`: `argparse`-based CLI, separation of UI from logic.
- **Mid-level Python features**
  - **dataclasses with slots** for efficient models.
  - **Enums** for safe status values.
  - **context managers** using `@contextmanager`.
  - **path handling** with `pathlib`.
  - **typing** (`Optional`, `List`, custom return types).
  - **clean exceptions**: `StorageError`, `TaskNotFoundError`, validation errors.

### Setup

```bash
cd PythonConceptsMidLevel
python -m venv .venv
.venv\Scripts\activate  # on Windows
pip install -r requirements.txt
```

### Running the example

Use the package as a module:

```bash
python -m app create "Learn mid-level Python"
python -m app list
python -m app status 1 done
python -m app delete 1
```

By default, tasks are stored in `./data/tasks.json`. You can change this with `--db`:

```bash
python -m app --db my_tasks.json list
```

### How to study this project

- **Start with `models.py`** to understand the core domain objects.
- **Read `storage.py`** to see how persistence is abstracted behind a repository.
- **Look at `services.py`** for business rules and error handling.
- **Explore `cli.py`** to see how user commands are mapped to service calls.

Use this as a base and extend it (e.g. priorities, due dates, tags, different storage) to practise mid-level Python in a real-world style structure.