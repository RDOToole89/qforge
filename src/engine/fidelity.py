"""Simulation data extraction and fidelity computation.

Extracts statevectors and density matrices from Qiskit simulation results
and computes fidelity against ideal theoretical states.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def extract_simulation_data(
    raw: Any,
    sim_mode: str,
    state_type: str,
    num_qubits: int,
) -> tuple[
    list[list[list[float]]] | None,  # density_matrix
    list[list[float]] | None,  # statevector
    float | None,  # fidelity
]:
    """Extract simulation-specific data from runner output.

    Returns (density_matrix, statevector, fidelity) — all JSON-safe.
    Complex numbers are serialized as [real, imag] pairs.
    """
    if sim_mode == "qasm":
        return None, None, None

    if sim_mode == "hardware":
        # Hardware provides counts only — estimate fidelity from distribution overlap
        counts = raw.get("counts") if isinstance(raw, dict) else None
        fidelity = _compute_fidelity_from_counts(counts, state_type, num_qubits) if counts else None
        return None, None, fidelity

    try:
        if sim_mode == "statevector" and isinstance(raw, dict):
            sv_obj = raw.get("statevector")
            if sv_obj is None:
                return None, None, None

            sv_data = np.asarray(sv_obj.data, dtype=complex)
            sv_serialized = [[float(c.real), float(c.imag)] for c in sv_data]
            fidelity = _compute_fidelity_statevector(sv_data, state_type, num_qubits)
            return None, sv_serialized, fidelity

        if sim_mode == "density_matrix" and isinstance(raw, dict):
            dm_obj = raw.get("density_matrix")
            if dm_obj is None:
                return None, None, None

            dm_data = np.asarray(dm_obj.data, dtype=complex)
            dm_serialized = [[[float(c.real), float(c.imag)] for c in row] for row in dm_data]
            fidelity = _compute_fidelity_density_matrix(dm_data, state_type, num_qubits)
            return dm_serialized, None, fidelity

    except Exception as e:
        logger.warning(f"Failed to extract simulation data for {sim_mode}: {e}")

    return None, None, None


def _compute_fidelity_statevector(sv: np.ndarray, state_type: str, num_qubits: int) -> float | None:
    """Compute |<psi_ideal|psi_sim>|^2 fidelity for a pure statevector."""
    try:
        from src.core.state_preparation import create_state_instance

        ideal = create_state_instance(state_type, num_qubits).get_theoretical_state_vector()
        overlap = np.abs(np.vdot(ideal, sv)) ** 2
        return float(np.clip(overlap, 0.0, 1.0))
    except Exception as e:
        logger.warning(f"Fidelity computation failed (statevector): {e}")
        return None


def _compute_fidelity_density_matrix(
    dm: np.ndarray, state_type: str, num_qubits: int
) -> float | None:
    """Compute <psi_ideal|rho|psi_ideal> fidelity for a density matrix."""
    try:
        from src.core.state_preparation import create_state_instance

        ideal = create_state_instance(state_type, num_qubits).get_theoretical_state_vector()
        # F = <psi|rho|psi>
        fidelity = float(np.real(ideal.conj() @ dm @ ideal))
        return float(np.clip(fidelity, 0.0, 1.0))
    except Exception as e:
        logger.warning(f"Fidelity computation failed (density_matrix): {e}")
        return None


def _compute_fidelity_from_counts(
    counts: dict[str, int], state_type: str, num_qubits: int
) -> float | None:
    """Estimate fidelity from measurement counts via Bhattacharyya coefficient.

    For hardware results where no statevector/density matrix is available,
    computes the classical fidelity:  F = (Σ_x √(p_ideal(x) · p_obs(x)))²

    This is a lower bound on the true quantum state fidelity.
    """
    try:
        from src.core.state_preparation import create_state_instance

        ideal_sv = create_state_instance(state_type, num_qubits).get_theoretical_state_vector()
        ideal_probs = np.abs(ideal_sv) ** 2

        total_shots = sum(counts.values())
        if total_shots == 0:
            return None

        observed_probs = np.zeros(2**num_qubits)
        for bitstring, count in counts.items():
            idx = int(bitstring, 2)
            if 0 <= idx < len(observed_probs):
                observed_probs[idx] = count / total_shots

        bc = float(np.sum(np.sqrt(ideal_probs * observed_probs)))
        return float(np.clip(bc**2, 0.0, 1.0))
    except Exception as e:
        logger.warning(f"Counts-based fidelity computation failed: {e}")
        return None
