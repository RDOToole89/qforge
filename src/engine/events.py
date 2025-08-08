"""Event interfaces (Phase 0 skeleton)."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Event:
    name: str
    payload: Dict[str, Any]


class EventBus:
    def publish(self, event: Event) -> None:  # pragma: no cover
        pass
