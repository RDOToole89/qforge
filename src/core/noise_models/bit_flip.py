"""
Bit Flip Noise for Classical Digital Error Research

# The Bit Flip Channel - Classical Computational Basis Errors
Bit flip noise represents classical digital errors where computational basis states
are randomly flipped: |0⟩ ↔ |1⟩. This models the simplest form of classical
error that preserves the computational structure while corrupting information.

# Physical Mechanism
Bit flip errors arise from transverse coupling to environmental fields that
cause unwanted X rotations:
- Microwave drive field fluctuations causing imperfect π pulses
- Crosstalk between neighboring qubits inducing unwanted rotations
- Control electronics noise creating random X gate applications
- AC Stark shifts from off-resonant driving fields

# Mathematical Description
The bit flip channel maps quantum states as:
ρ → (1-p)ρ + p(XρX) where X is the Pauli X operator
Kraus operators: K₀ = √(1-p)I, K₁ = √p X

# Hardware Origins
- Imperfect microwave pulse calibration in superconducting qubits
- Crosstalk and leakage in ion trap operations
- Control field amplitude noise and drift
- AC Stark shifts from imperfect pulse shaping

# Research Significance for Structured Pathways
Bit flip noise creates computational basis transitions that may reveal
structural biases in how classical error patterns propagate through
quantum networks, distinct from phase-based or energy-based decoherence.

# Educational Framework
Bit flip channels demonstrate fundamental concepts:
- Classical error models and their quantum generalizations
- Computational basis preservation with information corruption
- Coherent vs incoherent error mechanisms
- The relationship between drive field errors and bit flip rates
"""

import numpy as np
import logging
from typing import List, Dict, Any
from qiskit_aer.noise import NoiseModel, pauli_error
from .base_noise import BaseNoise

logger = logging.getLogger("QuantumExperiment.NoiseModels")


class BitFlipNoise(BaseNoise):
    """
    Bit flip noise model for classical digital error research.
    
    # Quantum Bit Flip Definition
    The bit flip channel models classical computational errors by applying
    random X (NOT) operations with probability p. This preserves the
    computational basis structure while corrupting stored information.
    
    This represents the quantum generalization of classical bit errors,
    making it ideal for studying digital error propagation patterns.
    
    # Physical Interpretation
    Bit flip noise models environmental coupling that is:
    - **Computational**: Affects stored digital information directly
    - **Basis-preserving**: Maintains computational basis structure
    - **Transverse**: Couples in X direction of Bloch sphere
    - **Coherent**: Can arise from coherent drive field errors
    
    # Research Applications in Pathway Studies
    - **Digital Pathways**: Test how classical errors propagate through quantum networks
    - **Basis Structure**: Study pathway dependence on computational basis preservation
    - **Classical Comparison**: Compare with quantum-specific decoherence mechanisms
    - **Error Correction**: Investigate pathway structure for classical error correction
    
    # Educational Significance
    Bit flip channels illustrate fundamental concepts:
    - **Classical Error Models**: Quantum generalization of digital bit errors
    - **Pauli Channel Structure**: Single Pauli operator error mechanisms
    - **Drive Field Errors**: How control field imperfections create bit flips
    - **Computational Basis**: Preservation of |0⟩, |1⟩ structure with content errors
    """

    def __init__(
        self, 
        error_rate: float = 0.05, 
        num_qubits: int = 1, 
        experiment_id: str = "N/A",
        coherent_error: bool = False,
        pulse_amplitude_error: float = None
    ):
        """
        Initialize bit flip noise with physics-based validation.
        
        # Physics Parameter Integration
        Supports both phenomenological bit flip rates and physics-based
        pulse error calculations:
        - Phenomenological: Direct specification of bit flip probability p
        - Physics-based: Calculate from pulse amplitude errors Δa/a
        - Coherent mode: Model systematic over/under-rotation errors
        
        Args:
            error_rate: Phenomenological bit flip probability p ∈ [0, 1]
            num_qubits: Number of qubits (bit flip is single-qubit)
            experiment_id: Unique identifier for experimental tracking
            coherent_error: Model as coherent rotation error vs incoherent flip
            pulse_amplitude_error: Relative pulse amplitude error (overrides error_rate)
            
        Raises:
            ValueError: If parameters violate physics constraints
            
        Example:
            >>> # Phenomenological bit flip
            >>> noise = BitFlipNoise(error_rate=0.01)
            
            >>> # Physics-based pulse error
            >>> noise = BitFlipNoise(
            ...     pulse_amplitude_error=0.02, coherent_error=True
            ... )
        """
        # Physics parameter validation before initialization
        self._validate_bit_flip_params(error_rate, pulse_amplitude_error)
        
        # Store physics parameters
        self.coherent_error = coherent_error
        self.pulse_amplitude_error = pulse_amplitude_error
        
        # Calculate effective bit flip rate
        if pulse_amplitude_error is not None:
            # Physics-based: p ≈ (Δa/a)² for small amplitude errors
            self._physics_flip_rate = min(1.0, pulse_amplitude_error**2)
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
            coherent_error=coherent_error,
            pulse_amplitude_error=pulse_amplitude_error
        )
        
        # Calculate derived properties
        self._flip_probabilities = self._calculate_flip_probabilities()
        
        # Log creation with physics context
        self.log_noise_creation(
            "BIT_FLIP",
            {
                "physics_flip_rate": self._physics_flip_rate,
                "flip_probabilities": self._flip_probabilities,
                "coherent_error": coherent_error,
                "pulse_amplitude_error": pulse_amplitude_error,
                "decoherence_type": "computational_basis_transverse",
                "channel_property": "unital",
                "research_role": "classical_digital_error_investigation"
            }
        )

    def apply(self, noise_model: NoiseModel, gate_list: List[str], qubits_for_error: int = None) -> None:
        """
        Apply bit flip noise to single-qubit quantum gates.
        
        # Classical Digital Error Implementation
        Creates Qiskit Pauli error channels that model bit flip transitions:
        |0⟩ → |1⟩ and |1⟩ → |0⟩ with probability p. This preserves computational
        basis structure while corrupting stored digital information.
        
        # Gate Application Strategy
        Bit flip noise primarily affects single-qubit operations:
        - X gates: Maximum sensitivity (coherent amplitude errors)
        - Z gates: Minimal sensitivity (different error axis)
        - General gates: Intermediate sensitivity based on X component
        
        Args:
            noise_model: Qiskit noise model to modify with bit flip errors
            gate_list: Quantum gates to apply noise to (single-qubit focus)
            qubits_for_error: Override qubit count (bit flip uses 1)
            
        Example:
            >>> noise_model = NoiseModel()
            >>> gates = ['h', 'x', 'cx']  # All gates get bit flip noise
            >>> bit_flip_noise.apply(noise_model, gates)
        """
        # Bit flip is inherently single-qubit but can affect all operations
        if qubits_for_error is not None and qubits_for_error != 1:
            logger.warning(
                f"Bit flip is single-qubit, but applying to {qubits_for_error}-qubit gates"
            )
        
        # Gate sensitivity mapping for bit flip errors
        gate_sensitivity = self._get_gate_sensitivity_map()
        
        # Apply bit flip noise to all gates with sensitivity weighting
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
                    
                    # Create Pauli error with bit flip probability
                    bit_flip_channel = pauli_error([
                        ("I", identity_prob),
                        ("X", effective_flip_prob)
                    ])
                    
                    noise_model.add_all_qubit_quantum_error(bit_flip_channel, gate)
                    successful_gates.append(f"{gate}(s={sensitivity:.2f})")
                else:
                    # Gates immune to bit flip (pure Z operations)
                    successful_gates.append(f"{gate}(immune)")
                    
            except Exception as e:
                failed_gates.append((gate, str(e)))
        
        # Log application results with physics context
        if successful_gates:
            logger.info(
                f"Applied BIT_FLIP noise (p={self.error_rate:.4f}) to "
                f"gates: {successful_gates} "
                f"(coherent={self.coherent_error}) "
                f"(experiment: {self.experiment_id})"
            )
        
        if failed_gates:
            logger.warning(
                f"Failed to apply BIT_FLIP noise to gates: "
                f"{[gate for gate, _ in failed_gates]}"
            )
    
    def get_kraus_operators(self) -> List[np.ndarray]:
        """
        Return Kraus operators for the bit flip channel.
        
        # Mathematical Construction
        For bit flip channel with flip probability p:
        K₀ = √(1-p) I  (identity with no flip)
        K₁ = √p X      (Pauli X bit flip)
        
        These satisfy K₀†K₀ + K₁†K₁ = I (completeness relation).
        
        Returns:
            List of Kraus operators as numpy arrays
            
        Educational Note:
            The X operator K₁ = [[0,1],[1,0]] implements |0⟩ ↔ |1⟩ swapping
            while preserving computational basis structure.
        """
        p = self.error_rate
        
        # Identity operator (no bit flip)
        K0 = np.sqrt(1 - p) * np.eye(2, dtype=complex)
        
        # Pauli X operator (bit flip)
        K1 = np.sqrt(p) * np.array([[0, 1], [1, 0]], dtype=complex)
        
        return [K0, K1]
    
    def get_physics_description(self) -> Dict[str, str]:
        """
        Return comprehensive physics description of bit flip decoherence.
        
        Returns:
            Dict with educational physics content about classical bit errors
        """
        return {
            "mechanism": "Classical bit flip: computational basis states |0⟩ ↔ |1⟩ are randomly swapped",
            "origin": "Microwave drive field errors, pulse amplitude noise, crosstalk between qubits",
            "mathematical_form": f"K₀ = √(1-{self.error_rate:.3f})I, K₁ = √{self.error_rate:.3f}X",
            "physical_timescale": f"Pulse error rate = {self.pulse_amplitude_error:.3f}" if self.pulse_amplitude_error else "phenomenological rate",
            "coherent_mode": f"Coherent rotation error: {self.coherent_error}",
            "computational_preservation": "Preserves computational basis structure while corrupting information content",
            "channel_properties": "Unital (preserves maximally mixed states), trace-preserving, completely positive",
            "real_world_examples": "Superconducting qubit drive errors, ion trap laser intensity fluctuations, semiconductor gate voltage noise",
            "quantum_principles": "Classical error generalization, Pauli channels, computational basis errors"
        }
    
    def get_theoretical_properties(self) -> Dict[str, Any]:
        """
        Get theoretical quantum properties specific to bit flip channels.
        
        Returns:
            Dict with bit flip channel specific properties
        """
        return {
            "decoherence_type": "computational_basis_transverse",
            "channel_classification": "unital",
            "flip_probability": self.error_rate,
            "no_flip_probability": 1 - self.error_rate,
            "coherent_error_mode": self.coherent_error,
            "pulse_amplitude_error": self.pulse_amplitude_error,
            "computational_structure": "preserved",
            "information_corruption": "digital_bit_level",
            "measurement_bias": "none_symmetric_bit_flips",
            "pauli_operator": "X_transverse_coupling",
            "unitality": True,
            "reversibility": False,  # Information loss is irreversible
            "information_capacity": self._calculate_channel_capacity()
        }
    
    def get_research_context(self) -> Dict[str, Any]:
        """
        Get research context for bit flip noise in pathway studies.
        
        Returns:
            Dict with research context and experimental predictions
        """
        return {
            "pathway_hypothesis": {
                "prediction": "Classical error propagation patterns with computational basis preservation",
                "test_method": "Compare digital vs quantum-specific error pathway structures",
                "expected_signature": "Pathway structure preserving |0⟩, |1⟩ while corrupting superposition content"
            },
            "decoherence_characteristics": {
                "error_type": "Classical digital errors with quantum generalization",
                "topology_dependence": "Moderate - affects computational basis correlations uniformly",
                "pathway_asymmetry": "Minimal - symmetric bit flip transitions",
                "scaling_behavior": "Linear scaling with computational basis population"
            },
            "experimental_role": {
                "classical_comparison": "Baseline for classical vs quantum error pathway differences",
                "digital_error_testing": "Test pathway behavior under pure computational errors",
                "basis_preservation_studies": "Investigate pathway structure with preserved basis",
                "error_correction_relevance": "Model errors addressable by classical error correction"
            },
            "research_predictions": {
                "vs_depolarizing": "Should show computational basis preservation unlike uniform depolarizing",
                "vs_phase_errors": "Should corrupt information content unlike phase-only errors",
                "coherent_effects": "Coherent bit flips may show different pathway structure than incoherent",
                "measurement_correlations": "Preserve measurement correlations while corrupting state content"
            },
            "educational_applications": {
                "classical_errors": "Demonstrate quantum generalization of classical bit errors",
                "pauli_channels": "Illustrate single Pauli operator error mechanisms",
                "computational_basis": "Show preservation of computational structure with content corruption",
                "error_correction": "Model errors correctable by classical error correction codes"
            }
        }
    
    def _validate_bit_flip_params(
        self, 
        error_rate: float, 
        pulse_amplitude_error: float
    ) -> None:
        """
        Validate bit flip parameters against physics constraints.
        
        # Physics Constraint Validation
        Ensures all parameters represent realistic bit flip scenarios
        consistent with quantum mechanics and control field physics.
        """
        # Validate flip probability
        if not 0 <= error_rate <= 1:
            raise ValueError(
                f"Bit flip rate must be in [0,1], got {error_rate}"
            )
        
        # Validate pulse amplitude error if provided
        if pulse_amplitude_error is not None:
            if pulse_amplitude_error < 0:
                raise ValueError(f"Pulse amplitude error must be non-negative, got {pulse_amplitude_error}")
            if pulse_amplitude_error > 0.5:
                logger.warning(
                    f"Large pulse amplitude error ({pulse_amplitude_error:.3f}) may indicate "
                    f"regime where perturbative approximations break down"
                )
    
    def _calculate_flip_probabilities(self) -> Dict[str, float]:
        """
        Calculate individual flip probabilities for educational display.
        
        Returns:
            Dict mapping operators to their probabilities
        """
        return {
            "identity": 1 - self.error_rate,
            "bit_flip_x": self.error_rate
        }
    
    def _get_gate_sensitivity_map(self) -> Dict[str, float]:
        """
        Get gate-specific bit flip sensitivity factors.
        
        # Gate Sensitivity Physics
        Different gates have different sensitivities to bit flip errors:
        - X gates: Maximum sensitivity (direct amplitude coupling)
        - Z gates: Minimal sensitivity (orthogonal error axis)
        - General gates: Sensitivity based on X component
        
        Returns:
            Dict mapping gate names to sensitivity factors [0, 1]
        """
        return {
            # X-axis gates (maximum sensitivity)
            'x': 1.0, 'rx': 1.0,
            
            # Y-axis gates (moderate sensitivity - has X component)
            'y': 0.7, 'ry': 0.7,
            
            # Hadamard (moderate sensitivity - creates X component)
            'h': 0.5,
            
            # Z-axis gates (minimal sensitivity - orthogonal axis)
            'z': 0.0, 'rz': 0.0, 'u1': 0.0, 'p': 0.0, 's': 0.0, 't': 0.0, 'sdg': 0.0, 'tdg': 0.0,
            
            # Identity (small sensitivity during idle)
            'id': 0.1,
            
            # General single-qubit gates (intermediate sensitivity)
            'u2': 0.5, 'u3': 0.8, 'u': 0.8
        }
    
    def _calculate_channel_capacity(self) -> float:
        """
        Calculate quantum channel capacity for bit flip channel.
        
        # Information Theory
        Channel capacity for bit flip depends on the flip probability
        and can be calculated using quantum information theory.
        """
        p = self.error_rate
        if p == 0:
            return 1.0  # Perfect channel
        elif p == 1:
            return 0.0  # Always flip (deterministic but useless)
        elif p == 0.5:
            return 0.0  # Maximally noisy channel
        else:
            # Binary symmetric channel capacity
            h_p = -p * np.log2(p) - (1-p) * np.log2(1-p) if p > 0 and p < 1 else 0
            return max(0, 1 - h_p)
    
    def _get_pathway_prediction(self) -> str:
        """
        Get specific pathway prediction for bit flip noise.
        
        Returns:
            Bit flip specific pathway hypothesis prediction
        """
        return (
            f"Bit flip noise should create computational basis pathway structure "
            f"with flip rate {self.error_rate:.4f}. Pathways should preserve "
            f"computational basis correlations while corrupting information content."
        )
    
    def _assess_topology_sensitivity(self) -> str:
        """
        Assess bit flip noise sensitivity to quantum state topology.
        """
        return (
            "Moderate topology sensitivity expected due to computational basis preservation. "
            "States with more computational basis components should show different "
            "pathway behavior than pure superposition states."
        )
    
    def _analyze_pathway_preferences(self) -> str:
        """
        Analyze bit flip noise pathway preferences.
        """
        return (
            f"Computational basis pathway preferences. Bit flip errors preferentially "
            f"affect stored information while preserving |0⟩, |1⟩ structure with "
            f"coherent mode: {self.coherent_error}."
        )
    
    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        if self.pulse_amplitude_error:
            return (
                f"Bit flip: pulse_error={self.pulse_amplitude_error:.3f}, p={self.error_rate:.4f}, "
                f"coherent={self.coherent_error} [classical digital error]"
            )
        else:
            return (
                f"Bit flip: p={self.error_rate:.4f} "
                f"[phenomenological classical bit error]"
            )
