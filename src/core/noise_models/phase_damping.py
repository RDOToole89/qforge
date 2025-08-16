"""
Phase Damping Noise for Pure Dephasing Research

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
The phase damping channel maps quantum states as:
ρ → (1-λ)ρ + λ(|0⟩⟨0|ρ|0⟩⟨0| + |1⟩⟨1|ρ|1⟩⟨1|)
Kraus operators: K₀ = √(1-λ/2)(I), K₁ = √(λ/2)|0⟩⟨0|, K₂ = √(λ/2)|1⟩⟨1|

# Hardware Origins
- Magnetic field noise from environmental sources
- Electric field fluctuations in gate electrodes
- Charge noise in semiconductor quantum dots
- Johnson noise in classical control electronics
- Nuclear spin baths in solid-state systems

# Research Significance for Structured Pathways
Phase damping creates coherence loss without energy transfer, potentially
revealing pathway structure that depends on phase relationships rather than
population dynamics. This may expose topological effects masked by energy
relaxation in other noise types.

# Educational Framework
Phase damping channels demonstrate core concepts:
- Pure dephasing vs mixed T1/T2 processes
- Preservation of computational basis populations
- T2* measurements and inhomogeneous broadening
- Environmental phase noise and its quantum effects
"""

import numpy as np
import logging
from typing import List, Dict, Any
from qiskit_aer.noise import NoiseModel, phase_damping_error
from .base_noise import BaseNoise

logger = logging.getLogger("QuantumExperiment.NoiseModels")

# Physical constants for T2* calculations
TYPICAL_MAGNETIC_NOISE = 1e-6  # Tesla RMS field fluctuations
GYROMAGNETIC_RATIO = 2.8e10    # rad/(s⋅Tesla) for electron spin
TYPICAL_CHARGE_NOISE = 1e-6    # eV RMS energy fluctuations


class PhaseDampingNoise(BaseNoise):
    """
    Phase damping noise model for pure dephasing research.
    
    # Quantum Pure Dephasing Definition
    The phase damping channel models pure dephasing: loss of quantum coherence
    without energy exchange. Populations |⟨0|ρ|0⟩| and |⟨1|ρ|1⟩| are preserved
    while off-diagonal coherences ⟨0|ρ|1⟩ decay exponentially.
    
    This creates decoherence that is fundamentally different from energy
    relaxation, making it ideal for studying coherence-based pathway effects.
    
    # Physical Interpretation
    Phase damping models environmental coupling that is:
    - **Coherence-destroying**: Eliminates phase relationships between basis states
    - **Population-preserving**: Maintains |0⟩ and |1⟩ state probabilities
    - **Unital**: Preserves maximally mixed states
    - **Elastic**: No energy exchange with environment
    
    # Research Applications in Pathway Studies
    - **Coherence Pathways**: Test how phase relationships affect pathway structure
    - **T2* Scaling**: Study pathway persistence vs dephasing timescales
    - **Elastic Decoherence**: Compare with energy-exchanging processes
    - **Topological Effects**: Investigate topology-dependent coherence protection
    
    # Educational Significance
    Phase damping illustrates fundamental concepts:
    - **T2* Processes**: Pure dephasing and inhomogeneous broadening
    - **Coherence vs Population**: Distinction between different decoherence types
    - **Environmental Noise**: Classical noise effects on quantum systems
    - **Ramsey Interferometry**: Experimental measurement of phase coherence
    """

    def __init__(
        self, 
        error_rate: float = 0.05, 
        num_qubits: int = 1, 
        experiment_id: str = "N/A",
        t2_star: float = None,
        gate_time: float = 20e-9,
        temperature: float = 0.015
    ):
        """
        Initialize phase damping noise with physics-based validation.
        
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
            self._physics_dephasing_rate = 1 - np.exp(-gate_time / t2_star)
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
            temperature=temperature
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
                "research_role": "coherence_pathway_investigation"
            }
        )

    def apply(self, noise_model: NoiseModel, gate_list: List[str], qubits_for_error: int = None) -> None:
        """
        Apply phase damping noise to single-qubit quantum gates.
        
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
            'id', 'x', 'y', 'z', 'h', 's', 't', 'sdg', 'tdg',
            'rx', 'ry', 'rz', 'u1', 'u2', 'u3', 'u', 'p'
        }
        
        valid_gates = [gate for gate in gate_list if gate in single_qubit_gates]
        skipped_gates = [gate for gate in gate_list if gate not in single_qubit_gates]
        
        if not valid_gates:
            logger.warning(
                f"No single-qubit gates found in {gate_list}. "
                f"Phase damping only affects single-qubit operations."
            )
            return
        
        # Calculate effective dephasing rate including thermal effects
        effective_rate = self._calculate_effective_dephasing_rate()
        
        # Gate-specific dephasing sensitivity
        gate_sensitivity = self._get_gate_sensitivity_map()
        
        # Create phase damping error channels with gate sensitivity
        successful_gates = []
        failed_gates = []
        
        for gate in valid_gates:
            try:
                # Apply gate-specific sensitivity
                sensitivity = gate_sensitivity.get(gate, 1.0)
                gate_specific_rate = effective_rate * sensitivity
                
                if gate_specific_rate > 0:
                    phase_damping_channel = phase_damping_error(gate_specific_rate)
                    noise_model.add_all_qubit_quantum_error(phase_damping_channel, gate)
                    successful_gates.append(f"{gate}(s={sensitivity:.2f})")
                else:
                    # Virtual gates with zero sensitivity
                    successful_gates.append(f"{gate}(virtual)")
                    
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
            logger.debug(
                f"Skipped multi-qubit gates for PHASE_DAMPING: {skipped_gates}"
            )
        
        if failed_gates:
            logger.warning(
                f"Failed to apply PHASE_DAMPING to gates: "
                f"{[gate for gate, _ in failed_gates]}"
            )
    
    def get_kraus_operators(self) -> List[np.ndarray]:
        """
        Return Kraus operators for the phase damping channel.
        
        # Mathematical Construction
        For phase damping with dephasing rate λ:
        K₀ = √(1-λ/2) I  (identity with coherence preservation)
        K₁ = √(λ/2) |0⟩⟨0|  (|0⟩ projection)
        K₂ = √(λ/2) |1⟩⟨1|  (|1⟩ projection)
        
        These satisfy K₀†K₀ + K₁†K₁ + K₂†K₂ = I (completeness relation).
        
        Returns:
            List of Kraus operators as numpy arrays
            
        Educational Note:
            The projection operators K₁, K₂ destroy coherences |⟨0|ρ|1⟩| 
            while preserving populations |⟨0|ρ|0⟩| and |⟨1|ρ|1⟩|.
        """
        λ = self.error_rate
        
        # Computational basis states
        zero_state = np.array([1, 0], dtype=complex)
        one_state = np.array([0, 1], dtype=complex)
        
        # Identity operator (coherence preservation)
        K0 = np.sqrt(1 - λ/2) * np.eye(2, dtype=complex)
        
        # Projection onto |0⟩ (destroys coherence from |1⟩)
        K1 = np.sqrt(λ/2) * np.outer(zero_state, zero_state)
        
        # Projection onto |1⟩ (destroys coherence from |0⟩)
        K2 = np.sqrt(λ/2) * np.outer(one_state, one_state)
        
        return [K0, K1, K2]
    
    def get_physics_description(self) -> Dict[str, str]:
        """
        Return comprehensive physics description of phase damping.
        
        Returns:
            Dict with educational physics content about pure dephasing
        """
        return {
            "mechanism": "Pure dephasing: environmental phase noise destroys coherence without energy exchange",
            "origin": "Magnetic field fluctuations, charge noise, voltage drifts causing random Z rotations",
            "mathematical_form": f"K₀ = √(1-{self.error_rate:.3f}/2)I, K₁ = √({self.error_rate:.3f}/2)|0⟩⟨0|, K₂ = √({self.error_rate:.3f}/2)|1⟩⟨1|",
            "physical_timescale": f"T2* = {self.t2_star:.2e}s" if self.t2_star else "phenomenological rate",
            "temperature_effects": f"Thermal dephasing = {self._thermal_dephasing:.4f} at {self.temperature}K",
            "population_preservation": "Computational basis populations |0⟩ and |1⟩ are exactly preserved",
            "channel_properties": "Unital (preserves maximally mixed states), trace-preserving, completely positive",
            "real_world_examples": "Superconducting qubit charge noise, trapped ion magnetic field fluctuations, semiconductor quantum dots",
            "quantum_principles": "T2* measurements, Ramsey interferometry, inhomogeneous broadening, elastic scattering"
        }
    
    def get_theoretical_properties(self) -> Dict[str, Any]:
        """
        Get theoretical quantum properties specific to phase damping.
        
        Returns:
            Dict with phase damping channel specific properties
        """
        return {
            "decoherence_type": "pure_dephasing_elastic",
            "channel_classification": "unital",
            "dephasing_probability": self.error_rate,
            "coherence_preservation": 1 - self.error_rate,
            "thermal_dephasing": self._thermal_dephasing,
            "t2_star_timescale": self.t2_star,
            "gate_timescale": self.gate_time,
            "population_preservation": "exact",
            "coherence_decay": "exponential",
            "measurement_bias": "none_populations_preserved",
            "energy_exchange": False,  # Pure dephasing is elastic
            "unitality": True,
            "reversibility": False,  # Information loss is irreversible
            "information_capacity": self._calculate_channel_capacity()
        }
    
    def get_research_context(self) -> Dict[str, Any]:
        """
        Get research context for phase damping in pathway studies.
        
        Returns:
            Dict with research context and experimental predictions
        """
        return {
            "pathway_hypothesis": {
                "prediction": "Coherence-dependent pathway structure with preserved population correlations",
                "test_method": "Compare superposition vs computational basis state pathway behavior",
                "expected_signature": "Phase-sensitive decoherence with population-independent pathways"
            },
            "decoherence_characteristics": {
                "energy_conservation": "Perfect - no energy exchange with environment",
                "topology_dependence": "Moderate - affects coherent superposition components selectively",
                "pathway_asymmetry": "Phase-dependent - coherent pathways affected differently than incoherent",
                "scaling_behavior": "Exponential coherence decay with preserved populations"
            },
            "experimental_role": {
                "coherence_testing": "Primary model for pure dephasing pathway analysis",
                "t2_star_studies": "Investigate pathway structure vs coherence timescales",
                "elastic_scattering": "Study energy-preserving decoherence pathways",
                "phase_sensitivity_mapping": "Test phase-dependent pathway preferences"
            },
            "research_predictions": {
                "vs_amplitude_damping": "Should preserve populations unlike energy-exchanging amplitude damping",
                "temperature_independence": "Minimal temperature dependence compared to thermal processes",
                "coherence_scaling": "Coherent pathways decay faster than population-based pathways",
                "phase_correlations": "Loss of phase correlations with preserved amplitude correlations"
            },
            "educational_applications": {
                "pure_dephasing": "Demonstrate pure dephasing vs mixed decoherence processes",
                "t2_star_physics": "Connect microscopic noise to macroscopic coherence measurements",
                "ramsey_interferometry": "Show experimental techniques for measuring phase coherence",
                "elastic_processes": "Illustrate energy-conserving environmental interactions"
            }
        }
    
    def _validate_phase_damping_params(
        self, 
        error_rate: float, 
        t2_star: float, 
        gate_time: float, 
        temperature: float
    ) -> None:
        """
        Validate phase damping parameters against physics constraints.
        
        # Physics Constraint Validation
        Ensures all parameters represent realistic phase damping scenarios
        consistent with quantum mechanics and experimental constraints.
        """
        # Validate dephasing probability
        if not 0 <= error_rate <= 1:
            raise ValueError(
                f"Phase damping rate must be in [0,1], got {error_rate}"
            )
        
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
        """
        Calculate thermal contribution to dephasing at operating temperature.
        
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
    
    def _calculate_effective_dephasing_rate(self) -> float:
        """
        Calculate effective dephasing rate including thermal contributions.
        
        # Effective Rate Calculation
        Combines intrinsic dephasing with thermal contributions:
        λ_eff = λ_intrinsic + λ_thermal
        
        Returns:
            Effective dephasing rate for gate application
        """
        base_rate = self._physics_dephasing_rate
        thermal_contribution = self._thermal_dephasing
        
        # Add thermal contribution (typically small)
        return min(1.0, base_rate + thermal_contribution)
    
    def _get_gate_sensitivity_map(self) -> Dict[str, float]:
        """
        Get gate-specific dephasing sensitivity factors.
        
        # Gate Sensitivity Physics
        Different gates have different sensitivities to dephasing:
        - Virtual gates (pure Z rotations): Minimal dephasing
        - Physical gates: Full dephasing during execution
        - Idle operations: Time-dependent dephasing
        
        Returns:
            Dict mapping gate names to sensitivity factors [0, 1]
        """
        return {
            # Virtual gates (minimal physical implementation)
            'z': 0.0, 'rz': 0.0, 'u1': 0.0, 'p': 0.0,
            
            # Identity and idle (time-dependent dephasing)
            'id': 0.1,
            
            # Physical single-qubit gates (full sensitivity)
            'x': 1.0, 'y': 1.0, 'h': 1.0,
            'rx': 1.0, 'ry': 1.0,
            
            # Phase gates (moderate sensitivity)
            's': 0.5, 't': 0.5, 'sdg': 0.5, 'tdg': 0.5,
            
            # Composite gates (full sensitivity)
            'u2': 1.0, 'u3': 1.0, 'u': 1.0
        }
    
    def _calculate_channel_capacity(self) -> float:
        """
        Calculate quantum channel capacity for phase damping.
        
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
    
    def _get_pathway_prediction(self) -> str:
        """
        Get specific pathway prediction for phase damping noise.
        
        Returns:
            Phase damping specific pathway hypothesis prediction
        """
        return (
            f"Phase damping should create coherence-dependent pathway structure "
            f"with dephasing rate {self.error_rate:.4f}. Pathways should preserve "
            f"population correlations while losing phase relationships."
        )
    
    def _assess_topology_sensitivity(self) -> str:
        """
        Assess phase damping sensitivity to quantum state topology.
        """
        return (
            "Moderate topology sensitivity expected due to coherence-dependence. "
            "States with more superposition components should show stronger "
            "pathway sensitivity to dephasing."
        )
    
    def _analyze_pathway_preferences(self) -> str:
        """
        Analyze phase damping pathway preferences.
        """
        return (
            f"Coherence-dependent pathway preferences. Phase damping preferentially "
            f"affects coherent superposition pathways while preserving computational "
            f"basis pathways with thermal contribution {self._thermal_dephasing:.4f}."
        )
    
    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        if self.t2_star:
            return (
                f"Phase damping: T2*={self.t2_star:.2e}s, λ={self.error_rate:.4f}, "
                f"temp={self.temperature}K [pure dephasing]"
            )
        else:
            return (
                f"Phase damping: λ={self.error_rate:.4f} "
                f"[phenomenological pure dephasing]"
            )
