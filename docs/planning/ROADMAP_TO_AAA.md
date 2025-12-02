# Roadmap to AAA+ Research Software

This document outlines the strategic plan to elevate the `qiskit-experiment-framework` from a functional prototype to a **AAA+ research-grade software package**.

**Current Status**: Functional, modular, but lacking rigorous scientific validation tests and comprehensive documentation.
**Goal**: A robust, reproducible, and mathematically verified framework suitable for high-impact publication and community adoption.

---

## Phase 1: Scientific Rigor & Validation (The "Physics")

The highest priority is ensuring the numbers are correct. We cannot publish if the math is shaky.

### 1.1. Exact Physics Test Suite (`tests/physics/`)

- **Objective**: Verify metrics against analytical solutions, not just "reasonable" values.
- **Tasks**:
  - [ ] **Analytical Baselines**: Create `tests/physics/test_analytical.py`.
    - Assert `entropy(GHZ_ideal) == 1.0` (bits) exactly.
    - Assert `entropy(Separable) == 0.0` exactly.
    - Assert `EEC(GHZ) == 1.0` exactly.
  - **Property-Based Testing**: Use `hypothesis` library to generate random valid probability distributions and assert invariants:
    - $0 \le H(p) \le \log_2(d)$
    - $MI(X;Y) \ge 0$
    - $Symmetry(A, B) \implies MI(A;B) == MI(B;A)$
  - **Numerical Stability**: Test with extreme values (probabilities near $10^{-16}$, highly skewed distributions) to ensure `log(0)` handling is robust.

### 1.2. Null Model Validation

- **Objective**: Prove that "structure" is not a statistical artifact.
- **Tasks**:
  - [ ] **Bootstrap Calibration**: Verify that the bootstrap confidence intervals cover the true value 95% of the time for known distributions.
  - [ ] **Null Model Distribution**: Verify that the "Structure Score" for purely random noise follows the expected distribution (e.g., Chi-squared or similar) under the null hypothesis.

---

## Phase 2: Software Engineering Excellence (The "Code")

Make the codebase maintainable, readable, and robust.

### 2.1. Strict Typing & Static Analysis

- **Objective**: Eliminate runtime type errors.
- **Tasks**:
  - [ ] **Strict Mypy**: Enforce `mypy --strict` across `src/`.
  - [ ] **Pydantic Validation**: Ensure all inputs to the `Engine` are validated via Pydantic models _before_ execution starts.
  - [ ] **Ruff Integration**: Replace `flake8`/`isort` with `ruff` for faster, more comprehensive linting.

### 2.2. API Stabilization

- **Objective**: A clean, intuitive surface for users.
- **Tasks**:
  - [ ] **Public API Definition**: Explicitly define `__all__` in `src/__init__.py` and submodules.
  - [ ] **Facade Pattern**: Ensure users only import from `qiskit_experiment_framework.api` or similar, never deep internal paths.
  - [ ] **Deprecation Policy**: Establish a clear way to mark features as experimental vs. stable.

### 2.3. Performance Profiling

- **Objective**: Handle large-scale experiments (e.g., 20+ qubits).
- **Tasks**:
  - [ ] **Benchmark Suite**: Create `tests/benchmarks/` using `pytest-benchmark`.
  - [ ] **Vectorization**: Ensure all metric calculations use vectorized `numpy` operations (no Python loops over outcomes).
  - [ ] **Memory Profiling**: Check memory usage for large $N$ (outcomes scale as $2^N$).

---

## Phase 3: Reproducibility & Data Management (The "Science")

Ensure that results can be reproduced by anyone, anywhere, anytime.

### 3.1. Provenance Tracking

- **Objective**: Every result file knows how it was created.
- **Tasks**:
  - [ ] **Metadata Injection**: Automatically inject git commit hash, dirty status, and installed package versions into every `ExperimentResult`.
  - [ ] **Config Serialization**: Save the exact `ExperimentConfig` JSON alongside the results.

### 3.2. Environment Management

- **Objective**: "It works on my machine" is not acceptable.
- **Tasks**:
  - [ ] **Lock Files**: Commit `poetry.lock` or `requirements.lock`.
  - [ ] **Docker Container**: Provide a `Dockerfile` that builds a pristine environment for running the framework.

---

## Phase 4: Documentation & Dissemination (The "Impact")

If it's not documented, it doesn't exist.

### 4.1. Theory Documentation

- **Objective**: Explain _why_ we are doing this, not just _how_.
- **Tasks**:
  - [ ] **Math Specs**: Write LaTeX-heavy markdown files explaining the derivation of AI, PCR, EEC, and CES.
  - [ ] **Interactive Tutorials**: Create Jupyter notebooks (`docs/tutorials/`) demonstrating the "Fog vs River" effect with visual plots.

### 4.2. Developer Documentation

- **Objective**: Lower the barrier to entry for contributors.
- **Tasks**:
  - [ ] **Architecture Diagrams**: Visual maps of how `Engine`, `Analysis`, and `Storage` interact.
  - [ ] **Contribution Guide**: Clear instructions on running tests, linting, and submitting PRs.

---

## Phase 5: Pathway Geometry Visualization (The "Seeing")

Recover and extend quantum geometry visualization tools for pathway analysis.

### 5.1. Hypergraph Visualization Recovery

- **Objective**: Restore valuable quantum geometry tools from pre-refactor codebase.
- **Source**: `main` branch `src/visualization/hypergraph.py` (879 lines)
- **Tasks**:
  - [ ] **Recover Core Functions**: Extract and modernize key functions to `src/core/analysis/geometry/`
  - [ ] **Integrate with Metrics**: Connect geometry measures to existing structured decoherence pipeline
  - [ ] **Add Research Context**: Document SST relevance for each measure

### 5.2. Key Measures to Recover (SST Relevance)

| Function | What It Does | SST Research Value |
|----------|--------------|-------------------|
| **`compute_fubini_study_distance()`** | Quantum distance between density matrices | **HIGH**: Measures "distance traveled" in reconfiguration space during decoherence. Could quantify pathway length and detect shortcuts vs scenic routes. |
| **`compute_su2_symmetry()`** | SU(2) symmetry analysis from measurement counts | **HIGH**: Symmetry breaking is central to SST — this measures how decoherence destroys rotational invariance along specific pathways. |
| **`compute_su3_symmetry()`** | SU(3) symmetry for higher-dimensional systems | **MEDIUM**: Useful for qutrit extensions and exploring richer substrate geometry. |
| **`plot_error_transition_graph()`** | Visualize transitions between error states | **HIGH**: Direct visualization of pathway structure — which bitstrings flow to which others. |
| **`compute_parity_distribution()`** | Parity analysis of measurement outcomes | **MEDIUM**: Parity conservation/violation tracks pathway topology. |
| **`compute_conditional_correlations()`** | Correlations conditioned on measurement outcomes | **HIGH**: Essential for H_Q3 sensor qubit experiments — how does observing the sensor constrain main system pathways? |
| **`compute_bloch_vector()`** + **`plot_bloch_sphere_vectors()`** | Bloch sphere visualization | **MEDIUM**: Educational value for showing single-qubit pathway trajectories. |

### 5.3. New Geometry Measures (Future)

- [ ] **Pathway Curvature**: Measure how "straight" vs "curved" decoherence trajectories are in state space
- [ ] **Geodesic Deviation**: Compare actual pathways to shortest paths (geodesics) in Hilbert space
- [ ] **Topology Persistence**: Use persistent homology to detect topological features of pathway networks

---

## Phase 6: Codebase Cleanup (The "Pruning")

Remove legacy code and dead imports from the refactor.

### 6.1. Legacy Code Audit

- **Objective**: Identify and remove code that's no longer used post-refactor.
- **Tasks**:
  - [ ] **Dead Import Analysis**: Find imports that reference removed modules
  - [ ] **Orphaned Functions**: Identify functions never called from active code paths
  - [ ] **Deprecated Patterns**: Remove old patterns superseded by new architecture
  - [ ] **Test Coverage Gaps**: Ensure removed code doesn't leave untested paths

### 6.2. Architecture Alignment

- **Objective**: Ensure all code follows the engine-first architecture.
- **Tasks**:
  - [ ] **Layer Violations**: Find code that violates AGENTS.md layer boundaries
  - [ ] **Circular Dependencies**: Detect and break circular import chains
  - [ ] **API Surface Cleanup**: Remove internal functions from public `__all__` exports

---

## Phase 7: Framework Generalizability (The "Abstraction")

Make explicit that SST is one use case, not the framework's identity.

### 7.1. ExperimentProgram Abstraction

- **Objective**: Formalize the "pluggable experiment" pattern.
- **Tasks**:
  - [x] **Create Protocol**: Add `src/experiments/base.py` with `ExperimentProgram` protocol
  - [x] **Refactor SST Experiments**: Refactored `sst_hypothesis_q1.py` and `sst_hypothesis_q1_structured.py` to implement the protocol
  - [x] **Add Registry**: Create `EXPERIMENT_REGISTRY` in `src/experiments/__init__.py`
  - [x] **Add README**: Created `src/experiments/README.md` with usage guide

### 7.2. Non-SST Experiment (Proof of Generality)

- **Objective**: Prove the framework works for experiments unrelated to structured decoherence.
- **Tasks**:
  - [x] **Bell Correlation Experiment**: Implemented as `src/experiments/bell_correlation.py`
    - Uses existing Bell state preparation (all 4 variants: Φ+, Φ-, Ψ+, Ψ-)
    - Computes correlation coefficient, fidelity, classical bound comparison
    - Demonstrates framework is not SST-specific
  - [x] **Register in EXPERIMENT_REGISTRY**: Available as `bell_correlation`
  - [x] **Bug fix**: Fixed `custom_params` handling in engine runner

### 7.3. Thin CLI Wrapper

- **Objective**: Provide command-line access without bloating the core.
- **Tasks**:
  - [x] **Create CLI**: Add `src/cli.py` using `typer`
  - [x] **Commands**:
    - `qxf run <name>` — Run predefined experiment by name with `-s key=value` overrides
    - `qxf run-config <path>` — Run from JSON config file
    - `qxf list` — List available experiment programs
  - [x] **Entry Point**: Add `qxf` command in `pyproject.toml`
  - [x] **Keep It Thin**: CLI = parser + caller + printer, no domain logic

### 7.4. Documentation Updates

- **Objective**: Make generalizability obvious to users and contributors.
- **Tasks**:
  - [ ] **Architecture Doc**: Add "Experiments as Modular Programs" section
  - [x] **Tutorial**: How to add a new experiment using `ExperimentProgram` (see `src/experiments/README.md`)
  - [x] **CLAUDE.md**: Document the abstraction pattern
  - [x] **AGENTS.md**: Updated `src/experiments/AGENTS.md` with new pattern

---

## Immediate Next Steps (The "Sprint")

1. **Fix the Science**: Implement `tests/physics/test_analytical.py` to guarantee our metrics are correct.
2. **Lock the Environment**: Generate a lock file to ensure consistent installs.
3. **Document the Theory**: Flesh out `docs/research-docs/` with the mathematical definitions used in the code.
4. **Audit Legacy Code**: Run comprehensive analysis to identify dead code from refactor.
5. **Recover Hypergraph**: Extract valuable geometry functions to new `src/core/analysis/geometry/` module.
6. **Framework Generalizability**: Implement `ExperimentProgram` abstraction and Bell/CHSH experiment.
