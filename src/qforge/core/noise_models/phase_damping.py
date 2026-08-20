"""Phase damping noise (pure dephasing).

# The Phase Damping Channel - Fundamental Pure Dephasing
Phase damping represents pure dephasing processes where qubits lose phase
coherence without energy exchange with the environment. This creates decoherence
that destroys superposition while preserving computational basis populations.

# Physical Mechanism
Phase damping arises from environmental fluctuations that randomly shift qubit
phases without causing |0⟩ ↔ |1⟩ transitions. Common sources include:
- Magnetic field fluctuations causing random Z rotations
- Charge noise in electrostatically defined qubits
- Voltage fluctuations in gate-controlled systems

# Mathematical Description
The phase damping channel maps quantum states by decaying off-diagonal
coherences while preserving populations:
ρ₀₀ → ρ₀₀, ρ₁₁ → ρ₁₁, ρ₀₁ → √(1-λ)·ρ₀₁
Kraus operators (standard 2-operator form): K₀ = diag(1, √(1-λ)), K₁ = diag(0, √λ)
This matches Qiskit's ``phase_damping_error(λ)`` (coherence factor √(1-λ)).

# Hardware Origins
- Magnetic field noise from environmental sources
- Electric field fluctuations in gate electrodes
- Charge noise in semiconductor quantum dots
- Johnson noise in classical control electronics
- Nuclear spin baths in solid-state systems

# Educational Framework
Phase damping channels demonstrate core concepts:
- Pure dephasing vs mixed T1/T2 processes
- Preservation of computational basis populations
- T2* measurements and inhomogeneous broadening
- Environmental phase noise and its quantum effects
"""

import logging
from typing import Any

import numpy as np
from qiskit_aer.noise import NoiseModel, phase_damping_error

from qforge.core.math import relaxation_probability

from .base_noise import BaseNoise

logger = logging.getLogger(__name__)

# Physical constants for T2* calculations
TYPICAL_MAGNETIC_NOISE = 1e-6  # Tesla RMS field fluctuations
GYROMAGNETIC_RATIO = 2.8e10  # rad/(s⋅Tesla) for electron spin
TYPICAL_CHARGE_NOISE = 1e-6  # eV RMS energy fluctuations


class PhaseDampingNoise(BaseNoise):
    """Phase damping noise model (pure dephasing).

    # Quantum Pure Dephasing Definition
    The phase damping channel models pure dephasing: loss of quantum coherence
    without energy exchange. Populations |⟨0|ρ|0⟩| and |⟨1|ρ|1⟩| are preserved
    while off-diagonal coherences ⟨0|ρ|1⟩ decay exponentially.

    This creates decoherence that is fundamentally different from energy
    relaxation (amplitude damping).

    # Physical Interpretation
    Phase damping models environmental coupling that is:
    - **Coherence-destroying**: Eliminates phase relationships between basis states
    - **Population-preserving**: Maintains |0⟩ and |1⟩ state probabilities
    - **Unital**: Preserves maximally mixed states
    - **Elastic**: No energy exchange with environment

    # Educational Significance
    Phase damping illustrates fundamental concepts:
    - **T2* Processes**: Pure dephasing and inhomogeneous broadening
    - **Coherence vs Population**: Distinction between different decoherence types
    - **Environmental Noise**: Classical noise effects on quantum systems
    - **Ramsey Interferometry**: Experimental measurement of phase coherence
    """

    NOISE_TYPE = "PHASE_DAMPING"
    IS_UNITAL = True
    CATALOG = {
        "description": "Pure dephasing without energy exchange",
        "mechanism": "Environmental coupling preserving energy eigenstates",
        "use_case": "Modeling T2*-limited coherence loss",
        "typical_origin": "Charge noise, magnetic field fluctuations",
        "educational_concepts": "T2* processes, elastic scattering, phase coherence",
    }

    def __init__(
        self,
        error_rate: float = 0.05,
        num_qubits: int = 1,
        experiment_id: str = "N/A",
        t2_star: float | None = None,
        gate_time: float = 20e-9,
        temperature: float = 0.015,
    ):
        """Initialize phase damping noise with physics-based validation.

        # Physics Parameter Integration
        Supports both phenomenological damping rates and physics-based T2* calculations:
        - Phenomenological: Direct specification of dephasing probability λ
        - Physics-based: Calculate λ = 1 - exp(-t_gate/T2*) from T2* time
        - Temperature effects: Include thermal dephasing contributions

        Args:
            error_rate: Phenomenological dephasing probability λ ∈ [0, 1]
            num_qubits: Number of qubits (phase damping is single-qubit)
            experiment_id: Unique identifier for experimental tracking
            t2_star: T2* dephasing time (seconds) - overrides error_rate if provided
            gate_time: Gate operation time for realistic dephasing calculation
            temperature: Operating temperature (Kelvin) for thermal noise assessment

        Raises:
            ValueError: If parameters violate physics constraints

        Example:
            >>> # Phenomenological dephasing
            >>> noise = PhaseDampingNoise(error_rate=0.01)

            >>> # Physics-based with T2* time
            >>> noise = PhaseDampingNoise(
            ...     t2_star=50e-6, gate_time=20e-9, temperature=0.015
            ... )
        """
        # Physics parameter validation before initialization
        self._validate_phase_damping_params(error_rate, t2_star, gate_time, temperature)

        # Store physics parameters for calculations
        self.t2_star = t2_star
        self.gate_time = gate_time
        self.temperature = temperature

        # Calculate effective dephasing rate
        if t2_star is not None:
            # Physics-based calculation: λ = 1 - exp(-t_gate/T2*)
            self._physics_dephasing_rate = relaxation_probability(gate_time, t2_star)
            effective_error_rate = self._physics_dephasing_rate
        else:
            # Use phenomenological rate
            self._physics_dephasing_rate = error_rate
            effective_error_rate = error_rate

        # Calculate thermal noise contribution
        self._thermal_dephasing = self._calculate_thermal_dephasing()

        # Initialize base noise with effective rate
        super().__init__(
            error_rate=effective_error_rate,
            num_qubits=num_qubits,
            experiment_id=experiment_id,
            t2_star=t2_star,
            gate_time=gate_time,
            temperature=temperature,
        )

        # Log creation with T2* physics context
        self.log_noise_creation(
            "PHASE_DAMPING",
            {
                "physics_dephasing_rate": self._physics_dephasing_rate,
                "thermal_dephasing": self._thermal_dephasing,
                "t2_star_time": t2_star,
                "gate_time": gate_time,
                "temperature": temperature,
                "decoherence_type": "pure_dephasing_elastic",
                "channel_property": "unital",
            },
        )

    def apply(
        self, noise_model: NoiseModel, gate_list: list[str], qubits_for_error: int | None = None
    ) -> None:
        """Apply phase damping noise to single-qubit quantum gates.

        # Pure Dephasing Implementation
        Creates Qiskit phase damping error channels that model pure dephasing:
        coherence loss without energy exchange. Populations are preserved while
        off-diagonal density matrix elements decay exponentially.

        # Gate Application Strategy
        Phase damping only affects single-qubit operations:
        - Single-qubit gates: Apply phase damping during execution
        - Multi-qubit gates: Skip (phase damping is inherently single-qubit)
        - Virtual gates: Reduced dephasing (no physical implementation)

        Args:
            noise_model: Qiskit noise model to modify with phase damping
            gate_list: Quantum gates to apply noise to (single-qubit only)
            qubits_for_error: Override qubit count (phase damping uses 1)

        Example:
            >>> noise_model = NoiseModel()
            >>> gates = ['h', 'x', 'cx']  # Only h, x will get phase damping
            >>> phase_noise.apply(noise_model, gates)
        """
        # Phase damping is inherently single-qubit
        if qubits_for_error is not None and qubits_for_error != 1:
            logger.warning(
                f"Phase damping is single-qubit only, ignoring qubits_for_error={qubits_for_error}"
            )

        # Filter to single-qubit gates only
        single_qubit_gates = {
            "id",
            "x",
            "y",
            "z",
            "h",
            "s",
            "t",
            "sdg",
            "tdg",
            "rx",
            "ry",
            "rz",
            "u1",
            "u2",
            "u3",
            "u",
            "p",
        }

        valid_gates = [gate for gate in gate_list if gate in single_qubit_gates]
        skipped_gates = [gate for gate in gate_list if gate not in single_qubit_gates]

        if not valid_gates:
            logger.warning(
                f"No single-qubit gates found in {gate_list}. "
                f"Phase damping only affects single-qubit operations."
            )
            return

        # Use the same dephasing rate λ as get_kraus_operators() so the
        # simulated channel matches the documented Kraus form exactly.
        effective_rate = self.error_rate

        # Apply a single uniform phase damping channel to every single-qubit gate.
        successful_gates = []
        failed_gates = []

        if effective_rate > 0:
            phase_damping_channel = phase_damping_error(effective_rate)
            for gate in valid_gates:
                try:
                    noise_model.add_all_qubit_quantum_error(phase_damping_channel, gate)
                    successful_gates.append(gate)
                except Exception as e:
                    failed_gates.append((gate, str(e)))

        # Log application results with physics context
        if successful_gates:
            logger.info(
                f"Applied PHASE_DAMPING noise (λ={effective_rate:.4f}) to "
                f"single-qubit gates: {successful_gates} "
                f"(T2*={self.t2_star}, temp={self.temperature}K) "
                f"(experiment: {self.experiment_id})"
            )

        if skipped_gates:
            logger.debug(f"Skipped multi-qubit gates for PHASE_DAMPING: {skipped_gates}")

        if failed_gates:
            logger.warning(
                f"Failed to apply PHASE_DAMPING to gates: {[gate for gate, _ in failed_gates]}"
            )

    def get_kraus_operators(self) -> list[np.ndarray]:
        """Return Kraus operators for the phase damping channel.

        # Mathematical Construction
        Standard 2-operator phase damping channel with dephasing rate λ:
        K₀ = diag(1, √(1-λ))  (coherence survival)
        K₁ = diag(0, √λ)       (phase-scattering operator)

        These satisfy K₀†K₀ + K₁†K₁ = I (completeness relation) and decay the
        off-diagonal coherence by the factor √(1-λ), exactly matching the channel
        simulated by ``apply()`` via Qiskit ``phase_damping_error(λ)``.

        The dephasing rate λ = ``self.error_rate`` is derived identically to the
        value passed to ``phase_damping_error`` in ``apply()``: it is the
        physics-based rate ``1 - exp(-gate_time / T2*)`` when ``t2_star`` is
        supplied, otherwise the phenomenological ``error_rate``.

        Returns:
            List of Kraus operators as numpy arrays

        Educational Note:
            K₁ removes only the |1⟩-component phase, shrinking the off-diagonal
            coherence ⟨0|ρ|1⟩ by √(1-λ) while preserving both populations.
        """
        λ = self.error_rate

        # Coherence-survival operator
        K0 = np.array([[1, 0], [0, np.sqrt(1 - λ)]], dtype=complex)

        # Phase-scattering operator (acts on the |1⟩ amplitude only)
        K1 = np.array([[0, 0], [0, np.sqrt(λ)]], dtype=complex)

        return [K0, K1]

    def get_physics_description(self) -> dict[str, str]:
        """Return comprehensive physics description of phase damping.

        Returns:
            Dict with educational physics content about pure dephasing
        """
        return {
            "mechanism": "Pure dephasing: environmental phase noise destroys coherence without energy exchange",
            "origin": "Magnetic field fluctuations, charge noise, voltage drifts causing random Z rotations",
            "mathematical_form": f"K₀ = diag(1, √(1-{self.error_rate:.3f})), K₁ = diag(0, √{self.error_rate:.3f})",
            "physical_timescale": f"T2* = {self.t2_star:.2e}s"
            if self.t2_star
            else "phenomenological rate",
            "temperature_effects": f"Thermal dephasing = {self._thermal_dephasing:.4f} at {self.temperature}K",
            "population_preservation": "Computational basis populations |0⟩ and |1⟩ are exactly preserved",
            "channel_properties": "Unital (preserves maximally mixed states), trace-preserving, completely positive",
            "real_world_examples": "Superconducting qubit charge noise, trapped ion magnetic field fluctuations, semiconductor quantum dots",
            "quantum_principles": "T2* measurements, Ramsey interferometry, inhomogeneous broadening, elastic scattering",
        }

    def get_theoretical_properties(self) -> dict[str, Any]:
        """Get theoretical quantum properties specific to phase damping.

        Returns:
            Dict with phase damping channel specific properties
        """
        return {
            "decoherence_type": "pure_dephasing_elastic",
            "channel_classification": "unital",
            "dephasing_probability": self.error_rate,
            "coherence_preservation": float(np.sqrt(1 - self.error_rate)),
            "thermal_dephasing": self._thermal_dephasing,
            "t2_star_timescale": self.t2_star,
            "gate_timescale": self.gate_time,
            "population_preservation": "exact",
            "coherence_decay": "exponential",
            "measurement_bias": "none_populations_preserved",
            "energy_exchange": False,  # Pure dephasing is elastic
            "unitality": True,
            "reversibility": False,  # Information loss is irreversible
            "information_capacity": self._calculate_channel_capacity(),
        }

    def _validate_phase_damping_params(
        self, error_rate: float, t2_star: float | None, gate_time: float, temperature: float
    ) -> None:
        """Validate phase damping parameters against physics constraints.

        # Physics Constraint Validation
        Ensures all parameters represent realistic phase damping scenarios
        consistent with quantum mechanics and experimental constraints.
        """
        # Validate dephasing probability
        if not 0 <= error_rate <= 1:
            raise ValueError(f"Phase damping rate must be in [0,1], got {error_rate}")

        # Validate T2* time if provided
        if t2_star is not None and t2_star <= 0:
            raise ValueError(f"T2* dephasing time must be positive, got {t2_star}")

        # Validate gate time
        if gate_time <= 0:
            raise ValueError(f"Gate time must be positive, got {gate_time}")

        # Validate temperature
        if temperature < 0:
            raise ValueError(f"Temperature must be non-negative, got {temperature}")

        # Check realistic parameter relationships
        if t2_star is not None and gate_time > t2_star:
            logger.warning(
                f"Gate time ({gate_time:.2e}s) exceeds T2* ({t2_star:.2e}s) - "
                f"this may lead to complete dephasing during gate operation"
            )

    def _calculate_thermal_dephasing(self) -> float:
        """Calculate thermal contribution to dephasing at operating temperature.

        # Thermal Dephasing
        At finite temperature, thermal fluctuations contribute to dephasing.
        This is typically much smaller than other sources but included for
        completeness in realistic modeling.

        Returns:
            Thermal dephasing contribution (dimensionless)
        """
        if self.temperature == 0:
            return 0.0

        # Rough estimate based on thermal energy scale
        # Real calculation would require specific noise spectral density
        thermal_energy = 8.617e-5 * self.temperature  # kT in eV
        typical_energy_scale = 1e-3  # eV, typical qubit energy scale

        # Thermal dephasing is typically weak at dilution refrigerator temperatures
        return min(0.01, thermal_energy / typical_energy_scale)

    def _calculate_channel_capacity(self) -> float:
        """Calculate quantum channel capacity for phase damping.

        # Information Theory
        Channel capacity for phase damping depends on the dephasing rate
        and can be calculated using quantum information theory.
        """
        λ = self.error_rate
        if λ == 0:
            return 1.0  # Perfect channel
        elif λ == 1:
            return 0.0  # Complete dephasing
        else:
            # Approximate capacity for phase damping channel
            return max(0, 1 - λ)

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        if self.t2_star:
            return (
                f"Phase damping: T2*={self.t2_star:.2e}s, λ={self.error_rate:.4f}, "
                f"temp={self.temperature}K [pure dephasing]"
            )
        else:
            return f"Phase damping: λ={self.error_rate:.4f} [phenomenological pure dephasing]"
