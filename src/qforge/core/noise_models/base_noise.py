"""Quantum noise model framework.

# Quantum Decoherence Fundamentals
Noise models represent the environmental coupling that destroys quantum coherence
in real quantum systems. Each noise type captures different physical mechanisms:
- Coupling to electromagnetic fields, thermal baths, charge fluctuations
- Microscopic interactions that cannot be controlled or measured
- Fundamental limits imposed by quantum mechanics and thermodynamics

# Mathematical Framework
Noise models are represented as completely positive trace-preserving (CPTP) maps
that describe how quantum states evolve under environmental interaction:
ρ → Σᵢ Kᵢ ρ Kᵢ† where Σᵢ Kᵢ† Kᵢ = I (Kraus representation)

# Educational Philosophy
Every noise model documents the physics of open quantum systems it implements,
bridging theory (master equations, Lindblad forms) with practice (real devices).
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, ClassVar

from qiskit_aer.noise import NoiseModel

logger = logging.getLogger(__name__)

# Default parameters matching physics standards
DEFAULT_ERROR_RATE = 0.05  # Typical gate fidelity ~95%
DEFAULT_T1_TIME = 100e-6  # 100 μs typical T1
DEFAULT_T2_TIME = 80e-6  # 80 μs typical T2 (< 2*T1)
DEFAULT_GATE_TIME = 20e-9  # 20 ns typical gate time
DEFAULT_TEMPERATURE = 0.015  # 15 mK typical dilution refrigerator


class BaseNoise(ABC):
    """Abstract base class for quantum noise models.

    # Quantum Decoherence Foundation
    BaseNoise provides the foundational architecture for modeling environmental
    interactions that destroy quantum coherence. Each subclass implements a
    specific physical decoherence mechanism.

    # Design Philosophy
    - **Physics-First**: Every noise model reflects real quantum decoherence mechanisms
    - **Educational Clarity**: Clear explanations of underlying physics principles
    - **Hardware Compatibility**: Validation against real quantum device constraints
    - **Framework Consistency**: Uniform interfaces matching state preparation patterns

    # Architecture Principles
    - **Single Responsibility**: Each noise class models one specific decoherence mechanism
    - **Separation of Concerns**: Noise creation cleanly separated from analysis
    - **Clean Interfaces**: Consistent patterns with state preparation framework

    # Framework Role
    BaseNoise serves as the contract between the noise factory and individual noise
    implementations, ensuring consistent behavior while allowing specialized physics
    modeling for each decoherence mechanism.

    # Abstract Methods (Must be implemented by subclasses)
    - `apply()`: Apply noise to quantum gates in noise model
    - `get_kraus_operators()`: Return mathematical representation
    - `get_physics_description()`: Educational physics explanation

    # Shared Functionality (Provided by BaseNoise)
    - Parameter validation with physics constraints
    - Hardware compatibility checking
    - Educational property access
    - Logging with experimental metadata

    # Educational Notes
    Understanding noise models is crucial for quantum computing because:
    - Real quantum devices always experience environmental coupling
    - Noise limits the size and complexity of quantum computations
    - Error correction schemes must be tailored to specific noise characteristics
    - Quantum advantage requires noise rates below critical thresholds
    """

    # ------------------------------------------------------------------ #
    # Per-channel metadata — declared here, overridden by each subclass.
    # Single home for "what kind of channel is this": no hardcoded lists
    # in the factory or base methods to drift out of sync.
    # ------------------------------------------------------------------ #

    #: Canonical registry key (matches ``noise_factory.NOISE_CLASSES``).
    NOISE_TYPE: ClassVar[str] = ""
    #: Whether the channel is unital (preserves the maximally mixed state I/d).
    IS_UNITAL: ClassVar[bool] = False
    #: Educational catalog entry, or ``None`` to omit from the intro catalog.
    CATALOG: ClassVar[dict[str, str] | None] = None

    def __init__(
        self,
        error_rate: float = DEFAULT_ERROR_RATE,
        num_qubits: int = 1,
        experiment_id: str = "N/A",
        **physics_params: Any,
    ):
        """Initialize base noise model with physics validation.

        # Parameter Validation Philosophy
        All parameters undergo physics-based validation to ensure they represent
        realistic quantum decoherence scenarios. This prevents unphysical
        configurations that could lead to incorrect results.

        Args:
            error_rate: Phenomenological error probability [0, 1]
            num_qubits: Number of qubits affected by noise (positive integer)
            experiment_id: Unique identifier for experiment tracking
            **physics_params: Model-specific physics parameters (T1, T2, temperature, etc.)

        Raises:
            ValueError: If parameters violate quantum physics constraints
        """
        # Validate fundamental parameters
        self._validate_error_rate(error_rate)
        self._validate_qubit_count(num_qubits)

        # Store validated parameters
        self.error_rate = error_rate
        self.num_qubits = num_qubits
        self.experiment_id = experiment_id
        self.physics_params = physics_params

        # Initialize derived properties. Prefer the explicit canonical NOISE_TYPE;
        # fall back to a name-derived guess only if a subclass forgot to declare it.
        self._noise_type = self.NOISE_TYPE or self.__class__.__name__.replace("Noise", "").upper()

        # Log initialization with physics context
        self._log_initialization()

    @abstractmethod
    def apply(
        self, noise_model: NoiseModel, gate_list: list[str], qubits_for_error: int | None = None
    ) -> None:
        """Apply quantum noise to specified gates in the noise model.

        # Abstract Method Contract
        Each noise type implements its specific decoherence mechanism while
        maintaining consistent interface patterns across all noise models.
        Implementation must handle physics validation and gate compatibility.

        Args:
            noise_model: Qiskit noise model to modify with decoherence
            gate_list: Quantum gates to which noise should be applied
            qubits_for_error: Override for number of qubits (None uses self.num_qubits)

        Raises:
            ValueError: If gate list or qubit configuration is invalid

        Example:
            >>> noise = DepolarizingNoise(error_rate=0.01, num_qubits=2)
            >>> noise_model = NoiseModel()
            >>> noise.apply(noise_model, ['cx', 'h'])
        """
        pass

    @abstractmethod
    def get_kraus_operators(self) -> list[Any]:
        """Return Kraus operators representing the quantum decoherence channel.

        # Mathematical Representation
        Kraus operators {Kᵢ} provide the fundamental mathematical description
        of how this noise channel transforms quantum states: ρ → Σᵢ Kᵢ ρ Kᵢ†

        Returns:
            List of Kraus operators for this decoherence channel

        Educational Note:
            Kraus operators must satisfy Σᵢ Kᵢ† Kᵢ = I (completeness relation)
            to ensure the map is trace-preserving.
        """
        pass

    @abstractmethod
    def get_physics_description(self) -> dict[str, str]:
        """Return educational description of the physical decoherence mechanism.

        # Educational Physics Content
        Provides comprehensive explanation of:
        - Physical origin of this decoherence mechanism
        - Environmental coupling responsible for noise
        - Real-world quantum systems where this occurs
        - Relationship to fundamental physics principles

        Returns:
            Dict with physics description keys: mechanism, origin, examples, principles

        Example:
            >>> noise = DepolarizingNoise(0.01)
            >>> physics = noise.get_physics_description()
            >>> print(physics['mechanism'])
            "Uniform mixing with maximally mixed state due to random Pauli errors"
        """
        pass

    def get_basic_properties(self) -> dict[str, Any]:
        """Get basic properties of the noise model for framework integration.

        # Framework Integration Contract
        Provides standardized interface for engine and analysis modules to
        access noise model properties without knowing implementation details.
        Mirrors BaseState.get_basic_properties() for architectural consistency.

        Returns:
            Dict with noise model properties for engine coordination
        """
        return {
            "noise_type": self._noise_type,
            "error_rate": self.error_rate,
            "num_qubits": self.num_qubits,
            "experiment_id": self.experiment_id,
            "physics_parameters": self.physics_params,
            "kraus_rank": len(self.get_kraus_operators()),
            "is_unital": self._is_unital_channel(),
            "channel_capacity": self._estimate_channel_capacity(),
            "hardware_compatible": True,  # Overridden by validation
        }

    def validate_for_hardware(self, backend_constraints: dict[str, Any]) -> list[str]:
        """Validate noise model compatibility with real quantum hardware.

        # Hardware Validation Philosophy
        Real quantum devices have constraints on gate sets, connectivity,
        coherence times, and error rates. This method ensures noise models
        reflect realistic hardware capabilities and limitations.

        Args:
            backend_constraints: Hardware specifications and limits
                - max_error_rate: Maximum supported error rate
                - supported_gates: Available gate set
                - coherence_times: T1/T2 specifications
                - temperature: Operating temperature

        Returns:
            List of warning messages (empty if fully compatible)

        Example:
            >>> constraints = {'max_error_rate': 0.1, 'min_t1': 50e-6}
            >>> warnings = noise.validate_for_hardware(constraints)
            >>> if warnings:
            >>>     print("Hardware issues:", warnings)
        """
        warnings = []

        # Validate error rate against hardware limits
        max_error_rate = backend_constraints.get("max_error_rate", 1.0)
        if self.error_rate > max_error_rate:
            warnings.append(
                f"Error rate {self.error_rate:.4f} exceeds hardware limit {max_error_rate:.4f}"
            )

        # Validate physics parameters against hardware specs
        min_t1 = backend_constraints.get("min_t1")
        if min_t1 and "t1" in self.physics_params:
            if self.physics_params["t1"] < min_t1:
                warnings.append(
                    f"T1 time {self.physics_params['t1']:.2e}s below hardware minimum {min_t1:.2e}s"
                )

        # Validate supported gates
        supported_gates = backend_constraints.get("supported_gates", set())
        if supported_gates:
            required_gates = self._get_required_gates()
            unsupported = set(required_gates) - set(supported_gates)
            if unsupported:
                warnings.append(f"Noise requires unsupported gates: {list(unsupported)}")

        # Validate qubit connectivity
        max_qubits = backend_constraints.get("max_qubits", float("inf"))
        if self.num_qubits > max_qubits:
            warnings.append(
                f"Noise affects {self.num_qubits} qubits but hardware supports max {max_qubits}"
            )

        return warnings

    # Helper Methods (Following BaseState patterns)

    def _validate_error_rate(self, error_rate: float) -> None:
        """Validate error rate against quantum physics constraints.

        # Physics Constraint Validation
        Error rates must be probabilities [0,1] and respect channel-specific
        physical bounds (e.g., depolarizing channels have maximum error rates).
        """
        if not isinstance(error_rate, (int, float)):
            raise TypeError(f"Error rate must be numeric, got {type(error_rate)}")

        if not 0 <= error_rate <= 1:
            raise ValueError(f"Error rate must be probability in [0,1], got {error_rate}")

        # Channel-specific bounds will be validated by subclasses

    def _validate_qubit_count(self, num_qubits: int) -> None:
        """Validate qubit count for noise model creation.

        # Computational Feasibility
        Large qubit counts create exponentially large noise operators
        that may be computationally infeasible to construct or apply.
        """
        if not isinstance(num_qubits, int):
            raise TypeError(f"Number of qubits must be integer, got {type(num_qubits)}")

        if num_qubits < 1:
            raise ValueError("Noise models require at least 1 qubit")

        if num_qubits > 10:
            logger.warning(
                f"Large qubit count ({num_qubits}) may create computationally expensive "
                f"noise operators with {4**num_qubits:,} elements"
            )

    def _estimate_decoherence_timescale(self) -> str:
        """Estimate characteristic decoherence timescale for this noise type.

        Returns:
            Human-readable timescale description
        """
        if "t1" in self.physics_params:
            return f"T1-limited: ~{self.physics_params['t1']:.1e}s"
        elif "t2" in self.physics_params:
            return f"T2-limited: ~{self.physics_params['t2']:.1e}s"
        else:
            # Estimate from error rate and typical gate time
            gate_time = self.physics_params.get("gate_time", DEFAULT_GATE_TIME)
            if self.error_rate > 0:
                decoherence_time = gate_time / self.error_rate
                return f"Rate-estimated: ~{decoherence_time:.1e}s"
            return "No decoherence (error_rate=0)"

    def _is_unital_channel(self) -> bool:
        """Check if this noise channel is unital (preserves maximally mixed state).

        # Channel Classification
        Unital channels satisfy E(I/d) = I/d where I is the identity matrix
        and d is the Hilbert space dimension. This is important for
        understanding which quantum states are preserved under noise.

        Each channel declares its own ``IS_UNITAL`` — there is no central list to
        keep in sync.
        """
        return self.IS_UNITAL

    def _estimate_channel_capacity(self) -> float:
        """Estimate quantum channel capacity for information transmission.

        # Information Theory
        Channel capacity determines maximum rate of reliable quantum
        information transmission through this noisy channel.
        """
        # Rough estimate based on error rate (exact calculation is complex)
        if self.error_rate == 0:
            return 1.0  # Perfect channel
        elif self.error_rate >= 0.5:
            return 0.0  # Heavily degraded channel
        else:
            # Approximate formula for moderate noise
            return max(0, 1 - 2 * self.error_rate)

    def _get_required_gates(self) -> list[str]:
        """Get list of quantum gates required for this noise model.

        # Hardware Compatibility
        Different noise types may require different gate sets for proper
        implementation on quantum hardware.
        """
        # Default gates - subclasses can override
        return ["id", "u1", "u2", "u3", "cx"]

    def log_noise_creation(self, noise_type: str, extra_info: dict | None = None) -> None:
        """Log noise model creation with comprehensive metadata.

        # Educational Logging Philosophy
        Structured logging helps users understand what noise models are being
        created and provides context for experimental reproducibility.
        Mirrors BaseState.log_state_creation() for consistency.

        Args:
            noise_type: Type of noise being created
            extra_info: Additional context for experiment tracking
        """
        base_info = {
            "noise_type": noise_type,
            "error_rate": self.error_rate,
            "num_qubits": self.num_qubits,
            "experiment_id": self.experiment_id,
            "physics_params": self.physics_params,
            "framework_role": "decoherence_channel_creation",
        }

        if extra_info:
            base_info.update(extra_info)

        logger.info(
            f"Created {noise_type} noise model: error_rate={self.error_rate:.4f}, "
            f"qubits={self.num_qubits} (experiment: {self.experiment_id})"
        )
        logger.debug(f"Noise creation details: {base_info}")

    def _log_initialization(self) -> None:
        """Log noise model initialization with physics validation."""
        logger.debug(
            f"Initialized {self._noise_type} noise: "
            f"error_rate={self.error_rate:.4f}, qubits={self.num_qubits}, "
            f"params={self.physics_params}"
        )

    def __str__(self) -> str:
        """Human-readable description for educational purposes."""
        return (
            f"{self._noise_type} noise: {self.num_qubits}-qubit, "
            f"error_rate={self.error_rate:.4f} [quantum decoherence]"
        )
