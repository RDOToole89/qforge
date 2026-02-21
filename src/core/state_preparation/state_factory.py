"""
Quantum State Factory for Research-Grade Decoherence Experiments

# State Preparation Factory
Centralized factory for creating quantum states used in structured decoherence
pathway research. Provides clean interface between engine and state classes
while maintaining separation of concerns.

# Educational Purpose
This factory demonstrates the Factory Pattern in quantum computing applications,
showing how to manage different quantum state types systematically while
keeping the interface simple and extensible.
"""

import logging
from typing import Optional

from qiskit import QuantumCircuit

from .base_state import BaseState
from .state_constants import STATE_CLASSES

logger = logging.getLogger("QuantumExperiment.StatePreparation")


def prepare_state(
    state_type: str,
    num_qubits: int,
    custom_params: Optional[dict] = None,
    add_barrier: bool = False,
    experiment_id: str = "N/A",
    balance: Optional[str] = None,
) -> QuantumCircuit:
    """
    Factory function to prepare quantum states for decoherence research.

    # Quantum State Factory Pattern
    Creates specific quantum states (GHZ, W, Bell, Cluster, etc.) using a unified
    interface. Each state type implements different entanglement topologies for
    studying how decoherence pathways depend on quantum correlation structure.

    # Research Applications
    - GHZ states: Global entanglement → pathway propagation studies
    - W states: Symmetric entanglement → asymmetric pathway emergence
    - Bell states: Two-qubit entanglement → fundamental pathway structures
    - Cluster states: Local correlations → network decoherence patterns

    Args:
        state_type: Type of quantum state to create
        num_qubits: Number of qubits (determines complexity)
        custom_params: State-specific parameters (angles, topology, etc.)
        add_barrier: Add quantum barrier for circuit visualization
        experiment_id: Unique identifier for experiment tracking

    Returns:
        QuantumCircuit: Prepared quantum circuit ready for noise application

    Raises:
        ValueError: If state_type is invalid or parameters are incompatible

    Example:
        >>> circuit = prepare_state("GHZ", 3)  # 3-qubit GHZ state
        >>> circuit = prepare_state("W", 4, custom_params={"symmetric": True})
    """
    # Validate state type
    if state_type not in STATE_CLASSES:
        available_states = list(STATE_CLASSES.keys())
        raise ValueError(
            f"Invalid state type: '{state_type}'. Available states: {available_states}"
        )

    try:
        # Create state instance
        state_class = STATE_CLASSES[state_type]
        state = state_class(
            num_qubits=num_qubits, custom_params=custom_params, experiment_id=experiment_id,
            balance=balance,
        )

        # Generate quantum circuit
        circuit = state.create(add_barrier=add_barrier)

        # Log successful creation
        logger.info(
            f"Created {state_type} state: {num_qubits} qubits (experiment: {experiment_id})"
        )
        logger.debug(f"State details: {state_type}, qubits={num_qubits}, params={custom_params}")

        return circuit

    except Exception as e:
        logger.error(
            f"State preparation failed: {state_type} with {num_qubits} qubits - {e} "
            f"(experiment: {experiment_id})"
        )
        raise ValueError(f"Failed to create {state_type} state: {e}") from e


def create_state_instance(
    state_type: str,
    num_qubits: int,
    custom_params: Optional[dict] = None,
    experiment_id: str = "N/A",
) -> BaseState:
    """
    Create a state instance without generating the circuit.

    # State Instance Factory
    Useful for analysis modules that need access to state properties
    and theoretical calculations without circuit generation.

    Args:
        state_type: Type of quantum state
        num_qubits: Number of qubits
        custom_params: State-specific parameters
        experiment_id: Experiment identifier

    Returns:
        BaseState: State instance for property access and analysis

    Example:
        >>> state = create_state_instance("GHZ", 3)
        >>> properties = state.get_basic_properties()
        >>> theory_vector = state.get_theoretical_state_vector()
    """
    if state_type not in STATE_CLASSES:
        available_states = list(STATE_CLASSES.keys())
        raise ValueError(
            f"Invalid state type: '{state_type}'. Available states: {available_states}"
        )

    state_class = STATE_CLASSES[state_type]
    return state_class(
        num_qubits=num_qubits, custom_params=custom_params, experiment_id=experiment_id
    )


def get_available_states() -> list[str]:
    """
    Get list of all available quantum state types.

    Returns:
        List[str]: Available state types for factory creation
    """
    return list(STATE_CLASSES.keys())


def prepare_state_for_hardware(
    state_type: str,
    num_qubits: int,
    backend=None,
    custom_params: Optional[dict] = None,
    add_barrier: bool = False,
    experiment_id: str = "N/A",
) -> QuantumCircuit:
    """
    Prepare quantum state with hardware validation for real quantum devices.

    # Hardware-Aware State Preparation
    This enhanced factory function validates state compatibility with real quantum
    hardware before circuit preparation, providing early feedback about device
    limitations and suggesting alternatives when needed.

    # Real Device Considerations
    - Qubit connectivity constraints
    - Gate set limitations
    - Circuit depth limitations
    - Measurement constraints
    - Noise model compatibility

    Args:
        state_type: Type of quantum state to create
        num_qubits: Number of qubits (must match backend constraints)
        backend: Qiskit backend object or None for simulation
        custom_params: State-specific parameters
        add_barrier: Add quantum barrier for visualization
        experiment_id: Unique identifier for experiment tracking

    Returns:
        QuantumCircuit: Hardware-validated quantum circuit

    Raises:
        ValueError: If state is incompatible with hardware constraints

    Example:
        >>> # For real quantum device
        >>> from qiskit import IBMQ
        >>> provider = IBMQ.load_account()
        >>> backend = provider.get_backend('ibmq_manila')
        >>> circuit = prepare_state_for_hardware(
        ...     'GHZ', 3, backend=backend
        ... )

        >>> # For simulation (no validation)
        >>> circuit = prepare_state_for_hardware('GHZ', 3)
    """
    # Create state instance for validation
    state = create_state_instance(state_type, num_qubits, custom_params, experiment_id)

    # Perform hardware validation if backend provided
    if backend is not None:
        try:
            # Extract backend constraints
            backend_config = backend.configuration()
            backend_constraints = {
                "max_qubits": backend_config.n_qubits,
                "gate_set": set(backend_config.basis_gates)
                if hasattr(backend_config, "basis_gates")
                else set(),
                "coupling_map": getattr(backend_config, "coupling_map", None),
                "max_shots": getattr(backend_config, "max_shots", 8192),
                "backend_name": backend_config.backend_name,
            }

            # Validate state compatibility with hardware
            hardware_warnings = state.validate_for_hardware(backend_constraints)

            if hardware_warnings:
                warning_msg = (
                    f"Hardware compatibility issues for {state_type} state "
                    f"on {backend_constraints['backend_name']}:\\n"
                    + "\\n".join(f"  - {warning}" for warning in hardware_warnings)
                )
                logger.warning(warning_msg)

                # For critical issues, raise error
                critical_keywords = ["unsupported", "exceeds", "incompatible", "requires"]
                if any(
                    keyword in warning.lower()
                    for warning in hardware_warnings
                    for keyword in critical_keywords
                ):
                    raise ValueError(
                        f"State {state_type} is incompatible with backend {backend_constraints['backend_name']}. "
                        f"Issues: {hardware_warnings}"
                    )

            logger.info(
                f"Hardware validation passed for {state_type} state "
                f"on {backend_constraints['backend_name']} "
                f"({num_qubits}/{backend_constraints['max_qubits']} qubits used)"
            )

        except Exception as e:
            logger.error(f"Hardware validation failed: {e}")
            raise ValueError(f"Cannot validate hardware compatibility: {e}") from e

    # Prepare the actual circuit
    return prepare_state(state_type, num_qubits, custom_params, add_barrier, experiment_id)


def validate_state_request(
    state_type: str, num_qubits: int, custom_params: Optional[dict] = None
) -> list[str]:
    """
    Validate state creation request before attempting preparation.

    # Pre-flight Validation
    Catches common errors before expensive quantum circuit creation,
    providing educational feedback about quantum computing constraints.

    Args:
        state_type: Requested state type
        num_qubits: Number of qubits
        custom_params: Custom parameters

    Returns:
        List[str]: List of validation warnings (empty if valid)

    Example:
        >>> warnings = validate_state_request("GHZ", 25)
        >>> if warnings:
        >>>     print("Warnings:", warnings)
    """
    warnings = []

    # Check state type
    if state_type not in STATE_CLASSES:
        warnings.append(f"Unknown state type: {state_type}")
        return warnings

    # Check qubit count
    if num_qubits < 1:
        warnings.append("Quantum states require at least 1 qubit")
    elif num_qubits > 20:
        warnings.append(
            f"Large quantum system ({num_qubits} qubits) requires "
            f"2^{num_qubits} = {2**num_qubits:,} amplitudes - "
            f"consider smaller systems for experiments"
        )

    # State-specific validations
    if state_type in ["BELL"] and num_qubits != 2:
        warnings.append("Bell states require exactly 2 qubits")
    elif state_type in ["GHZ", "W"] and num_qubits < 2:
        warnings.append(f"{state_type} states require at least 2 qubits for entanglement")

    return warnings
