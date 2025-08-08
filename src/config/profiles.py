"""
Profiles management for the Quantum Experiment Framework.

This module allows saving and loading named profiles that capture
common settings and defaults for experiments. Profiles are stored
as JSON files under the `profiles/` directory at the repository root.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Optional

from .settings import settings


PROFILES_DIR = Path("profiles")


def _ensure_profiles_dir() -> None:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def list_profiles() -> List[str]:
    """List available profile names (without .json extension)."""
    _ensure_profiles_dir()
    return [p.stem for p in PROFILES_DIR.glob("*.json")]


def get_current_profile_dict() -> Dict[str, Any]:
    """Capture the current settings/defaults into a serializable dict."""
    defaults = settings.get_experiment_defaults()
    logging_cfg = settings.get_logging_config()
    plugin_cfg = settings.get_plugin_config()
    return {
        "experiment_defaults": defaults,
        "logging": logging_cfg,
        "plugins": plugin_cfg,
    }


def save_profile(name: str, profile: Optional[Dict[str, Any]] = None) -> str:
    """Save a profile JSON under `profiles/<name>.json`.

    Args:
        name: Profile name (filename stem)
        profile: Optional profile dict. If None, capture current settings.

    Returns:
        The absolute path to the saved profile file.
    """
    _ensure_profiles_dir()
    payload = profile or get_current_profile_dict()
    target = PROFILES_DIR / f"{name}.json"
    with open(target, "w") as f:
        json.dump(payload, f, indent=2)
    return str(target.resolve())


def load_profile(name: str) -> Dict[str, Any]:
    """Load a profile by name and return its dict."""
    _ensure_profiles_dir()
    path = PROFILES_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Profile not found: {path}")
    with open(path, "r") as f:
        return json.load(f)


def apply_profile(profile: Dict[str, Any]) -> None:
    """Apply a loaded profile to the global `settings` instance.

    Only known, safe fields are applied.
    """
    # Experiment defaults
    defaults = profile.get("experiment_defaults", {})
    if "num_qubits" in defaults:
        settings.DEFAULT_NUM_QUBITS = int(defaults["num_qubits"])
    if "state_type" in defaults:
        settings.DEFAULT_STATE_TYPE = str(defaults["state_type"])  # noqa: N815
    if "noise_type" in defaults:
        settings.DEFAULT_NOISE_TYPE = str(defaults["noise_type"])  # noqa: N815
    if "noise_enabled" in defaults:
        settings.DEFAULT_NOISE_ENABLED = bool(defaults["noise_enabled"])  # noqa: N815
    if "shots" in defaults:
        settings.DEFAULT_SHOTS = int(defaults["shots"])  # noqa: N815
    if "sim_mode" in defaults:
        settings.DEFAULT_SIM_MODE = str(defaults["sim_mode"])  # noqa: N815
    if "error_rate" in defaults:
        settings.DEFAULT_ERROR_RATE = float(defaults["error_rate"])  # noqa: N815
    if "t1" in defaults:
        settings.DEFAULT_T1 = float(defaults["t1"])  # noqa: N815
    if "t2" in defaults:
        settings.DEFAULT_T2 = float(defaults["t2"])  # noqa: N815
    if "z_prob" in defaults:
        settings.DEFAULT_Z_PROB = float(defaults["z_prob"])  # noqa: N815
    if "i_prob" in defaults:
        settings.DEFAULT_I_PROB = float(defaults["i_prob"])  # noqa: N815
    if "cluster_lattice" in defaults:
        settings.DEFAULT_CLUSTER_LATTICE = str(
            defaults["cluster_lattice"]
        )  # noqa: N815

    # Logging config
    logging_cfg = profile.get("logging", {})
    if "results_dir" in logging_cfg:
        settings.DEFAULT_RESULTS_DIR = str(logging_cfg["results_dir"])  # noqa: N815
    if "logs_dir" in logging_cfg:
        settings.DEFAULT_LOGS_DIR = str(logging_cfg["logs_dir"])  # noqa: N815
    if "log_level" in logging_cfg:
        settings.DEFAULT_LOG_LEVEL = str(logging_cfg["log_level"])  # noqa: N815

    # No return; settings modified in place
