# Hardware — Real Quantum Processors

You've mastered simulation. Now run on real IBM Quantum hardware and see how physical noise shapes quantum states.

```
hardware/
├── steps/              5-step progression to real decoherence
│   ├── step01 → step05
│   └── README.md
└── deep_dives/         Full study suites
    ├── dd_full_study
    ├── dd_readout_errors
    └── README.md
```

## Prerequisites

You need IBM Quantum credentials. See [docs/guides/hardware-setup.md](../../../docs/guides/hardware-setup.md).

```python
from qiskit_ibm_runtime import QiskitRuntimeService
QiskitRuntimeService.save_account(
    channel="ibm_quantum_platform", token="YOUR_TOKEN", set_as_default=True
)
```

---

## The Hardware Journey

### Connect and Compare (Steps 1-2)

| Step | Run | What you'll learn |
|------|-----|-------------------|
| 1 | `python -m src.cli run hw_01_first_hardware_run` | Your first real quantum computer — see real physical noise |
| 2 | `python -m src.cli run hw_02_hardware_vs_simulation` | Same circuit on hardware vs simulation — where do models break down? |

### Understand the Machine (Steps 3-4)

| Step | Run | What you'll learn |
|------|-----|-------------------|
| 3 | `python -m src.cli run hw_03_transpilation` | See your logical circuit become physical gates — SWAP insertion, depth changes |
| 4 | `python -m src.cli run hw_04_backend_exploration` | Try different processors — is your result chip-independent? |

### Real Decoherence (Step 5)

| Step | Run | What you'll learn |
|------|-----|-------------------|
| 5 | `python -m src.cli run hw_05_real_decoherence` | Decoherence structure on real hardware — the culmination of your journey |

---

## Deep Dives

| After step | Run | What you'll explore |
|------------|-----|---------------------|
| 2 | `python -m src.cli run dd_readout_errors` | Gate noise vs readout noise vs both — where errors come from |
| 5 | Run `dd_full_study` programmatically | The complete 10-experiment decoherence study |

The full study is a documented experiment suite (not a single CLI command):

```python
from src.experiments.hardware.deep_dives.dd_full_study import run_all
results = run_all(mode="hardware")    # Real hardware
results = run_all(mode="simulation")  # Matched simulation for comparison
```

---

## The Complete Arc

```
Basics (11 steps)     Advanced (8 steps)     Hardware (5 steps)
────────────────      ────────────────       ─────────────────
What is a qubit?  →   Quantum superpowers →  First hardware run
Entanglement      →   Entanglement tools  →  HW vs simulation
What is noise?    →   QFT + error corr.  →  Transpilation
Noise & entangle. →   Design your own    →  Backend comparison
                                          →  REAL DECOHERENCE
                                                   ↓
                                          Full 10-experiment
                                          study suite
```

After Step 5, you've completed the full journey — from "what is a qubit?" to measuring real decoherence on a physical quantum processor. You're now equipped to design and run your own quantum experiments on real hardware.

---

## QPU Time Usage

Each step uses minimal QPU time:

| Step | Shots | QPU time |
|------|-------|----------|
| 1 | 4096 | ~5 seconds |
| 2 | 8192 | ~7 seconds |
| 3 | 4096 × 3 | ~15 seconds |
| 4 | 8192 × 3 | ~20 seconds |
| 5 | 8192 × 3 | ~20 seconds |
| **Total** | | **~1-2 minutes** |

The free IBM Quantum tier provides 10 minutes per month — plenty for the full hardware journey.
