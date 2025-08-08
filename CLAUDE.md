# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **research-grade quantum experiment framework** built on Qiskit for conducting quantum computing experiments with noise modeling, state preparation, and advanced analysis. The project is currently undergoing an "engine-first" refactor to decouple the core execution from the CLI and make it web-ready.

## Architecture Overview

The framework uses a modular architecture with clean separation of concerns:

### Core Layers
- **Engine** (`src/engine/`) - Clean importable library with unified API
- **Core** (`src/core/`) - Quantum logic (state preparation, noise models, analysis)
- **CLI** (`src/cli/`) - Command-line interface (interactive and headless)
- **Visualization** (`src/visualization/`) - Multi-backend plotting and reporting
- **Experiments** (`src/experiments/`) - Preset experiments and management

### Key Components
- **State Preparation**: GHZ, Bell, superposition, W-states, cluster states, custom states
- **Noise Models**: Physics-compliant models with quantum constraints (T2≤2*T1)
- **Analysis**: Information theory, correlations, decoherence dynamics, symmetry analysis
- **Visualization**: Quantum-aware histograms, density matrices, hypergraphs, animations

## Development Commands

### Running Experiments

**Interactive Mode:**
```bash
python main.py                    # Start interactive CLI
```

**Headless Mode:**
```bash
# Run specific experiments
python main.py --run ghz_basic
python main.py run --preset ghz_structured_decoherence_ref

# Run from config file
python main.py run --config path/to/config.json

# List available experiments
python main.py --list
```

**Parameter Sweeps:**
```bash
# Run parameter sweep on experiment
python main.py --sweep ghz_structured_decoherence_ref

# Run from manifest file
python main.py sweep --manifest path/to/manifest.json
```

**Visualization:**
```bash
# Visualize saved results
python main.py --viz results/analysis.json --type histogram
python main.py viz --from results/analysis.json --type density_matrix --backend matplotlib

# Generate reports
python main.py report --from results/analysis.json --format md
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

### Current Refactor Status
The project is in the middle of an "engine-first" refactor (see `docs/ENGINE_FIRST_REFACTOR_PLAN.md`):
- **Engine skeleton**: ✅ Complete
- **Pydantic models**: ✅ Complete  
- **Storage unification**: ✅ Complete
- **CLI adapter switch**: ✅ Complete (feature-flagged)
- **Visualization adapters**: ✅ Basic implementation complete
- **Interactive simplification**: 🚧 Next phase
- **Cleanup and release**: 📋 Planned

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

## Research Features

### Advanced Analysis
- **Information theory**: Shannon entropy, mutual information, quantum discord
- **Decoherence dynamics**: Cluster analysis, transition tracking
- **Symmetry analysis**: SU(2)/SU(3) symmetries, parity distributions
- **Correlations**: Quantum correlations and entanglement measures

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

## Common Workflow Patterns

### Running a Research Experiment
```bash
# 1. Run structured decoherence experiment
python main.py --run ghz_structured_decoherence_ref

# 2. Visualize results
python main.py --viz results/structured_decoherence/latest.json --type histogram

# 3. Generate research report  
python main.py report --from results/structured_decoherence/latest.json
```

### Parameter Sweep Workflow
```bash
# 1. Create sweep manifest (JSON)
# 2. Run sweep
python main.py sweep --manifest sweeps/noise_analysis.json

# 3. Analyze aggregated results
python main.py --viz results/parameter_sweeps/latest_manifest.json
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

This framework is designed for serious quantum computing research while remaining accessible for education and exploration.