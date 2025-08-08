"""Event interfaces (Phase 5: basic bus)."""

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Callable, List, Optional


RUN_START = "run_start"
RUN_END = "run_end"
SWEEP_START = "sweep_start"
SWEEP_END = "sweep_end"
PROGRESS = "progress"


@dataclass
class Event:
    name: str
    timestamp: str
    payload: Dict[str, Any]


class EventBus:
    def subscribe(self, handler: Callable[[Event], None]) -> None:  # pragma: no cover
        raise NotImplementedError

    def unsubscribe(self, handler: Callable[[Event], None]) -> None:  # pragma: no cover
        raise NotImplementedError

    def publish(self, event: Event) -> None:  # pragma: no cover
        raise NotImplementedError


class SimpleEventBus(EventBus):
    def __init__(self) -> None:
        self._handlers: List[Callable[[Event], None]] = []

    def subscribe(self, handler: Callable[[Event], None]) -> None:
        if handler not in self._handlers:
            self._handlers.append(handler)

    def unsubscribe(self, handler: Callable[[Event], None]) -> None:
        if handler in self._handlers:
            self._handlers.remove(handler)

    def publish(self, event: Event) -> None:
        for h in list(self._handlers):
            try:
                h(event)
            except Exception:
                # Handlers should not break publisher
                continue


def make_event(name: str, payload: Optional[Dict[str, Any]] = None) -> Event:
    return Event(name=name, timestamp=datetime.now().isoformat(), payload=payload or {})
