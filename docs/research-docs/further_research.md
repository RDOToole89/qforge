# Future Research Directions: From Detection to Characterisation

**Building on:** State Probe Sensitivity Study (February 2026)
**Author:** Roibín · Independent Researcher
**Status:** Proposed directions, not yet executed

---

> **Where we are:** We proved that GHZ states detect correlated Pauli noise topologies via NTC, that detection depends on circuit topology matching (G*circuit), and that states with uniform Z-basis distributions are fundamentally blind. These are results about the \_instrument*. The next step is using the instrument to study the _phenomenon_ — the structure of decoherence itself.

---

## 1. The Overarching Question

The completed study answered: **which probes detect correlated noise?**

The next programme asks: **what does correlated noise look like from multiple measurement perspectives, and does it have geometric structure?**

This is a shift from detection (binary: signal or no signal) to characterisation (rich: what shape is the signal, how does it transform, what does it reveal about the underlying physics). Each direction below opens a different window onto the same phenomenon.

---

## 2. Direction 1: Measurement Basis as a Second Probe Dimension

### 2.1 The Motivation

Our strongest theoretical finding was the Pauli invariance theorem: states with uniform Z-basis distributions (Cluster, Product) produce exactly zero NTC signal regardless of noise parameters. But this blindness is specific to the Z-basis. Cluster states have _non-uniform_ distributions in other bases.

The immediate question: if we measure in the X-basis or a stabilizer-adapted basis, do previously blind states become sensitive?

### 2.2 Why This Matters for Structure

If X-basis measurement recovers Cluster sensitivity, we gain something qualitatively new: two complementary views of the same noise. The Z-basis GHZ response and the X-basis Cluster response to identical chain noise will generally produce _different_ ΔCov matrices. The differences between these matrices encode information about the noise that neither view captures alone.

Think of it like medical imaging: a CT scan and an MRI of the same body reveal different tissue contrasts. Neither is "better" — they see different things. Z-basis and X-basis measurements of the same quantum noise are analogous. The combination is richer than either alone.

### 2.3 What We Already Know

**Cluster state in X-basis:** The linear cluster state |C⟩ = ∏CZ\_{i,i+1} H⊗n |0⟩n has a uniform distribution in Z-basis (all bitstrings equally likely) but a _non-uniform_ distribution in X-basis. Specifically, measuring all qubits in the X-basis (applying H to each qubit before measurement) collapses the cluster state onto outcomes determined by its stabilizer structure, which concentrates probability on a strict subset of bitstrings.

**GHZ state in X-basis:** The GHZ state (|00…0⟩ + |11…1⟩)/√2 measured in X-basis produces outcomes with specific parity constraints. The distribution is non-uniform but structured differently than in Z-basis.

**Product state in X-basis:** The |+⟩⊗n state measured in X-basis gives |0⟩⊗n deterministically (since H·H = I). This is maximally _non-uniform_ — a single outcome with probability 1. In principle, any noise that disturbs this would be detectable, but there is no entanglement to amplify the signal.

### 2.4 The Experimental Design

**Phase A — Basis recovery for Cluster states:**

Take the exact same experimental conditions from Phase 1 (n=6, chain noise, p ∈ {0.1, 0.2, 0.3}, cs ∈ {0.3, 0.6, 0.8}) but measure in X-basis instead of Z-basis. Apply Hadamard gates to all qubits immediately before measurement.

- Run Cluster state with X-basis measurement.
- Compute ΔCov and NTC exactly as before.
- Compare against the Z-basis Cluster results (which were identically zero).

**Prediction:** NTC becomes non-zero for Cluster in X-basis. The Pauli invariance is broken because the X-basis distribution is non-uniform, so Pauli noise channels no longer act as invisible permutations.

**Null prediction:** If NTC remains zero in X-basis, it means the Cluster state's structure does not interact with Pauli noise in a way that produces pairwise covariance contrast, regardless of measurement basis. This would be a surprising and important negative result.

**Phase B — Cross-basis comparison:**

Run GHZ in both Z-basis and X-basis under identical noise conditions. Compare the ΔCov matrices.

- If ΔCov_Z ≈ ΔCov_X (same pattern): the noise fingerprint is basis-independent, meaning one measurement perspective suffices.
- If ΔCov_Z ≠ ΔCov_X (different patterns): different bases reveal different facets of the noise structure. This is the more interesting outcome and opens the door to tomographic reconstruction.

**Phase C — Stabilizer-adapted basis:**

For the Cluster state, the natural measurement basis is defined by its stabilizer generators. Measure each qubit in the basis that diagonalises its local stabilizer. This is the measurement basis in which the Cluster state's correlations are most "visible."

This requires computing the stabilizer generators for the linear cluster state and deriving the corresponding single-qubit measurement rotations. For a linear cluster on n qubits, the stabilizer generators are:

```
g_1 = X_1 Z_2
g_i = Z_{i-1} X_i Z_{i+1}   for 1 < i < n
g_n = Z_{n-1} X_n
```

The adapted measurement basis for qubit i depends on its neighbours in the stabilizer graph. This is more complex to implement than simple X or Z measurement, but it represents the "optimal" basis for extracting correlations from the Cluster state.

### 2.5 Deliverables

1. **Basis recovery plot:** NTC for Cluster state in Z-basis (zero) vs X-basis (predicted non-zero) vs stabilizer basis. Side-by-side bar chart with error bars.
2. **Cross-basis ΔCov comparison:** Heatmaps of ΔCov matrices for GHZ in Z vs X basis under identical noise. Visual inspection plus cosine similarity score.
3. **Basis sensitivity table:** For each (state, basis) combination, the maximum NTC achieved across noise parameters. This becomes the "probe catalogue" — a reference table for which state+basis combinations detect which noise types.

### 2.6 What This Opens Up

If different bases reveal different noise structure, the natural next question is: can you _combine_ multi-basis measurements to reconstruct the full noise correlation matrix? This connects to quantum process tomography, but focused specifically on the correlation structure rather than the full channel. It is a more tractable problem and directly useful for hardware calibration.

---

## 3. Direction 2: Noise Fingerprint Analysis

### 3.1 The Motivation

The Phase 1 results produced 9 GHZ ΔCov matrices (3 error rates × 3 correlation strengths). We computed NTC for each — a single scalar summary. But the full ΔCov matrix contains much more information than NTC captures. The fingerprint vector f = vec(ΔCov\_{ij}) for i < j preserves the complete pairwise structure.

### 3.2 Questions to Answer

**Q1: Does the fingerprint scale or shift?**

As cs increases from 0.3 to 0.8 at fixed p, does the fingerprint vector just get longer (same direction, larger magnitude), or does its _direction_ change?

- Compute cosine similarity between f(cs=0.3) and f(cs=0.8) at each error rate.
- sim ≈ 1.0: pure scaling. The noise has one structural signature that amplifies.
- sim < 0.9: pattern shift. Different correlation strengths produce qualitatively different decoherence structures.

**Q2: Does the fingerprint depend on error rate?**

At fixed cs, compare fingerprints across p = 0.1, 0.2, 0.3.

- sim ≈ 1.0 across p: the noise topology signature is robust to total noise level. This would be very useful practically — it means you can identify noise topology even without knowing the exact error rate.
- sim varies with p: higher noise levels distort the fingerprint, which complicates diagnosis.

**Q3: Can you cluster noise topologies from fingerprints?**

If you add the Phase 2 data (chain vs star noise), do the fingerprints separate by topology in a low-dimensional embedding (e.g., PCA or t-SNE on the fingerprint vectors)?

### 3.3 Implementation

This requires no new experiments. All data exists in the Phase 1 and Phase 2 results. The analysis is:

1. Extract the full ΔCov matrix for each GHZ condition (not just the NTC summary).
2. Flatten each into a vector of length n(n−1)/2 = 15 for n=6.
3. Compute the cosine similarity matrix across all conditions.
4. Optionally: PCA on the fingerprint matrix to visualise clustering.

### 3.4 Deliverables

1. **Similarity heatmap:** Cosine similarity between all pairs of GHZ fingerprint vectors, ordered by (p, cs). Look for block structure.
2. **Scaling vs shifting plot:** For each fixed p, plot the cosine similarity between adjacent cs values. A flat line near 1.0 means pure scaling.
3. **PCA scatter:** If Phase 2 chain vs star fingerprints are included, project all fingerprints onto the first 2 principal components. Colour by noise topology.
4. **Robustness summary:** "Fingerprint direction is [stable / unstable] across error rates, and [stable / unstable] across correlation strengths."

### 3.5 What This Opens Up

If fingerprints are stable and topology-separable, the next step is classification: can you train a simple model to predict noise topology from the fingerprint vector? This is the path toward practical noise tomography — measure, extract fingerprint, classify. Cross-validating across different probe states (train on GHZ fingerprints, test on W fingerprints if W becomes detectable in X-basis) would test generalisability.

---

## 4. Direction 3: Coherent Correlated Errors

### 4.1 The Motivation

Everything in the completed study used Pauli noise channels — stochastic errors where each occurrence is random, just biased toward certain operators. Real quantum hardware also experiences _coherent_ errors: systematic, deterministic rotations caused by imperfect calibration, always-on qubit-qubit coupling, or crosstalk.

Coherent errors are fundamentally different from stochastic Pauli errors:

- **Pauli errors** are diagonal in the Pauli basis. They scramble the state randomly. The Pauli invariance theorem applies because the errors act as permutations on measurement outcomes.
- **Coherent errors** are unitary rotations. They trace continuous paths through state space. They accumulate deterministically rather than averaging out. And critically, they are _not_ Pauli operators, so the Pauli invariance theorem does not apply.

This means coherent correlated errors might produce detectable NTC signal on states that were blind to Pauli noise — including Cluster and Product states.

### 4.2 The Physics

The simplest coherent correlated error is an always-on ZZ coupling between neighbouring qubits:

```
U_ZZ(θ) = exp(-i · θ/2 · Z_i ⊗ Z_j)
```

This is a unitary operation (not a noise channel) that rotates the two-qubit state around the ZZ axis by angle θ. In real hardware, this arises from residual coupling that is never perfectly turned off.

For small θ, this looks like a weak entangling interaction. Applied to pairs of qubits along a noise topology graph, it creates _coherent_ correlated errors that have geometric structure: they trace arcs in state space rather than random jumps.

### 4.3 What Changes From the Pauli Case

**Pauli invariance breaks:** The ZZ rotation is not a Pauli operator (it is a continuous rotation, not a discrete permutation). Applied to a Cluster state or Product state, it _changes_ the measurement probability distribution. Therefore ΔCov can become non-zero even for states that were invisible to Pauli noise.

**Accumulation:** Coherent errors add constructively over multiple applications. If you apply the circuit twice, the coherent error doubles (approximately). Pauli errors, being stochastic, grow as √n. This means coherent errors might produce stronger NTC signals at low error rates but more complex behaviour at high error rates.

**Basis dependence changes:** The relationship between measurement basis and detectability may be completely different for coherent errors. States that are "good probes" for Pauli noise may be poor probes for coherent errors, and vice versa.

### 4.4 The Experimental Design

**Phase A — Direct comparison:**

Take the exact Phase 1 conditions (n=6, chain topology, same states) but replace the Pauli correlated noise with coherent ZZ rotations on edge pairs.

- For each edge (i, j) in G_noise, apply U_ZZ(θ) where θ plays the role of "error strength."
- Sweep θ ∈ {0.05, 0.1, 0.2, 0.4} radians (small to moderate rotations).
- Compute ΔCov using the θ=0 condition as baseline (no coherent error applied).
- Compute NTC with the same permutation test.

**Key question:** Does the sensitivity ordering change? Is GHZ still dominant, or do Cluster/Product states gain sensitivity?

**Phase B — Coherent vs stochastic fingerprints:**

For the same noise topology (chain) and the same probe state (GHZ), compare the ΔCov fingerprint from Pauli noise against the fingerprint from coherent ZZ noise.

- If the fingerprints are similar: the NTC metric detects topology regardless of noise type. The method is robust.
- If the fingerprints differ: different noise types produce distinguishable signatures. This means you can potentially identify not just _where_ the noise is, but _what kind_ it is.

### 4.5 Implementation Notes

The main new piece is a coherent correlated noise model. Your framework currently applies noise channels (Kraus operators). For coherent errors, you need to apply unitary gates instead:

```python
# Pseudocode for coherent ZZ coupling on edge (i, j)
from qiskit.circuit import QuantumCircuit
import numpy as np

def apply_coherent_zz(circuit, i, j, theta):
    """Apply ZZ rotation between qubits i and j."""
    circuit.cx(i, j)
    circuit.rz(theta, j)
    circuit.cx(i, j)
```

This is a standard decomposition of the ZZ rotation into native gates. It can be inserted after state preparation (analogous to where noise channels are applied) on each edge in G_noise.

### 4.6 What This Opens Up

Coherent errors have _geometric_ structure. They trace paths on the Bloch sphere (single qubit) or in higher-dimensional state space (multi-qubit). If coherent errors produce richer ΔCov patterns than Pauli noise, the natural next step is to characterise those patterns geometrically:

- **Fubini-Study distance** between the noisy state and the ideal state, as a function of error strength.
- **Curvature** of the error trajectory in state space.
- **Geodesic deviation** — does the coherent error push the state along or away from the "natural" decoherence pathway?

This is where your original SST intuition (decoherence as structured flow along entanglement "springs") becomes most testable. Coherent errors _literally_ create flows in state space, and the entanglement topology determines the geometry of that space. If the flow follows the entanglement structure, you have direct evidence for structured decoherence pathways.

---

## 5. Direction 4: Multi-Round Circuits — Watching Structure Evolve

### 5.1 The Motivation

All completed experiments are single-round: prepare state, apply noise, measure. This captures a _snapshot_ of noise-induced correlations but says nothing about how those correlations evolve over time (circuit depth).

Real quantum computations involve many rounds of gates and noise. The structure of decoherence may change as the circuit deepens:

- Early rounds: noise correlations might be weak and topology-aligned (matching G_noise).
- Middle rounds: correlations might spread beyond the noise topology as errors propagate through subsequent gates.
- Late rounds: the system might thermalise, with correlations becoming uniform and structure disappearing.

Understanding this evolution is central to the question of whether decoherence structure is _persistent_ (useful for error correction) or _transient_ (only visible in a narrow window).

### 5.2 The Experimental Design

**The circuit structure:**

Instead of a single round of (state preparation → noise → measurement), run multiple rounds:

```
Round 1: state preparation → noise layer → identity layer
Round 2:                     noise layer → identity layer
Round 3:                     noise layer → identity layer
...
Round d:                     noise layer → measurement
```

The "identity layer" ensures that the circuit depth increases uniformly without adding new entangling gates. The noise layer applies the same correlated noise model at each round.

Alternatively, for a more realistic model, interleave noise with actual computation gates:

```
Round 1: state preparation → noise → random single-qubit gates → noise
Round 2:                     random single-qubit gates → noise
...
```

The single-qubit gates simulate ongoing computation without adding new two-qubit correlations.

**The measurement protocol:**

At each circuit depth d, measure and compute ΔCov and NTC. This produces a _trajectory_:

```
NTC(d=1), NTC(d=2), NTC(d=3), ...
```

**Parameters:**

- State: GHZ (best probe from Phase 1)
- n = 6
- Noise: chain topology, p = 0.2, cs = 0.6
- Depths: d ∈ {1, 2, 3, 5, 8, 12, 20}

### 5.3 Hypotheses

**H4a: Structure persistence.** NTC remains positive and topology-aligned for moderate circuit depths (d ≤ 5), then decays toward zero as the system thermalises.

**H4b: Structure spreading.** The ΔCov fingerprint changes with depth — initially concentrated on noise edges, then spreading to non-edges as errors propagate. The NTC may remain positive (edges still dominate) but the fingerprint direction rotates in the vector space.

**H4c: Structure amplification.** For coherent errors (Direction 3), NTC might _increase_ with depth as coherent errors accumulate constructively, unlike Pauli errors which average out. This would be a striking difference between stochastic and coherent noise structure.

### 5.4 Deliverables

1. **NTC vs depth curve:** Shows how long the topology-selective signal persists.
2. **Fingerprint evolution:** Cosine similarity between the d=1 fingerprint and each subsequent depth. Decay of similarity indicates structural change.
3. **ΔCov heatmap sequence:** Visual representation of how the covariance pattern spreads or shifts across depths.

### 5.5 What This Opens Up

If structure persists across multiple rounds, it has direct implications for quantum error correction: error correction codes could be designed to exploit the structured nature of noise rather than assuming it is random. If structure is transient, it still provides a diagnostic window — you just need to measure early.

The depth evolution also connects to the Temporal Pathway Stability (TPS) metric from your original framework, which was designed for exactly this purpose but never tested.

---

## 6. How the Directions Connect

The four directions are not independent. They form a coherent programme that progressively reveals more about decoherence structure:

```
Direction 1                Direction 2
(Measurement Basis)        (Fingerprints)
    │                          │
    │  "What do different      │  "What shape is the
    │   views reveal?"         │   noise signature?"
    │                          │
    ▼                          ▼
    ┌──────────────────────────┐
    │  Combined: Multi-basis   │
    │  fingerprint atlas of    │
    │  noise topologies        │
    └──────────────────────────┘
                │
                │  "Does the shape
                │   change over time
                │   or with noise type?"
                │
        ┌───────┴───────┐
        ▼               ▼
   Direction 3      Direction 4
   (Coherent        (Multi-Round
    Errors)          Circuits)
        │               │
        │               │
        ▼               ▼
    ┌──────────────────────┐
    │  Convergence:        │
    │  Geometric structure  │
    │  of decoherence       │
    │  pathways             │
    └──────────────────────┘
```

Direction 1 gives you multiple measurement perspectives. Direction 2 gives you tools to compare and classify those perspectives. Direction 3 introduces the richer noise type that has actual geometric structure. Direction 4 adds the time dimension. Together, they build toward a complete picture of decoherence as a structured, geometric, time-evolving phenomenon — which is what your original SST intuition was reaching for, now grounded in validated methodology.

---

## 7. Recommended Sequencing

| Order | Direction                           | Effort | New Infrastructure Needed                                  | Risk                                        |
| ----: | ----------------------------------- | ------ | ---------------------------------------------------------- | ------------------------------------------- |
|     1 | **Fingerprints** (Direction 2)      | Low    | None — uses existing Phase 1 data                          | Low (analysis only)                         |
|     2 | **Measurement Basis** (Direction 1) | Medium | X-basis measurement option, stabilizer basis computation   | Medium (Cluster might still be insensitive) |
|     3 | **Coherent Errors** (Direction 3)   | Medium | Coherent ZZ noise model (unitary insertion)                | Medium (new noise type, untested)           |
|     4 | **Multi-Round** (Direction 4)       | High   | Depth-sweep circuit builder, multi-round noise application | High (large parameter space, long runtimes) |

Start with Direction 2 because it costs nothing and answers an immediate question about your existing data. Then Direction 1 because it directly tests your strongest theorem. Direction 3 when you are ready for a new noise type. Direction 4 when you want to add the time dimension.

---

## 8. What This Programme Becomes

If the four directions produce positive results, you will have built:

- A **probe catalogue**: which (state, basis) combinations detect which noise types and topologies.
- A **fingerprint atlas**: characteristic ΔCov signatures for different noise topologies, viewable from multiple measurement bases.
- A **noise type discriminator**: the ability to distinguish Pauli from coherent correlated noise based on fingerprint shape.
- A **temporal characterisation**: how noise structure evolves with circuit depth, and whether it persists long enough to be exploitable.

Together, this constitutes a **structured noise tomography framework** — a systematic method for characterising the correlation structure of quantum noise using entangled state probes. That is a genuine contribution to the quantum error characterisation literature, grounded in simulation with a clear path to hardware validation.

---

> **North Star (updated):** I am building a multi-perspective characterisation method that reveals the structure of correlated quantum noise through entangled state probes, complementary measurement bases, and noise fingerprint analysis.
