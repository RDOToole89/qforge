# Schema Documentation

This directory contains JSON schemas for validating quantum experiment configurations, sweep manifests, and results data. All schemas have been updated to support structured decoherence research.

## Schema Files

### `experiment_config.schema.json`
Validates individual experiment configurations with full research parameter support.

**New Research Parameters:**
- `enable_research_metrics` (boolean) - Enable structured decoherence metrics computation
- `research_type` (enum) - Type of research analysis: `structured_decoherence`, `parameter_sweep`, `noise_comparison`, `control`, `scaling`, `convergence`, `batch_sweep`
- `multiple_runs` (integer) - Number of experimental runs for statistical validation
- `track_convergence` (boolean) - Enable convergence tracking for high-precision experiments  
- `visualization_type` (enum) - Visualization type: `histogram`, `density_matrix`, `research`, `plot`, `none`

**Example:**
```json
{
  "num_qubits": 3,
  "state_type": "GHZ", 
  "noise_type": "depolarizing",
  "noise_enabled": true,
  "error_rate": 0.05,
  "shots": 4096,
  "enable_research_metrics": true,
  "research_type": "structured_decoherence",
  "multiple_runs": 1,
  "visualization_type": "research"
}
```

### `manifest.schema.json`
Validates parameter sweep manifests with enhanced configurability.

**Key Features:**
- Supports both `base_preset` (string) and `base_config` (object) for flexibility
- Includes all research parameters from experiment config
- `override` section for parameter overrides applied to base configuration
- `parameter_ranges` for systematic parameter sweeps

**Example:**
```json
{
  "base_config": {
    "num_qubits": 3,
    "state_type": "GHZ",
    "enable_research_metrics": true,
    "research_type": "structured_decoherence"
  },
  "parameter_ranges": {
    "num_qubits": [3, 4, 5],
    "error_rate": [0.0, 0.05, 0.1, 0.2]
  },
  "runs_per_config": 1,
  "override": {
    "shots": 10000,
    "track_convergence": false
  }
}
```

### `results.schema.json`
Validates experiment results including structured decoherence metrics.

**Structured Decoherence Metrics Schema:**
- `asymmetry_index` (number, ≥0) - AI: Deviation from uniform error distribution
- `pathway_concentration_ratio` (number, ≥0) - PCR: Concentration in top pathways  
- `entanglement_error_correlation` (number, -1 to 1) - EEC: Topology-error correlation
- `temporal_pathway_stability` (number, 0-1 or null) - TPS: Pathway consistency
- `complexity_emergence_score` (number, ≥0 or null) - CES: Emergence threshold
- `metadata` (object) - Analysis metadata (state_type, num_qubits, etc.)
- `pathway_analysis` (object) - Human-readable pathway analysis summary

**Updated Artifact Types:**
- Removed: `hypergraph` (cleaned up)
- Supported: `histogram`, `density_matrix`, `report`, `other`

## Schema Usage in Code

### Validation Functions
```python
from src.utils.schema import validate_manifest_schema, validate_results_schema

# Validate sweep manifest
validate_manifest_schema(manifest_data)

# Validate experiment results  
validate_results_schema(results_data)
```

### Research Metrics Integration
The structured decoherence metrics are automatically computed when `enable_research_metrics: true` and included in the results under `metrics.structured_decoherence_metrics`.

### Engine API Integration
The schemas work seamlessly with both engine API and legacy execution paths, ensuring consistent data validation across all experiment workflows.

## Research Configuration Patterns

### Basic Research Experiment
```json
{
  "num_qubits": 3,
  "state_type": "GHZ",
  "noise_type": "depolarizing", 
  "noise_enabled": true,
  "error_rate": 0.05,
  "enable_research_metrics": true,
  "research_type": "structured_decoherence"
}
```

### Parameter Sweep for Research
```json
{
  "base_config": {
    "state_type": "GHZ",
    "enable_research_metrics": true,
    "research_type": "parameter_sweep",
    "shots": 10000
  },
  "parameter_ranges": {
    "num_qubits": [3, 4, 5],
    "error_rate": [0.005, 0.01, 0.02, 0.05, 0.1]
  },
  "runs_per_config": 5
}
```

### High-Precision Convergence Study  
```json
{
  "num_qubits": 3,
  "state_type": "GHZ",
  "enable_research_metrics": true,
  "research_type": "convergence",
  "shots": 16384,
  "multiple_runs": 1,
  "track_convergence": true
}
```

## Schema Validation Benefits

1. **Data Integrity** - Ensures consistent data structures across all experiments
2. **Research Compliance** - Validates that research parameters are properly configured
3. **Error Prevention** - Catches configuration errors before experiments run
4. **Documentation** - Serves as living documentation of supported parameters
5. **Tool Integration** - Enables IDE autocompletion and validation in editors

## Future Enhancements

- Additional research types as new analysis methods are developed
- Enhanced validation rules for parameter combinations
- Conditional validation based on research type
- Integration with experiment design assistance tools