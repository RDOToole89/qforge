# Advanced — From Quantum Algorithms to Designing Your Own Experiments

You've completed the basics (steps 1-11). You understand qubits, gates, entanglement, and noise. Now learn how quantum algorithms **solve problems** — and build up to designing your own experiments.

```
advanced/
├── steps/              8-step progression to experiment design
│   ├── step01 → step08
│   └── README.md
└── deep_dives/         Apply techniques to real problems
    ├── dd_shor, dd_vqe, dd_qaoa, dd_bb84, ...
    └── README.md
```

---

## The Advanced Journey

### Act 1: Quantum Superpowers (Steps 1-3)

What can quantum do that classical can't?

| Step | Run | What you'll learn | Default metrics |
|------|-----|-------------------|-----------------|
| 1 | `qforge run adv_01_quantum_randomness` | True randomness from physics — better than any algorithm | Structure Score, Total Correlation (~0) |
| 2 | `qforge run adv_02_deutsch_jozsa` | Your first speedup — classify a function in one query | Concentration, Asymmetry Index |
| 3 | `qforge run adv_03_grover_search` | Search with √N speedup — amplitude amplification | Concentration, Asymmetry Index |

### Act 2: Entanglement as a Resource (Steps 4-5)

Entanglement isn't just a phenomenon — it's a tool.

| Step | Run | What you'll learn | Default metrics |
|------|-----|-------------------|-----------------|
| 4 | `qforge run adv_04_teleportation` | Transfer a quantum state using entanglement + classical bits | none (protocol success, not histogram shape) |
| 5 | `qforge run adv_05_superdense_coding` | Send 2 classical bits using 1 qubit + entanglement | none (protocol success) |

### Act 3: The Key Subroutines (Steps 6-7)

The building blocks of real quantum algorithms.

| Step | Run | What you'll learn | Default metrics |
|------|-----|-------------------|-----------------|
| 6 | `qforge run adv_06_qft` | Quantum Fourier Transform — the engine inside Shor's | Asymmetry Index, Concentration |
| 7 | `qforge run adv_07_error_correction` | 3-qubit bit-flip code — protecting quantum information | Concentration, Asymmetry Index |

### Act 4: Design Your Own (Step 8)

Put it all together. Design, configure, run, and analyze your own experiment.

| Step | Run | What you'll learn | Default metrics |
|------|-----|-------------------|-----------------|
| 8 | `qforge run adv_08_design_your_own` | The experiment design pattern — hypothesis → config → run → analyze | Structure Score (add more as you go) |

After Step 8, you're ready to create experiments in `decoherence/`, `hardware/`, or an entirely new direction.

---

## Deep Dives

Apply the techniques from the steps to real-world problems.

| After step | Run | What you'll explore |
|------------|-----|---------------------|
| 2 | `qforge run dd_bernstein_vazirani` | Find a hidden string in one query — a more practical oracle problem |
| 4 | `qforge run dd_bb84` | BB84 quantum key distribution — provably secure communication |
| 6 | `qforge run shor` | Shor's factoring algorithm — uses QFT to break RSA |
| 7 | `qforge run vqe` | VQE — ⟨H⟩ for the 2-qubit H2 operator from Pauli estimates |
| 7 | `qforge run qaoa` | QAOA — MaxCut ⟨C⟩ from one ⟨ZZ⟩ per edge |
| Any | `qforge run grover` | Extended Grover's search with scaling analysis |

---

## The Complete Arc

```
Basics (11 steps)          Advanced (8 steps)           Beyond
─────────────────          ──────────────────           ──────
What is a qubit?     →     Quantum superpowers    →     Topology comparison
What is entanglement? →    Entanglement as tool   →     Scaling ladder
What is noise?       →     QFT + Error correction →     Noise sweep
Noise & entanglement →     Design your own        →     Hardware experiments
                                   ↓
                           You are here: ready to
                           create your own experiments
```
