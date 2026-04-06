"""Storage and Artifact Models.

Purpose: Define models for file storage, artifact management, and result persistence.
These models handle the organization and referencing of all experiment outputs
including plots, reports, raw data, and analysis results.

Key Features:
- Artifact reference management
- Storage configuration
- File path organization
- Metadata preservation

Dependencies: Pydantic only
Used by: Engine storage systems, visualization, reporting
"""

from __future__ import annotations

import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ArtifactRef(BaseModel):
    """Reference to a generated experiment artifact.

    Artifacts include plots, reports, raw data files, and any other
    outputs generated during experiment execution and analysis.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    kind: Literal[
        "histogram",
        "density_matrix",
        "correlation",
        "circuit",
        "metrics_summary",
        "bloch_sphere",
        "sweep_line",
        "comparison",
        "report",
        "raw_data",
        "analysis",
        "visualization",
        "other",
    ] = Field(default="other", description="Type of artifact for organization and processing")

    path: str = Field(
        description="File path to the artifact (absolute or relative to results directory)"
    )

    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata about the artifact"
    )

    # File characteristics
    file_size_bytes: int | None = Field(default=None, ge=0, description="File size in bytes")

    mime_type: str | None = Field(default=None, description="MIME type of the file")

    creation_timestamp: str | None = Field(
        default=None, description="When the artifact was created"
    )

    # Content description
    title: str | None = Field(default=None, description="Human-readable title for the artifact")

    description: str | None = Field(
        default=None, description="Detailed description of artifact contents"
    )

    # Access and permissions
    public: bool = Field(default=False, description="Whether artifact can be shared publicly")

    publication_ready: bool = Field(
        default=False,
        description="Whether artifact meets publication quality standards",
    )

    @classmethod
    def from_file(
        cls,
        file_path: str | Path,
        *,
        kind: Literal[
            "histogram",
            "density_matrix",
            "correlation",
            "circuit",
            "report",
            "raw_data",
            "analysis",
            "visualization",
            "other",
        ] = "other",
        title: str | None = None,
        description: str | None = None,
        public: bool = False,
        publication_ready: bool = False,
        metadata: dict[str, Any] | None = None,
    ) -> ArtifactRef:
        """Create an ArtifactRef by inspecting an existing file on disk.

        Populates size, MIME type, and creation timestamp when available.
        """
        p = Path(file_path).expanduser().resolve()
        size = p.stat().st_size if p.exists() and p.is_file() else None
        mime, _ = mimetypes.guess_type(str(p))
        ctime = None
        try:
            if p.exists():
                ctime = datetime.fromtimestamp(p.stat().st_ctime).isoformat()
        except Exception:
            ctime = None

        return cls(
            kind=kind,
            path=str(p),
            metadata=metadata or {},
            file_size_bytes=size,
            mime_type=mime,
            creation_timestamp=ctime,
            title=title,
            description=description,
            public=public,
            publication_ready=publication_ready,
        )

    @field_validator("path")
    @classmethod
    def _normalize_path(cls, v: str) -> str:
        """Normalize path to avoid surprises ('./', duplicated separators, etc.)."""
        if not v:
            raise ValueError("path must be a non-empty string")
        return str(Path(v).expanduser())

    def refresh_file_stats(self) -> ArtifactRef:
        """Refresh file_size_bytes, mime_type, and creation_timestamp from disk.

        Safe to call even if the file is missing.
        """
        p = Path(self.path).expanduser()
        size = p.stat().st_size if p.exists() and p.is_file() else None
        mime, _ = mimetypes.guess_type(str(p))
        ctime = None
        try:
            if p.exists():
                ctime = datetime.fromtimestamp(p.stat().st_ctime).isoformat()
        except Exception:
            ctime = None

        self.file_size_bytes = size
        self.mime_type = mime
        self.creation_timestamp = ctime
        return self


class StorageConfig(BaseModel):
    """Configuration for experiment result storage.

    Defines how and where experiment results, artifacts, and analysis
    outputs should be stored and organized.
    """

    # Base storage location
    base_directory: str = Field(description="Base directory for all experiment storage")

    # Organization scheme
    use_date_organization: bool = Field(
        default=True, description="Organize results by date (YYYY/MM/DD structure)"
    )

    use_experiment_subdirs: bool = Field(
        default=True, description="Create subdirectories for each experiment"
    )

    # File naming
    filename_template: str = Field(
        default="{research_type}_{experiment_id}_{timestamp}",
        description="Template for generated filenames",
    )

    # Compression and archival
    compress_raw_data: bool = Field(default=False, description="Compress raw measurement data")

    archive_old_results: bool = Field(
        default=False, description="Archive results older than retention period"
    )

    retention_days: int | None = Field(
        default=None, ge=1, description="Days to retain results before archival"
    )

    # Backup and redundancy
    backup_enabled: bool = Field(default=False, description="Enable automatic backup of results")

    backup_location: str | None = Field(default=None, description="Location for backup storage")

    @field_validator("base_directory")
    @classmethod
    def _validate_base_dir(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("base_directory must be a non-empty path")
        return str(Path(v).expanduser())

    @model_validator(mode="after")
    def _validate_backup_and_retention(self) -> StorageConfig:
        # If backup is enabled, backup_location must be present
        if self.backup_enabled and not self.backup_location:
            raise ValueError("backup_location must be set when backup_enabled=True")
        # If retention_days is set, archival should be enabled
        if self.retention_days is not None and not self.archive_old_results:
            raise ValueError("retention_days requires archive_old_results=True")
        return self

    # ---------- Helpers (engine-friendly) ----------

    def base_path(self) -> Path:
        """Return the normalized base storage Path (created if missing)."""
        p = Path(self.base_directory).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p

    def render_filename(
        self,
        *,
        experiment_id: str,
        research_type: str | None,
        timestamp: str,
    ) -> str:
        """Render a filename using the template (without extension)."""
        safe_research = (research_type or "experiment").replace(" ", "_")
        return self.filename_template.format(
            research_type=safe_research,
            experiment_id=experiment_id,
            timestamp=timestamp.replace(":", "-"),
        )

    def ensure_directory(self, path: Path) -> Path:
        """Create a directory if it doesn't exist and return it."""
        path.mkdir(parents=True, exist_ok=True)
        return path


class DirectoryStructure(BaseModel):
    """Standard directory structure for experiment storage.

    Defines the organization of experiment files for consistency
    and easy navigation.
    """

    # Main directories
    experiments: str = Field(default="experiments", description="Individual experiment results")
    sweeps: str = Field(default="sweeps", description="Parameter sweep results")
    campaigns: str = Field(default="campaigns", description="Long-term research campaigns")
    analysis: str = Field(default="analysis", description="Cross-experiment analysis")
    visualizations: str = Field(default="visualizations", description="Generated plots and figures")
    reports: str = Field(default="reports", description="Generated reports and summaries")
    exports: str = Field(default="exports", description="Publication-ready exports")

    # Subdirectory organization
    by_date: bool = Field(default=True, description="Use date-based subdirectories")
    by_research_type: bool = Field(default=True, description="Use research-type subdirectories")
    by_quantum_state: bool = Field(default=False, description="Use quantum-state subdirectories")

    def get_path(self, base: Path, category: str, **kwargs) -> Path:
        """Generate appropriate path for given category and metadata.

        Args:
            base: Base storage directory
            category: Storage category (experiments, sweeps, etc.)
            **kwargs: Additional metadata for path generation

        Returns:
            Complete path for storage
        """
        path = base / getattr(self, category, category)

        # Add date organization if enabled
        if self.by_date and "timestamp" in kwargs and kwargs["timestamp"]:
            ts = kwargs["timestamp"]
            if isinstance(ts, str):
                # Robust ISO parsing; allow trailing 'Z'
                ts = ts.replace("Z", "+00:00")
                dt = datetime.fromisoformat(ts)
            else:
                dt = ts
            path = path / dt.strftime("%Y/%m/%d")

        # Add research type organization if enabled
        if self.by_research_type and "research_type" in kwargs and kwargs["research_type"]:
            path = path / str(kwargs["research_type"]).replace(" ", "_")

        # Add quantum state organization if enabled
        if self.by_quantum_state and "state_type" in kwargs and kwargs["state_type"]:
            path = path / str(kwargs["state_type"]).lower()

        return path

    # Convenience helper
    def experiment_dir(
        self,
        storage: StorageConfig,
        *,
        category: Literal["experiments", "sweeps", "campaigns"] = "experiments",
        experiment_id: str,
        timestamp: str,
        research_type: str | None = None,
        state_type: str | None = None,
    ) -> Path:
        """Build and ensure the directory path for an experiment-like entity."""
        base = storage.base_path()
        path = self.get_path(
            base,
            category,
            timestamp=timestamp,
            research_type=research_type,
            state_type=state_type,
        )
        if storage.use_experiment_subdirs:
            path = path / experiment_id
        return storage.ensure_directory(path)


class ResultManifest(BaseModel):
    """Manifest file for tracking experiment results and artifacts.

    This provides an index of all results and artifacts for efficient
    searching, organization, and cleanup.
    """

    # Manifest metadata
    manifest_version: str = Field(default="1.0", description="Manifest format version")
    created: str = Field(description="When manifest was created")
    last_updated: str = Field(description="When manifest was last updated")

    # Result tracking
    experiment_count: int = Field(ge=0, description="Number of experiments tracked")
    total_artifacts: int = Field(ge=0, description="Total number of artifacts")
    total_size_bytes: int = Field(ge=0, description="Total storage size used")

    # Organization
    experiments: dict[str, ExperimentManifestEntry] = Field(
        default_factory=dict, description="Index of experiment results"
    )

    artifact_index: dict[str, ArtifactRef] = Field(
        default_factory=dict, description="Index of all artifacts by path"
    )

    # Cleanup tracking
    archived_experiments: list[str] = Field(
        default_factory=list, description="List of archived experiment IDs"
    )

    orphaned_artifacts: list[str] = Field(
        default_factory=list,
        description="List of artifacts without associated experiments",
    )

    # ---------- Manifest helpers ----------

    def register_experiment(
        self,
        entry: ExperimentManifestEntry,
        *,
        artifacts: list[ArtifactRef] | None = None,
    ) -> None:
        """Add/update an experiment entry and fold in its artifacts.

        Safely updates counters and totals.
        """
        self.experiments[entry.experiment_id] = entry
        self.experiment_count = len(self.experiments)

        if artifacts:
            for ref in artifacts:
                # Normalize and store
                ref = ref.refresh_file_stats()
                self.artifact_index[ref.path] = ref

        self._recompute_totals()
        self.last_updated = datetime.now().isoformat()

    def register_artifact(self, ref: ArtifactRef) -> None:
        """Add or update a single artifact index entry."""
        self.artifact_index[ref.path] = ref.refresh_file_stats()
        self._recompute_totals()
        self.last_updated = datetime.now().isoformat()

    def mark_archived(self, experiment_id: str, archived: bool = True) -> None:
        """Set archived flag and maintain archived_experiments index."""
        if experiment_id in self.experiments:
            self.experiments[experiment_id].archived = archived
            if archived and experiment_id not in self.archived_experiments:
                self.archived_experiments.append(experiment_id)
            elif not archived and experiment_id in self.archived_experiments:
                self.archived_experiments.remove(experiment_id)
            self.last_updated = datetime.now().isoformat()

    def _recompute_totals(self) -> None:
        """Recompute total_artifacts and total_size_bytes from artifact_index."""
        self.total_artifacts = len(self.artifact_index)
        total = 0
        for ref in self.artifact_index.values():
            if ref.file_size_bytes is not None:
                total += int(ref.file_size_bytes)
        self.total_size_bytes = total


class ExperimentManifestEntry(BaseModel):
    """Entry in the experiment manifest for a single experiment."""

    experiment_id: str = Field(description="Unique experiment identifier")
    timestamp: str = Field(description="When experiment was performed")
    research_type: str | None = Field(default=None, description="Type of research")

    # File references
    result_file: str = Field(description="Path to main result file")
    artifacts: list[str] = Field(default_factory=list, description="Paths to artifact files")

    # Status
    status: str = Field(description="Current status of experiment results")
    archived: bool = Field(default=False, description="Whether results are archived")

    # Metrics
    file_count: int = Field(ge=0, description="Number of files for this experiment")
    total_size_bytes: int = Field(ge=0, description="Total size of all files")

    # Research metadata
    has_research_metrics: bool = Field(
        default=False, description="Whether structured decoherence metrics available"
    )
    publication_ready: bool = Field(
        default=False, description="Whether results are publication ready"
    )

    @field_validator("result_file")
    @classmethod
    def _normalize_result_path(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("result_file must be a valid path string")
        return str(Path(v).expanduser())

    @field_validator("artifacts")
    @classmethod
    def _normalize_artifact_paths(cls, v: list[str]) -> list[str]:
        return [str(Path(p).expanduser()) for p in v]
