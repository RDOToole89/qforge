# Running Experiments on IBM Quantum Hardware

This guide walks through setting up and running experiments on real IBM Quantum processors.

## Prerequisites

### 1. Create an IBM Quantum Account

Sign up at [quantum.ibm.com](https://quantum.ibm.com) (the free "Open Plan" provides access to 127-qubit systems with a monthly usage limit).

### 2. Copy Your API Token

From the IBM Quantum dashboard, go to your account settings and copy your API token.

### 3. Save Credentials Locally

Run this once in a Python shell:

```python
from qiskit_ibm_runtime import QiskitRuntimeService

QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token="YOUR_API_TOKEN_HERE",
    set_as_default=True,
)
```

This writes credentials to `~/.qiskit/qiskit-ibm.json`. The framework loads them automatically.

**IBM Cloud users** (instead of IBM Quantum Platform):
```python
QiskitRuntimeService.save_account(
    channel="ibm_cloud",
    token="YOUR_API_KEY",
    instance="crn:v1:bluemix:public:quantum-computing:...",
    set_as_default=True,
)
```

### 4. Verify Setup

```python
from qiskit_ibm_runtime import QiskitRuntimeService

service = QiskitRuntimeService()
backends = service.backends(operational=True, simulator=False)
print(f"Available backends: {[b.name for b in backends]}")
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt  # qiskit-ibm-runtime is already listed
```

---

## Quick Start

### Run a Single Hardware Experiment

```python
from src.engine.api import run

result = run({
    "num_qubits": 3,
    "state_type": "GHZ",
    "sim_mode": "hardware",
    "shots": 1024,
    "visualization_type": "none",
})

print(f"Backend: {result.provenance.simulator_info['backend_name']}")
print(f"Job ID: {result.provenance.simulator_info['job_id']}")
print(f"Counts: {result.analysis.measurement_results.raw_counts}")
print(f"Fidelity: {result.analysis.measurement_results.fidelity}")
```

### Choose a Specific Backend

```python
result = run({
    "num_qubits": 3,
    "state_type": "GHZ",
    "sim_mode": "hardware",
    "shots": 1024,
    "backend_name": "ibm_brisbane",
    "optimization_level": 2,
    "visualization_type": "none",
})
```

### Run a Hardware Sweep with Sessions

Sessions keep the backend reserved across multiple experiments, avoiding re-queuing:

```python
from src.engine.api import sweep

results = sweep({
    "base_config": {
        "num_qubits": 3,
        "sim_mode": "hardware",
        "shots": 1024,
        "hardware_session": True,
        "visualization_type": "none",
    },
    "parameter_ranges": {
        "state_type": ["GHZ", "W", "CLUSTER"],
    },
})

for r in results:
    params = r.analysis.experiment_parameters
    counts = r.analysis.measurement_results.raw_counts
    print(f"{params['state_type']}: {counts}")
```

---

## Hardware vs Simulation: Key Differences

| Aspect | Simulation | Hardware |
|--------|-----------|----------|
| Statevector / density matrix | Available | Not available (counts only) |
| Noise | Configurable (`noise_enabled`) | Physical (always present) |
| Determinism | Reproducible (`rng_seed`) | Inherently probabilistic |
| Fidelity | Exact (state overlap) | Estimated (Bhattacharyya coefficient) |
| Circuit depth | As written | Increases after transpilation |
| Qubit connectivity | All-to-all | Constrained by coupling map |

---

## Understanding Hardware Results

### Transpilation Provenance

Every hardware result captures transpilation details in `result.provenance.transpilation_summary`:

```python
transp = result.provenance.transpilation_summary
print(f"Original depth: {transp['original_depth']}")
print(f"Transpiled depth: {transp['transpiled_depth']}")
print(f"SWAPs inserted: {transp['swap_count']}")
print(f"Qubit layout (logical→physical): {transp['qubit_layout']}")
print(f"Basis gates: {transp['basis_gates']}")
```

### Calibration Snapshot

Provenance also captures a lightweight calibration snapshot:

```python
cal = transp['calibration_snapshot']
print(f"Backend: {cal['backend_name']}")
print(f"Median T1: {cal.get('t1_us_median')} us")
print(f"Median T2: {cal.get('t2_us_median')} us")
```

### Counts-Based Fidelity

Since hardware doesn't provide statevectors, fidelity is estimated from the measurement distribution using the Bhattacharyya coefficient:

```
F = (sum_x sqrt(p_ideal(x) * p_observed(x)))^2
```

This is a **lower bound** on the true quantum state fidelity.

---

## Configuration Reference

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `sim_mode` | `"hardware"` | — | Enables hardware execution |
| `backend_name` | `str \| None` | `None` | Specific backend (auto-selects least busy if None) |
| `optimization_level` | `0-3` | `1` | Transpiler optimization level |
| `hardware_session` | `bool` | `False` | Keep backend reserved in sweeps |
| `shots` | `1-100000` | `1024` | Measurement shots (hardware max: 100k) |

### Invalid Combinations

These configurations will raise `ValueError`:
- `sim_mode="hardware"` + `noise_enabled=True` (physical noise, not simulated)
- `sim_mode="hardware"` + `rng_seed=42` (hardware is non-deterministic)
- `backend_name="ibm_brisbane"` + `sim_mode="qasm"` (backend_name requires hardware mode)
- `sim_mode="hardware"` + `shots=200000` (exceeds 100k limit)

---

## Troubleshooting

### "Failed to connect to IBM Quantum"

Verify credentials are saved:
```python
from qiskit_ibm_runtime import QiskitRuntimeService
print(QiskitRuntimeService.saved_accounts())
```

Re-save if needed with `save_account(...)`.

### "No operational hardware backends found"

- Check IBM Quantum status: https://quantum.ibm.com/services/resources
- Some backends may be under maintenance
- Ensure your account plan has access to hardware

### Long Queue Times

- Use `backend_name` to pick a less popular backend
- Reduce `shots` for faster turnaround during development
- Use Sessions (`hardware_session=True`) in sweeps to avoid re-queuing

### Transpilation Increases Circuit Depth

This is expected. Real hardware has limited qubit connectivity (e.g., IBM's heavy-hex topology). The transpiler inserts SWAP gates to route 2-qubit operations between non-adjacent physical qubits. Check `transpilation_summary.swap_count` to see how many SWAPs were added.

---

## Known Limitations

- **EEC metric**: Uses logical qubit topology, not physical layout after transpilation. Interpret with this caveat for hardware runs.
- **Max qubits**: Framework limit is 20 qubits (configurable, not a hardware limit).
- **Max shots**: 100,000 per job (IBM backend limit).
- **Z-basis only**: All measurements are in the computational basis.
- **No mid-circuit measurement**: Classical feed-forward is not supported.
- **Blocking execution**: Hardware jobs block until completion. For long queue times, consider using the IBM Quantum dashboard to monitor jobs.
