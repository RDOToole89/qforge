from __future__ import annotations

from main import run_sweep_from_manifest as legacy_run_sweep


def run_from_manifest(path: str) -> None:
    legacy_run_sweep(path)
