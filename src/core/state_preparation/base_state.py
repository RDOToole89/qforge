"""Base state preparation framework.

# Foundation of Quantum State Engineering
This module provides the abstract foundation for creating quantum states.
Each state class prepares a specific entanglement structure (global, symmetric,
graph-based, bipartite, or separable).

# Educational Purpose
Every state preparation class documents the quantum mechanics involved, so the
code can serve both as an experiment tool and a learning resource.

# Framework Integration
States created here feed into:
1. Noise models (applying decoherence channels to the prepared circuits)
2. Analysis metrics (quantifying the measured outcome distributions)
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, cast

import numpy as np
from qiskit import QuantumCircuit

logger = logging.getLogger(__name__)


class BaseState(ABC):
    """Abstract base class for quantum state preparation.

    # Quantum Computing Fundamentals
    A quantum state is a complete description of a quantum system. Each subclass
    prepares a specific entangled (or separable) state whose behavior under
    noise can then be simulated and measured.

    # Design Philosophy
    - Educational: Every method explains the quantum mechanics involved
    - Extensible: Easy to add new state types
    - Robust: Comprehensive validation with helpful error messages

    # State Types
    - GHZ: Global (all-or-nothing) multipartite entanglement
    - W: Symmetric single-excitation entanglement
    - Cluster: Graph states with nearest-neighbor entanglement
    - Bell: Maximally entangled two-qubit states

    Attributes:
        num_qubits (int): Number of qubits in the quantum state
        custom_params (Dict): State-specific parameters for customization
        experiment_id (str): Unique identifier for reproducibility
    """

    def __init__(
        self,
        num_qubits: int,
        custom_params: dict | None = None,
        experiment_id: str = "N/A",
        balance: str | None = None,
    ):
        """Initialize quantum state preparation.

        # Quantum System Size Considerations
        The number of qubits determines the Hilbert space dimension (2^n) and
        computational complexity:
        - 2-4 qubits: Small systems with clear theoretical predictions
        - 5-10 qubits: Intermediate complexity, still exactly simulable
        - 10+ qubits: Large systems, simulation cost grows exponentially

        Args:
            num_qubits: Number of qubits (determines entanglement complexity)
            custom_params: State-specific parameters (angles, topology, etc.)
            experiment_id: Unique identifier for experiment tracking
            balance: Optional circuit balancing strategy name.

        Raises:
            ValueError: If num_qubits is invalid for quantum computation
        """
        if num_qubits < 1:
            raise ValueError(
                f"Quantum states require at least 1 qubit. Got {num_qubits}. "
                f"Note: Single qubits have no entanglement; use 2+ qubits for "
                f"entangled states."
            )

        if num_qubits > 25:
            logger.warning(
                f"Large quantum system ({num_qubits} qubits) requires "
                f"2^{num_qubits} = {2**num_qubits:,} amplitudes. "
                f"Consider smaller systems for initial experiments."
            )

        self.num_qubits = num_qubits
        self.custom_params = custom_params or {}
        self.experiment_id = experiment_id
        self.balance = balance

        # Internal state tracking
        self._state_prepared = False
        self._circuit_cache = None

    @abstractmethod
    def create(self, add_barrier: bool = False) -> QuantumCircuit:
        """Create the quantum circuit that prepares this state.

        # Quantum Circuit Construction Principles
        A quantum circuit is a sequence of quantum gates that transforms the
        initial |00...0⟩ state into the desired entangled state. The circuit
        construction determines:
        - Which qubits become entangled
        - The correlation structure (topology)
        - Sensitivity to different types of noise

        # Framework Integration
        The prepared circuit is used in experiments where:
        1. State is prepared (this method)
        2. Noise is applied (noise models)
        3. Measurement outcomes are analyzed (analysis metrics)

        Args:
            add_barrier: Add barrier after preparation (cleaner visualization)

        Returns:
            QuantumCircuit: Circuit that prepares the desired quantum state

        Raises:
            NotImplementedError: Subclasses must implement their specific preparation
        """
        pass

    def get_theoretical_state_vector(self) -> np.ndarray:
        """Calculate the ideal state vector for educational and validation purposes.

        # Quantum State Mathematics
        The state vector |ψ⟩ is a complex vector in the 2^n dimensional Hilbert space
        representing all possible measurement outcomes and their amplitudes:
        |ψ⟩ = Σᵢ αᵢ|i⟩, where |αᵢ|² gives the probability of measuring state |i⟩

        # Uses
        - Validate circuit preparation against theoretical expectations
        - Calculate entanglement measures
        - Educational demonstrations of quantum superposition

        Returns:
            np.ndarray: Complex state vector of shape (2^n,)

        # Implementation Note
        Base class returns |00...0⟩. Subclasses override for specific states.
        """
        # Default: computational basis state |00...0⟩
        state_vector = np.zeros(2**self.num_qubits, dtype=complex)
        state_vector[0] = 1.0  # |00...0⟩ state

        logger.debug(f"Generated theoretical state vector for {self.num_qubits} qubits")
        return state_vector

    def get_basic_properties(self) -> dict[str, Any]:
        """Get basic quantum state properties for engine coordination.

        # State Properties for the Engine
        Provides essential information that the engine needs to coordinate
        with analysis modules, without mixing concerns.

        Returns:
            Dict with basic state properties for engine use
        """
        return {
            "state_class": self.__class__.__name__,
            "num_qubits": self.num_qubits,
            "hilbert_dimension": 2**self.num_qubits,
            "has_entanglement": self.num_qubits > 1,
            "custom_parameters": self.custom_params,
            "theoretical_state_available": True,
        }

    def validate_for_hardware(self, backend_constraints: dict[str, Any]) -> list[str]:
        """Check if this quantum state is suitable for given quantum hardware.

        # Hardware Compatibility Validation
        Real quantum computers have physical limitations that restrict which
        quantum states can be prepared. This method checks compatibility
        before attempting expensive circuit compilation and execution.

        # Common Hardware Constraints
        - Maximum qubit count (varies by quantum computer)
        - Gate connectivity (not all qubits can interact directly)
        - Gate fidelity (error rates for different gate types)
        - Coherence times (how long quantum states remain stable)

        Args:
            backend_constraints: Dictionary of hardware limitations
                - max_qubits: Maximum number of qubits supported
                - max_circuit_depth: Maximum gate sequence length
                - supported_gates: List of available quantum gates
                - connectivity: Qubit connection topology

        Returns:
            List[str]: Hardware compatibility warnings (empty if compatible)

        Example:
            >>> constraints = {"max_qubits": 5, "max_circuit_depth": 100}
            >>> warnings = state.validate_for_hardware(constraints)
            >>> if warnings:
            >>>     print("Hardware warnings:", warnings)
        """
        warnings = []

        # Check qubit count against hardware limits
        max_qubits = backend_constraints.get("max_qubits", 20)
        if self.num_qubits > max_qubits:
            warnings.append(
                f"State requires {self.num_qubits} qubits, hardware supports maximum {max_qubits}"
            )

        # Check circuit depth if constraint is provided
        max_depth = backend_constraints.get("max_circuit_depth")
        if max_depth is not None:
            # Estimate circuit depth (subclasses can override for better estimates)
            estimated_depth = self._estimate_circuit_depth()
            if estimated_depth > max_depth:
                warnings.append(
                    f"Estimated circuit depth {estimated_depth} exceeds hardware limit {max_depth}"
                )

        # Check for large systems that may have stability issues
        if self.num_qubits > 10:
            warnings.append(
                f"Large quantum system ({self.num_qubits} qubits) may be "
                f"sensitive to decoherence on current hardware"
            )

        # Check supported gates if constraint is provided
        supported_gates = backend_constraints.get("supported_gates")
        if supported_gates is not None:
            required_gates = self._get_required_gates()
            unsupported = set(required_gates) - set(supported_gates)
            if unsupported:
                warnings.append(f"State requires unsupported gates: {list(unsupported)}")

        return warnings

    def _estimate_circuit_depth(self) -> int:
        """Estimate the circuit depth for this quantum state.

        # Circuit Depth Estimation
        Provides rough estimate of quantum gate sequence length.
        Subclasses should override with state-specific calculations.

        Returns:
            int: Estimated number of gate layers (depth)
        """
        # Default conservative estimate: O(n) for n-qubit entangling state
        return max(1, self.num_qubits)

    def _get_required_gates(self) -> list[str]:
        """Get list of quantum gates required for this state preparation.

        # Gate Requirements
        Different quantum states require different sets of quantum gates.
        Subclasses should override with specific gate requirements.

        Returns:
            List[str]: Required quantum gate names
        """
        # Default: assume basic gate set (most states use these)
        return ["h", "cx"]  # Hadamard and CNOT gates

    # ========================================================================
    # PHASE 1: SAFE ABSTRACTION HELPERS (No Behavior Changes)
    # ========================================================================

    def _simulate_circuit_state_vector(self, circuit: QuantumCircuit) -> np.ndarray:
        """Common state vector simulation helper for states that need circuit simulation.

        # Safe Abstraction Pattern
        This helper eliminates duplicated AerSimulator boilerplate found in
        ClusterState and CustomState without changing their behavior. States
        with analytical formulas (GHZ, Bell, W) continue using their efficient
        direct calculations.

        # Computational Safety
        - Validates system size before expensive simulation
        - Provides consistent error handling across all states
        - Generates normalized fallback states when simulation fails

        Args:
            circuit: Quantum circuit to simulate

        Returns:
            np.ndarray: State vector from simulation or normalized fallback

        Note:
            Only used by states that require circuit simulation for state vector
            calculation. States with analytical formulas should use direct math.
        """
        # Validate system size before expensive simulation
        if circuit.num_qubits > 20:
            raise ValueError(
                f"Circuit simulation for {circuit.num_qubits} qubits "
                f"requires 2^{circuit.num_qubits} = {2**circuit.num_qubits:,} amplitudes. "
                f"This exceeds practical simulation limits."
            )

        try:
            # Import here to avoid circular dependencies
            from qiskit_aer import AerSimulator

            # Prepare circuit for simulation
            sim_circuit = circuit.copy()
            sim_circuit.save_statevector()

            # Run simulation
            simulator = AerSimulator(method="statevector")
            job = simulator.run(sim_circuit, shots=1)
            result = job.result()
            statevector = result.get_statevector()

            return cast(np.ndarray, statevector.data)

        except Exception as e:
            # Use helper for consistent fallback behavior
            logger.warning(
                f"Circuit simulation failed for {circuit.num_qubits}-qubit state: {e}. "
                f"Using normalized random fallback state."
            )
            return self._generate_fallback_state(circuit.num_qubits)

    def _validate_large_system(self, operation: str, threshold: int = 10) -> None:
        """Validate system size for computationally expensive operations.

        # Safe Abstraction Pattern
        Provides consistent size validation across all states that perform
        expensive operations like state vector calculation or circuit simulation.

        # Educational Value
        Teaches users about computational complexity of quantum systems and
        provides clear guidance about practical limitations.

        Args:
            operation: Description of the operation being attempted
            threshold: Qubit count threshold for warnings (default: 10)

        Raises:
            ValueError: If system exceeds hard computational limits (>15 qubits)

        Note:
            Threshold can be adjusted per operation. Some states may override
            this for their specific computational requirements.
        """
        if self.num_qubits > threshold:
            warning_msg = (
                f"{operation} for {self.num_qubits} qubits "
                f"requires 2^{self.num_qubits} = {2**self.num_qubits:,} amplitudes. "
                f"Consider using circuit simulation instead for n > {threshold}."
            )

            # Hard limit to prevent memory exhaustion
            if self.num_qubits > 15:
                raise ValueError(warning_msg)
            else:
                logger.warning(warning_msg)

    def _generate_fallback_state(self, num_qubits: int) -> np.ndarray:
        """Generate normalized random fallback state for failed simulations.

        # Safe Abstraction Pattern
        Provides consistent fallback behavior when circuit simulation fails.
        Used by simulation helper to maintain consistent error handling.

        # Mathematical Properties
        - Properly normalized: ||ψ|| = 1
        - Random phases and amplitudes
        - Correct Hilbert space dimension (2^n)

        Args:
            num_qubits: Number of qubits for the fallback state

        Returns:
            np.ndarray: Normalized complex state vector

        Note:
            This is a last resort when simulation fails. The random state
            won't match theoretical expectations but allows code to continue
            executing for debugging purposes.
        """
        # Generate random complex amplitudes
        real_parts = np.random.random(2**num_qubits)
        imag_parts = np.random.random(2**num_qubits)
        state = real_parts + 1j * imag_parts

        # Normalize to unit vector
        return cast(np.ndarray, state / np.linalg.norm(state))

    def _apply_gate_count_balancing(self, circuit: QuantumCircuit) -> QuantumCircuit:
        """Pad qubits with identity gates so all qubits have equal gate count.

        Under per-gate depolarizing noise, qubits with more gates accumulate
        more noise. Padding with identity gates equalizes the noise budget
        so that observed asymmetries are due to state structure, not circuit
        depth imbalance.

        Args:
            circuit: Circuit to balance (modified in-place and returned)

        Returns:
            The same circuit with identity-gate padding applied.
        """
        gate_counts: dict[int, int] = {i: 0 for i in range(circuit.num_qubits)}

        for instruction in circuit.data:
            op = instruction.operation
            if op.name in ("barrier", "measure"):
                continue
            for qubit in instruction.qubits:
                idx = circuit.qubits.index(qubit)
                gate_counts[idx] += 1

        max_count = max(gate_counts.values()) if gate_counts else 0
        padding: dict[int, int] = {}

        for q, count in gate_counts.items():
            deficit = max_count - count
            if deficit > 0:
                for _ in range(deficit):
                    circuit.id(q)
                padding[q] = deficit

        circuit.metadata = circuit.metadata or {}
        circuit.metadata["padding_per_qubit"] = padding
        circuit.metadata["balanced"] = True

        logger.debug(f"Gate-count balancing: max={max_count}, padding={padding}")
        return circuit

    def get_experiment_metadata(self) -> dict[str, Any]:
        """Generate metadata describing this state preparation.

        Metadata lets experiments be reproduced and results attributed to
        specific state preparations and parameter choices.

        Returns:
            Dict with basic metadata about the prepared state.
        """
        return {
            "state_class": self.__class__.__name__,
            "num_qubits": self.num_qubits,
            "custom_parameters": self.custom_params,
            "experiment_id": self.experiment_id,
            "hilbert_space_dimension": 2**self.num_qubits,
            "theoretical_state_computed": True,
        }

    def log_state_creation(self, state_type: str, extra_info: dict | None = None) -> None:
        """Log quantum state creation with educational context.

        # Documentation
        Comprehensive logging enables:
        - Experiment reproducibility
        - Educational step-by-step explanations
        - Metadata collection

        Args:
            state_type: Human-readable state description
            extra_info: Additional technical details
        """
        base_info = {
            "state_type": state_type,
            "num_qubits": self.num_qubits,
            "hilbert_dimension": 2**self.num_qubits,
            "entanglement_expected": self.num_qubits > 1,
        }

        if extra_info:
            base_info.update(extra_info)

        logger.info(
            f"Prepared {state_type} state: {self.num_qubits} qubits "
            f"(experiment: {self.experiment_id})"
        )
        logger.debug(f"State preparation details: {base_info}")

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        return (
            f"{self.__class__.__name__}(num_qubits={self.num_qubits}, params={self.custom_params})"
        )

    def __repr__(self) -> str:
        """Technical representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"num_qubits={self.num_qubits}, "
            f"custom_params={self.custom_params}, "
            f"experiment_id='{self.experiment_id}')"
        )
