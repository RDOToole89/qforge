# QForge: Comprehensive Design Document

**Version:** 0.2 (Beta)
**Author:** Roibín O'Toole, Research Engineering
**Date:** 2025-12-02
**Status:** Beta — Active Research Development

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Research Foundation](#2-research-foundation)
3. [System Architecture](#3-system-architecture)
4. [Core Module: Physics Primitives](#4-core-module-physics-primitives)
5. [Engine Module: Execution & Orchestration](#5-engine-module-execution--orchestration)
6. [Structured Decoherence Metrics Suite](#6-structured-decoherence-metrics-suite)
7. [Quantum State Preparation](#7-quantum-state-preparation)
8. [Noise Models](#8-noise-models)
9. [Data Flow & Execution Pipeline](#9-data-flow--execution-pipeline)
10. [API Reference](#10-api-reference)
11. [Schema System](#11-schema-system)
12. [Quality Assurance](#12-quality-assurance)
13. [Future Roadmap](#13-future-roadmap)
14. [Getting Started](#14-getting-started)
15. [Assumptions & Limitations](#15-assumptions--limitations)
16. [Appendices](#16-appendices)

---

## 1. Executive Summary

### 1.1 What Is This Framework?

The **QForge** is a research-grade quantum experimentation platform with **production-style software architecture** (schema validation, provenance tracking, modular layering). It is designed to investigate **structured decoherence pathways** in quantum systems—a novel research direction that treats decoherence as potentially structured rather than purely random.

**Current Focus:** Testing the structured decoherence hypothesis through quantitative metrics and reproducible experiments.

**Future Vision:** Although the current experiments focus on structured decoherence, the component-driven architecture is explicitly designed as a **general quantum experiment engine**. New research programs (e.g., benchmarking, entanglement witnesses, variational circuits, circuit synthesis, sensor protocols) can be implemented by:
- reusing the **core** physics layer,
- orchestrating runs via the **engine**,
- and adding new experiments under `src/experiments/`.

The clean separation between core physics, execution engine, and experiment implementations is intentional: structured decoherence is the first use case, not the only one.

### 1.2 Key Capabilities

| Capability | Description |
|------------|-------------|
| **8 Research Metrics** | Publication-ready metrics for structured decoherence detection |
| **6 Quantum States** | Educational state preparation (GHZ, W, Bell, Cluster, etc.) |
| **6 Noise Models** | Physics-compliant decoherence channels with validation |
| **Type-Safe API** | Pydantic v2 schemas throughout with strict validation |
| **Reproducible Science** | Deterministic execution with RNG plumbing and provenance tracking |
| **Schema Compliance** | v1.0 frozen schemas for interoperability |

### 1.3 Technical Statistics

```
Source Code:        65 Python modules (~15,000 lines)
Test Suite:         128 tests (all passing)
Metrics Code:       4,397 lines (research-grade)
Dependencies:       Qiskit, NumPy, SciPy (optional), Pydantic v2
Python Version:     3.11+
```

---

## 2. Research Foundation

### 2.1 The Central Hypothesis

**structured decoherence hypothesis:** Quantum decoherence follows structured pathways determined by the entanglement network topology, rather than occurring randomly across all qubits.

Traditional View:
```
Decoherence = Random noise affecting all qubits equally
             (Like fog spreading uniformly)
```

Structured decoherence view:
```
Decoherence = Structured flow along entanglement "springs"
             (Like water flowing through channels)
```

### 2.2 The Spring Network Model

The framework implements a **Spring Network Model** where:

1. **Entanglement bonds** act as springs connecting qubits
2. **Decoherence** flows preferentially along high-tension springs
3. **Error patterns** correlate with the entanglement topology
4. **Structure** emerges from the interplay of topology and noise

This model predicts that:
- GHZ states (global entanglement) show different decoherence patterns than W states (distributed entanglement)
- Error distributions are non-uniform and correlate with qubit connectivity
- Certain topologies are more robust to specific noise types

### 2.3 Research Questions

The framework is designed to answer:

| Question | Metric | Expected Signal |
|----------|--------|-----------------|
| **Q1:** Does entanglement topology influence decoherence pathways? | EEC | EEC ≠ 0 for structured states |
| **Q2:** Do errors concentrate in specific pathways? | PCR, AI | PCR > 1, AI > 0.1 |
| **Q3:** Are pathway patterns stable across conditions? | TPS | TPS > 0.5 for structured decoherence |
| **Q4:** Is there a critical threshold for structure emergence? | CES | CES identifies transition point |

### 2.4 Key Discovery: "Fog vs River"

Initial experiments using this framework revealed a **"Fog vs River"** pattern in the *joint* behavior of state + noise:

- **Fog:** When we compare superposition-like or weakly structured states against maximally ignorant noise baselines, decoherence spreads uniformly (AI ≈ 0, PCR ≈ 1).
- **River:** For highly entangled, topology-rich states (e.g., GHZ) under physically realistic noise, probability mass flows along preferred pathways (AI > 0.3, PCR > 2).

The combination of entanglement topology and noise model produces directional "currents" in outcome space. Depolarizing channels remain isotropic at the single-qubit level, but the entangled state's structure creates "river-like" channels in the resulting distribution.

**Important clarification:** The depolarizing channel itself is isotropic—it applies X, Y, and Z errors with equal probability. The structure ("River" behavior) emerges from how those symmetric errors interact with the entangled state's topology. The structured decoherence hypothesis posits that this interaction is predictable and follows the entanglement "springs."

### 2.5 Operational Hypotheses

The framework is designed to test three concrete, falsifiable operational hypotheses derived from the hypothesis:

| Hypothesis | Statement | Test Metric | Pass Criterion |
|------------|-----------|-------------|----------------|
| **H_Q1** | Entanglement topology influences decoherence pathways | EEC, AI, PCR | EEC > 0.3 for entangled states vs. EEC ≈ 0 for product states |
| **H_Q2** | Pathway structure persists across circuit depth | TPS | TPS > 0.5 across increasing noise levels |
| **H_Q3** | Sensor qubits exhibit subspace structure | SS, CI | SS > 0.2 for designated sensor qubits |

**Current Status:**
- **H_Q1**: ✅ Initial evidence supports hypothesis ("Fog vs River" discovery)
- **H_Q2**: ⏳ Planned (requires depth-sweep experiments)
- **H_Q3**: ⏳ Planned (requires sensor-qubit protocol implementation)

These hypotheses transform the abstract hypothesis into measurable predictions that the framework can systematically evaluate.

### 2.6 Connection to Structured Substrate Thesis

The **structured decoherence hypothesis** posits that quantum decoherence is not purely random, but follows structured pathways determined by the underlying entanglement network. This framework provides the experimental apparatus to test it:

```
Hypothesis Claim                    Framework Component
─────────────────────────────────────────────────────────────
Entanglement creates "springs"  →   State preparation (GHZ, W, Cluster)
Springs guide error flow        →   Noise models + EEC metric
Structure is measurable         →   8-metric suite (AI, PCR, EEC, etc.)
Structure is reproducible       →   Provenance tracking + RNG plumbing
```

**Why this matters:** If the hypothesis is correct, decoherence becomes partially predictable—opening paths for error correction strategies that leverage structure rather than fighting against noise uniformly.

### 2.7 Beyond Structured Decoherence: General Experiment Use

While the initial design and metrics suite were motivated by the Structured Substrate Thesis, the framework is intentionally **domain-general**:

- The **core layer** (`src/core/`) is agnostic to any specific hypothesis. It exposes:
  - state factories (GHZ, W, Bell, Cluster, Superposition, Custom),
  - noise models,
  - and information-theoretic tools (entropy, mutual information, divergences).
- The **engine layer** (`src/engine/`) knows nothing about "structured decoherence" as a concept. It just:
  - validates configs,
  - builds circuits,
  - runs Qiskit backends,
  - collects counts,
  - and persists results with provenance.
- The **experiments layer** (`src/experiments/`) is where "research programs" live. Structured decoherence is one such program; others can be added without touching the existing architecture.

In practice, this means the same framework could be reused for:
- cross-noise-model robustness studies,
- entanglement scaling experiments,
- VQE/ansatz evaluation with custom metrics,
- sensor-qubit protocols,
- or educational demos of canonical quantum states.

Structured decoherence is currently the **flagship** research line, but the framework itself is deliberately **general-purpose and reusable**.

---

## 3. System Architecture

### 3.1 Layered Architecture

The framework follows a strict **three-layer architecture** with unidirectional dependencies:

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXPERIMENTS                               │
│  src/experiments/                                                │
│  • Concrete hypothesis tests                                     │
│  • Research notebooks                                            │
│  • Can import from: engine, core                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                          ENGINE                                  │
│  src/engine/                                                     │
│  • Execution orchestration                                       │
│  • IO, persistence, visualization                                │
│  • Public API surface                                            │
│  • Can import from: core                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                           CORE                                   │
│  src/core/                                                       │
│  • Pure physics calculations                                     │
│  • No side effects (no IO, network)                              │
│  • Deterministic, reproducible                                   │
│  • Cannot import from: engine, experiments                       │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Directory Structure

```
qforge/
├── src/
│   ├── core/                          # Pure physics (no IO)
│   │   ├── math/                      # Shared math primitives (single source of truth)
│   │   │   ├── pauli.py                     # Pauli matrices
│   │   │   ├── rates.py                     # relaxation_probability
│   │   │   ├── distances.py                 # TVD, Gini coefficient
│   │   │   └── indexing.py                  # Canonical qubit/bit indexing
│   │   ├── analysis/                  # Research metrics & pipelines
│   │   │   ├── core/                  # Mathematical foundations
│   │   │   │   ├── information_theory.py    # Entropy, MI, divergences
│   │   │   │   ├── null_models.py           # Factorized null model
│   │   │   │   ├── correlations.py          # Topology analysis
│   │   │   │   └── bootstrap.py             # Confidence intervals
│   │   │   ├── metrics/               # Individual metric implementations
│   │   │   │   ├── asymmetry_index.py       # AI: TVD from uniform
│   │   │   │   ├── pathway_concentration_ratio.py  # PCR
│   │   │   │   ├── entanglement_error_correlation.py  # EEC
│   │   │   │   ├── temporal_pathway_stability.py  # TPS
│   │   │   │   ├── complexity_emergence_score.py  # CES
│   │   │   │   ├── structure_score.py       # SS: J-S divergence
│   │   │   │   ├── concentration_index.py   # CI: Gini coefficient
│   │   │   │   ├── total_correlation.py     # TC: Multi-information
│   │   │   │   ├── registry.py              # Metric registration
│   │   │   │   └── schema_bridge.py         # v1.0 schema conversion
│   │   │   ├── pipelines/             # High-level orchestration
│   │   │   │   └── pathway_analysis.py      # Complete analysis pipeline
│   │   │   └── constants.py           # Centralized configuration
│   │   ├── noise_models/              # Physics-compliant noise
│   │   │   ├── depolarizing.py
│   │   │   ├── amplitude_damping.py
│   │   │   ├── phase_damping.py
│   │   │   ├── thermal_relaxation.py
│   │   │   ├── bit_flip.py
│   │   │   ├── phase_flip.py
│   │   │   └── noise_factory.py
│   │   └── state_preparation/         # Quantum state factory
│   │       ├── ghz_state.py
│   │       ├── w_state.py
│   │       ├── bell_state.py
│   │       ├── cluster_state.py
│   │       ├── superposition_state.py
│   │       ├── custom_state.py
│   │       └── state_factory.py
│   │
│   ├── engine/                        # Execution & IO
│   │   ├── api.py                     # Public interface: run(), sweep()
│   │   ├── execution/                 # Runtime components
│   │   │   ├── runner.py              # Circuit execution
│   │   │   ├── context.py             # Execution context
│   │   │   └── sweep.py               # Parameter sweeps
│   │   ├── persistence/               # Data storage
│   │   │   ├── storage.py             # Atomic JSON persistence
│   │   │   └── hashing.py             # Config hashing
│   │   ├── infrastructure/            # Cross-cutting concerns
│   │   │   └── events.py              # Event bus for progress
│   │   ├── models/                    # Pydantic schemas
│   │   │   ├── config.py              # ExperimentConfig
│   │   │   ├── results.py             # ExperimentResult
│   │   │   ├── research.py            # StructuredDecoherenceMetrics
│   │   │   └── storage.py             # Artifact management
│   │   ├── analysis/                  # Research integration
│   │   │   └── research_integration.py
│   │   └── visualization/             # Plotting (optional)
│   │
│   └── experiments/                   # Concrete implementations
│       ├── sst_hypothesis_q1.py       # Primary structured decoherence experiment
│       └── sst_hypothesis_q1_structured.py
│
├── tests/                             # Test suite (128 tests)
├── schemas/                           # JSON Schema definitions (v1.0)
├── docs/                              # Documentation
└── results/                           # Experiment outputs (gitignored)
```

### 3.3 Dependency Flow

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│experiments │ ──► │   engine   │ ──► │    core    │
└────────────┘     └────────────┘     └────────────┘
      │                  │                   │
      │                  │                   │
      ▼                  ▼                   ▼
┌──────────────────────────────────────────────────┐
│                External Dependencies              │
│  • qiskit, qiskit-aer (quantum simulation)       │
│  • numpy (numerical computation)                  │
│  • scipy (optional, statistical functions)        │
│  • pydantic (schema validation)                   │
└──────────────────────────────────────────────────┘
```

### 3.4 Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Physics-First** | Core layer enforces physical validity (e.g., T₂ ≤ 2T₁) |
| **Schema-Hardened** | All data validated via Pydantic v2 models |
| **Deterministic** | Explicit RNG seeds throughout, canonical ordering |
| **Educational** | Extensive docstrings with physics explanations |
| **Reproducible** | Provenance tracking (hash, timestamp, versions) |
| **Pure Functions** | Core layer has no side effects |

---

## 4. Core Module: Physics Primitives

### 4.1 Overview

The `src/core/` module contains pure physics calculations with no side effects. Every function is deterministic and reproducible.

### 4.2 Analysis Submodule

#### 4.2.1 Information Theory (`core/information_theory.py`)

Mathematical foundations for entropy-based analysis:

```python
# Key functions
entropy(p: ndarray) -> float           # Shannon entropy in bits
mutual_information(counts, i, j)       # MI between qubits i and j
jensen_shannon_divergence(p, q)        # J-S divergence
counts_to_probabilities(counts, alpha) # Jeffreys-smoothed probabilities
```

**Smoothing Strategy:**
All probability calculations use **Jeffreys prior smoothing** with full support:

```
p̃(x) = (count(x) + α) / (N + α·K)

where:
  α = 0.5 (Jeffreys prior)
  K = 2^n (full support, including unobserved outcomes)
  N = total shots
```

#### 4.2.2 Null Models (`core/null_models.py`)

Reference distributions for structure detection:

```python
factorized_null_model(counts, alpha) -> dict[str, float]
```

The **factorized null model** Q is the maximum-entropy distribution with the same single-qubit marginals as the observed data:

```
Q(x₁, x₂, ..., xₙ) = ∏ᵢ p(xᵢ)
```

Structure Score (SS) compares observed distribution P to this null:
```
SS = D_JS(P || Q)
```

#### 4.2.3 Correlations (`core/correlations.py`)

Topology analysis for EEC computation:

```python
compute_adjacency_matrix(state_type, n_qubits) -> ndarray
compute_mutual_information_matrix(counts) -> ndarray
```

**Adjacency Matrix Construction:**

| State Type | Adjacency Pattern |
|------------|-------------------|
| GHZ | Fully connected (all-to-all) |
| W | Fully connected (symmetric) |
| Bell | Bipartite (qubit pairs) |
| Cluster | Linear chain (nearest-neighbor) |

#### 4.2.4 Bootstrap (`core/bootstrap.py`)

Reproducible confidence intervals:

```python
bootstrap_ci(
    data: ndarray,
    statistic: Callable,
    B: int = 1000,
    confidence: float = 0.95,
    rng: Generator | None = None
) -> tuple[float, float]
```

**RNG Plumbing:** All bootstrap functions accept an explicit `rng` parameter for reproducibility.

### 4.3 Constants Module

Centralized configuration in `analysis/constants.py`:

| Constant | Value | Purpose |
|----------|-------|---------|
| `ALPHA` | 0.5 | Jeffreys prior parameter |
| `EPS` | 1e-12 | Numerical stability floor |
| `DEFAULT_BOOTSTRAP_B` | 1000 | Bootstrap samples |
| `CONFIDENCE_LEVEL` | 0.95 | Standard confidence |
| `SCHEMA_VERSION` | "1.0" | Output schema version |
| `MAX_OUTCOMES_EXACT` | 2¹⁶ | Enumeration threshold |
| `STRUCTURE_MODERATE_THRESHOLD` | 0.3 | Evidence threshold |

---

## 5. Engine Module: Execution & Orchestration

### 5.1 Overview

The `src/engine/` module handles all IO, execution, and orchestration. It provides the public API surface for the framework.

### 5.2 Submodule Structure

```
engine/
├── api.py                 # Public interface
├── execution/
│   ├── runner.py          # Qiskit circuit execution
│   ├── context.py         # AppContext configuration
│   └── sweep.py           # Parameter sweep driver
├── persistence/
│   ├── storage.py         # Atomic JSON storage
│   └── hashing.py         # Deterministic config hashing
├── infrastructure/
│   └── events.py          # Event bus (RUN_START, RUN_END, etc.)
├── models/                # Pydantic schemas
│   ├── config.py          # ExperimentConfig
│   ├── results.py         # ExperimentResult, ExperimentAnalysis
│   ├── research.py        # StructuredDecoherenceMetrics
│   └── storage.py         # ArtifactRef, DirectoryStructure
└── visualization/         # Optional plotting
```

### 5.3 Execution Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                         api.run(config)                          │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  1. Config Validation (Pydantic)                                 │
│     • ExperimentConfig model validates all parameters            │
│     • Physics constraints checked (e.g., noise parameters)       │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  2. Circuit Execution (execution/runner.py)                      │
│     • State preparation via core.state_preparation               │
│     • Noise model via core.noise_models                          │
│     • Qiskit AerSimulator execution                              │
│     • Counts extraction and canonicalization                     │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  3. Analysis Assembly                                            │
│     • ExperimentAnalysis with metadata, stats, measurements      │
│     • Optional: StructuredDecoherenceMetrics computation         │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  4. Provenance & Storage (persistence/storage.py)                │
│     • Config hash, timestamp, Qiskit version                     │
│     • Atomic JSON write with artifact registration               │
└──────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│  5. Return ExperimentResult (Pydantic-validated)                 │
└──────────────────────────────────────────────────────────────────┘
```

### 5.4 Event System

The engine emits events for progress tracking:

```python
from src.engine.infrastructure.events import (
    SimpleEventBus,
    RUN_START, RUN_END,
    SWEEP_START, SWEEP_END,
    make_event
)

# Subscribe to events
bus = SimpleEventBus()
bus.subscribe(RUN_START, lambda e: print(f"Starting: {e.data}"))

# Events emitted automatically by api.run() and api.sweep()
```

| Event | Payload | When |
|-------|---------|------|
| `RUN_START` | config | Before single experiment |
| `RUN_END` | result | After single experiment |
| `SWEEP_START` | manifest | Before parameter sweep |
| `SWEEP_END` | results list | After parameter sweep |
| `PROGRESS` | progress info | During long operations |

---

## 6. Structured Decoherence Metrics Suite

### 6.1 Overview

The framework implements **8 research-grade metrics** for detecting and quantifying structured decoherence patterns. All metrics follow rigorous mathematical definitions with educational documentation.

### 6.2 Metric Summary

| Metric | Symbol | Range | Purpose |
|--------|--------|-------|---------|
| Asymmetry Index | AI | [0, 0.5] | Deviation from uniform distribution |
| Pathway Concentration Ratio | PCR | [0, ∞) | Top vs bottom pathway concentration |
| Entanglement-Error Correlation | EEC | [-1, 1] | Topology-error pattern correlation |
| Temporal Pathway Stability | TPS | [0, 1] | Consistency across conditions |
| Complexity Emergence Score | CES | [0, ∞) | Critical threshold identification |
| Structure Score | SS | [0, 1] | Jensen-Shannon from null model |
| Concentration Index | CI | [0, 1] | Gini coefficient of errors |
| Total Correlation | TC | [0, n] bits | Multi-information across qubits |

### 6.3 Detailed Metric Definitions

#### 6.3.1 Asymmetry Index (AI)

**Purpose:** Quantify deviation from uniform error distribution using Total Variation Distance (TVD).

**Mathematical Definition:**
```
AI = TVD(P, U) = (1/2) · Σᵢ |p(xᵢ) - 1/K|

where:
  P = observed probability distribution (Jeffreys-smoothed)
  U = uniform distribution over K = 2^n outcomes
  K = full support size
```

**Physical Interpretation:**
- AI = 0: Perfect uniform distribution (random decoherence)
- AI → 0.5: Maximum asymmetry (deterministic outcomes)
- AI > 0.1: Weak evidence for structured decoherence
- AI > 0.3: Moderate evidence for structured decoherence

**Computational Note:** Uses O(|observed|) closed-form calculation, avoiding O(2^n) enumeration for large systems.

#### 6.3.2 Pathway Concentration Ratio (PCR)

**Purpose:** Measure error concentration in dominant pathways vs rare pathways.

**Mathematical Definition:**
```
PCR = (Σ top 25% pathway frequencies) / (Σ bottom 25% pathway frequencies)

where frequencies are sorted in descending order
```

**Physical Interpretation:**
- PCR ≈ 1: Errors spread uniformly across pathways
- PCR > 2: Strong concentration in dominant pathways
- PCR → ∞: Errors concentrated in single pathway

#### 6.3.3 Entanglement-Error Correlation (EEC)

**Purpose:** Correlate error topology with entanglement topology.

**Mathematical Definition:**
```
EEC = ρ(A, M)  (Pearson correlation)

where:
  A = entanglement adjacency matrix (state-dependent)
  M = mutual information matrix from measurements

  A_ij = exp(-λ · d_ij)  for GHZ/W states
  M_ij = I(Xᵢ; Xⱼ) = H(Xᵢ) + H(Xⱼ) - H(Xᵢ, Xⱼ)
```

**Physical Interpretation:**
- EEC ≈ 0: No correlation (random errors)
- EEC > 0.5: Strong positive correlation (errors follow entanglement)
- EEC < -0.5: Strong negative correlation (errors avoid entanglement)

**State-Specific Adjacency:**

| State | Adjacency Pattern |
|-------|-------------------|
| GHZ | Fully connected: A_ij = 1 for all i ≠ j |
| W | Fully connected: A_ij = 1 for all i ≠ j |
| Cluster | Chain: A_ij = 1 if |i-j| = 1 |
| Bell | Bipartite: A_01 = A_10 = 1 |

#### 6.3.4 Temporal Pathway Stability (TPS)

**Purpose:** Assess consistency of pathway rankings across different noise conditions.

**Mathematical Definition:**
```
TPS = E[ρ_s(Rₜ, Rₜ₊₁)]  (mean Spearman correlation)

where:
  Rₜ = ranking of pathways at condition t
  ρ_s = Spearman rank correlation
```

**Physical Interpretation:**
- TPS > 0.5: Pathways maintain relative ranking (structured)
- TPS ≈ 0: Random reordering across conditions

**Note:** Requires multiple experimental conditions (e.g., different noise levels).

#### 6.3.5 Complexity Emergence Score (CES)

**Purpose:** Identify critical threshold where structured patterns emerge.

**Mathematical Definition:**
```
CES = n₀ from logistic fit: SS(n) = L / (1 + exp(-k(n - n₀)))

where:
  SS(n) = Structure Score at n qubits
  n₀ = emergence threshold (CES)
  k = steepness of transition
  L = maximum structure level
```

**Physical Interpretation:**
- CES identifies the qubit count where complexity "switches on"
- Systems with n > CES show structured decoherence
- Systems with n < CES show random decoherence

**Note:** Requires multi-qubit sweep data. Uses AIC for model selection.

#### 6.3.6 Structure Score (SS)

**Purpose:** Quantify deviation from the factorized (no-structure) null model.

**Mathematical Definition:**
```
SS = D_JS(P || Q)  (Jensen-Shannon divergence)

where:
  P = observed distribution
  Q = factorized null model: Q(x) = ∏ᵢ p(xᵢ)
```

**Physical Interpretation:**
- SS = 0: No structure beyond single-qubit marginals
- SS > 0: Multi-qubit correlations present
- SS → 1: Maximum structure (pure correlations)

#### 6.3.7 Concentration Index (CI)

**Purpose:** Economic inequality measure applied to error distributions.

**Mathematical Definition:**
```
CI = G(P)  (Gini coefficient)

G = (2 · Σᵢ i · p_sorted[i]) / (n · Σᵢ p_sorted[i]) - (n+1)/n
```

**Physical Interpretation:**
- CI = 0: Perfect equality (uniform errors)
- CI = 1: Maximum inequality (single dominant pathway)

#### 6.3.8 Total Correlation (TC)

**Purpose:** Measure multi-information across all qubits.

**Mathematical Definition:**
```
TC = Σᵢ H(Xᵢ) - H(X₁, X₂, ..., Xₙ)

where H(Xᵢ) is marginal entropy of qubit i
```

**Physical Interpretation:**
- TC = 0: Independent qubits (no correlation)
- TC = n-1: Maximum correlation (GHZ-like)
- Ideal 2-qubit GHZ: TC = 1 bit
- Ideal 3-qubit GHZ: TC = 2 bits

### 6.4 Using the Metrics

#### 6.4.1 Direct Pipeline Usage

```python
from src.core.analysis.pipelines.pathway_analysis import run_all_to_schema

# Your quantum measurement data
counts = {"000": 400, "111": 400, "001": 100, "110": 100}

# Compute all metrics with v1.0 schema output
results = run_all_to_schema(counts)

print(f"Schema version: {results['schema_version']}")
print(f"Structure Score: {results['structure_score']['value']:.4f}")
print(f"Asymmetry Index: {results['asymmetry_index']['value']:.4f}")
```

#### 6.4.2 Via Engine API

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

config = ExperimentConfig(
    num_qubits=4,
    state_type="GHZ",
    enable_research_metrics=True,  # Enable metric computation
    research_type="structured_decoherence",
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
    shots=2048
)

result = run(config)

# Access metrics
metrics = result.structured_decoherence_metrics
print(f"AI: {metrics.asymmetry_index:.4f}")
print(f"PCR: {metrics.pathway_concentration_ratio:.4f}")
print(f"EEC: {metrics.entanglement_error_correlation:.4f}")
print(f"Is Structured: {metrics.is_structured}")
```

#### 6.4.3 Individual Metric Computation

```python
from src.core.analysis.metrics import (
    compute_asymmetry_index,
    compute_pathway_concentration_ratio,
    compute_entanglement_error_correlation,
)

counts = {"000": 400, "111": 400, "001": 100, "110": 100}

ai = compute_asymmetry_index(counts)
pcr = compute_pathway_concentration_ratio(counts)
eec = compute_entanglement_error_correlation(counts, state_type="GHZ")

print(f"AI={ai:.4f}, PCR={pcr:.4f}, EEC={eec:.4f}")
```

### 6.5 Evidence Thresholds

| Evidence Level | AI | PCR | EEC | Interpretation |
|----------------|-----|-----|-----|----------------|
| None | < 0.1 | < 1.2 | < 0.2 | Random decoherence |
| Weak | 0.1 - 0.3 | 1.2 - 1.5 | 0.2 - 0.5 | Possible structure |
| Moderate | 0.3 - 0.5 | 1.5 - 3.0 | 0.5 - 0.8 | Likely structure |
| Strong | > 0.5 | > 3.0 | > 0.8 | Definite structure |

---

## 7. Quantum State Preparation

### 7.1 Overview

The framework provides an educational state preparation system with 6 quantum state types. Each state includes comprehensive physics documentation.

### 7.2 Supported States

| State | Mathematical Form | Entanglement Type |
|-------|-------------------|-------------------|
| **GHZ** | \|GHZ⟩ = (\|00...0⟩ + \|11...1⟩)/√2 | Global (all-or-nothing) |
| **W** | \|W⟩ = (\|100...0⟩ + \|010...0⟩ + ...)/√n | Distributed (symmetric) |
| **Bell** | \|Φ⁺⟩ = (\|00⟩ + \|11⟩)/√2 | Bipartite (2-qubit) |
| **Cluster** | Linear graph state with CZ gates | Graph-based |
| **Superposition** | \|+⟩⊗ⁿ = H⊗ⁿ\|0⟩⊗ⁿ | None (product state) |
| **Custom** | User-defined circuit | User-defined |

### 7.3 Factory Pattern Usage

```python
from src.core.state_preparation import prepare_state, prepare_state_for_hardware

# Basic usage
circuit = prepare_state(
    state_type="GHZ",
    num_qubits=4,
    seed=42  # For any randomization
)

# Hardware-optimized
circuit = prepare_state_for_hardware(
    state_type="GHZ",
    num_qubits=4,
    backend=real_backend,
    optimization_level=2
)
```

### 7.4 State Properties for Research

| State | GHZ | W | Bell | Cluster |
|-------|-----|---|------|---------|
| Max Qubits | 20 | 20 | 2 | 20 |
| Entanglement Depth | O(n) | O(n²) | O(1) | O(n) |
| Single-Qubit Loss | Destroys entanglement | Preserves (n-1)-partite | N/A | Local damage |
| Error Sensitivity | High (fragile) | Medium (robust) | Medium | Low |
| Structure Signal | Strong (River) | Medium | Medium | Weak |

### 7.5 Circuit Diagrams

**GHZ State (n=4):**
```
q0: ─[H]─●───────────
         │
q1: ─────X───●───────
             │
q2: ─────────X───●───
                 │
q3: ─────────────X───
```

**W State (n=3):**
```
q0: ─[Ry(θ₁)]─●─────────●─────
              │         │
q1: ──────────X─[Ry(θ₂)]┼──●──
                        │  │
q2: ────────────────────X──X──
```

**Cluster State (n=4):**
```
q0: ─[H]─●─────────────
         │
q1: ─[H]─Z───●─────────
             │
q2: ─[H]─────Z───●─────
                 │
q3: ─[H]─────────Z─────
```

---

## 8. Noise Models

### 8.1 Overview

The framework provides 6 physics-compliant noise models with validation to ensure physically realizable parameters.

### 8.2 Supported Noise Types

| Noise Model | Key Parameter | Physical Origin |
|-------------|---------------|-----------------|
| **Depolarizing** | error_rate (p) | Symmetric decoherence |
| **Amplitude Damping** | gamma (γ) | Energy dissipation (T₁) |
| **Phase Damping** | gamma (γ) | Dephasing (T₂*) |
| **Bit Flip** | error_rate (p) | X errors |
| **Phase Flip** | error_rate (p) | Z errors |
| **Thermal Relaxation** | T₁, T₂ | Combined T₁/T₂ processes |

### 8.3 Noise Model Details

#### 8.3.1 Depolarizing Channel

```
ε(ρ) = (1-p)ρ + (p/3)(XρX + YρY + ZρZ)

where p ∈ [0, 1] is the error probability
```

**Use Case:** General noise modeling, benchmarking

#### 8.3.2 Amplitude Damping

```
E₀ = [[1, 0], [0, √(1-γ)]]
E₁ = [[0, √γ], [0, 0]]

where γ = 1 - exp(-t/T₁)
```

**Use Case:** Energy relaxation, spontaneous emission

#### 8.3.3 Thermal Relaxation

```
Combined T₁ (energy relaxation) and T₂ (dephasing) processes

Constraint: T₂ ≤ 2T₁ (thermodynamic requirement)
```

**Use Case:** Realistic hardware simulation

### 8.4 Usage

```python
from src.core.noise_models import create_noise_model, get_available_noise_types

# List available types
print(get_available_noise_types())
# ['depolarizing', 'amplitude_damping', 'phase_damping', 'bit_flip', 'phase_flip', 'thermal_relaxation']

# Create noise model
noise = create_noise_model(
    noise_type="depolarizing",
    error_rate=0.05,
    num_qubits=4
)

# Thermal relaxation with physics validation
noise = create_noise_model(
    noise_type="thermal_relaxation",
    t1=100e-6,      # 100 μs
    t2=80e-6,       # 80 μs (must be ≤ 2*T₁)
    num_qubits=4
)
```

### 8.5 Physics Validation

The framework enforces physical constraints:

```python
# This will raise ValueError: T₂ > 2T₁ is unphysical
noise = create_noise_model(
    noise_type="thermal_relaxation",
    t1=50e-6,
    t2=120e-6  # Invalid: 120 > 2*50
)
```

---

## 9. Data Flow & Execution Pipeline

### 9.1 Single Experiment Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          User Code                                   │
│  config = ExperimentConfig(num_qubits=4, state_type="GHZ", ...)     │
│  result = run(config)                                                │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      1. Config Validation                            │
│  • Pydantic model validation                                         │
│  • Physics constraint checking                                       │
│  • Default value population                                          │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   2. State Preparation                               │
│  • StatePreparationFactory.create_state()                            │
│  • Returns QuantumCircuit with state preparation gates               │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    3. Noise Application                              │
│  • NoiseFactory.create_noise_model()                                 │
│  • Physics validation (T₂ ≤ 2T₁, etc.)                               │
│  • Returns NoiseModel for Qiskit                                     │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    4. Circuit Execution                              │
│  • Add measurement gates                                             │
│  • Transpile for backend                                             │
│  • AerSimulator.run(circuit, noise_model, shots)                     │
│  • Extract counts (MSB-left, fixed-width)                            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│              5. Research Metrics (if enabled)                        │
│  • compute_all(counts) → MetricResult objects                        │
│  • metrics_to_schema() → v1.0 schema format                          │
│  • Assemble StructuredDecoherenceMetrics                             │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    6. Result Assembly                                │
│  • ExperimentAnalysis (metadata, stats, measurements)                │
│  • Provenance (config_hash, timestamp, qiskit_version)               │
│  • Optional visualization                                            │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    7. Persistence                                    │
│  • Atomic JSON write (tmp → rename)                                  │
│  • Artifact registration                                             │
│  • Return ExperimentResult                                           │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 Parameter Sweep Flow

```python
from src.engine.api import sweep
from src.engine.models import SweepManifest

manifest = SweepManifest(
    base_config=ExperimentConfig(
        num_qubits=4,
        state_type="GHZ",
        enable_research_metrics=True,
        shots=2048
    ),
    sweep_parameters={
        "error_rate": [0.01, 0.05, 0.1],
        "noise_type": ["depolarizing", "amplitude_damping"]
    }
)

# Executes 3 × 2 = 6 experiments
results = sweep(manifest)
```

---

## 10. API Reference

### 10.1 Public API Surface

The framework exposes a minimal, stable public API:

```python
# Primary entry points
from src.engine.api import run, sweep

# Configuration
from src.engine.models import ExperimentConfig, SweepManifest

# Results
from src.engine.models import ExperimentResult
from src.engine.models.research import StructuredDecoherenceMetrics

# Direct metric access
from src.core.analysis.pipelines import run_all_to_schema
from src.core.analysis.metrics import compute_metric, compute_all
```

### 10.2 Function Signatures

#### `run(config, ctx=None) -> ExperimentResult`

Execute a single quantum experiment.

| Parameter | Type | Description |
|-----------|------|-------------|
| `config` | `ExperimentConfig \| dict` | Experiment configuration |
| `ctx` | `AppContext \| None` | Execution context (optional) |
| **Returns** | `ExperimentResult` | Validated result with analysis |

#### `sweep(manifest, ctx=None) -> list[ExperimentResult]`

Execute a parameter sweep across multiple configurations.

| Parameter | Type | Description |
|-----------|------|-------------|
| `manifest` | `SweepManifest \| dict` | Sweep specification |
| `ctx` | `AppContext \| None` | Execution context (optional) |
| **Returns** | `list[ExperimentResult]` | Results for each configuration |

### 10.3 Configuration Options

```python
ExperimentConfig(
    # Core quantum parameters
    num_qubits: int,                    # 1-20
    state_type: str,                    # GHZ, W, BELL, CLUSTER, SUPERPOSITION, CUSTOM

    # Simulation
    shots: int = 1024,                  # 1-1,000,000
    sim_mode: str = "qasm",             # Only qasm supported

    # Noise
    noise_enabled: bool = False,
    noise_type: str | None = None,      # depolarizing, amplitude_damping, etc.
    error_rate: float | None = None,    # 0.0-1.0
    t1: float | None = None,            # For thermal_relaxation
    t2: float | None = None,            # For thermal_relaxation

    # Research
    enable_research_metrics: bool = False,
    research_type: str | None = None,   # structured_decoherence, parameter_sweep, etc.

    # Visualization
    visualization_type: str = "histogram"  # histogram, none
)
```

---

## 11. Schema System

### 11.1 Overview

The framework uses **v1.0 frozen schemas** to ensure data compatibility and reproducibility. All outputs conform to these schemas.

### 11.2 Schema Hierarchy

```
schemas/
├── config.schema.json        # ExperimentConfig
├── result.schema.json        # ExperimentResult
├── metrics.schema.json       # StructuredDecoherenceMetrics
├── analysis.schema.json      # ExperimentAnalysis
└── provenance.schema.json    # Provenance metadata
```

### 11.3 Metric Schema Format

Each metric in the v1.0 schema follows this structure:

```json
{
  "metric_name": {
    "value": 0.4532,
    "status": "validated",
    "confidence_interval": [0.42, 0.49],
    "metadata": {
      "computation_time_ms": 12.5,
      "samples_used": 1000
    }
  }
}
```

### 11.4 Status Values

| Status | Meaning | Criteria |
|--------|---------|----------|
| `validated` | High confidence | CV < 0.33, samples ≥ 100 |
| `experimental` | Moderate confidence | CV < 0.50, samples ≥ 50 |
| `unstable` | Low confidence | Otherwise |

---

## 12. Quality Assurance

### 12.1 Test Suite

The framework includes 128 tests covering:

| Category | Tests | Coverage |
|----------|-------|----------|
| Unit Tests | 80+ | Core functions, metrics |
| Integration Tests | 30+ | End-to-end pipelines |
| Physics Tests | 15+ | Analytical validation |
| Property Tests | Planned | Invariant verification |

### 12.2 Running Tests

```bash
# All tests
pytest tests/

# Physics validation only
pytest tests/physics/

# With coverage
pytest --cov=src tests/
```

### 12.3 Validation Principles

1. **Mathematical Correctness:** Metrics validated against analytical solutions
2. **Numerical Stability:** Edge cases tested (near-zero probabilities, etc.)
3. **Reproducibility:** Same seed → same results
4. **Schema Compliance:** All outputs validated against JSON schemas

---

## 13. Future Roadmap

### 13.1 Phase 1: Scientific Rigor (In Progress)

| Task | Status | Priority |
|------|--------|----------|
| Exact physics test suite | Planned | High |
| Property-based testing (Hypothesis) | Planned | High |
| Bootstrap calibration validation | Planned | Medium |
| Null model distribution tests | Planned | Medium |

### 13.2 Phase 2: Software Excellence

| Task | Status | Priority |
|------|--------|----------|
| Strict mypy enforcement | Planned | High |
| Ruff integration | Planned | Medium |
| Performance benchmarks | Planned | Medium |
| Memory profiling (20+ qubits) | Planned | Low |

### 13.3 Phase 3: Reproducibility

| Task | Status | Priority |
|------|--------|----------|
| Commit poetry.lock | Planned | High |
| Docker container | Planned | Medium |
| Git commit hash in provenance | Planned | Medium |

### 13.4 Phase 4: Documentation

| Task | Status | Priority |
|------|--------|----------|
| LaTeX metric derivations | Planned | High |
| Interactive Jupyter tutorials | Planned | High |
| Architecture diagrams | Planned | Medium |
| Contribution guide | Planned | Medium |

### 13.5 Phase 5: Pathway Geometry (Research Extension)

| Task | Status | Priority |
|------|--------|----------|
| Fubini-Study distance | Planned | High |
| SU(2) symmetry analysis | Planned | High |
| Error transition graphs | Planned | High |
| Bloch sphere visualization | Planned | Medium |
| Pathway curvature | Future | Low |
| Geodesic deviation | Future | Low |

### 13.6 Research Hypotheses

| Hypothesis | Experiment | Status |
|------------|------------|--------|
| H_Q1: Topology influences pathways | sst_hypothesis_q1 | Complete |
| H_Q2: Pathway persistence in depth | Planned | Future |
| H_Q3: Sensor qubit subspaces | Planned | Future |

---

## 14. Getting Started

### 14.1 Installation

```bash
# Clone repository
git clone <repository-url>
cd qforge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -e .
# or
poetry install
```

### 14.2 Quick Start

```python
from src.engine.api import run
from src.engine.models import ExperimentConfig

# Define experiment
config = ExperimentConfig(
    num_qubits=4,
    state_type="GHZ",
    enable_research_metrics=True,
    research_type="structured_decoherence",
    noise_enabled=True,
    noise_type="depolarizing",
    error_rate=0.05,
    shots=2048
)

# Run experiment
result = run(config)

# Access results
print(f"Top outcomes: {result.analysis.measurements.top_outcomes}")

# Access research metrics
metrics = result.structured_decoherence_metrics
print(f"Asymmetry Index: {metrics.asymmetry_index:.4f}")
print(f"Pathway Concentration: {metrics.pathway_concentration_ratio:.4f}")
print(f"Entanglement Correlation: {metrics.entanglement_error_correlation:.4f}")
print(f"Is Structured: {metrics.is_structured}")
```

### 14.3 Running Existing Experiments

```bash
# Run Structured Decoherence Hypothesis Q1
python -m src.experiments.sst_hypothesis_q1

# Run structured version
python -m src.experiments.sst_hypothesis_q1_structured
```

---

## 15. Assumptions & Limitations

### 15.1 Current Scope Limitations

This framework is in **active research development (Beta v0.2)**. The following limitations apply:

| Limitation | Description | Planned Resolution |
|------------|-------------|-------------------|
| **Simulation Only** | Currently supports Qiskit Aer simulator, no direct hardware integration | Phase 3+ |
| **Qubit Limit** | Tested up to 20 qubits; 2^n scaling limits exact computation | Sampling approximations |
| **Single-Shot Analysis** | Most metrics computed per-run, limited temporal analysis | TPS metric expansion |
| **State Types** | 6 predefined states; custom states require manual circuit construction | Extended factory |

### 15.2 Theoretical Assumptions

The framework operates under these assumptions:

1. **Measurement Basis:** All measurements are in the computational (Z) basis
2. **Noise Independence:** Noise channels are applied uniformly across qubits (no spatial correlation in noise model)
3. **Markovian Noise:** Current noise models are memoryless (no non-Markovian dynamics)
4. **Ideal Preparation:** State preparation is assumed perfect (noise applied after state creation)
5. **Classical Readout:** Measurement errors are not currently modeled separately from decoherence

### 15.3 Statistical Considerations

| Consideration | Current Approach | Impact |
|---------------|------------------|--------|
| **Shot Noise** | Jeffreys smoothing (α=0.5) mitigates sparse sampling | Requires ≥100 shots for stable metrics |
| **Finite Sample Bias** | Bootstrap CI provides uncertainty quantification | Wide CIs for low shot counts |
| **Multiple Comparisons** | No correction applied | User should apply Bonferroni/FDR for multi-test studies |

### 15.4 Beta Status Implications

As a Beta v0.2 framework:

- **API Stability:** Core API (`run()`, `sweep()`) is stable; internal modules may change
- **Schema Compatibility:** v1.0 metric schemas are frozen; new metrics may be added
- **Documentation:** Comprehensive but evolving; some edge cases may lack coverage
- **Testing:** 128 tests passing, but property-based testing is planned

### 15.5 What This Framework Does NOT Claim

To be explicit about research positioning:

- **NOT** a production quantum computing platform
- **NOT** validated on real quantum hardware (yet)
- **NOT** claiming the hypothesis is proven—framework tests the hypothesis
- **NOT** a complete theory of decoherence—provides measurement tools

The framework's value is in providing **rigorous, reproducible tools** to investigate structured decoherence, not in making claims about the underlying physics.

---

## 16. Appendices

### Appendix A: Mathematical Notation

| Symbol | Meaning |
|--------|---------|
| P | Observed probability distribution |
| Q | Null model (factorized) |
| K | Full support size (2^n) |
| α | Jeffreys prior parameter (0.5) |
| H(X) | Shannon entropy of X |
| I(X;Y) | Mutual information between X and Y |
| D_JS | Jensen-Shannon divergence |
| TVD | Total Variation Distance |
| ρ | Pearson correlation |
| ρ_s | Spearman rank correlation |

### Appendix B: File Locations

| Component | Path |
|-----------|------|
| Public API | `src/engine/api.py` |
| Experiment Config | `src/engine/models/config.py` |
| Research Metrics | `src/engine/models/research.py` |
| Metric Implementations | `src/core/analysis/metrics/` |
| State Preparation | `src/core/state_preparation/` |
| Noise Models | `src/core/noise_models/` |
| Constants | `src/core/analysis/constants.py` |
| Tests | `tests/` |

### Appendix C: References

1. Nielsen, M. A., & Chuang, I. L. (2010). *Quantum Computation and Quantum Information*
2. Cover, T. M., & Thomas, J. A. (2006). *Elements of Information Theory*
3. Efron, B., & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*
4. Jeffreys, H. (1946). "An Invariant Form for the Prior Probability"
5. MacKay, D. J. C. (2003). *Information Theory, Inference and Learning Algorithms*

### Appendix D: Glossary

| Term | Definition |
|------|------------|
| **Structured decoherence** | Hypothesis that decoherence follows topology-dependent pathways |
| **GHZ State** | Greenberger-Horne-Zeilinger state |
| **W State** | Dicke state with single excitation |
| **TVD** | Total Variation Distance |
| **MI** | Mutual Information |
| **Jeffreys Prior** | Non-informative prior with α=0.5 |
| **Full Support** | All 2^n possible outcomes |
| **Provenance** | Origin tracking (hash, timestamp, versions) |

---

**Document Version:** 0.2
**Last Updated:** 2025-12-02
**Framework Version:** Beta v0.2
**Contact:** Research Engineering (Roibín O'Toole)
