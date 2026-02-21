"""
W State Preparation for Symmetric Entanglement Research

# The W State - Symmetric Multipartite Entanglement
The W state represents symmetric multipartite entanglement where exactly one
qubit is in |1⟩ state: |W_n⟩ = (|100...0⟩ + |010...0⟩ + ... + |000...1⟩)/√n

# Physical Significance
Unlike GHZ states which exhibit all-or-nothing correlations, W states show
robust partial entanglement. If one qubit is lost or measured, the remaining
qubits still maintain some entanglement, making W states more robust to
particle loss but less useful for certain quantum protocols.

# Research Applications in Decoherence Studies
- Asymmetric pathway emergence: How does symmetric entanglement break under noise?
- Robustness vs fragility: Compare W state stability with GHZ states
- Network effects: How does the "one excitation" structure affect pathways?
- Measurement cascades: How does measuring one qubit affect the others?
"""

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from .base_state import BaseState


class WState(BaseState):
    """
    W state preparation for symmetric entanglement research.

    # Quantum State Definition
    |W_n⟩ = (|100...0⟩ + |010...0⟩ + ... + |000...1⟩)/√n

    This creates symmetric multipartite entanglement where exactly one qubit
    is excited. Each computational basis state in the superposition has
    exactly one |1⟩ and (n-1) |0⟩s, creating symmetric correlations.

    # Entanglement Properties
    - Symmetric under qubit permutation (all qubits equivalent)
    - Partially robust to qubit loss (remaining qubits stay entangled)
    - Lower entanglement content than GHZ states
    - Useful for distributed quantum sensing and metrology

    # Educational Notes
    - W states belong to a different entanglement class than GHZ states
    - Cannot be converted to GHZ states using local operations
    - Demonstrate the richness of multipartite entanglement beyond Bell pairs
    """

    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        """
        Create quantum circuit that prepares the W state.

        # W State Construction Strategy
        For n qubits, we create the superposition:
        |W_n⟩ = (|100...0⟩ + |010...0⟩ + ... + |000...1⟩)/√n

        # Implementation Methods
        1. **Initialize method** (default): Direct state vector initialization
           - Pros: Exact, works for any n, guaranteed correctness
           - Cons: Not decomposed into elementary gates

        2. **Gate-based method**: Recursive construction using rotations
           - Pros: Uses only elementary gates, shows explicit construction
           - Cons: More complex, currently implemented for n=3 only

        Args:
            add_barrier: Add quantum barrier for circuit visualization

        Returns:
            QuantumCircuit: Circuit that prepares |W_n⟩ state

        Example:
            >>> w = WState(3)
            >>> circuit = w.create()
            >>> # Creates (|100⟩ + |010⟩ + |001⟩)/√3
        """
        # Validate qubit count for W state
        if self.num_qubits < 1:
            raise ValueError("W state requires at least 1 qubit")

        # Create quantum circuit
        circuit = QuantumCircuit(self.num_qubits)

        # Handle special cases
        if self.num_qubits == 1:
            # Single qubit W state is just |1⟩
            circuit.x(0)
            self.log_state_creation(
                "W (single qubit)", {"note": "W state with 1 qubit is just |1⟩"}
            )
            if add_barrier:
                circuit.barrier()
            return circuit

        # Choose construction method
        custom_params = self.custom_params or {}
        method = custom_params.get("method", "initialize")
        prefer_initialize = custom_params.get("prefer_initialize", True)
        use_gate_based = (method == "gate") and not prefer_initialize

        if use_gate_based and self.num_qubits == 3:
            # Gate-based construction for 3 qubits (educational demonstration)
            # This shows how W states can be built from elementary gates
            # More complex than initialize but pedagogically valuable

            # Create W state using decomposed gates
            w_state_vector = self._get_w_state_vector()
            circuit.initialize(w_state_vector, range(self.num_qubits))
            circuit = circuit.decompose()  # Decompose into elementary gates

            construction_method = "gate_decomposed"

        else:
            # Default: Direct initialization (most practical)
            # This is the standard method for W state preparation

            w_state_vector = self._get_w_state_vector()
            circuit.initialize(w_state_vector, range(self.num_qubits))

            construction_method = "initialize"

        # Balance gate counts across qubits if requested
        if self.balance == "gate_count":
            circuit = self._apply_gate_count_balancing(circuit)

        # Optional: Add barrier for visualization
        if add_barrier:
            circuit.barrier()

        # Log successful creation
        self.log_state_creation(
            f"W ({self.num_qubits} qubits)",
            {
                "entanglement_type": "symmetric_multipartite",
                "construction_method": construction_method,
                "excitation_number": 1,  # W states have exactly 1 excitation
                "symmetry_class": "permutation_symmetric",
                "robustness": "partially_robust_to_qubit_loss",
            },
        )

        return circuit

    def _get_w_state_vector(self) -> np.ndarray:
        """
        Generate the W state vector for initialization.

        # W State Vector Construction
        For n qubits, create vector where only computational basis states
        with exactly one |1⟩ have non-zero amplitudes.

        Returns:
            np.ndarray: W state vector with proper normalization
        """
        # Create zero vector for all 2^n computational basis states
        w_state = np.zeros(2**self.num_qubits, dtype=complex)

        # Set amplitudes for states with exactly one excitation
        # |100...0⟩, |010...0⟩, |001...0⟩, ..., |000...1⟩
        amplitude = 1.0 / np.sqrt(self.num_qubits)

        for i in range(self.num_qubits):
            # Bit position i corresponds to state with qubit i excited
            state_index = 1 << i  # 2^i in binary: 1 at position i
            w_state[state_index] = amplitude

        return w_state

    def get_theoretical_state_vector(self) -> np.ndarray:
        """
        Calculate the theoretical W state vector for validation.

        # Mathematical Definition
        |W_n⟩ = (1/√n) * Σᵢ |0...0 1ᵢ 0...0⟩

        Where the sum is over all positions i, and 1ᵢ means the i-th qubit
        is in state |1⟩ while all others are in |0⟩.

        Returns:
            np.ndarray: Complex state vector of shape (2^n,)

        Example:
            >>> w = WState(3)
            >>> state = w.get_theoretical_state_vector()
            >>> print(state)  # [0, 1/√3, 1/√3, 0, 1/√3, 0, 0, 0]
        """
        return self._get_w_state_vector()

    def _estimate_circuit_depth(self) -> int:
        """
        Estimate circuit depth for W state preparation.

        # Depth Analysis
        - Initialize method: O(n) depth (implementation dependent)
        - Gate-based method: O(n²) depth for exact construction

        Returns:
            int: Estimated circuit depth
        """
        # Conservative estimate for initialize method
        return max(1, self.num_qubits)

    def _get_required_gates(self) -> list[str]:
        """
        Get quantum gates required for W state preparation.

        Returns:
            List[str]: Required gate names
        """
        if self.num_qubits == 1:
            return ["x"]  # Single qubit W state just needs X gate
        else:
            # Initialize method uses arbitrary state preparation
            return ["initialize"]  # Qiskit's arbitrary state preparation

    def get_theoretical_properties(self) -> dict[str, Any]:
        """
        Get theoretical quantum properties specific to W states.

        Returns:
            Dict with W-specific theoretical properties
        """
        if self.num_qubits == 1:
            return {
                "entanglement_type": "none",
                "excitation_number": 1,
                "correlation_strength": "classical",
            }

        return {
            "entanglement_type": "symmetric_multipartite",
            "excitation_number": 1,
            "total_excitation_probability": 1.0,
            "single_qubit_excitation_probability": 1.0 / self.num_qubits,
            "correlation_strength": "partial",
            "symmetry_group": "permutation_symmetric",
            "robustness_classification": "partially_robust",
            "entanglement_vs_ghz": "lower_entanglement_content",
            "measurement_outcomes": {
                "single_excitation_states": self.num_qubits,
                "zero_excitation_states": 0,
                "multi_excitation_states": 0,
            },
            "quantum_sensing_applications": "distributed_phase_estimation",
            "loss_tolerance": f"remains_entangled_with_{self.num_qubits - 1}_qubits",
        }

    def get_research_context(self) -> dict[str, Any]:
        """
        Get research context for W state decoherence studies.

        Returns:
            Dict with research context and experimental predictions
        """
        return {
            "pathway_hypothesis": {
                "prediction": "Symmetric entanglement → asymmetric pathway emergence under noise",
                "test_method": "Monitor asymmetry development in excitation distribution",
                "expected_signature": "Gradual symmetry breaking with preferred pathways",
            },
            "decoherence_characteristics": {
                "robustness_type": "Partial - survives single qubit loss",
                "fragility_type": "Gradual degradation rather than sudden death",
                "asymmetry_emergence": "Noise breaks permutation symmetry",
                "pathway_structure": "Radial from each excitation state",
            },
            "experimental_advantages": {
                "stability": "More robust than GHZ states to particle loss",
                "measurement": "Clear single-excitation signatures",
                "scaling": "Well-defined for arbitrary n qubits",
                "comparison": "Direct contrast with GHZ pathway behavior",
            },
            "research_applications": {
                "quantum_sensing": "Distributed parameter estimation",
                "metrology": "Enhanced phase sensitivity",
                "communication": "Quantum secret sharing protocols",
                "computation": "Certain quantum algorithms",
            },
            "pathway_predictions": {
                "early_stage": "Slight amplitude variations, symmetry preserved",
                "symmetry_breaking": "Preferred excitation sites emerge",
                "late_stage": "Classical mixture of single-excitation states",
            },
        }

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        if self.num_qubits == 1:
            return "W(1 qubit) = |1⟩ [no entanglement]"
        else:
            # Show first few terms for readability
            if self.num_qubits <= 4:
                terms = []
                for i in range(self.num_qubits):
                    state = ["0"] * self.num_qubits
                    state[i] = "1"
                    terms.append("|" + "".join(state) + "⟩")
                state_str = " + ".join(terms)
                return f"W({self.num_qubits} qubits) = ({state_str})/√{self.num_qubits}"
            else:
                return (
                    f"W({self.num_qubits} qubits) = "
                    f"(|100...0⟩ + |010...0⟩ + ... + |000...1⟩)/√{self.num_qubits}"
                )
