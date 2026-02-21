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
from qiskit import QuantumCircuit, transpile as _qk_transpile
from qiskit.circuit.library import UnitaryGate

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

        Uses an efficient gate-based construction via cascaded Givens rotations
        in the {|01⟩, |10⟩} subspace. This produces O(n) two-qubit gates,
        ensuring the circuit has explicit entangling gates that noise models
        can act on (unlike the monolithic ``initialize`` instruction).

        Args:
            add_barrier: Add quantum barrier for circuit visualization

        Returns:
            QuantumCircuit: Circuit that prepares |W_n⟩ state

        Example:
            >>> w = WState(3)
            >>> circuit = w.create()
            >>> # Creates (|100⟩ + |010⟩ + |001⟩)/√3
        """
        if self.num_qubits < 1:
            raise ValueError("W state requires at least 1 qubit")

        circuit = QuantumCircuit(self.num_qubits)

        if self.num_qubits == 1:
            circuit.x(0)
            self.log_state_creation(
                "W (single qubit)", {"note": "W state with 1 qubit is just |1⟩"}
            )
            if add_barrier:
                circuit.barrier()
            return circuit

        # Givens rotation cascade: spread one excitation across all qubits
        # Start with excitation on the last qubit
        circuit.x(self.num_qubits - 1)

        for k in range(self.num_qubits - 1, 0, -1):
            # Givens rotation G(θ) in {|01⟩, |10⟩} subspace of (q_{k-1}, q_k):
            #   |10⟩ → cos(θ)|10⟩ + sin(θ)|01⟩
            # with cos²(θ) = 1/(k+1) so each qubit ends up with amplitude 1/√n
            theta = np.arccos(np.sqrt(1.0 / (k + 1)))
            circuit.append(self._givens_gate(theta), [k - 1, k])

        # Decompose UnitaryGate instructions to standard basis gates
        # so that noise models can attach errors to each gate.
        circuit = _qk_transpile(
            circuit, basis_gates=["cx", "rz", "sx", "x"], optimization_level=1
        )

        # Gate-count balancing (equalize noise exposure across qubits)
        if self.balance == "gate_count":
            circuit = self._apply_gate_count_balancing(circuit)

        if add_barrier:
            circuit.barrier()

        self.log_state_creation(
            f"W ({self.num_qubits} qubits)",
            {
                "entanglement_type": "symmetric_multipartite",
                "construction_method": "givens_cascade",
                "excitation_number": 1,
                "two_qubit_gates": self.num_qubits - 1,
                "symmetry_class": "permutation_symmetric",
                "robustness": "partially_robust_to_qubit_loss",
            },
        )

        return circuit

    @staticmethod
    def _givens_gate(theta: float) -> UnitaryGate:
        """Givens rotation in the {|01⟩, |10⟩} subspace.

        Matrix (basis order |00⟩, |01⟩, |10⟩, |11⟩)::

            [[1,    0,       0,    0],
             [0,  cos θ,   sin θ,  0],
             [0, -sin θ,   cos θ,  0],
             [0,    0,       0,    1]]
        """
        c, s = np.cos(theta), np.sin(theta)
        U = np.eye(4, dtype=complex)
        U[1, 1] = c
        U[1, 2] = s
        U[2, 1] = -s
        U[2, 2] = c
        return UnitaryGate(U, label="Givens")

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

        Uses n-1 Givens rotations, each decomposing to ~2 CX + single-qubit gates.

        Returns:
            int: Estimated circuit depth
        """
        if self.num_qubits == 1:
            return 1
        return 2 * (self.num_qubits - 1)  # ~2 layers per Givens rotation

    def _get_required_gates(self) -> list[str]:
        """
        Get quantum gates required for W state preparation.

        Returns:
            List[str]: Required gate names
        """
        if self.num_qubits == 1:
            return ["x"]
        return ["x", "cx", "rz", "sx"]  # Givens rotations decompose to these

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
