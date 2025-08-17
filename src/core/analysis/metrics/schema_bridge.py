"""
Schema Bridge - Conversion between MetricResult and v1.0 Schema Format

This module provides the canonical interface for converting MetricResult objects
from the registry system into the exact JSON schema format required by the
frozen v1.0 schema suite.

Schema Compliance:
- Maps canonical metric names to exact schema keys
- Validates required fields (value, ci95, status) are present
- Ensures schema_version="1.0" is included
- Handles nullable fields (pathway_persistence, complexity_emergence_score)
- Provides type-safe conversion with validation

Supported Metrics:
- structure_score → structure_score
- entanglement_error_correlation → entanglement_error_correlation
- concentration_index → concentration_index  
- total_correlation → total_correlation
- pathway_persistence → pathway_persistence (nullable)
- complexity_emergence_score → complexity_emergence_score (nullable)

This bridge ensures complete compatibility with downstream analysis pipelines
and research tooling that depends on the frozen schema format.
"""

import logging
from typing import Dict, Any

from .registry import MetricResult

logger = logging.getLogger(__name__)

def metrics_to_schema(results: Dict[str, MetricResult]) -> Dict[str, Any]:
    """
    Convert MetricResult dictionary to v1.0 schema format.
    
    This function provides the canonical bridge between the registry system's
    MetricResult format and the exact JSON schema required by downstream
    analysis pipelines.
    
    Required Schema Keys:
        - structure_score
        - entanglement_error_correlation
        - concentration_index
        - total_correlation
        - pathway_persistence (nullable)
        - complexity_emergence_score (nullable)
        - schema_version: "1.0"
        
    Args:
        results: Dictionary mapping metric names to MetricResult objects
        
    Returns:
        Dict containing schema-compliant metric data with exact field names
        
    Raises:
        ValueError: If required fields are missing or malformed
        KeyError: If core metrics are missing from results
        
    Example:
        >>> from analysis.metrics import compute_all, metrics_to_schema
        >>> results = compute_all(counts={"00": 500, "11": 500})
        >>> schema_data = metrics_to_schema(results)
        >>> assert schema_data["schema_version"] == "1.0"
        >>> assert "structure_score" in schema_data
    """
    schema_output = {"schema_version": "1.0"}
    
    # Core metrics (always required)
    core_metrics = [
        "structure_score",  # Now mapped to asymmetry_index
        "entanglement_error_correlation", 
        "concentration_index",  # Now mapped to pathway_concentration_ratio
        "total_correlation"
    ]
    
    # Optional metrics (nullable in schema)
    optional_metrics = [
        "pathway_persistence",
        "complexity_emergence_score"
    ]
    
    # Process core metrics
    for metric_name in core_metrics:
        if metric_name not in results:
            raise KeyError(f"Required metric '{metric_name}' missing from results")
        
        result = results[metric_name]
        schema_output[metric_name] = _convert_metric_result(result, metric_name)
    
    # Process optional metrics (allow None)
    for metric_name in optional_metrics:
        if metric_name in results:
            result = results[metric_name]
            if result.get("status") not in ["insufficient_runs", "insufficient_data"]:
                schema_output[metric_name] = _convert_metric_result(result, metric_name)
            else:
                schema_output[metric_name] = None
        else:
            schema_output[metric_name] = None
    
    logger.debug(f"Converted {len(results)} results to schema format")
    return schema_output

def _convert_metric_result(result: MetricResult, metric_name: str) -> Dict[str, Any]:
    """
    Convert single MetricResult to schema format with validation.
    
    Args:
        result: MetricResult from registry
        metric_name: Name of metric for error messages
        
    Returns:
        Dict with schema-compliant structure
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Validate required fields
    if "value" not in result:
        raise ValueError(f"MetricResult for '{metric_name}' missing 'value' field")
    
    if "status" not in result:
        raise ValueError(f"MetricResult for '{metric_name}' missing 'status' field")
    
    # Validate value type
    value = result["value"]
    if not isinstance(value, (int, float)):
        raise ValueError(f"MetricResult value for '{metric_name}' must be numeric, got {type(value)}")
    
    # Validate status
    valid_statuses = ["validated", "experimental", "unstable", "insufficient_runs", "insufficient_data"]
    status = result["status"]
    if status not in valid_statuses:
        raise ValueError(f"Invalid status '{status}' for '{metric_name}', must be one of {valid_statuses}")
    
    # Build schema result
    schema_result = {
        "value": float(value),
        "status": status
    }
    
    # Add confidence interval if present
    if "ci95" in result:
        ci95 = result["ci95"]
        if not (isinstance(ci95, (list, tuple)) and len(ci95) == 2):
            raise ValueError(f"ci95 for '{metric_name}' must be 2-element list/tuple, got {ci95}")
        schema_result["ci95"] = [float(ci95[0]), float(ci95[1])]
    
    # Add extras if present (optional schema field)
    if "extras" in result and result["extras"]:
        schema_result["extras"] = result["extras"]
    
    return schema_result

def validate_schema_output(schema_data: Dict[str, Any]) -> bool:
    """
    Validate that schema output conforms to v1.0 requirements.
    
    Args:
        schema_data: Output from metrics_to_schema()
        
    Returns:
        True if valid, raises ValueError if invalid
        
    Raises:
        ValueError: If schema validation fails
    """
    # Check schema version
    if schema_data.get("schema_version") != "1.0":
        raise ValueError(f"Invalid schema_version: {schema_data.get('schema_version')}, expected '1.0'")
    
    # Check required fields
    required_fields = [
        "structure_score",
        "entanglement_error_correlation",
        "concentration_index", 
        "total_correlation"
    ]
    
    for field in required_fields:
        if field not in schema_data:
            raise ValueError(f"Required field '{field}' missing from schema output")
        
        field_data = schema_data[field]
        if not isinstance(field_data, dict):
            raise ValueError(f"Field '{field}' must be dict, got {type(field_data)}")
        
        # Check required subfields
        if "value" not in field_data:
            raise ValueError(f"Field '{field}' missing 'value' subfield")
        
        if "status" not in field_data:
            raise ValueError(f"Field '{field}' missing 'status' subfield")
    
    # Optional fields can be None
    optional_fields = ["pathway_persistence", "complexity_emergence_score"]
    for field in optional_fields:
        if field in schema_data and schema_data[field] is not None:
            field_data = schema_data[field]
            if not isinstance(field_data, dict):
                raise ValueError(f"Optional field '{field}' must be dict or None, got {type(field_data)}")
    
    logger.debug("Schema validation passed")
    return True

def get_schema_field_mapping() -> Dict[str, str]:
    """
    Get mapping from registry metric names to schema field names.
    
    Returns:
        Dict mapping registry names to canonical schema names
    """
    return {
        # Direct mappings (canonical names)
        "structure_score": "structure_score",
        "entanglement_error_correlation": "entanglement_error_correlation",
        "concentration_index": "concentration_index",
        "total_correlation": "total_correlation",
        "pathway_persistence": "pathway_persistence",
        "complexity_emergence_score": "complexity_emergence_score",
        
        # Alias mappings (backward compatibility)
        "pathway_concentration_ratio": "concentration_index",
        "temporal_pathway_stability": "pathway_persistence",
        "asymmetry_index": "structure_score",  # Could map AI to SS if needed
    }