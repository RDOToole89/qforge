# Codebase Audit Report (December 2024)

**Branch**: `refactor/simplify-codebase`
**Date**: 2024-12-02
**Auditor**: Claude (Opus 4.5)

---

## Executive Summary

The refactor successfully established a clean architecture but left some **legacy artifacts** and **broken import paths** that should be cleaned up before merging.

### Critical Issues

| Issue | Severity | Files Affected |
|-------|----------|----------------|
| Broken import path `src.analysis.*` | 🔴 HIGH | 2 files |
| Orphaned duplicate `research_handler.py` | 🟡 MEDIUM | 1 file (386 lines) |
| Misleading documentation in `src/core/__init__.py` | 🟡 MEDIUM | 1 file |
| Thin facade `runner.py` adds indirection | 🟢 LOW | 1 file |

---

## Issue 1: Broken Import Path (CRITICAL)

### Description
Two files use the non-existent path `src.analysis.metrics.*` instead of the correct `src.core.analysis.metrics.*`.

### Affected Files

**`src/engine/experiment_runner.py:22-27`**
```python
# BROKEN - src.analysis doesn't exist!
try:
    from src.analysis.metrics.registry import compute_all
    from src.analysis.metrics.schema_bridge import metrics_to_schema
except Exception:
    compute_all = None
    metrics_to_schema = None
```

**`src/engine/research_handler.py:36-37`**
```python
# BROKEN - src.analysis doesn't exist!
from src.analysis.metrics.registry import compute_all
from src.analysis.metrics.schema_bridge import metrics_to_schema
```

### Correct Path
```python
from src.core.analysis.metrics.registry import compute_all
from src.core.analysis.metrics.schema_bridge import metrics_to_schema
```

### Why It Works Currently
`experiment_runner.py` has a try/except that silently sets `compute_all = None`, so the code runs but **metrics computation is silently disabled**.

### Fix
1. Update import paths to use `src.core.analysis.metrics.*`
2. Remove the silent fallback — fail loudly if metrics aren't available

---

## Issue 2: Orphaned `research_handler.py` (MEDIUM)

### Description
`src/engine/research_handler.py` (386 lines) is a **complete duplicate** of `experiment_runner.py` with nearly identical code. Nothing imports from it.

### Evidence
```bash
$ grep -r "from src.engine.research_handler" src/
# No results
```

### Content Analysis
| Content | research_handler.py | experiment_runner.py |
|---------|---------------------|---------------------|
| `EngineExperimentRunner` class | ✅ Lines 46-360 | ✅ Lines 32-383 |
| `run_raw()` function | ✅ Lines 360-386 | ✅ Lines 383-409 |
| Line count | 386 | 409 |

### Recommendation
**DELETE** `src/engine/research_handler.py` — it's dead code.

---

## Issue 3: Misleading Documentation (MEDIUM)

### Description
`src/core/__init__.py` contains incorrect documentation about metric locations.

### Location
**`src/core/__init__.py:16-17`**
```python
* Structured-decoherence **metrics** (registry, schema bridge, etc.)
  live under `src.analysis.metrics`. Import them from there when needed.
```

### Correct Documentation
```python
* Structured-decoherence **metrics** (registry, schema bridge, etc.)
  live under `src.core.analysis.metrics`. Import them from there when needed.
```

---

## Issue 4: Thin Facade `runner.py` (LOW)

### Description
`src/engine/runner.py` (36 lines) is a thin facade that only validates config and delegates to `experiment_runner.py`. It adds indirection without significant value.

### Current Flow
```
api.py → runner.py → experiment_runner.py
```

### Recommendation
Consider removing `runner.py` and having `api.py` import directly from `experiment_runner.py`, OR keep it as a stable import point but document why.

---

## Clean Code: What's Working Well

### Correct Import Paths Found

**`src/engine/analysis/research_integration.py:15-16`** ✅
```python
from src.core.analysis.metrics.registry import compute_all
from src.core.analysis.metrics.schema_bridge import metrics_to_schema
```

**`src/engine/api.py:62`** ✅
```python
from src.engine.analysis import compute_research_metrics, extract_counts_from_result
```

### Active Components (Not Orphaned)

| File | Imported By | Status |
|------|-------------|--------|
| `experiment_runner.py` | sweep_driver, experiments | ✅ ACTIVE |
| `api.py` | external callers | ✅ ACTIVE |
| `sweep_driver.py` | api.py | ✅ ACTIVE |
| `storage.py` | api.py, sweep_driver | ✅ ACTIVE |
| `context.py` | api.py | ✅ ACTIVE |
| `events.py` | api.py | ✅ ACTIVE |
| `hashing.py` | api.py | ✅ ACTIVE |
| `analysis/research_integration.py` | api.py, sweep_driver | ✅ ACTIVE |
| `visualization/` | api.py | ✅ ACTIVE |
| `models/` | everywhere | ✅ ACTIVE |

---

## File Size Analysis (Largest Files)

These files might benefit from splitting if they grow further:

| File | Lines | Assessment |
|------|-------|------------|
| `complexity_emergence_score.py` | 685 | OK — complex metric |
| `temporal_pathway_stability.py` | 679 | OK — complex metric |
| `entanglement_error_correlation.py` | 664 | OK — complex metric |
| `thermal_relaxation.py` | 608 | OK — comprehensive noise |
| `results.py` | 595 | ⚠️ Consider splitting Pydantic models |
| `phase_damping.py` | 572 | OK |

---

## Recommended Actions

### Immediate (Before Merge)

1. **Fix broken imports** in `experiment_runner.py`
   ```python
   # Change from:
   from src.analysis.metrics.registry import compute_all
   # To:
   from src.core.analysis.metrics.registry import compute_all
   ```

2. **Delete orphaned file** `src/engine/research_handler.py`

3. **Fix documentation** in `src/core/__init__.py`

### Short-Term (Post-Merge)

4. **Evaluate `runner.py`** — keep or remove the facade

5. **Add import validation** to CI — prevent `src.analysis.*` paths

### Long-Term (Phase 5-6)

6. **Recover hypergraph.py** — as documented in roadmap

7. **Split large model files** if they continue growing

---

## Appendix: Complete Import Graph

```
src/engine/api.py
├── src.engine.analysis.compute_research_metrics ✅
├── src.engine.analysis.extract_counts_from_result ✅
├── src.engine.context.AppContext ✅
├── src.engine.events.* ✅
├── src.engine.hashing.sha1_of ✅
├── src.engine.runner.run_raw ← src.engine.experiment_runner.run_raw
├── src.engine.storage.LocalStorage ✅
├── src.engine.models.* ✅
└── src.engine.visualization.create_default_service ✅

src/engine/experiment_runner.py
├── src.core.noise_models.create_noise_model ✅
├── src.core.state_preparation.prepare_state ✅
└── src.analysis.metrics.* ❌ BROKEN (silently None)

src/engine/research_handler.py ← ORPHANED, DELETE
├── src.analysis.metrics.* ❌ BROKEN
├── src.core.noise_models.* ✅
└── src.core.state_preparation.* ✅

src/engine/sweep_driver.py
├── src.engine.experiment_runner.EngineExperimentRunner ✅
├── src.engine.analysis.* ✅
├── src.engine.storage.LocalStorage ✅
└── src.engine.models.* ✅
```

---

## Validation Commands

```bash
# Check for broken imports
grep -r "from src\.analysis\." src/ --include="*.py"
# Should return 0 results after fix

# Check for orphaned files
grep -r "from src\.engine\.research_handler" src/
# Should return 0 results (confirms it's orphaned)

# Verify correct imports
grep -r "from src\.core\.analysis\.metrics" src/
# Should show all metric imports
```
