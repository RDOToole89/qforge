"""Phase Flip Noise for Longitudinal Environmental Coupling Research.

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

# Research Significance for Structured Pathways
Phase flip noise creates measurement-preserving decoherence that may reveal
structural pathway effects based on phase relationships rather than population
dynamics, complementing amplitude damping studies.

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

from .base_noise import BaseNoise

logger = logging.getLogger(__name__)


class PhaseFlipNoise(BaseNoise):
    """Phase flip noise model for longitudinal environmental coupling research.

    # Quantum Phase Flip Definition
    The phase flip channel models longitudinal decoherence by applying random
    Z (phase flip) operations with probability p. This preserves computational
    basis populations while corrupting quantum interference.

    This represents measurement-preserving decoherence that affects quantum
    coherence without changing classical measurement statistics.

    # Physical Interpretation
    Phase flip noise models environmental coupling that is:
    - **Longitudinal**: Couples along Z direction of Bloch sphere
    - **Population-preserving**: Maintains |0⟩ and |1⟩ probabilities
    - **Interference-destroying**: Eliminates quantum superposition effects
    - **Classical-preserving**: Maintains classical measurement correlations

    # Research Applications in Pathway Studies
    - **Longitudinal Pathways**: Test how Z-axis coupling creates pathway structure
    - **Population Conservation**: Study pathway behavior with preserved measurements
    - **Classical Comparison**: Compare with bit flip for directional coupling effects
    - **Interference Effects**: Investigate pathway dependence on quantum interference

    # Educational Significance
    Phase flip channels illustrate fundamental concepts:
    - **Longitudinal Coupling**: Environmental interaction along measurement axis
    - **Classical Information**: Preservation of classical information content
    - **Quantum Interference**: Destruction of quantum coherence effects
    - **Dephasing Mechanisms**: Alternative to pure dephasing channels
    """

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
                "research_role": "longitudinal_pathway_investigation",
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
        Phase flip noise affects all quantum operations:
        - Z gates: Minimal additional error (already Z-axis)
        - X/Y gates: Maximum sensitivity (orthogonal to error axis)
        - General gates: Intermediate sensitivity based on Z component

        Args:
            noise_model: Qiskit noise model to modify with phase flip errors
            gate_list: Quantum gates to apply noise to
            qubits_for_error: Override qubit count (phase flip uses 1)

        Example:
            >>> noise_model = NoiseModel()
            >>> gates = ['h', 'x', 'cx']
            >>> phase_flip_noise.apply(noise_model, gates)
        """
        # Phase flip is inherently single-qubit but can affect all operations
        if qubits_for_error is not None and qubits_for_error != 1:
            logger.warning(
                f"Phase flip is single-qubit, but applying to {qubits_for_error}-qubit gates"
            )

        # Gate sensitivity mapping for phase flip errors
        gate_sensitivity = self._get_gate_sensitivity_map()

        # Apply phase flip noise to all gates with sensitivity weighting
        successful_gates = []
        failed_gates = []

        for gate in gate_list:
            try:
                # Get gate-specific sensitivity
                sensitivity = gate_sensitivity.get(gate, 0.5)

                if sensitivity > 0:
                    # Calculate effective flip probability
                    effective_flip_prob = self.error_rate * sensitivity
                    identity_prob = 1.0 - effective_flip_prob

                    # Create Pauli error with phase flip probability
                    phase_flip_channel = pauli_error(
                        [("I", identity_prob), ("Z", effective_flip_prob)]
                    )

                    noise_model.add_all_qubit_quantum_error(phase_flip_channel, gate)
                    successful_gates.append(f"{gate}(s={sensitivity:.2f})")
                else:
                    # Gates with minimal phase flip sensitivity
                    successful_gates.append(f"{gate}(minimal)")

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
        K0 = np.sqrt(1 - p) * np.eye(2, dtype=complex)

        # Pauli Z operator (phase flip)
        K1 = np.sqrt(p) * np.array([[1, 0], [0, -1]], dtype=complex)

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

    def get_research_context(self) -> dict[str, Any]:
        """Get research context for phase flip noise in pathway studies.

        Returns:
            Dict with research context and experimental predictions
        """
        return {
            "pathway_hypothesis": {
                "prediction": "Longitudinal pathway structure with preserved measurement correlations",
                "test_method": "Compare population-preserving vs energy-exchanging pathway behavior",
                "expected_signature": "Classical measurement preservation with quantum interference loss",
            },
            "decoherence_characteristics": {
                "coupling_direction": "Longitudinal Z-axis environmental interaction",
                "topology_dependence": "Moderate - affects quantum interference selectively",
                "pathway_asymmetry": "Minimal - symmetric Z-axis coupling",
                "scaling_behavior": "Interference-dependent scaling with superposition content",
            },
            "experimental_role": {
                "longitudinal_testing": "Primary model for Z-axis environmental coupling analysis",
                "classical_preservation": "Study pathway behavior with preserved classical information",
                "interference_effects": "Test pathway dependence on quantum interference",
                "measurement_invariance": "Investigate pathways with measurement-invariant decoherence",
            },
            "research_predictions": {
                "vs_bit_flip": "Should preserve populations unlike bit flip which corrupts stored information",
                "vs_phase_damping": "Should affect superposition coherence similarly to pure dephasing",
                "measurement_independence": "Pathways should be independent of measurement basis choice",
                "interference_correlations": "Loss of interference with preserved amplitude correlations",
            },
            "educational_applications": {
                "longitudinal_coupling": "Demonstrate Z-axis environmental interaction mechanisms",
                "classical_information": "Show preservation of classical information during decoherence",
                "interference_physics": "Illustrate quantum interference destruction without population change",
                "measurement_theory": "Connect measurement statistics to environmental coupling direction",
            },
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

    def _get_gate_sensitivity_map(self) -> dict[str, float]:
        """Get gate-specific phase flip sensitivity factors.

        # Gate Sensitivity Physics
        Different gates have different sensitivities to phase flip errors:
        - Z gates: Minimal sensitivity (same error axis)
        - X/Y gates: High sensitivity (orthogonal to error axis)
        - General gates: Sensitivity based on non-Z component

        Returns:
            Dict mapping gate names to sensitivity factors [0, 1]
        """
        return {
            # Z-axis gates (minimal sensitivity - same axis as error)
            "z": 0.1,
            "rz": 0.1,
            "u1": 0.1,
            "p": 0.1,
            "s": 0.1,
            "t": 0.1,
            "sdg": 0.1,
            "tdg": 0.1,
            # X-axis gates (high sensitivity - orthogonal axis)
            "x": 1.0,
            "rx": 1.0,
            # Y-axis gates (high sensitivity - orthogonal axis)
            "y": 1.0,
            "ry": 1.0,
            # Hadamard (high sensitivity - creates superposition)
            "h": 1.0,
            # Identity (moderate sensitivity during idle)
            "id": 0.3,
            # General single-qubit gates (high sensitivity)
            "u2": 0.8,
            "u3": 0.9,
            "u": 0.9,
        }

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

    def _get_pathway_prediction(self) -> str:
        """Get specific pathway prediction for phase flip noise.

        Returns:
            Phase flip specific pathway hypothesis prediction
        """
        return (
            f"Phase flip noise should create longitudinal pathway structure "
            f"with flip rate {self.error_rate:.4f}. Pathways should preserve "
            f"measurement statistics while losing quantum interference."
        )

    def _assess_topology_sensitivity(self) -> str:
        """Assess phase flip noise sensitivity to quantum state topology."""
        return (
            "Moderate topology sensitivity expected due to interference dependence. "
            "States with more superposition content should show stronger "
            "pathway sensitivity while computational basis states are preserved."
        )

    def _analyze_pathway_preferences(self) -> str:
        """Analyze phase flip noise pathway preferences."""
        return (
            f"Longitudinal pathway preferences. Phase flip errors affect "
            f"quantum interference while preserving computational basis "
            f"structure with environmental coupling: magnetic={self.magnetic_field_noise}, "
            f"charge={self.charge_noise}."
        )

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
