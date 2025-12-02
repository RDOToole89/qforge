# Phase 1: Scientific Rigor & Validation

**Status**: 🔄 In Progress
**Priority**: Highest - "We cannot publish if the math is shaky"
**Goal**: Ensure metrics produce correct numbers via analytical solutions, property invariants, and statistical validation.

---

## Current State Assessment

### Existing Assets ✅
- [x] `tests/physics/test_analytical.py` exists (97 lines) with basic tests
- [x] All 8 metrics have `validate_*_properties()` functions
- [x] Jeffreys smoothing (α=0.5) implemented throughout
- [x] Numerical stability (EPS=1e-12) in place
- [x] Known exact values documented in code comments

### Gaps to Address ❌
- [ ] No `hypothesis` library installed (needed for property-based testing)
- [ ] Incomplete analytical baseline coverage
- [ ] No numerical stability stress tests
- [ ] No bootstrap calibration verification
- [ ] No null model distribution tests

---

## Phase 1.1: Exact Physics Test Suite

### Step 1: Add Hypothesis Library
- [ ] Run `poetry add --group dev hypothesis`
- [ ] Verify installation with `poetry run python -c "import hypothesis; print(hypothesis.__version__)"`

### Step 2: Extend Analytical Baselines
**File**: `tests/physics/test_analytical.py` (extend existing)

| Test | Metric | Input | Expected | Tolerance | Status |
|------|--------|-------|----------|-----------|--------|
| [ ] | Entropy | Deterministic `{"000": 1000}` | ~0.0 bits | <0.01 | |
| [ ] | Entropy | Uniform 2-qubit | 2.0 bits | <0.01 | |
| [ ] | TC | Bell `{"00": 500, "11": 500}` | 1.0 bit | <0.05 | |
| [ ] | TC | 3-qubit GHZ | 2.0 bits | <0.05 | |
| [ ] | AI | Uniform distribution | 0.0 | <0.01 | |
| [ ] | AI | Deterministic | 0.5 | <0.05 | |
| [ ] | EEC | Any valid input | ∈ [-1, 1] | exact | |
| [ ] | PCR | Uniform distribution | 1.0 | <0.05 | |

### Step 3: Property-Based Tests with Hypothesis
**File**: `tests/physics/test_properties.py` (CREATE)

| Invariant | Property | Status |
|-----------|----------|--------|
| [ ] | H(p) ≥ 0 for all distributions | |
| [ ] | H(p) ≤ log₂(d) for d outcomes | |
| [ ] | MI(X;Y) ≥ 0 always | |
| [ ] | MI(A;B) == MI(B;A) (symmetry) | |
| [ ] | AI ∈ [0, 1] always | |
| [ ] | PCR > 0 for non-degenerate distributions | |

### Step 4: Numerical Stability Tests
**File**: `tests/physics/test_numerical_stability.py` (CREATE)

| Edge Case | Input | Expected | Status |
|-----------|-------|----------|--------|
| [ ] | Near-zero probability | `{"000": 10^7, "001": 1}` | No NaN/Inf | |
| [ ] | Highly skewed | `{"00": 999999, "01": 1}` | Valid result | |
| [ ] | Single count | `{"0000": 1}` | No crash | |
| [ ] | Large shots | `{"00": 10^9, "11": 10^9}` | Correct entropy | |
| [ ] | Many qubits (10+) | Sparse GHZ | Scales correctly | |
| [ ] | Empty counts | `{}` | Raises ValueError | |
| [ ] | Zero total | All zeros | Raises error | |
| [ ] | Negative counts | `{"00": -50}` | Raises ValueError | |

---

## Phase 1.2: Null Model Validation

### Step 5: Bootstrap Calibration Tests
**File**: `tests/physics/test_bootstrap_calibration.py` (CREATE)

- [ ] **95% CI Coverage Test** (`@pytest.mark.slow`)
  - Generate N=200 samples from known distribution (fair coin, H=1.0)
  - Compute bootstrap 95% CI for each
  - Count coverage of true value
  - Assert coverage ∈ [90%, 100%]

### Step 6: Null Model Distribution Tests
**File**: `tests/physics/test_null_model.py` (CREATE)

- [ ] **Null Distribution Test** (`@pytest.mark.slow`)
  - Generate N=500 uniform random samples
  - Compute AI for each
  - Assert mean(AI) < 0.1
  - Assert 90th percentile < 0.2

- [ ] **Structured vs Null Separation Test**
  - Compare GHZ AI vs uniform AI
  - Assert clear separation (gap > 0.2)

---

## Files Summary

| File | Action | Purpose | Status |
|------|--------|---------|--------|
| `pyproject.toml` | MODIFY | Add `hypothesis` | [ ] |
| `tests/physics/test_analytical.py` | EXTEND | More exact value tests | [ ] |
| `tests/physics/test_properties.py` | CREATE | Property-based tests | [ ] |
| `tests/physics/test_numerical_stability.py` | CREATE | Edge case tests | [ ] |
| `tests/physics/test_bootstrap_calibration.py` | CREATE | CI coverage verification | [ ] |
| `tests/physics/test_null_model.py` | CREATE | Null distribution tests | [ ] |

---

## Verification Commands

```bash
# Step 1: Install hypothesis
poetry add --group dev hypothesis

# Run all physics tests (fast)
poetry run pytest tests/physics/ -v --ignore=tests/physics/test_bootstrap_calibration.py --ignore=tests/physics/test_null_model.py

# Run property-based tests with statistics
poetry run pytest tests/physics/test_properties.py -v --hypothesis-show-statistics

# Run slow tests (bootstrap, null model) - takes minutes
poetry run pytest tests/physics/ -v -m slow

# Run everything
poetry run pytest tests/physics/ -v
```

---

## Success Criteria

| Criterion | Target | Verified |
|-----------|--------|----------|
| Analytical baselines pass | All with documented tolerances | [ ] |
| Property invariants hold | 1000+ examples, no violations | [ ] |
| Numerical stability | No NaN/Inf, all edge cases pass | [ ] |
| Bootstrap coverage | 90-100% (95% nominal) | [ ] |
| Null AI distribution | Mean < 0.1, P90 < 0.2 | [ ] |
| Structured separation | Clear gap from null | [ ] |

---

## Risk Mitigation

| Risk | Mitigation | Status |
|------|------------|--------|
| hypothesis pathological inputs | Use strategies with sensible bounds | [ ] |
| Bootstrap tests slow | Mark `@pytest.mark.slow`, run separately | [ ] |
| Jeffreys affects exact tests | Use relaxed tolerances | [ ] |
| Missing bootstrap function | Check existence, implement if needed | [ ] |

---

## Dependencies

- **hypothesis**: Property-based testing (NEW - to be added)
- **scipy**: Statistical tests (already installed)
- **numpy**: Already installed
- **pytest**: Already installed

---

## Notes

- Tolerances are relaxed where Jeffreys smoothing affects exact values
- Slow tests should be run before commits but not on every save
- Property-based tests may find edge cases we haven't considered
- All tests should be deterministic (use RNG seeds where needed)
