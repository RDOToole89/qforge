"""
GHZ State Preparation for Decoherence Pathway Research

# The Greenberger-Horne-Zeilinger (GHZ) State
The GHZ state represents maximal multipartite entanglement where all qubits
are globally correlated: |GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2

# Physical Significance
GHZ states exhibit the strongest possible quantum correlations for n qubits,
making them ideal for studying how global entanglement affects decoherence
pathway structure. Unlike Bell states (2-qubit) or W states (symmetric),
GHZ states show all-or-nothing correlations.

# Research Applications in Structured Decoherence
- Pathway propagation: How does decoherence spread through global entanglement?
- Measurement correlations: Which computational basis states remain correlated under noise?
- Entanglement robustness: How quickly does global entanglement decay?
- Symmetry breaking: Does noise break the |000⟩ ↔ |111⟩ symmetry?
"""

from typing import Any

import numpy as np
from qiskit import QuantumCircuit

from .base_state import BaseState


class GHZState(BaseState):
    """
    GHZ state preparation for quantum decoherence research.

    # Quantum State Definition
    |GHZ_n⟩ = (|00...0⟩ + |11...1⟩)/√2

    This creates maximal multipartite entanglement where measuring any qubit
    immediately determines all others. Perfect correlations make GHZ states
    sensitive to decoherence but also excellent for studying pathway structure.

    # Circuit Construction
    The standard GHZ preparation uses:
    1. Hadamard gate on first qubit: creates superposition
    2. Chain of CNOT gates: propagates entanglement to all qubits
    3. Result: Global entanglement with perfect computational basis correlations

    # Educational Notes
    - 2-qubit GHZ = Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
    - 3+ qubits: Genuine multipartite entanglement (cannot be factored)
    - Measurement outcomes: Only |00...0⟩ and |11...1⟩ have non-zero amplitudes
    """

    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        """
        Create quantum circuit that prepares the GHZ state.

        # Circuit Construction Steps
        1. Start with computational basis: |00...0⟩
        2. Apply Hadamard to qubit 0: (|0⟩ + |1⟩)|00...0⟩/√2
        3. Apply CNOT chain: propagates entanglement through all qubits
        4. Final state: (|00...0⟩ + |11...1⟩)/√2

        # Gate Sequence Analysis
        - Hadamard: Creates initial superposition
        - CNOT(0,1): Entangles qubits 0 and 1
        - CNOT(1,2): Extends entanglement to qubit 2
        - ... continue for all qubits
        - Depth: O(n) where n = number of qubits

        Args:
            add_barrier: Add quantum barrier for cleaner circuit visualization

        Returns:
            QuantumCircuit: Circuit that prepares |GHZ_n⟩ state

        Example:
            >>> ghz = GHZState(3)
            >>> circuit = ghz.create()
            >>> print(circuit)  # Shows H on qubit 0, CNOTs connecting all
        """
        # Validate qubit count for GHZ state
        if self.num_qubits < 1:
            raise ValueError("GHZ state requires at least 1 qubit")

        # Create quantum circuit
        circuit = QuantumCircuit(self.num_qubits)

        # Single qubit case: just |0⟩ state (no entanglement possible)
        if self.num_qubits == 1:
            # No gates needed, |0⟩ is already the ground state
            self.log_state_creation("GHZ (single qubit)", {"note": "No entanglement with 1 qubit"})
            return circuit

        # Multi-qubit GHZ preparation
        # Step 1: Create superposition on first qubit
        circuit.h(0)  # |0⟩ → (|0⟩ + |1⟩)/√2

        # Step 2: Propagate entanglement through CNOT chain
        for i in range(self.num_qubits - 1):
            circuit.cx(i, i + 1)  # Controlled-X from qubit i to i+1

        # Balance gate counts across qubits if requested
        if self.balance == "gate_count":
            circuit = self._apply_gate_count_balancing(circuit)

        # Optional: Add barrier for visualization
        if add_barrier:
            circuit.barrier()

        # Log successful creation
        self.log_state_creation(
            f"GHZ ({self.num_qubits} qubits)",
            {
                "entanglement_type": "maximal_multipartite",
                "circuit_depth": self.num_qubits,  # H + (n-1) CNOTs
                "measurement_outcomes": ["0" * self.num_qubits, "1" * self.num_qubits],
                "symmetry": "computational_basis_symmetric",
            },
        )

        return circuit

    def get_theoretical_state_vector(self) -> np.ndarray:
        """
        Calculate the theoretical GHZ state vector for validation.

        # Mathematical Definition
        |GHZ_n⟩ = (|00...0⟩ + |11...1⟩)/√2

        In computational basis representation:
        - All-zeros state |00...0⟩ has amplitude 1/√2
        - All-ones state |11...1⟩ has amplitude 1/√2
        - All other basis states have amplitude 0

        Returns:
            np.ndarray: Complex state vector of shape (2^n,)

        Example:
            >>> ghz = GHZState(3)
            >>> state = ghz.get_theoretical_state_vector()
            >>> print(state)  # [1/√2, 0, 0, 0, 0, 0, 0, 1/√2]
        """
        # Create zero vector for all 2^n computational basis states
        state_vector = np.zeros(2**self.num_qubits, dtype=complex)

        if self.num_qubits == 1:
            # Single qubit: just |0⟩ state
            state_vector[0] = 1.0
        else:
            # Multi-qubit GHZ: (|00...0⟩ + |11...1⟩)/√2
            amplitude = 1.0 / np.sqrt(2)
            state_vector[0] = amplitude  # |00...0⟩ state (index 0)
            state_vector[-1] = amplitude  # |11...1⟩ state (index 2^n - 1)

        return state_vector

    def _estimate_circuit_depth(self) -> int:
        """
        Estimate circuit depth for GHZ state preparation.

        # Depth Analysis
        GHZ preparation requires:
        - 1 Hadamard gate (depth 1)
        - (n-1) sequential CNOT gates (depth n-1)
        - Total depth: n gates in sequence

        Returns:
            int: Circuit depth for this GHZ state
        """
        return max(1, self.num_qubits)  # H + (n-1) CNOTs = n total depth

    def _get_required_gates(self) -> list[str]:
        """
        Get quantum gates required for GHZ state preparation.

        # Gate Requirements
        GHZ states use the minimal universal gate set:
        - Hadamard (H): Creates superposition
        - CNOT (CX): Creates entanglement

        Returns:
            List[str]: Required gate names
        """
        if self.num_qubits == 1:
            return []  # Single qubit needs no gates
        else:
            return ["h", "cx"]  # Hadamard and CNOT

    def get_theoretical_properties(self) -> dict[str, Any]:
        """
        Get theoretical quantum properties specific to GHZ states.

        # GHZ State Properties
        These properties are useful for analysis modules and educational
        demonstrations of multipartite entanglement characteristics.

        Returns:
            Dict with GHZ-specific theoretical properties
        """
        if self.num_qubits == 1:
            return {
                "entanglement_type": "none",
                "max_violation_mermin": 1.0,  # No violation possible
                "schmidt_rank": 1,
                "correlation_strength": "classical",
            }

        return {
            "entanglement_type": "maximal_multipartite",
            "measurement_probabilities": {"all_zeros": 0.5, "all_ones": 0.5, "mixed_outcomes": 0.0},
            "correlation_strength": "maximal",
            "bell_inequality_violation": "maximal" if self.num_qubits == 2 else "n/a",
            "mermin_inequality_violation": 2 ** (self.num_qubits / 2)
            if self.num_qubits > 2
            else "n/a",
            "schmidt_rank": 2,  # Only 2 non-zero eigenvalues
            "robustness_to_decoherence": "fragile",
            "decoherence_sensitivity": "all_qubits_equally_critical",
        }

    def get_research_context(self) -> dict[str, Any]:
        """
        Get research context for structured decoherence pathway studies.

        # Research Significance
        GHZ states are particularly valuable for pathway research because:
        1. Clear binary outcomes make pathway tracking easier
        2. Global entanglement tests pathway propagation mechanisms
        3. Symmetry properties reveal pathway structure

        Returns:
            Dict with research context and experimental predictions
        """
        return {
            "pathway_hypothesis": {
                "prediction": "Global entanglement → synchronized decoherence pathways",
                "test_method": "Monitor correlation between |000⟩ and |111⟩ populations",
                "expected_signature": "Correlated decay of both amplitudes",
            },
            "decoherence_pattern": {
                "early_stage": "Slight amplitude reduction, coherence preserved",
                "intermediate": "Asymmetric decay, mixed state emergence",
                "late_stage": "Approach to maximally mixed state",
            },
            "research_metrics": {
                "primary": ["AI (Asymmetry Index)", "PCR (Pathway Concentration Ratio)"],
                "secondary": [
                    "EEC (Entanglement-Error Correlation)",
                    "TPS (Temporal Pathway Stability)",
                ],
            },
            "control_comparisons": {
                "vs_product_states": "Should show structured vs random decoherence",
                "vs_w_states": "Different pathway topology effects",
                "vs_bell_states": "Scaling behavior with system size",
            },
        }

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        if self.num_qubits == 1:
            return "GHZ(1 qubit) = |0⟩ [no entanglement]"
        else:
            return f"GHZ({self.num_qubits} qubits) = (|{'0' * self.num_qubits}⟩ + |{'1' * self.num_qubits}⟩)/√2"
