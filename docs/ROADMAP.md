# Engine Roadmap

Last updated: 2026-02-20
Status: Post-audit, pre-implementation

---

## Where We Are

The framework runs quantum experiments on a local Aer simulator, computes 8 research metrics with bootstrap CIs, saves JSON results with histograms, and serves them via a FastAPI + Expo React Native stack.

**What works well:**
- Metric math is research-grade (Jeffreys smoothing, full 2^n support, deterministic ordering)
- Pydantic config with cross-field validation
- Plugin architecture for visualization (easy to extend)
- MetricsBundle system (generic, profile-based metric selection)
- Atomic file storage with artifact ledger

**What doesn't work or is missing:**
- Locked to QASM simulator (no statevector, no density matrix mode)
- No path to real quantum hardware (despite qiskit-ibm-runtime being installed)
- Only histogram visualization (no density maps, Bloch spheres, correlation heatmaps)
- Logging is non-functional (loggers exist, no configuration)
- PNG-only output (journals need PDF/SVG)

---

## Phase 1: Simulation Backends (unlock density matrix analysis)

**Goal:** Let the user choose `sim_mode` from `qasm`, `statevector`, `density_matrix`.

**Why first:** Density matrix mode directly serves the structured decoherence research. It lets you see the full mixed state under noise, not just sampled counts. Statevector mode lets you validate state preparation without noise interference.

**Changes:**

| File | What |
|------|------|
| `src/engine/models/config.py` | Extend `sim_mode: Literal["qasm", "statevector", "density_matrix"]` |
| `src/engine/execution/runner.py` | Backend factory: `AerSimulator(method=sim_mode)`. Skip noise for statevector. Handle result type differences. |
| `src/engine/api.py` | Extract density matrix / statevector from result when available. Populate `MeasurementResults.density_matrix`. |
| `src/engine/models/results.py` | Ensure `density_matrix` and `fidelity` fields get populated. |

**Estimated effort:** 3-4 hours

**Verification:**
```python
# Density matrix mode with noise
result = run(ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    sim_mode="density_matrix",
    noise_enabled=True, noise_type="depolarizing", error_rate=0.05,
))
assert result.analysis.measurement_results.density_matrix is not None

# Statevector mode (no noise, exact state)
result = run(ExperimentConfig(
    num_qubits=3, state_type="GHZ",
    sim_mode="statevector",
))
# Should have pure state vector, fidelity=1.0
```

---

## Phase 2: Visualization Expansion

**Goal:** Add density matrix heatmap, correlation heatmap, and circuit diagram renderers. Support PDF/SVG export.

**Why:** Publication figures. The histogram alone can't tell the structured decoherence story. You need to *show* the density matrix decaying, the MI correlation structure, and the circuit that produced it.

### 2a. Density Matrix Renderer

New `DensityMatrixRenderer` in `renderers.py`:
- Heatmap of |rho_ij| with colorbar
- Eigenvalue spectrum subplot
- Purity annotation: `Tr(rho^2)`
- Triggered by `visualization_type="density_matrix"` or auto-detected when density matrix data is present

### 2b. Correlation Heatmap Renderer

New `CorrelationRenderer` in `renderers.py`:
- MI matrix heatmap (already computed by EEC metric)
- Overlay entanglement topology graph edges
- Annotate with EEC value

### 2c. Circuit Diagram

Wrap Qiskit's `circuit.draw(output='mpl')`:
- Save as artifact alongside other visualizations
- Include gate counts and depth in annotation

### 2d. Multi-Format Export

Add `export_formats` to config or viz service:
- `plt.savefig(path, format="pdf")` for journals
- `plt.savefig(path, format="svg")` for web
- Update ArtifactRef with correct MIME types

### 2e. Extend visualization_type

```python
visualization_type: Literal[
    "histogram", "density_matrix", "correlation",
    "circuit", "all", "none"
] = "histogram"
```

**Estimated effort:** 6-8 hours total (2h per renderer, 1h for export, 1h for wiring)

---

## Phase 3: Logging & Observability

**Goal:** Make the engine observable. Structured logging, configurable levels, progress events.

**Changes:**

| What | How |
|------|-----|
| Logging config | `setup_logging(level, format, file)` called from CLI and AppContext |
| JSON logging | Honor `AppContext.logging_mode == "json"` |
| Log file output | Write to `results/<date>/engine.log` alongside artifacts |
| Progress events | Publish `PROGRESS` in `api.py` sweep loop |
| CLI flags | `--log-level`, `--log-file`, `--quiet` |
| Env vars | `QEF_LOG_LEVEL`, `QEF_RESULTS_DIR` |

**Estimated effort:** 4-5 hours

---

## Phase 4: Real Quantum Hardware

**Goal:** Run experiments on IBM Quantum cloud backends.

**Why after Phase 1-3:** Need backend abstraction (Phase 1), proper logging for debugging async jobs (Phase 3), and visualization to validate hardware results vs simulation (Phase 2).

### 4a. Backend Abstraction

Create `src/engine/execution/backends.py`:

```python
def get_backend(config, ctx):
    if config.backend_type == "simulator":
        return AerSimulator(method=config.sim_mode)
    elif config.backend_type == "ibm_quantum":
        from qiskit_ibm_runtime import QiskitRuntimeService
        service = ctx.provider or QiskitRuntimeService()
        return service.backend(config.backend_name)
```

### 4b. Config Extension

```python
backend_type: Literal["simulator", "ibm_quantum"] = "simulator"
backend_name: str | None = None
optimization_level: int = Field(default=1, ge=0, le=3)
```

### 4c. Transpilation

- Pass `optimization_level`, `coupling_map`, `basis_gates` to `transpile()`
- Extract these from real backend properties automatically
- Log transpiled circuit depth vs original

### 4d. Job Management

- Async job submission with timeout
- Status polling with progress events
- Graceful handling of queue times

### 4e. Readout Error Mitigation

- Use `qiskit-ibm-runtime` built-in error suppression
- Or implement simple confusion matrix correction
- Flag mitigated vs raw counts in results

### 4f. Validation

- Check circuit qubits <= backend qubits
- Check gate set compatibility
- Warn about expected queue times
- Test against `FakeBackend` before real submissions

**Estimated effort:** 15-22 hours total

**New config fields:**

```python
backend_type: Literal["simulator", "ibm_quantum"] = "simulator"
backend_name: str | None = None         # e.g. "ibm_osaka"
optimization_level: int = 1             # transpiler optimization 0-3
error_mitigation: bool = False          # readout error mitigation
job_timeout_seconds: int = 3600         # max wait for real hardware
```

---

## Phase 5: Analysis Gaps

**Goal:** Address known scientific limitations found in the audit.

### 5a. EEC State-Aware Default

Make the state-aware null model the default for EEC on GHZ states. The factorized null is too conservative and the MI confounding issue is well-documented.

### 5b. CES Minimum Data Threshold

Raise minimum from 4 to 8 data points for logistic fitting. At n=4 the fit is underpowered.

### 5c. TPS Vacuous Truth

Return `NaN` instead of `1.0` when fewer than 2 rankings are available. Current behavior masks insufficient data.

### 5d. NTC Metric

Implement the Noise Topology Correlation metric from Feb 2026 findings. It uses excess covariance with permutation testing and correctly handles the MI/GHZ confounding.

**Estimated effort:** 6-8 hours

---

## Phase 6: Sweep & Campaign Visualization

**Goal:** Visualize parameter sweeps and multi-experiment campaigns.

### 6a. Sweep Heatmap

2D parameter grid (e.g., error_rate x num_qubits) with metric values as color.

### 6b. Convergence Plots

Metric value vs shots with bootstrap CI bands. Shows when results stabilize.

### 6c. Comparison Plots

Side-by-side metric comparison across state types or noise models. Bar charts with error bars.

**Estimated effort:** 4-6 hours

---

## Suggested Order

```
Phase 1  (sim backends)        ← unlocks density matrix research
Phase 2a (density viz)         ← see what density matrix mode gives you
Phase 5a (EEC fix)             ← quick scientific fix
Phase 3  (logging)             ← needed before hardware debugging
Phase 2b-d (more viz)          ← publication figures
Phase 4  (hardware)            ← real quantum computer
Phase 5b-d (analysis fixes)    ← scientific polish
Phase 6  (sweep viz)           ← nice to have
```

---

## What This Doesn't Cover

- Web UI beyond current Expo app (keep it simple)
- Multi-user / auth (not needed for research)
- Database backend for results (JSONL ledger is fine)
- Distributed execution (overkill for current scale)
- Auto-generated papers (tempting but premature)
