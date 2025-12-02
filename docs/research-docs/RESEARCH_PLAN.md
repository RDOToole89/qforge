- **Page 1: Executive Summary** (high-level framing)
- **Appendix A: Detailed Protocol** (step-by-step, all caveats, metrics, data structure)

---

# 📑 Research Plan: Structured Decoherence Pathways in Quantum Systems

---

## Page 1. Executive Summary

**Background**
Quantum noise is usually modeled as effectively random once averaged, producing uniform error distributions. Yet pilot simulations suggest otherwise: entangled multi-qubit states exhibit reproducible, non-uniform patterns in error outcomes.

**Hypothesis**
_Decoherence follows structured pathways shaped by entanglement topology, rather than spreading uniformly._

**Significance**

- **Physics:** Suggests collapse is reconfiguration, not destruction.
- **Computation:** Pathway knowledge may guide noise-aware error correction.
- **Foundations:** Supports structural/relational interpretations of quantum mechanics.

**Research Question**
Does decoherence in entangled systems exhibit reproducible structure in error pathways, or is it indistinguishable from random noise?

**Phased Approach**

1. Validate structure in GHZ₃ (stats, null models, reproducibility).
2. Map entanglement thresholds (product vs entangled, 1–5 qubits).
3. Test topology dependence (GHZ, W, cluster, star, etc.).
4. Compare across noise models (depolarizing, amplitude damping, etc.).
5. Predict unseen pathway structure (scaling, cross-validation).

**Metrics**

- Structure Score (JSD from null).
- Entanglement–Error Correlation.
- Pathway Persistence.
- Concentration Index.
- Total Correlation.

**Success Criteria**

- SS > 0.1, EEC > 0.3, PP > 0.5.
- Threshold at ≥3 qubits.
- Topology- and noise-dependent reproducible patterns.

---

## Appendix A. Detailed Protocol

---

### 1. Pilot Evidence

- GHZ₃, depolarizing noise (p = 0.05, 10k shots).
- Error string **001**: 1.72%, **100**: 0.51% → **3.4× asymmetry**.
- Suggests structured propagation, not uniform randomness.

---

### 2. Hypothesis

Entanglement **binds degrees of freedom** between qubits. Under noise, these bindings guide decoherence along **preferred error pathways**, producing reproducible non-uniform distributions. Collapse is not destruction but **reconfiguration** constrained by topology.

---

### 3. Phases

**Phase 0. Structure Validation**

- Controls: product states, random classical strings.
- Null model: independent per-qubit error rates + readout confusions.
- Tests:
  - Bootstrap confidence intervals.
  - JSD vs null model.
  - Reproducibility across ≥3 seeds.

**Phase 1. Entanglement Threshold**

- States: product, Bell, GHZ₃–₅.
- Prediction: structure appears ≥3 qubits.
- Control: identical marginals, different entanglement.

**Phase 2. Topology Dependence**

- Compare GHZ, W, linear chain, star, cluster.
- Analyze **error pathway fingerprints** per topology.

**Phase 3. Noise Model Independence**

- Depolarizing, amplitude damping, phase damping, bit-flip.
- Normalize by average gate infidelity (χ-matrix or diamond norm).
- Check structure persistence across models.

**Phase 4. Predictive Validation**

- Predict dominant pathways in unseen states.
- Cross-validate: train on GHZ, test on W.
- Extrapolate n=3–4 → n=5+.

---

### 4. Metrics

1. **Structure Score (SS)**
   - JSD between observed counts and null.
   - SS ≈ 0 → random, SS > 0.1 → structure.
   - Bootstrapped CI.

2. **Entanglement–Error Correlation (EEC)**
   - Compute qubit-pair mutual information from counts.
   - Compare with entanglement adjacency.
   - EEC = Spearman( MI , adjacency ).
   - > 0.3 = moderate correlation.

3. **Pathway Persistence (PP)**
   - Rank correlation of top-k error strings across runs.
   - PP > 0.5 = stable structure.

4. **Concentration Index (CI)**
   - Gini coefficient over error string distribution.

5. **Total Correlation (TC)**
   - Difference between joint entropy and sum of marginals.

6. **Complexity Emergence Score (CES)**
   - Track SS vs qubit count.
   - Detect inflection with logistic fit.

**Caveats**

- CES unstable at small n.
- PP requires ≥3 runs.
- Null model accuracy depends on calibration.

---

### 5. Implementation Details

- **Data type:** QASM simulation shots + counts only (no density matrices yet).
- **Pipeline:** analysis decoupled from Qiskit; pure statistics layer.
- **Data structures:**
  - `ExperimentSpec`: state, noise, qubits, runs, seed.
  - `ResultSpec`: counts, metrics, null fit, CI.

- **Versioning:** metrics tracked, schema upgrades allowed.
- **Reproducibility:** fixed seeds, ≥3 independent runs per config.

---

### 6. Validation

- Bootstrap 95% confidence intervals.
- Multiple-comparison correction for thresholds.
- Cross-check with Qiskit Aer and Cirq.
- **Falsification scenarios:**
  - SS ≈ 0 across configs.
  - No correlation with entanglement adjacency.
  - Inconsistent patterns across seeds.

---

### 7. Timeline

- Weeks 1–2: GHZ₃ validation.
- Weeks 3–6: Threshold mapping.
- Weeks 7–12: Topology + noise dependence.
- Weeks 13–16: Predictive validation.

---

### 8. Future Work

- Graph-kernel embeddings of pathway fingerprints.
- Structured noise–aware error correction.
- Physical experiments on hardware (IBM, IonQ).

---

# How to read your metrics (quick cheat-sheet)

**Your hypothesis:** _Decoherence follows entanglement bonds_ → errors prefer the same connections your state entangles.

**Primary indicator**

- **EEC** (Entanglement-Error Correlation): correlation between the **topology weights** and the **observed error correlation (MI) matrix**.
  - **+ and significant** ⇒ errors align with entanglement bonds (supports hypothesis)
  - **\~0** ⇒ errors look topology-independent (falsifies or “no evidence”)
  - **–** ⇒ anti-alignment (interesting counter-evidence)

**Secondary indicators**

- **PCR** (Pathway Concentration Ratio): are a few pathways dominating?
  - **> 2** moderate concentration; **> 5** high. Structure tends to increase PCR.

- **AI** (Asymmetry Index): non-uniformity of outcomes. Big AI supports “something structured,” but by itself is nonspecific.
- **TPS** (Temporal Pathway Stability): do pathway rankings persist across conditions/time?
  - **≥ 0.7** under sweeps ⇒ persistent structure, not flukes.

- **TC** (Total Correlation): global multi-information. Higher TC on structured runs vs matched nulls supports coordination among qubits.
- **CES** (Complexity Emergence Score): does structure “turn on” at ≥3 qubits? If yes, that’s consistent with an entanglement-driven effect.

**Sanity thresholds (you can pre-register these)**

- **EEC:** mean > **0.30** with **p < 0.05** (permutation or Pearson) across ≥3 runs/layouts on GHZ/cluster.
- **PCR:** **> 2.0** on structured runs and ≈1–1.5 on nulls.
- **TPS:** **≥ 0.70** across a sweep (e.g., idle time / T2 sweep).
- **TC:** higher on structured vs randomized baselines.
- **CES:** uptick at ≥3 qubits vs 2-qubit baseline.

# Experiments that prove or falsify your hypothesis

> Goal: separate “entanglement-guided” structure from random or hardware-idiosyncratic artifacts.

## A. Null baseline (falsification target)

- **Setup:** Random circuits (or phase-scrambled versions of your state) with the **same depth and shots** as the real experiment. Also generate **layout-scrambled** versions of your state (same logic, random physical mapping).
- **Expect (if hypothesis true):**
  EEC ≈ 0, PCR \~ 1–2, AI low, TPS low/variable, TC lower.
- **Interpretation:** If EEC > 0.3 and significant _in nulls_, your pipeline has a confound (bit order mismatch, readout bias, etc.).

## B. Topology-preserving vs topology-broken (key test)

- **Setup:** Prepare GHZ/cluster states **aligned to physical couplers** (preserving the entanglement graph). Run matched versions with **intentionally broken mapping** (non-adjacent, detuned edges). Same depth and shots. ≥3 random layouts each.
- **Expect:**
  Preserving: EEC > 0.3 (p<0.05), PCR > 2, TC higher.
  Broken: EEC → 0, PCR smaller, TC lower.
- **Decision:** If preserving > broken by your thresholds (and nulls are near zero), that **supports** the hypothesis.

## C. Temporal/parametric sweeps (stability)

- **Setup:** Sweep idle time (T1/T2-sensitive), gate amplitude/angle, or depth.
- **Expect:** EEC stays positive (maybe slowly decays with time), TPS ≥ 0.7 across the mid-range of the sweep.
- **Falsification:** TPS collapses (<0.4) and EEC bounces around zero with no consistent sign.

## D. Complexity scaling (emergence)

- **Setup:** Run 2, 3, 4, 5-qubit versions (same layout density).
- **Expect:** CES increases at ≥3 qubits; EEC and TC grow with n.
- **Falsification:** Flat CES and EEC ≈ 0 across sizes.

## E. Counterfactual noise injection (specificity)

- **Setup:** In simulation or hardware (if you can), inject **independent** noise vs **pair-correlated** noise.
- **Expect:** Independent noise → EEC ≈ 0; pair-correlated along entangled edges → EEC > 0.3 and significant.
- **Use:** Shows EEC’s specificity to the mechanism you claim.

## F. Cross-layout replication (robustness)

- **Setup:** Same logical state over ≥3 physical layouts.
- **Expect:** EEC tracks the **physical** couplers (layout), not just logical labels.

# Minimal workflow (step-by-step)

1. **Data hygiene**
   - Confirm **bit order/qubit index mapping**. Log one example mapping every run.
   - Fill **missing outcomes with zero** counts (no “others” buckets in production).
   - If available, apply basic **measurement error mitigation** or subtract per-qubit readout bias.

2. **Compute metrics** on each run:
   - EEC (+ p-value & CI), PCR, AI, TPS (if you have ≥2–3 conditions), TC, CES (if multiple n).

3. **Significance testing**
   - Keep bootstrap CIs (already in your stack).
   - Add **permutation p-value** for EEC: shuffle the topology weights vs. MI matrix 1–5k times; p = fraction ≥ observed correlation.

4. **Multiple comparisons**
   - If testing many states/sweeps, control FDR (Benjamini–Hochberg) on EEC p-values.

5. **Decision rules**
   - **Support**: Preserving > broken > null; EEC consistently positive and significant; PCR high; TPS stable; TC elevated; CES increases with n.
   - **Falsify**: EEC \~ 0 on preserving (and nulls) across layouts/sweeps; PCR \~ 1–2; TPS low; TC similar to nulls; CES flat.

# What to plot (so interpretation is obvious)

- **Topology vs Error scatter:** x = Wᵢⱼ (topology weights), y = MIᵢⱼ (error correlation). Add Pearson r (EEC) and p.
- **MI heatmap** side-by-side with **topology heatmap**.
- **EEC permutation null histogram** with observed r marked.
- **PCR bars**: top-quartile vs bottom-quartile mass.
- **TPS line** across the sweep (with CI ribbons).
- **TC vs condition/n**: show global correlation growth.
- **CES curve** vs number of qubits.

# Shot counts & replication (practical guidelines)

- For ≥5-qubit MI estimates, target **≥10k shots** per condition (rule of thumb; you _can_ work lower with wider CIs).
- **Replicate** each condition across **≥3 layouts** for inference on layout-dependence.
- Use **B=500–2000** bootstraps for stable CIs; **1–5k permutations** for EEC p-values.

# Common confounds (and quick fixes)

- **Bit order / labeling mismatch** → nonsense EEC. _Fix:_ one asserted mapping log per run.
- **Readout bias** looks like structure. _Fix:_ basic mitigation or bias subtraction and re-check EEC sign.
- **Sparse tails** inflate PCR. _Fix:_ report top-k sensitivity (k ∈ {10%, 25%, 40%}).
- **Topology parameter λ** (GHZ ring decay) set oddly → weak Wᵢⱼ variance. _Fix:_ keep λ so W has a useful dynamic range (your default EEC_LAMBDA is okay).

# Glossary (plain-English, quick)

- **Bitstring / counts / shots:** Outcomes like “0101” with how many times they appeared; shots = total trials.
- **GHZ/W/Bell/Cluster:** Canonical entangled states (GHZ = all-zeros/all-ones superposition; W = single excitation shared; Bell = 2-qubit maximally entangled; Cluster = graph/nearest-neighbor entanglement).
- **Entanglement topology (Wᵢⱼ):** A matrix that says which qubits are “bonded” (and how strongly) in the ideal state.
- **Error correlation matrix (MIᵢⱼ):** Mutual information between qubit i and j computed from your counts; proxies how often their errors co-move.
- **EEC:** Pearson correlation between Wᵢⱼ and MIᵢⱼ over all i\<j. Positive and significant supports your hypothesis.
- **PCR:** Ratio of mass in the **top** quartile of pathways to the **bottom** quartile; measures concentration.
- **AI:** How far your distribution is from uniform across observed outcomes.
- **TPS:** Stability of pathway rankings across time/conditions (1 = stable).
- **TC (Total Correlation):** Multi-information across all qubits; zero if fully independent.
- **CES:** Where structure “turns on” as you increase qubits.
- **Bootstrap CI:** Resampling your data to get a 95% interval for a metric.
- **Permutation test:** Randomly shuffling labels (e.g., topology/error pairing) to build a null distribution for a correlation.
- **Coupling map:** Physical hardware connectivity; **layout** is which logical qubit lands on which physical qubit.

---
