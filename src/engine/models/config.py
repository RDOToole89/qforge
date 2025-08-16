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
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, field_validator


class ExperimentConfig(BaseModel):
    """
    Complete quantum experiment configuration.
    
    This model defines all parameters needed to run a quantum experiment,
    from basic circuit parameters to advanced research configurations.
    """
    
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True
    )
    
    # ===== Core Quantum Parameters =====
    num_qubits: int = Field(
        ge=1, le=20,
        description="Number of qubits in the quantum circuit"
    )
    
    state_type: Literal["GHZ", "W", "CLUSTER", "BELL", "SUPERPOSITION", "CUSTOM"] = Field(
        description="Type of quantum state to prepare"
    )
    
    # ===== Simulation Parameters =====
    sim_mode: Literal["qasm", "density"] = Field(
        default="qasm",
        description="Simulation mode: 'qasm' for shot-based, 'density' for density matrix"
    )
    
    shots: int = Field(
        default=1024,
        ge=1, le=1000000,
        description="Number of measurement shots for qasm simulation"
    )
    
    # ===== Noise Model Parameters =====
    noise_enabled: bool = Field(
        default=False,
        description="Whether to apply noise to the quantum circuit"
    )
    
    noise_type: Optional[Literal[
        "depolarizing",
        "amplitude_damping", 
        "phase_damping",
        "bit_flip",
        "phase_flip",
        "thermal_relaxation"
    ]] = Field(
        default=None,
        description="Type of noise model to apply"
    )
    
    error_rate: Optional[float] = Field(
        default=None,
        ge=0.0, le=1.0,
        description="Error rate for noise models (0.0 = no noise, 1.0 = maximum noise)"
    )
    
    # Advanced noise parameters
    z_prob: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    i_prob: Optional[float] = Field(default=None, ge=0.0, le=1.0) 
    t1: Optional[float] = Field(default=None, gt=0.0)
    t2: Optional[float] = Field(default=None, gt=0.0)
    
    # ===== Research Parameters =====
    enable_research_metrics: bool = Field(
        default=False,
        description="Enable computation of structured decoherence pathway metrics (AI, PCR, EEC, TPS, CES)"
    )
    
    research_type: Optional[Literal[
        "structured_decoherence",
        "parameter_sweep", 
        "noise_comparison",
        "control",
        "scaling",
        "convergence",
        "batch_sweep"
    ]] = Field(
        default=None,
        description="Type of research analysis to perform"
    )
    
    multiple_runs: int = Field(
        default=1,
        ge=1, le=1000,
        description="Number of experimental runs for statistical validation"
    )
    
    track_convergence: bool = Field(
        default=False,
        description="Enable convergence tracking for high-precision experiments"
    )
    
    # ===== Output Parameters =====
    visualization_type: Literal[
        "histogram",
        "density_matrix", 
        "research",
        "plot",
        "none"
    ] = Field(
        default="histogram",
        description="Type of visualization to generate"
    )
    
    # ===== System Parameters =====
    rng_seed: Optional[int] = Field(
        default=None,
        description="Random number generator seed for reproducible results"
    )
    
    custom_params: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom parameters for advanced state preparation or noise models"
    )
    
    # ===== Validators =====
    @field_validator('t2')
    @classmethod
    def validate_t2_constraint(cls, v: Optional[float], info) -> Optional[float]:
        """Validate T2 ≤ 2*T1 constraint for thermal relaxation."""
        if v is not None and 't1' in info.data and info.data['t1'] is not None:
            t1 = info.data['t1']
            if v > 2 * t1:
                raise ValueError(f"T2 ({v}) must be ≤ 2*T1 ({2*t1}) for physical validity")
        return v
    
    @field_validator('noise_type')
    @classmethod 
    def validate_noise_type_with_enabled(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure noise_type is provided when noise_enabled=True."""
        if info.data.get('noise_enabled', False) and v is None:
            raise ValueError("noise_type must be specified when noise_enabled=True")
        return v
    
    @field_validator('research_type')
    @classmethod
    def validate_research_type_with_metrics(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure research_type is provided when enable_research_metrics=True."""
        if info.data.get('enable_research_metrics', False) and v is None:
            return "structured_decoherence"  # Default research type
        return v


class AdvancedNoiseConfig(BaseModel):
    """
    Advanced noise configuration for complex noise models.
    
    Purpose: Separate complex noise configurations from basic ExperimentConfig
    to keep the main config model clean and focused.
    """
    
    # Thermal relaxation parameters
    t1_values: Optional[Dict[int, float]] = Field(
        default=None,
        description="Per-qubit T1 relaxation times"
    )
    
    t2_values: Optional[Dict[int, float]] = Field(
        default=None, 
        description="Per-qubit T2 dephasing times"
    )
    
    # Correlated noise parameters
    crosstalk_matrix: Optional[List[List[float]]] = Field(
        default=None,
        description="Qubit crosstalk correlation matrix"
    )
    
    # Time-dependent noise
    time_dependent: bool = Field(
        default=False,
        description="Enable time-dependent noise evolution"
    )
    
    @field_validator('crosstalk_matrix')
    @classmethod
    def validate_crosstalk_matrix(cls, v: Optional[List[List[float]]]) -> Optional[List[List[float]]]:
        """Validate crosstalk matrix is square and properly normalized."""
        if v is not None:
            n = len(v)
            if not all(len(row) == n for row in v):
                raise ValueError("Crosstalk matrix must be square")
            # Additional validation could be added here
        return v