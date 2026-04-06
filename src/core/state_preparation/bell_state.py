"""Bell State Preparation for Fundamental Entanglement Research.

# The Bell States (Einstein-Podolsky-Rosen Pairs)
Bell states represent the fundamental building blocks of quantum entanglement,
demonstrating two-qubit quantum correlations that cannot be explained by
classical physics. These states form the foundation of quantum information.

# The Four Bell States
|Φ+⟩ = (|00⟩ + |11⟩)/√2  [phi_plus]  - Standard maximally entangled state
|Φ-⟩ = (|00⟩ - |11⟩)/√2  [phi_minus] - Phase-flipped entangled state
|Ψ+⟩ = (|01⟩ + |10⟩)/√2  [psi_plus]  - Bit-flipped entangled state
|Ψ-⟩ = (|01⟩ - |10⟩)/√2  [psi_minus] - Both phase and bit flipped

# Research Applications in Decoherence Studies
Bell states provide the minimal case for studying structured decoherence:
- Binary entanglement: Simplest case of quantum correlation breakdown
- Local vs global effects: How noise on one qubit affects the other
- Entanglement sudden death: Discrete loss of quantum correlations
"""

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from .base_state import BaseState


class BellState(BaseState):
    """Bell state preparation for fundamental entanglement research.

    # Quantum Entanglement Foundation
    Bell states demonstrate the core phenomenon of quantum mechanics:
    measurement outcomes on separated particles remain correlated
    regardless of distance. This "spooky action at a distance" forms
    the basis for quantum computing and quantum communication.

    # Educational Significance
    - Historical: Resolves Einstein-Podolsky-Rosen paradox
    - Practical: Foundation for quantum teleportation and cryptography
    - Theoretical: Demonstrates non-locality and Bell's theorem violations

    # Circuit Construction
    All Bell states start from |Φ+⟩ = (|00⟩ + |11⟩)/√2 then apply:
    - Φ-: Phase flip (Z gate) → relative phase change
    - Ψ+: Bit flip (X gate) → computational basis change
    - Ψ-: Both phase and bit flip → combined transformation
    """

    def __init__(
        self,
        num_qubits: int,
        custom_params: dict = None,
        experiment_id: str = "N/A",
        **kwargs: Any,
    ):
        """Initialize Bell state with variant specification.

        Args:
            num_qubits: Must be exactly 2 for Bell states.
            custom_params: Dictionary with 'variant' key specifying Bell state type.
            experiment_id: Unique identifier for experiment tracking.
            **kwargs: Additional keyword arguments (ignored).

        Raises:
            ValueError: If num_qubits != 2 (Bell states are strictly two-qubit).
        """
        if num_qubits != 2:
            raise ValueError(
                f"Bell states require exactly 2 qubits, got {num_qubits}. "
                f"Note: For multi-qubit entanglement, use GHZ or W states."
            )

        super().__init__(num_qubits, custom_params, experiment_id)

        # Validate Bell state variant
        valid_variants = ["phi_plus", "phi_minus", "psi_plus", "psi_minus"]
        variant = (custom_params or {}).get("variant", "phi_plus").lower()
        if variant not in valid_variants:
            raise ValueError(f"Invalid Bell variant: '{variant}'. Choose from: {valid_variants}")

    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        """Create quantum circuit that prepares the specified Bell state.

        # Bell State Construction Strategy
        1. Start with computational basis: |00⟩
        2. Create superposition: H|0⟩ → (|0⟩ + |1⟩)/√2
        3. Create entanglement: CNOT → (|00⟩ + |11⟩)/√2 = |Φ+⟩
        4. Apply variant transformations for other Bell states

        # Variant Transformations
        - Φ+ (phi_plus): No additional gates [default]
        - Φ- (phi_minus): Z gate on first qubit (phase flip)
        - Ψ+ (psi_plus): X gate on second qubit (bit flip)
        - Ψ- (psi_minus): Both Z and X gates (phase + bit flip)

        Args:
            add_barrier: Add quantum barrier for circuit visualization

        Returns:
            QuantumCircuit: Circuit that prepares the specified Bell state

        Example:
            >>> bell = BellState(2, {"variant": "phi_plus"})
            >>> circuit = bell.create()
            >>> print(circuit)  # Shows H-CNOT pattern
        """
        # Get Bell state variant
        variant = (self.custom_params or {}).get("variant", "phi_plus").lower()

        # Create 2-qubit circuit
        circuit = QuantumCircuit(2)

        # Base Bell state preparation: |Φ+⟩ = (|00⟩ + |11⟩)/√2
        circuit.h(0)  # Create superposition on qubit 0
        circuit.cx(0, 1)  # Entangle qubits 0 and 1

        # Apply variant-specific transformations
        if variant == "phi_plus":
            # |Φ+⟩ = (|00⟩ + |11⟩)/√2 - No additional gates needed
            pass

        elif variant == "phi_minus":
            # |Φ-⟩ = (|00⟩ - |11⟩)/√2 - Apply phase flip
            circuit.z(0)  # Z gate creates relative phase

        elif variant == "psi_plus":
            # |Ψ+⟩ = (|01⟩ + |10⟩)/√2 - Apply bit flip
            circuit.x(1)  # X gate flips second qubit

        elif variant == "psi_minus":
            # |Ψ-⟩ = (|01⟩ - |10⟩)/√2 - Apply both transformations
            circuit.z(1)  # Phase flip on second qubit
            circuit.x(1)  # Bit flip on second qubit
            # Note: Combined Z-X creates the correct relative phase

        # Optional: Add barrier for visualization
        if add_barrier:
            circuit.barrier()

        # Log successful creation
        self.log_state_creation(
            f"Bell {variant.upper()}",
            {
                "variant": variant,
                "entanglement_type": "maximal_bipartite",
                "circuit_depth": 3 if variant in ["psi_minus"] else 2,
                "measurement_correlations": "perfect_anti-correlation"
                if "minus" in variant
                else "perfect_correlation",
            },
        )

        return circuit

    def get_theoretical_state_vector(self) -> np.ndarray:
        """Calculate the theoretical Bell state vector for validation.

        # Mathematical Definitions
        |Φ+⟩ = (|00⟩ + |11⟩)/√2 = [1/√2, 0, 0, 1/√2]
        |Φ-⟩ = (|00⟩ - |11⟩)/√2 = [1/√2, 0, 0, -1/√2]
        |Ψ+⟩ = (|01⟩ + |10⟩)/√2 = [0, 1/√2, 1/√2, 0]
        |Ψ-⟩ = (|01⟩ - |10⟩)/√2 = [0, 1/√2, -1/√2, 0]

        Returns:
            np.ndarray: Complex state vector [|00⟩, |01⟩, |10⟩, |11⟩]

        Example:
            >>> bell = BellState(2, {"variant": "phi_plus"})
            >>> state = bell.get_theoretical_state_vector()
            >>> print(state)  # [0.707, 0, 0, 0.707]
        """
        # Get Bell state variant
        variant = (self.custom_params or {}).get("variant", "phi_plus").lower()

        # Amplitude for normalized states
        amplitude = 1.0 / np.sqrt(2)

        # Initialize 4-dimensional state vector for 2 qubits
        state_vector = np.zeros(4, dtype=complex)

        if variant == "phi_plus":
            # |Φ+⟩ = (|00⟩ + |11⟩)/√2
            state_vector[0] = amplitude  # |00⟩
            state_vector[3] = amplitude  # |11⟩

        elif variant == "phi_minus":
            # |Φ-⟩ = (|00⟩ - |11⟩)/√2
            state_vector[0] = amplitude  # |00⟩
            state_vector[3] = -amplitude  # |11⟩ with negative phase

        elif variant == "psi_plus":
            # |Ψ+⟩ = (|01⟩ + |10⟩)/√2
            state_vector[1] = amplitude  # |01⟩
            state_vector[2] = amplitude  # |10⟩

        elif variant == "psi_minus":
            # |Ψ-⟩ = (|01⟩ - |10⟩)/√2
            state_vector[1] = amplitude  # |01⟩
            state_vector[2] = -amplitude  # |10⟩ with negative phase

        return state_vector

    def _estimate_circuit_depth(self) -> int:
        """Estimate circuit depth for Bell state preparation.

        # Depth Analysis by Variant
        - Φ+: H + CNOT = 2 gates
        - Φ-: H + CNOT + Z = 3 gates
        - Ψ+: H + CNOT + X = 3 gates
        - Ψ-: H + CNOT + Z + X = 4 gates (but Z,X can be parallel)

        Returns:
            int: Circuit depth for this Bell state variant
        """
        variant = (self.custom_params or {}).get("variant", "phi_plus").lower()

        if variant == "phi_plus":
            return 2  # H + CNOT
        elif variant in ["phi_minus", "psi_plus"]:
            return 3  # H + CNOT + (Z or X)
        else:  # psi_minus
            return 3  # H + CNOT + combined Z-X transformation

    def _get_required_gates(self) -> list[str]:
        """Get quantum gates required for Bell state preparation.

        Returns:
            List[str]: Required gate names for this Bell variant
        """
        variant = (self.custom_params or {}).get("variant", "phi_plus").lower()

        base_gates = ["h", "cx"]  # All Bell states need H and CNOT

        if variant == "phi_minus":
            return base_gates + ["z"]
        elif variant == "psi_plus":
            return base_gates + ["x"]
        elif variant == "psi_minus":
            return base_gates + ["z", "x"]
        else:  # phi_plus
            return base_gates

    def get_theoretical_properties(self) -> dict[str, Any]:
        """Get theoretical quantum properties specific to Bell states.

        Returns:
            Dict with Bell-specific theoretical properties
        """
        variant = (self.custom_params or {}).get("variant", "phi_plus").lower()

        # Common properties for all Bell states
        base_properties = {
            "entanglement_type": "maximal_bipartite",
            "schmidt_rank": 2,
            "von_neumann_entropy": 1.0,  # log2(2) = 1 bit
            "bell_inequality_violation": "maximal",
            "concurrence": 1.0,  # Maximum entanglement
            "robustness_to_decoherence": "moderate",
        }

        # Variant-specific properties
        if variant in ["phi_plus", "phi_minus"]:
            measurement_basis = "computational (Z-basis)"
            correlation_type = (
                "perfect correlation" if variant == "phi_plus" else "perfect anti-correlation"
            )
        else:  # psi_plus, psi_minus
            measurement_basis = "superposition (X-basis)"
            correlation_type = (
                "perfect correlation" if variant == "psi_plus" else "perfect anti-correlation"
            )

        base_properties.update(
            {
                "variant": variant,
                "optimal_measurement_basis": measurement_basis,
                "correlation_type": correlation_type,
                "classical_correlation_bound": 0.5,  # Bell inequality bound
                "quantum_correlation_achieved": 1.0,  # Maximum violation
            }
        )

        return base_properties

    def get_research_context(self) -> dict[str, Any]:
        """Get research context for Bell state decoherence studies.

        Returns:
            Dict with research context and experimental predictions
        """
        variant = (self.custom_params or {}).get("variant", "phi_plus").lower()

        return {
            "pathway_hypothesis": {
                "prediction": "Binary entanglement → coupled decoherence pathways",
                "test_method": "Monitor correlation decay between entangled outcomes",
                "expected_signature": "Synchronized loss of quantum correlations",
            },
            "decoherence_characteristics": {
                "entanglement_sudden_death": "Finite-time complete correlation loss",
                "local_vs_global": "Test whether single-qubit noise affects both qubits",
                "symmetry_breaking": f"Monitor {variant} state symmetry under noise",
            },
            "research_applications": {
                "quantum_communication": "Bell states enable quantum teleportation",
                "cryptography": "Foundation for quantum key distribution",
                "computation": "Building blocks for quantum algorithms",
            },
            "experimental_advantages": {
                "simplicity": "Only 2 qubits - minimal complexity",
                "clear_signatures": "Binary outcomes easy to analyze",
                "theoretical_foundation": "Well-understood analytical predictions",
            },
        }

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        variant = (self.custom_params or {}).get("variant", "phi_plus").lower()

        state_symbols = {
            "phi_plus": "|Φ+⟩ = (|00⟩ + |11⟩)/√2",
            "phi_minus": "|Φ-⟩ = (|00⟩ - |11⟩)/√2",
            "psi_plus": "|Ψ+⟩ = (|01⟩ + |10⟩)/√2",
            "psi_minus": "|Ψ-⟩ = (|01⟩ - |10⟩)/√2",
        }

        return f"Bell {variant.upper()}: {state_symbols[variant]}"
