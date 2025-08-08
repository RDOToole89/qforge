"""Thin runner wrapper (Phase 3 wiring).

Calls legacy core runner and returns (circuit, raw_result).
"""

from __future__ import annotations
from typing import Dict, Any, Tuple

from src.core.experiment_runner import ExperimentRunner


_NOISE_MAP = {
    None: None,
    "depolarizing": "DEPOLARIZING",
    "phase_flip": "PHASE_FLIP",
    "amplitude_damping": "AMPLITUDE_DAMPING",
    "phase_damping": "PHASE_DAMPING",
    "thermal_relaxation": "THERMAL_RELAXATION",
    "bit_flip": "BIT_FLIP",
}


def _map_noise_type(noise_type: str | None) -> str | None:
    if noise_type is None:
        return None
    return _NOISE_MAP.get(noise_type, noise_type.upper())


def run_raw(config: Dict[str, Any]) -> Tuple[Any, Any]:
    """Execute using legacy core runner, return (circuit, raw_result).

    Args:
        config: experiment config dict
    Returns:
        (QuantumCircuit, qiskit result payload)
    """
    runner = ExperimentRunner(experiment_id=config.get("experiment_id", "engine-run"))

    noise_enabled = bool(config.get("noise_enabled", False))
    noise_type = _map_noise_type(config.get("noise_type")) or "DEPOLARIZING"

    circuit, raw = runner.run_experiment(
        num_qubits=int(config["num_qubits"]),
        state_type=str(config["state_type"]).upper(),
        noise_type=noise_type,
        noise_enabled=noise_enabled,
        shots=int(config.get("shots", 1024)),
        sim_mode=str(config.get("sim_mode", "qasm")),
        error_rate=config.get("error_rate"),
        z_prob=config.get("z_prob"),
        i_prob=config.get("i_prob"),
        t1=config.get("t1"),
        t2=config.get("t2"),
        custom_params=config.get("custom_params"),
        rng_seed=config.get("rng_seed"),
    )
    return circuit, raw
