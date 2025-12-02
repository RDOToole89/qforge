# Constants

Core constants and validation functions for the quantum decoherence analysis framework.

::: src.core.analysis.constants

## Usage Examples

### Validating Measurement Data

```python
from src.core.analysis.constants import validate_counts_dict

# Valid measurement counts
counts = {"00": 100, "01": 200, "10": 150, "11": 50}
validated = validate_counts_dict(counts)
print(validated)  # {"00": 100, "01": 200, "10": 150, "11": 50}

# Invalid counts (will raise ValueError)
try:
    invalid_counts = {"00": -50, "01": 100}
    validate_counts_dict(invalid_counts)
except ValueError as e:
    print(f"Validation error: {e}")
```

### Working with Bitstrings

```python
from src.core.analysis.constants import n_qubits_from_counts, all_bitstrings

# Detect number of qubits
counts = {"000": 100, "111": 200, "001": 50}
n_qubits = n_qubits_from_counts(counts)
print(f"Number of qubits: {n_qubits}")  # 3

# Generate all possible bitstrings
all_outcomes = all_bitstrings(n_qubits)
print(f"All possible outcomes: {all_outcomes}")
# ["000", "001", "010", "011", "100", "101", "110", "111"]
```

### Using Framework Constants

```python
from src.core.analysis.constants import (
    ALPHA, CONF_INT_DEFAULT, MAX_TOP_K, TOPK_MASS_TARGET
)

print(f"Jeffreys prior: {ALPHA}")  # 0.5
print(f"Default CI bounds: {CONF_INT_DEFAULT}")  # (2.5, 97.5)
print(f"Max top-k pathways: {MAX_TOP_K}")
print(f"Mass threshold: {TOPK_MASS_TARGET}")
```

## Mathematical Background

### Jeffreys Prior Smoothing

The framework uses Jeffreys prior smoothing with α = 0.5 to ensure:

- **Full Support**: All 2^n possible outcomes have non-zero probability
- **Bias Reduction**: Eliminates bias when many outcomes are unobserved
- **Deterministic Ordering**: Lexicographic ordering prevents run-to-run drift

### Confidence Intervals

Default confidence intervals use the (2.5, 97.5) percentile range, providing 95% coverage for bootstrap distributions.

### Top-K Analysis

Top-k pathway analysis focuses on outcomes with significant probability mass, filtering noise from rare events while preserving structural information.
