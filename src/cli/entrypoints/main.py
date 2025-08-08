# src/cli/entrypoints/main.py

from __future__ import annotations

import sys

# For now, reuse project root main
from main import main as project_main  # type: ignore


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        return project_main(argv)
    except SystemExit as exc:  # allow passthrough
        return int(exc.code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
