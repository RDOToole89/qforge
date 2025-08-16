"""
Storage and Artifact Models

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
from typing import Any, Dict, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from pathlib import Path


class ArtifactRef(BaseModel):
    """
    Reference to a generated experiment artifact.
    
    Artifacts include plots, reports, raw data files, and any other
    outputs generated during experiment execution and analysis.
    """
    
    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True
    )
    
    kind: Literal[
        "histogram",
        "density_matrix", 
        "report",
        "raw_data",
        "analysis",
        "visualization",
        "other"
    ] = Field(
        default="other",
        description="Type of artifact for organization and processing"
    )
    
    path: str = Field(
        description="File path to the artifact (absolute or relative to results directory)"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata about the artifact"
    )
    
    # File characteristics
    file_size_bytes: Optional[int] = Field(
        default=None, ge=0,
        description="File size in bytes"
    )
    
    mime_type: Optional[str] = Field(
        default=None,
        description="MIME type of the file"
    )
    
    creation_timestamp: Optional[str] = Field(
        default=None,
        description="When the artifact was created"
    )
    
    # Content description
    title: Optional[str] = Field(
        default=None,
        description="Human-readable title for the artifact"
    )
    
    description: Optional[str] = Field(
        default=None,
        description="Detailed description of artifact contents"
    )
    
    # Access and permissions
    public: bool = Field(
        default=False,
        description="Whether artifact can be shared publicly"
    )
    
    publication_ready: bool = Field(
        default=False,
        description="Whether artifact meets publication quality standards"
    )


class StorageConfig(BaseModel):
    """
    Configuration for experiment result storage.
    
    Defines how and where experiment results, artifacts, and analysis
    outputs should be stored and organized.
    """
    
    # Base storage location
    base_directory: str = Field(
        description="Base directory for all experiment storage"
    )
    
    # Organization scheme
    use_date_organization: bool = Field(
        default=True,
        description="Organize results by date (YYYY/MM/DD structure)"
    )
    
    use_experiment_subdirs: bool = Field(
        default=True,
        description="Create subdirectories for each experiment"
    )
    
    # File naming
    filename_template: str = Field(
        default="{research_type}_{experiment_id}_{timestamp}",
        description="Template for generated filenames"
    )
    
    # Compression and archival
    compress_raw_data: bool = Field(
        default=False,
        description="Compress raw measurement data"
    )
    
    archive_old_results: bool = Field(
        default=False,
        description="Archive results older than retention period"
    )
    
    retention_days: Optional[int] = Field(
        default=None, ge=1,
        description="Days to retain results before archival"
    )
    
    # Backup and redundancy
    backup_enabled: bool = Field(
        default=False,
        description="Enable automatic backup of results"
    )
    
    backup_location: Optional[str] = Field(
        default=None,
        description="Location for backup storage"
    )


class DirectoryStructure(BaseModel):
    """
    Standard directory structure for experiment storage.
    
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
        """
        Generate appropriate path for given category and metadata.
        
        Args:
            base: Base storage directory
            category: Storage category (experiments, sweeps, etc.)
            **kwargs: Additional metadata for path generation
            
        Returns:
            Complete path for storage
        """
        path = base / getattr(self, category, category)
        
        # Add date organization if enabled
        if self.by_date and 'timestamp' in kwargs:
            from datetime import datetime
            if isinstance(kwargs['timestamp'], str):
                dt = datetime.fromisoformat(kwargs['timestamp'].replace('Z', '+00:00'))
            else:
                dt = kwargs['timestamp']
            path = path / dt.strftime("%Y/%m/%d")
        
        # Add research type organization if enabled
        if self.by_research_type and 'research_type' in kwargs:
            path = path / kwargs['research_type']
        
        # Add quantum state organization if enabled
        if self.by_quantum_state and 'state_type' in kwargs:
            path = path / kwargs['state_type'].lower()
            
        return path


class ResultManifest(BaseModel):
    """
    Manifest file for tracking experiment results and artifacts.
    
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
    experiments: Dict[str, ExperimentManifestEntry] = Field(
        default_factory=dict,
        description="Index of experiment results"
    )
    
    artifact_index: Dict[str, ArtifactRef] = Field(
        default_factory=dict,
        description="Index of all artifacts by path"
    )
    
    # Cleanup tracking
    archived_experiments: List[str] = Field(
        default_factory=list,
        description="List of archived experiment IDs"
    )
    
    orphaned_artifacts: List[str] = Field(
        default_factory=list,
        description="List of artifacts without associated experiments"
    )


class ExperimentManifestEntry(BaseModel):
    """Entry in the experiment manifest for a single experiment."""
    
    experiment_id: str = Field(description="Unique experiment identifier")
    timestamp: str = Field(description="When experiment was performed")
    research_type: Optional[str] = Field(default=None, description="Type of research")
    
    # File references
    result_file: str = Field(description="Path to main result file")
    artifacts: List[str] = Field(default_factory=list, description="Paths to artifact files")
    
    # Status
    status: str = Field(description="Current status of experiment results")
    archived: bool = Field(default=False, description="Whether results are archived")
    
    # Metrics
    file_count: int = Field(ge=0, description="Number of files for this experiment")
    total_size_bytes: int = Field(ge=0, description="Total size of all files")
    
    # Research metadata
    has_research_metrics: bool = Field(default=False, description="Whether structured decoherence metrics available")
    publication_ready: bool = Field(default=False, description="Whether results are publication ready")