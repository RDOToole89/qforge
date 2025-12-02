# Experiments Module

This module provides a pluggable experiment system for running quantum decoherence research.

## Quick Start

```python
from src.experiments import get_experiment, list_experiments

# See what's available
for name, description in list_experiments():
    print(f"{name}: {description}")

# Run an experiment
exp = get_experiment("sst_q1")
result = exp.run()

# Check the metrics
print(f"Asymmetry Index: {result.structured_decoherence_metrics.asymmetry_index:.4f}")
```

## CLI Usage

The `qxf` command-line tool provides quick access to experiments:

```bash
# List all available experiments
qxf list

# Run an experiment with defaults
qxf run sst_q1

# Run with custom parameters
qxf run bell_correlation -s error_rate=0.1 -s shots=2048

# Get JSON output for scripting
qxf run sst_q1 --json

# Run from a JSON config file
qxf run-config my_config.json
```

## Available Experiments

| Name | Description | Noise Type |
|------|-------------|------------|
| `sst_q1` | SST Hypothesis Q1 - Tests if entanglement topology influences decoherence | Depolarizing |
| `sst_q1_structured` | SST Q1 with structured noise - Compares pathway behavior | Amplitude Damping |
| `bell_correlation` | Bell state correlation test - Quantum vs classical bounds | Depolarizing |

## Run vs Sweep

### `run()` - Single Experiment

Executes one experiment with a specific configuration.

```python
from src.experiments import sst_q1

# Run with defaults
result = sst_q1.run()

# Run with custom parameters
result = sst_q1.run({
    "num_qubits": 3,
    "error_rate": 0.1,
    "shots": 8192
})
```

**Returns:** Single `ExperimentResult` with metrics and analysis.

### `sweep()` - Parameter Sweep

Runs multiple experiments varying one or more parameters.

```python
from src.experiments import sst_q1

# Sweep over error rates
results = sst_q1.sweep({
    "error_rate": [0.01, 0.05, 0.1, 0.2]
})

# Sweep over multiple parameters (all combinations)
results = sst_q1.sweep({
    "num_qubits": [3, 4, 5],
    "error_rate": [0.01, 0.05, 0.1]
})
# This runs 3 × 3 = 9 experiments
```

**Returns:** List of `ExperimentResult`, one per parameter combination.

### Convenience Methods

Some experiments have specialized sweep methods:

```python
from src.experiments import sst_q1

# Noise sweep with sensible defaults
results = sst_q1.run_noise_sweep(
    noise_steps=20,      # Number of error rate steps
    max_error_rate=0.5   # Maximum error rate to test
)
```

## Configuration Options

All experiments use `ExperimentConfig`. Common parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `num_qubits` | int | 4 | Number of qubits in the system |
| `state_type` | str | "GHZ" | Quantum state: "GHZ", "W", "Bell", "Cluster" |
| `noise_enabled` | bool | True | Whether to apply noise |
| `noise_type` | str | "depolarizing" | Noise model: "depolarizing", "amplitude_damping" |
| `error_rate` | float | 0.05 | Noise strength (0.0 to 1.0) |
| `shots` | int | 4096 | Number of measurement shots |
| `enable_research_metrics` | bool | True | Compute structured decoherence metrics |
| `research_type` | str | "structured_decoherence" | Type of research metrics |

### Override Examples

```python
from src.experiments import sst_q1

# Higher precision (more shots)
result = sst_q1.run({"shots": 16384})

# Different state topology
result = sst_q1.run({"state_type": "W", "num_qubits": 5})

# No noise (ideal reference)
result = sst_q1.run({"noise_enabled": False})

# Higher error rate
result = sst_q1.run({"error_rate": 0.2})
```

## Working with Results

### ExperimentResult Structure

```python
result = exp.run()

# Status and timestamp
print(result.status)      # "completed"
print(result.timestamp)   # ISO timestamp

# Structured decoherence metrics (when enabled)
metrics = result.structured_decoherence_metrics
print(metrics.asymmetry_index)              # AI: deviation from uniform
print(metrics.pathway_concentration_ratio)  # PCR: pathway concentration
print(metrics.entanglement_error_correlation)  # EEC: topology correlation
```

### Analyzing Sweep Results

```python
results = sst_q1.sweep({"error_rate": [0.01, 0.05, 0.1, 0.2]})

# Extract metrics for plotting
error_rates = [0.01, 0.05, 0.1, 0.2]
ai_values = [r.structured_decoherence_metrics.asymmetry_index for r in results]

import matplotlib.pyplot as plt
plt.plot(error_rates, ai_values)
plt.xlabel("Error Rate")
plt.ylabel("Asymmetry Index")
plt.title("AI vs Noise Strength")
plt.show()
```

## Creating a New Experiment

1. Create a new file in `src/experiments/`:

```python
# src/experiments/my_experiment.py
from src.experiments.base import BaseExperiment
from src.engine.models import ExperimentConfig

class MyExperiment(BaseExperiment):
    """
    My Custom Experiment

    Research Question: [What are you testing?]
    Hypothesis: [What do you expect?]
    Pass Criteria: [What defines success?]
    """

    name = "my_exp"
    description = "Tests something interesting"

    def default_config(self) -> ExperimentConfig:
        return ExperimentConfig(
            num_qubits=4,
            state_type="GHZ",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            shots=4096,
            enable_research_metrics=True,
            research_type="structured_decoherence",
        )

# Module-level instance for convenience
my_exp = MyExperiment()
```

1. Register in `src/experiments/__init__.py`:

```python
from src.experiments.my_experiment import MyExperiment, my_exp

EXPERIMENT_REGISTRY["my_exp"] = my_exp

__all__ = [
    # ... existing exports
    "MyExperiment",
    "my_exp",
]
```

1. Use it:

```python
from src.experiments import my_exp

result = my_exp.run()
```

## Research Metrics

When `enable_research_metrics=True`, the following metrics are computed:

| Metric | Abbreviation | Description |
|--------|--------------|-------------|
| Asymmetry Index | AI | Total variation distance from uniform distribution |
| Pathway Concentration Ratio | PCR | Concentration in top vs bottom pathway quartiles |
| Entanglement-Error Correlation | EEC | Correlation between topology and error patterns |
| Temporal Pathway Stability | TPS | Consistency across experimental conditions |
| Complexity Emergence Score | CES | Critical threshold detection |
| Structure Score | SS | Jensen-Shannon divergence from null model |
| Concentration Index | CI | Gini-like pathway concentration measure |
| Total Correlation | TC | Multi-information across all qubits |

## Tips

### Performance

- Start with fewer shots (1024) for exploration, increase (8192+) for publication
- Use `sweep()` instead of manual loops - it's optimized
- Smaller qubit counts (3-4) run faster for initial testing

### Reproducibility

- Results include timestamps and config hashes
- Set explicit seeds if needed: `run({"seed": 42})`
- Save results using the engine's built-in storage

### Comparing Noise Models

```python
from src.experiments import sst_q1, sst_q1_structured

# Same parameters, different noise
depol_result = sst_q1.run({"error_rate": 0.1})
amp_result = sst_q1_structured.run({"error_rate": 0.1})

print(f"Depolarizing AI: {depol_result.structured_decoherence_metrics.asymmetry_index:.4f}")
print(f"Amplitude Damping AI: {amp_result.structured_decoherence_metrics.asymmetry_index:.4f}")
```

### Bell State Experiments (Non-SST)

```python
from src.experiments import bell_correlation

# Run Bell correlation test
result, metrics = bell_correlation.run_with_bell_metrics()
print(f"Correlation: {metrics.correlation_coefficient:.4f}")
print(f"Exceeds classical bound: {metrics.exceeds_classical}")

# Compare all Bell variants
results = bell_correlation.compare_variants(error_rate=0.1)
for variant, (result, metrics) in results.items():
    print(f"{variant}: fidelity={metrics.fidelity:.4f}")

# Watch correlation decay with noise
for error_rate, result, metrics in bell_correlation.run_noise_sweep():
    print(f"Error {error_rate:.2f}: correlation={metrics.correlation_coefficient:.4f}")
```

## Troubleshooting

**"Unknown experiment: X"**
- Check spelling with `list_experiments()`
- Ensure experiment is registered in `__init__.py`

**"No structured_decoherence_metrics"**
- Ensure `enable_research_metrics=True` in config
- Check `research_type` is set correctly

**Slow execution**
- Reduce `shots` for faster iteration
- Use smaller `num_qubits` for testing
- Consider using `sweep()` for batch processing
