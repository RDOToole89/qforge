# Phase 1.2: Integrate Structured Decoherence into Engine API

## 🎯 Objective
Integrate structured decoherence metrics computation directly into the engine API so that when `enable_research_metrics=True`, experiments automatically compute the 5 research metrics (AI, PCR, EEC, TPS, CES).

## 📋 Current State Assessment

### What's Working Now
1. ✅ **Engine models** have research parameters (Phase 1.1 complete)
2. ✅ **Structured decoherence metrics** implemented in `src/core/analysis/structured_decoherence/`
3. ✅ **Engine API** exists and runs basic experiments via `run()` and `sweep()`
4. ✅ **Core research handler** processes results (but not integrated with engine)
5. ✅ **Schemas** support research configurations

### Current Flow (What We Don't Want to Break)
```
Engine API (api.py) 
    → Engine Runner (runner.py) 
    → Core ExperimentRunner 
    → Core ResearchHandler 
    → Results
```

### Target Flow (What We Want to Achieve)
```
Engine API (api.py)
    → Engine Runner (runner.py)
    → Core ExperimentRunner 
    → [NEW] Integrated Research Analysis
    → Results with StructuredDecoherenceMetrics
```

## 🔧 Implementation Plan

### Step 1: Create Research Analysis Integration Module
**File**: `src/engine/analysis/__init__.py` and `src/engine/analysis/research_integration.py`

**Purpose**: Bridge between engine and core analysis modules

**Key Functions**:
```python
def compute_research_metrics(
    counts: Dict[str, int],
    config: ExperimentConfig
) -> Optional[StructuredDecoherenceMetrics]:
    """
    Compute structured decoherence metrics if enabled.
    Returns None if not a research experiment.
    """
    
def extract_counts_from_result(
    raw_result: Any
) -> Dict[str, int]:
    """
    Extract measurement counts from various Qiskit result formats.
    """
```

### Step 2: Update Engine API to Call Research Analysis
**File**: `src/engine/api.py`

**Changes**:
1. Import research integration module
2. After getting raw results, check if `enable_research_metrics=True`
3. If yes, compute structured decoherence metrics
4. Attach metrics to ExperimentResult

**Pseudocode**:
```python
def run(config, ctx):
    # ... existing code ...
    circuit, raw = run_raw(config)
    
    # NEW: Research metrics integration
    if config.enable_research_metrics:
        counts = extract_counts_from_result(raw)
        metrics = compute_research_metrics(counts, config)
        result.structured_decoherence_metrics = metrics
    
    return result
```

### Step 3: Create Validation Tests BEFORE Making Changes
**File**: `tests/engine/test_research_integration.py`

**Test Cases**:
1. **Basic functionality preserved**: Run experiment without research metrics
2. **Research metrics computed**: Run with `enable_research_metrics=True`
3. **All 5 metrics present**: Verify AI, PCR, EEC, TPS, CES computed
4. **Backward compatibility**: Old configs still work
5. **Schema validation**: Results validate against schema

### Step 4: Incremental Implementation with Validation

#### 4.1: First, Test Current Functionality
```bash
# Run basic experiment (should work)
python main.py run --state GHZ --qubits 3 --shots 1024

# Run with research (currently might not compute metrics)
python main.py run --state GHZ --qubits 3 --enable-research
```

#### 4.2: Add Research Integration Module
- Create new module
- Import existing structured decoherence functions
- Test in isolation

#### 4.3: Wire Into Engine API
- Minimal change to api.py
- Test with simple experiment
- Verify metrics appear in result

#### 4.4: Test Full Pipeline
- Run various experiments
- Verify all metrics computed correctly
- Check schema validation

## 🧪 Validation Strategy

### Pre-Implementation Tests (Baseline)
```python
# tests/engine/test_baseline.py
def test_engine_runs_without_research():
    """Ensure basic experiments still work."""
    config = ExperimentConfig(
        num_qubits=3,
        state_type="GHZ",
        enable_research_metrics=False
    )
    result = run(config)
    assert result is not None
    assert result.structured_decoherence_metrics is None

def test_current_research_handler_works():
    """Ensure research handler still computes metrics."""
    # Direct test of research handler
    pass
```

### Integration Tests
```python
# tests/engine/test_research_integration.py
def test_research_metrics_computed():
    """Test that research metrics are computed when enabled."""
    config = ExperimentConfig(
        num_qubits=3,
        state_type="GHZ",
        enable_research_metrics=True,
        research_type="structured_decoherence"
    )
    result = run(config)
    
    assert result.structured_decoherence_metrics is not None
    assert result.structured_decoherence_metrics.asymmetry_index >= 0
    assert result.structured_decoherence_metrics.pathway_concentration_ratio >= 0
    # ... test all 5 metrics

def test_sweep_with_research():
    """Test parameter sweep with research metrics."""
    manifest = SweepManifest(
        base_config=ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=True
        ),
        parameter_ranges={"error_rate": [0.0, 0.05, 0.1]}
    )
    results = sweep(manifest)
    
    for result in results:
        assert result.structured_decoherence_metrics is not None
```

### End-to-End Validation
```python
def test_cli_still_works():
    """Ensure CLI commands still function."""
    # Test various CLI commands
    pass

def test_results_validate_against_schema():
    """Ensure results match JSON schema."""
    from src.utils.schema import validate_results_schema
    
    config = ExperimentConfig(
        num_qubits=3,
        state_type="GHZ",
        enable_research_metrics=True
    )
    result = run(config)
    
    # Convert to dict and validate
    result_dict = result.model_dump()
    validate_results_schema(result_dict)
```

## 🚨 Risk Mitigation

### What Could Break
1. **Import cycles**: Engine importing from core
2. **Missing dependencies**: Structured decoherence not found
3. **Schema mismatches**: New fields not in schema
4. **Performance**: Research metrics slow down experiments
5. **Memory**: Large experiments with metrics use too much memory

### Mitigation Strategies
1. **Import cycles**: Use lazy imports or dependency injection
2. **Missing dependencies**: Check imports in try/except blocks
3. **Schema mismatches**: Regenerate schemas after changes
4. **Performance**: Make metrics computation optional/async
5. **Memory**: Stream results instead of holding in memory

## ✅ Success Criteria

### Phase 1.2 is complete when:
1. ✅ Running experiment with `enable_research_metrics=True` computes all 5 metrics
2. ✅ Metrics appear in ExperimentResult as `structured_decoherence_metrics`
3. ✅ All existing functionality still works (no regressions)
4. ✅ Results validate against JSON schema
5. ✅ Tests pass for both research and non-research experiments
6. ✅ Parameter sweeps work with research metrics
7. ✅ CLI commands function correctly

## 📊 Validation Checklist

Before implementation:
- [ ] Run and save output of current working experiment
- [ ] Document current result structure
- [ ] Create baseline tests

During implementation:
- [ ] Test after each code change
- [ ] Verify no import errors
- [ ] Check memory usage
- [ ] Validate against schema

After implementation:
- [ ] Compare results with baseline
- [ ] Run full test suite
- [ ] Test CLI commands
- [ ] Run parameter sweep
- [ ] Validate research metrics accuracy

## 🔄 Rollback Plan

If things break:
1. **Git stash changes**: `git stash`
2. **Revert to last commit**: `git reset --hard HEAD`
3. **Restore working state**: `git checkout refactor/simplify-codebase`
4. **Analyze what went wrong**
5. **Try smaller incremental change**

## 📁 File Changes Summary

### New Files
- `src/engine/analysis/__init__.py`
- `src/engine/analysis/research_integration.py`
- `tests/engine/test_research_integration.py`
- `tests/engine/test_baseline.py`

### Modified Files
- `src/engine/api.py` (add research metrics computation)
- `src/engine/models/results.py` (ensure compatibility)

### Unchanged (Critical - Don't Touch)
- `src/core/experiment_runner.py`
- `src/core/research_handler.py`
- `src/core/analysis/structured_decoherence/*`

## 🚀 Implementation Order

1. **Create test files first** (establish baseline)
2. **Create research integration module** (isolated new code)
3. **Test integration module standalone**
4. **Wire into engine API** (minimal change)
5. **Test incrementally**
6. **Run full validation suite**
7. **Update documentation**

This approach ensures we build incrementally, test continuously, and can rollback if needed!