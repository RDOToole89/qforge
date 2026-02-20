# Entangled States as Probes for Correlated Noise Topologies

**A Simulation-Based Framework for Quantum Noise Characterisation**

Roibín · Independent Researcher · February 2026

---

> **Thesis:** Entangled states act as structured probes: they transform correlated-noise graphs into measurable, topology-selective signatures in outcome statistics.

---

## 1. What This Research Is About

Quantum computers are noisy. Every operation you perform on qubits introduces errors, and those errors do not always behave independently. In real hardware, when qubit 0 gets an error, qubit 1 (sitting physically next to it) often gets a _correlated_ error at the same time. This is called **correlated noise**, and understanding it matters enormously for building reliable quantum systems.

This research asks a specific, testable question:

> _If I prepare different types of entangled quantum states and then expose them to correlated noise, can I tell which states are better at revealing the structure of that noise?_

Think of it like this: you are in a dark room with a torch. Different torches (UV, infrared, visible light) reveal different things. A UV torch shows fluorescent paint that visible light misses. In this analogy, **entangled states are your torches** and **correlated noise is the hidden structure** you are trying to reveal.

This is not speculative theory. You already have a working simulation framework that can prepare these states, apply controlled noise, and measure the results. This document gives you a clear path from those tools to publishable findings.

---

## 2. The Experimental Setup

Every experiment in this programme has three ingredients: a quantum state you prepare, a noise pattern you apply, and measurements you collect.

### 2.0 The Three Graphs

Before describing the ingredients, it is important to distinguish three graph structures that operate in every experiment. Keeping these separate is essential for clean reasoning and avoids a real confound that can invalidate results.

| Graph             | Symbol    | What It Describes                                                                                                               | Who Controls It                                           |
| ----------------- | --------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| **Noise Graph**   | G_noise   | Which qubit pairs receive correlated noise injection. These are the edges you are trying to detect.                             | You (the experimenter). This is the independent variable. |
| **Circuit Graph** | G_circuit | Which qubit pairs physically interact via two-qubit gates (CX/CZ) during state preparation. Errors propagate along these edges. | Determined by the state preparation circuit.              |
| **State Graph**   | G_state   | The conceptual entanglement or stabilizer structure of the ideal state. This is a mathematical property of the state family.    | Determined by the state definition.                       |

**Why this matters:** For a GHZ state prepared as a CX chain, G*state is "global" (all qubits are maximally entangled with each other in the ideal state), but G_circuit is a chain (CX gates fire sequentially: 0→1, 1→2, 2→3, …). If your NTC result aligns with the chain, is that because the \_state* detected chain noise, or because the _circuit_ created chain-like error propagation paths?

This research primarily tests alignment between the probe and G_noise, while explicitly controlling for and observing confounds from G_circuit. The distinction sharpens Hypothesis 2 (see Section 4).

### 2.1 The Quantum States (Your Probes)

You will prepare four types of quantum states. Each has a different internal correlation structure, which is why they respond differently to noise.

A probe state S is considered "good" if its NTC response to increasing correlation strength is large and stable — formally, if ∂NTC(S)/∂cs is large. This turns the "torch" metaphor into a quantitative definition: a good probe is one where small increases in correlated noise produce large, reliable increases in the topology-selective signal.

| State       | What It Is                                                                                                             | G_state                                      | G_circuit                           | Why It Matters as a Probe                                                                                                                                                                                                                                                                       |
| ----------- | ---------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Product** | Each qubit is independent. No entanglement. Like n separate coins.                                                     | Empty (no edges)                             | Minimal (single-qubit gates only)   | This is your control. Any correlation you see in the output must come from the noise, not the state. Essential baseline.                                                                                                                                                                        |
| **GHZ**     | All qubits maximally entangled in a single global superposition. Like n coins glued together: all heads or all tails.  | Complete (all-to-all, conceptually)          | Chain (sequential CX: 0→1→2→…→n−1)  | GHZ has strong intrinsic correlations; therefore MI-based metrics saturate. Our baseline-subtracted ΔCov removes the dominant state background, restoring sensitivity to noise-induced correlations. The mismatch between G_state (global) and G_circuit (chain) is itself a testable confound. |
| **W**       | Exactly one qubit is in state \|1⟩, but you do not know which one. The excitation is shared equally across all qubits. | Symmetric (democratic pairwise entanglement) | Tree / fan-out (see note below)     | Distributes correlation more evenly. May detect noise patterns that GHZ misses because its structure is more democratic. G_circuit is explicitly non-chain, which helps disentangle the G_circuit confound when comparing against GHZ.                                                          |
| **Cluster** | Qubits entangled in a chain: qubit 0 with 1, qubit 1 with 2, etc. Local neighbour-to-neighbour connections only.       | Chain                                        | Chain (CZ gates between neighbours) | G_state and G_circuit both match a chain topology. Key state for testing whether matching structure to noise boosts detection, and for disentangling the G_state vs G_circuit confound when compared against GHZ.                                                                               |

**Note on W-state preparation circuit:** The standard W-state preparation uses a cascade of controlled-Ry rotations with a tree-like structure. For n = 6: qubit 0 is rotated and then a controlled rotation targets qubit 1; qubit 1 then controls qubit 2; and so on with CNOT swaps at each level to distribute the excitation. The resulting G_circuit is a **directed tree / fan-out** pattern, not a linear chain. This is important: because W's G_circuit differs structurally from both GHZ's chain and Cluster's chain, the W state provides a clean comparison point for disentangling G_circuit effects from G_state effects. The specific circuit used must be documented in every experiment's provenance metadata.

### 2.2 The Noise Topologies (What You Are Trying to Detect)

**Noise topology** (G_noise) refers to **which pairs of qubits experience correlated errors**. You control this in your simulator. Think of it as a graph: qubits are nodes, and you draw edges between pairs that share correlated noise.

| Topology       | Which Pairs Get Correlated Noise                                                             | Real-World Analogue                                                                                                |
| -------------- | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Chain**      | (0,1), (1,2), (2,3), … Each qubit is correlated with its neighbours, like beads on a string. | Nearest-neighbour crosstalk in a linear qubit chip layout (e.g., IBM's superconducting processors).                |
| **Star**       | (0,1), (0,2), (0,3), … One central qubit correlated with all others.                         | A bus qubit or shared coupler that mediates interactions across the chip.                                          |
| **All-to-All** | Every pair of qubits shares correlated noise.                                                | Global noise sources: vibrations, electromagnetic interference, temperature fluctuations affecting the whole chip. |

### 2.3 The Noise Model (How Correlated Noise Works)

Your simulator already implements this, but here is the conceptual picture so you can explain it to others.

Standard quantum noise models (like depolarising noise) assume each qubit gets errors independently. Your **correlated depolarising noise model** adds a crucial feature: for each edge in G_noise, you inject a two-qubit noise channel where the errors on both qubits are coordinated.

You control two parameters:

- **p (error probability):** How much total noise is present. Higher p means more errors overall. Think of it as the volume knob.
- **cs (correlation strength):** How much of that noise is correlated vs independent. At cs = 0, noise on qubit pairs is independent (standard depolarising). At cs = 0.8, most of the noise budget is spent on correlated errors (XX, YY, ZZ Pauli pairs). Think of it as the tuning dial between random static and structured interference.

> **Key insight:** By comparing results at cs = 0 (baseline) against cs > 0 (correlated), you isolate what the correlated component adds. This baseline subtraction is the methodological foundation of the entire programme.

---

## 3. What You Measure

After preparing a state and applying noise, you measure all qubits. You repeat this many times (called shots) and collect a histogram of measurement outcomes (bitstrings). From these raw counts, you extract meaningful statistics.

### 3.1 From Measurement Counts to Covariance

Each measurement gives you an n-bit string like `010110`. You treat each bit position as a random variable B_i that is either 0 or 1. From thousands of shots, you can compute the **covariance matrix**, which tells you how much each pair of qubits tends to flip together.¹

```
Cov(i,j) = E[B_i · B_j] − E[B_i] · E[B_j]
```

If Cov(i,j) is positive, qubits i and j tend to produce the same outcomes more than chance predicts. If it is near zero, they behave independently. _This is the raw signal you are looking for._

> ¹ We compute covariance on bits (B_i ∈ {0,1}); an equivalent formulation uses spins S_i = 2B_i − 1 ∈ {−1,+1}, which makes some formulas more symmetric. The two representations carry identical information and our results do not depend on this choice.

### 3.2 Baseline Subtraction: The Key Move

The entangled state itself produces correlations (a GHZ state has massive built-in covariance). To see what the noise adds, you subtract the covariance you get with no correlated noise from the covariance you get with correlated noise:

```
ΔCov(i,j) = Cov(i,j) at cs > 0  −  Cov(i,j) at cs = 0
```

**This ΔCov (delta-covariance) matrix is your core experimental observable.** Positive values on a qubit pair mean correlated noise is adding extra correlation there. Negative values mean it is suppressing correlation.

### 3.3 NTC: Noise Topology Correlation (Your Primary Metric)

NTC answers the question: **_does the excess correlation concentrate on the edges where we injected correlated noise?_**

Let E be the set of noise edges (pairs in G_noise) and Ē be all other qubit pairs.

```
NTC = (mean ΔCov on edges in E) − (mean ΔCov on non-edges in Ē)
```

Interpreting NTC is straightforward:

- **NTC > 0:** Correlated noise leaves a detectable, topology-aligned fingerprint. The method is working.
- **NTC ≈ 0:** No topology-specific signal. Either the noise is too weak, the state is not sensitive, or the sample size is too small.
- **NTC < 0:** Correlated noise suppresses correlation on edges (anti-alignment). This would be an interesting and publishable finding.

### 3.4 Statistical Significance: The Permutation Test

How do you know your NTC value is not just noise? You use a permutation test. Here is the logic:

1. Keep the ΔCov matrix exactly as measured.
2. Randomly relabel the qubits (shuffle which qubit is called 0, 1, 2, etc.).
3. Recompute NTC using the shuffled edge set.
4. Repeat 1000+ times to build a null distribution.

The **p-value** is the fraction of shuffled NTC values that are as large or larger than your real NTC. A p-value below 0.05 means there is less than a 5% chance the signal appeared by random chance. _You already have this implemented._

### 3.5 Supporting Metrics

Beyond NTC, report these to strengthen your findings:

| Metric                    | What It Tells You                                                                                                            | When to Use It                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| **Effect Size (d)**       | How far apart the edge and non-edge excess means are, normalised by their spread. A d > 0.8 is considered large.             | Always report alongside NTC. Reviewers expect it.                                |
| **Edge / Non-Edge Means** | The two components of NTC reported separately. Shows whether NTC is driven by edges going up, non-edges going down, or both. | Every experiment. Makes the mechanism transparent.                               |
| **Structure Score**       | Overall measure of how structured (non-uniform) the output distribution is. Not topology-specific.                           | As context: confirms noise made the distribution change, even when NTC is small. |

---

## 4. The Three Hypotheses

These are the claims you will test. Stating them upfront makes your research honest and falsifiable. If the data does not support them, that is a valid result too.

### H1: State Sensitivity Ordering

> _For a fixed noise topology, fixed error probability, and fixed correlation strength, some entangled states produce stronger NTC signals than others._

**Why this matters:** If every state gives the same NTC, there is no point choosing one over another. If some states are dramatically more sensitive, you have discovered a practical tool for noise characterisation: prepare the right state, measure, and you learn about the noise.

**Prediction:** GHZ will likely show the strongest NTC at high cs because it has the most fragile, globally entangled structure. Product state will show the weakest NTC because it has no entanglement to amplify the noise signal. W and Cluster will fall in between, but their relative ordering is genuinely unknown and interesting.

### H2: Topology Matching Boosts Detection

> _Matching G_noise to G_circuit or G_state improves detectability — we empirically test which match matters._

**The specific test:** Cluster state has chain-like circuit and state structure (G_circuit = G_state = chain). We test whether NTC is higher when G_noise = chain than when G_noise = star, holding p, cs, and n fixed. Comparing this against GHZ (where G_state is global but G_circuit is a chain) lets us disentangle whether it is the state's conceptual structure or the circuit's physical interaction pattern that drives the matching effect. The W state provides additional leverage because its G_circuit (tree/fan-out) differs from both GHZ and Cluster's chains.

**Why this matters:** If topology matching works, you can use it in reverse. If you do not know the noise topology of your quantum chip, you can prepare different states, see which one gives the strongest signal, and infer the noise structure from the result. This turns your framework into a diagnostic tool.

### H3: Signal Emerges with Qubit Count

> _NTC signal strength and statistical reliability increase as you add more qubits, with a practical detection threshold around 5–6 qubits._

**What you already know:** Your prior experiments showed that 4-qubit systems are statistically underpowered — the NTC values are noisy and p-values are unstable. At 6+ qubits, the signal becomes consistent. This hypothesis formalises that observation and tests whether the trend continues to 7 and 8 qubits.

**On including n=4 and n=5:** These are expected to produce weak or non-significant results based on prior work. They are included deliberately to empirically demonstrate the detection threshold. If the ΔCov-based approach recovers significant signal at n=4 or n=5 where MI-based approaches previously failed, that is itself a strong result — it demonstrates that the methodological improvement (baseline subtraction) has practical impact on the minimum system size needed for noise characterisation.

**Why this matters:** It establishes the practical conditions under which your method works. Every diagnostic tool has a sensitivity threshold, and identifying yours is essential for anyone wanting to use this approach.

---

## 5. The Research Protocol

This is your execution plan. Three phases, each building on the last.

### 5.0 Universal Protocol Requirements

The following requirements apply to **every experiment** across all phases:

1. **Gate-count balancing is mandatory.** All state preparation circuits must be balanced to the same gate count using identity gate padding. Prior work showed that unbalanced circuits created a 3.4× asymmetry artifact in GHZ₃ results — this is not optional. Use `balance="gate_count"` (or equivalent) in every run.

2. **Circuit provenance must be recorded.** Every experiment must log the exact preparation circuit used, including gate count, G_circuit edges, and any balancing applied. This is critical for the three-graph analysis.

3. **Seed control is mandatory.** Baseline (cs = 0) and test (cs > 0) runs for the same condition must use the same random seed to ensure fair comparison.

4. **Minimum shot count: 8192.** Lower counts produce unstable covariance estimates. This is a floor, not a target — use more shots where computationally feasible.

### Phase 1: Sensitivity Ranking Across States

**Goal:** For a single noise topology (chain), determine which states are most and least sensitive to correlated noise.

**Fixed parameters:**

- Qubit count: n = 6
- Error probability: p ∈ {0.1, 0.2, 0.3}
- Correlation strength: cs ∈ {0.0, 0.3, 0.6, 0.8}
- Noise topology: chain
- States: Product, GHZ, W, Cluster
- Gate-count balancing: enabled (mandatory)

**Controls:**

- **Baseline control:** Product state at cs = 0 (no entanglement, no correlated noise). Any non-zero NTC here indicates a methodological problem.
- **Topology-shuffled noise control:** Keep the same number of correlated noise edges, but randomise which qubit pairs are edges. Compute NTC against the _true_ edge set. Prediction: NTC drops to ≈ 0 because the correlated noise is no longer at the expected locations. This confirms that NTC detects _location-specific_ correlation, not just "more correlation in general."

**For each combination:**

1. Run the baseline (cs = 0) and the test condition (cs > 0) with the same random seed to ensure fair comparison.
2. Compute the covariance matrix and ΔCov matrix for each.
3. Calculate NTC, p-value, and effect size.
4. Store results in a structured JSON table (one row per condition).

**Deliverable:** Sensitivity curves showing NTC versus cs for each state, with separate curves for each error probability level. These curves are the core finding of the entire programme.

**Bonus analysis (low cost, high value):** Once the Phase 1 results table is complete, compute the noise fingerprint vector f = vec(ΔCov_ij) for each condition and the cosine similarity matrix between all condition pairs. This is computationally trivial given the data already collected and provides an immediate visual (similarity heatmap) showing whether different states produce distinguishable fingerprints for the same noise topology. If the fingerprints cluster cleanly by noise topology regardless of state, that strengthens the case for noise characterisation. If they cluster by state regardless of topology, that reveals a limitation. Either result is informative.

### Phase 2: Topology Matching

**Goal:** Test whether a state detects noise better when G_noise matches its structure.

**Design:** Pick two noise topologies (chain, star) and two states (GHZ, Cluster). Run all four combinations at n = 6, p = 0.2, cs = 0.6. For GHZ, note that G_state (global) differs from G_circuit (chain) — this is the key comparison that disentangles the two matching hypotheses. Include W state as a third probe: its tree-like G_circuit differs from both chain and star, providing additional leverage for separating G_circuit effects from G_state effects.

**Gate-count balancing:** enabled (mandatory).

**Deliverable:** A 3×2 comparison (three states × two topologies) showing NTC for matched vs mismatched state–topology pairs. Bar plots with confidence intervals.

### Phase 3: Scaling with Qubit Count

**Goal:** Show how NTC evolves from 4 to 8 qubits and empirically identify the detection threshold.

Sweep n ∈ {4, 5, 6, 7, 8} at fixed p = 0.2, cs = 0.6, chain topology. Use the best-performing state from Phase 1.

**Gate-count balancing:** enabled (mandatory). Note that gate counts will differ across qubit counts — balancing ensures fairness _within_ each n, not across n values.

**Framing:** n = 4 and n = 5 are expected to produce weak or non-significant NTC based on prior MI-based experiments. Including them serves two purposes: (a) empirically demonstrating the detection threshold, and (b) testing whether the ΔCov methodology recovers signal at smaller n where MI-based approaches failed.

**Deliverable:** NTC versus n plot, annotated with p-values. Shows the emergence threshold and confirms (or refutes) that larger systems give clearer signals.

---

## 6. Expected Outputs and Visualisations

Each phase produces specific plots that tell the research story.

| Plot                    | X-Axis                    | Y-Axis                 | What It Shows                                                                  |
| ----------------------- | ------------------------- | ---------------------- | ------------------------------------------------------------------------------ |
| **Sensitivity Curves**  | Correlation strength (cs) | NTC value              | One line per state. Reveals which probe is most sensitive at each noise level. |
| **Match vs Mismatch**   | State–Topology pair       | NTC value (bar height) | Do matched pairs produce higher NTC? Direct test of H2.                        |
| **Emergence Plot**      | Qubit count (n)           | NTC and p-value        | Where does the signal become statistically reliable?                           |
| **Edge Decomposition**  | Experimental condition    | Mean ΔCov              | Two bars per condition (edge mean and non-edge mean). Shows mechanism.         |
| **Shuffled Control**    | True vs shuffled topology | NTC value              | Confirms signal is location-specific, not just "more correlation."             |
| **Fingerprint Heatmap** | Condition pairs           | Cosine similarity      | Do different states/topologies produce distinguishable ΔCov signatures?        |

---

## 7. What Success Looks Like

If the results support your hypotheses, you will be able to make these claims:

- **Entangled quantum states can serve as structured sensors for correlated noise.** Different states have measurably different sensitivity to the same noise.
- **Sensitivity depends on the match between state topology and noise topology.** This makes it possible to infer noise structure from state response.
- **Baseline-subtracted covariance with topology-selective scoring (NTC) is a robust diagnostic.** The metric is simple, interpretable, and statistically testable.

Even partial success is publishable. If H2 fails (topology matching does not matter), that is itself an interesting finding: it means noise detection is state-dependent but not topology-matchable, which constrains how you can use these probes.

### 7.1 What This Research Is Not

To keep the scope honest and reviewers satisfied, be clear about boundaries:

- This is a simulation study, not a claim about hardware behaviour (yet).
- You are not discovering new physics. You are developing a measurement methodology.
- The noise model is a controlled abstraction. Real noise is messier, and extending to hardware is future work.
- NTC is not a universal noise diagnostic. It tests topology alignment specifically.

### 7.2 Future Work: Noise Fingerprinting and Classification

The Phase 1 bonus analysis (fingerprint vectors and cosine similarity) opens a natural extension path. If fingerprints prove distinguishable, the next steps are:

**Clustering:** Apply unsupervised clustering (e.g., k-means or hierarchical) to the fingerprint vectors across all experimental conditions. If noise topologies form distinct clusters regardless of probe state, the method generalises.

**Classification:** Train a simple classifier (e.g., logistic regression or nearest-centroid) to predict noise topology from the fingerprint vector. Cross-validate across states to test whether a classifier trained on Cluster-state fingerprints can predict topology when given GHZ-state fingerprints. Success here would demonstrate practical noise tomography.

**Scaling:** Test whether fingerprint distinguishability improves with qubit count, paralleling the NTC emergence in Phase 3.

This is not required for the current programme but positions the work toward practical noise tomography and connects to the broader quantum error characterisation literature.

### 7.3 Completed Results (February 2026)

The full three-phase protocol has been executed. See `docs/research-docs/STATE_PROBE_FINDINGS.md` for the complete findings report with data tables. Key results:

**H1 (Sensitivity Ordering) — Confirmed, stronger than predicted:**
- GHZ: 9/9 significant (all p < 0.01, all d > 2.3), mean NTC = 0.0154
- W: 0/9 significant, mean NTC ≈ 0 (confirmed with 10-seed validation)
- Cluster: NTC = 0.000 exactly, all conditions (Pauli-invariant)
- Product: NTC = 0.000 exactly, all conditions (Pauli-invariant)

**H2 (Topology Matching) — Partially confirmed:**
- GHZ detects chain noise (NTC = 0.013, p = 0.006) but not star noise (NTC = -0.005, p = 1.0)
- G_circuit alignment (not G_state) is the dominant driver of detection
- Shuffled-topology control confirms location-specificity: 70% NTC reduction when edges are randomized

**H3 (Scaling) — Confirmed:**
- Detection threshold at n ≥ 5 qubits
- Effect size scales from d = 1.5 (n=4) to d = 3.65 (n=8)

**Novel finding — Pauli Invariance Blindness:**
States with uniform Z-basis probability distributions (cluster, product superposition) are provably invisible to Pauli noise channels under Z-basis measurement. Any Pauli error permutes bitstrings within the uniform distribution, leaving measurement statistics unchanged. This is a fundamental constraint on NTC-based noise characterisation: the measurement basis must be adapted to the probe state.

### 7.4 Future Work: Measurement-Basis Extension

The Pauli invariance finding opens the most promising extension direction. The current study uses Z-basis (computational basis) measurement exclusively. The key insight is:

> **Probe sensitivity depends on the triple (state, noise topology, measurement basis), not just (state, noise topology).**

**Immediate next experiment:** Measure cluster states in the X-basis (apply H to all qubits before measurement). The cluster state's X-basis distribution is non-uniform (it concentrates on stabilizer eigenstates), so Pauli noise should produce detectable ΔCov in X-basis measurements. If this recovers NTC sensitivity for cluster states, it demonstrates that:

1. Cluster states can serve as probes with the right measurement basis
2. The (state, basis) pairing determines which noise channels are visible
3. Multiple measurement bases on the same state could triangulate noise structure

**Extended programme:**

| State | Z-basis (done) | X-basis | Stabilizer-adapted |
| --- | --- | --- | --- |
| GHZ | Strong signal | Predict: weak (uniform in X) | Predict: strong |
| Cluster | Zero (proven) | Predict: non-zero | Predict: strong |
| W | Weak | Predict: unknown | Predict: unknown |
| Product | Zero (proven) | Predict: zero (uniform in all Pauli bases) | N/A |

**Why this matters:** If measurement-basis adaptation recovers sensitivity for cluster states, the framework becomes a complete noise characterisation toolkit. Different (state, basis) combinations act as orthogonal probes, each revealing different aspects of the noise structure. This is analogous to quantum state tomography, but for noise rather than states.

---

## 8. Implementation Notes

Your existing framework already supports everything needed:

| Research Need        | Your Existing Capability                                    |
| -------------------- | ----------------------------------------------------------- |
| Prepare states       | State factory: GHZ, W, Cluster, Product via engine API      |
| Apply noise          | Correlated depolarising noise model with (p, cs) parameters |
| Run experiments      | engine.api.run() and sweep() with seed control              |
| Extract covariance   | Covariance extraction from QASM counts                      |
| Compute NTC          | topology_comparison routine                                 |
| Significance testing | Permutation test with qubit-label shuffling                 |
| Gate-count balancing | balance="gate_count" in state preparation                   |
| Output results       | JSON structured output + histogram generation               |
| Visualise results    | React Native dashboard consuming JSON output                |

**The main new piece** is a study harness (e.g. **_state_probe_sensitivity.py_**) that loops over states, runs baseline and test conditions, computes all metrics, and writes a single results table. Each row of that table contains: state, n, p, cs, noise_topology, ntc, p_value, effect_size, edge_excess, non_edge_excess. All plots and the dashboard are generated from this table.

**Dashboard integration:** The results table schema (Appendix B) is designed to be directly consumable by the React Native dashboard. Each row is a self-contained experiment record. The dashboard should support filtering by state, topology, and qubit count, and render the sensitivity curves, bar plots, and heatmaps described in Section 6.

---

## Appendix A: Glossary of Terms

This glossary explains every technical term used in this document in plain language. Terms are grouped by category.

### A.1 Quantum Basics

**Qubit** — The quantum equivalent of a classical bit. A classical bit is either 0 or 1. A qubit can be in a superposition of both simultaneously. When you measure it, you get either 0 or 1, but before measurement it can be in a blend of both. Physically, a qubit might be a superconducting circuit, a trapped ion, or a photon.

**Superposition** — A qubit in superposition is not 0 and not 1 — it is in a combination of both. The state |+⟩ means the qubit has equal probability of measuring 0 or 1. Superposition is fragile: noise and measurement both destroy it. The notation |0⟩ and |1⟩ (called _ket notation_) is just the standard way physicists write quantum states.

**Entanglement** — When two or more qubits are entangled, their measurement outcomes are correlated in a way that cannot be explained by classical physics. If you measure one, it instantly tells you something about the other, no matter how far apart they are. Entanglement is not magic communication — it is a correlation that was established when the qubits interacted.

**Bitstring** — The result of measuring all qubits at once. For 6 qubits, a bitstring might be `010110`. Each digit is the measurement result (0 or 1) of one qubit. You collect thousands of bitstrings (shots) and count how often each one appears to build a probability distribution.

**Shots** — The number of times you run and measure an experiment. Since quantum measurement is probabilistic, you need many repetitions (typically 8192 or more) to get reliable statistics. More shots means less statistical noise in your results.

**Two-Qubit Gate (CX / CZ)** — A quantum operation that acts on two qubits simultaneously and can create entanglement between them. CX (controlled-NOT) flips the target qubit if the control qubit is |1⟩. CZ (controlled-Z) applies a phase flip. These are the building blocks for creating entangled states. Every two-qubit gate creates an edge in G_circuit.

### A.2 Quantum States Used in This Research

**Product State (|+⟩⊗n)** — Each qubit is independently in superposition. There is no entanglement. Like flipping n separate coins. This is your control: any correlations in the output must come from noise, not from the state. G_state is empty (no edges), G_circuit is minimal (only single-qubit gates).

**GHZ State** — Named after Greenberger, Horne, and Zeilinger. For n qubits: (|00…0⟩ + |11…1⟩)/√2. This means the system is in a superposition of _all qubits are 0_ and _all qubits are 1_. There is nothing in between. This creates maximal global correlation: if you measure any qubit, you immediately know all the others. GHZ states are extremely fragile — any noise on any qubit can collapse the superposition. Important subtlety: G_state is conceptually global (all-to-all), but G_circuit is typically a chain of CX gates (0→1→2→3…).

**W State** — For n qubits, the W state is an equal superposition of all states where exactly one qubit is 1: (|100…0⟩ + |010…0⟩ + |001…0⟩ + …)/√n. The single excitation is democratically shared. W states are more robust than GHZ: losing one qubit does not destroy the entanglement in the remaining qubits. G_circuit is a tree/fan-out structure from the cascade of controlled rotations used in preparation, which is structurally distinct from both chain and star topologies.

**Cluster State** — Qubits are entangled in a graph pattern. In a _linear cluster_ (which is what you use), qubit 0 is entangled with 1, qubit 1 with 2, qubit 2 with 3, and so on. The entanglement is local — only neighbours are directly connected. Cluster states are the foundation of measurement-based quantum computing. Uniquely, G_state and G_circuit are both chains, making this the cleanest state for topology-matching experiments.

### A.3 Noise Concepts

**Quantum Noise / Decoherence** — Unwanted interactions between a quantum system and its environment that cause errors. Noise is the fundamental obstacle to building useful quantum computers. It turns pure superpositions into mixtures, erases entanglement, and introduces random bit and phase flips.

**Depolarising Noise** — A noise model where, with probability p, a qubit is replaced by a completely random state (losing all its quantum information). With probability 1−p, it is untouched. This is the simplest and most common noise model. It affects each qubit independently.

**Correlated Noise** — Noise where errors on different qubits are not independent. When qubit 0 gets an error, qubit 1 is more likely to also get an error at the same time. In real hardware, this happens because physically adjacent qubits share the same environment (e.g., the same thermal fluctuations or electromagnetic interference).

**Pauli Operators (X, Y, Z)** — Three fundamental single-qubit operations: X flips a qubit (like a NOT gate), Z flips the phase, and Y does both. Every possible quantum error can be expressed as a combination of these three operators and the identity (I, which means no error). When we say the correlated sector is {XX, YY, ZZ}, we mean both qubits experience the same type of error simultaneously.

**Correlation Strength (cs)** — A parameter you control in your simulator, ranging from −1 to 1. It determines what fraction of the noise budget goes to correlated errors (XX, YY, ZZ) versus independent errors. At cs = 0, noise is standard independent depolarising. At cs = 0.8, 80% of the two-qubit noise budget is correlated. The parameter **does not change the total amount of noise**, only its structure.

**Noise Topology (G_noise)** — The graph describing which qubit pairs share correlated noise. The nodes are qubits, the edges connect pairs with correlated errors. A chain topology means qubit 0–1, 1–2, 2–3 share correlated noise. A star topology means qubit 0 shares correlated noise with every other qubit. This is distinct from G_circuit (where gates occur) and G_state (the ideal entanglement structure).

### A.4 Statistical Concepts

**Covariance** — A measure of how much two variables tend to move together. If qubit 0 and qubit 1 both tend to be 1 at the same time (more than chance predicts), their covariance is positive. If they are independent, their covariance is zero. In this research, the covariance matrix captures all pairwise correlations in the measurement results.

**Baseline Subtraction (ΔCov)** — The technique of subtracting the covariance measured with no correlated noise (cs = 0) from the covariance measured with correlated noise (cs > 0). The result shows only what the correlated noise added. This removes the state's inherent correlations, isolating the noise signal.

**NTC (Noise Topology Correlation)** — The primary metric of this research. It compares the average excess covariance on noise edges (where correlated noise was injected) versus non-edges (everywhere else). A positive NTC means the correlated noise left a detectable fingerprint at the expected locations.

**Permutation Test** — A non-parametric statistical test that does not assume any particular distribution (like a normal/bell curve). You keep your data fixed and randomly shuffle the labels. If your real metric is larger than almost all the shuffled versions, you have evidence of a real effect, not just random chance. The beauty is that it makes no assumptions about the shape of your data.

**p-value** — The probability that your observed result (or something more extreme) would occur by chance alone. A p-value of 0.003 means there is only a 0.3% chance the result is a statistical fluke. The standard threshold is 0.05 (5%). Below that, you can claim statistical significance.

**Effect Size (Cohen's d)** — A standardised measure of how large a difference is, regardless of sample size. It is the difference between two group means, divided by their pooled standard deviation. Values of 0.2 are considered small, 0.5 medium, and 0.8+ large. Reporting effect size alongside p-values is best practice because p-values alone do not tell you whether the effect is practically meaningful.

**Confidence Interval (CI)** — A range of values that is likely to contain the true value of a quantity. A 95% CI means: if you repeated the experiment 100 times, about 95 of those intervals would contain the true value. Wider CIs mean less certainty. In your plots, error bars will represent CIs computed via bootstrapping (resampling your data with replacement).

**Cosine Similarity** — A measure of how similar two vectors are, regardless of their magnitude. It computes the cosine of the angle between them: 1.0 means identical direction, 0.0 means orthogonal (unrelated), −1.0 means opposite. Used here to compare noise fingerprint vectors (ΔCov patterns) across experimental conditions.

### A.5 Framework-Specific Terms

**Jeffreys Smoothing** — A method for handling zero counts in probability distributions. If a bitstring was never observed in your shots, its raw probability is 0. But zero probability can cause mathematical problems (like infinity when computing logarithms). Jeffreys smoothing adds a tiny pseudocount (0.5) to every outcome before normalising, so nothing is exactly zero. It is a standard Bayesian technique.

**Gate-Count Balancing** — Ensuring that different quantum states use the same number of quantum gates (operations). This matters because each gate introduces a small amount of noise. If GHZ uses 10 gates and Product uses 2, the difference in NTC might be due to the extra gate noise, not the state's inherent sensitivity. Balancing gate counts (by adding identity gates where needed) ensures fair comparisons. Prior work showed that unbalanced circuits created a 3.4× asymmetry artifact, making this a mandatory protocol requirement rather than an optional feature.

**Seed Control** — Using a fixed random number seed so that experiments are reproducible. Quantum simulation involves random processes (noise injection, measurement sampling). Setting the same seed means you get the same random sequence every time, so you can reproduce results exactly. Different seeds give different random sequences, which you can use to estimate variability.

**Noise Fingerprint Vector** — The flattened vector of all ΔCov values across qubit pairs for a given experimental condition. For n qubits, this vector has n(n−1)/2 elements (one per unique pair). Comparing fingerprint vectors via cosine similarity reveals whether different experimental conditions produce distinguishable correlation patterns.

---

## Appendix B: Result Data Schema

Every experiment produces one row in a results table with this structure:

| Field           | Type    | Description                                                             |
| --------------- | ------- | ----------------------------------------------------------------------- |
| state           | string  | Name of the quantum state (Product, GHZ, W, Cluster)                    |
| n               | integer | Number of qubits                                                        |
| p               | float   | Error probability (total noise level)                                   |
| cs              | float   | Correlation strength (0 = independent, 1 = fully correlated)            |
| noise_topology  | string  | Graph structure of correlated noise (chain, star, all_to_all, shuffled) |
| ntc             | float   | Noise Topology Correlation score                                        |
| p_value         | float   | Statistical significance from permutation test                          |
| effect_size     | float   | Cohen's d: standardised difference between edge and non-edge excess     |
| edge_excess     | float   | Mean ΔCov on noise topology edges                                       |
| non_edge_excess | float   | Mean ΔCov on non-edge qubit pairs                                       |
| gate_count      | integer | Total gates in balanced circuit (for provenance)                        |
| g_circuit_type  | string  | Structure of G_circuit (chain, tree, minimal, etc.)                     |
| seed            | integer | Random seed used for this run                                           |
| shots           | integer | Number of measurement shots                                             |

**Example row:**

```json
{
  "state": "GHZ",
  "n": 6,
  "p": 0.2,
  "cs": 0.8,
  "noise_topology": "chain",
  "ntc": 0.0289,
  "p_value": 0.003,
  "effect_size": 2.67,
  "edge_excess": 0.029,
  "non_edge_excess": -0.0,
  "gate_count": 12,
  "g_circuit_type": "chain",
  "seed": 42,
  "shots": 8192
}
```

---

> **North Star:** I am building a measurement-based method to compare which entangled states are best at detecting correlated noise topologies.
