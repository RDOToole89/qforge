"""Engine-native runner wrapper.

Uses engine-native experiment runner instead of legacy core dependencies.
"""

from __future__ import annotations
from typing import Dict, Any, Tuple

from .experiment_runner import run_raw as engine_run_raw


def run_raw(config: Dict[str, Any]) -> Tuple[Any, Any]:
    """Execute using engine-native runner, return (circuit, raw_result).

    Args:
        config: experiment config dict
    Returns:
        (QuantumCircuit, qiskit result payload)
    """
    return engine_run_raw(config)
