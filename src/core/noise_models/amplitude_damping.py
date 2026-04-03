"""Amplitude Damping Noise for T1 Energy Relaxation Research.

# The Amplitude Damping Channel - Fundamental Energy Relaxation
Amplitude damping represents one of the most fundamental quantum decoherence
mechanisms: spontaneous emission and energy relaxation from excited to ground states.
It models the irreversible loss of quantum excitation to the environment.

# Physical Mechanism
Amplitude damping arises from spontaneous emission processes where qubits in the
excited state |1⟩ decay to the ground state |0⟩ through electromagnetic coupling.
This creates asymmetric decoherence that preferentially affects excited states,
distinguishing it from symmetric processes like depolarizing noise.

# Mathematical Description
The amplitude damping channel maps quantum states as:
ρ → K₀ρK₀† + K₁ρK₁† where:
K₀ = |0⟩⟨0| + √(1-γ)|1⟩⟨1|  (survival amplitude)
K₁ = √γ|0⟩⟨1|                  (decay amplitude)

# Hardware Origins
- Spontaneous photon emission from superconducting transmon qubits
- Coupling to lossy transmission lines and resonator modes
- Purcell effect enhancing radiative decay rates
- Finite temperature effects causing thermal excitation/relaxation

# Research Significance for Structured Pathways
Amplitude damping creates directional bias in decoherence pathways by preferentially
affecting excited computational basis states. This asymmetry may reveal how
energy flow patterns interact with entanglement topology to create structured
pathway signatures distinct from isotropic noise.

# Educational Framework
Amplitude damping channels demonstrate core quantum mechanics concepts:
- Non-unital channels that break detailed balance at zero temperature
- Energy conservation and thermodynamic constraints on quantum processes
- The relationship between T1 relaxation times and gate operation timescales
- Asymmetric decoherence and its effects on quantum state preparation
"""

import logging
from typing import Any

import numpy as np
from qiskit_aer.noise import NoiseModel, amplitude_damping_error

from .base_noise import BaseNoise

logger = logging.getLogger(__name__)

# Physical constants for realistic parameter calculations
BOLTZMANN_CONSTANT = 8.617e-5  # eV/K
PLANCK_CONSTANT = 4.136e-15  # eV⋅s
TYPICAL_QUBIT_FREQUENCY = 5.5e9  # Hz (superconducting transmon)


class AmplitudeDampingNoise(BaseNoise):
    """Amplitude damping noise model for T1 energy relaxation research.

    # Quantum Energy Relaxation Definition
    The amplitude damping channel models spontaneous emission: |1⟩ → |0⟩
    with probability γ = 1 - exp(-t/T1) over time t.

    This creates asymmetric decoherence that preferentially affects excited states,
    making it ideal for studying directional pathway biases in quantum decoherence.

    # Physical Interpretation
    Amplitude damping models environmental coupling that is:
    - **Directional**: Preferentially affects |1⟩ → |0⟩ transitions
    - **Energy-conserving**: Respects fundamental energy conservation laws
    - **Non-unital**: Does not preserve maximally mixed states
    - **Temperature-dependent**: Finite temperature enables reverse excitation

    # Research Applications in Pathway Studies
    - **Directional Bias**: Test how energy flow creates pathway asymmetries
    - **T1 Scaling**: Study pathway structure vs relaxation timescales
    - **Thermal Effects**: Investigate finite temperature pathway modifications
    - **State Asymmetry**: Compare excited vs ground state pathway preferences

    # Educational Significance
    Amplitude damping illustrates fundamental concepts:
    - **T1 Processes**: Energy relaxation and spontaneous emission physics
    - **Non-unital Channels**: Channels that break detailed balance symmetry
    - **Thermal Equilibrium**: Temperature effects on quantum decoherence
    - **Energy Conservation**: How conservation laws constrain quantum channels
    """

    def __init__(
        self,
        error_rate: float = 0.05,
        num_qubits: int = 1,
        experiment_id: str = "N/A",
        t1: float = None,
        gate_time: float = 20e-9,
        temperature: float = 0.015,
    ):
        """Initialize amplitude damping noise with physics-based validation.

        # Physics Parameter Integration
        Supports both phenomenological error rates and physics-based T1 calculations:
        - Phenomenological: Direct specification of damping probability γ
        - Physics-based: Calculate γ = 1 - exp(-t_gate/T1) from T1 time
        - Thermal effects: Include finite temperature excitation processes

        Args:
            error_rate: Phenomenological damping probability γ ∈ [0, 1]
            num_qubits: Number of qubits (amplitude damping is single-qubit)
            experiment_id: Unique identifier for experimental tracking
            t1: T1 relaxation time (seconds) - overrides error_rate if provided
            gate_time: Gate operation time for realistic damping calculation
            temperature: Operating temperature (Kelvin) for thermal corrections

        Raises:
            ValueError: If parameters violate physics constraints

        Example:
            >>> # Phenomenological damping
            >>> noise = AmplitudeDampingNoise(error_rate=0.01)

            >>> # Physics-based with T1 time
            >>> noise = AmplitudeDampingNoise(
            ...     t1=100e-6, gate_time=20e-9, temperature=0.015
            ... )
        """
        # Physics parameter validation before initialization
        self._validate_amplitude_damping_params(error_rate, t1, gate_time, temperature)

        # Store physics parameters for calculations
        self.t1 = t1
        self.gate_time = gate_time
        self.temperature = temperature

        # Calculate effective damping rate
        if t1 is not None:
            # Physics-based calculation: γ = 1 - exp(-t_gate/T1)
            self._physics_damping_rate = 1 - np.exp(-gate_time / t1)
            effective_error_rate = self._physics_damping_rate
        else:
            # Use phenomenological rate
            self._physics_damping_rate = error_rate
            effective_error_rate = error_rate

        # Calculate thermal population effects
        self._thermal_population = self._calculate_thermal_population()

        # Initialize base noise with effective rate
        super().__init__(
            error_rate=effective_error_rate,
            num_qubits=num_qubits,
            experiment_id=experiment_id,
            t1=t1,
            gate_time=gate_time,
            temperature=temperature,
        )

        # Log creation with T1 physics context
        self.log_noise_creation(
            "AMPLITUDE_DAMPING",
            {
                "physics_damping_rate": self._physics_damping_rate,
                "thermal_population": self._thermal_population,
                "t1_time": t1,
                "gate_time": gate_time,
                "temperature": temperature,
                "decoherence_type": "energy_relaxation_directional",
                "channel_property": "non_unital",
                "research_role": "directional_pathway_bias_investigation",
            },
        )

    def apply(
        self, noise_model: NoiseModel, gate_list: list[str], qubits_for_error: int = None
    ) -> None:
        """Apply amplitude damping noise to quantum gates.

        # Energy Relaxation Implementation
        Creates Qiskit amplitude damping error channels that model spontaneous
        emission: |1⟩ → |0⟩ with probability γ.

        # Gate Application Strategy
        - Single-qubit gates: Apply single-qubit amplitude damping
        - Two-qubit gates: Apply tensor product of amplitude damping (AD ⊗ AD)
          This models independent relaxation on both qubits during the gate.

        Args:
            noise_model: Qiskit noise model to modify with amplitude damping
            gate_list: Quantum gates to apply noise to
            qubits_for_error: Override qubit count (ignored as AD is constructed per-gate)
        """
        # Define gate arity
        one_qubit_gates = {
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
            "sx",
        }
        two_qubit_gates = {"cx", "cy", "cz", "ch", "swap", "iswap", "ecr"}

        # Calculate effective damping rate including thermal effects
        effective_rate = self._calculate_effective_damping_rate()

        try:
            # Create single-qubit AD channel
            ad_1q = amplitude_damping_error(effective_rate)
            # Create two-qubit AD channel (AD ⊗ AD) for independent decay
            ad_2q = ad_1q.tensor(ad_1q)
        except Exception as e:
            raise ValueError(
                f"Failed to create amplitude damping channels with rate {effective_rate:.4f}: {e}"
            ) from e

        successful_gates = []
        failed_gates = []

        for gate in gate_list:
            try:
                if gate in one_qubit_gates:
                    noise_model.add_all_qubit_quantum_error(ad_1q, gate)
                    successful_gates.append(gate)
                elif gate in two_qubit_gates:
                    noise_model.add_all_qubit_quantum_error(ad_2q, gate)
                    successful_gates.append(gate)
                else:
                    # Skip unknown or multi-qubit gates for now
                    pass
            except Exception as e:
                failed_gates.append((gate, str(e)))

        # Log application results with physics context
        if successful_gates:
            logger.info(
                f"Applied AMPLITUDE_DAMPING noise (γ={effective_rate:.4f}) to "
                f"gates: {successful_gates} "
                f"(T1={self.t1}, temp={self.temperature}K) "
                f"(experiment: {self.experiment_id})"
            )

        if failed_gates:
            logger.warning(
                f"Failed to apply AMPLITUDE_DAMPING to gates: {[gate for gate, _ in failed_gates]}"
            )

    def get_kraus_operators(self) -> list[np.ndarray]:
        """Return Kraus operators for the amplitude damping channel.

        # Mathematical Construction
        For amplitude damping with damping rate γ:
        K₀ = |0⟩⟨0| + √(1-γ)|1⟩⟨1|  (survival operator)
        K₁ = √γ|0⟩⟨1|                  (decay operator)

        These satisfy K₀†K₀ + K₁†K₁ = I (completeness relation).

        Returns:
            List of Kraus operators as numpy arrays

        Educational Note:
            The asymmetry K₁ = √γ|0⟩⟨1| (but no K†₁ = √γ|1⟩⟨0|)
            shows this channel is non-unital and energy-conserving.
        """
        γ = self.error_rate

        # Computational basis states
        zero_state = np.array([1, 0], dtype=complex)
        one_state = np.array([0, 1], dtype=complex)

        # Survival operator: no decay occurs
        K0 = np.outer(zero_state, zero_state) + np.sqrt(1 - γ) * np.outer(one_state, one_state)

        # Decay operator: |1⟩ → |0⟩ transition
        K1 = np.sqrt(γ) * np.outer(zero_state, one_state)

        return [K0, K1]

    def get_physics_description(self) -> dict[str, str]:
        """Return comprehensive physics description of amplitude damping.

        Returns:
            Dict with educational physics content about energy relaxation
        """
        return {
            "mechanism": "Spontaneous emission: excited state |1⟩ decays to ground state |0⟩ through electromagnetic coupling",
            "origin": "Coupling to vacuum electromagnetic field modes, lossy transmission lines, and thermal reservoirs",
            "mathematical_form": f"K₀ = |0⟩⟨0| + √(1-{self.error_rate:.3f})|1⟩⟨1|, K₁ = √{self.error_rate:.3f}|0⟩⟨1|",
            "physical_timescale": f"T1 = {self.t1:.2e}s" if self.t1 else "phenomenological rate",
            "temperature_effects": f"Thermal population = {self._thermal_population:.4f} at {self.temperature}K",
            "energy_conservation": "Irreversible |1⟩ → |0⟩ transitions preserve energy conservation",
            "channel_properties": "Non-unital (breaks detailed balance), trace-preserving, completely positive",
            "real_world_examples": "Superconducting transmon qubits, trapped ion spontaneous emission, photonic mode decay",
            "quantum_principles": "T1 relaxation, spontaneous emission, Purcell effect, thermal equilibrium",
        }

    def get_theoretical_properties(self) -> dict[str, Any]:
        """Get theoretical quantum properties specific to amplitude damping.

        Returns:
            Dict with amplitude damping channel specific properties
        """
        return {
            "decoherence_type": "energy_relaxation_directional",
            "channel_classification": "non_unital",
            "decay_probability": self.error_rate,
            "survival_probability": 1 - self.error_rate,
            "thermal_population": self._thermal_population,
            "t1_timescale": self.t1,
            "gate_timescale": self.gate_time,
            "energy_bias": "|1⟩_preferential_decay",
            "equilibrium_state": "|0⟩⟨0|",  # Ground state attractor
            "asymmetry_parameter": self.error_rate,  # Degree of |0⟩ vs |1⟩ bias
            "unitality": False,
            "time_reversibility": False,  # Irreversible decay process
            "information_capacity": self._calculate_channel_capacity(),
        }

    def get_research_context(self) -> dict[str, Any]:
        """Get research context for amplitude damping in pathway studies.

        Returns:
            Dict with research context and experimental predictions
        """
        return {
            "pathway_hypothesis": {
                "prediction": "Directional pathway bias favoring |1⟩ → |0⟩ transitions",
                "test_method": "Compare excited vs ground state pathway utilization patterns",
                "expected_signature": "Asymmetric decoherence with |1⟩-state pathway dominance",
            },
            "decoherence_characteristics": {
                "energy_bias": "Preferential decay of excited computational basis states",
                "topology_dependence": "Strong - affects entangled states with |1⟩ components asymmetrically",
                "pathway_asymmetry": "Expected - energy flow creates directional pathway preferences",
                "thermal_scaling": "Finite temperature reduces asymmetry through excitation processes",
            },
            "experimental_role": {
                "directional_testing": "Primary model for non-isotropic decoherence pathway analysis",
                "t1_scaling_studies": "Investigate pathway structure vs energy relaxation timescales",
                "thermal_pathway_effects": "Study temperature-dependent pathway modifications",
                "energy_flow_mapping": "Trace energy dissipation pathways through quantum networks",
            },
            "research_predictions": {
                "vs_depolarizing": "Should show strong |1⟩-state pathway bias unlike isotropic depolarizing",
                "temperature_dependence": "Pathway asymmetry decreases with increasing temperature",
                "entanglement_scaling": "Asymmetric entanglement decay with |1⟩-rich states more fragile",
                "measurement_bias": "Preferential loss of |1⟩-component correlations in measurements",
            },
            "educational_applications": {
                "energy_conservation": "Demonstrate energy conservation constraints in quantum channels",
                "t1_physics": "Connect microscopic relaxation to macroscopic T1 measurements",
                "thermal_equilibrium": "Show approach to thermal equilibrium in open quantum systems",
                "non_unital_channels": "Illustrate channels that break detailed balance symmetry",
            },
        }

    def _validate_amplitude_damping_params(
        self, error_rate: float, t1: float, gate_time: float, temperature: float
    ) -> None:
        """Validate amplitude damping parameters against physics constraints.

        # Physics Constraint Validation
        Ensures all parameters represent realistic amplitude damping scenarios
        consistent with quantum mechanics and thermodynamics.
        """
        # Validate damping probability
        if not 0 <= error_rate <= 1:
            raise ValueError(f"Amplitude damping rate must be in [0,1], got {error_rate}")

        # Validate T1 time if provided
        if t1 is not None and t1 <= 0:
            raise ValueError(f"T1 relaxation time must be positive, got {t1}")

        # Validate gate time
        if gate_time <= 0:
            raise ValueError(f"Gate time must be positive, got {gate_time}")

        # Validate temperature
        if temperature < 0:
            raise ValueError(f"Temperature must be non-negative, got {temperature}")

        # Check realistic parameter relationships
        if t1 is not None and gate_time > t1:
            logger.warning(
                f"Gate time ({gate_time:.2e}s) exceeds T1 ({t1:.2e}s) - "
                f"this may lead to complete relaxation during gate operation"
            )

    def _calculate_thermal_population(self) -> float:
        """Calculate thermal population of excited state at operating temperature.

        # Thermal Physics
        At finite temperature, thermal fluctuations can excite qubits from |0⟩ to |1⟩.
        Population follows Boltzmann distribution: n₁ = 1/(1 + exp(ℏω/kT))

        Returns:
            Thermal population of excited state (0 = pure ground, 0.5 = infinite temp)
        """
        if self.temperature == 0:
            return 0.0

        # Calculate thermal energy scale
        thermal_energy = BOLTZMANN_CONSTANT * self.temperature  # eV
        photon_energy = PLANCK_CONSTANT * TYPICAL_QUBIT_FREQUENCY  # eV

        # Boltzmann factor
        beta_omega = photon_energy / thermal_energy

        # Excited state population
        return 1.0 / (1.0 + np.exp(beta_omega))

    def _calculate_effective_damping_rate(self) -> float:
        """Calculate effective damping rate including thermal corrections.

        # Thermal Corrections
        At finite temperature, thermal excitation competes with relaxation:
        γ_eff = γ₀(1 - n_th) where n_th is thermal population

        Returns:
            Effective damping rate including temperature effects
        """
        base_rate = self._physics_damping_rate

        if self._thermal_population > 0:
            # Thermal excitation reduces effective relaxation
            return base_rate * (1 - self._thermal_population)
        else:
            return base_rate

    def _calculate_channel_capacity(self) -> float:
        """Calculate quantum channel capacity for amplitude damping.

        # Information Theory
        Channel capacity for amplitude damping depends on the damping rate
        and can be calculated analytically for specific input ensembles.
        """
        γ = self.error_rate
        if γ == 0:
            return 1.0  # Perfect channel
        elif γ == 1:
            return 0.0  # Complete damping
        else:
            # Approximate capacity (exact calculation is complex)
            return max(0, 1 - γ)

    def _get_pathway_prediction(self) -> str:
        """Get specific pathway prediction for amplitude damping noise.

        Returns:
            Amplitude damping specific pathway hypothesis prediction
        """
        return (
            f"Amplitude damping should create directional pathway bias favoring "
            f"|1⟩ → |0⟩ transitions with damping rate {self.error_rate:.4f}. "
            f"Pathway asymmetry reflects energy conservation and T1 physics."
        )

    def _assess_topology_sensitivity(self) -> str:
        """Assess amplitude damping sensitivity to quantum state topology."""
        return (
            "High topology sensitivity expected due to |1⟩-state bias. "
            "Entangled states with more |1⟩ components should show stronger "
            "pathway utilization and faster decoherence rates."
        )

    def _analyze_pathway_preferences(self) -> str:
        """Analyze amplitude damping pathway preferences."""
        return (
            f"Strong intrinsic pathway preference for |1⟩ → |0⟩ transitions. "
            f"Energy conservation creates directional bias with thermal "
            f"population {self._thermal_population:.4f} providing weak reverse process."
        )

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        if self.t1:
            return (
                f"Amplitude damping: T1={self.t1:.2e}s, γ={self.error_rate:.4f}, "
                f"temp={self.temperature}K [energy relaxation]"
            )
        else:
            return (
                f"Amplitude damping: γ={self.error_rate:.4f} [phenomenological energy relaxation]"
            )
