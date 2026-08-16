"""Experiment Metadata Model."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ExperimentMetadata(BaseModel):
    """Basic experiment identification and context."""

    experiment_id: str = Field(description="Unique experiment identifier")
    timestamp: str = Field(description="When experiment was performed")
    framework_version: str = Field(description="Quantum experiment framework version")

    experiment_type: str | None = Field(
        default=None, description="Experiment category used for grouping and storage"
    )

    experiment_description: str | None = Field(
        default=None,
        description="Human-readable description of experiment purpose",
    )
