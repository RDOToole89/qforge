# Publishable Prediction: Spectral Bridge Between Noise Topology and Decoherence Fingerprints

**Date:** 2026-03-18
**Author:** Roibin O'Toole
**Status:** Proposed experiment — the single testable prediction most likely to produce a publishable result
**Builds on:** State Probe Sensitivity Study, ΔCov Fingerprint Analysis, Reconfiguration Space Hypothesis

---

## 1. The Prediction (One Sentence)

**The eigenvalue spectrum of the PCA decomposition of decoherence fingerprints is determined by the eigenvalue spectrum of the graph Laplacian of the noise topology.**

In plain language: the geometric structure you observe in measurement statistics is a direct reflection of the mathematical structure of the noise connectivity graph. The noise topology's "shape" (as captured by its graph Laplacian) predicts the "shape" of the decoherence pattern (as captured by PCA eigenvalues).

If this holds, it's a concrete, falsifiable bridge between graph theory and quantum decoherence — connecting a property of the environment (its topology) to a property of the measurement statistics (their principal component structure) via a precise mathematical relationship.

---

## 2. Why This Is Publishable

Most decoherence research treats noise as a scalar (error rate) or a channel (process matrix). The contribution here is showing that the **topology** of noise — which qubits are correlated with which — leaves a specific, predictable **spectral signature** in measurement statistics.

This matters practically because:
- Hardware calibration could diagnose noise topology from measurement data alone
- Error correction could be adapted to the specific noise geometry
- Noise characterization wouldn't require explicit tomography — the computation itself becomes a sensor

It matters theoretically because:
- It demonstrates that decoherence has geometric structure beyond scalar degradation
- It connects graph theory (Laplacian spectrum) to quantum information (fingerprint PCA) via a concrete mapping
- It provides empirical evidence for the idea that geometry emerges from transformation structure (Section 3 of the Reconfiguration Space Manifesto)

**Target venues:** Physical Review Letters (if the result is clean and the connection is tight), Physical Review A (if more detail is needed), or New Journal of Physics (open access, good for novel frameworks).

---

## 3. Background: The Two Spectra

### 3.1 The Graph Laplacian Spectrum (Noise Side)

Every noise topology is a graph G = (V, E) where vertices are qubits and edges connect correlated qubit pairs.

The **graph Laplacian** is:

```
L = D - A
```

where:
- A is the adjacency matrix (A_ij = 1 if qubits i,j are correlated, 0 otherwise)
- D is the degree matrix (D_ii = number of edges connected to qubit i)

For n qubits, L is an n×n matrix. Its eigenvalues λ₀ ≤ λ₁ ≤ ... ≤ λ_{n-1} encode the topology's structure:

| Eigenvalue property | What it means |
|-------------------|---------------|
| λ₀ = 0 always | Connected component (trivially true for connected graphs) |
| λ₁ (algebraic connectivity) | How "connected" the graph is — higher = more tightly coupled |
| Multiplicity of 0 | Number of disconnected components |
| Spectral gap (λ₁ - λ₀) | How quickly information spreads across the graph |
| Full spectrum shape | Complete topological fingerprint of the graph |

**Examples for n=6:**

**Chain** (1-2-3-4-5-6):
```
L_chain = [[1,-1,0,0,0,0],
           [-1,2,-1,0,0,0],
           [0,-1,2,-1,0,0],
           [0,0,-1,2,-1,0],
           [0,0,0,-1,2,-1],
           [0,0,0,0,-1,1]]

Eigenvalues: [0, 0.268, 1.0, 2.0, 3.0, 3.732]
```

**Star** (qubit 1 connected to all others):
```
L_star = [[5,-1,-1,-1,-1,-1],
          [-1,1,0,0,0,0],
          [-1,0,1,0,0,0],
          [-1,0,0,1,0,0],
          [-1,0,0,0,1,0],
          [-1,0,0,0,0,1]]

Eigenvalues: [0, 1, 1, 1, 1, 6]
```

**Ring** (1-2-3-4-5-6-1):
```
Eigenvalues: [0, 1, 1, 3, 3, 4]
```

**Complete** (all-to-all):
```
Eigenvalues: [0, 6, 6, 6, 6, 6]
```

Note how different these spectra are. Chain has a gradually increasing spectrum. Star has a degenerate middle (all leaves are equivalent). Complete has maximum degeneracy. These spectral differences should show up in the decoherence fingerprints.

### 3.2 The PCA Eigenvalue Spectrum (Measurement Side)

From Phase 1 and Direction 2 results, we extract ΔCov fingerprints — 15-dimensional vectors (for n=6) representing the excess pairwise covariance under noise.

Running PCA on a collection of fingerprints produces eigenvalues μ₁ ≥ μ₂ ≥ ... ≥ μ_k that capture how variance is distributed across principal components.

From Direction 2 results (GHZ, chain noise):
```
PC1: 79.7% of variance (scaling axis)
PC2: 10.0% (topology distinction)
PC3:  4.0% (fine structure)
```

This spectrum — how quickly the eigenvalues decay — encodes the effective dimensionality of the decoherence pattern. A steep decay (one dominant PC) means the noise produces a simple, one-dimensional pattern. A flat decay means the noise produces a complex, high-dimensional pattern.

### 3.3 The Predicted Connection

**Hypothesis:** The PCA eigenvalue spectrum {μ_k} of decoherence fingerprints is functionally related to the graph Laplacian eigenvalue spectrum {λ_k} of the noise topology.

Specifically, the conjecture has three levels of increasing strength:

**Level 1 (Weak):** The number of significant PCA components equals the number of distinct Laplacian eigenvalues. Chain (6 distinct eigenvalues) → 5-6 significant PCs. Star (3 distinct: 0, 1, 6) → 2-3 significant PCs. Complete (2 distinct: 0, 6) → 1-2 significant PCs.

**Level 2 (Moderate):** The ratio of consecutive PCA eigenvalues correlates with the ratio of consecutive Laplacian eigenvalues. Where the Laplacian has a large gap, PCA has a large gap. Where the Laplacian has degeneracy, PCA shows near-degenerate components.

**Level 3 (Strong):** There exists a monotonic function f such that μ_k ≈ f(λ_k) for all k. The PCA spectrum is a transformed version of the Laplacian spectrum. The function f depends on the probe state and noise parameters (p, cs) but not on the topology itself — topology is entirely encoded in {λ_k}.

Level 1 alone is publishable. Level 2 is a strong paper. Level 3 is a significant contribution.

---

## 4. Experimental Design

### 4.1 Phase A — Multi-Topology Fingerprint Collection

**Goal:** Collect ΔCov fingerprints for many different noise topologies, all at the same noise parameters, to isolate the effect of topology.

**Topologies to test (n=6):**

| Topology | Edges | Laplacian eigenvalues | Distinct eigenvalues |
|----------|-------|----------------------|---------------------|
| Chain | (1,2)(2,3)(3,4)(4,5)(5,6) | [0, 0.27, 1.0, 2.0, 3.0, 3.73] | 6 |
| Star | (1,2)(1,3)(1,4)(1,5)(1,6) | [0, 1, 1, 1, 1, 6] | 3 |
| Ring | (1,2)(2,3)(3,4)(4,5)(5,6)(6,1) | [0, 1, 1, 3, 3, 4] | 4 |
| Complete | all 15 pairs | [0, 6, 6, 6, 6, 6] | 2 |
| Path-star | (1,2)(2,3)(3,4)(3,5)(3,6) | computed at runtime | ~5 |
| Two-chain | (1,2)(2,3) + (4,5)(5,6) | has λ₀=0 twice (disconnected) | ~4 |
| Ladder | (1,2)(2,3)(4,5)(5,6)(1,4)(2,5)(3,6) | computed at runtime | ~5 |

Seven topologies gives enough variation to test the spectral relationship while keeping the experiment manageable.

**Fixed parameters:**
```python
state = "ghz"        # Best probe — broadband detector
n_qubits = 6
error_rate = 0.15    # Moderate
correlation_strength = 0.6  # Strong enough for clear signal
shots = 8192
runs_per_topology = 10  # Need good statistics for PCA
```

**For each topology:**
1. Run 10 independent experiments (different seeds)
2. Extract the full ΔCov matrix from each run
3. Flatten to 15-dimensional fingerprint vector
4. Collect all 10 fingerprints into a 10×15 matrix
5. Run PCA on this matrix → get PCA eigenvalue spectrum {μ_k}

**Also compute:**
6. The graph Laplacian L for the topology
7. Its eigenvalue spectrum {λ_k}

**Total experiments:** 7 topologies × 10 runs = 70 runs. At 8192 shots each, this is fast — maybe 10 minutes on a simulator.

### 4.2 Phase B — The Spectral Comparison

**For each topology, produce:**

1. **Laplacian spectrum:** the sorted eigenvalues [λ₀, λ₁, ..., λ₅]
2. **PCA spectrum:** the sorted eigenvalues [μ₁, μ₂, ..., μ_k] (normalized to sum to 1 for comparability)

**Analysis 1 — Effective dimensionality test (Level 1):**

For each topology, count:
- N_L = number of distinct Laplacian eigenvalues (treating eigenvalues within 0.01 as degenerate)
- N_P = number of PCA components capturing >95% of variance

**Prediction:** N_P ≈ N_L - 1 (minus 1 because the zero eigenvalue of the Laplacian corresponds to the overall "connected" component, which doesn't contribute to variance structure).

| Topology | N_L | Predicted N_P |
|----------|-----|--------------|
| Chain | 6 | 5 |
| Star | 3 | 2 |
| Ring | 4 | 3 |
| Complete | 2 | 1 |

If this table matches the data, Level 1 is confirmed.

**Analysis 2 — Spectral shape correlation (Level 2):**

Normalize both spectra to [0, 1] range. Compute the Pearson correlation between the normalized Laplacian spectrum (excluding λ₀=0) and the PCA eigenvalue spectrum.

```python
# Pseudocode
for each topology:
    laplacian_spectrum = sorted eigenvalues of L, excluding λ₀=0
    pca_spectrum = PCA eigenvalues, zero-padded to same length

    # Normalize both to [0,1]
    L_norm = (laplacian_spectrum - min) / (max - min)
    P_norm = (pca_spectrum - min) / (max - min)

    correlation = pearsonr(L_norm, P_norm)
```

**Prediction:** Correlation > 0.8 for all topologies. Where the Laplacian has gaps (e.g., star: gap between λ=1 and λ=6), PCA should show corresponding gaps.

**Analysis 3 — Universal transform function (Level 3):**

Plot all (λ_k, μ_k) pairs from all 7 topologies on a single scatter plot. If a universal function f exists, all points should fall on a single curve regardless of topology.

```python
all_points = []
for each topology:
    for k in range(n_components):
        all_points.append((laplacian_eigenvalue[k], pca_eigenvalue[k]))

# Plot and fit
plt.scatter([p[0] for p in all_points], [p[1] for p in all_points],
            color_by_topology)
# Try fits: linear, power law, exponential
```

If the points cluster around a single curve, fit candidates:
- Linear: μ = a·λ + b
- Power: μ = a·λ^α
- Exponential: μ = a·(1 - exp(-b·λ))

The power law is the most physically motivated — it would mean PCA eigenvalues scale as a power of the Laplacian eigenvalues, with the exponent α encoding how "efficiently" the noise topology translates into measurement statistics.

### 4.3 Phase C — Parameter Robustness

**Question:** Does the spectral relationship hold across different noise strengths?

Repeat Phase A for:
```python
error_rates = [0.05, 0.10, 0.15, 0.20, 0.30]
correlation_strengths = [0.3, 0.6, 0.8]
```

But only for 3 topologies (chain, star, complete) to keep it manageable.

**Prediction:** The function f changes (different a, α parameters) but the *form* of the relationship stays the same. The Laplacian spectrum predicts PCA structure at all noise levels, just with different scaling.

If the exponent α is independent of noise parameters — meaning the shape of the PCA spectrum depends only on topology, not on how much noise there is — that's a very strong result. It would mean the topology-fingerprint mapping is a fundamental structural property, not an accident of parameter tuning.

### 4.4 Phase D — Probe State Independence (Stretch Goal)

**Question:** Does the spectral relationship depend on the probe state?

Repeat Phase A with:
- GHZ state (primary)
- W state (if it becomes detectable — see NEXT_EXPERIMENTS_SUGGESTIONS.md)
- GHZ state measured in X-basis

If the Laplacian → PCA mapping is the same regardless of probe state, the spectral bridge is a property of the noise topology itself — completely independent of how you measure it. That would be the strongest possible result and would imply that **noise topology has an intrinsic geometric signature that any sufficiently sensitive probe will recover.**

---

## 5. What New Infrastructure Is Needed

### 5.1 Topology Builder (extend existing)

The framework already has chain, star, and all-to-all builders in `src/core/analysis/core/topology.py`. Need to add:

```python
def ring_adjacency(n: int) -> np.ndarray:
    """Ring: nearest-neighbor + wrap-around."""
    adj = chain_adjacency(n)
    adj[0, n-1] = adj[n-1, 0] = 1
    return adj

def custom_adjacency(n: int, edges: list[tuple[int, int]]) -> np.ndarray:
    """Arbitrary topology from edge list."""
    adj = np.zeros((n, n))
    for i, j in edges:
        adj[i, j] = adj[j, i] = 1
    return adj
```

### 5.2 Graph Laplacian Computation

```python
def graph_laplacian(adjacency: np.ndarray) -> np.ndarray:
    """Compute the graph Laplacian L = D - A."""
    degree = np.diag(adjacency.sum(axis=1))
    return degree - adjacency

def laplacian_spectrum(adjacency: np.ndarray) -> np.ndarray:
    """Sorted eigenvalues of the graph Laplacian."""
    L = graph_laplacian(adjacency)
    eigenvalues = np.linalg.eigvalsh(L)
    return np.sort(eigenvalues)
```

This is ~10 lines of numpy. Trivial to implement.

### 5.3 Correlated Noise from Arbitrary Topology

The framework's correlated depolarizing model currently supports chain, star, and all-to-all. Need to generalize it to accept an arbitrary adjacency matrix:

```python
def correlated_depolarizing_from_adjacency(
    adjacency: np.ndarray,
    error_rate: float,
    correlation_strength: float
) -> NoiseModel:
    """Build correlated depolarizing noise from an arbitrary adjacency matrix."""
    edges = [(i, j) for i in range(len(adjacency))
             for j in range(i+1, len(adjacency)) if adjacency[i,j] > 0]
    # ... existing correlated noise logic, but with edges from adjacency
```

### 5.4 Multi-Topology Sweep Config

```python
TOPOLOGIES = {
    "chain": chain_adjacency(6),
    "star": star_adjacency(6),
    "ring": ring_adjacency(6),
    "complete": all_to_all_adjacency(6),
    "path_star": custom_adjacency(6, [(0,1),(1,2),(2,3),(2,4),(2,5)]),
    "two_chain": custom_adjacency(6, [(0,1),(1,2),(3,4),(4,5)]),
    "ladder": custom_adjacency(6, [(0,1),(1,2),(3,4),(4,5),(0,3),(1,4),(2,5)]),
}
```

### 5.5 Spectral Analysis Module

New analysis module — takes the raw PCA results and Laplacian spectra and produces the comparison plots and correlation metrics. Pure numpy/matplotlib, no quantum circuits.

**Estimated total effort:** 1-2 focused sessions for infrastructure. 1 session for running experiments. 1 session for analysis and visualization.

---

## 6. Expected Results and Interpretation

### 6.1 If the prediction holds (spectral bridge confirmed)

**What you have:** A quantitative law linking noise graph topology to measurement statistics. Given any noise topology G, compute its Laplacian spectrum, apply the transform function f, and you know what the PCA structure of the decoherence pattern will look like — without running a single quantum circuit.

**Paper structure:**
1. Introduction: decoherence has structure beyond scalar error rates
2. Background: graph Laplacians, PCA, correlated noise models
3. Prediction: Laplacian spectrum → PCA spectrum via monotonic transform
4. Experiments: 7 topologies, spectral comparison at 3 levels
5. Results: correlation plots, universal transform function, parameter robustness
6. Discussion: implications for noise characterization and the geometry of decoherence
7. Connection to reconfiguration space framework (brief, forward-looking)

**Title suggestion:** "Spectral Correspondence Between Noise Topology and Decoherence Geometry in Multi-Qubit Entangled States"

### 6.2 If Level 1 holds but Level 3 fails

The effective dimensionality prediction works (N_P matches N_L) but there's no universal transform function. This still publishable — it means topology constrains the *complexity* of decoherence patterns even if the detailed mapping is state-dependent or parameter-dependent. Weaker result but still novel.

### 6.3 If the prediction fails entirely

PCA structure shows no relationship to Laplacian spectrum. This is also publishable as a negative result — it would mean decoherence fingerprint geometry is determined by something other than noise topology alone (perhaps the interaction between noise topology and entanglement topology). That points to the resonance experiment (NEXT_EXPERIMENTS_SUGGESTIONS.md, Experiment 2) as the next step.

**A clean negative result is still a contribution** — it rules out the simplest hypothesis and sharpens the question.

---

## 7. Why This Specific Prediction

Out of everything in the reconfiguration space programme, this prediction has three properties that make it the right first target:

1. **Concrete and falsifiable.** No hand-waving. Either the spectra correlate or they don't. A referee can check the numbers.

2. **Connects two well-understood mathematical objects.** Graph Laplacians are textbook spectral graph theory. PCA is textbook linear algebra. The novelty is in the *connection*, not in either object individually. This makes the paper accessible to both quantum information and graph theory audiences.

3. **Almost all infrastructure already exists.** The framework already computes ΔCov fingerprints, runs PCA, and supports correlated noise. You need to add ~50 lines of code for new topology builders and Laplacian computation. The experiment itself is 70 runs at 8192 shots — maybe 10 minutes of compute time.

The ratio of potential impact to implementation effort is extremely high. This is the low-hanging fruit that validates the entire programme.

---

## 8. From Prediction to Programme

If the spectral bridge holds, it opens a clear sequence of follow-up papers:

1. **This paper:** Spectral correspondence (static, single probe state, single noise type)
2. **Paper 2:** Probe state independence — does the bridge hold for GHZ, W, Cluster in X-basis? (addresses universality)
3. **Paper 3:** Temporal evolution — does the spectral correspondence evolve predictably with circuit depth? (connects to reconfiguration trajectories)
4. **Paper 4:** Coherent noise — does the bridge extend to non-Pauli noise? (addresses generality)
5. **Paper 5:** Hardware validation — run on real quantum devices, compare to simulation predictions

Each paper builds on the previous. Each is independently publishable. Together they constitute a research programme on the geometry of structured decoherence — grounded in one clean, testable prediction.

---

## 9. The Deepest Implication

If the graph Laplacian of the noise topology predicts the PCA structure of decoherence patterns, it means:

**The environment's connectivity graph is encoded in the system's measurement statistics.**

The system "knows" the shape of its environment — not because we told it, but because the shape of the environment determines the geometry of the system's degradation. The noise topology writes its signature into the quantum state, and PCA reads it back.

This is Section 3 of the Reconfiguration Space Manifesto made quantitative:

> *Possible transformations → geometry*

The noise topology defines the possible transformations (which qubit pairs can be correlated). The Laplacian encodes the geometry of those transformations. The PCA spectrum recovers that geometry from measurement data. The full circle — from transformation structure to geometry to measurement — is closed by a single mathematical relationship.

That's the publishable result. Everything else follows from it.
