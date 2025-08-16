"""
Version-Agnostic Experiment Validation and Creation System.

Unified system for validating and creating experiments using JSON Schema
validation with automatic version detection and schema evolution support.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid

try:
    import jsonschema
    from referencing import Registry, Resource
    from referencing.jsonschema import DRAFT7
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logging.warning("jsonschema not available - validation will be limited")

logger = logging.getLogger("QuantumExperiment.Validation")


class SchemaValidator:
    """
    Version-agnostic schema validator for experiments.
    
    Automatically detects schema versions and provides validation
    and experiment creation with proper version handling.
    """
    
    def __init__(self, schemas_root: Optional[Path] = None, version: Optional[str] = None):
        """
        Initialize the schema validator.
        
        Args:
            schemas_root: Path to schemas directory (auto-detected if None)
            version: Schema version to use (auto-detected if None)
        """
        self.schemas_root = self._find_schemas_root(schemas_root)
        self.version = version or self._detect_latest_version()
        self.registry = None
        
        if JSONSCHEMA_AVAILABLE:
            self.registry = self._build_registry()
            logger.info(f"Initialized schema validator for version {self.version}")
        else:
            logger.warning("JSON Schema validation not available - using fallback validation")
    
    def _find_schemas_root(self, schemas_root: Optional[Path]) -> Path:
        """Find the schemas directory automatically."""
        if schemas_root and schemas_root.exists():
            return Path(schemas_root)
        
        # Auto-detect from current location
        current = Path(__file__).parent
        while current.parent != current:
            schemas_dir = current / "schemas"
            if schemas_dir.exists():
                return schemas_dir
            current = current.parent
        
        raise ValueError("Could not locate schemas directory")
    
    def _detect_latest_version(self) -> str:
        """Detect the latest available schema version."""
        version_dirs = [d for d in self.schemas_root.iterdir() 
                       if d.is_dir() and d.name.startswith('v')]
        
        if not version_dirs:
            raise ValueError(f"No schema versions found in {self.schemas_root}")
        
        # Sort versions and get latest
        versions = sorted(version_dirs, key=lambda x: x.name)
        latest = versions[-1].name
        
        logger.info(f"Auto-detected latest schema version: {latest}")
        return latest
    
    def _build_registry(self) -> Optional[Registry]:
        """Build a registry of schemas for the current version."""
        if not JSONSCHEMA_AVAILABLE:
            return None
            
        registry = Registry()
        version_path = self.schemas_root / self.version
        
        if not version_path.exists():
            logger.error(f"Schema version {self.version} not found at {version_path}")
            return registry
        
        # Load all schema files for this version
        schema_count = 0
        for schema_file in version_path.rglob("*.schema.json"):
            try:
                with open(schema_file) as f:
                    schema = json.load(f)
                
                if "$id" in schema:
                    resource = Resource.from_contents(schema, default_specification=DRAFT7)
                    registry = registry.with_resource(schema["$id"], resource)
                    schema_count += 1
                    logger.debug(f"Loaded schema: {schema['$id']}")
                    
            except Exception as e:
                logger.error(f"Failed to load schema {schema_file}: {e}")
        
        logger.info(f"Built registry with {schema_count} schemas for {self.version}")
        return registry
    
    def validate(self, data: Dict[str, Any], schema_type: Optional[str] = None) -> bool:
        """
        Validate data against appropriate schema.
        
        Args:
            data: Data to validate
            schema_type: Specific schema type (auto-detected if None)
            
        Returns:
            True if valid, False otherwise
        """
        if not JSONSCHEMA_AVAILABLE:
            return self._fallback_validation(data)
        
        try:
            schema_id = self._detect_schema_type(data, schema_type)
            resolver = self.registry.resolver(schema_id)
            schema = resolver.lookup(schema_id).contents
            
            jsonschema.validate(
                instance=data,
                schema=schema,
                resolver=resolver,
                format_checker=jsonschema.draft7_format_checker
            )
            
            logger.debug(f"Validation successful for schema: {schema_id}")
            return True
            
        except jsonschema.ValidationError as e:
            logger.error(f"Validation failed: {e.message}")
            return False
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def get_validation_errors(self, data: Dict[str, Any], schema_type: Optional[str] = None) -> List[str]:
        """Get detailed validation errors."""
        if not JSONSCHEMA_AVAILABLE:
            return ["JSON Schema validation not available"]
        
        errors = []
        try:
            schema_id = self._detect_schema_type(data, schema_type)
            resolver = self.registry.resolver(schema_id)
            schema = resolver.lookup(schema_id).contents
            
            validator = jsonschema.Draft7Validator(
                schema=schema,
                resolver=resolver,
                format_checker=jsonschema.draft7_format_checker
            )
            
            for error in validator.iter_errors(data):
                path = " -> ".join(str(p) for p in error.absolute_path)
                errors.append(f"{path}: {error.message}")
                
        except Exception as e:
            errors.append(f"Validation setup failed: {e}")
        
        return errors
    
    def _detect_schema_type(self, data: Dict[str, Any], schema_type: Optional[str] = None) -> str:
        """Auto-detect the appropriate schema type for data."""
        if schema_type:
            return f"https://schemas.quantum-experiments.org/{self.version}/{schema_type}"
        
        # Auto-detection based on data structure
        if "experiment_metadata" in data:
            return f"https://schemas.quantum-experiments.org/{self.version}/experiment_spec"
        elif "circuit_metadata" in data:
            return f"https://schemas.quantum-experiments.org/{self.version}/execution_result"
        elif "asymmetry_index" in data:
            return f"https://schemas.quantum-experiments.org/{self.version}/structure_metrics"
        else:
            # Default to experiment_spec
            return f"https://schemas.quantum-experiments.org/{self.version}/experiment_spec"
    
    def _fallback_validation(self, data: Dict[str, Any]) -> bool:
        """Basic validation when jsonschema is not available."""
        try:
            # Basic structural validation
            if not isinstance(data, dict):
                return False
            
            # Check for basic required fields based on data type
            if "experiment_metadata" in data:
                metadata = data["experiment_metadata"]
                required = ["experiment_id", "name", "description"]
                return all(field in metadata for field in required)
            
            # Legacy format validation
            if "config" in data:
                config = data["config"]
                required = ["num_qubits", "shots"]
                return all(field in config for field in required)
            
            return True
            
        except Exception:
            return False
    
    def create_experiment(self, experiment_type: str, **kwargs) -> Dict[str, Any]:
        """
        Create a new experiment with automatic schema compliance.
        
        Args:
            experiment_type: Type of experiment to create
            **kwargs: Experiment parameters
            
        Returns:
            Schema-compliant experiment dictionary
        """
        factory_method = getattr(self, f"_create_{experiment_type}", None)
        if not factory_method:
            raise ValueError(f"Unknown experiment type: {experiment_type}")
        
        experiment = factory_method(**kwargs)
        
        # Validate the created experiment
        if not self.validate(experiment):
            errors = self.get_validation_errors(experiment)
            logger.warning(f"Created experiment has validation issues: {errors[:3]}")
        
        return experiment
    
    def _create_basic(self, name: str, description: str, **kwargs) -> Dict[str, Any]:
        """Create a basic experiment."""
        experiment_id = kwargs.get("experiment_id", str(uuid.uuid4())[:8])
        
        experiment = {
            "$schema": f"../../../{self.version}/core/experiment_spec.schema.json",
            "experiment_metadata": {
                "experiment_id": experiment_id,
                "name": name,
                "description": description,
                "phase": "planning",
                "created_timestamp": datetime.now().isoformat(),
                "tags": kwargs.get("tags", []),
                "difficulty_level": kwargs.get("difficulty_level", "beginner")
            },
            "quantum_configuration": {
                "num_qubits": kwargs.get("num_qubits", 2),
                "state_type": kwargs.get("state_type", "Bell"),
                "shots": kwargs.get("shots", 1024)
            },
            "noise_configuration": {
                "noise_enabled": kwargs.get("enable_noise", False)
            },
            "research_configuration": {
                "research_type": kwargs.get("research_type", "general"),
                "enable_research_metrics": kwargs.get("enable_research_metrics", False),
                "statistical_validation": kwargs.get("statistical_validation", True)
            },
            "provenance": {
                "created_by": "schema_validator",
                "creation_method": "basic_experiment",
                "framework_version": self.version,
                "schema_version": self.version
            }
        }
        
        # Add noise configuration if enabled
        if kwargs.get("enable_noise", False):
            experiment["noise_configuration"].update({
                "noise_type": kwargs.get("noise_type", "depolarizing"),
                "error_rate": kwargs.get("error_rate", 0.01)
            })
        
        return experiment
    
    def _create_structured_decoherence(self, name: str, **kwargs) -> Dict[str, Any]:
        """Create a structured decoherence experiment."""
        kwargs.setdefault("description", f"Structured decoherence pathway analysis")
        kwargs.setdefault("difficulty_level", "research")
        kwargs.setdefault("enable_noise", True)
        kwargs.setdefault("research_type", "structured_decoherence")
        kwargs.setdefault("enable_research_metrics", True)
        kwargs.setdefault("tags", ["structured_decoherence", "research"])
        
        experiment = self._create_basic(name, **kwargs)
        
        # Add structured decoherence specific configuration
        experiment["research_configuration"].update({
            "null_models": ["independent_bitflip", "independent_pauli", "readout_confusion"],
            "bootstrap_samples": 1000
        })
        
        experiment["analysis_configuration"] = {
            "enabled_metrics": [
                "shannon_entropy",
                "kl_divergence",
                "total_variation_distance",
                "mutual_information",
                "qubit_wise_bias"
            ],
            "analysis_parameters": {
                "precision_threshold": 0.001,
                "confidence_level": 0.95
            }
        }
        
        return experiment
    
    def convert_legacy(self, legacy_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert legacy experiment format to current schema version.
        
        Args:
            legacy_config: Legacy experiment configuration
            
        Returns:
            Current schema version experiment
        """
        # Extract basic information
        name = legacy_config.get("name", "Converted Experiment")
        description = legacy_config.get("description", "Converted from legacy format")
        
        # Extract config section if present
        config = legacy_config.get("config", legacy_config)
        
        # Build current format
        return self._create_basic(
            name=name,
            description=description,
            experiment_id=legacy_config.get("id", str(uuid.uuid4())[:8]),
            num_qubits=config.get("num_qubits", 3),
            state_type=config.get("state_type", "GHZ"),
            shots=config.get("shots", 1024),
            enable_noise=config.get("noise_enabled", False),
            noise_type=config.get("noise_type", "depolarizing"),
            error_rate=config.get("error_rate", 0.01),
            research_type=legacy_config.get("research_type", "general"),
            enable_research_metrics=config.get("enable_research_metrics", False),
            difficulty_level=legacy_config.get("difficulty", "intermediate")
        )
    
    def get_available_versions(self) -> List[str]:
        """Get list of available schema versions."""
        version_dirs = [d.name for d in self.schemas_root.iterdir() 
                       if d.is_dir() and d.name.startswith('v')]
        return sorted(version_dirs)
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the current schema version."""
        return {
            "version": self.version,
            "schemas_root": str(self.schemas_root),
            "available_versions": self.get_available_versions(),
            "jsonschema_available": JSONSCHEMA_AVAILABLE
        }


# Convenience functions
def create_validator(version: Optional[str] = None) -> SchemaValidator:
    """Create a schema validator instance."""
    return SchemaValidator(version=version)


def validate_experiment(data: Dict[str, Any], version: Optional[str] = None) -> bool:
    """Validate an experiment using the current schema version."""
    validator = create_validator(version)
    return validator.validate(data)


def create_experiment(experiment_type: str, version: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Create a new experiment with schema validation."""
    validator = create_validator(version)
    return validator.create_experiment(experiment_type, **kwargs)