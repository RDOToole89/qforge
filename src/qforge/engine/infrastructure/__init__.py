"""Infrastructure Module.

Cross-cutting infrastructure components:
- events: Event bus for progress tracking and notifications
- logging: Centralized logging configuration and formatters
"""

from .events import (
    ALL,
    PROGRESS,
    RUN_END,
    RUN_START,
    SWEEP_END,
    SWEEP_START,
    Event,
    SimpleEventBus,
    Subscription,
    make_event,
)
from .logging import event_log_handler, setup_logging

__all__ = [
    "SimpleEventBus",
    "Event",
    "Subscription",
    "make_event",
    "RUN_START",
    "RUN_END",
    "SWEEP_START",
    "SWEEP_END",
    "PROGRESS",
    "ALL",
    "setup_logging",
    "event_log_handler",
]
