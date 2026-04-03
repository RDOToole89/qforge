"""Provenance Model."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Provenance(BaseModel):
    """Complete provenance information for experiment reproducibility.

    Captures all information needed to exactly reproduce an experiment,
    following research best practices for computational reproducibility.
    """

    schema_version: str = Field(default="1.0.0", description="Provenance schema version")
    timestamp: str = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Provenance record creation timestamp",
    )

    software_versions: dict[str, str] = Field(
        default_factory=dict,
        description="Versions of all software dependencies",
    )

    host_info: dict[str, str] = Field(default_factory=dict, description="Host system information")

    git_sha: str | None = Field(
        default=None,
        description="Git commit SHA for exact code version",
    )

    rng_seed: int | None = Field(
        default=None,
        description="Random number generator seed used",
    )

    simulator_info: dict[str, Any] = Field(
        default_factory=dict,
        description="Quantum simulator configuration and metadata",
    )

    transpilation_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Circuit transpilation details and optimizations",
    )

    execution_time_seconds: float | None = Field(
        default=None,
        ge=0.0,
        description="Total execution time in seconds",
    )

    memory_usage_mb: float | None = Field(
        default=None,
        ge=0.0,
        description="Peak memory usage in megabytes",
    )
