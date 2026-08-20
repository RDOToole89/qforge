# AGENTS.md — Analysis Metrics

Owner: Roibín O'Toole
Token budget: 400

## Purpose

Information-theoretic and statistical measures of measurement-outcome distributions. Each metric follows rigorous mathematical definitions with educational documentation.

**Core Metrics**: AI, PCR, EEC, TPS, CES, SS, CI, TC (8 total)

## Critical Patterns

### 1. Full-Support Jeffreys Smoothing

**Always use K = 2^n support with α = 0.5:**

```python
# Good: Full support smoothing
from ..constants import ALPHA
K = 1 << n_qubits  # 2^n
denom = N + ALPHA * K
p_smoothed = (count + ALPHA) / denom

# Bad: Observed-only smoothing
p_bad = count / total  # Missing outcomes get p=0
```

### 2. Deterministic Ordering

**Always use canonical (lexicographic) ordering:**

```python
# Good: Sorted keys for reproducibility
outcomes = sorted(counts.keys())
probs = np.array([prob_dict[o] for o in outcomes])

# Bad: Dict iteration order
probs = np.array(list(prob_dict.values()))  # Non-deterministic!
```

### 3. RNG Plumbing for Reproducibility

**Pass RNG explicitly through all functions:**

```python
# Good: Explicit RNG parameter
def compute_metric(counts: dict, rng: np.random.Generator | None = None):
    if rng is None:
        rng = np.random.default_rng()
    # Use rng for any sampling

# Bad: Global random state
def compute_metric(counts: dict):
    sample = np.random.choice(...)  # Non-reproducible!
```

### 4. MetricResult Dataclass

**Return structured results, not raw floats:**

```python
from .registry import MetricResult, Status, determine_status

def compute_my_metric(counts: dict) -> MetricResult:
    value = _compute_value(counts)
    return MetricResult(
        name="my_metric",
        value=value,
        status=determine_status(value, thresholds),
        confidence_interval=(lower, upper),
        metadata={"shots": sum(counts.values())}
    )
```

### 5. Schema Compliance

**Support v1.0 schema output via schema_bridge:**

```python
# Metric must be registered and convertible to schema
from .schema_bridge import metrics_to_schema

results = compute_all(counts=counts, rng=rng)
schema_output = metrics_to_schema(results)  # v1.0 compliant
```

## Do Not

- **Use observed-only smoothing** — Always smooth over full 2^n support
- **Iterate dicts without sorting** — Breaks reproducibility
- **Use global random state** — Pass RNG explicitly
- **Return raw floats** — Use MetricResult dataclass
- **Enumerate 2^n for large n** — Use closed-form when possible (see asymmetry_index.py)
- **Skip validation functions** — Every metric needs `validate_X_properties()`

## Always

- **Import thresholds from constants.py** — Never hardcode
- **Include educational docstrings** — Physics context, formulas, references
- **Add validation function** — Mathematical property checks
- **Register in registry.py** — For compute_all() and schema bridge
- **Test edge cases** — Empty counts, single outcome, uniform distribution

## File Structure

```
metrics/
├── registry.py              # MetricResult, compute_all, register
├── schema_bridge.py         # v1.0 schema conversion
├── profiles.py              # Topic-free profiles ("structure", "quick", "information_theory") + register_profile()
├── asymmetry_index.py       # AI: TVD from uniform (canonical example)
├── pathway_concentration_ratio.py  # PCR
├── entanglement_error_correlation.py  # EEC (hardware caveat: uses logical topology)
├── temporal_pathway_stability.py  # TPS
├── complexity_emergence_score.py  # CES
├── structure_score.py       # SS
├── concentration_index.py   # CI (alias of PCR quartile ratio)
├── total_correlation.py     # TC
├── pathway_persistence.py   # Additional temporal analysis
└── noise_topology_correlation.py  # NTC: covariance-based noise-topology correlation
```

## Adding a New Metric

User modules and experiment packages can add metrics without editing core:

```python
from qforge.core.analysis.metrics import register, register_profile, MetricResult

@register("my_metric")
def compute_my_metric(**kwargs) -> MetricResult: ...

register_profile("my_profile", ["my_metric"])
# then: ExperimentConfig(..., metrics="my_profile")
```

To add a metric **in core** (shared with the engine by default):

1. Create `my_metric.py` following asymmetry_index.py pattern
2. Implement `compute_my_metric()` returning MetricResult
3. Add `validate_my_metric_properties()` function
4. Register in `registry.py`
5. Add schema mapping in `schema_bridge.py`
6. Export in `__init__.py`
7. Add tests in `tests/core/`

## Constants Reference

Key constants from `../constants.py`:
- `ALPHA = 0.5` — Jeffreys prior
- `EPS = 1e-12` — Numerical stability
- `STRUCTURE_WEAK_THRESHOLD` — Evidence thresholds
- `MAX_OUTCOMES_EXACT` — When to avoid enumeration
