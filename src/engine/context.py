"""Application Context (Phase 0 skeleton).

Holds runtime configuration that should not be read as globals by the engine.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class AppContext:
    base_results_dir: str = "results"
    viz_backend: str = "matplotlib"
    logging_mode: str = "human"  # human|json
    profiles_root: Optional[str] = None
