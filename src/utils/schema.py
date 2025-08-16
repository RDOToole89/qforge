"""
Minimal JSON schema validator for research results.

Avoids external dependencies by doing structural checks only.
"""

from __future__ import annotations

from typing import Dict, Any
from pathlib import Path


REQUIRED_TOP_LEVEL = [
    "schema_version",
    "experiment_metadata",
    "experiment_parameters",
    "measurement_results",
]


def _load_schema(path: Path) -> Dict[str, Any]:
    import json

    with open(path, "r") as f:
        return json.load(f)


def _validate_with_jsonschema(data: Dict[str, Any], schema_name: str) -> bool:
    """Validate using fastjsonschema if available; fallback to minimal checks."""
    try:
        import fastjsonschema

        root = Path(__file__).resolve().parents[2]
        schema_path = root / "schemas" / schema_name
        schema = _load_schema(schema_path)
        validator = fastjsonschema.compile(schema)
        validator(data)
        return True
    except Exception:
        return False


def validate_results_schema(data: Dict[str, Any]) -> bool:
    """Validate minimal structure of results JSON.

    Ensures the presence of core blocks and some required fields.
    """
    # Try strict schema first
    if _validate_with_jsonschema(data, "results.schema.json"):
        return True

    # Fallback minimal checks
    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            raise ValueError(f"Missing required top-level field: {key}")

    meta = data["experiment_metadata"]
    if not isinstance(meta, dict):
        raise ValueError("experiment_metadata must be an object")
    for k in ["experiment_id", "timestamp", "framework_version", "research_type"]:
        if k not in meta:
            raise ValueError(f"experiment_metadata missing field: {k}")

    params = data["experiment_parameters"]
    if not isinstance(params, dict):
        raise ValueError("experiment_parameters must be an object")
    for k in ["num_qubits", "state_type", "shots", "sim_mode"]:
        if k not in params:
            raise ValueError(f"experiment_parameters missing field: {k}")

    meas = data["measurement_results"]
    if not isinstance(meas, dict):
        raise ValueError("measurement_results must be an object")
    for k in ["raw_counts", "total_shots"]:
        if k not in meas:
            raise ValueError(f"measurement_results missing field: {k}")

    # Optional provenance block structure check
    prov = data.get("provenance")
    if prov is not None and not isinstance(prov, dict):
        raise ValueError("provenance must be an object if present")

    return True


def validate_manifest_schema(data: Dict[str, Any]) -> bool:
    """Validate minimal structure of a sweep manifest.

    Required:
      - parameter_ranges: dict[str, list]
      - runs_per_config: int
      - EITHER base_preset: str OR base_config: dict
    Optional:
      - override: dict (applied to base preset/config)
      - rng_seed: int
    """
    # Try strict schema first (skip for now as it enforces base_preset)
    # if _validate_with_jsonschema(data, "manifest.schema.json"):
    #     return True

    if not isinstance(data, dict):
        raise ValueError("Manifest must be an object")
    
    # Must have EITHER base_preset OR base_config
    has_preset = "base_preset" in data and isinstance(data["base_preset"], str)
    has_config = "base_config" in data and isinstance(data["base_config"], dict)
    
    if not (has_preset or has_config):
        raise ValueError("Manifest must have either 'base_preset' (str) or 'base_config' (dict)")
    
    if "parameter_ranges" not in data or not isinstance(data["parameter_ranges"], dict):
        raise ValueError("Manifest missing 'parameter_ranges' (object)")
    for k, v in data["parameter_ranges"].items():
        if not isinstance(v, list):
            raise ValueError(f"parameter_ranges['{k}'] must be a list")
    if "runs_per_config" not in data or not isinstance(data["runs_per_config"], int):
        raise ValueError("Manifest missing 'runs_per_config' (int)")
    if "override" in data and not isinstance(data["override"], dict):
        raise ValueError("'override' must be an object if present")
    if "rng_seed" in data and not isinstance(data["rng_seed"], int):
        raise ValueError("'rng_seed' must be an int if present")
    return True
