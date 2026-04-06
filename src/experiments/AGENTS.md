# AGENTS.md — Experiments Module

Owner: Research Engineering
Last updated: 2026-04-05

## Purpose

Pluggable experiment programs built on a **general-purpose quantum experiment engine**. The current research focus is structured decoherence, but the engine supports any quantum experiment — entanglement witnesses, variational circuits, benchmarking, error correction, or anything that fits "prepare state → apply noise/operations → measure → analyze."

Every folder follows the same pattern: `steps/` for guided progressions and `deep_dives/` for extended explorations. New experiment types and new research directions are welcome.

## Structure

```
experiments/
├── __init__.py              # Registry: 49 experiments, get_experiment(), list_experiments()
├── base.py                  # ExperimentProgram protocol + BaseExperiment helper
├── README.md                # User-facing overview with quick start
├── AGENTS.md                # This file — agent guidance
│
├── basics/                  # Learn quantum computing (11 steps + 10 deep dives)
│   ├── steps/
│   │   ├── step01_superposition.py         # What IS a qubit?
│   │   ├── step02_measurement.py           # Probability and collapse
│   │   ├── step03_single_gates.py          # X, H, Z, Y, S, T gates
│   │   ├── step04_two_qubits.py            # Independent vs entangled
│   │   ├── step05_bell_states.py           # The four Bell states
│   │   ├── step06_ghz_states.py            # Multi-qubit GHZ
│   │   ├── step07_w_states.py              # W states
│   │   ├── step08_cluster_states.py        # Cluster states
│   │   ├── step09_noise_intro.py           # What noise does
│   │   ├── step10_noise_types.py           # Five noise models
│   │   └── step11_noise_and_entanglement.py # River vs Fog (capstone)
│   └── deep_dives/
│       ├── dd_bloch_geometry.py            # Gates as Bloch rotations
│       ├── dd_bell_basics.py               # Bell with noise sweeps
│       ├── dd_bell_correlations.py         # Full Bell metrics
│       ├── dd_teleportation_intro.py       # Teleportation protocol
│       ├── dd_ghz_structure_metrics.py     # SS, TC, CI on GHZ
│       ├── dd_entanglement_fragility.py    # GHZ fragile, W robust
│       ├── dd_measurement_basis.py         # Z vs X basis
│       ├── dd_noise_model_comparison.py    # Side-by-side noise
│       ├── dd_density_matrix.py            # Full quantum state
│       └── dd_structure_scaling.py         # SS grows with qubits
│
├── advanced/                # Quantum algorithms (8 steps + 7 deep dives)
│   ├── steps/
│   │   ├── step01_quantum_randomness.py    # True randomness
│   │   ├── step02_deutsch_jozsa.py         # First quantum speedup
│   │   ├── step03_grover_search.py         # Amplitude amplification
│   │   ├── step04_teleportation.py         # Entanglement as resource
│   │   ├── step05_superdense_coding.py     # 2 bits from 1 qubit
│   │   ├── step06_qft.py                   # Quantum Fourier Transform
│   │   ├── step07_error_correction.py      # 3-qubit bit-flip code
│   │   └── step08_design_your_own.py       # Experiment template
│   └── deep_dives/
│       ├── dd_shor.py                      # Shor's factoring
│       ├── dd_grover.py                    # Extended Grover's
│       ├── dd_teleportation.py             # Extended teleportation
│       ├── dd_vqe.py                       # Variational Eigensolver
│       ├── dd_qaoa.py                      # QAOA optimization
│       ├── dd_bernstein_vazirani.py        # Hidden string
│       └── dd_bb84.py                      # Quantum key distribution
│
├── decoherence/             # Structured decoherence research (6 steps + 2 deep dives)
│   ├── steps/
│   │   ├── step01_river_vs_fog.py          # Foundational observation
│   │   ├── step02_topology_matters.py      # Four topologies compared
│   │   ├── step03_scaling.py               # Structure grows with qubits
│   │   ├── step04_noise_resilience.py      # How robust is structure?
│   │   ├── step05_global_vs_local.py       # GHZ global, W local
│   │   └── step06_simulation_vs_reality.py # Where models break down
│   └── deep_dives/
│       ├── dd_state_probe.py               # 47-condition sensitivity
│       ├── dd_classical_null.py            # Classical null model test
│       ├── dd_topology_full.py             # Full topology comparison
│       ├── dd_scaling_full.py              # Complete scaling ladder
│       └── dd_noise_sweep_full.py          # Comprehensive noise sweep
│
└── hardware/                # Real IBM Quantum (5 steps + 3 deep dives)
    ├── steps/
    │   ├── step01_first_hardware_run.py    # First real QPU
    │   ├── step02_hardware_vs_simulation.py # HW vs sim comparison
    │   ├── step03_transpilation.py         # Logical → physical
    │   ├── step04_backend_exploration.py   # Compare processors
    │   └── step05_real_decoherence.py      # River vs Fog on hardware
    └── deep_dives/
        ├── dd_full_study.py                # 10-experiment research suite
        └── dd_readout_errors.py            # Gate vs readout noise
```

## Registry

All experiments registered in `__init__.py` under `EXPERIMENT_REGISTRY` (49 total):

### Basics (21)

| Key | Folder | Description |
|-----|--------|-------------|
| `01_superposition` | basics/steps/ | What IS a qubit? |
| `02_measurement` | basics/steps/ | Probability and collapse |
| `03_single_gates` | basics/steps/ | X, H, Z, Y, S, T gates |
| `04_two_qubits` | basics/steps/ | Independent vs entangled |
| `05_bell_states` | basics/steps/ | The four Bell states |
| `06_ghz_states` | basics/steps/ | Multi-qubit GHZ |
| `07_w_states` | basics/steps/ | W states |
| `08_cluster_states` | basics/steps/ | Cluster states |
| `09_noise_intro` | basics/steps/ | What noise does |
| `10_noise_types` | basics/steps/ | Five noise models |
| `11_noise_and_entanglement` | basics/steps/ | River vs Fog |
| `dd_bloch_geometry` | basics/deep_dives/ | Gates as Bloch rotations |
| `dd_bell_correlations` | basics/deep_dives/ | Full Bell metrics |
| `dd_teleportation_intro` | basics/deep_dives/ | Teleportation protocol |
| `dd_ghz_structure_metrics` | basics/deep_dives/ | SS, TC, CI on GHZ |
| `dd_entanglement_fragility` | basics/deep_dives/ | GHZ fragile, W robust |
| `dd_measurement_basis` | basics/deep_dives/ | Z vs X basis |
| `dd_noise_model_comparison` | basics/deep_dives/ | Side-by-side noise |
| `dd_density_matrix` | basics/deep_dives/ | Density matrix mode |
| `dd_structure_scaling` | basics/deep_dives/ | SS scaling |
| `bell_state` | basics/deep_dives/ | Bell with noise sweep |

### Advanced (15)

| Key | Folder | Description |
|-----|--------|-------------|
| `adv_01_quantum_randomness` | advanced/steps/ | True randomness |
| `adv_02_deutsch_jozsa` | advanced/steps/ | First quantum speedup |
| `adv_03_grover_search` | advanced/steps/ | Amplitude amplification |
| `adv_04_teleportation` | advanced/steps/ | Entanglement as resource |
| `adv_05_superdense_coding` | advanced/steps/ | 2 bits from 1 qubit |
| `adv_06_qft` | advanced/steps/ | QFT |
| `adv_07_error_correction` | advanced/steps/ | 3-qubit bit-flip code |
| `adv_08_design_your_own` | advanced/steps/ | Experiment template |
| `dd_bernstein_vazirani` | advanced/deep_dives/ | Hidden string |
| `dd_bb84` | advanced/deep_dives/ | BB84 QKD |
| `shor` | advanced/deep_dives/ | Shor's factoring |
| `grover` | advanced/deep_dives/ | Extended Grover's |
| `vqe` | advanced/deep_dives/ | VQE for H2 |
| `qaoa` | advanced/deep_dives/ | QAOA MaxCut |

### Decoherence (8)

| Key | Folder | Description |
|-----|--------|-------------|
| `dec_01_river_vs_fog` | decoherence/steps/ | Foundational observation |
| `dec_02_topology_matters` | decoherence/steps/ | Four topologies |
| `dec_03_scaling` | decoherence/steps/ | Structure grows with qubits |
| `dec_04_noise_resilience` | decoherence/steps/ | Noise robustness |
| `dec_05_global_vs_local` | decoherence/steps/ | GHZ global, W local |
| `dec_06_simulation_vs_reality` | decoherence/steps/ | Model accuracy |
| `dd_classical_null` | decoherence/deep_dives/ | Classical null model |
| `state_probe` | decoherence/deep_dives/ | 47-condition study |

### Hardware (6 registered + 1 programmatic)

| Key | Folder | Description |
|-----|--------|-------------|
| `hw_01_first_hardware_run` | hardware/steps/ | First real QPU |
| `hw_02_hardware_vs_simulation` | hardware/steps/ | HW vs sim |
| `hw_03_transpilation` | hardware/steps/ | Logical → physical |
| `hw_04_backend_exploration` | hardware/steps/ | Compare processors |
| `hw_05_real_decoherence` | hardware/steps/ | River vs Fog on hardware |
| `dd_readout_errors` | hardware/deep_dives/ | Gate vs readout noise |

Hardware `dd_full_study` is run programmatically (not via registry) because it manages backend sessions internally.

## How to Add a New Experiment

### 1. Decide which folder it belongs in

- **basics/steps/** — Teaches a single quantum concept. Numbered sequentially.
- **basics/deep_dives/** — Goes deeper on a concept from the steps. Prefixed `dd_`.
- **advanced/steps/** — Teaches an algorithm or protocol technique. Numbered `adv_NN_`.
- **advanced/deep_dives/** — Applies techniques to real problems. Prefixed `dd_`.
- **decoherence/steps/** — Guided structured decoherence research. Numbered `dec_NN_`.
- **decoherence/deep_dives/** — Full research experiments. Prefixed `dd_`.
- **hardware/steps/** — Hardware learning path. Numbered `hw_NN_`.
- **hardware/deep_dives/** — Advanced hardware experiments. Prefixed `dd_`.
- **New folders welcome** — Create `benchmarking/`, `error_correction/`, etc. as needed.

### 2. Create the module

Every experiment file MUST have in its docstring:
- **WHAT YOU'LL LEARN / EXPLORE** — educational context
- **CIRCUIT** — ASCII circuit diagram showing the quantum circuit
- **TRY IT** — code example with import and run

Follow the template in `advanced/steps/step08_design_your_own.py`.

### 3. Register it

Add to **four** places:
1. The folder's `__init__.py`
2. `src/experiments/__init__.py` — import and add to `EXPERIMENT_REGISTRY`
3. The folder's `README.md`
4. **This file** — update the registry table

### 4. Test it

```bash
python -m src.cli run my_experiment_name
```

## Architecture Rules

### DO

- Subclass `BaseExperiment`
- Define `name`, `description`, and `default_config()`
- Include CIRCUIT diagrams and educational docstrings
- Add convenience methods (`run_comparison()`, `run_sweep()`, etc.)
- Keep experiments self-contained

### DO NOT

- Put analysis logic in experiments (belongs in `src/core/analysis/`)
- Put visualization logic here (handled by the engine)
- Reference SST, SQM, or personal theory branding — use "structured decoherence"
- Hardcode hardware-specific logic in basics/ or advanced/ experiments

### ALWAYS

- Update ALL four places when adding/removing experiments (see step 3 above)
- Test via CLI before committing
- Include WHAT YOU'LL LEARN, CIRCUIT, and TRY IT in every docstring
