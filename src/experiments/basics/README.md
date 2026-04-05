# Basics — Learn Quantum Computing Step by Step

Start here if you're new to quantum computing. Follow the 11 steps in order, then explore the deep dives to go further on topics that interest you.

```
basics/
├── steps/              11-step core learning path (do these in order)
│   ├── step01 → step11
│   └── README.md
└── deep_dives/         Go deeper on specific topics (after the relevant step)
    ├── dd_bloch_geometry
    ├── dd_bell_correlations
    ├── dd_teleportation_intro
    ├── ... (10 total)
    └── README.md
```

---

## The Core Path: 11 Steps

### Single Qubit (Steps 1-3)

| Step | Run | What you'll learn |
|------|-----|-------------------|
| 1 | `python -m src.cli run 01_superposition` | What IS a qubit? \|0⟩, \|1⟩, and \|+⟩ |
| 2 | `python -m src.cli run 02_measurement` | Probability, collapse, Born rule |
| 3 | `python -m src.cli run 03_single_gates` | X, H, Z, Y, S, T — what each gate does |

### Two Qubits and Entanglement (Steps 4-5)

| Step | Run | What you'll learn |
|------|-----|-------------------|
| 4 | `python -m src.cli run 04_two_qubits` | Independent vs entangled — the CNOT gate |
| 5 | `python -m src.cli run 05_bell_states` | All four Bell states and hidden phase |

### Multi-Qubit Entanglement (Steps 6-8)

| Step | Run | What you'll learn |
|------|-----|-------------------|
| 6 | `python -m src.cli run 06_ghz_states` | Scale entanglement: 2 to 6 qubits |
| 7 | `python -m src.cli run 07_w_states` | Distributed excitation — a different topology |
| 8 | `python -m src.cli run 08_cluster_states` | Nearest-neighbor entanglement, invisible in Z-basis |

### Noise and Decoherence (Steps 9-11)

| Step | Run | What you'll learn |
|------|-----|-------------------|
| 9 | `python -m src.cli run 09_noise_intro` | What noise does to a qubit |
| 10 | `python -m src.cli run 10_noise_types` | Five noise models on the same state |
| 11 | `python -m src.cli run 11_noise_and_entanglement` | River vs Fog — the capstone |

---

## Deep Dives

After completing a step, go deeper with these optional explorations. Each one is linked to the step it builds on.

| After step | Run | What you'll explore |
|------------|-----|---------------------|
| 1-3 | `python -m src.cli run dd_bloch_geometry` | Gates as rotations — trace paths on the Bloch sphere with Rx, Ry, Rz |
| 5 | `python -m src.cli run dd_bell_correlations` | Full Bell metrics, all 4 variants, correlation strength analysis |
| 5 | `python -m src.cli run dd_teleportation_intro` | Quantum teleportation — transfer a state using a Bell pair |
| 6-7 | `python -m src.cli run dd_ghz_structure_metrics` | Structure Score, Total Correlation, Concentration Index on GHZ |
| 6-7 | `python -m src.cli run dd_entanglement_fragility` | GHZ is fragile, W is robust — what survives qubit loss? |
| 8 | `python -m src.cli run dd_measurement_basis` | Z-basis vs X-basis — see hidden quantum information appear |
| 10 | `python -m src.cli run dd_noise_model_comparison` | Side-by-side noise model analysis with metrics |
| 10 | `python -m src.cli run dd_density_matrix` | See the full quantum state (including coherences) via density matrix |
| 11 | `python -m src.cli run dd_structure_scaling` | Watch Structure Score grow with qubit count — the scaling ladder |

---

## What you'll understand after this

After the 11 steps + deep dives, you'll know:
- What superposition and measurement collapse mean in practice
- How quantum gates transform qubit states (and why they're rotations)
- What entanglement looks like in measurement data
- Why GHZ, W, and Cluster states behave so differently
- How to teleport a quantum state using entanglement
- Why some entangled states are fragile and others are robust
- How noise degrades quantum states and why noise type matters
- What a density matrix reveals that measurement can't
- The "River vs Fog" phenomenon in structured decoherence
- How structure scales with system size

You're then ready for:
- **`advanced/`** — Shor's, Grover's, VQE, QAOA, Teleportation
- **`decoherence/`** — Structured decoherence research experiments
- **`hardware/`** — Run experiments on real IBM Quantum processors
