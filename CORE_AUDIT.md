# Core Directory Audit & Architecture Documentation

## Current Engine-Core Integration

### Active Engine Dependencies
```
src/engine/api.py → src/core/research_handler.py
src/engine/runner.py → src/core/experiment_runner.py  
src/engine/analysis/research_integration.py → src/core/analysis/structured_decoherence/pathway_metrics.py
```

### Core Directory Structure Analysis

#### ✅ CLEAN - Noise Models (`src/core/noise_models/`)
- `amplitude_damping.py` - Physics-compliant amplitude damping
- `base_noise.py` - Abstract noise base class
- `bit_flip.py` - Bit flip noise implementation  
- `depolarizing.py` - Depolarizing noise with validation
- `noise_factory.py` - Factory pattern for noise creation
- `phase_damping.py` - Phase damping implementation
- `phase_flip.py` - Phase flip noise
- `thermal_relaxation.py` - T1/T2 thermal relaxation
- **Status**: Clean, no CLI dependencies, used by experiment_runner

#### ✅ CLEAN - State Preparation (`src/core/state_preparation/`)
- `base_state.py` - Abstract state base class
- `bell_state.py` - Bell state preparation
- `cluster_state.py` - Cluster state implementation
- `custom_state.py` - Custom state support
- `ghz_state.py` - GHZ state preparation  
- `state_constants.py` - State type constants
- `state_factory.py` - Factory pattern for state creation
- `superposition_state.py` - Superposition states
- `w_state.py` - W state implementation
- **Status**: Clean, no CLI dependencies, used by experiment_runner

#### ✅ CLEAN - Analysis Core (`src/core/analysis/core/`)
- `bloch.py` - Bloch sphere analysis (clean)
- `correlations.py` - Quantum correlations
- `information_theory.py` - Shannon entropy, mutual information
- **Status**: Clean, no external dependencies

#### ✅ CLEAN - Structured Decoherence (`src/core/analysis/structured_decoherence/`)
- `pathway_analysis.py` - Research pathway analysis
- `pathway_metrics.py` - AI, PCR, EEC metrics computation  
- **Status**: Clean, used by engine analysis

#### ✅ CLEAN - Analysis Dynamics (`src/core/analysis/dynamics/`)
- `clustering.py` - Pathway clustering
- `decoherence.py` - Fubini-Study distance
- `transitions.py` - State transitions
- **Status**: Clean analysis modules

#### ✅ CLEAN - Analysis Symmetry (`src/core/analysis/symmetry/`)
- `symmetry.py` - Symmetry analysis
- **Status**: Clean

#### ✅ ACTIVE - Core Runners
- `experiment_runner.py` - **ACTIVE** - Main quantum execution
- `research_handler.py` - **ACTIVE** - Research analysis and JSON output

#### ❌ LEGACY - To Clean Up
- `parameter_sweep.py` - **HAS CLI DEPENDENCY** (rich progress bars)
  - Uses `from rich.progress import ...`
  - Uses `from ..experiments.manager import get_experiment_manager`
  - **Action**: Remove or clean up CLI dependencies

## Issues Found

### 1. CLI Dependencies in Core
- `src/core/parameter_sweep.py` imports `rich` progress bars
- Should be engine responsibility, not core

### 2. Experiments Module Dependencies  
- `parameter_sweep.py` imports from `src.experiments.manager`
- Creates coupling between core and experiments

### 3. Utils Dependencies
- `experiment_runner.py` and `noise_factory.py` import from `src.utils`
- Should use standard logging

## Recommended Cleanup

### 1. Remove CLI Dependencies
- Remove `rich` imports from `parameter_sweep.py`
- Move progress reporting to engine layer

### 2. Decouple from Experiments Module
- Remove `get_experiment_manager` dependency
- Keep core focused on quantum mechanics only

### 3. Clean Utils Dependencies
- Replace `src.utils.logger` with standard Python logging
- Remove coupling to framework utilities

## Clean Architecture Vision

```
┌─────────────────────────────────────┐
│ Engine Layer                        │
│ • API endpoints                     │  
│ • Progress reporting               │
│ • High-level orchestration        │
├─────────────────────────────────────┤
│ Core Layer (Pure Quantum)          │
│ • Noise models (physics-compliant) │
│ • State preparation               │  
│ • Quantum analysis                │
│ • Research metrics               │
│ • No CLI/UI dependencies        │
└─────────────────────────────────────┘
```

## Files That Need Attention

1. **src/core/parameter_sweep.py** - Remove rich/CLI dependencies
2. **src/core/experiment_runner.py** - Clean utils imports  
3. **src/core/noise_models/noise_factory.py** - Clean utils imports

## Engine Integration Points

The engine should interact with core through these clean interfaces:

1. **Quantum Execution**: `ExperimentRunner.run_experiment()`
2. **Research Analysis**: `ResearchExperimentHandler.process_experiment_result()`  
3. **Structured Decoherence**: Pathway metrics computation functions
4. **Noise Models**: Factory pattern via `create_noise_model()`
5. **State Preparation**: Factory pattern via `create_quantum_state()`