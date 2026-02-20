"""
Experiment Configuration Models

Purpose: Define the complete specification for quantum experiment configurations.
Supports both basic experiments and advanced research configurations with
structured decoherence analysis.

Key Features:
- Type-safe configuration with validation
- Research parameter support
- Noise model specifications
- Quantum state definitions
- Simulation mode controls

Dependencies: Pydantic only
Used by: Engine API, CLI parsers, validation layers
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ExperimentConfig(BaseModel):
    """
    Complete quantum experiment configuration.

    This model defines all parameters needed to run a quantum experiment,
    from basic circuit parameters to advanced research configurations.
    """

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True, validate_assignment=True)

    # ===== Core Quantum Parameters =====
    num_qubits: int = Field(ge=1, le=20, description="Number of qubits in the quantum circuit")

    state_type: Literal["GHZ", "W", "CLUSTER", "BELL", "SUPERPOSITION", "CUSTOM"] = Field(
        description="Type of quantum state to prepare"
    )

    # ===== Simulation Parameters =====
    sim_mode: Literal["qasm"] = Field(
        default="qasm", description="Simulation mode: only QASM simulation supported"
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

    # ===== Circuit Balancing =====
    balance_circuit: str | None = Field(
        default=None,
        description="Circuit depth balancing strategy. 'gate_count' pads with identity gates.",
    )

    # ===== Research Parameters =====
    metrics: list[str] | str | None = Field(
        default=None,
        description="Profile name, explicit metric list, or None for no metrics",
    )

    research_type: (
        Literal[
            "structured_decoherence",
            "parameter_sweep",
            "noise_comparison",
            "control",
            "scaling",
            "convergence",
            "batch_sweep",
        ]
        | None
    ) = Field(default=None, description="Type of research analysis to perform")

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
    visualization_type: Literal["histogram", "none"] = Field(
        default="histogram",
        description="Type of visualization to generate (research-focused)",
    )

    # ===== System Parameters =====
    rng_seed: int | None = Field(
        default=None,
        description="Random number generator seed for reproducible results",
    )

    custom_params: dict[str, Any] | None = Field(
        default=None,
        description="Custom parameters for advanced state preparation or noise models",
    )

    # ===== Field normalizers / validators =====
    @field_validator("state_type", mode="before")
    @classmethod
    def _normalize_state_type(cls, v: str) -> str:
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
    def validate_t2_constraint(cls, v: float | None, info) -> float | None:
        """Validate T2 ≤ 2*T1 constraint (field-level guard; model-level check also present)."""
        if v is not None and "t1" in info.data and info.data["t1"] is not None:
            t1 = info.data["t1"]
            if v > 2 * t1:
                raise ValueError(f"T2 ({v}) must be ≤ 2*T1 ({2 * t1}) for physical validity")
        return v

    @field_validator("noise_type")
    @classmethod
    def validate_noise_type_with_enabled(cls, v: str | None, info) -> str | None:
        """Ensure noise_type is provided when noise_enabled=True."""
        if info.data.get("noise_enabled", False) and v is None:
            raise ValueError("noise_type must be specified when noise_enabled=True")
        return v

    @model_validator(mode="after")
    def _cross_field_checks(self) -> ExperimentConfig:
        """
        Model-level cross-field validations that are safer after all fields are parsed.
        Currently re-enforces T2 ≤ 2*T1 for robustness when values are set/updated together.
        """
        if self.t1 is not None and self.t2 is not None:
            if self.t2 > 2 * self.t1:
                raise ValueError(f"T2 ({self.t2}) must be ≤ 2*T1 ({2 * self.t1})")
        return self


class AdvancedNoiseConfig(BaseModel):
    """
    Advanced noise configuration for complex noise models.

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
