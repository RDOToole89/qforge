# Decoherence — Structured Decoherence Research

Core experiments investigating how entanglement topology determines the structure of decoherence pathways in quantum systems.

These experiments test the central hypothesis: **different entanglement topologies do not merely decohere at different rates — they decohere into qualitatively different classical structures.**

## Experiments (in suggested order)

### 1. `topology_comparison` — Does entanglement type matter?

The foundational experiment. Runs GHZ, W, Cluster, and Product states at 6 qubits under the same noise and compares their decoherence structure.

Key finding: GHZ and W show 12x higher Structure Score than Cluster and Product. Two distinct structured modes emerge — "correlated river" (GHZ) and "distributed river" (W).

```python
from src.experiments import get_experiment
exp = get_experiment("topology_comparison")
results = exp.run_all_states()
```

### 2. `scaling_ladder` — Does structure grow with system size?

Runs GHZ and W from 2 to 6 qubits to test whether structure increases with qubit count. Reveals two different scaling modes:
- GHZ: amplification (entropy stays flat, probability compresses)
- W: redistribution (entropy grows, new pathways emerge)

```python
exp = get_experiment("scaling_ladder")
ghz_results, w_results = exp.run_comparison()
```

### 3. `noise_sweep` — How robust is the structure?

Sweeps noise rate from 0% to 20% and tracks how Structure Score degrades. Tests whether structure collapses at a threshold or degrades smoothly.

```python
exp = get_experiment("noise_sweep")
results = exp.run_sweep(steps=10, max_error=0.2)
```

### 4. `state_probe` — Which states detect correlated noise best?

A comprehensive 47-condition sensitivity study testing which quantum states best detect correlated noise topologies. Uses the NTC (Noise Topology Correlation) metric across multiple states, error rates, and correlation strengths.

```python
exp = get_experiment("state_probe")
result = exp.run()  # Single run
# Or run the full multi-phase study:
# results = exp.run_all()
```

## Research context

These experiments produced the findings documented in:
- `docs/research/2026-04-hardware-decoherence/` — Hardware results on IBM Quantum
- `docs/research/2026-02-state-probe-study/` — State probe sensitivity findings

The experiments can be run in simulation (`sim_mode="qasm"`) or on real hardware (`sim_mode="hardware"`) using the same interface. See `hardware/` for dedicated hardware experiment suites.
