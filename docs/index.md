# QForge

A research-grade quantum experiment framework for structured decoherence analysis built on Qiskit.

> **For Researchers:** See the [Comprehensive Design Document](reference/design-document.md) for full technical details, metric definitions, architecture, and research roadmap.

## Overview

This framework provides comprehensive tools for analyzing quantum decoherence patterns and detecting structured error pathways in quantum systems. It implements the **Spring Network Model** hypothesis, which proposes that quantum decoherence follows structured pathways determined by entanglement network topology rather than random patterns.

## Key Features

- **Research-Grade Metrics**: 8 specialized metrics for structured decoherence analysis
- **Information Theory Foundation**: Robust statistical analysis with full-support Jeffreys smoothing
- **Bootstrap Validation**: Confidence intervals and statistical significance testing
- **Schema Compliance**: v1.0 frozen schema format for reproducible research
- **Pipeline Architecture**: High-level orchestration for complex analysis workflows

## Core Research Metrics

### Structure Detection

- **Asymmetry Index (AI)**: Primary screening metric for structured vs random decoherence
- **Pathway Concentration Ratio (PCR)**: Quantifies concentration in preferred pathways
- **Entanglement-Error Correlation (EEC)**: Correlation between topology and error patterns

### Temporal & Complexity Analysis

- **Temporal Pathway Stability (TPS)**: Consistency across experimental conditions
- **Complexity Emergence Score (CES)**: Critical threshold detection for structure emergence

### Information Theory

- **Total Correlation**: Multivariate mutual information
- **Structure Score**: Jensen-Shannon divergence from the factorized (independent-marginals) null model
- **Concentration Index**: Economic inequality measures for pathway preferences

## Quick Start

**Using the CLI:**

```bash
# List available experiments
qforge list

# Run an experiment
qforge run 01_superposition

# With custom parameters
qforge run 01_superposition -s error_rate=0.1 -s num_qubits=3
```

See [CLI Reference](reference/cli.md) for full documentation.

**Using ExperimentProgram (Recommended):**

```python
from src.experiments import 01_superposition

# Run with defaults
result = 01_superposition.run()

# Or customize parameters
result = 01_superposition.run({"num_qubits": 3, "error_rate": 0.1})

# Access metrics
metrics = result.structured_decoherence_metrics
print(f"Asymmetry Index: {metrics.asymmetry_index:.4f}")
```

**Using Engine API Directly:**

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

config = ExperimentConfig(
    num_qubits=3,
    state_type="GHZ",
    enable_research_metrics=True,
    research_type="structured_decoherence",
    shots=1024,
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05
)

result = run(config)
metrics = result.structured_decoherence_metrics
print(f"Asymmetry Index: {metrics.asymmetry_index:.4f}")
```

See the [Quick Start](guides/getting-started/quickstart.md) for more usage examples.

## Research Applications

- **Quantum Error Analysis**: Detecting non-random decoherence patterns
- **Entanglement Dynamics**: Understanding how topology influences error propagation
- **Critical Phenomena**: Identifying emergence thresholds in quantum systems
- **Noise Characterization**: Distinguishing structured from stochastic noise sources

## Architecture

The framework follows an **engine-first architecture** with clean separation:

- **Engine API**: Clean entry points via `run()` and `sweep()` functions
- **Core Logic**: Quantum mechanics implementation and analysis algorithms
- **Analysis Framework**: Specialized metrics and statistical methods
- **Schema System**: Standardized data formats for reproducible research

See [Architecture](architecture/architecture.md) for the detailed design blueprint and [Framework Integration](architecture/framework-integration.md) for how the components work together.

## Documentation Structure

- **[Design Document](reference/design-document.md)**: Comprehensive framework design (metrics, architecture, roadmap)
- **[CLI Reference](reference/cli.md)**: Command-line tool usage and examples
- **Getting Started**: [Installation](guides/getting-started/installation.md) and [Quick Start](guides/getting-started/quickstart.md)
- **API Reference**: [Metrics](guides/api/metrics.md) and [Constants](guides/api/constants.md)
- **Research**: [Research Direction](research/research-direction.md) and [Hardware Results](research/2026-04-hardware-decoherence/hardware-scaling-results.md)
- **[Architecture](architecture/architecture.md)**: System design and integration patterns

## Research Background

This framework implements research on **structured decoherence pathways** - the hypothesis that quantum errors follow predictable patterns determined by entanglement network topology. The Spring Network Model treats entanglement bonds as springs, with decoherence flowing along tension patterns rather than random diffusion.

## Getting Started

Continue to the [Installation Guide](guides/getting-started/installation.md) to set up the framework, or jump to the [Quick Start](guides/getting-started/quickstart.md) for immediate usage examples.
