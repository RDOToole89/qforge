"""Event interfaces and lightweight pub/sub bus (no back-compat).

Purpose
-------
A tiny, dependency-free event system for the engine. Orchestrators publish
structured lifecycle events; observers subscribe to specific events (or ALL)
without coupling.

Key points
----------
- Explicit subscriptions: you MUST name the event (or use ALL).
- Synchronous delivery on publisher's thread.
- Thread-safe (RLock) and best-effort (handler errors are suppressed).
- Ergonomic: returns a Subscription handle; supports `with` for auto-unsub.
- Convenience: `publish_progress(fraction, message, meta=...)`.

Canonical events
----------------
RUN_START, RUN_END, SWEEP_START, SWEEP_END, PROGRESS

Typical usage
-------------
    from src.engine.events import (
        SimpleEventBus, make_event, RUN_START, RUN_END, PROGRESS, ALL
    )

    bus = SimpleEventBus()

    # subscribe to everything (explicit ALL)
    def log_all(ev): print(ev.name, ev.payload)
    bus.subscribe(ALL, log_all)

    # subscribe to progress only
    def on_prog(ev): print(ev.payload.get("fraction", 0.0))
    bus.subscribe(PROGRESS, on_prog)

    # publish events
    bus.publish(make_event(RUN_START, {"config_hash": "abc123"}))
    bus.publish_progress(fraction=0.5, message="Halfway")
    bus.publish(make_event(RUN_END, {"ok": True}))
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import RLock
from typing import Any, Callable, Literal, Union

# ---- Canonical event names ---------------------------------------------------

RUN_START: Literal["run_start"] = "run_start"
RUN_END: Literal["run_end"] = "run_end"
SWEEP_START: Literal["sweep_start"] = "sweep_start"
SWEEP_END: Literal["sweep_end"] = "sweep_end"
PROGRESS: Literal["progress"] = "progress"

# Explicit wildcard (must be used to subscribe to all)
ALL: Literal["*"] = "*"

EventName = Literal["run_start", "run_end", "sweep_start", "sweep_end", "progress"]
EventKey = Union[EventName, Literal["*"]]

# ---- Event structure ---------------------------------------------------------


@dataclass(frozen=True)
class Event:
    """Immutable event payload delivered to subscribers.

    Attributes
    ----------
    name : EventName
        Canonical event name (see constants above).
    timestamp : str
        ISO-8601 timestamp when the event object was created.
    payload : Dict[str, Any]
        Structured payload (keep small & serializable).
    """

    name: EventName
    timestamp: str
    payload: dict[str, Any]


Handler = Callable[[Event], None]


# ---- Bus interface & subscription handle ------------------------------------


class Subscription:
    """Handle for an active subscription (supports context-manager)."""

    __slots__ = ("_bus", "_name", "_handler", "_active")

    def __init__(self, bus: SimpleEventBus, name: EventKey, handler: Handler) -> None:
        self._bus = bus
        self._name = name
        self._handler = handler
        self._active = True

    def unsubscribe(self) -> None:
        if self._active:
            self._bus.unsubscribe(self._name, self._handler)
            self._active = False

    def __enter__(self) -> Subscription:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.unsubscribe()


class SimpleEventBus:
    """Minimal, thread-safe pub/sub bus with explicit event subscriptions.

    Features
    --------
    - Subscribe to a specific `EventName` or `ALL`.
    - Synchronous, ordered delivery (subscription order).
    - Handlers are isolated; exceptions are suppressed.
    - Thread-safe via RLock.

    Notes
    -----
    Publishing is synchronous. If you need async, wrap handlers yourself or
    extend this class.
    """

    def __init__(self) -> None:
        self._by_name: dict[EventName, list[Handler]] = {
            RUN_START: [],
            RUN_END: [],
            SWEEP_START: [],
            SWEEP_END: [],
            PROGRESS: [],
        }
        self._wildcard: list[Handler] = []
        self._lock = RLock()

    def subscribe(self, name: EventKey, handler: Handler) -> Subscription:
        """Subscribe `handler` to a specific event `name` or `ALL`."""
        with self._lock:
            if name == ALL:
                if handler not in self._wildcard:
                    self._wildcard.append(handler)
            else:
                lst = self._by_name[name]
                if handler not in lst:
                    lst.append(handler)
        return Subscription(self, name, handler)

    def unsubscribe(self, name: EventKey, handler: Handler) -> None:
        """Unsubscribe `handler` from `name` (or `ALL`)."""
        with self._lock:
            if name == ALL:
                if handler in self._wildcard:
                    self._wildcard.remove(handler)
            else:
                lst = self._by_name.get(name)
                if lst and handler in lst:
                    lst.remove(handler)

    def publish(self, event: Event) -> None:
        """Publish an event to all matching subscribers (synchronous)."""
        with self._lock:
            specific = list(self._by_name.get(event.name, []))
            wildcard = list(self._wildcard)

        for h in (*specific, *wildcard):
            try:
                h(event)
            except Exception:
                # Best-effort delivery: one bad handler never stops others.
                continue

    # ---- Convenience helper --------------------------------------------------

    def publish_progress(
        self,
        *,
        fraction: float,
        message: str = "",
        meta: dict[str, Any] | None = None,
    ) -> None:
        """Publish a standardized PROGRESS event.

        Parameters
        ----------
        fraction : float
            Progress in [0, 1] (clamped).
        message : str
            Optional human-readable message.
        meta : Optional[Dict[str, Any]]
            Extra context (e.g., {"i": 3, "total": 10, "label": "beta=0.2"}).
        """
        f = max(0.0, min(1.0, float(fraction)))
        payload = {"fraction": f, "message": message}
        if meta:
            payload.update(meta)
        self.publish(make_event(PROGRESS, payload))


# ---- Factory ----------------------------------------------------------------


def make_event(name: EventName, payload: dict[str, Any] | None = None) -> Event:
    """Create an `Event` with ISO-8601 timestamp."""
    return Event(name=name, timestamp=datetime.now().isoformat(), payload=payload or {})


__all__ = [
    # constants / types
    "RUN_START",
    "RUN_END",
    "SWEEP_START",
    "SWEEP_END",
    "PROGRESS",
    "ALL",
    "EventName",
    "EventKey",
    # classes & helpers
    "Event",
    "SimpleEventBus",
    "Subscription",
    "make_event",
]
