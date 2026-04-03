"""Provenance collection for experiment reproducibility.

Gathers software versions, host info, git SHA, and execution metadata
into a typed Provenance block attached to every ExperimentResult.
"""

from __future__ import annotations

import logging
from datetime import datetime

from src.engine.models import ExperimentConfig, Provenance

logger = logging.getLogger(__name__)


def build_provenance(
    cfg: ExperimentConfig,
    execution_time_seconds: float | None = None,
) -> Provenance:
    """Build a Provenance block with software, host, and simulator info."""
    return Provenance(
        schema_version="1.0.0",
        timestamp=datetime.now().isoformat(),
        software_versions=_collect_software_versions(),
        host_info=_collect_host_info(),
        git_sha=_get_git_sha(),
        rng_seed=cfg.rng_seed,
        simulator_info={
            "sim_mode": cfg.sim_mode,
            "shots": cfg.shots,
            "noise_enabled": cfg.noise_enabled,
            "noise_type": cfg.noise_type,
            "error_rate": cfg.error_rate,
        },
        transpilation_summary={},
        execution_time_seconds=execution_time_seconds,
        memory_usage_mb=None,
    )


def _collect_software_versions() -> dict[str, str]:
    """Collect versions of key dependencies."""
    import sys

    versions: dict[str, str] = {"python": sys.version.split()[0]}
    for pkg in ("qiskit", "qiskit_aer", "numpy", "pydantic"):
        try:
            mod = __import__(pkg)
            versions[pkg] = getattr(mod, "__version__", "unknown")
        except ImportError:
            pass
    return versions


def _collect_host_info() -> dict[str, str]:
    """Collect host platform info."""
    import platform

    return {
        "system": platform.system(),
        "machine": platform.machine(),
        "platform": platform.platform(),
    }


def _get_git_sha() -> str | None:
    """Return the current git SHA, or None if unavailable."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return None
