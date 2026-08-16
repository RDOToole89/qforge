"""Depolarizing noise (isotropic Pauli errors).

# The Depolarizing Channel - Fundamental Quantum Decoherence
Depolarizing noise represents the most fundamental quantum decoherence mechanism:
uniform mixing of any quantum state with the maximally mixed state. It models
worst-case environmental coupling where all quantum information is equally degraded.

# Physical Mechanism
Depolarizing channels arise from random, uncorrelated coupling to all environmental
degrees of freedom. The quantum state experiences random Pauli errors (X, Y, Z)
with equal probability, creating isotropic decoherence that destroys all quantum
correlations uniformly.

# Mathematical Description
The depolarizing channel maps quantum states as:
ρ → (1-p)ρ + p(I/2^n) where p is the depolarizing probability
Kraus operators: √(1-3p/4)I, √(p/4)X, √(p/4)Y, √(p/4)Z (single qubit)

# Hardware Origins
- High-temperature environments with many environmental modes
- Multiple simultaneous error sources (electromagnetic, thermal, mechanical)
- Poorly isolated qubits with broad-spectrum environmental coupling
- Overdamped systems where coherent dynamics are completely suppressed

# Educational Framework
Depolarizing channels demonstrate fundamental quantum information concepts:
- Unital channels and their preservation of the maximally mixed state
- The relationship between Pauli errors and computational basis measurements
- Physical bounds on decoherence rates and quantum information preservation
- The connection between environmental symmetries and decoherence isotropy
"""

import logging
from typing import Any

import numpy as np
from qiskit.quantum_info import Kraus
from qiskit_aer.noise import NoiseModel, depolarizing_error

from src.core.math import PAULI_I, PAULI_X, PAULI_Y, PAULI_Z

from .base_noise import BaseNoise

logger = logging.getLogger(__name__)


class DepolarizingNoise(BaseNoise):
    """Depolarizing noise model (isotropic Pauli errors).

    # Quantum Decoherence Definition
    The depolarizing channel creates isotropic decoherence by applying random
    Pauli errors with equal probability. For n qubits:
    ρ → (1-p)ρ + p(I/2^n) where p ∈ [0, 1-1/4^n]

    This is the most symmetric possible decoherence, often used as a
    worst-case baseline noise model.

    # Physical Interpretation
    Depolarizing noise models environmental coupling that is:
    - **Isotropic**: No preferred direction in state space
    - **Memoryless**: Independent errors at each time step
    - **Unital**: Preserves maximally mixed states
    - **Worst-case**: Destroys quantum information most efficiently

    # Educational Significance
    Depolarizing channels illustrate fundamental concepts:
    - **Pauli Error Model**: X, Y, Z errors and their measurement signatures
    - **Channel Bounds**: Physical limits on decoherence rates (p ≤ 1-1/4^n)
    - **Unital Property**: Preservation of maximally mixed states
    - **Information Geometry**: Uniform contraction in quantum state space
    """

    NOISE_TYPE = "DEPOLARIZING"
    IS_UNITAL = True
    CATALOG = {
        "description": "Uniform random Pauli errors creating isotropic decoherence",
        "mechanism": "Random coupling to all environmental degrees of freedom",
        "use_case": "Baseline worst-case noise model",
        "typical_origin": "High-temperature environments, multiple error sources",
        "educational_concepts": "Pauli channels, unital maps, worst-case noise",
    }

    def __init__(self, error_rate: float = 0.05, num_qubits: int = 1, experiment_id: str = "N/A"):
        """Initialize depolarizing noise with physics-compliant validation.

        # Physics Constraint Validation
        Depolarizing channels have fundamental physical bounds:
        - Single qubit: p ≤ 3/4 (cannot exceed maximally mixed state)
        - n qubits: p ≤ 1-1/4^n (complete positivity constraint)
        - p = 0: Perfect quantum channel (no decoherence)
        - p = p_max: Maximally depolarizing channel

        Args:
            error_rate: Depolarizing probability p ∈ [0, 1-1/4^n]
            num_qubits: Number of qubits affected by noise (determines bounds)
            experiment_id: Unique identifier for experimental tracking

        Raises:
            ValueError: If error_rate exceeds physical bounds for given qubit count

        Example:
            >>> # Single-qubit depolarizing noise
            >>> noise = DepolarizingNoise(error_rate=0.01, num_qubits=1)

            >>> # Two-qubit depolarizing noise
            >>> noise = DepolarizingNoise(error_rate=0.05, num_qubits=2)
        """
        # Validate error rate against physical bounds before initialization
        self._validate_depolarizing_bounds(error_rate, num_qubits)

        # Initialize base noise with validated parameters
        super().__init__(error_rate=error_rate, num_qubits=num_qubits, experiment_id=experiment_id)

        # Store depolarizing-specific properties
        self._max_error_rate = 1 - (1 / (4**num_qubits))
        self._pauli_probabilities = self._calculate_pauli_probabilities()

        # Log creation with physics context
        self.log_noise_creation(
            "DEPOLARIZING",
            {
                "max_physical_rate": self._max_error_rate,
                "pauli_probabilities": self._pauli_probabilities,
                "decoherence_type": "isotropic_uniform",
                "channel_property": "unital",
            },
        )

    def apply(
        self, noise_model: NoiseModel, gate_list: list[str], qubits_for_error: int | None = None
    ) -> None:
        """Apply depolarizing noise to quantum gates in the noise model.

        # Depolarizing Channel Implementation
        Creates Qiskit depolarizing error channels that apply random Pauli errors
        with probability p/4 for each of X, Y, Z, and identity with probability 1-3p/4.
        This implements the standard depolarizing channel definition.

        # Gate Application Strategy
        Depolarizing noise affects all quantum operations during their execution:
        - Single-qubit gates: Apply single-qubit depolarizing errors
        - Two-qubit gates: Apply two-qubit depolarizing errors
        - Multi-qubit gates: Apply n-qubit depolarizing errors
        - Measurement: Can optionally include readout errors

        Args:
            noise_model: Qiskit noise model to modify with depolarizing errors
            gate_list: Quantum gates to apply noise to during execution
            qubits_for_error: Override qubit count (None uses self.num_qubits)

        Example:
            >>> noise_model = NoiseModel()
            >>> gates = ['h', 'x', 'cx']
            >>> depol_noise.apply(noise_model, gates)
            >>> # Now noise_model includes depolarizing errors on H, X, CNOT gates
        """
        # Define gate arity for standard gates
        one_qubit_gates = {
            "id",
            "u1",
            "u2",
            "u3",
            "h",
            "x",
            "y",
            "z",
            "s",
            "t",
            "sx",
            "rz",
            "ry",
            "rx",
        }
        two_qubit_gates = {"cx", "cy", "cz", "ch", "swap", "iswap", "ecr"}

        successful_gates = []
        failed_gates = []

        for gate in gate_list:
            try:
                # Determine required qubits for this gate
                if gate in one_qubit_gates:
                    gate_qubits = 1
                elif gate in two_qubit_gates:
                    gate_qubits = 2
                else:
                    # For unknown gates, try to use the system size or skip
                    # If qubits_for_error is explicitly provided, use that
                    if qubits_for_error is not None:
                        gate_qubits = qubits_for_error
                    else:
                        # Skip unknown gates to avoid dimension mismatch errors
                        logger.debug(f"Skipping unknown gate '{gate}' for depolarizing noise")
                        continue

                # Create depolarizing error channel for this specific gate size
                # We use self.error_rate as the channel parameter
                try:
                    channel = depolarizing_error(self.error_rate, gate_qubits)
                except Exception as e:
                    logger.warning(
                        f"Could not create depolarizing channel for {gate_qubits} qubits: {e}"
                    )
                    continue

                # Apply error to all instances of this gate type
                noise_model.add_all_qubit_quantum_error(channel, gate)
                successful_gates.append(gate)

            except Exception as e:
                failed_gates.append((gate, str(e)))

        # Log application results with educational context
        if successful_gates:
            logger.info(
                f"Applied DEPOLARIZING noise (p={self.error_rate:.4f}) to "
                f"gates: {successful_gates} "
                f"(experiment: {self.experiment_id})"
            )

        if failed_gates:
            logger.warning(
                f"Failed to apply DEPOLARIZING noise to gates: "
                f"{[gate for gate, _ in failed_gates]}. "
                f"This may indicate gate-noise compatibility issues."
            )

        # Educational logging of physics properties
        logger.debug(
            f"Depolarizing channel properties: "
            f"error_rate={self.error_rate:.4f}, "
            f"max_rate={self._max_error_rate:.4f}, "
            f"pauli_probs={self._pauli_probabilities}"
        )

    def get_kraus_operators(self) -> list[np.ndarray]:
        """Return Kraus operators for the depolarizing channel.

        # Mathematical Construction
        For single-qubit depolarizing channel with error rate p:
        K₀ = √(1-3p/4) I  (identity with survival probability)
        K₁ = √(p/4) X     (X error with probability p/4)
        K₂ = √(p/4) Y     (Y error with probability p/4)
        K₃ = √(p/4) Z     (Z error with probability p/4)

        For n > 1 qubits this returns the Kraus operators of the genuine
        n-qubit depolarizing channel (Qiskit ``depolarizing_error(p, n)``) so
        that ``get_kraus_operators()`` matches the channel ``apply()`` simulates.
        Note this is NOT the tensor product of n single-qubit channels (which is
        a different map with identity weight (1-3p/4)ⁿ).

        Returns:
            List of Kraus operators as numpy arrays

        Educational Note:
            Kraus operators satisfy ∑ᵢ Kᵢ† Kᵢ = I (completeness relation)
            ensuring the channel is trace-preserving.
        """
        if self.num_qubits == 1:
            # Single-qubit closed form (equivalent to depolarizing_error(p, 1)).
            pauli_ops = [PAULI_I, PAULI_X, PAULI_Y, PAULI_Z]
            pauli_probs = [1 - 3 * self.error_rate / 4] + [self.error_rate / 4] * 3
            return [np.sqrt(prob) * op for prob, op in zip(pauli_probs, pauli_ops, strict=True)]

        # Genuine n-qubit depolarizing channel, matching apply().
        channel = Kraus(depolarizing_error(self.error_rate, self.num_qubits))
        return [np.asarray(op, dtype=complex) for op in channel.data]

    def get_physics_description(self) -> dict[str, str]:
        """Return comprehensive physics description of depolarizing decoherence.

        Returns:
            Dict with educational physics content about depolarizing channels
        """
        return {
            "mechanism": "Random Pauli errors (X, Y, Z) applied with equal probability, creating uniform mixing with maximally mixed state",
            "origin": "Isotropic environmental coupling to all degrees of freedom - electromagnetic, thermal, and mechanical noise sources",
            "mathematical_form": f"ρ → (1-{self.error_rate:.3f})ρ + {self.error_rate:.3f}(I/2^{self.num_qubits})",
            "kraus_representation": f"√(1-3p/4)I + √(p/4)(X + Y + Z) for single qubit, tensor products for {self.num_qubits} qubits",
            "physical_bounds": f"Error rate p ≤ {self._max_error_rate:.4f} for {self.num_qubits} qubits (complete positivity constraint)",
            "channel_properties": "Unital (preserves maximally mixed states), trace-preserving, completely positive",
            "real_world_examples": "High-temperature superconducting qubits, overdamped trapped ions, noisy photonic systems",
            "quantum_principles": "Pauli error model, quantum channel theory, environmental decoherence symmetries",
        }

    def get_theoretical_properties(self) -> dict[str, Any]:
        """Get theoretical quantum properties specific to depolarizing channels.

        Returns:
            Dict with depolarizing channel specific properties
        """
        return {
            "decoherence_type": "isotropic_uniform",
            "channel_classification": "unital",
            "pauli_error_rates": self._pauli_probabilities,
            "maximum_error_rate": self._max_error_rate,
            "fidelity_decay": 1 - self.error_rate,
            "entropy_increase": self._calculate_entropy_increase(),
            "coherence_preservation": "none_global_mixing",
            "measurement_bias": "uniform_all_outcomes",
            "symmetry_properties": "SO(3)_invariant_in_bloch_sphere",
            "information_capacity": max(0, 1 - 2 * self.error_rate),
            "channel_rank": 4**self.num_qubits,
            "unitality": True,
        }

    def _validate_depolarizing_bounds(self, error_rate: float, num_qubits: int) -> None:
        """Validate error rate against depolarizing channel physical bounds.

        # Physical Constraint Derivation
        Depolarizing channels must satisfy complete positivity, which constrains
        the maximum error rate: p ≤ 1 - 1/4ⁿ for n qubits.
        This ensures the channel maps positive semidefinite operators to positive
        semidefinite operators.
        """
        max_rate = 1 - (1 / (4**num_qubits))

        if error_rate > max_rate:
            raise ValueError(
                f"Depolarizing error rate {error_rate:.4f} exceeds physical bound "
                f"{max_rate:.4f} for {num_qubits} qubits. This would violate "
                f"complete positivity and create an unphysical quantum channel."
            )

        if error_rate < 0:
            raise ValueError(f"Error rate must be non-negative, got {error_rate:.4f}")

    def _calculate_pauli_probabilities(self) -> dict[str, float]:
        """Calculate individual Pauli error probabilities for educational display.

        Returns:
            Dict mapping Pauli operators to their error probabilities
        """
        return {
            "identity": 1 - 3 * self.error_rate / 4,
            "pauli_x": self.error_rate / 4,
            "pauli_y": self.error_rate / 4,
            "pauli_z": self.error_rate / 4,
        }

    def _calculate_entropy_increase(self) -> float:
        """Calculate von Neumann entropy increase for depolarizing channel.

        # Information Theory
        Depolarizing channels increase entropy by mixing pure states with
        the maximally mixed state. For pure input states:
        S_out = -p log₂(2^(-n)) - (1-p) log₂(1) = p·n

        Returns:
            Entropy increase in bits
        """
        if self.error_rate == 0:
            return 0.0
        elif self.error_rate == self._max_error_rate:
            return self.num_qubits  # Maximum entropy
        else:
            # Approximate entropy increase for partial depolarization
            return self.error_rate * self.num_qubits

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        return (
            f"Depolarizing noise: {self.num_qubits}-qubit, "
            f"error_rate={self.error_rate:.4f} "
            f"(max={self._max_error_rate:.4f}) [isotropic decoherence]"
        )
