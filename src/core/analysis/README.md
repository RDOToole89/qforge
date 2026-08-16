# Analysis Framework

Information-theoretic and statistical analysis of quantum measurement outcomes. Provides 8 core metrics with bootstrap confidence intervals and v1.0 schema-compliant output.

This is pure analysis code with no experiment-specific logic. Feed it measurement counts from any source -- the engine, a Jupyter notebook, or an external dataset -- and get back standardized metrics.

---

## Quick Start

### Complete Pipeline (Recommended)

```python
from src.core.analysis.pipelines.pathway_analysis import run_all_to_schema

counts = {"000": 400, "111": 400, "001": 100, "110": 100}
results = run_all_to_schema(counts)

print(f"Schema version: {results['schema_version']}")
print(f"Structure Score: {results['structure_score']['value']:.4f}")
print(f"Entanglement Correlation: {results['entanglement_error_correlation']['value']:.4f}")
```

### Individual Metrics

```python
from src.core.analysis.metrics.asymmetry_index import compute_asymmetry_index

ai = compute_asymmetry_index({"000": 400, "111": 400, "001": 100, "110": 100})
print(f"Asymmetry Index: {ai:.4f}")
```

### Registry API (With Bootstrap CIs)

```python
from src.core.analysis.metrics.registry import compute_all
import numpy as np

results = compute_all(
    counts={"000": 400, "111": 400, "001": 100, "110": 100},
    rng=np.random.default_rng(42),
)
for name, result in results.items():
    print(f"{name}: {result['value']:.4f} [{result['ci95'][0]:.3f}, {result['ci95'][1]:.3f}]")
```

---

## The 8 Metrics

| Abbrev | Name | What It Measures | Range |
|--------|------|-----------------|-------|
| **AI** | Asymmetry Index | Total Variation Distance from uniform distribution | [0, 1] |
| **PCR** | Pathway Concentration Ratio | Concentration in top vs bottom pathway quartiles | [0, inf) |
| **EEC** | Entanglement-Error Correlation | Pearson correlation between topology and MI matrices | [-1, 1] |
| **TPS** | Temporal Pathway Stability | Spearman correlation consistency across conditions | [0, 1] |
| **CES** | Complexity Emergence Score | Logistic emergence threshold detection | [0, 1] |
| **SS** | Structure Score | Jensen-Shannon divergence from factorized null model | [0, 1] |
| **CI** | Concentration Index | Top-vs-bottom quartile probability ratio (alias of PCR) | [1, ∞) |
| **TC** | Total Correlation | Multi-information across all qubits | [0, inf) |

All metrics include 95% bootstrap confidence intervals and a quality status (validated / experimental / unstable). They are general measures of measurement-outcome distributions — interpretation is left to the experiment programs that use them.

---

## Architecture

```
analysis/
  constants.py              Centralized thresholds and parameters

  metrics/                  Individual metric implementations
    registry.py               Declarative MetricSpec + compute_metric/compute_all
    schema_bridge.py          v1.0 schema conversion
    asymmetry_index.py        AI: TVD from uniform (closed-form, O(|observed|))
    complexity_emergence_score.py  CES: logistic fit with AIC model selection
    entanglement_error_correlation.py  EEC: multi-topology Pearson correlation
    temporal_pathway_stability.py  TPS: Spearman consistency + transition matrices
    pathway_concentration_ratio.py  PCR: adaptive quartile concentration
    concentration_index.py    CI: alias of the PCR quartile ratio
    pathway_persistence.py    Pathway persistence wrapper
    total_correlation.py      TC: multi-information
    noise_topology_correlation.py  NTC: permutation test for noise-topology
    structure_score.py        SS: JSD from factorized (independent-marginals) null model
    profiles.py               Metric selection profiles (decoherence, quick, information_theory)

  core/                     Mathematical foundations
    information_theory.py     Entropy, MI, JSD with Jeffreys smoothing (alpha=0.5, K=2^n)
    null_models.py            Factorized null model (SciPy-free, reproducible sampling)
    correlations.py           Topology analysis, adjacency matrix construction
    bootstrap.py              Reproducible bootstrap CIs with RNG plumbing
    topology.py               Topology builders (chain, star, ring, complete)

  pipelines/                High-level orchestration
    pathway_analysis.py       run_all_to_schema() -- complete pipeline with v1.0 output
```

---

## Registry System

Metrics are registered via a declarative `MetricSpec` pattern in `registry.py`:

```python
# Standard bootstrap-based metrics use MetricSpec:
MetricSpec(
    name="concentration_index",
    module=".pathway_concentration_ratio",
    func_name="compute_pathway_concentration_ratio",
    method_label="pathway_concentration_ratio",
)

# Special metrics (fallback chains, analysis dicts) use explicit wrappers.
```

Public API:
- `compute_metric(name, **kwargs)` -- Compute a single metric by name
- `compute_all(metric_names, **kwargs)` -- Compute multiple metrics with shared parameters
- `@register(name)` -- Decorator to register new metrics

`structure_score` (JSD from the factorized null model) and `asymmetry_index`
(TVD from uniform) are distinct, separately registered metrics.

Aliases are provided for backward compatibility:
- `pathway_concentration_ratio` -> `concentration_index`
- `temporal_pathway_stability` -> `pathway_persistence`

---

## Mathematical Foundations

### Jeffreys Smoothing

All probability estimates use Jeffreys prior smoothing with full support:
- Prior: alpha = 0.5 (Jeffreys)
- Support: K = 2^n (all possible bitstrings, not just observed)
- Smoothed probability: p(x) = (count(x) + alpha) / (N + K * alpha)

This prevents zero-probability outcomes from dominating entropy and divergence calculations.

### Canonical Ordering

All computations use lexicographic ordering of bitstrings (`000, 001, 010, ...`). This ensures deterministic results across runs and platforms.

### Bootstrap Confidence Intervals

CIs are computed via multinomial resampling with explicit RNG plumbing:
- Default: 1000 bootstrap samples
- Resampling: multinomial from observed probability distribution
- CI extraction: percentile method (2.5th, 97.5th)
- Reproducible: pass `rng=np.random.default_rng(seed)` for deterministic results
