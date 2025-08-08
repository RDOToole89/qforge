# src/cli/entrypoints/main.py

from __future__ import annotations

import sys

# For now, reuse project root main
from .args import dispatch


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    try:
        return dispatch(argv)
    except SystemExit as exc:
        return int(exc.code or 0)


if __name__ == "__main__":
    raise SystemExit(main())
