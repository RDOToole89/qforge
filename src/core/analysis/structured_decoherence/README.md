# Structured Decoherence Analysis Module

This module implements the 5 quantitative metrics for detecting structured decoherence pathways in quantum systems.

## Research Hypothesis

**Quantum decoherence follows structured pathways determined by entanglement network topology, emerging above a critical complexity threshold (≥3 qubits).**

## The 5 Core Metrics

### 1. Asymmetry Index (AI)
**Formula**: `AI = (1/N) Σᵢ |pᵢ - p_uniform| / p_uniform`

Measures deviation from uniform error distribution. Higher values indicate structured (non-random) decoherence patterns.

- **Range**: 0 to ∞ (typically 0-2)
- **Interpretation**: 
  - AI < 0.1: Very uniform (random)
  - AI > 0.6: Highly structured

### 2. Pathway Concentration Ratio (PCR)  
**Formula**: `PCR = (Top 25% frequencies) / (Bottom 25% frequencies)`

Quantifies concentration of errors in preferred pathways vs. least likely pathways.

- **Range**: 1 to ∞ 
- **Interpretation**:
  - PCR ≈ 1: Uniform distribution
  - PCR > 2: Strong pathway preferences

### 3. Entanglement-Error Correlation (EEC)
**Formula**: `EEC = correlation(entanglement_topology, error_patterns)`

Measures correlation between quantum state entanglement structure and observed error patterns.

- **Range**: -1 to +1
- **Interpretation**:
  - |EEC| < 0.2: No correlation
  - |EEC| > 0.5: Strong topology influence

### 4. Temporal Pathway Stability (TPS)
**Formula**: `TPS = 1 - σ(pathway_rankings) / mean(pathway_rankings)`

Measures consistency of pathway rankings across different noise levels or experimental runs.

- **Range**: 0 to 1
- **Interpretation**:
  - TPS < 0.5: Unstable pathways
  - TPS > 0.8: Highly stable structure

### 5. Complexity Emergence Score (CES)
**Formula**: `CES = emergence_rate_at_critical_threshold`

Quantifies at what complexity level structured decoherence patterns emerge clearly.

- **Range**: 0 to ∞
- **Interpretation**:
  - CES ≈ 0: No clear emergence
  - CES > 0.3: Strong emergence at 3+ qubits

## Usage Examples

### Basic Analysis
```python
from src.core.analysis.structured_decoherence import compute_all_pathway_metrics

# Compute all 5 metrics
metrics = compute_all_pathway_metrics(
    counts={"000": 450, "111": 420, "001": 80, "110": 50},
    state_type="GHZ",
    num_qubits=3
)

print(f"AI: {metrics['asymmetry_index']:.3f}")
print(f"PCR: {metrics['pathway_concentration_ratio']:.3f}")
print(f"EEC: {metrics['entanglement_error_correlation']:.3f}")
```

### High-Level Structure Analysis
```python
from src.core.analysis.structured_decoherence import analyze_decoherence_structure

# Get structured vs random classification
analysis = analyze_decoherence_structure(
    counts=measurement_data,
    state_type="GHZ",
    confidence_threshold=0.7
)

print(f"Classification: {analysis['classification']}")
print(f"Confidence: {analysis['confidence']:.3f}")
print(f"Interpretation: {analysis['interpretation']}")
```

### Individual Metrics
```python
from src.core.analysis.structured_decoherence import (
    compute_asymmetry_index,
    compute_pathway_concentration_ratio,
    compute_entanglement_error_correlation
)

ai = compute_asymmetry_index(counts)
pcr = compute_pathway_concentration_ratio(counts)
eec = compute_entanglement_error_correlation(counts, "GHZ")
```

## Integration with Research Pipeline

The metrics are automatically computed when `enable_research_metrics: true` is set in experiment configurations. They are included in the research analysis JSON output under the `structured_decoherence_metrics` field.

## Mathematical Background

The metrics are designed to detect:

1. **Non-uniform error distributions** (AI)
2. **Pathway concentration effects** (PCR)  
3. **Topology-dependent error patterns** (EEC)
4. **Temporal consistency** (TPS)
5. **Complexity thresholds** (CES)

Together, these metrics provide comprehensive characterization of whether quantum decoherence exhibits structured (non-random) behavior consistent with the research hypothesis.

## Files

- **`pathway_metrics.py`** - Core implementation of all 5 metrics
- **`pathway_analysis.py`** - High-level analysis and interpretation functions
- **`__init__.py`** - Module interface and exports
- **`README.md`** - This documentation file