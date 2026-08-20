"""Provenance collection for experiment reproducibility.

Gathers software versions, host info, git SHA, and execution metadata
into a typed Provenance block attached to every ExperimentResult.
"""

from __future__ import annotations

import logging
from datetime import datetime

from qforge.engine.models import ExperimentConfig, Provenance

logger = logging.getLogger(__name__)


def build_provenance(
    cfg: ExperimentConfig,
    execution_time_seconds: float | None = None,
    hardware_metadata: dict | None = None,
) -> Provenance:
    """Build a Provenance block with software, host, and simulator info.

    When hardware_metadata is provided (from sim_mode='hardware'),
    populates simulator_info and transpilation_summary with backend,
    job, calibration, and transpilation details.
    """
    if hardware_metadata and hardware_metadata.get("hardware_result"):
        hw = hardware_metadata["hardware_result"]
        sim_info = {
            "sim_mode": "hardware",
            "backend_name": hw.job_info.backend_name,
            "job_id": hw.job_info.job_id,
            "shots": cfg.shots,
            "execution_time_seconds": hw.job_info.execution_time_seconds,
        }
        transp = {
            "optimization_level": hw.transpilation_info.optimization_level,
            "original_depth": hw.transpilation_info.original_depth,
            "transpiled_depth": hw.transpilation_info.transpiled_depth,
            "original_gate_count": hw.transpilation_info.original_gate_count,
            "transpiled_gate_count": hw.transpilation_info.transpiled_gate_count,
            "swap_count": hw.transpilation_info.swap_count,
            "qubit_layout": hw.transpilation_info.qubit_layout,
            "basis_gates": hw.transpilation_info.basis_gates,
            "calibration_snapshot": hw.calibration_snapshot,
        }
    else:
        sim_info = {
            "sim_mode": cfg.sim_mode,
            "shots": cfg.shots,
            "noise_enabled": cfg.noise_enabled,
            "noise_type": cfg.noise_type,
            "error_rate": cfg.error_rate,
        }
        transp = {}

    return Provenance(
        schema_version="1.0.0",
        timestamp=datetime.now().isoformat(),
        software_versions=_collect_software_versions(),
        host_info=_collect_host_info(),
        git_sha=_get_git_sha(),
        rng_seed=cfg.rng_seed,
        simulator_info=sim_info,
        transpilation_summary=transp,
        execution_time_seconds=execution_time_seconds,
        memory_usage_mb=None,
    )


def _collect_software_versions() -> dict[str, str]:
    """Collect versions of key dependencies."""
    import sys

    versions: dict[str, str] = {"python": sys.version.split()[0]}
    for pkg in ("qiskit", "qiskit_aer", "qiskit_ibm_runtime", "numpy", "pydantic"):
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
