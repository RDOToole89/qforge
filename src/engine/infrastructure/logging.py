"""Centralized logging configuration for the engine.

Provides a single ``setup_logging()`` call that wires console (and optional
file) handlers to the ``"src"`` logger hierarchy, so every ``logging.getLogger(__name__)``
call inside ``src.*`` automatically inherits the configuration.

Two formatters are available:

- **HumanFormatter** — readable terminal output::

      2026-02-20 16:15:03 INFO     src.engine.api: Starting experiment

- **JsonFormatter** — one JSON object per line for machine consumption::

      {"ts": "2026-02-20T16:15:03", "level": "INFO", "logger": "src.engine.api", "msg": "Starting experiment"}

The ``event_log_handler`` bridges the engine's ``SimpleEventBus`` events into
stdlib logging so lifecycle events (RUN_START, RUN_END, PROGRESS, …) appear
in the configured log output.
"""

from __future__ import annotations

import json as _json
import logging
import sys
from datetime import datetime
from pathlib import Path

_CONFIGURED = False


class HumanFormatter(logging.Formatter):
    """Clean, readable log format for terminal use."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


class JsonFormatter(logging.Formatter):
    """Structured JSON-line format for machine consumption."""

    def format(self, record: logging.LogRecord) -> str:
        return _json.dumps({
            "ts": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        })


def setup_logging(
    level: str = "INFO",
    mode: str = "human",
    log_file: str | Path | None = None,
) -> logging.Logger:
    """Configure logging for the framework.

    Targets the ``"src"`` logger so all ``src.*`` modules inherit the config.
    Safe to call multiple times — subsequent calls update level and formatter.

    Parameters
    ----------
    level : str
        Python log level name (DEBUG, INFO, WARNING, ERROR).
    mode : str
        ``"human"`` for readable terminal output, ``"json"`` for structured lines.
    log_file : optional path
        If provided, also write logs to this file.

    Returns
    -------
    logging.Logger
        The configured ``"src"`` root logger.
    """
    global _CONFIGURED

    root = logging.getLogger("src")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = JsonFormatter() if mode == "json" else HumanFormatter()

    if not _CONFIGURED:
        console = logging.StreamHandler(sys.stderr)
        console.setFormatter(formatter)
        root.addHandler(console)
        _CONFIGURED = True
    else:
        for h in root.handlers:
            h.setFormatter(formatter)

    if log_file is not None:
        path = Path(log_file).resolve()
        # Avoid adding duplicate file handlers for the same path.
        existing = {
            Path(h.baseFilename).resolve()
            for h in root.handlers
            if isinstance(h, logging.FileHandler)
        }
        if path not in existing:
            path.parent.mkdir(parents=True, exist_ok=True)
            fh = logging.FileHandler(str(path))
            fh.setFormatter(formatter)
            root.addHandler(fh)

    return root


def event_log_handler(event) -> None:
    """Event bus subscriber that logs engine events.

    Subscribe to ``ALL`` on a ``SimpleEventBus`` to bridge events into logging::

        bus.subscribe(ALL, event_log_handler)
    """
    logger = logging.getLogger("src.engine.events")
    payload_str = ", ".join(f"{k}={v}" for k, v in event.payload.items())
    logger.info("%s: %s", event.name, payload_str)
