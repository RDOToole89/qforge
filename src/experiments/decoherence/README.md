# Decoherence — Structure in Noisy Measurement Data

These experiments explore a simple, testable question about noise and entanglement.

## The Question

> When a quantum state decoheres, do the resulting errors spread uniformly across measurement outcomes, or do they concentrate into patterns shaped by the state's entanglement topology?

The experiments in this folder let you investigate this yourself: prepare different entangled states (GHZ, W, Cluster, Product), apply noise, and compare structure metrics (Structure Score, Total Correlation, Concentration Index) across topologies, system sizes, noise rates, and measurement bases. Nothing is assumed in advance — run the experiments and see what the data shows.

```
decoherence/
├── steps/              6-step guided progression
│   ├── step01 → step06
│   └── README.md
└── deep_dives/         Extended experiments and validation
    ├── dd_topology_full, dd_scaling_full, dd_noise_sweep_full
    ├── dd_state_probe, dd_classical_null
    └── README.md
```

---

## The Guided Progression (6 Steps)

### Observe (Steps 1-2)

| Step | Run | What you'll explore |
|------|-----|---------------------|
| 1 | `python -m src.cli run dec_01_structured_vs_uniform` | Structured vs uniform decoherence — compare structure metrics for GHZ and Product states under identical noise |
| 2 | `python -m src.cli run dec_02_topology_matters` | Four topologies compared — how do GHZ, W, Cluster, and Product differ? |

### Measure (Steps 3-4)

| Step | Run | What you'll explore |
|------|-----|---------------------|
| 3 | `python -m src.cli run dec_03_scaling` | How structure metrics change with qubit count |
| 4 | `python -m src.cli run dec_04_noise_resilience` | How structure metrics respond to increasing noise |

### Understand (Steps 5-6)

| Step | Run | What you'll explore |
|------|-----|---------------------|
| 5 | `python -m src.cli run dec_05_global_vs_local` | Global vs local correlation structure — GHZ and W compared |
| 6 | `python -m src.cli run dec_06_simulation_vs_reality` | Where noise models diverge from each other — compare noise models on the same state |

---

## Deep Dives

| After step | Run | What you'll explore |
|------------|-----|---------------------|
| 2 | Use `dd_topology_full` programmatically | Full topology comparison with all metrics and sweep capability |
| 3 | Use `dd_scaling_full` programmatically | Complete GHZ + W scaling ladder with comparison |
| 4 | Use `dd_noise_sweep_full` programmatically | Comprehensive noise sweep with entropy analysis |
| 5 | Use `dd_state_probe` programmatically | 47-condition sensitivity study across states, noise rates, and correlations |
| 6 | `python -m src.cli run dd_classical_null` | Can classical (factorized) distributions produce the same metric values? A null-model check |

---

## Interpreting the Metrics

- **Structure Score (SS)**: Jensen-Shannon divergence from a factorized null model — how far the joint outcome distribution is from what independent qubits would produce.
- **Total Correlation (TC)**: Multi-information across all qubits.
- **Concentration Index (CI)**: Gini-like measure of how concentrated the error mass is among outcomes.

These are general information-theoretic measures of measurement-outcome distributions. What they mean physically depends on the state, the noise model, and the measurement basis — which is exactly what these experiments are designed to probe. Always compare against control states (Product/Superposition) and null models (`dd_classical_null`) before drawing conclusions.

---

## Extending These Experiments

- **Reproduce**: Run the experiments with different seeds and shot counts. Check that conclusions are stable.
- **Extend**: Try different state types, qubit counts, noise models, measurement bases, or hardware platforms.
- **Challenge**: Test alternative explanations and null hypotheses.
- **Correct**: If the math or physics is wrong, please open an issue. Correctness matters more than novelty.

The framework makes all of this straightforward. Pick an experiment, modify the config, run it, and analyze the results.
