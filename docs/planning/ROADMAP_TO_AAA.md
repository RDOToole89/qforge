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

## Immediate Next Steps (The "Sprint")

1. **Fix the Science**: Implement `tests/physics/test_analytical.py` to guarantee our metrics are correct.
2. **Lock the Environment**: Generate a lock file to ensure consistent installs.
3. **Document the Theory**: Flesh out `docs/research-docs/` with the mathematical definitions used in the code.
