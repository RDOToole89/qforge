# Hardware — Real Quantum Hardware Experiments

Run experiments on IBM Quantum processors. Requires an IBM Quantum account and saved credentials.

## Prerequisites

See `docs/guides/hardware-setup.md` for full setup instructions.

Quick version:
```python
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform",
    token="YOUR_TOKEN",
    set_as_default=True,
)
```

## Experiments

### `hardware_study` — Complete structured decoherence study

A documented 10-experiment suite designed for systematic comparison between simulation and real hardware. Includes:

1. GHZ scaling ladder (2-6 qubits)
2. Topology comparison (GHZ, W, Cluster, Product)
3. Backend comparison (same experiment on all available processors)
4. Measurement basis comparison (Z vs X basis on Cluster)
5. Optimization level comparison (transpiler impact)

```python
# Run everything
from src.experiments.hardware.hardware_study import run_all
results = run_all(mode="hardware")

# Run in simulation for comparison
results = run_all(mode="simulation")

# Run individual experiments
from src.experiments.hardware.hardware_study import run_scaling_ladder
results = run_scaling_ladder(mode="hardware")
```

### Running decoherence experiments on hardware

Any experiment from `decoherence/` can also run on hardware by overriding `sim_mode`:

```python
from src.experiments import get_experiment

result = get_experiment("topology_comparison").run({
    "sim_mode": "hardware",
    "shots": 8192,
})
```

## Results

All hardware results include full provenance:
- Backend name, job ID, execution time
- Transpilation details (depth, SWAP count, qubit layout)
- Calibration snapshot (T1/T2 medians)
- Software versions and git SHA

Results are saved to `results/hardware_study/` as JSON.

## What we found

See `docs/research/2026-04-hardware-decoherence/` for the complete analysis of our hardware experiments on three IBM Heron r2 processors.
