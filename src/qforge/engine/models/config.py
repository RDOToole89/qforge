"""Experiment Configuration Models.

Purpose: Define the complete specification for quantum experiment configurations,
from basic circuits to noisy simulations with analysis metrics.

Key Features:
- Type-safe configuration with validation
- Analysis metric selection
- Noise model specifications
- Quantum state definitions
- Simulation mode controls

Dependencies: Pydantic only
Used by: Engine API, CLI parsers, validation layers
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

# Suggested labels for grouping/storage. Not a closed taxonomy — any string is valid.
EXPERIMENT_TYPE_EXAMPLES: tuple[str, ...] = (
    "control",
    "scaling",
    "parameter_sweep",
    "noise_comparison",
    "convergence",
    "batch_sweep",
)


class ExperimentConfig(BaseModel):
    """Complete quantum experiment configuration.

    This model defines all parameters needed to run a quantum experiment,
    from basic circuit parameters to advanced analysis configurations.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    # ===== Core Quantum Parameters =====
    num_qubits: int = Field(ge=1, le=20, description="Number of qubits in the quantum circuit")

    state_type: Literal["GHZ", "W", "CLUSTER", "BELL", "SUPERPOSITION", "CUSTOM"] = Field(
        description="Type of quantum state to prepare"
    )

    # ===== Simulation Parameters =====
    sim_mode: Literal["qasm", "statevector", "density_matrix", "hardware"] = Field(
        default="qasm",
        description=(
            "Execution mode: "
            "'qasm' = shot-based simulation (supports noise), "
            "'statevector' = exact noiseless state, "
            "'density_matrix' = full mixed-state simulation, "
            "'hardware' = execute on IBM Quantum hardware via qiskit-ibm-runtime"
        ),
    )

    shots: int = Field(
        default=1024,
        ge=1,
        le=1000000,
        description="Number of measurement shots for qasm simulation",
    )

    # ===== Noise Model Parameters =====
    noise_enabled: bool = Field(
        default=False, description="Whether to apply noise to the quantum circuit"
    )

    noise_type: (
        Literal[
            "depolarizing",
            "amplitude_damping",
            "phase_damping",
            "bit_flip",
            "phase_flip",
            "thermal_relaxation",
            "correlated_depolarizing",
        ]
        | None
    ) = Field(default=None, description="Type of noise model to apply")

    error_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Error rate for noise models (0.0 = no noise, 1.0 = maximum noise)",
    )

    # Advanced noise parameters
    z_prob: float | None = Field(default=None, ge=0.0, le=1.0)
    i_prob: float | None = Field(default=None, ge=0.0, le=1.0)
    t1: float | None = Field(default=None, gt=0.0)
    t2: float | None = Field(default=None, gt=0.0)

    # Readout (measurement) error
    readout_error_rate: float | None = Field(
        default=None,
        ge=0.0,
        le=0.5,
        description=(
            "Per-qubit readout error probability (bit-flip on "
            "measurement). Independent of gate noise."
        ),
    )

    # Circuit balancing
    balance_circuit: str | None = Field(
        default=None,
        description=(
            "Circuit balancing strategy. 'gate_count' pads circuits "
            "with identity gates to equalize depth across state types."
        ),
    )

    # ===== Analysis Parameters =====
    metrics: list[str] | str | None = Field(
        default=None,
        description=(
            "Profile name, explicit metric list, or None. "
            "Built-in profiles: 'structure', 'quick', 'information_theory'. "
            "Register more with register_profile()."
        ),
    )

    observables: list[str] | None = Field(
        default=None,
        description=(
            "Optional Pauli strings to estimate (e.g. ['ZZ', 'XX']). "
            "Same MSB-left order as bitstrings: leftmost character is logical "
            "index 0. I/Z-only strings reuse the Z-basis shots; X/Y require "
            "extra circuits (qasm/hardware) or are exact in statevector/"
            "density_matrix modes. Not a VQE energy — experiment programs "
            "interpret these values."
        ),
    )

    experiment_type: str | None = Field(
        default=None,
        description=(
            "Optional label for grouping and storage — not a closed taxonomy. "
            "Use any string (for example your research track). "
            "Suggested: control, scaling, parameter_sweep, noise_comparison, "
            "convergence, batch_sweep."
        ),
        max_length=64,
    )

    multiple_runs: int = Field(
        default=1,
        ge=1,
        le=1000,
        description="Number of experimental runs for statistical validation",
    )

    track_convergence: bool = Field(
        default=False,
        description="Enable convergence tracking for high-precision experiments",
    )

    # ===== Output Parameters =====
    visualization_type: list[str] | str = Field(
        default="histogram",
        description=(
            "Visualization type(s) to generate. "
            "String for single type, list for multiple. "
            "'circuit' uses Qiskit's circuit.draw (mpl) plus gate explainers; "
            "omit it or set 'none' to skip. "
            "Valid: 'histogram', 'density_matrix', 'correlation', 'circuit', "
            "'metrics_summary', 'bloch_sphere', 'all', 'none'"
        ),
    )

    export_formats: list[Literal["png", "pdf", "svg"]] = Field(
        default=["png"],
        description="Output formats for generated visualizations",
    )

    # ===== System Parameters =====
    rng_seed: int | None = Field(
        default=None,
        description="Random number generator seed for reproducible results",
    )

    # ===== Hardware Execution Parameters =====
    backend_name: str | None = Field(
        default=None,
        description=(
            "IBM Quantum backend name (e.g. 'ibm_brisbane'). "
            "If None and sim_mode='hardware', the least busy backend is auto-selected."
        ),
    )

    optimization_level: int = Field(
        default=1,
        ge=0,
        le=3,
        description="Transpiler optimization level (0-3). Only used for sim_mode='hardware'.",
    )

    hardware_session: bool = Field(
        default=False,
        description="Keep backend reserved across sweep jobs. Only used for sim_mode='hardware'.",
    )

    custom_params: dict[str, Any] | None = Field(
        default=None,
        description="Custom parameters for advanced state preparation or noise models",
    )

    # ===== Field normalizers / validators =====
    @field_validator("visualization_type", mode="before")
    @classmethod
    def _validate_visualization_type(cls, v: Any) -> Any:
        """Validate visualization_type values against allowed set."""
        valid = {
            "histogram",
            "density_matrix",
            "correlation",
            "circuit",
            "metrics_summary",
            "bloch_sphere",
            "sweep_line",
            "comparison",
            "all",
            "none",
        }
        if isinstance(v, str):
            if v not in valid:
                raise ValueError(f"Invalid visualization_type '{v}'. Valid: {valid}")
            return v
        if isinstance(v, list):
            for item in v:
                if item not in valid:
                    raise ValueError(f"Invalid visualization_type '{item}'. Valid: {valid}")
            return v
        return v

    @field_validator("state_type", mode="before")
    @classmethod
    def _normalize_state_type(cls, v: Any) -> Any:
        """Normalize state_type to UPPERCASE for engine compatibility."""
        if isinstance(v, str):
            return v.strip().upper()
        return v

    @field_validator("noise_type", mode="before")
    @classmethod
    def _normalize_noise_type(cls, v: str | None) -> str | None:
        """Normalize noise_type to lowercase to match enum."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("t2")
    @classmethod
    def validate_t2_constraint(cls, v: float | None, info: ValidationInfo) -> float | None:
        """Validate T2 ≤ 2*T1 constraint (field-level guard; model-level check also present)."""
        if v is not None and "t1" in info.data and info.data["t1"] is not None:
            t1 = info.data["t1"]
            if v > 2 * t1:
                raise ValueError(f"T2 ({v}) must be ≤ 2*T1 ({2 * t1}) for physical validity")
        return v

    @field_validator("observables")
    @classmethod
    def _normalize_observables(cls, v: list[str] | None) -> list[str] | None:
        """Uppercase Pauli labels; length is checked against num_qubits below."""
        if v is None:
            return None
        return [label.strip().upper() for label in v]

    @field_validator("noise_type")
    @classmethod
    def validate_noise_type_with_enabled(cls, v: str | None, info: ValidationInfo) -> str | None:
        """Ensure noise_type is provided when noise_enabled=True."""
        if info.data.get("noise_enabled", False) and v is None:
            raise ValueError("noise_type must be specified when noise_enabled=True")
        return v

    @model_validator(mode="after")
    def _cross_field_checks(self) -> ExperimentConfig:
        """Model-level cross-field validations that are safer after all fields are parsed."""
        if self.t1 is not None and self.t2 is not None:
            if self.t2 > 2 * self.t1:
                raise ValueError(f"T2 ({self.t2}) must be ≤ 2*T1 ({2 * self.t1})")

        # Aer statevector backend does not support NoiseModel
        if self.sim_mode == "statevector" and self.noise_enabled:
            raise ValueError(
                "sim_mode='statevector' is incompatible with noise_enabled=True. "
                "The statevector backend computes the exact noiseless state. "
                "Use sim_mode='density_matrix' for noisy simulations with full state access."
            )

        # Hardware mode rejects simulated noise (physical noise is the point)
        if self.sim_mode == "hardware" and self.noise_enabled:
            raise ValueError(
                "sim_mode='hardware' is incompatible with noise_enabled=True. "
                "Real quantum hardware has physical noise; simulated noise models "
                "cannot be applied."
            )

        # Hardware is inherently non-deterministic
        if self.sim_mode == "hardware" and self.rng_seed is not None:
            raise ValueError(
                "sim_mode='hardware' does not support rng_seed. "
                "Quantum hardware measurements are inherently probabilistic."
            )

        # backend_name only meaningful for hardware mode
        if self.backend_name is not None and self.sim_mode != "hardware":
            raise ValueError("backend_name is only valid when sim_mode='hardware'.")

        # IBM hardware shot limit
        if self.sim_mode == "hardware" and self.shots > 100_000:
            raise ValueError(f"shots={self.shots} exceeds IBM Quantum hardware limit (100,000).")

        if self.observables:
            from qforge.core.math.observables import parse_pauli_string

            for label in self.observables:
                parse_pauli_string(label, self.num_qubits)

        return self


class AdvancedNoiseConfig(BaseModel):
    """Advanced noise configuration for complex noise models.

    Purpose: Separate complex noise configurations from basic ExperimentConfig
    to keep the main config model clean and focused.
    """

    # Thermal relaxation parameters
    t1_values: dict[int, float] | None = Field(
        default=None, description="Per-qubit T1 relaxation times"
    )

    t2_values: dict[int, float] | None = Field(
        default=None, description="Per-qubit T2 dephasing times"
    )

    # Correlated noise parameters
    crosstalk_matrix: list[list[float]] | None = Field(
        default=None, description="Qubit crosstalk correlation matrix"
    )

    # Time-dependent noise
    time_dependent: bool = Field(default=False, description="Enable time-dependent noise evolution")

    @field_validator("crosstalk_matrix")
    @classmethod
    def validate_crosstalk_matrix(cls, v: list[list[float]] | None) -> list[list[float]] | None:
        """Validate crosstalk matrix is square and properly normalized."""
        if v is not None:
            n = len(v)
            if not all(len(row) == n for row in v):
                raise ValueError("Crosstalk matrix must be square")
            # Additional validation could be added here
        return v
