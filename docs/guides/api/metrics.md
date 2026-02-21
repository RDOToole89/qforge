# Metrics

Structured decoherence analysis metrics for quantum error pattern detection.

## Asymmetry Index

Primary screening metric for structured vs random decoherence patterns.

::: src.core.analysis.metrics.asymmetry_index

## Pathway Concentration Ratio

Quantifies concentration of errors in preferred pathways.

::: src.core.analysis.metrics.pathway_concentration_ratio

## Entanglement-Error Correlation

Measures correlation between entanglement topology and error patterns.

::: src.core.analysis.metrics.entanglement_error_correlation

## Temporal Pathway Stability

Analyzes consistency of pathway rankings across experimental conditions.

::: src.core.analysis.metrics.temporal_pathway_stability

## Complexity Emergence Score

Detects critical thresholds for structure emergence as system complexity increases.

::: src.core.analysis.metrics.complexity_emergence_score

## Usage Examples

### Basic Metric Computation

```python
from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index
from src.core.analysis.metrics.pathway_concentration_ratio import compute_pathway_concentration_ratio

# Quantum measurement data
counts = {"000": 400, "111": 350, "001": 150, "110": 100}

# Compute individual metrics
ai = compute_asymmetry_index(counts)
pcr = compute_pathway_concentration_ratio(counts)

print(f"Asymmetry Index: {ai:.4f}")
print(f"Pathway Concentration: {pcr:.2f}x")
```

### Comprehensive Analysis

```python
from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index
from src.core.analysis.metrics.entanglement_error_correlation import compute_entanglement_error_correlation

# GHZ state decoherence analysis
ghz_counts = {"000": 450, "111": 450, "001": 50, "110": 50}

# Detailed analysis with full results
ai_analysis = compute_asymmetry_index(ghz_counts, return_analysis=True)
eec = compute_entanglement_error_correlation(ghz_counts, "GHZ")

print(f"Structure Evidence: {ai_analysis.structure_evidence}")
print(f"Dominant Outcomes: {ai_analysis.dominant_outcomes}")
print(f"Topology Correlation: {eec:.4f}")
```

### Temporal Analysis

```python
from src.core.analysis.metrics.temporal_pathway_stability import compute_temporal_pathway_stability

# Pathway rankings across different noise levels
rankings = [
    ["000", "111", "001", "110"],  # Low noise
    ["000", "111", "001", "110"],  # Medium noise
    ["000", "111", "110", "001"]   # High noise
]

tps = compute_temporal_pathway_stability(rankings, return_analysis=True)
print(f"Temporal Stability: {tps.temporal_pathway_stability:.4f}")
print(f"Ranking Consistency: {tps.ranking_consistency}")
print(f"Persistent Pathways: {tps.persistent_pathways}")
```

### Emergence Analysis

```python
from src.core.analysis.metrics.complexity_emergence_score import compute_complexity_emergence_score

# Multi-qubit system data
multi_qubit_data = {
    2: {"00": 500, "11": 500},  # Random
    3: {"000": 400, "111": 300, "001": 200, "110": 100},  # Emerging
    4: {"0000": 500, "1111": 300, "0001": 100, "1110": 100},  # Structured
}

ces = compute_complexity_emergence_score(multi_qubit_data, return_analysis=True)
print(f"Emergence Score: {ces.complexity_emergence_score:.4f}")
print(f"Critical Threshold: {ces.critical_threshold:.1f} qubits")
print(f"Emergence Quality: {ces.emergence_quality}")
```

## Mathematical Foundations

### Total Variation Distance

Asymmetry Index is based on Total Variation Distance from uniform distribution:

$$AI = \frac{1}{2} \sum_i |p(x_i) - p_{uniform}|$$

### Economic Inequality Measures

Pathway Concentration Ratio uses Palma ratio from economic inequality:

$$PCR = \frac{\text{Top 10% pathway mass}}{\text{Bottom 40% pathway mass}}$$

### Rank Correlation Analysis

Temporal Pathway Stability uses coefficient of variation for ranking correlations:

$$TPS = 1 - \frac{\sigma(\rho_{rankings})}{\mu(\rho_{rankings})}$$

### Logistic Emergence Models

Complexity Emergence Score fits emergence curves:

$$S(n) = \frac{A}{1 + \exp(-k(n - n_0))} + S_0$$

Where CES = k × A combines emergence sharpness and magnitude.
