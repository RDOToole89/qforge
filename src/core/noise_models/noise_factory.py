# src/noise_models/noise_factory.py

import logging
from typing import Optional, List
from qiskit_aer.noise import NoiseModel
from src.utils import logger as logger_utils
from .base_noise import BaseNoise
from .depolarizing import DepolarizingNoise
from .phase_flip import PhaseFlipNoise
from .amplitude_damping import AmplitudeDampingNoise
from .phase_damping import PhaseDampingNoise
from .thermal_relaxation import ThermalRelaxationNoise
from .bit_flip import BitFlipNoise

logger = logging.getLogger("QuantumExperiment.NoiseModels")

# Example defaults (you might want to move these to config if needed)
DEFAULT_ERROR_RATE = 0.1
DEFAULT_T1 = 100e-6
DEFAULT_T2 = 80e-6

NOISE_CLASSES = {
    "DEPOLARIZING": DepolarizingNoise,
    "PHASE_FLIP": PhaseFlipNoise,
    "AMPLITUDE_DAMPING": AmplitudeDampingNoise,
    "PHASE_DAMPING": PhaseDampingNoise,
    "THERMAL_RELAXATION": ThermalRelaxationNoise,
    "BIT_FLIP": BitFlipNoise,
}

NOISE_CONFIG = {
    "DEPOLARIZING": {"error_rate": 0.1},
    "PHASE_FLIP": {"error_rate": 0.1},
    "AMPLITUDE_DAMPING": {"error_rate": 0.05},
    "PHASE_DAMPING": {"error_rate": 0.05},
    "THERMAL_RELAXATION": {"t1": 100e-6, "t2": 80e-6},
    "BIT_FLIP": {"error_rate": 0.1},
}


def create_noise_model(
    noise_type: str,
    num_qubits: int,
    error_rate: Optional[float] = None,
    z_prob: Optional[float] = None,
    i_prob: Optional[float] = None,
    t1: Optional[float] = None,
    t2: Optional[float] = None,
    t2_star: Optional[float] = None,
    gate_time: Optional[float] = None,
    temperature: Optional[float] = None,
    simulate_density: bool = False,
    experiment_id: str = "N/A",
) -> NoiseModel:
    """
    Enhanced noise model factory with comprehensive validation and physics-based parameters.

    Creates physically accurate noise models with proper parameter validation.
    Supports both phenomenological error rates and physics-based parameters (T1, T2, etc.).

    Args:
        noise_type (str): Type of noise to apply. Supported: {list(NOISE_CLASSES.keys())}
        num_qubits (int): Number of qubits in the circuit (must be positive).
        error_rate (float, optional): Phenomenological error rate [0, 1].
        z_prob (float, optional): Z probability for Pauli error models.
        i_prob (float, optional): Identity probability for Pauli error models.
        t1 (float, optional): T1 relaxation time (seconds, positive).
        t2 (float, optional): T2 dephasing time (seconds, positive, ≤ 2*T1).
        t2_star (float, optional): T2* pure dephasing time (seconds, positive).
        gate_time (float, optional): Gate duration (seconds, default: 20ns).
        temperature (float, optional): Operating temperature (Kelvin, default: 15mK).
        simulate_density (bool): Whether to optimize for density matrix simulation.
        experiment_id (str): Unique identifier for this experiment run.

    Returns:
        NoiseModel: Configured Qiskit noise model with validation.

    Raises:
        ValueError: If noise type, parameters, or physics constraints are invalid.
        TypeError: If parameter types are incorrect.
    """
    # Input validation
    if not isinstance(noise_type, str):
        raise TypeError(f"noise_type must be string, got {type(noise_type)}")

    if noise_type not in NOISE_CLASSES:
        raise ValueError(
            f"Invalid noise_type: '{noise_type}'. Choose from {list(NOISE_CLASSES.keys())}"
        )

    if not isinstance(num_qubits, int) or num_qubits <= 0:
        raise ValueError(f"num_qubits must be positive integer, got {num_qubits}")

    if num_qubits > 10:
        logger.warning(f"Large qubit count ({num_qubits}) may impact simulation performance")

    # Validate optional parameters
    if error_rate is not None and not (0 <= error_rate <= 1):
        raise ValueError(f"error_rate must be in [0, 1], got {error_rate}")

    if z_prob is not None and not (0 <= z_prob <= 1):
        raise ValueError(f"z_prob must be in [0, 1], got {z_prob}")

    if i_prob is not None and not (0 <= i_prob <= 1):
        raise ValueError(f"i_prob must be in [0, 1], got {i_prob}")

    if z_prob is not None and i_prob is not None:
        if abs(z_prob + i_prob - 1.0) > 1e-6:
            raise ValueError(f"z_prob + i_prob must equal 1, got {z_prob + i_prob}")

    # Physics parameter validation
    if t1 is not None and t1 <= 0:
        raise ValueError(f"T1 must be positive, got {t1}")

    if t2 is not None and t2 <= 0:
        raise ValueError(f"T2 must be positive, got {t2}")

    if t2_star is not None and t2_star <= 0:
        raise ValueError(f"T2* must be positive, got {t2_star}")

    if t1 is not None and t2 is not None and t2 > 2 * t1:
        raise ValueError(f"T2 ({t2}) cannot exceed 2*T1 ({2*t1}) - violates quantum physics")

    if gate_time is not None and gate_time <= 0:
        raise ValueError(f"gate_time must be positive, got {gate_time}")

    if temperature is not None and temperature <= 0:
        raise ValueError(f"temperature must be positive, got {temperature}")

    # Set defaults
    gate_time = gate_time or 20e-9  # 20 ns default
    temperature = temperature or 0.015  # 15 mK default

    logger.info(f"Creating {noise_type} noise model with {num_qubits} qubits")

    noise_model = NoiseModel()
    noise_class = NOISE_CLASSES[noise_type]

    # Instantiate noise with enhanced parameters and validation
    try:
        if noise_type == "THERMAL_RELAXATION":
            noise = noise_class(
                error_rate=error_rate or DEFAULT_ERROR_RATE,
                num_qubits=num_qubits,
                t1=t1 or DEFAULT_T1,
                t2=t2 or DEFAULT_T2,
                gate_time=gate_time,
                temperature=temperature,
                experiment_id=experiment_id,
            )
        elif noise_type == "PHASE_FLIP":
            noise = noise_class(
                error_rate=error_rate or DEFAULT_ERROR_RATE,
                num_qubits=num_qubits,
                z_prob=z_prob,
                i_prob=i_prob,
                experiment_id=experiment_id,
            )
        elif noise_type == "AMPLITUDE_DAMPING":
            noise = noise_class(
                error_rate=error_rate or NOISE_CONFIG[noise_type]["error_rate"],
                num_qubits=num_qubits,
                t1=t1,  # Optional physics-based parameter
                gate_time=gate_time,
                temperature=temperature,
                experiment_id=experiment_id,
            )
        elif noise_type == "PHASE_DAMPING":
            noise = noise_class(
                error_rate=error_rate or NOISE_CONFIG[noise_type]["error_rate"],
                num_qubits=num_qubits,
                t2_star=t2_star,  # Optional physics-based parameter
                gate_time=gate_time,
                experiment_id=experiment_id,
            )
        elif noise_type == "BIT_FLIP":
            noise = noise_class(
                error_rate=error_rate or NOISE_CONFIG[noise_type]["error_rate"],
                num_qubits=num_qubits,
                x_prob=z_prob,  # Reuse z_prob parameter for X probability
                i_prob=i_prob,
                experiment_id=experiment_id,
            )
        else:
            # Default case for DEPOLARIZING and other noise types
            noise = noise_class(
                error_rate=error_rate or NOISE_CONFIG[noise_type]["error_rate"],
                num_qubits=num_qubits,
                experiment_id=experiment_id,
            )

        logger.info(f"Successfully created {noise_type} noise instance")

    except Exception as e:
        logger.error(f"Failed to create {noise_type} noise: {e}")
        raise ValueError(f"Error creating {noise_type} noise: {e}") from e

    # Define gate lists and their corresponding qubit counts
    gate_configs = []
    single_qubit_noise_types = [
        "PHASE_FLIP",
        "AMPLITUDE_DAMPING",
        "PHASE_DAMPING",
        "BIT_FLIP",
    ]

    if noise_type in single_qubit_noise_types:
        # Apply single-qubit noise to each qubit individually
        for qubit in range(num_qubits):
            gate_configs.append(
                {"qubits": 1, "gates": ["id"], "target_qubits": [qubit]}
            )
    else:
        # For multi-qubit noise types like DEPOLARIZING and THERMAL_RELAXATION
        if simulate_density:
            if num_qubits >= 2:
                gate_configs.append({"qubits": 2, "gates": ["cx"]})
            if num_qubits > 2:
                gate_configs.append(
                    {"qubits": num_qubits, "gates": [f"mct_{num_qubits}"]}
                )
        else:
            gate_configs.extend(
                [
                    {"qubits": 1, "gates": ["id", "u1", "u2", "u3"]},
                    {"qubits": 2, "gates": ["cx"]},
                    {"qubits": num_qubits, "gates": [f"mct_{num_qubits}"]},
                ]
            )

    # Apply noise to gates
    for config in gate_configs:
        qubits = config["qubits"]
        gate_list = config["gates"]
        target_qubits = config.get("target_qubits", None)

        # Skip if the noise type is single-qubit but the gate requires more qubits (for non-single-qubit noise types)
        if noise_type in single_qubit_noise_types and qubits > 1:
            logger_utils.log_with_experiment_id(
                logger,
                "info",
                (
                    f"Skipping {noise_type} noise for {qubits}-qubit gates {gate_list}: "
                    "This noise type only supports single-qubit gates. "
                    "Use a multi-qubit noise type like DEPOLARIZING for these gates."
                ),
                experiment_id,
                extra_info={
                    "noise_type": noise_type,
                    "qubits": qubits,
                    "gates": gate_list,
                },
            )
            continue

        try:
            if target_qubits is not None:
                # Apply noise to specific qubits (for single-qubit noise)
                noise.apply(
                    noise_model,
                    gate_list,
                    qubits_for_error=qubits,
                    specific_qubits=target_qubits,
                )
                logger_utils.log_with_experiment_id(
                    logger,
                    "info",
                    f"Applied {noise_type} noise to qubit {target_qubits} on gates: {gate_list}",
                    experiment_id,
                    extra_info={
                        "noise_type": noise_type,
                        "qubits": target_qubits,
                        "gates": gate_list,
                    },
                )
            else:
                # Apply noise to gates with specified qubit count
                noise.apply(noise_model, gate_list, qubits_for_error=qubits)
                logger_utils.log_with_experiment_id(
                    logger,
                    "info",
                    f"Applied {noise_type} noise to {qubits}-qubit gates: {gate_list}",
                    experiment_id,
                    extra_info={
                        "noise_type": noise_type,
                        "qubits": qubits,
                        "gates": gate_list,
                    },
                )
        except Exception as e:
            logger_utils.log_with_experiment_id(
                logger,
                "warning",
                (
                    f"Failed to apply {noise_type} noise to {qubits}-qubit gates {gate_list}. "
                    f"Error: {str(e)}. This may be due to an incompatible qubit count. "
                    "Ensure the noise type matches the gate's qubit requirements."
                ),
                experiment_id,
                extra_info={
                    "noise_type": noise_type,
                    "qubits": qubits,
                    "gates": gate_list,
                    "error": str(e),
                },
            )

    return noise_model
