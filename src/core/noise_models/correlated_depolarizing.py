"""
Correlated Depolarizing Noise for Topology-Dependent Error Studies

Depolarizing noise with pair correlations along entanglement topology edges.
This enables in-simulation tests of the structured decoherence hypothesis:

- correlation_strength > 0: errors correlated along topology edges
- correlation_strength = 0: standard independent depolarizing (baseline)
- correlation_strength < 0: errors anti-correlated along topology edges

Comparing NTC across these three conditions is the definitive simulation test.
"""

import logging
from typing import Any

import numpy as np
from qiskit_aer.noise import NoiseModel, pauli_error

from src.core.analysis.core.topology import TOPOLOGY_BUILDERS

from .base_noise import BaseNoise

logger = logging.getLogger("QuantumExperiment.NoiseModels")


class CorrelatedDepolarizingNoise(BaseNoise):
    """Depolarizing noise with topology-dependent pair correlations."""

    def __init__(
        self,
        error_rate: float = 0.05,
        num_qubits: int = 3,
        correlation_strength: float = 0.3,
        topology: str = "GHZ",
        custom_topology: np.ndarray | None = None,
        experiment_id: str = "N/A",
    ):
        """
        Args:
            error_rate: Base per-gate depolarizing probability.
            num_qubits: Number of qubits.
            correlation_strength: Bias factor for correlated Pauli errors
                on topology-connected pairs. Range [-1, 1].
                Positive = correlated, negative = anti-correlated, 0 = standard.
            topology: Topology name ("GHZ", "W", "CLUSTER", "CHAIN", "STAR", "ALL_TO_ALL").
            custom_topology: Explicit adjacency matrix (overrides topology name).
            experiment_id: Experiment tracking ID.
        """
        super().__init__(
            error_rate=error_rate, num_qubits=num_qubits, experiment_id=experiment_id
        )

        if not -1.0 <= correlation_strength <= 1.0:
            raise ValueError(
                f"correlation_strength must be in [-1, 1], got {correlation_strength}"
            )

        self.correlation_strength = correlation_strength
        self.topology_name = topology.upper()

        if custom_topology is not None:
            self.topology_matrix = np.asarray(custom_topology, dtype=np.float64)
        elif self.topology_name in TOPOLOGY_BUILDERS:
            self.topology_matrix = TOPOLOGY_BUILDERS[self.topology_name](num_qubits)
        else:
            raise ValueError(
                f"Unknown topology '{topology}'. "
                f"Provide custom_topology or use one of: {list(TOPOLOGY_BUILDERS)}"
            )

        # Pairs connected in topology
        self.connected_pairs: list[tuple[int, int]] = []
        for i in range(num_qubits):
            for j in range(i + 1, num_qubits):
                if self.topology_matrix[i, j] > 0:
                    self.connected_pairs.append((i, j))

        self.log_noise_creation(
            "CORRELATED_DEPOLARIZING",
            {
                "correlation_strength": correlation_strength,
                "topology": self.topology_name,
                "connected_pairs": self.connected_pairs,
            },
        )

    def apply(
        self,
        noise_model: NoiseModel,
        gate_list: list[str],
        qubits_for_error: int | None = None,
    ) -> None:
        """Apply correlated depolarizing noise to the noise model.

        - Single-qubit gates get standard depolarizing noise.
        - Two-qubit gates get a custom 2-qubit Pauli channel where correlated
          errors (XX, YY, ZZ) are boosted/suppressed based on correlation_strength,
          but only for qubit pairs connected in the topology.
        """
        from qiskit_aer.noise import depolarizing_error

        one_qubit_gates = {
            "id", "u1", "u2", "u3", "h", "x", "y", "z", "s", "t", "sx", "rz", "ry", "rx",
        }
        two_qubit_gates = {"cx", "cy", "cz", "ch", "swap", "iswap", "ecr"}

        # 1) Standard single-qubit depolarizing on all 1q gates
        for gate in gate_list:
            if gate in one_qubit_gates:
                try:
                    err = depolarizing_error(self.error_rate, 1)
                    noise_model.add_all_qubit_quantum_error(err, gate)
                except Exception:
                    pass

        # 2) Two-qubit gates: correlated channel for connected pairs,
        #    standard 2q depol for non-connected pairs
        for gate in gate_list:
            if gate not in two_qubit_gates:
                continue

            # Standard 2q depolarizing for non-connected pairs
            try:
                standard_2q = depolarizing_error(self.error_rate, 2)
            except Exception:
                continue

            if abs(self.correlation_strength) < 1e-10:
                # No correlation -- just use standard 2q depol everywhere
                noise_model.add_all_qubit_quantum_error(standard_2q, gate)
                continue

            # Build correlated channel for connected pairs
            correlated_2q = self._build_correlated_2q_channel()

            # Apply per-pair: correlated on connected pairs, standard on others
            for i in range(self.num_qubits):
                for j in range(i + 1, self.num_qubits):
                    pair = (i, j)
                    if pair in self.connected_pairs:
                        noise_model.add_quantum_error(correlated_2q, gate, [i, j])
                        noise_model.add_quantum_error(correlated_2q, gate, [j, i])
                    else:
                        noise_model.add_quantum_error(standard_2q, gate, [i, j])
                        noise_model.add_quantum_error(standard_2q, gate, [j, i])

    def _build_correlated_2q_channel(self) -> Any:
        """Build a 2-qubit Pauli error channel with correlation bias.

        Uses a mixing formula between standard 2q depolarizing and a
        purely correlated (or purely uncorrelated) channel:

        For cs >= 0 (correlated bias):
            Mixed channel = (1-cs) * standard_depol + cs * correlated_only
            Result: correlated Paulis get (1-cs)*p/15 + cs*p/3
                    uncorrelated Paulis get (1-cs)*p/15

        For cs < 0 (anti-correlated bias), let t = |cs|:
            Mixed channel = (1-t) * standard_depol + t * uncorrelated_only
            Result: correlated Paulis get (1-t)*p/15
                    uncorrelated Paulis get (1-t)*p/15 + t*p/12

        Total error probability is preserved at p in all cases.
        """
        p = self.error_rate
        cs = self.correlation_strength

        if cs >= 0:
            corr_prob = (1 - cs) * p / 15.0 + cs * p / 3.0
            uncorr_prob = (1 - cs) * p / 15.0
        else:
            t = abs(cs)
            corr_prob = (1 - t) * p / 15.0
            uncorr_prob = (1 - t) * p / 15.0 + t * p / 12.0

        # Identity probability = 1 - total error (conserved at 1 - p)
        total_error = 3 * corr_prob + 12 * uncorr_prob
        identity_prob = max(1.0 - total_error, 0.0)

        # Build Pauli error terms
        paulis_1q = ["I", "X", "Y", "Z"]
        correlated_labels = {"XX", "YY", "ZZ"}

        noise_ops = []
        for p1 in paulis_1q:
            for p2 in paulis_1q:
                label = p1 + p2
                if label == "II":
                    if identity_prob > 1e-15:
                        noise_ops.append((label, identity_prob))
                elif label in correlated_labels:
                    if corr_prob > 1e-15:
                        noise_ops.append((label, corr_prob))
                else:
                    if uncorr_prob > 1e-15:
                        noise_ops.append((label, uncorr_prob))

        return pauli_error(noise_ops)

    def get_kraus_operators(self) -> list[np.ndarray]:
        """Kraus operators for the correlated channel (delegated to Qiskit)."""
        return []

    def get_physics_description(self) -> dict[str, str]:
        return {
            "mechanism": (
                "Depolarizing noise with topology-dependent pair correlations. "
                "Errors on connected qubit pairs are biased toward correlated "
                "Paulis (XX, YY, ZZ)."
            ),
            "origin": "Simulation model for testing structured decoherence hypothesis",
            "correlation_strength": str(self.correlation_strength),
            "topology": self.topology_name,
        }
