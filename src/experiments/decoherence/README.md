# Decoherence — Structured Decoherence Research

This is the author's primary research interest and the reason this framework was built.

## The Research Question

> When a quantum state decoheres, do errors spread randomly (like fog diffusing in all directions) or follow structured pathways determined by the entanglement topology (like rain channeling into rivers)?

The answer, based on experiments on three IBM Quantum processors, appears to be: **it depends on the topology.** Some entangled states (GHZ, W) produce highly structured error patterns. Others (Cluster, Product) produce uniform noise. The structure grows with system size, survives deep circuits, and is consistent across hardware.

This is an active research direction. The findings are exploratory and preliminary. The framework is designed to make it easy for others to reproduce, extend, and challenge these results.

```
decoherence/
├── steps/              6-step guided research progression
│   ├── step01 → step06
│   └── README.md
└── deep_dives/         Full research experiments and validation
    ├── dd_topology_full, dd_scaling_full, dd_noise_sweep_full
    ├── dd_state_probe, dd_classical_null
    └── README.md
```

---

## The Research Journey (6 Steps)

This progression mirrors the actual research arc that produced the findings documented in `docs/research/2026-04-hardware-decoherence/`.

### Observe (Steps 1-2)

| Step | Run | What you'll discover |
|------|-----|---------------------|
| 1 | `python -m src.cli run dec_01_river_vs_fog` | The foundational observation — GHZ shows 12x more structure than Product |
| 2 | `python -m src.cli run dec_02_topology_matters` | Four topologies, four behaviors — W surprises, Cluster is invisible |

### Measure (Steps 3-4)

| Step | Run | What you'll discover |
|------|-----|---------------------|
| 3 | `python -m src.cli run dec_03_scaling` | Structure grows with qubit count — the River gets deeper |
| 4 | `python -m src.cli run dec_04_noise_resilience` | Structure degrades smoothly under noise — no sharp collapse |

### Understand (Steps 5-6)

| Step | Run | What you'll discover |
|------|-----|---------------------|
| 5 | `python -m src.cli run dec_05_global_vs_local` | GHZ structure is global, W structure is local — fundamentally different |
| 6 | `python -m src.cli run dec_06_simulation_vs_reality` | Depolarizing over-predicts GHZ, amplitude damping is closer for W |

---

## Deep Dives

| After step | Run | What you'll explore |
|------------|-----|---------------------|
| 2 | Use `dd_topology_full` programmatically | Full topology comparison with all metrics and sweep capability |
| 3 | Use `dd_scaling_full` programmatically | Complete GHZ + W scaling ladder with comparison |
| 4 | Use `dd_noise_sweep_full` programmatically | Comprehensive noise sweep with entropy analysis |
| 5 | Use `dd_state_probe` programmatically | 47-condition sensitivity study across states, noise rates, and correlations |
| 6 | `python -m src.cli run dd_classical_null` | Can classical distributions fake the quantum effect? |

---

## Key Findings (from real hardware)

These findings are documented in detail in `docs/research/2026-04-hardware-decoherence/`.

1. **River vs Fog**: GHZ and W show structured decoherence (SS > 0.7). Cluster and Product show uniform noise (SS ≈ 0.05). The separation is 12x.

2. **Two kinds of River**: GHZ concentrates into 2 peaks (correlated). W distributes across N peaks (distributed). Both are structured, but differently.

3. **Structure scales**: SS grows from 0.45 (2 qubits) to 0.80 (6 qubits) for GHZ, even as fidelity decreases.

4. **Hardware-independent**: Structure Score is consistent across three IBM processors (CV = 5.7%).

5. **Cluster is fog in both bases**: Tested Z and X measurement basis. Cluster structure is below detection threshold on current hardware.

All findings are presented as preliminary observations. The author is not a physicist and welcomes review, reproduction, and critique from the community.

---

## Contributing to This Research

If structured decoherence interests you:

- **Reproduce**: Run the experiments yourself. Compare your results with ours.
- **Extend**: Try different state types, qubit counts, noise models, or hardware platforms.
- **Challenge**: Find alternative explanations. Test null hypotheses we haven't considered.
- **Correct**: If the math or physics is wrong, please open an issue. Correctness matters more than novelty.

The framework makes all of this straightforward. Pick an experiment, modify the config, run it, and analyze the results.
