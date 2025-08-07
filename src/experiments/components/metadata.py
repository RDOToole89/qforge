"""
Metadata management for experiments and components.

Provides structured metadata tracking for experiments and their components,
including versioning, timestamps, and configuration information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
import json


@dataclass
class ComponentMetadata:
    """Metadata for an experiment component."""

    name: str
    version: str
    component_type: str
    created_at: datetime
    description: str = ""
    author: str = ""
    tags: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            "name": self.name,
            "version": self.version,
            "component_type": self.component_type,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "author": self.author,
            "tags": self.tags,
            "parameters": self.parameters
        }

    def to_json(self) -> str:
        """Convert metadata to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class ExperimentMetadata:
    """Metadata for a complete experiment."""

    name: str
    experiment_id: str
    created_at: datetime
    description: str = ""
    category: str = "custom"
    difficulty: str = "intermediate"
    author: str = ""
    version: str = "1.0.0"
    tags: List[str] = field(default_factory=list)
    research_type: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            "name": self.name,
            "experiment_id": self.experiment_id,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "author": self.author,
            "version": self.version,
            "tags": self.tags,
            "research_type": self.research_type,
            "parameters": self.parameters
        }

    def to_json(self) -> str:
        """Convert metadata to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExperimentMetadata':
        """Create metadata from dictionary."""
        created_at = datetime.fromisoformat(data["created_at"]) if isinstance(data["created_at"], str) else data["created_at"]

        return cls(
            name=data["name"],
            experiment_id=data["experiment_id"],
            created_at=created_at,
            description=data.get("description", ""),
            category=data.get("category", "custom"),
            difficulty=data.get("difficulty", "intermediate"),
            author=data.get("author", ""),
            version=data.get("version", "1.0.0"),
            tags=data.get("tags", []),
            research_type=data.get("research_type"),
            parameters=data.get("parameters", {})
        )
