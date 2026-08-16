"""Phase flip noise (random Pauli-Z errors).

# The Phase Flip Channel - Longitudinal Decoherence
Phase flip noise represents longitudinal environmental coupling where computational
basis states maintain their populations while acquiring random phase factors.
This models decoherence that preserves measurement statistics while corrupting
quantum interference patterns.

# Physical Mechanism
Phase flip errors arise from longitudinal coupling to environmental fields:
- Magnetic field fluctuations causing random Z rotations
- Electric field noise in gate-defined quantum dots
- Charge noise fluctuations in semiconductor qubits
- Nuclear spin bath interactions in solid-state systems

# Mathematical Description
The phase flip channel maps quantum states as:
ρ → (1-p)ρ + p(ZρZ) where Z is the Pauli Z operator
Kraus operators: K₀ = √(1-p)I, K₁ = √p Z

# Hardware Origins
- Magnetic field noise from environmental sources
- Voltage noise in gate electrodes
- Charge fluctuations in semiconductor devices
- Nuclear spin bath decoherence in solid-state qubits

# Educational Framework
Phase flip channels demonstrate core concepts:
- Longitudinal vs transverse environmental coupling
- Preservation of measurement probabilities with interference loss
- Classical vs quantum information corruption
- Z-basis errors and their measurement signatures
"""

import logging
from typing import Any

import numpy as np
from qiskit_aer.noise import NoiseModel, pauli_error

from src.core.math import PAULI_I, PAULI_Z

from .base_noise import BaseNoise

logger = logging.getLogger(__name__)


class PhaseFlipNoise(BaseNoise):
    """Phase flip noise model (random Pauli-Z errors).

    # Quantum Phase Flip Definition
    The phase flip channel models longitudinal decoherence by applying random
    Z (phase flip) operations with probability p. This preserves computational
    basis populations while corrupting quantum interference.

    This is measurement-preserving decoherence that affects quantum
    coherence without changing classical measurement statistics.

    # Physical Interpretation
    Phase flip noise models environmental coupling that is:
    - **Longitudinal**: Couples along Z direction of Bloch sphere
    - **Population-preserving**: Maintains |0⟩ and |1⟩ probabilities
    - **Interference-destroying**: Eliminates quantum superposition effects
    - **Classical-preserving**: Maintains classical measurement correlations

    # Educational Significance
    Phase flip channels illustrate fundamental concepts:
    - **Longitudinal Coupling**: Environmental interaction along measurement axis
    - **Classical Information**: Preservation of classical information content
    - **Quantum Interference**: Destruction of quantum coherence effects
    - **Dephasing Mechanisms**: Alternative to pure dephasing channels
    """

    NOISE_TYPE = "PHASE_FLIP"
    IS_UNITAL = True
    CATALOG = {
        "description": "Random Z rotations preserving computational basis populations",
        "mechanism": "Longitudinal coupling to environmental fields",
        "use_case": "Modeling dephasing that preserves measurement statistics",
        "typical_origin": "Magnetic field noise, charge fluctuations",
        "educational_concepts": "Longitudinal coupling, classical information preservation, interference destruction",
    }

    def __init__(
        self,
        error_rate: float = 0.05,
        num_qubits: int = 1,
        experiment_id: str = "N/A",
        magnetic_field_noise: float | None = None,
        charge_noise: float | None = None,
    ):
        """Initialize phase flip noise with physics-based validation.

        # Physics Parameter Integration
        Supports both phenomenological flip rates and physics-based
        environmental noise calculations:
        - Phenomenological: Direct specification of phase flip probability p
        - Magnetic noise: Calculate from magnetic field fluctuations
        - Charge noise: Calculate from electric field/voltage fluctuations

        Args:
            error_rate: Phenomenological phase flip probability p ∈ [0, 1]
            num_qubits: Number of qubits (phase flip is single-qubit)
            experiment_id: Unique identifier for experimental tracking
            magnetic_field_noise: RMS magnetic field fluctuations (Tesla)
            charge_noise: RMS charge/voltage fluctuations (eV)

        Raises:
            ValueError: If parameters violate physics constraints

        Example:
            >>> # Phenomenological phase flip
            >>> noise = PhaseFlipNoise(error_rate=0.01)

            >>> # Physics-based magnetic noise
            >>> noise = PhaseFlipNoise(
            ...     magnetic_field_noise=1e-6  # 1 μT RMS field noise
            ... )
        """
        # Physics parameter validation before initialization
        self._validate_phase_flip_params(error_rate, magnetic_field_noise, charge_noise)

        # Store physics parameters
        self.magnetic_field_noise = magnetic_field_noise
        self.charge_noise = charge_noise

        # Calculate effective phase flip rate
        if magnetic_field_noise is not None or charge_noise is not None:
            # Physics-based calculation
            self._physics_flip_rate = self._calculate_physics_flip_rate()
            effective_error_rate = self._physics_flip_rate
        else:
            # Use phenomenological rate
            self._physics_flip_rate = error_rate
            effective_error_rate = error_rate

        # Initialize base noise with effective rate
        super().__init__(
            error_rate=effective_error_rate,
            num_qubits=num_qubits,
            experiment_id=experiment_id,
            magnetic_field_noise=magnetic_field_noise,
            charge_noise=charge_noise,
        )

        # Calculate derived properties
        self._flip_probabilities = self._calculate_flip_probabilities()

        # Log creation with physics context
        self.log_noise_creation(
            "PHASE_FLIP",
            {
                "physics_flip_rate": self._physics_flip_rate,
                "flip_probabilities": self._flip_probabilities,
                "magnetic_field_noise": magnetic_field_noise,
                "charge_noise": charge_noise,
                "decoherence_type": "longitudinal_population_preserving",
                "channel_property": "unital",
            },
        )

    def apply(
        self, noise_model: NoiseModel, gate_list: list[str], qubits_for_error: int | None = None
    ) -> None:
        """Apply phase flip noise to quantum gates.

        # Longitudinal Error Implementation
        Creates Qiskit Pauli error channels that model phase flip transitions:
        random Z operations that preserve computational basis populations while
        destroying quantum interference patterns.

        # Gate Application Strategy
        A single, uniform single-qubit Pauli-Z error with probability p is applied
        to every target gate, exactly matching the documented Kraus operators
        K₀ = √(1-p)I, K₁ = √p Z. Two-qubit gates (which cannot accept a 1-qubit
        error) are skipped and reported as failures.

        Args:
            noise_model: Qiskit noise model to modify with phase flip errors
            gate_list: Quantum gates to apply noise to
            qubits_for_error: Override qubit count (phase flip uses 1)

        Example:
            >>> noise_model = NoiseModel()
            >>> gates = ['h', 'x']
            >>> phase_flip_noise.apply(noise_model, gates)
        """
        # Phase flip is inherently single-qubit but can affect all operations
        if qubits_for_error is not None and qubits_for_error != 1:
            logger.warning(
                f"Phase flip is single-qubit, but applying to {qubits_for_error}-qubit gates"
            )

        # Uniform single-qubit phase-flip channel: K₀ = √(1-p)I, K₁ = √p Z
        p = self.error_rate
        phase_flip_channel = pauli_error([("I", 1.0 - p), ("Z", p)])

        # Apply the same channel to every target gate
        successful_gates = []
        failed_gates = []

        for gate in gate_list:
            try:
                noise_model.add_all_qubit_quantum_error(phase_flip_channel, gate)
                successful_gates.append(gate)
            except Exception as e:
                failed_gates.append((gate, str(e)))

        # Log application results with physics context
        if successful_gates:
            logger.info(
                f"Applied PHASE_FLIP noise (p={self.error_rate:.4f}) to "
                f"gates: {successful_gates} "
                f"(magnetic={self.magnetic_field_noise}, charge={self.charge_noise}) "
                f"(experiment: {self.experiment_id})"
            )

        if failed_gates:
            logger.warning(
                f"Failed to apply PHASE_FLIP noise to gates: {[gate for gate, _ in failed_gates]}"
            )

    def get_kraus_operators(self) -> list[np.ndarray]:
        """Return Kraus operators for the phase flip channel.

        # Mathematical Construction
        For phase flip channel with flip probability p:
        K₀ = √(1-p) I  (identity with no phase flip)
        K₁ = √p Z      (Pauli Z phase flip)

        These satisfy K₀†K₀ + K₁†K₁ = I (completeness relation).

        Returns:
            List of Kraus operators as numpy arrays

        Educational Note:
            The Z operator K₁ = [[1,0],[0,-1]] adds -1 phase to |1⟩ state
            while leaving |0⟩ unchanged, preserving populations.
        """
        p = self.error_rate

        # Identity operator (no phase flip)
        K0 = np.sqrt(1 - p) * PAULI_I

        # Pauli Z operator (phase flip)
        K1 = np.sqrt(p) * PAULI_Z

        return [K0, K1]

    def get_physics_description(self) -> dict[str, str]:
        """Return comprehensive physics description of phase flip decoherence.

        Returns:
            Dict with educational physics content about longitudinal coupling
        """
        return {
            "mechanism": "Longitudinal phase flip: random Z rotations preserving computational basis populations",
            "origin": "Magnetic field fluctuations, charge noise, voltage drifts causing random phase shifts",
            "mathematical_form": f"K₀ = √(1-{self.error_rate:.3f})I, K₁ = √{self.error_rate:.3f}Z",
            "magnetic_noise": f"Magnetic field noise = {self.magnetic_field_noise:.2e}T"
            if self.magnetic_field_noise
            else "phenomenological rate",
            "charge_noise": f"Charge noise = {self.charge_noise:.2e}eV"
            if self.charge_noise
            else "no charge coupling",
            "population_preservation": "Computational basis populations |0⟩ and |1⟩ are exactly preserved",
            "channel_properties": "Unital (preserves maximally mixed states), trace-preserving, completely positive",
            "real_world_examples": "Superconducting qubit flux noise, trapped ion magnetic field fluctuations, quantum dot charge noise",
            "quantum_principles": "Longitudinal coupling, classical information preservation, quantum interference destruction",
        }

    def get_theoretical_properties(self) -> dict[str, Any]:
        """Get theoretical quantum properties specific to phase flip channels.

        Returns:
            Dict with phase flip channel specific properties
        """
        return {
            "decoherence_type": "longitudinal_population_preserving",
            "channel_classification": "unital",
            "flip_probability": self.error_rate,
            "no_flip_probability": 1 - self.error_rate,
            "magnetic_field_noise": self.magnetic_field_noise,
            "charge_noise": self.charge_noise,
            "population_preservation": "exact",
            "interference_destruction": "complete_for_superposition",
            "measurement_bias": "none_populations_preserved",
            "pauli_operator": "Z_longitudinal_coupling",
            "unitality": True,
            "reversibility": False,  # Information loss is irreversible
            "information_capacity": self._calculate_channel_capacity(),
        }

    def _validate_phase_flip_params(
        self, error_rate: float, magnetic_field_noise: float | None, charge_noise: float | None
    ) -> None:
        """Validate phase flip parameters against physics constraints.

        # Physics Constraint Validation
        Ensures all parameters represent realistic phase flip scenarios
        consistent with quantum mechanics and environmental noise physics.
        """
        # Validate flip probability
        if not 0 <= error_rate <= 1:
            raise ValueError(f"Phase flip rate must be in [0,1], got {error_rate}")

        # Validate magnetic field noise if provided
        if magnetic_field_noise is not None and magnetic_field_noise < 0:
            raise ValueError(
                f"Magnetic field noise must be non-negative, got {magnetic_field_noise}"
            )

        # Validate charge noise if provided
        if charge_noise is not None and charge_noise < 0:
            raise ValueError(f"Charge noise must be non-negative, got {charge_noise}")

    def _calculate_physics_flip_rate(self) -> float:
        """Calculate phase flip rate from physics parameters.

        # Physics-Based Rate Calculation
        Converts environmental noise parameters to effective phase flip rates
        using realistic coupling strengths and timescales.

        Returns:
            Effective phase flip rate from environmental parameters
        """
        flip_rate = 0.0

        # Magnetic field contribution
        if self.magnetic_field_noise is not None:
            # Gyromagnetic ratio for electron spin
            gamma = 2.8e10  # rad/(s⋅Tesla)
            gate_time = 20e-9  # 20 ns typical gate time

            # Phase accumulation from field fluctuations
            phase_variance = (gamma * self.magnetic_field_noise * gate_time) ** 2
            magnetic_contribution = min(1.0, phase_variance / (2 * np.pi) ** 2)
            flip_rate += magnetic_contribution

        # Charge noise contribution
        if self.charge_noise is not None:
            # Typical energy scale for phase sensitivity
            typical_energy = 1e-3  # eV
            charge_contribution = min(1.0, (self.charge_noise / typical_energy) ** 2)
            flip_rate += charge_contribution

        return min(1.0, flip_rate)

    def _calculate_flip_probabilities(self) -> dict[str, float]:
        """Calculate individual flip probabilities for educational display.

        Returns:
            Dict mapping operators to their probabilities
        """
        return {"identity": 1 - self.error_rate, "phase_flip_z": self.error_rate}

    def _calculate_channel_capacity(self) -> float:
        """Calculate quantum channel capacity for phase flip channel.

        # Information Theory
        Channel capacity for phase flip depends on the flip probability
        and preservation of classical information.
        """
        p = self.error_rate
        if p == 0:
            return 1.0  # Perfect channel
        elif p == 1:
            return 0.0  # Always flip (deterministic but reduces capacity)
        elif p == 0.5:
            return 0.0  # Maximally noisy for coherent information
        else:
            # Classical information preserved, quantum coherence lost
            return max(0, 1 - p)  # Simplified capacity estimate

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        if self.magnetic_field_noise or self.charge_noise:
            physics_info = []
            if self.magnetic_field_noise:
                physics_info.append(f"B_noise={self.magnetic_field_noise:.2e}T")
            if self.charge_noise:
                physics_info.append(f"q_noise={self.charge_noise:.2e}eV")
            return (
                f"Phase flip: {', '.join(physics_info)}, p={self.error_rate:.4f} "
                f"[longitudinal coupling]"
            )
        else:
            return f"Phase flip: p={self.error_rate:.4f} [phenomenological longitudinal error]"
