# QForge: Comprehensive Architecture & Capabilities

**Version:** 0.2.0 (Refactor/Simplify Branch)
**Status:** Beta (Stable Core, Research-Ready)

## 1. Executive Summary

The QForge is a specialized Python library designed for **Structured Decoherence Research**. Unlike general-purpose quantum tools, it focuses specifically on analyzing how quantum information decays in entangled systems. It provides a rigorous, "physics-first" environment for testing hypotheses about the relationship between entanglement topology and error propagation.

## 2. System Architecture

The codebase follows a strict separation of concerns between the **Scientific Kernel** (`src/core`) and the **Execution Engine** (`src/engine`).

### A. The Scientific Kernel (`src/core`)

_Pure physics logic. Independent of execution environment._

- **`state_preparation/`**: Implements the **Factory Pattern** for quantum states.
  - **Capabilities**: Generates GHZ, W, Cluster, Bell, and Superposition states.
  - **Key Feature**: Supports "Parametric States" (custom angles) for sensitivity analysis.
- **`noise_models/`**: Physics-compliant decoherence channels.
  - **Capabilities**: Depolarizing, Amplitude/Phase Damping, Thermal Relaxation.
  - **Key Feature**: `create_noise_model_for_hardware()` validates theoretical noise parameters against physical hardware constraints (e.g., ensuring $T_2 \le 2T_1$).
- **`analysis/`**: The research heart of the framework.
  - **`metrics/`**: Custom research metrics including:
    - **EEC (Entanglement-Error Correlation)**: Correlates error topology with state topology.
    - **PCR (Pathway Concentration Ratio)**: Measures if errors localize in specific qubits.
    - **Structure Score**: Jensen-Shannon divergence between the observed distribution and its factorized (independent-marginals) null model. (Distinct from the Asymmetry Index, which is TVD from uniform.)
  - **`pipelines/`**: Automated analysis workflows (e.g., `pathway_analysis.py`).

### B. The Execution Engine (`src/engine`)

_Orchestration, I/O, and Qiskit integration._

- **`models/`**: **Pydantic** data models (v2) that enforce strict schema validation for Configs, Results, and Sweeps.
- **`experiment_runner.py`**: The atomic unit of execution. Handles transpilation, simulation (Aer), and result collection.
- **`sweep_driver.py`**: Manages multi-dimensional parameter sweeps (e.g., `error_rate` vs. `qubit_count`).
- **`storage.py`**: Handles JSON serialization and artifact management, ensuring all data is saved with provenance (hashes, timestamps).

---

## 3. Detailed Folder Structure

```text
src/
├── core/                           # SCIENTIFIC KERNEL
│   ├── math/                       # Shared math primitives (single source of truth):
│   │   │                           #   Pauli matrices, relaxation_probability,
│   │   │                           #   TVD/Gini, canonical qubit indexing
│   ├── analysis/
│   │   ├── core/                   # Information theory basics (Entropy, Mutual Info)
│   │   ├── metrics/                # Research metrics (EEC, PCR, Structure Score)
│   │   └── pipelines/              # Analysis workflows
│   ├── noise_models/               # Physics-compliant noise channels
│   └── state_preparation/          # Quantum state factories
│
├── engine/                         # ORCHESTRATION LAYER
│   ├── models/                     # Pydantic data models (Config, Results, Sweep)
│   ├── visualization/              # Plotting services
│   ├── experiment_runner.py        # Single experiment execution
│   ├── research_handler.py         # High-level research API
│   ├── storage.py                  # Artifact management & I/O
│   └── sweep_driver.py             # Parameter sweep orchestration
│
└── experiments/                    # CONCRETE EXPERIMENTS
    ├── sst_hypothesis_q1.py        # "Structured Decoherence" hypothesis tests
    └── ...
```

---

## 4. Current Capabilities

### 1. Structured Hypothesis Testing

- **What it does**: Automatically tests if specific entangled states (e.g., GHZ-5) exhibit "structured decay" compared to random baselines.
- **How**: It compares the `StructureScore` of the target state against a `SuperpositionState` (control) under identical noise conditions.

### 2. Physics-Aware Simulation

- **What it does**: Simulates noise that respects physical laws (Kraus operator formalism).
- **How**: The `NoiseFactory` rejects unphysical parameters (e.g., negative probabilities, invalid T1/T2 ratios) before simulation begins.

### 3. Automated Data Pipelines

- **What it does**: Runs experiments $\rightarrow$ Computes Metrics $\rightarrow$ Validates Schema $\rightarrow$ Saves JSON.
- **How**: The `Runner` class integrates with `src.analysis` to compute metrics on-the-fly, ensuring no raw data is stored without its corresponding analysis.

### 4. Analytical Validation ("Gold Standard")

- **What it does**: Verifies the software produces exact theoretical values for known states.
- **How**: `tests/physics/test_analytical.py` checks, for example, that a Bell state has exactly 0 entropy and perfect correlation, ensuring the metrics are mathematically sound.

---

## 5. Research Workflow

1. **Define Configuration**: Create an `ExperimentConfig` (JSON/Dict) specifying qubits, state type, and noise model.
2. **Execute**: Pass config to `experiment_runner.py`.
   - _Engine_ builds the circuit via `src.core.state_preparation`.
   - _Engine_ builds noise via `src.core.noise_models`.
   - _Engine_ runs simulation on Qiskit Aer.
3. **Analyze**:
   - Raw counts are passed to `src.core.analysis.metrics`.
   - Metrics (EEC, PCR, etc.) are computed.
4. **Store**:
   - Results are validated against `MeasurementResults` schema.
   - Saved to `results/` with unique hash and timestamp.

## 6. Integration Points for AI Analysis

If analyzing this codebase with an LLM, focus on:

1. **`src/core/analysis/metrics/`**: To understand the novel scientific contributions (EEC, PCR).
2. **`src/engine/models/`**: To understand the data structure and schema constraints.
3. **`tests/physics/`**: To verify the scientific accuracy of the implementation.
