# Topology-Dependent Decoherence Structures in Entangled Quantum Systems: An Exploratory Study on IBM Quantum Hardware

*Roibin O'Toole, April 2026*

*Exploratory research note — sharing findings and inviting discussion*

---

## Abstract

We report an exploratory study of how entanglement topology shapes the structure of decoherence in small quantum systems (2-6 qubits) on IBM Quantum hardware. Using information-theoretic metrics — Structure Score (Jensen-Shannon divergence from a factorized null model), Total Correlation (multi-information), and Concentration Index — we observe that different entangled states do not merely decohere at different rates, but decohere into qualitatively different classical distributions.

GHZ states produce concentrated, correlated error patterns ("correlated river"), with probability funneling into two macroscopic outcomes and their single-bit-flip neighbors. W states produce distributed, locally structured patterns ("distributed river"), with probability spreading across N single-excitation outcomes. Cluster states and product states produce near-uniform distributions ("fog") consistent with independent qubit noise under the present hardware and measurement conditions.

These patterns are consistent across three independent IBM Heron r2 processors (structure score CV = 5.7%), scale monotonically with qubit count (2-6 qubits), and were not reproduced by the classical null models we tested. Matched simulation comparisons reveal that depolarizing noise models over-predict GHZ structure and under-predict W structure, suggesting real hardware noise interacts with entanglement topology in ways that simple symmetric noise models do not capture.

We present these findings as preliminary observations that we believe merit further investigation, and we describe the open-source framework used to produce them.

---

## 1. Introduction and Motivation

Quantum decoherence — the process by which quantum states lose coherence through interaction with their environment — is typically modeled as a stochastic process where each qubit experiences independent, random errors. Under this assumption, the *pattern* of errors across a multi-qubit system should be unstructured: errors spread roughly uniformly across the space of possible measurement outcomes.

However, in entangled systems, qubits are not independent. A perturbation to one qubit propagates through the entanglement network to others. This raises a natural question:

> **Does the topology of entanglement determine the structure of decoherence?**

If so, different entangled states should produce different error *patterns* — not just different error *rates*. An all-to-all entangled state (GHZ) might channel errors differently than a symmetric excitation-sharing state (W), which might differ again from a nearest-neighbor graph state (Cluster).

We designed a series of experiments to test this on real quantum hardware, using information-theoretic metrics to characterize the *shape* of the decoherence rather than just its magnitude.

### An Analogy

We find it useful to think of decoherence as rain falling on a landscape. The rain (noise) is the same everywhere. But the landscape (entanglement topology) determines where the water collects:

- **Fog**: On flat terrain (product states), water spreads uniformly. Every outcome is equally likely. No rivers, no structure.
- **River**: In a valley (entangled states like GHZ), water channels into rivers and lakes. Probability concentrates in specific outcomes determined by the entanglement topology.

The question is whether this analogy holds on real hardware, and whether different landscapes produce different kinds of rivers.

---

## 2. Methods

### 2.1 Hardware

All hardware experiments were performed on IBM Quantum Heron r2 processors (156 qubits, heavy-hex topology) accessed via `qiskit-ibm-runtime`. Three backends were used: `ibm_fez` (median T1 = 140 us, T2 = 99 us), `ibm_kingston` (T1 = 260 us, T2 = 135 us), and `ibm_marrakesh` (T1 = 191 us, T2 = 98 us). All circuits used logical qubits [0..N-1] mapped to adjacent physical qubits via Qiskit's default transpiler at optimization level 1.

### 2.2 States

Four entanglement topologies were tested at 6 qubits:

| State | Entanglement | Circuit | Transpiled Depth |
|-------|-------------|---------|-----------------|
| GHZ | All-to-all correlation | H + CNOT chain | 24 |
| W | Symmetric excitation sharing | Givens rotation cascade | 52 |
| Cluster | Nearest-neighbor graph | H + CZ chain | 9 |
| Product | None | H on all | 4 |

### 2.3 Metrics

We characterize each measurement distribution using four information-theoretic metrics:

**Structure Score (SS)**: Jensen-Shannon divergence between the observed distribution P and a factorized null model Q (product of single-qubit marginals). SS = 0 indicates independent qubit behavior; higher values indicate inter-qubit correlation in the errors.

**Total Correlation (TC)**: Multi-information, defined as the sum of individual qubit entropies minus the joint entropy. TC quantifies how much knowing one qubit's outcome reduces uncertainty about the others.

**Concentration Index (CI)**: A Gini-like measure of how concentrated probability mass is in a few outcomes versus spread across many. CI ≈ 1 for uniform distributions; CI >> 1 for concentrated ones.

**KL Divergence from uniform**: How far the distribution is from maximum entropy.

All metrics are computed from raw measurement counts (8,192 shots per experiment) using our open-source analysis framework. No post-selection or error mitigation is applied.

### 2.4 Simulation Comparison

Matched simulations were performed using Qiskit Aer with depolarizing noise (2% per gate) and amplitude damping noise (2% per gate) to compare against hardware results.

### 2.5 Framework

All experiments were conducted using our open-source quantum experiment framework, which provides a clean engine API, automated provenance capture, and a suite of structured decoherence metrics. The framework and all data are available at [repository link].

---

## 3. Results

### 3.1 Entanglement Topology Determines Decoherence Structure (Hardware)

We observe a clear separation between entangled states that produce structured decoherence and those that do not:

| State | SS | TC | CI | Fidelity | Depth |
|-------|------|------|--------|----------|-------|
| GHZ | 0.745 | 2.908 | 426 | 0.640 | 24 |
| W | 0.818 | ~0.5* | ~313* | 0.908 | 52 |
| Cluster | 0.060 | 0.010 | 1.5 | 0.994 | 9 |
| Product | 0.061 | 0.005 | 1.5 | 0.995 | 4 |

*\*W-6 TC and CI values from the topology comparison run could not be recomputed (full counts not saved). Values shown are from the later scaling run with full counts. See errata note.*

GHZ and W produce highly structured distributions (SS > 0.7). Cluster and Product produce distributions indistinguishable from independent qubit noise (SS ≈ 0.06). The separation is large: a 12x difference in Structure Score and a 280x difference in Concentration Index.

Notably, the Cluster state is genuinely entangled (it is a stabilizer state with nearest-neighbor CZ entanglement), yet it shows no detectable structure. We tested both Z-basis and X-basis measurement; neither revealed structure (SS = 0.048 and 0.046 respectively). The Cluster state's entanglement appears to be below the detection threshold under current hardware noise levels.

**The two structured states produce qualitatively different distributions:**

- **GHZ (correlated river)**: Two dominant outcomes — |000000⟩ (30.8%) and |111111⟩ (33.2%) — with errors concentrated in single-bit-flip neighbors. High TC (~2.9-4.4 depending on run) indicates strong inter-qubit correlation.
- **W (distributed river)**: Six dominant outcomes — the single-excitation states |100000⟩ through |000001⟩, each at 14-16% — with |000000⟩ (excitation loss) as a minor seventh peak. Low TC (~0.4-0.6) indicates each qubit carries structure with weaker inter-qubit dependence.

This suggests that "structured decoherence" is not a single phenomenon but admits at least two distinct modes, determined by the entanglement topology.

### 3.2 Structure Scales with System Size (Hardware)

GHZ states were run at 2, 3, 4, 5, and 6 qubits. Structure Score increases monotonically:

| Qubits | Fidelity | SS | TC | CI |
|--------|----------|------|------|--------|
| 2 | 0.947 | 0.447 | 0.702 | 20 |
| 3 | 0.927 | 0.676 | 1.523 | 75 |
| 4 | 0.873 | 0.747 | 2.186 | 195 |
| 5 | 0.852 | 0.788 | 2.969 | 638 |
| 6 | 0.786 | 0.786 | 3.542 | 558 |

Fidelity decreases with system size (more qubits = more accumulated gate error), yet structure *increases*. TC grows approximately linearly at +0.7 bits per qubit, consistent with the CNOT chain propagating correlated errors additively.

### 3.3 GHZ and W Scale Differently (Hardware)

W states were run at the same qubit counts for comparison. Both show increasing structure, but through different mechanisms:

**GHZ — Amplification**: Entropy stays flat (~1.5-2.0 bits regardless of N) while the entropy gap (H_max - H) grows from 34% to 74%. Probability compresses into fewer, taller peaks.

**W — Redistribution**: Entropy grows with N (1.5 → 3.7 bits), tracking closer to H_max. The entropy gap grows more slowly (27% → 39%). Each added qubit adds a new structured pathway.

| N | GHZ SS | GHZ entropy gap | W SS | W entropy gap |
|---|--------|----------------|------|--------------|
| 2 | 0.440 | 33.7% | 0.396 | 27.4% |
| 3 | 0.664 | 48.9% | 0.511 | 29.3% |
| 4 | 0.750 | 55.2% | 0.589 | 31.2% |
| 5 | 0.799 | 60.8% | 0.697 | 37.4% |
| 6 | 0.899* | 74.1% | 0.730 | 38.5% |

*\*GHZ-6 ran on ibm_kingston (better coherence) due to auto-selection; SS comparison remains valid per backend comparison results.*

W circuits are approximately 2x deeper than GHZ at each qubit count (52 vs 24 at 6 qubits). The fact that W shows comparable or higher structure scores despite significantly deeper circuits is inconsistent with circuit depth as the primary driver of the observed structure.

### 3.4 Structure is Hardware-Independent (Hardware, 3 backends)

The same GHZ-6 experiment was run on all three available IBM backends:

| Backend | T1 (us) | Fidelity | SS |
|---------|---------|----------|------|
| ibm_fez | 140.5 | 0.798 | 0.800 |
| ibm_kingston | 260.3 | 0.926 | 0.892 |
| ibm_marrakesh | 191.2 | 0.898 | 0.876 |

Structure Score coefficient of variation: **5.7%**. Three physically distinct processors with T1 values ranging from 140 to 260 microseconds produce structure scores within a tight band. This is consistent with the structure being a property of the quantum state rather than the specific hardware.

We note that better hardware (higher T1) shows slightly *higher* structure scores, which we interpret as lower background noise making the structured pathways more visible.

### 3.5 Structure is Global for GHZ, Local for W (Analysis of hardware data)

Marginal analysis of the hardware counts reveals where the structure "lives" in each state:

| Marginal level | GHZ KL from uniform | W KL from uniform |
|---------------|-------------------|-----------------|
| Full 6-qubit | 4.44 | 2.31 |
| Mean 3-qubit | 1.71 | 0.99 |
| Mean 2-qubit | 0.83 | 0.64 |
| Mean 1-qubit | 0.001 | 0.310 |

GHZ structure is **purely global**: individual qubits show no detectable deviation from 50/50 (KL ≈ 0). The structure exists only in the correlations between qubits.

W structure is **local and global**: individual qubits are biased ~80/20 toward |0⟩ (KL = 0.31). Each qubit "knows" the excitation is probably elsewhere. Structure is detectable at every level from single qubits up.

### 3.6 Simulation Comparison (Simulation)

Matched simulations with 2% depolarizing noise reveal systematic differences from hardware:

**GHZ**: Simulation over-predicts structure at 2-5 qubits (sim SS 5-8% higher than hardware), converging at 6 qubits. This is expected — real hardware has noise sources beyond depolarizing.

**W**: Hardware shows slightly more structure than depolarizing simulation predicts. At 6 qubits: hardware SS = 0.730 vs simulation SS = 0.684 (7% higher). Hardware TC ≈ 0.43 vs simulation TC = 0.38 — a modest difference consistent with different noise profiles rather than a fundamental gap.

We tested whether amplitude damping (which models T1 relaxation, the dominant noise channel in superconducting hardware) better predicts the W results:

| Model | W-6 SS | SS error vs HW |
|-------|--------|---------------|
| Hardware | 0.730 | — |
| Depolarizing 2% | 0.684 | 0.045 |
| Amplitude damping 2% | 0.764 | 0.035 |

Amplitude damping is closer for SS (error 0.035 vs 0.045) and on the correct side (slightly over-predicting rather than under-predicting). This is consistent with the physical picture: amplitude damping causes |1⟩→|0⟩ transitions, which concentrates the W distribution toward its natural structure rather than scrambling it.

**Note on earlier TC values:** Initial reports from this study claimed a 6x TC gap between hardware and simulation for W states. Upon recomputation from saved full count data, this gap was found to be a reporting artifact — the live session extracted TC from incomplete counts, inflating the values. The corrected hardware TC (~0.43) is within 1.1x of simulation (0.38). See errata document for details. This correction does not affect SS-based findings.

### 3.7 Classical Null Models (Simulation)

We tested whether classical probability distributions with similar shapes could reproduce the hardware metric signatures. Seven classical models were tested, including distributions designed to mimic GHZ and W shapes:

| Source | SS | TC | CI |
|--------|------|------|--------|
| Real GHZ-6 (hardware)* | 0.899 | 4.350 | 988 |
| Classical fake-GHZ | 0.868 | 4.038 | 55 |
| Real W-6 (hardware) | 0.730 | ~0.5* | ~313* |
| Classical fake-W | 0.810 | 0.997 | 59 |

*\*GHZ-6 reference values here are from the ibm_kingston backend comparison run (best coherence). The topology comparison run on ibm_fez gives SS = 0.745, TC = 2.908, CI = 426. The qualitative conclusion (CI >> classical) holds for both.*

Classical models can approximate SS and TC individually, but no tested model reproduced the Concentration Index observed on hardware. Real GHZ produces CI = 426-988 (depending on backend) vs CI = 55 for the closest classical match — an **8-18x difference**. This gap arises because real quantum decoherence creates structured error neighborhoods (single-bit-flip neighbors of the ideal state), while classical models spread their noise floor uniformly.

We emphasize that this does not prove the effect is "uniquely quantum" in a Bell-inequality sense — only that the specific pattern of concentration was not reproduced by the classical models we tested. More sophisticated classical models might narrow this gap.

---

## 4. Discussion

### 4.1 What we observe

Our central observation is:

> **Different entanglement topologies do not merely decohere at different rates. They decohere into qualitatively different classical structures.**

This manifests in three ways:

1. **Shape**: GHZ concentrates into 2 peaks (correlated river); W distributes across N peaks (distributed river); Cluster/Product spread uniformly (fog).

2. **Scaling**: GHZ amplifies (entropy stays flat, gap grows); W redistributes (entropy grows, new pathways emerge). Both show increasing SS with qubit count, but through different mechanisms.

3. **Locality**: GHZ structure is purely global (invisible at single-qubit level); W structure is local (each qubit carries a structural signature).

### 4.2 What we do not claim

- **Universality**: Structured decoherence is not universal across all entangled states. The Cluster state — genuinely entangled — shows no detectable structure under current hardware noise. The effect is selective and topology-dependent.

- **Mechanism**: We observe correlations between entanglement topology and decoherence structure, but we do not establish a causal mechanism. The structure could arise from entanglement constraining which error transitions are quantum-mechanically accessible, from noise-entanglement interaction effects, or from a combination of factors.

- **Noise model validity**: Our simulation comparisons show where depolarizing and amplitude damping models agree and disagree with hardware for SS. An earlier version of this note reported a large TC discrepancy that was subsequently found to be a reporting artifact (see errata). The corrected comparison shows hardware and simulation TC values within ~1.1x for W states.

- **Precision of specific values**: The numerical values of SS, TC, and CI depend on shot count, hardware calibration, and measurement basis. We consider the *qualitative* patterns (River vs Fog, amplification vs redistribution, global vs local) to be the robust findings.

### 4.3 Relationship to existing work

The observation that entangled states exhibit structured decoherence is broadly consistent with the quantum error correction literature, which has long recognized that errors in entangled systems have structure that can be exploited. Our contribution is to characterize this structure using information-theoretic metrics on real hardware, and to identify the topology-dependent scaling behaviors.

The "River vs Fog" distinction may be related to the concept of decoherence-free subspaces, where certain quantum states are inherently protected from specific noise channels. The W state's resilience on hardware — higher structure despite deeper circuits — could reflect partial protection within the single-excitation subspace.

---

## 5. Open Questions

We present these as directions we find interesting, and where we would welcome input from the community.

**How do different noise models compare for TC predictions?** Our corrected comparison shows hardware and simulation TC values are close for W states (~1.1x ratio), but the SS comparison reveals that amplitude damping better predicts W structure while depolarizing better predicts GHZ. What determines which noise model is most appropriate for a given entanglement topology?

**Does the Cluster state show structure under different conditions?** We tested Z and X basis measurement with null results. Would a different hardware architecture (e.g., trapped ions with all-to-all connectivity and lower noise) reveal Cluster structure? Is the absence of detectable structure inherent to the Cluster topology under depolarizing-like noise, or a consequence of our specific noise level and hardware?

**How does the scaling extend beyond 6 qubits?** SS appears to approach a ceiling near 0.8-0.9 for GHZ. Does it saturate? Does W continue to add new pathways? At what qubit count does circuit depth on current hardware overwhelm the structure? Future hardware with better coherence times may make 10-20 qubit experiments feasible.

**Can structured decoherence be exploited for error correction?** If errors follow predictable pathways, correction could be targeted at those pathways. Has anyone investigated topology-aware error correction that exploits the specific decoherence structure of the logical state being protected?

**What happens with correlated noise models?** Our framework includes correlated depolarizing noise (topology-dependent Pauli correlations). Running comparisons with more realistic noise models could reveal which correlation structures best match hardware for different state topologies.

**Is the Fog-River distinction related to measurement-induced phase transitions?** The sharp boundary between structured and unstructured decoherence (12x SS gap) is reminiscent of phase transitions. Is there a critical noise threshold where Rivers collapse into Fog? Our simulation noise sweep suggests a continuous degradation, but the hardware data doesn't have enough noise-rate resolution to test this.

---

## 6. Experimental Summary

| # | Experiment | Platform | Key Finding |
|---|-----------|----------|-------------|
| 1 | GHZ scaling (2-6q) | Hardware (ibm_fez) | SS grows 0.45→0.79 with qubit count |
| 2 | Topology comparison (4 states, 6q) | Hardware (ibm_fez) | GHZ/W = River, Cluster/Product = Fog |
| 3 | Backend comparison (GHZ-6, 3 chips) | Hardware (3 backends) | SS consistent at 5.7% CV |
| 4 | Measurement basis (Cluster Z vs X) | Hardware (ibm_fez) | Cluster = Fog in both bases |
| 5 | GHZ vs W scaling (2-6q) | Hardware (mixed*) | GHZ amplifies, W redistributes |
| 6 | Noise sweep (GHZ/W at 0-20%) | Simulation | GHZ decays slowly, W decays faster |
| 7 | Marginal analysis (GHZ/W) | Analysis of HW data | GHZ = global, W = local structure |
| 8 | Classical null model (7 models) | Simulation | CI distinguishes quantum from classical (18x) |
| 9 | Matched simulation (depol. 2%) | Simulation | Depolarizing over-predicts GHZ, under-predicts W |
| 10 | Noise model comparison | Simulation vs HW data | Amp. damping closer for W (SS); TC comparable |

*\*GHZ-6q point in Experiment 5 ran on ibm_kingston due to auto-selection; see Section 3.3.*

---

## 7. Data and Reproducibility

All experiments were conducted using the QForge, an open-source research tool built on Qiskit. The framework provides:

- Automated circuit preparation for GHZ, W, Cluster, Bell, and Product states
- Readout error support and noise model configuration
- Eight information-theoretic decoherence metrics with bootstrap confidence intervals
- Hardware execution via IBM Quantum Runtime (SamplerV2) with full provenance capture
- Simulation backends (qasm, statevector, density matrix) for matched comparisons

Every hardware result includes provenance: backend name, job ID, calibration snapshot (T1/T2 medians), transpilation details (depth, SWAP count, qubit layout), software versions, and git SHA.

Raw measurement counts, analysis results, and the framework source code are available at [repository link]. We encourage others to reproduce these experiments, extend them to different hardware platforms, and test whether the topology-dependent decoherence patterns we observe generalize.

---

## Appendix A: Raw Data

### A.1 Topology Comparison (6 qubits, ibm_fez, 8192 shots)

**GHZ top outcomes:**
```
|111111⟩:  2720 (33.2%)    |000000⟩:  2523 (30.8%)
|111110⟩:   588 ( 7.2%)    |000010⟩:   464 ( 5.7%)
|000001⟩:   398 ( 4.9%)
--- remaining 59 outcomes share 18.2% ---
```

**W top outcomes:**
```
|100000⟩:  1311 (16.0%)    |000001⟩:  1254 (15.3%)
|000010⟩:  1245 (15.2%)    |000100⟩:  1213 (14.8%)
|001000⟩:  1212 (14.8%)    |010000⟩:  1206 (14.7%)
|000000⟩:   182 ( 2.2%)
--- remaining 57 outcomes share 7.0% ---
```

**Cluster top outcomes:**
```
|000110⟩: 184 (2.2%)  |000011⟩: 170 (2.1%)  |110110⟩: 167 (2.0%)
--- remaining 61 outcomes share 93.7%, all between 1.1-2.0% ---
All 64 outcomes populated. Near-uniform distribution consistent with fog.
```

**Product top outcomes:**
```
|011110⟩: 167 (2.0%)  |101111⟩: 164 (2.0%)  |101010⟩: 160 (2.0%)
--- remaining 61 outcomes share 94.0%, all between 1.1-2.0% ---
All 64 outcomes populated. Near-uniform distribution consistent with fog.
```

### A.2 Backend Comparison (GHZ 6-qubit, 8192 shots)

| Backend | T1 (us) | T2 (us) | Fidelity | SS | TC | CI | EEC |
|---------|---------|---------|----------|------|------|--------|------|
| ibm_fez | 140.5 | 98.8 | 0.798 | 0.800 | 3.608 | 489 | 0.342 |
| ibm_kingston | 260.3 | 134.5 | 0.926 | 0.892 | 4.350 | 988 | 0.454 |
| ibm_marrakesh | 191.2 | 97.6 | 0.898 | 0.876 | 4.208 | 990 | 0.205 |

### A.3 GHZ Scaling Ladder (ibm_fez, 8192 shots)

| N | Depth | Fidelity | SS | TC | CI | EEC |
|---|-------|----------|------|------|--------|------|
| 2 | 8 | 0.947 | 0.447 | 0.702 | 20 | 0.000 |
| 3 | 12 | 0.927 | 0.676 | 1.523 | 75 | 0.000 |
| 4 | 16 | 0.873 | 0.747 | 2.186 | 195 | 0.127 |
| 5 | 20 | 0.852 | 0.788 | 2.969 | 638 | 0.364 |
| 6 | 24 | 0.786 | 0.786 | 3.542 | 558 | 0.443 |

### A.4 W Scaling Ladder (ibm_fez except 6q*, 8192 shots)

*TC and CI values corrected from saved full counts. See errata.*

| N | Depth | Fidelity | SS | TC | CI |
|---|-------|----------|------|------|--------|
| 2 | 14 | 0.894 | 0.396 | 0.534 | 21 |
| 3 | 22 | 0.884 | 0.511 | 0.623 | 37 |
| 4 | 33 | 0.833 | 0.589 | 0.545 | 227 |
| 5 | 44 | 0.847 | 0.697 | 0.640 | 264 |
| 6 | 52 | 0.763 | 0.730 | 0.427 | 313 |

### A.5 Cluster Basis Comparison (6 qubits, ibm_fez, 8192 shots)

| Basis | Depth | SS | TC | CI | Parity bias |
|-------|-------|------|------|------|------------|
| Z | 9 | 0.048 | 0.005 | 1.38 | 2.0% |
| X | 12 | 0.046 | 0.008 | 1.32 | 0.5% |

### A.6 Noise Model Comparison (Simulation vs hardware reference)

**GHZ-6:**

| Model | SS | ΔSS from HW |
|-------|------|------------|
| Hardware | 0.899 | — |
| Depolarizing 2% | 0.895 | -0.004 |
| Amplitude damping 2% | 0.871 | -0.028 |

**W-6:**

| Model | SS | TC | ΔSS from HW |
|-------|------|------|------------|
| Hardware | 0.730 | 0.427* | — |
| Depolarizing 2% | 0.684 | 0.375 | -0.045 |
| Amplitude damping 2% | 0.764 | 0.495 | +0.035 |

*\*TC corrected from saved full counts. Originally reported as 2.312 due to incomplete count extraction during live session.*
