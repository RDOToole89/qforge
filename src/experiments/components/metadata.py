"""
Schema-aligned metadata management for experiments and components.

Built directly from the actual schema definitions rather than legacy concepts.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
import json


@dataclass
class ExperimentMetadata:
    """
    Experiment metadata based on the actual experiment_spec schema.
    
    Maps directly to schema fields rather than legacy concepts.
    """
    
    # Core schema fields
    experiment_id: str
    state_type: str = "GHZ"
    n_qubits: int = 3
    shots: int = 1024
    noise_model: Optional[str] = None
    error_rate: Optional[float] = None
    seed: Optional[int] = None
    engine_config_hash: str = "default"
    
    # Research context (required by schema)
    research_phase: str = "structure_validation"
    research_hypothesis: str = ""
    research_notes: str = ""
    
    # Component metadata (not in schema but useful for components)
    name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_schema_dict(self) -> Dict[str, Any]:
        """Convert to experiment_spec schema format."""
        data = {
            "schema_version": "1.0",
            "experiment_id": self.experiment_id,
            "state_type": self.state_type,
            "n_qubits": self.n_qubits,
            "shots": self.shots,
            "engine_config_hash": self.engine_config_hash,
            "research": {
                "phase": self.research_phase,
                "hypothesis": self.research_hypothesis,
                "notes": self.research_notes
            }
        }
        
        # Add optional fields if they exist
        if self.noise_model is not None:
            data["noise_model"] = self.noise_model
        if self.error_rate is not None:
            data["error_rate"] = self.error_rate
        if self.seed is not None:
            data["seed"] = self.seed
            
        return data
    
    def to_component_dict(self) -> Dict[str, Any]:
        """Convert to component metadata format (includes non-schema fields)."""
        return {
            "name": self.name,
            "experiment_id": self.experiment_id,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags,
            "quantum_config": {
                "state_type": self.state_type,
                "n_qubits": self.n_qubits,
                "shots": self.shots,
                "noise_model": self.noise_model,
                "error_rate": self.error_rate,
                "seed": self.seed
            },
            "research": {
                "phase": self.research_phase,
                "hypothesis": self.research_hypothesis,
                "notes": self.research_notes
            }
        }

    @classmethod
    def from_schema_dict(cls, data: Dict[str, Any]) -> 'ExperimentMetadata':
        """Create from experiment_spec schema format."""
        research = data.get("research", {})
        
        return cls(
            experiment_id=data["experiment_id"],
            state_type=data["state_type"],
            n_qubits=data["n_qubits"],
            shots=data["shots"],
            noise_model=data.get("noise_model"),
            error_rate=data.get("error_rate"),
            seed=data.get("seed"),
            engine_config_hash=data.get("engine_config_hash", "default"),
            research_phase=research.get("phase", "structure_validation"),
            research_hypothesis=research.get("hypothesis", ""),
            research_notes=research.get("notes", ""),
            name=f"Experiment {data['experiment_id']}",
            description="Generated from schema"
        )


@dataclass
class ComponentMetadata:
    """
    Simple component metadata for internal component system use.
    
    This is for the component framework itself, not tied to schemas.
    """
    
    name: str
    component_type: str
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    description: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "component_type": self.component_type,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "parameters": self.parameters
        }