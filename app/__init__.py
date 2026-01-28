"""
Small, modular "Task Manager" example project.

This package is intentionally simple but structured to demonstrate
mid-level Python concepts in a real-world style layout:

- models: dataclasses and type hints for domain objects
- storage: file-based repository with clean interfaces
- services: business logic separated from I/O
- cli: user interface implemented with argparse and rich
"""

__all__ = ["models", "storage", "services", "cli"]
