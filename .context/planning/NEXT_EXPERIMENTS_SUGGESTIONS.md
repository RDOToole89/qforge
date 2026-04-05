# Next Experiment Suggestions: W State Scaling & Topology Resonance

**Date:** 2026-03-18
**Source:** Cross-project discussion (Sommi session) — observations from vector space parallels
**Status:** Proposed, not yet executed

---

## The Core Observation

The fingerprint analysis revealed that GHZ acts like a **broadband antenna** — its all-to-all correlations detect *any* noise topology. W state's single-excitation structure showed zero detection at n=6. But the GHZ scaling data shows a clear qubit-count threshold:

| n | GHZ Effect Size (d) |
|---|---------------------|
| 4 | 1.51 (below significance) |
| 5 | ~2.0 (threshold) |
| 6 | 2.3+ |
| 8 | 3.65 |

**Hypothesis:** W state has a similar threshold, just higher — perhaps n=10-12. The single-excitation subspace grows linearly with n, so the correlation structure may need more qubits to develop enough "surface area" to interact with topology-dependent noise.

---

## Experiment 1: W State Extended Scaling Sweep

### Motivation

We declared W "insensitive" based on n=6 alone. But GHZ was also below significance at n=4. If W's threshold is n=10, we'd miss it entirely at n=6.

### Design

```
States:     W only (GHZ as positive control)
Qubits:     n = 6, 8, 10, 12, 14
Noise:      Chain topology, p=0.2, cs=0.6 (strongest signal from Phase 1)
Shots:      8192
Runs:       5 per config (statistical stability at higher n)
Metrics:    NTC + full fingerprint vector
```

### Predictions

- **Optimistic:** W NTC becomes significant at n=10-12 with d > 2.0. The W fingerprint direction differs from GHZ — revealing that W "sees" different aspects of the noise topology.
- **Null:** W remains flat through n=14. This would confirm W's insensitivity is fundamental (symmetry-based), not just a scaling artifact.

### Why This Matters

If W detects at higher n, it means the **entanglement structure determines the minimum probe size**, not just the measurement basis. Different entanglement geometries need different amounts of "quantum real estate" to resolve topology. This connects directly to the question of how open systems interact with closed systems — the interaction surface scales differently for different entanglement types.

---

## Experiment 2: Topology-Entanglement Resonance

### Motivation

An intriguing question from the fingerprint analysis: GHZ (all-to-all entanglement) detects chain topology. But what if the probe's entanglement topology *matches* the noise topology? Does detection improve?

The hypothesis: **resonance** — when the probe's entanglement graph is isomorphic to the noise topology graph, detection is amplified. When they're orthogonal, detection is suppressed.

### Design

Create topology-matched probe states:

| Probe State | Entanglement Graph | Test Against |
|-------------|-------------------|-------------|
| GHZ | Complete (all-to-all) | Chain, Star, All-to-all |
| Linear Cluster | Chain (nearest-neighbor) | Chain, Star, All-to-all |
| Star Cluster | Star (hub-spoke) | Chain, Star, All-to-all |

**Linear Cluster** is the standard cluster state (already implemented).
**Star Cluster** = prepare |+> on hub qubit, apply CZ from hub to each leaf. Entanglement graph is a star.

```
States:     GHZ, Linear Cluster (X-basis), Star Cluster (adapted basis)
Qubits:     n = 6
Noise:      Chain, Star, All-to-all topologies
Basis:      Adapted per state (Z for GHZ, X for Cluster states)
Parameters: p=0.2, cs=0.6
Shots:      8192
```

### Predictions

- **Resonance hypothesis:** Linear Cluster (X-basis) shows strongest NTC for chain noise, weakest for star noise. Star Cluster shows the inverse. GHZ shows roughly equal sensitivity to all topologies (broadband).
- **Null:** Cluster states show equal sensitivity regardless of noise topology match. This would mean entanglement geometry doesn't interact preferentially with noise geometry.

### What "Resonance" Would Mean

If confirmed, resonance implies the open-closed system boundary has **geometric selectivity** — the environment's correlation structure is most visible when the probe's entanglement structure mirrors it. This is analogous to impedance matching in electrical engineering, or mode matching in optical cavities. It would be a concrete, measurable manifestation of how entanglement topology mediates the system-environment interaction.

---

## Experiment 3: Fingerprint Rotation Under Topology Mixing

### Motivation

Real hardware noise isn't purely "chain" or purely "star." It's a mixture. The ΔCov fingerprint lives in a 15-dimensional vector space (for n=6). If chain and star produce orthogonal directions, what does a 50/50 mixture look like?

### Design

```
Noise model: Mixed topology
  - Pure chain (baseline)
  - Pure star (baseline)
  - 75% chain + 25% star
  - 50% chain + 50% star
  - 25% chain + 75% star

Implementation: For each noise application, randomly select
  chain or star edge set with the mixing probability.

State:      GHZ (n=6)
Parameters: p=0.2, cs=0.6
Shots:      8192
Runs:       5 per mixing ratio
```

### Analysis

1. Extract fingerprint vectors for all 5 conditions
2. Project onto the chain-star plane (first 2 PCs from the pure cases)
3. Plot the trajectory: does the fingerprint rotate smoothly from chain-direction to star-direction as mixing ratio changes?

### Predictions

- **Linear interpolation:** Mixed fingerprint = weighted average of pure fingerprints. Clean rotation in ΔCov space. Would mean fingerprints decompose linearly — you can unmix noise topologies from measurements.
- **Nonlinear:** The trajectory curves or shows discontinuities. Would indicate noise topologies interact nonlinearly when combined — more complex but physically richer.

### Why This Matters

If fingerprints interpolate linearly, you can build a **noise topology decomposer**: measure fingerprint → project onto known topology basis vectors → read off the mixture coefficients. This is practical noise characterization from a single probe state measurement. If nonlinear, you still learn something about how topology correlations interact, which is fundamental physics.

---

## Connection to the Broader Programme

These three experiments extend the existing 4 directions (further_research.md) with a specific focus on the **geometry of the probe-noise interaction**:

```
Existing Programme                    These Additions
─────────────────                    ──────────────────
Dir 1: Measurement Basis        ←→   Exp 2: Topology-matched basis
Dir 2: Fingerprints             ←→   Exp 3: Fingerprint interpolation
Dir 3: Coherent Errors               (independent, do later)
Dir 4: Multi-Round                    (independent, do later)
                                      Exp 1: W scaling (fills data gap)
```

Experiment 1 is pure data collection — fills a gap from Phase 1. Run it first; it's cheap and the answer shapes everything else.

Experiments 2 and 3 test whether the ΔCov vector space has the structure we hope it does — geometric selectivity and linear decomposability. If both confirm, the "structured noise tomography framework" from the existing roadmap becomes a practical tool, not just a theoretical programme.

---

## Implementation Priority

| Order | Experiment | Effort | New Infrastructure | Blocking? |
|------:|-----------|--------|-------------------|-----------|
| 1 | W State Scaling | Low | None (sweep existing configs at higher n) | No |
| 2 | Topology Resonance | Medium | Star cluster state prep + adapted basis | Needs Direction 1 (X-basis) |
| 3 | Fingerprint Mixing | Medium | Mixed topology noise model | Needs Exp 2 baselines |

Start with Experiment 1 — it's a single sweep parameter change and answers whether the W gap is fundamental or just a scaling artifact. That answer determines whether topology resonance (Exp 2) is even worth pursuing with W states.
