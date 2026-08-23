"""Quantum noise model factory.

# Noise Model Factory
Centralized factory for creating quantum decoherence channels. Provides a
clean interface between the engine and the noise classes while maintaining
separation of concerns and physics compliance.

# Educational Purpose
This factory demonstrates the Factory Pattern in quantum decoherence applications,
showing how to manage different environmental coupling mechanisms systematically
while keeping the interface simple and extensible.
"""

from __future__ import annotations

import logging
from typing import Any

from qiskit_aer.noise import NoiseModel

from .amplitude_damping import AmplitudeDampingNoise
from .base_noise import BaseNoise
from .bit_flip import BitFlipNoise
from .correlated_depolarizing import CorrelatedDepolarizingNoise
from .depolarizing import DepolarizingNoise
from .phase_damping import PhaseDampingNoise
from .phase_flip import PhaseFlipNoise
from .thermal_relaxation import ThermalRelaxationNoise

logger = logging.getLogger(__name__)

# Noise registry for available noise models
NOISE_CLASSES: dict[str, type[BaseNoise]] = {
    "DEPOLARIZING": DepolarizingNoise,
    "AMPLITUDE_DAMPING": AmplitudeDampingNoise,
    "PHASE_DAMPING": PhaseDampingNoise,
    "BIT_FLIP": BitFlipNoise,
    "PHASE_FLIP": PhaseFlipNoise,
    "THERMAL_RELAXATION": ThermalRelaxationNoise,
    "CORRELATED_DEPOLARIZING": CorrelatedDepolarizingNoise,
}


def create_noise_model(
    noise_type: str,
    num_qubits: int,
    error_rate: float | None = None,
    custom_params: dict | None = None,
    experiment_id: str = "N/A",
    readout_error_rate: float | None = None,
) -> NoiseModel:
    """Factory function to create noise models.

    # Quantum Noise Factory Pattern
    Creates specific decoherence channels using a unified interface. Each
    noise type implements a different environmental coupling mechanism:
    - Depolarizing noise: Random Pauli errors (isotropic decoherence)
    - Amplitude damping: T1 energy relaxation
    - Phase damping: Pure dephasing (T2* coherence loss)
    - Thermal relaxation: Combined T1/T2 processes at finite temperature

    Args:
        noise_type: Type of decoherence channel to create
        num_qubits: Number of qubits (determines system complexity)
        error_rate: Phenomenological error probability [0, 1]
        custom_params: Noise-specific parameters (T1, T2, temperature, etc.)
        experiment_id: Unique identifier for experiment tracking
        readout_error_rate: Optional measurement readout error probability.

    Returns:
        NoiseModel: Configured quantum decoherence channel

    Raises:
        ValueError: If noise_type is invalid or parameters violate physics constraints

    Example:
        >>> # Basic depolarizing noise
        >>> noise_model = create_noise_model("DEPOLARIZING", 3, error_rate=0.01)

        >>> # Physics-based thermal relaxation
        >>> noise_model = create_noise_model(
        ...     "THERMAL_RELAXATION", 2,
        ...     custom_params={"t1": 100e-6, "t2": 80e-6, "temperature": 0.015}
        ... )
    """
    # Validate noise type
    if noise_type not in NOISE_CLASSES:
        available_noise = list(NOISE_CLASSES.keys())
        raise ValueError(
            f"Invalid noise type: '{noise_type}'. Available noise models: {available_noise}"
        )

    try:
        # Create noise instance with physics validation
        noise_class = NOISE_CLASSES[noise_type]

        # Prepare parameters for noise creation
        init_params: dict[str, Any] = {"num_qubits": num_qubits, "experiment_id": experiment_id}

        # Add error rate if provided
        if error_rate is not None:
            init_params["error_rate"] = error_rate

        # Add custom physics parameters
        if custom_params:
            init_params.update(custom_params)

        # Create noise instance with comprehensive validation
        noise = noise_class(**init_params)

        # Create Qiskit noise model
        noise_model = NoiseModel()

        # Apply noise to appropriate gates based on noise type characteristics
        gate_list = _get_appropriate_gates(noise_type, num_qubits)
        noise.apply(noise_model, gate_list)

        # Apply readout errors if requested
        if readout_error_rate is not None and readout_error_rate > 0:
            _apply_readout_errors(noise_model, num_qubits, readout_error_rate)

        # Log successful creation
        logger.info(
            f"Created {noise_type} noise model: {num_qubits} qubits, "
            f"error_rate={noise.error_rate:.4f} (experiment: {experiment_id})"
        )
        logger.debug(f"Noise details: {noise_type}, qubits={num_qubits}, params={custom_params}")

        return noise_model

    except Exception as e:
        logger.error(
            f"Noise model creation failed: {noise_type} with {num_qubits} qubits - {e} "
            f"(experiment: {experiment_id})"
        )
        raise ValueError(f"Failed to create {noise_type} noise model: {e}") from e


def create_noise_instance(
    noise_type: str,
    num_qubits: int,
    error_rate: float | None = None,
    custom_params: dict | None = None,
    experiment_id: str = "N/A",
) -> BaseNoise:
    """Create a noise instance without generating the full noise model.

    # Noise Instance Factory
    Useful for analysis modules that need access to noise properties
    and theoretical calculations without full noise model construction.
    Mirrors state preparation's create_state_instance() for consistency.

    Args:
        noise_type: Type of decoherence channel
        num_qubits: Number of qubits
        error_rate: Phenomenological error probability
        custom_params: Physics parameters (T1, T2, etc.)
        experiment_id: Experiment identifier

    Returns:
        BaseNoise: Noise instance for property access and analysis

    Example:
        >>> noise = create_noise_instance("DEPOLARIZING", 3, error_rate=0.01)
        >>> properties = noise.get_basic_properties()
        >>> physics = noise.get_physics_description()
        >>> kraus_ops = noise.get_kraus_operators()
    """
    if noise_type not in NOISE_CLASSES:
        available_noise = list(NOISE_CLASSES.keys())
        raise ValueError(
            f"Invalid noise type: '{noise_type}'. Available noise models: {available_noise}"
        )

    noise_class = NOISE_CLASSES[noise_type]

    # Prepare parameters
    init_params: dict[str, Any] = {"num_qubits": num_qubits, "experiment_id": experiment_id}

    if error_rate is not None:
        init_params["error_rate"] = error_rate

    if custom_params:
        init_params.update(custom_params)

    return noise_class(**init_params)


def get_available_noise_types() -> list[str]:
    """Get list of all available quantum noise types.

    Returns:
        List[str]: Available noise types for factory creation
    """
    return list(NOISE_CLASSES.keys())


def create_noise_model_for_hardware(
    noise_type: str,
    num_qubits: int,
    backend: Any = None,
    error_rate: float | None = None,
    custom_params: dict | None = None,
    experiment_id: str = "N/A",
) -> NoiseModel:
    """Create noise model with hardware validation for real quantum devices.

    # Hardware-Aware Noise Creation
    This enhanced factory function validates noise compatibility with real quantum
    hardware before model creation, providing early feedback about device
    limitations and suggesting alternatives when needed.

    # Real Device Considerations for Noise Models
    - Coherence time constraints (T1/T2 limitations)
    - Gate set limitations and error rate bounds
    - Temperature and environmental constraints
    - Coupling topology restrictions
    - Measurement and control system noise

    Args:
        noise_type: Type of decoherence channel to create
        num_qubits: Number of qubits (must match backend constraints)
        backend: Qiskit backend object or None for simulation
        error_rate: Phenomenological error probability
        custom_params: Physics parameters (T1, T2, temperature, etc.)
        experiment_id: Unique identifier for experiment tracking

    Returns:
        NoiseModel: Hardware-validated quantum decoherence channel

    Raises:
        ValueError: If noise model is incompatible with hardware constraints

    Example:
        >>> # For real quantum device
        >>> from qiskit import IBMQ
        >>> provider = IBMQ.load_account()
        >>> backend = provider.get_backend('ibmq_manila')
        >>> noise_model = create_noise_model_for_hardware(
        ...     'THERMAL_RELAXATION', 3, backend=backend,
        ...     custom_params={'t1': 100e-6, 't2': 80e-6}
        ... )

        >>> # For simulation (no validation)
        >>> noise_model = create_noise_model_for_hardware(
        ...     'DEPOLARIZING', 3, error_rate=0.01
        ... )
    """
    # Create noise instance for validation
    noise = create_noise_instance(noise_type, num_qubits, error_rate, custom_params, experiment_id)

    # Perform hardware validation if backend provided
    if backend is not None:
        try:
            # Extract backend constraints
            backend_config = backend.configuration()
            backend_constraints = {
                "max_qubits": backend_config.n_qubits,
                "supported_gates": set(backend_config.basis_gates)
                if hasattr(backend_config, "basis_gates")
                else set(),
                "max_error_rate": getattr(backend_config, "max_error_rate", 0.1),  # Typical limit
                "min_t1": getattr(backend_config, "min_t1", 10e-6),  # Typical minimum
                "min_t2": getattr(backend_config, "min_t2", 5e-6),  # Typical minimum
                "temperature": getattr(backend_config, "temperature", 0.015),  # 15 mK typical
                "backend_name": backend_config.backend_name,
            }

            # Validate noise compatibility with hardware
            hardware_warnings = noise.validate_for_hardware(backend_constraints)

            if hardware_warnings:
                warning_msg = (
                    f"Hardware compatibility issues for {noise_type} noise "
                    f"on {backend_constraints['backend_name']}:\\n"
                    + "\\n".join(f"  - {warning}" for warning in hardware_warnings)
                )
                logger.warning(warning_msg)

                # For critical issues, raise error
                critical_keywords = ["exceeds", "below", "unsupported", "incompatible"]
                if any(
                    keyword in warning.lower()
                    for warning in hardware_warnings
                    for keyword in critical_keywords
                ):
                    raise ValueError(
                        f"Noise {noise_type} is incompatible with backend {backend_constraints['backend_name']}. "
                        f"Issues: {hardware_warnings}"
                    )

            logger.info(
                f"Hardware validation passed for {noise_type} noise "
                f"on {backend_constraints['backend_name']} "
                f"({num_qubits}/{backend_constraints['max_qubits']} qubits used)"
            )

        except Exception as e:
            logger.error(f"Hardware validation failed: {e}")
            raise ValueError(f"Cannot validate hardware compatibility: {e}") from e

    # Create the actual noise model
    return create_noise_model(noise_type, num_qubits, error_rate, custom_params, experiment_id)


def validate_noise_request(
    noise_type: str,
    num_qubits: int,
    error_rate: float | None = None,
    custom_params: dict | None = None,
) -> list[str]:
    """Validate noise creation request before attempting model creation.

    # Pre-flight Validation
    Catches common errors before expensive quantum noise model creation,
    providing educational feedback about quantum decoherence constraints
    and physics limitations.

    Args:
        noise_type: Requested noise type
        num_qubits: Number of qubits
        error_rate: Error rate parameter
        custom_params: Physics parameters

    Returns:
        List[str]: List of validation warnings (empty if valid)

    Example:
        >>> warnings = validate_noise_request("DEPOLARIZING", 15, error_rate=0.9)
        >>> if warnings:
        >>>     print("Warnings:", warnings)
    """
    warnings = []

    # Check noise type
    if noise_type not in NOISE_CLASSES:
        warnings.append(f"Unknown noise type: {noise_type}")
        return warnings

    # Check qubit count
    if num_qubits < 1:
        warnings.append("Noise models require at least 1 qubit")
    elif num_qubits > 15:
        warnings.append(
            f"Large quantum system ({num_qubits} qubits) requires "
            f"4^{num_qubits} = {4**num_qubits:,} Kraus elements - "
            f"consider smaller systems for efficient simulation"
        )

    # Check error rate bounds
    if error_rate is not None:
        if not 0 <= error_rate <= 1:
            warnings.append(f"Error rate must be in [0,1], got {error_rate}")
        elif error_rate > 0.5:
            warnings.append(
                f"High error rate ({error_rate:.3f}) may indicate regime "
                f"where quantum advantage is lost"
            )

    # Noise-specific validations
    if noise_type == "DEPOLARIZING" and error_rate is not None:
        max_depol_rate = 1 - (1 / (4**num_qubits))
        if error_rate > max_depol_rate:
            warnings.append(
                f"Depolarizing error rate {error_rate:.4f} exceeds physical bound "
                f"{max_depol_rate:.4f} for {num_qubits} qubits"
            )

    # Physics parameter validations
    if custom_params:
        t1 = custom_params.get("t1")
        t2 = custom_params.get("t2")
        if t1 and t2 and t2 > 2 * t1:
            warnings.append(
                f"T2 ({t2:.2e}s) cannot exceed 2*T1 ({2 * t1:.2e}s) - violates quantum physics"
            )

        temperature = custom_params.get("temperature")
        if temperature and temperature < 0:
            warnings.append(f"Temperature must be non-negative, got {temperature}K")

    return warnings


def _apply_readout_errors(
    noise_model: NoiseModel, num_qubits: int, readout_error_rate: float
) -> None:
    """Apply per-qubit readout (measurement) errors to the noise model.

    Models imperfect measurement: each qubit has probability `readout_error_rate`
    of reporting the wrong computational basis outcome. This is independent of
    gate errors and represents measurement apparatus imperfections.

    The confusion matrix per qubit is:
        P(measured | true) = [[1-p,  p ],
                              [ p,  1-p]]
    where p = readout_error_rate.
    """
    from qiskit_aer.noise import ReadoutError

    p = float(readout_error_rate)
    probs = [[1 - p, p], [p, 1 - p]]
    for qubit in range(num_qubits):
        noise_model.add_readout_error(ReadoutError(probs), [qubit])

    logger.info(f"Applied readout error (rate={p:.4f}) to {num_qubits} qubits")


def _get_appropriate_gates(noise_type: str, num_qubits: int) -> list[str]:
    """Get appropriate gate list for specific noise type.

    # Gate Selection Strategy
    Different noise types affect different classes of quantum gates:
    - Single-qubit coherent errors: affect single-qubit gates
    - Thermal processes: affect all gates during execution
    - Correlated errors: affect multi-qubit entangling gates

    Args:
        noise_type: Type of noise channel
        num_qubits: Number of qubits in system

    Returns:
        List of gate names appropriate for this noise type
    """
    # Gate classifications for different noise mechanisms
    single_qubit_gates = ["id", "u1", "u2", "u3", "h", "x", "y", "z", "s", "t"]
    two_qubit_gates = ["cx", "cy", "cz", "ch", "swap", "iswap"]

    # Noise type specific gate selections
    if noise_type in ["BIT_FLIP", "PHASE_FLIP", "AMPLITUDE_DAMPING", "PHASE_DAMPING"]:
        # Single-qubit processes affect all operations (applied to each qubit involved)
        return single_qubit_gates + two_qubit_gates
    elif noise_type in ["DEPOLARIZING", "THERMAL_RELAXATION", "CORRELATED_DEPOLARIZING"]:
        # Global processes affect all gate types
        if num_qubits == 1:
            return single_qubit_gates
        elif num_qubits == 2:
            return single_qubit_gates + two_qubit_gates
        else:
            return single_qubit_gates + two_qubit_gates
    else:
        # Default: apply to common gate set
        return single_qubit_gates + two_qubit_gates


def get_noise_info() -> dict[str, dict[str, str]]:
    """Get comprehensive information about all available noise types.

    # Educational Noise Catalog
    Built from each noise class's ``CATALOG`` class attribute — a single source of
    truth that cannot drift from ``NOISE_CLASSES``. Channels that set ``CATALOG = None``
    (e.g. advanced variants like correlated depolarizing) are omitted.

    Returns:
        Dict mapping noise types to their descriptions and applications

    Example:
        >>> info = get_noise_info()
        >>> print(info["DEPOLARIZING"]["description"])
        >>> print(info["AMPLITUDE_DAMPING"]["use_case"])
    """
    catalog: dict[str, dict[str, str]] = {}
    for noise_type, noise_class in NOISE_CLASSES.items():
        entry = noise_class.CATALOG
        if entry is not None:
            catalog[noise_type] = entry
    return catalog
