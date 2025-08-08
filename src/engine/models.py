"""Pydantic models for engine configs and results (Phase 1).

These are the source of truth for JSON schemas.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class ArtifactRef(BaseModel):
    kind: Literal["histogram", "density_matrix", "hypergraph", "report", "other"] = "other"
    path: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Provenance(BaseModel):
    schema_version: str = "1.0.0"
    timestamp: str
    software_versions: Dict[str, str] = Field(default_factory=dict)
    host_info: Dict[str, str] = Field(default_factory=dict)
    git_sha: Optional[str] = None
    rng_seed: Optional[int] = None
    simulator_info: Dict[str, Any] = Field(default_factory=dict)
    transpilation_summary: Dict[str, Any] = Field(default_factory=dict)


class ExperimentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    num_qubits: int
    state_type: Literal["GHZ", "W", "CLUSTER", "BELL", "SUPERPOSITION", "CUSTOM"]
    sim_mode: Literal["qasm", "density"] = "qasm"
    shots: int = 1024

    noise_enabled: bool = False
    noise_type: Optional[Literal[
        "depolarizing", "amplitude_damping", "phase_damping", "bit_flip", "phase_flip", "thermal_relaxation"
    ]] = None
    error_rate: Optional[float] = None

    rng_seed: Optional[int] = None
    custom_params: Optional[Dict[str, Any]] = None


class ExperimentResult(BaseModel):
    model_config = ConfigDict(extra="allow")

    analysis: Dict[str, Any]
    metrics: Dict[str, Any]
    artifacts: List[ArtifactRef] = Field(default_factory=list)
    provenance: Provenance
    config_hash: str
    timestamp: str


class SweepManifest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    base_preset: Optional[str] = None
    base_config: Optional[ExperimentConfig] = None
    parameter_ranges: Dict[str, List[Any]]
    runs_per_config: int = 1
    rng_seed: Optional[int] = None
