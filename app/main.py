from __future__ import annotations

import sys

from .cli import ExitCode, main as cli_main


def run() -> None:
    """
    Entry point for running as a module.

    Example:
        python -m app create "Read about mid-level Python"
    """

    code: ExitCode = cli_main()
    sys.exit(int(code))


if __name__ == "__main__":
    run()

