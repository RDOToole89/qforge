"""VQE — Variational Quantum Eigensolver for H2.

WHAT YOU'LL LEARN:
  - A molecular Hamiltonian is a weighted sum of Pauli strings
  - The engine estimates each ⟨P⟩; this program turns those into an energy
  - One evaluation is not a full optimizer loop — θ is chosen, then ⟨H⟩ is measured

This uses the published 2-qubit H2 operator at 0.735 Å (STO-3G, parity mapping):

  H = c_II II + c_ZI ZI + c_IZ IZ + c_ZZ ZZ + c_XX XX

Coefficients: Qiskit Aqua / Qiskit Textbook VQE example. ⟨II⟩ = 1 is a constant.
Energy lives here, not in core metrics.

CIRCUIT (2-qubit hardware-efficient ansatz):
  q0: ─Ry(θ)──●── M
  q1: ─Ry(θ)──X── M

  One VQE iteration: prepare → estimate Paulis → E = Σ c_P ⟨P⟩.

TRY IT:
    from qforge.experiments.advanced.deep_dives.dd_vqe import vqe_experiment

    result = vqe_experiment.run()
    print(result.h2_energy, result.h2_fci)

    results = vqe_experiment.run_theta_sweep()
    # Circuit draw is on by default (Qiskit mpl). Off: visualization_type="none"
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from qforge.core.math.observables import pauli_matrix
from qforge.engine.models import ExperimentConfig, ExperimentResult
from qforge.engine.models.measurement import ObservableEstimate
from qforge.experiments.base import BaseExperiment

# Qiskit Aqua "algorithm_introduction_with_vqe" / Qiskit Textbook.
# H2 at 0.735 Å, STO-3G, parity mapping. Pauli labels match QForge MSB-left.
H2_PARITY_STO3G_0_735: dict[str, float] = {
    "II": -1.052373245772859,
    "ZI": 0.39793742484318045,
    "IZ": -0.39793742484318045,
    "ZZ": -0.01128010425623538,
    "XX": 0.18093119978423156,
}

H2_EQUILIBRIUM_ANGSTROM = 0.735

# Lowest eigenvalue of H2_PARITY_STO3G_0_735 (Hartree), electronic.
# This operator's identity shift is not the textbook total-energy (-1.137 Ha)
# convention that folds in nuclear repulsion.
H2_FCI_0_735 = -1.8572750302023795


def h2_pauli_coeffs(
    bond_distance: float = H2_EQUILIBRIUM_ANGSTROM,
    *,
    pauli_coeffs: dict[str, float] | None = None,
) -> dict[str, float]:
    """Return Pauli coefficients for the educational 2-qubit H2 operator.

    Args:
        bond_distance: Internuclear distance in angstroms.
        pauli_coeffs: Optional override (any geometry / mapping).

    Returns:
        Mapping of Pauli string → coefficient. ``II`` is the identity shift.

    Raises:
        ValueError: If ``bond_distance`` is not 0.735 and no override is given.
    """
    if pauli_coeffs is not None:
        return dict(pauli_coeffs)
    if abs(bond_distance - H2_EQUILIBRIUM_ANGSTROM) > 1e-6:
        raise ValueError(
            "This educational Hamiltonian is the published 2-qubit H2 operator "
            f"at {H2_EQUILIBRIUM_ANGSTROM} Å. Pass custom_params['pauli_coeffs'] "
            "for another geometry — do not invent coefficients."
        )
    return dict(H2_PARITY_STO3G_0_735)


def measured_paulis(coeffs: Mapping[str, float]) -> list[str]:
    """Pauli strings the engine must estimate (skip the identity)."""
    return [label for label in coeffs if set(label) - {"I"}]


def fci_energy(coeffs: Mapping[str, float]) -> float:
    """Lowest eigenvalue of Σ c_P P. Classical exact diagonalization."""
    labels = list(coeffs)
    n_qubits = len(labels[0])
    dim = 2**n_qubits
    hamiltonian = np.zeros((dim, dim), dtype=complex)
    identity = np.eye(dim, dtype=complex)
    for label, coeff in coeffs.items():
        if set(label) <= {"I"}:
            hamiltonian += coeff * identity
        else:
            hamiltonian += coeff * pauli_matrix(label)
    eigvals = np.linalg.eigvalsh(hamiltonian)
    return float(np.min(np.real(eigvals)))


def energy_from_estimates(
    estimates: Mapping[str, ObservableEstimate],
    coeffs: Mapping[str, float],
) -> tuple[float, float | None]:
    """E = Σ c_P ⟨P⟩. Identity contributes c_II. Stderr assumes independent terms."""
    energy = 0.0
    variance = 0.0
    have_stderr = True
    for label, coeff in coeffs.items():
        if set(label) <= {"I"}:
            energy += coeff
            continue
        entry = estimates[label]
        energy += coeff * entry.value
        if entry.stderr is None:
            have_stderr = False
        else:
            variance += (coeff * entry.stderr) ** 2
    stderr = math.sqrt(variance) if have_stderr else None
    return float(energy), stderr


def _build_vqe_ansatz(n_qubits: int = 2, depth: int = 1, theta: float = 0.0) -> QuantumCircuit:
    """Build a hardware-efficient Ry + CNOT ansatz."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    for layer in range(depth):
        for q in range(n_qubits):
            qc.ry(theta + 0.5 * layer, q)
        for q in range(n_qubits - 1):
            qc.cx(q, q + 1)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


class VQEExperiment(BaseExperiment):
    """Variational Quantum Eigensolver for the 2-qubit H2 operator."""

    name = "vqe"
    description = "VQE — estimate H2 energy from Pauli observables (one variational evaluation)"
    metrics_hint = (
        "⟨H⟩ is the H2 energy at 0.735 Å from the estimated Paulis. "
        "h2_fci is the exact lowest eigenvalue of this 2-qubit operator (~-1.857 Ha)."
    )

    def default_config(self) -> ExperimentConfig:
        """Return the default configuration for this experiment."""
        return self._config()

    def _config(
        self,
        *,
        theta: float = 0.5,
        depth: int = 1,
        bond_distance: float = H2_EQUILIBRIUM_ANGSTROM,
        pauli_coeffs: dict[str, float] | None = None,
        **kwargs: Any,
    ) -> ExperimentConfig:
        coeffs = h2_pauli_coeffs(bond_distance, pauli_coeffs=pauli_coeffs)
        circuit = _build_vqe_ansatz(n_qubits=2, depth=depth, theta=theta)
        return ExperimentConfig(
            num_qubits=2,
            state_type="CUSTOM",
            shots=4096,
            noise_enabled=False,
            observables=measured_paulis(coeffs),
            custom_params={
                "source": "circuit",
                "circuit": circuit,
                "bond_distance": bond_distance,
                "theta": theta,
                "ansatz_depth": depth,
                "pauli_coeffs": coeffs,
            },
            visualization_type=["histogram", "circuit"],
            **kwargs,
        )

    def run(
        self,
        overrides: Mapping[str, Any] | None = None,
        *,
        ctx: Any | None = None,
    ) -> ExperimentResult:
        """Run one energy evaluation and attach ⟨H⟩ / FCI as extra result fields."""
        merged = dict(overrides or {})
        incoming = dict(merged.get("custom_params") or {})
        theta = float(incoming.get("theta", 0.5))
        depth = int(incoming.get("ansatz_depth", 1))
        distance = float(incoming.get("bond_distance", H2_EQUILIBRIUM_ANGSTROM))
        override_coeffs = incoming.get("pauli_coeffs")
        coeffs = h2_pauli_coeffs(distance, pauli_coeffs=override_coeffs)
        merged["custom_params"] = {
            "source": "circuit",
            "circuit": _build_vqe_ansatz(n_qubits=2, depth=depth, theta=theta),
            "bond_distance": distance,
            "theta": theta,
            "ansatz_depth": depth,
            "pauli_coeffs": coeffs,
        }
        merged.setdefault("observables", measured_paulis(coeffs))
        result = super().run(merged, ctx=ctx)
        estimates = result.analysis.measurement_results.observables or {}
        energy, stderr = energy_from_estimates(estimates, coeffs)
        return result.model_copy(
            update={
                "h2_energy": energy,
                "h2_energy_stderr": stderr,
                "h2_fci": fci_energy(coeffs),
                "h2_bond_distance": distance,
            }
        )

    def run_theta_sweep(
        self,
        thetas: list[float] | None = None,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """Evaluate ⟨H⟩ at several ansatz angles (one VQE iteration each)."""
        angles = thetas if thetas is not None else [0.0, 0.5, 1.0, 1.5, 2.0, math.pi]
        custom = dict(overrides.pop("custom_params", {}) or {})
        results: list[ExperimentResult] = []
        for theta in angles:
            merged = {**overrides, "custom_params": {**custom, "theta": theta}}
            results.append(self.run(merged))
        return results

    def run_noise_sweep(
        self,
        steps: int = 5,
        max_error: float = 0.1,
        **overrides: Any,
    ) -> list[ExperimentResult]:
        """See how depolarizing noise shifts the energy estimate."""
        rates = np.linspace(0.001, max_error, steps).tolist()
        results: list[ExperimentResult] = []
        for rate in rates:
            merged = {
                **overrides,
                "noise_enabled": True,
                "noise_type": "depolarizing",
                "error_rate": rate,
            }
            results.append(self.run(merged))
        return results


vqe_experiment = VQEExperiment()
