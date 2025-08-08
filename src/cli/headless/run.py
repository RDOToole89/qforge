from __future__ import annotations

from typing import Optional, Dict, Any

from main import run_experiment_by_name as legacy_run_by_name
from main import run_from_config as legacy_run_from_config


def run_by_name(name: str) -> None:
    legacy_run_by_name(name)


def run_from_config(path: str) -> None:
    legacy_run_from_config(path)
