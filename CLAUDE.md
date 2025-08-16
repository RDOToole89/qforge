# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **research-grade quantum experiment framework** designed specifically for investigating **structured decoherence pathways** in quantum systems. The framework provides precision tools for testing the hypothesis that quantum decoherence follows structured pathways determined by entanglement network topology, rather than uniform random patterns.

### Current Research Focus: Structured Decoherence Pathways

**Core Hypothesis**: Quantum decoherence propagates along structured pathways determined by entanglement topology, emerging above a critical complexity threshold (≥3 qubits).

**Key Experimental Goals**:
- Map entanglement complexity thresholds where structured pathways emerge
- Characterize pathway signatures across different quantum state topologies  
- Validate pathway persistence across multiple noise models
- Develop quantitative metrics for pathway detection and engineering

The framework is currently undergoing targeted refactoring to optimize it specifically for this research while removing unnecessary complexity.

## Architecture Overview

The framework uses a modular architecture with clean separation of concerns:

### Core Layers
- **Engine** (`src/engine/`) - Clean importable library with unified API
- **Core** (`src/core/`) - Quantum logic (state preparation, noise models, analysis)
- **CLI** (`src/cli/`) - Command-line interface (interactive and headless)
- **Visualization** (`src/visualization/`) - Multi-backend plotting and reporting
- **Experiments** (`src/experiments/`) - Preset experiments and management

### Key Components for Structured Decoherence Research
- **State Preparation**: GHZ (symmetric), W (asymmetric), cluster states (local), Bell pairs - essential for topology studies
- **Noise Models**: All 5 physics-compliant models (depolarizing, amplitude damping, phase damping, bit flip, thermal relaxation)
- **Quantitative Metrics**: Asymmetry Index (AI), Pathway Concentration Ratio (PCR), Entanglement-Error Correlation (EEC), Temporal Pathway Stability (TPS), Complexity Emergence Score (CES)
- **Parameter Sweeps**: Systematic noise strength studies (p ∈ [0.005, 0.01, 0.02, 0.05, 0.1]) with statistical validation
- **Precision Analysis**: 10,000-shot experiments with 5-run statistical validation
- **Research Visualization**: Error pattern histograms, pathway analysis plots, publication-ready exports

## Development Commands

### Running Experiments

**Interactive Mode:**
```bash
python main.py                    # Start interactive CLI
```

**Research Experiments:**
```bash
# Threshold mapping experiments (1-5 qubits)
python main.py --run ghz_basic                    # 3-qubit GHZ baseline
python main.py --run ghz_5q_decoherence           # 5-qubit complexity study

# Topology comparison experiments  
python main.py --run ghz_structured_decoherence_ref    # GHZ symmetric entanglement
python main.py --run w_structured_decoherence          # W asymmetric entanglement
python main.py --run bell_decoherence                  # Bell pair studies

# Custom experiment configurations
python main.py run --config experiments/threshold_study.json
```

**Parameter Sweeps (Critical for Research):**
```bash
# Systematic noise strength studies
python main.py sweep --manifest experiments/ghz_5q_sweep_manifest.json
python main.py --sweep ghz_structured_decoherence_ref

# Noise model comparison studies
python main.py sweep --manifest experiments/noise_model_comparison.json
```

**Research Analysis & Visualization:**
```bash
# Error pattern analysis (essential for pathway detection)
python main.py --viz results/structured_decoherence/latest.json --type histogram

# Quantitative pathway metrics
python main.py analyze --results results/structured_decoherence/ --metrics all
python main.py analyze --results results/ --metric asymmetry_index
python main.py analyze --results results/ --metric pathway_concentration

# Publication-ready exports
python main.py export --results results/threshold_study/ --format paper
```

### Testing

**Run all tests:**
```bash
pytest                           # Run full test suite
pytest tests/engine/            # Test engine components only  
pytest tests/cli/               # Test CLI components only
pytest -k "test_ghz"           # Run specific test patterns
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html
```

### Development Tools

**Schema generation (when modifying models):**
```bash
python tools/gen_schemas.py     # Regenerate JSON schemas from Pydantic models
```

**Smoke tests:**
```bash
python scripts/smoke_cli_checks.py  # Quick CLI validation
```

## Key Architectural Patterns

### Engine-First Design (Current Refactor)
The project is migrating to an "engine-first" architecture where:
- **Engine API** (`src/engine/api.py`) provides `run()` and `sweep()` functions
- **Pydantic models** (`src/engine/models.py`) define all data contracts
- **Storage layer** (`src/engine/storage.py`) handles deterministic file paths
- **Event bus** (`src/engine/events.py`) decouples progress reporting

**Feature flag:** Set `QEXP_USE_ENGINE_API=1` to use the new engine paths.

### Physics Compliance
All noise models enforce quantum physics constraints:
- **CPTP (Completely Positive Trace Preserving)** channel validation
- **T2 ≤ 2*T1 constraint** for thermal relaxation
- **Physical error bounds** (e.g., 3/4 max for single-qubit depolarizing)
- **Gate timing dependencies** with realistic hardware parameters

### Experiment Management
Experiments are organized in a registry system:
- **Presets** in `src/experiments/presets/` organized by difficulty
- **Factory pattern** for state preparation and noise model creation
- **Composable components** with mixins for noise, analysis, and visualization

### Data Model
- **ExperimentConfig**: Input parameters and settings
- **ExperimentResult**: Complete results with raw data, metrics, and artifacts
- **Provenance**: Full reproducibility tracking (versions, git SHA, seed, etc.)
- **ArtifactRef**: References to saved files (plots, animations, reports)

## Configuration and Settings

### Environment Variables
```bash
# Engine behavior
QEXP_USE_ENGINE_API=1           # Use new engine API
QUANTUM_INTERACTIVE=true        # Enable interactive mode

# Logging
QUANTUM_LOG_LEVEL=INFO          # Set log level
QEXP_LOGS_DIR=logs              # Log directory

# Experiment defaults
QEXP_NUM_QUBITS=3               # Default qubit count
QEXP_STATE_TYPE=GHZ             # Default quantum state
QEXP_NOISE_TYPE=DEPOLARIZING    # Default noise model
QEXP_SHOTS=1024                 # Default measurement shots
```

### Profiles System
The framework supports configuration profiles for different use cases:
```bash
python main.py --profile research    # Apply research profile
python main.py --profile beginner    # Apply beginner profile
```

## File Organization

### Results Structure
```
results/
├── structured_decoherence/      # Decoherence experiment results
├── parameter_sweeps/            # Parameter sweep results  
└── visualizations/              # Generated plots and animations
    ├── histograms/
    ├── density_matrices/
    ├── hypergraphs/
    └── animations/
```

### Key Configuration Files
- `requirements.txt` - Python dependencies
- `schemas/*.json` - Auto-generated JSON schemas from Pydantic models
- `src/config/settings.py` - Application settings and defaults

## Important Development Notes

### Current Refactor Status: Research Optimization
The project is undergoing targeted refactoring to optimize for structured decoherence pathway research:
- **Scientific Core**: ✅ All 5 noise models validated, parameter sweeps robust
- **Quantitative Metrics**: 🚧 Implementing AI, PCR, EEC, TPS, CES metrics  
- **Research Engine API**: 🚧 Clean scientific interface for systematic studies
- **Visualization Simplification**: 📋 Remove bloat, keep essential error pattern analysis
- **CLI Research Focus**: 📋 Streamline to research commands only
- **Framework Cleanup**: 📋 Remove unnecessary complexity while preserving scientific rigor

### Testing Strategy
- **Unit tests** for all core modules with physics validation
- **Integration tests** for complete workflows
- **Smoke tests** for CLI and basic functionality
- **Feature-flagged testing** for both legacy and engine paths

### Code Quality Standards
- **Pydantic models** as source of truth for all data structures
- **Physics validation** with clear error messages for invalid parameters
- **Deterministic hashing** for reproducible results and file paths
- **Structured logging** with JSON output for analysis
- **Strong typing** throughout with mypy validation

## Research Features: Structured Decoherence Pathways

### Quantitative Pathway Metrics (Core Research Tools)
- **Asymmetry Index (AI)**: Measures deviation from uniform error distribution
- **Pathway Concentration Ratio (PCR)**: Quantifies error clustering in specific patterns  
- **Entanglement-Error Correlation (EEC)**: Correlates entanglement topology with error patterns
- **Temporal Pathway Stability (TPS)**: Measures pathway consistency across noise levels
- **Complexity Emergence Score (CES)**: Quantifies entanglement threshold for pathway emergence

### Advanced Analysis Infrastructure  
- **Information theory**: Shannon entropy, mutual information for pathway characterization
- **Decoherence dynamics**: Error pattern clustering, pathway transition tracking
- **Topology mapping**: Network analysis of entanglement structure vs. error propagation
- **Statistical validation**: Multi-run confidence intervals, significance testing

### Publication-Ready Output
- **Structured JSON** results with complete metadata
- **Statistical validation** with confidence intervals
- **Provenance tracking** for full reproducibility  
- **LaTeX-ready** tables and publication-quality plots

### Parameter Sweeps
Automated systematic exploration with:
- **Configurable ranges** for any experiment parameter
- **Statistical aggregation** across multiple runs
- **Convergence analysis** and significance testing
- **Visualization** of parameter dependencies

## Research Workflow Patterns: Structured Decoherence Studies

### Threshold Mapping Study (Phase 1)
```bash
# 1. Run systematic qubit complexity study
python main.py --run single_qubit_superposition     # Baseline (no pathways expected)
python main.py --run bell_pair_study                # 2-qubit (threshold test)
python main.py --run ghz_3q_structured_decoherence  # 3-qubit (pathway emergence)
python main.py --run ghz_4q_structured_decoherence  # 4-qubit (pathway confirmation)
python main.py --run ghz_5q_structured_decoherence  # 5-qubit (scaling study)

# 2. Analyze threshold patterns
python main.py analyze --results results/threshold_study/ --metric complexity_emergence
```

### Topology Comparison Study (Phase 2)
```bash
# 1. Run different entanglement topologies
python main.py --run ghz_structured_decoherence_ref  # Symmetric entanglement
python main.py --run w_structured_decoherence        # Asymmetric entanglement  
python main.py --run cluster_structured_decoherence  # Local correlations

# 2. Analyze pathway signatures
python main.py analyze --results results/topology_study/ --metric asymmetry_index
python main.py analyze --results results/topology_study/ --metric pathway_concentration
```

### Parameter Sweep Studies (Critical)
```bash
# 1. Systematic noise strength sweeps (p ∈ [0.005, 0.01, 0.02, 0.05, 0.1])
python main.py sweep --manifest experiments/ghz_5q_sweep_manifest.json

# 2. Multi-noise model validation
python main.py sweep --manifest experiments/noise_model_comparison.json

# 3. Statistical analysis across sweeps  
python main.py analyze --results results/parameter_sweeps/ --metric temporal_pathway_stability
```

### Interactive Development
```bash
# Start interactive mode for exploration
python main.py

# Use menu system to:
# - Browse available experiments
# - Customize parameters interactively
# - View recent results
# - Manage settings and profiles
```

This framework is specifically optimized for structured decoherence pathway research - a potentially groundbreaking investigation into whether quantum decoherence follows predictable network patterns rather than random distributions. The framework maintains research-grade rigor while providing clear, focused tools for this specific scientific hypothesis.