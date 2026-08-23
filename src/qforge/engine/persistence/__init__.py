"""Persistence Module.

Data persistence and artifact management:
- storage: Result persistence and artifact management
- hashing: Deterministic configuration hashing
"""

from .hashing import sha1_of
from .storage import LocalStorage

__all__ = [
    "LocalStorage",
    "sha1_of",
]
