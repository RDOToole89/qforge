"""Thermal Relaxation Noise for Realistic Hardware Modeling.

# The Thermal Relaxation Channel - Combined T1/T2 Processes
Thermal relaxation noise represents the most realistic decoherence model by combining
both energy relaxation (T1) and dephasing (T2) processes at finite temperature.
This models the comprehensive environmental coupling that occurs in real quantum
hardware operating in dilution refrigerators.

# Physical Mechanism
Thermal relaxation arises from coupling to a thermal bath that causes:
- Energy relaxation: Spontaneous emission and thermal excitation (T1 processes)
- Pure dephasing: Elastic scattering without energy exchange (T2* processes)
- Thermal equilibration: Approach to Boltzmann distribution at bath temperature
- Combined effects: T2_eff = 1/(1/T2* + 1/2T1) relationship

# Mathematical Description
The thermal relaxation channel combines amplitude damping and pure dephasing:
- Amplitude damping with thermal population: |1⟩ → |0⟩ and |0⟩ → |1⟩
- Pure dephasing: Random Z rotations without energy exchange
- Temperature-dependent equilibrium: p_eq = 1/(1 + exp(ħω/kT))

# Hardware Origins
- Electromagnetic coupling to vacuum fluctuations (T1)
- Charge noise and magnetic field fluctuations (T2*)
- Johnson noise in control electronics
- Phonon coupling in solid-state systems
- Nuclear spin baths in semiconductors

# Research Significance for Structured Pathways
Thermal relaxation creates the most realistic decoherence environment for studying
pathway emergence, combining energy flow and dephasing in ways that may reveal
the full complexity of structured decoherence patterns.

# Educational Framework
Thermal relaxation demonstrates advanced concepts:
- Combined T1/T2 physics and their relationship
- Finite temperature effects and thermal equilibrium
- Realistic hardware constraints and operating conditions
- Master equation dynamics and Lindblad evolution
"""

import logging
from typing import Any

import numpy as np
from qiskit_aer.noise import NoiseModel, thermal_relaxation_error

from src.core.math import relaxation_probability

from .base_noise import BaseNoise

logger = logging.getLogger(__name__)

# Physical constants for thermal calculations
BOLTZMANN_EV = 8.617e-5  # Boltzmann constant in eV/K
PLANCK_EV = 4.136e-15  # Planck constant in eV⋅s
TYPICAL_QUBIT_FREQ = 5.5e9  # 5.5 GHz typical superconducting qubit


class ThermalRelaxationNoise(BaseNoise):
    """Thermal relaxation noise model for realistic hardware decoherence research.

    # Combined T1/T2 Decoherence Definition
    The thermal relaxation channel models the combined effects of energy relaxation
    (T1) and pure dephasing (T2*) in a finite temperature environment. This represents
    the most comprehensive and realistic decoherence model for quantum hardware.

    # Physical Interpretation
    Thermal relaxation models environmental coupling that includes:
    - **Energy Exchange**: T1 processes with spontaneous emission and thermal excitation
    - **Pure Dephasing**: T2* processes with elastic environmental scattering
    - **Thermal Equilibration**: Approach to Boltzmann distribution at bath temperature
    - **Combined Dynamics**: Realistic T2_eff = 1/(1/T2* + 1/2T1) relationship

    # Research Applications in Pathway Studies
    - **Realistic Modeling**: Most accurate representation of hardware decoherence
    - **Combined Mechanisms**: Study pathway behavior under multiple decoherence types
    - **Temperature Effects**: Investigate thermal population effects on pathways
    - **Hardware Validation**: Compare theoretical predictions with real device behavior

    # Educational Significance
    Thermal relaxation illustrates advanced concepts:
    - **T1/T2 Physics**: Comprehensive understanding of relaxation timescales
    - **Thermal Effects**: Finite temperature quantum mechanics
    - **Master Equations**: Lindblad dynamics and open quantum systems
    - **Hardware Reality**: Connection between theory and experimental constraints
    """

    def __init__(
        self,
        error_rate: float = 0.05,
        num_qubits: int = 1,
        experiment_id: str = "N/A",
        t1: float = 100e-6,
        t2: float = 80e-6,
        gate_time: float = 20e-9,
        temperature: float = 0.015,
        qubit_frequency: float = TYPICAL_QUBIT_FREQ,
    ):
        """Initialize thermal relaxation noise with comprehensive physics validation.

        # Physics Parameter Integration
        Supports both phenomenological error rates and physics-based T1/T2 calculations:
        - Phenomenological: Direct specification of combined error probability
        - Physics-based: Calculate from T1, T2, gate times, and temperature
        - Temperature effects: Include thermal population in equilibrium distribution

        Args:
            error_rate: Phenomenological combined error probability (overridden by T1/T2)
            num_qubits: Number of qubits (thermal relaxation is single-qubit)
            experiment_id: Unique identifier for experimental tracking
            t1: Energy relaxation time (seconds)
            t2: Dephasing time (seconds) - must satisfy T2 ≤ 2T1
            gate_time: Gate operation time for realistic error calculation
            temperature: Operating temperature (Kelvin)
            qubit_frequency: Qubit transition frequency (Hz) for thermal calculations

        Raises:
            ValueError: If parameters violate physics constraints

        Example:
            >>> # Realistic superconducting qubit parameters
            >>> noise = ThermalRelaxationNoise(
            ...     t1=100e-6, t2=80e-6, gate_time=20e-9, temperature=0.015
            ... )

            >>> # High-performance parameters
            >>> noise = ThermalRelaxationNoise(
            ...     t1=200e-6, t2=150e-6, temperature=0.010
            ... )
        """
        # Physics parameter validation before initialization
        self._validate_thermal_params(error_rate, t1, t2, gate_time, temperature, qubit_frequency)

        # Store physics parameters
        self.t1 = t1
        self.t2 = t2
        self.gate_time = gate_time
        self.temperature = temperature
        self.qubit_frequency = qubit_frequency

        # Calculate thermal population (Boltzmann distribution)
        self._thermal_population = self._calculate_thermal_population()

        # Calculate physics-based error rates
        self._t1_error_rate = self._calculate_t1_error_rate()
        self._t2_error_rate = self._calculate_t2_error_rate()
        self._combined_error_rate = self._calculate_combined_error_rate()

        # Use physics-based rate instead of phenomenological
        effective_error_rate = self._combined_error_rate

        # Initialize base noise with effective rate
        super().__init__(
            error_rate=effective_error_rate,
            num_qubits=num_qubits,
            experiment_id=experiment_id,
            t1=t1,
            t2=t2,
            gate_time=gate_time,
            temperature=temperature,
            qubit_frequency=qubit_frequency,
        )

        # Calculate derived properties
        self._effective_t2 = self._calculate_effective_t2()

        # Log creation with comprehensive physics context
        self.log_noise_creation(
            "THERMAL_RELAXATION",
            {
                "t1_time": t1,
                "t2_time": t2,
                "effective_t2": self._effective_t2,
                "gate_time": gate_time,
                "temperature": temperature,
                "thermal_population": self._thermal_population,
                "t1_error_rate": self._t1_error_rate,
                "t2_error_rate": self._t2_error_rate,
                "combined_error_rate": self._combined_error_rate,
                "decoherence_type": "combined_t1_t2_thermal",
                "channel_property": "non_unital_thermal",
                "research_role": "realistic_hardware_pathway_modeling",
            },
        )

    def apply(
        self, noise_model: NoiseModel, gate_list: list[str], qubits_for_error: int | None = None
    ) -> None:
        """Apply thermal relaxation noise to quantum gates with realistic physics.

        # Comprehensive Decoherence Implementation
        Creates Qiskit thermal relaxation error channels that model combined T1/T2
        processes with finite temperature effects. This represents the most realistic
        decoherence model for quantum hardware.

        # Gate-Dependent Error Rates
        Different gates have different durations and sensitivities:
        - Virtual gates (Z rotations): Minimal duration, reduced T1/T2 effects
        - Single-qubit gates: Standard gate time with full T1/T2 coupling
        - Two-qubit gates: Extended duration with increased decoherence

        Args:
            noise_model: Qiskit noise model to modify with thermal relaxation
            gate_list: Quantum gates to apply noise to
            qubits_for_error: Override qubit count (thermal relaxation uses 1)

        Example:
            >>> noise_model = NoiseModel()
            >>> gates = ['h', 'x', 'cx', 'rz']
            >>> thermal_noise.apply(noise_model, gates)
        """
        # Thermal relaxation is inherently single-qubit but affects all operations
        if qubits_for_error is not None and qubits_for_error != 1:
            logger.warning(
                f"Thermal relaxation is single-qubit, but applying to {qubits_for_error}-qubit gates"
            )

        # Gate-specific timing and sensitivity
        gate_times = self._get_gate_times()

        # Apply thermal relaxation to gates with time-dependent errors
        successful_gates = []
        failed_gates = []

        for gate in gate_list:
            try:
                # Get gate-specific timing
                gate_duration = gate_times.get(gate, self.gate_time)

                if gate_duration > 0:
                    # Create thermal relaxation error with gate-specific timing
                    thermal_error = thermal_relaxation_error(
                        t1=self.t1,
                        t2=self.t2,
                        time=gate_duration,
                        excited_state_population=self._thermal_population,
                    )

                    noise_model.add_all_qubit_quantum_error(thermal_error, gate)
                    successful_gates.append(f"{gate}(t={gate_duration:.1e}s)")
                else:
                    # Virtual gates with zero duration
                    successful_gates.append(f"{gate}(virtual)")

            except Exception as e:
                failed_gates.append((gate, str(e)))

        # Log application results with comprehensive physics context
        if successful_gates:
            logger.info(
                f"Applied THERMAL_RELAXATION noise (T1={self.t1:.1e}s, T2={self.t2:.1e}s) to "
                f"gates: {successful_gates} "
                f"(temp={self.temperature}K, thermal_pop={self._thermal_population:.4f}) "
                f"(experiment: {self.experiment_id})"
            )

        if failed_gates:
            logger.warning(
                f"Failed to apply THERMAL_RELAXATION noise to gates: "
                f"{[gate for gate, _ in failed_gates]}"
            )

    def get_kraus_operators(self) -> list[np.ndarray]:
        """Return Kraus operators for the thermal relaxation channel.

        # Mathematical Construction
        Thermal relaxation combines amplitude damping and dephasing channels.
        The exact Kraus operators depend on gate time and are complex for the
        combined channel. This returns the conceptual operators.

        Returns:
            List of conceptual Kraus operators for educational purposes

        Educational Note:
            APPROXIMATION: this returns only the T=0 amplitude-damping operators
            (energy relaxation, K₀ = diag(1, √(1-γ₁)), K₁ = √γ₁|0⟩⟨1|) and
            silently ignores the pure-dephasing (T2) and thermal-excitation
            contributions. The full thermal-relaxation channel that ``apply()``
            simulates via Qiskit ``thermal_relaxation_error`` requires additional
            Kraus operators. Use ``apply()`` for a faithful simulation.
        """
        # Approximate the channel by its T1 amplitude-damping component only.
        gamma_1 = self._t1_error_rate  # Energy relaxation probability over the gate

        K0 = np.array([[1, 0], [0, np.sqrt(1 - gamma_1)]], dtype=complex)
        K1 = np.sqrt(gamma_1) * np.array([[0, 1], [0, 0]], dtype=complex)

        return [K0, K1]

    def get_physics_description(self) -> dict[str, str]:
        """Return comprehensive physics description of thermal relaxation.

        Returns:
            Dict with educational physics content about combined T1/T2 processes
        """
        return {
            "mechanism": "Combined thermal relaxation: energy exchange (T1) and pure dephasing (T2) in thermal environment",
            "origin": "Electromagnetic coupling to thermal bath, charge noise, magnetic field fluctuations",
            "mathematical_form": f"Combined T1={self.t1:.2e}s, T2={self.t2:.2e}s, T2_eff={self._effective_t2:.2e}s",
            "t1_process": f"Energy relaxation time = {self.t1:.2e}s with spontaneous emission and thermal excitation",
            "t2_process": f"Dephasing time = {self.t2:.2e}s with elastic environmental scattering",
            "temperature_effects": f"Thermal population = {self._thermal_population:.4f} at {self.temperature}K",
            "physics_constraint": f"T2 ≤ 2T1: {self.t2:.2e}s ≤ {2 * self.t1:.2e}s ✓",
            "channel_properties": "Non-unital (thermal equilibrium), trace-preserving, completely positive",
            "real_world_examples": "Superconducting qubits in dilution refrigerators, trapped ions with heating, semiconductor quantum dots",
            "quantum_principles": "Master equation dynamics, Lindblad evolution, thermal equilibrium, open quantum systems",
        }

    def get_theoretical_properties(self) -> dict[str, Any]:
        """Get theoretical quantum properties specific to thermal relaxation.

        Returns:
            Dict with thermal relaxation channel specific properties
        """
        return {
            "decoherence_type": "combined_t1_t2_thermal",
            "channel_classification": "non_unital_thermal",
            "t1_relaxation_time": self.t1,
            "t2_dephasing_time": self.t2,
            "effective_t2": self._effective_t2,
            "gate_time": self.gate_time,
            "temperature": self.temperature,
            "thermal_population": self._thermal_population,
            "t1_error_rate": self._t1_error_rate,
            "t2_error_rate": self._t2_error_rate,
            "combined_error_rate": self._combined_error_rate,
            "energy_exchange": True,  # T1 processes exchange energy
            "pure_dephasing": True,  # T2* processes preserve energy
            "thermal_equilibrium": True,
            "unitality": False,  # Thermal channels are non-unital
            "reversibility": False,  # Information loss is irreversible
            "information_capacity": self._calculate_channel_capacity(),
        }

    def get_research_context(self) -> dict[str, Any]:
        """Get research context for thermal relaxation in pathway studies.

        Returns:
            Dict with research context and experimental predictions
        """
        return {
            "pathway_hypothesis": {
                "prediction": "Comprehensive pathway structure combining energy flow and dephasing effects",
                "test_method": "Compare realistic hardware behavior with idealized noise models",
                "expected_signature": "Complex pathway patterns reflecting combined T1/T2 dynamics",
            },
            "decoherence_characteristics": {
                "mechanism_combination": "Simultaneous energy relaxation and pure dephasing",
                "topology_dependence": "High - affects both energy and coherence simultaneously",
                "pathway_asymmetry": "Moderate - thermal effects create equilibrium bias",
                "scaling_behavior": "Complex scaling with both T1 and T2 contributions",
            },
            "experimental_role": {
                "hardware_validation": "Primary model for real quantum device behavior",
                "combined_mechanism_testing": "Study pathway behavior under multiple decoherence types",
                "temperature_effects": "Investigate thermal population effects on pathway structure",
                "realistic_benchmarking": "Benchmark theoretical predictions against hardware reality",
            },
            "research_predictions": {
                "vs_individual_channels": "Should show complex behavior combining individual channel effects",
                "temperature_dependence": "Pathway structure should vary with thermal population",
                "hardware_correlation": "Should correlate strongly with real device measurements",
                "pathway_complexity": "Most complex pathway patterns due to combined mechanisms",
            },
            "educational_applications": {
                "realistic_modeling": "Demonstrate most accurate decoherence representation",
                "t1_t2_physics": "Teach comprehensive relaxation and dephasing physics",
                "thermal_effects": "Illustrate finite temperature quantum mechanics",
                "open_systems": "Show master equation dynamics and Lindblad evolution",
            },
        }

    def _validate_thermal_params(
        self,
        error_rate: float,
        t1: float,
        t2: float,
        gate_time: float,
        temperature: float,
        qubit_frequency: float,
    ) -> None:
        """Validate thermal relaxation parameters against physics constraints.

        # Comprehensive Physics Validation
        Ensures all parameters represent realistic thermal relaxation scenarios
        consistent with quantum mechanics and thermodynamics.
        """
        # Validate error rate
        if not 0 <= error_rate <= 1:
            raise ValueError(f"Error rate must be in [0,1], got {error_rate}")

        # Validate relaxation times
        if t1 <= 0:
            raise ValueError(f"T1 relaxation time must be positive, got {t1}")
        if t2 <= 0:
            raise ValueError(f"T2 dephasing time must be positive, got {t2}")

        # Fundamental quantum mechanics constraint
        if t2 > 2 * t1:
            raise ValueError(
                f"T2 ({t2:.2e}s) cannot exceed 2*T1 ({2 * t1:.2e}s) - violates quantum physics. "
                f"This constraint arises because pure dephasing cannot be faster than "
                f"the combination of energy relaxation and pure dephasing."
            )

        # Validate gate time
        if gate_time <= 0:
            raise ValueError(f"Gate time must be positive, got {gate_time}")

        # Validate temperature
        if temperature < 0:
            raise ValueError(f"Temperature must be non-negative, got {temperature}")

        # Validate qubit frequency
        if qubit_frequency <= 0:
            raise ValueError(f"Qubit frequency must be positive, got {qubit_frequency}")

        # Check realistic parameter ranges
        if gate_time > t1:
            logger.warning(
                f"Gate time ({gate_time:.2e}s) exceeds T1 ({t1:.2e}s) - "
                f"significant energy relaxation during gate operation"
            )

        if gate_time > t2:
            logger.warning(
                f"Gate time ({gate_time:.2e}s) exceeds T2 ({t2:.2e}s) - "
                f"significant dephasing during gate operation"
            )

    def _calculate_thermal_population(self) -> float:
        """Calculate thermal population using Boltzmann distribution.

        # Thermal Physics
        At finite temperature, the excited state has non-zero population
        according to the Boltzmann distribution: p = 1/(1 + exp(ħω/kT))

        Returns:
            Thermal population of excited state
        """
        if self.temperature == 0:
            return 0.0  # Pure ground state at zero temperature

        # Energy scale: ħω = h * frequency
        photon_energy = PLANCK_EV * self.qubit_frequency
        thermal_energy = BOLTZMANN_EV * self.temperature

        # Boltzmann factor
        if thermal_energy > 0:
            boltzmann_factor = np.exp(photon_energy / thermal_energy)
            return float(1.0 / (1.0 + boltzmann_factor))
        else:
            return 0.0

    def _calculate_t1_error_rate(self) -> float:
        """Calculate T1 error rate for the gate time.

        Returns:
            T1 error probability for single gate operation
        """
        return relaxation_probability(self.gate_time, self.t1)

    def _calculate_t2_error_rate(self) -> float:
        """Calculate T2 error rate for the gate time.

        Returns:
            T2 error probability for single gate operation
        """
        return relaxation_probability(self.gate_time, self.t2)

    def _calculate_combined_error_rate(self) -> float:
        """Calculate combined T1/T2 error rate.

        # Combined Error Physics
        The combined error rate accounts for both energy relaxation and
        dephasing processes occurring simultaneously during gate operation.

        Returns:
            Combined error probability
        """
        # Simplified combined rate (more complex in full treatment)
        t1_rate = self._t1_error_rate
        t2_rate = self._t2_error_rate

        # Combined rate avoiding double-counting
        return min(1.0, t1_rate + t2_rate - t1_rate * t2_rate)

    def _calculate_effective_t2(self) -> float:
        """Calculate effective T2 including T1 contributions.

        # Effective T2 Physics
        The observed dephasing time includes contributions from both
        pure dephasing and energy relaxation: 1/T2_eff = 1/T2* + 1/(2T1)

        Returns:
            Effective T2 time including T1 effects
        """
        return 1.0 / (1.0 / self.t2 + 1.0 / (2 * self.t1))

    def _get_gate_times(self) -> dict[str, float]:
        """Get gate-specific operation times.

        # Gate Timing Physics
        Different gates have different physical implementation times:
        - Virtual gates: Zero time (software rotation)
        - Single-qubit gates: Standard gate time
        - Two-qubit gates: Extended time due to complexity

        Returns:
            Dict mapping gate names to operation times (seconds)
        """
        return {
            # Virtual gates (zero duration)
            "z": 0.0,
            "rz": 0.0,
            "u1": 0.0,
            "p": 0.0,
            "s": 0.0,
            "t": 0.0,
            "sdg": 0.0,
            "tdg": 0.0,
            # Identity (zero active time)
            "id": 0.0,
            # Single-qubit physical gates
            "x": self.gate_time,
            "y": self.gate_time,
            "h": self.gate_time,
            "rx": self.gate_time,
            "ry": self.gate_time,
            "u2": self.gate_time,
            "u3": self.gate_time,
            "u": self.gate_time,
            # Two-qubit gates (longer duration)
            "cx": 2 * self.gate_time,
            "cy": 2 * self.gate_time,
            "cz": 2 * self.gate_time,
            "ch": 2 * self.gate_time,
            "swap": 3 * self.gate_time,
            "iswap": 3 * self.gate_time,
        }

    def _calculate_channel_capacity(self) -> float:
        """Calculate quantum channel capacity for thermal relaxation.

        # Information Theory
        Channel capacity for thermal relaxation is complex due to the
        combination of T1 and T2 processes with thermal effects.
        """
        # Simplified capacity estimate based on combined error rate
        combined_rate = self._combined_error_rate
        return max(0, 1 - combined_rate)

    def _get_pathway_prediction(self) -> str:
        """Get specific pathway prediction for thermal relaxation noise.

        Returns:
            Thermal relaxation specific pathway hypothesis prediction
        """
        return (
            f"Thermal relaxation should create complex pathway structure combining "
            f"T1 ({self.t1:.2e}s) and T2 ({self.t2:.2e}s) processes. Pathways should "
            f"reflect both energy flow and dephasing with thermal population {self._thermal_population:.4f}."
        )

    def _assess_topology_sensitivity(self) -> str:
        """Assess thermal relaxation sensitivity to quantum state topology."""
        return (
            "High topology sensitivity expected due to combined T1/T2 mechanisms. "
            "States with different energy and coherence characteristics should show "
            "distinct pathway behavior under realistic decoherence."
        )

    def _analyze_pathway_preferences(self) -> str:
        """Analyze thermal relaxation pathway preferences."""
        return (
            f"Complex pathway preferences combining energy flow (T1) and dephasing (T2). "
            f"Thermal effects at {self.temperature}K create equilibrium bias with "
            f"effective T2 = {self._effective_t2:.2e}s."
        )

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        return (
            f"Thermal relaxation: T1={self.t1:.1e}s, T2={self.t2:.1e}s, "
            f"T2_eff={self._effective_t2:.1e}s, temp={self.temperature}K "
            f"[realistic hardware decoherence]"
        )
