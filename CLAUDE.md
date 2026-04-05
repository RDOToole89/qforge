# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **research-grade quantum experiment framework** built on Qiskit for conducting quantum computing experiments with noise modeling, state preparation, and advanced analysis. The project uses an **engine-first architecture** with a clean API for running structured decoherence pathway experiments.

## Research Focus: Structured Decoherence Pathways

**Central Hypothesis**: Quantum decoherence follows structured pathways determined by entanglement network topology rather than random patterns. The framework uses a **Spring Network Model** where entanglement bonds act as springs and decoherence flows along tension patterns.

**Complete Research Metrics Suite (v1.0 Schema Compliant):**

- **AI (Asymmetry Index)**: TVD from uniform distribution with full 2^n support
- **PCR (Pathway Concentration Ratio)**: Concentration in top vs bottom pathway quartiles
- **EEC (Entanglement-Error Correlation)**: Pearson correlation between topology and MI matrices
- **TPS (Temporal Pathway Stability)**: Spearman correlation consistency across conditions
- **CES (Complexity Emergence Score)**: Logistic emergence threshold detection
- **SS (Structure Score)**: Jensen-Shannon divergence from factorized null model
- **CI (Concentration Index)**: Gini-like pathway concentration measure
- **TC (Total Correlation)**: Multi-information across all qubits

## Engine-First Architecture

The framework is built around a clean, decoupled engine API:

### Core Components

- **Engine API** (`src/engine/api.py`) - Clean entry points: `run()` and `sweep()`
- **Pydantic Models** (`src/engine/models/`) - Type-safe configuration and results
- **Core Logic** (`src/core/`) - Quantum mechanics and analysis
- **Analysis Framework** (`src/core/analysis/`) - Research-grade structured decoherence metrics

### Usage Examples

**Basic Research Experiment:**

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

# Access structured decoherence metrics
metrics = result.structured_decoherence_metrics
print(f"Asymmetry Index: {metrics.asymmetry_index:.4f}")
print(f"Pathway Concentration: {metrics.pathway_concentration_ratio:.4f}")
print(f"Topology Correlation: {metrics.entanglement_error_correlation:.4f}")
```

**Statevector Mode (exact noiseless state):**

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

result = run(ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    sim_mode="statevector", shots=1000, rng_seed=42,
))
meas = result.analysis.measurement_results
print(f"Fidelity: {meas.fidelity:.6f}")       # ~1.0 (exact state)
print(f"Statevector: {len(meas.statevector)} amplitudes")
```

**Density Matrix Mode (full mixed state with noise):**

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

result = run(ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    sim_mode="density_matrix",
    noise_enabled=True, noise_type="depolarizing", error_rate=0.1,
    shots=1000,
))
meas = result.analysis.measurement_results
print(f"Fidelity: {meas.fidelity:.4f}")        # < 1.0 (noise degradation)
print(f"DM shape: {len(meas.density_matrix)}x{len(meas.density_matrix[0])}")
```

**Direct Analysis Pipeline:**

```python
from src.core.analysis.pipelines.pathway_analysis import run_all_to_schema

# Run complete analysis pipeline with v1.0 schema output
schema_result = run_all_to_schema(counts=measurement_data, rng=rng)

# Access all 8 metrics in standardized format
print(f"Structure Score: {schema_result['structure_score']['value']:.4f}")
print(f"Entanglement Correlation: {schema_result['entanglement_error_correlation']['value']:.4f}")
```

## Development Commands

### Core Analysis Testing

```bash
# Test individual metrics
python -c "
from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index
ai = compute_asymmetry_index({'000': 400, '111': 400, '001': 100, '110': 100})
print(f'AI: {ai:.4f}')
"

# Test complete pipeline
python -c "
from src.core.analysis.pipelines.pathway_analysis import run_all_to_schema
result = run_all_to_schema({'000': 400, '111': 400, '001': 100, '110': 100})
print(f'Schema version: {result[\"schema_version\"]}')
print(f'Metrics computed: {len(result) - 1}')
"
```

### Research Validation

```bash
# Test engine integration with hardened metrics
python -c "
from src.engine.api import run
from src.engine.models import ExperimentConfig

config = ExperimentConfig(
    num_qubits=4,
    state_type='GHZ',
    enable_research_metrics=True,
    research_type='structured_decoherence',
    noise_enabled=True,
    noise_type='depolarizing',
    error_rate=0.05
)

result = run(config)
metrics = result.structured_decoherence_metrics
print(f'AI: {metrics.asymmetry_index:.4f}')
print(f'Evidence for structured pathways: {metrics.asymmetry_index > 0.2}')
"
```

## File Organization

### Analysis Framework (Research-Grade, Hardened Dec 2024)

- `src/core/analysis/metrics/` - **Individual metric implementations**
  - `asymmetry_index.py` - Fast closed-form TVD with educational documentation
  - `complexity_emergence_score.py` - Logistic emergence fitting with AIC model selection
  - `entanglement_error_correlation.py` - Multi-topology support with statistical testing
  - `temporal_pathway_stability.py` - Advanced time series analysis with transition matrices
  - `pathway_concentration_ratio.py` - Adaptive quartile-based concentration
  - `concentration_index.py` - Gini-like pathway concentration measure
  - `pathway_persistence.py` - Pathway persistence measurement
  - `total_correlation.py` - Multi-information (total correlation) across all qubits
  - `noise_topology_correlation.py` - Noise-topology correlation analysis
  - `structure_score.py` - Clean delegation wrapper for all metrics
  - `schema_bridge.py` - v1.0 schema compliance with robust validation
  - `registry.py` - Declarative MetricSpec pattern with bootstrap CI and status logic
  - `profiles.py` - Metric selection profiles (structured_decoherence, minimal, full)

- `src/core/analysis/core/` - **Mathematical foundations**
  - `information_theory.py` - Full-support Jeffreys smoothing, deterministic ordering
  - `null_models.py` - SciPy-free factorized models with reproducible sampling
  - `correlations.py` - Topology analysis with adjacency matrix construction
  - `bootstrap.py` - Reproducible confidence intervals with RNG plumbing
  - `topology.py` - Topology builders for noise model and metric computation

- `src/core/analysis/pipelines/` - **High-level orchestration**
  - `pathway_analysis.py` - Complete research pipeline with schema output

- `src/core/analysis/constants.py` - **Centralized configuration**
  - All thresholds, parameters, and validation functions

### Engine (Primary Interface)

- `src/engine/api.py` - Main entry points: `run()`, `sweep()`, `iter_experiment_configs()`
- `src/engine/bloch_math.py` - Bloch sphere coordinate math for visualization
- `src/engine/provenance.py` - Provenance building (software versions, git SHA, host info)
- `src/engine/fidelity.py` - Simulation data extraction (statevector, density matrix, fidelity)
- `src/engine/viz_pipeline.py` - Visualization rendering orchestration
- `src/engine/models/` - Pydantic models, split into focused submodules:
  - `config.py` - Experiment configuration
  - `metadata.py` - Experiment identification and context
  - `circuit.py` - Quantum circuit statistics with auto-healing validators
  - `measurement.py` - Measurement results with auto-healing validators
  - `provenance.py` - Reproducibility provenance tracking
  - `quality.py` - Quality assessment metrics
  - `results.py` - Top-level result composition (imports above)
  - `research.py` - Structured decoherence research models
  - `sweep.py` - Parameter sweep configuration and results
  - `storage.py` - Storage, artifacts, and manifest models

### Core Quantum Mechanics

- `src/core/noise_models/` - Physics-compliant noise model implementations
- `src/core/state_preparation/` - Quantum state preparation (6 state types)

### State Preparation (Educational Excellence)

- `src/core/state_preparation/` - **PRODUCTION-READY**
  - Complete educational framework with 6 state types
  - Hardware compatibility and validation
  - Clean factory pattern and registry system

## Current Development Status (Updated April 2026)

### ✅ **MAJOR ACHIEVEMENT: Research-Grade Analysis Framework Complete**

**Framework Hardening (December 2024)**

- **Mathematical Rigor**: Full-support Jeffreys smoothing (K = 2^n) throughout all metrics
- **Deterministic Behavior**: Canonical lexicographic ordering prevents run-to-run drift
- **Type Safety**: Comprehensive NumPy typing with `NDArray[np.float64]`
- **Reproducible Science**: RNG plumbing for deterministic bootstrap confidence intervals
- **Dependency Optimization**: SciPy-optional architecture with graceful fallbacks
- **Schema Compliance**: Complete v1.0 schema support with robust validation

**Individual Metric Excellence**

- **Asymmetry Index**: Fast closed-form TVD computation avoiding 2^n enumeration when possible
- **Complexity Emergence**: Sophisticated logistic regression with AIC model selection
- **Entanglement Correlation**: Multi-topology support (GHZ, W, Bell, Cluster) with statistical validation
- **Temporal Stability**: Advanced time series analysis with transition matrices and persistence scores
- **Schema Bridge**: Robust conversion between MetricResult and v1.0 schema with alias support

**Quality Assurance**

- **Comprehensive Testing**: All metrics pass rigorous smoke tests
- **Mathematical Validation**: Property verification functions for each metric
- **Educational Documentation**: Research-grade documentation with physics interpretations
- **Error Handling**: Graceful degradation and meaningful error messages

### 🎯 **Current Architecture Status**

**Analysis Framework (`src/core/analysis/`)** - ✅ **RESEARCH-GRADE & COMPLETE**

- **8 Metrics**: All structured decoherence metrics implemented to publication standards
- **Mathematical Foundation**: Rigorous information theory, statistics, and quantum mechanics
- **Schema Compliance**: Full v1.0 compatibility with validation
- **Performance Optimized**: Fast algorithms with smart enumeration avoidance
- **Educational Value**: Comprehensive documentation and examples

**State Preparation (`src/core/state_preparation/`)** - ✅ **PRODUCTION-READY**

- **Educational Framework**: Teaches quantum mechanics while enabling research
- **Hardware Integration**: Real quantum device compatibility
- **6 State Types**: GHZ, Bell, W, Cluster, Superposition, Custom

**Engine Integration** - ✅ **STABLE & MODULAR**

- Clean API through `run()`, `sweep()`, and `iter_experiment_configs()`
- Type-safe Pydantic models split into focused submodules (metadata, circuit, measurement, provenance, quality)
- Automated structured decoherence metrics computation
- Extracted provenance, fidelity, and visualization into dedicated modules

**Code Quality** - ✅ **ENFORCED**

- **Linting**: ruff with pydocstyle (D), complexity (C901 max 15), Google convention
- **Pre-commit hooks**: ruff check + format, trailing whitespace, YAML/JSON/TOML validation
- **Type checking**: mypy strict mode
- **Testing**: pytest with 90% coverage on core analysis, 277+ passing tests

**Frontend (React Native / Expo)** - ✅ **REFACTORED**

- BlochSphereScreen split from 1064 lines into hooks + sub-components (~232 lines main screen)
- Custom hooks: useBuiltInMode, useExperimentMode, useSweepMode, useDragRotation
- Component hierarchy: Header, BuiltinSidebar, ExperimentSidebar, DataPanel
- Quantum Glossary: searchable reference of 100+ quantum computing terms across 16 categories
- Expo Router file-based navigation with 6 tabs (configure, results, visualizer, circuit, registry, glossary)

### 🚀 **Ready for Next Phase**

**High-Priority Next Steps:**

1. **H_Q2 Experiment**: Test "Pathway Persistence" in deeper circuits.
2. **H_Q3 Experiment**: Implement sensor-qubit subspaces.
3. **Research Documentation**: Expand on the "Fog vs River" findings.
4. **Performance Benchmarking**: Profile large-scale studies and optimize bottlenecks.

**Research Readiness:**

- ✅ **Publication-Ready Metrics**: All 8 metrics implemented to research standards
- ✅ **Reproducible Results**: Deterministic behavior with full provenance tracking
- ✅ **Schema Compliance**: v1.0 compatibility for downstream analysis pipelines
- ✅ **Educational Value**: Framework serves both learning and research purposes
- ✅ **First Discovery**: "Fog vs River" phenomenon confirmed in H_Q1.

## Architecture Principles

1. **Research-Grade Quality**: All components meet publication standards for scientific rigor
2. **Deterministic Behavior**: Reproducible results with canonical ordering and RNG control
3. **Educational Excellence**: Code teaches quantum mechanics while enabling advanced research
4. **Schema Compliance**: v1.0 compatibility ensures interoperability with analysis pipelines
5. **Mathematical Rigor**: Full-support smoothing, proper statistics, validated algorithms
6. **Performance Optimization**: Smart algorithms that scale to large quantum systems
7. **Type Safety**: Comprehensive typing prevents runtime errors in research workflows
8. **Error Resilience**: Graceful degradation and meaningful diagnostics

---

## Framework Generalizability

**Key insight**: Although the current flagship is **structured decoherence research**, the architecture is **deliberately general**:

- `src/core/` is not tied to any specific hypothesis — it's pure physics + metrics
- `src/engine/` doesn't know what "structured decoherence" means — it just orchestrates
- Only `src/experiments/` carries research-specific semantics

### ExperimentProgram Abstraction

Experiments should follow a pluggable protocol:

```python
# src/experiments/base.py
from typing import Protocol, Mapping, Any
from src.engine.models import ExperimentConfig, ExperimentResult

class ExperimentProgram(Protocol):
    """A pluggable experiment program."""

    name: str
    description: str

    def default_config(self) -> ExperimentConfig:
        ...

    def run(self, overrides: Mapping[str, Any] | None = None) -> ExperimentResult:
        ...
```

### Experiment Registry

```python
# src/experiments/__init__.py
EXPERIMENT_REGISTRY = {
    "bell_state": BellExperiment(),
    "topology_comparison": TopologyComparison(),
    "scaling_ladder": ScalingLadder(),
    "shor": ShorExperiment(),
    # ... 13 experiments across basics/, advanced/, decoherence/, hardware/
}
```

### CLI Principles

The CLI should be **thin and boring**:

- **DO**: Parse args → call `run()` / `ExperimentProgram.run()` → print results
- **DON'T**: Encode orchestration logic, domain decisions, or complex branching

```python
# CLI is just: parser + caller + printer
@app.command()
def run_experiment(name: str, override: list[str] = []):
    program = EXPERIMENT_REGISTRY[name]
    result = program.run(parse_overrides(override))
    print(result.model_dump_json(indent=2))
```

### Metrics Stay General, Interpretation Specializes

- `src/core/analysis/metrics/` — **strictly general** (no research-specific language)
- `StructuredDecoherenceMetrics` — one _view_ over the metric bundle
- Future: `BenchmarkMetrics`, `EntanglementMetrics`, etc.

The engine routes via `research_type`:

- `research_type="structured_decoherence"` → decoherence pathway metrics
- `research_type="benchmark"` → hardware benchmark metrics
- etc.

---

## Rules for Claude in This Repo

### DO

- Respect the layered architecture (`experiments → engine → core`)
- Keep everything deterministic and reproducible
- Keep metrics mathematically and physically faithful
- Treat structured decoherence as **one experiment program**, not the framework's identity
- Keep CLI/UI layers thin — they call into the framework, not the reverse

### DO NOT (without being asked)

- "Simplify" metrics just to make code shorter — they are research-grade on purpose
- Fold `core` and `engine` together — the layered architecture is a feature
- Turn this into a product-like framework with web UI, auth, etc.
- Move physics or metric logic into CLI/UI layers
- Add "Co-Authored-By", "Powered by", "Generated with", or any AI attribution to commits, PRs, code comments, or docs

### Breaking Changes Policy

**We are at Beta v0.2, NOT v1.0.** Breaking changes are allowed and preferred over:

- Backward compatibility shims
- Legacy function wrappers
- Dead code accumulation
- Deprecation warnings that never get resolved

**Rule:** Remove old code, don't wrap it. Clean breaks > cruft.

When refactoring:

- Delete procedural code, replace with class-based implementations
- Don't keep old function signatures "for compatibility"
- Don't add `# deprecated` comments — just remove the code
- Update imports and tests to use new patterns

## Research Workflow

1. **Design Experiment**: Configure quantum state, noise model, research parameters
2. **Run Analysis**: Use direct pipeline or engine API for metric computation
3. **Statistical Validation**: Bootstrap confidence intervals and significance testing
4. **Schema Output**: v1.0 compliant results for downstream analysis
5. **Scientific Interpretation**: Educational docs guide physical understanding
6. **Publish Results**: Complete provenance tracking for reproducible science

This framework enables systematic investigation of the **Spring Network Model** hypothesis and provides the tools needed to discover and validate structured decoherence pathways in quantum systems.

## Quick Start for Research

```python
# Complete structured decoherence analysis
from src.core.analysis.pipelines.pathway_analysis import run_all_to_schema

# Your quantum measurement data
counts = {"000": 400, "111": 400, "001": 100, "110": 100}

# Get complete analysis with all 8 metrics
results = run_all_to_schema(counts)

# Results are v1.0 schema compliant
print(f"Schema version: {results['schema_version']}")
print(f"Structure evidence: {results['structure_score']['value']:.4f}")
print(f"Topology correlation: {results['entanglement_error_correlation']['value']:.4f}")
```

The framework is now **research-ready** and optimized for investigating structured decoherence pathways in quantum systems!
