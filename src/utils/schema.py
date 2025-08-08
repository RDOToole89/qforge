"""
Minimal JSON schema validator for research results.

Avoids external dependencies by doing structural checks only.
"""

from __future__ import annotations

from typing import Dict, Any


REQUIRED_TOP_LEVEL = [
    "schema_version",
    "experiment_metadata",
    "experiment_parameters",
    "measurement_results",
]


def validate_results_schema(data: Dict[str, Any]) -> bool:
    """Validate minimal structure of results JSON.

    Ensures the presence of core blocks and some required fields.
    """
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
