# SQM Intuitions → Formal Physics: A Study Guide

**Purpose:** For each SQM intuition, this document shows the formal physics it maps to, the actual math, and geometric examples you can visualise. Read alongside `sqm-research-report.md` and the STATE_PROBE_FINDINGS Appendix B.

---

## 1. "Structure, Not Substance"

### Your Intuition
The wavefunction is a real relational structure. What matters is the pattern of relationships between amplitudes, not the amplitudes themselves. A quantum state *is* its geometry.

### The Formal Physics: Projective Hilbert Space & the Fubini-Study Metric

In quantum mechanics, a state vector |ψ⟩ and eiφ|ψ⟩ (same vector with a different global phase) are **physically identical** — no experiment can distinguish them. So the "real" state space isn't the full Hilbert space H, it's the **projective** Hilbert space:

```
    CP^n = { rays in H } = H \ {0} / ~

    where |ψ⟩ ~ |φ⟩  iff  |ψ⟩ = eiθ|φ⟩  for some θ
```

This is a curved manifold (like the surface of a sphere, but in higher dimensions). The natural distance on this manifold is the **Fubini-Study metric**:

```
    d_FS(|ψ⟩, |φ⟩) = arccos( |⟨ψ|φ⟩| )
```

This measures the **angle** between two state rays. It has a beautiful property: it depends only on the inner product — the *relation* between the two states — not on any absolute property of either state alone.

### The Math: Inner Products Are Everything

The inner product ⟨ψ|φ⟩ encodes all physically meaningful information:

```
    |⟨ψ|φ⟩|²  = probability of measuring |ψ⟩ and getting |φ⟩
                = "overlap" between the two states
                = cos²(d_FS)   (geometric: cosine of the angle!)

    ⟨ψ|φ⟩ = 0    → orthogonal → perfectly distinguishable
    |⟨ψ|φ⟩| = 1  → parallel → identical state (up to phase)
    0 < |⟨ψ|φ⟩| < 1  → partially distinguishable
```

### Geometric Example: The Bloch Sphere IS Projective Space

For one qubit, the projective Hilbert space CP¹ is literally the Bloch sphere:

```
                |0⟩ ●  ← north pole
                   /|
                  / |
         |+⟩ ● /  |  The Fubini-Study distance between
                \  |  |0⟩ and |+⟩ is:
                 \ |
                  \|  d_FS = arccos(|⟨0|+⟩|)
                |1⟩ ●       = arccos(1/√2)
                            = π/4  (45°)

    Every point on the sphere = a ray in CP¹
    Antipodal points = orthogonal states (d_FS = π/2)
    Great circle distance = Fubini-Study distance
```

The Bloch sphere isn't just a visualisation trick — it IS the projective Hilbert space for one qubit, equipped with the Fubini-Study metric. Your intuition that "geometry is primary" is literally true here.

### Connection to Your Experiment

When you compute cosine similarity between fingerprint vectors:

```
    cos(θ) = (fv₁ · fv₂) / (||fv₁|| · ||fv₂||)
```

You're doing the same thing as the Fubini-Study metric — measuring the **angle** (relational geometry) between two objects, ignoring their magnitudes (absolute properties). The fingerprint direction is a structural invariant; the magnitude is "substance" that varies with parameters.

---

## 2. "Decoherence Reconfigures, It Doesn't Destroy"

### Your Intuition
When a quantum system decoheres, the state doesn't "collapse" or get randomly destroyed. It changes form — the relational structure reconfigures into a new geometry.

### The Formal Physics: CPTP Maps and Stinespring Dilation

Any physical process on a quantum system (including noise and decoherence) is described by a **completely positive trace-preserving (CPTP) map** E:

```
    ρ  →  E(ρ) = Σᵢ Kᵢ ρ Kᵢ†

    where {Kᵢ} are "Kraus operators" satisfying Σᵢ Kᵢ†Kᵢ = I
```

The Kraus operators are like "possible things the environment does." The trace-preserving condition (Σ Kᵢ†Kᵢ = I) guarantees probabilities still sum to 1.

**Stinespring dilation** is the theorem that makes "reconfiguration not destruction" rigorous:

```
    Any CPTP map on system S can be written as:

    1. Attach a fresh environment E in state |0⟩
    2. Apply a UNITARY U on S+E together
    3. Trace out (ignore) E

    E(ρ_S) = Tr_E [ U (ρ_S ⊗ |0⟩⟨0|_E) U† ]
```

**This is profound:** What looks like irreversible, random destruction from the system's perspective is actually **reversible, unitary evolution** of a larger system. Nothing is destroyed — information moves from the system into the environment. The system's state *reconfigures* to reflect its new relationship with the environment.

### The Math: Depolarising Channel in Kraus Form

The depolarising channel (the noise in your experiment) has Kraus operators:

```
    K₀ = √(1-p) · I      (nothing happens, weight 1-p)
    K₁ = √(p/3) · X      (bit flip, weight p/3)
    K₂ = √(p/3) · Y      (bit+phase flip, weight p/3)
    K₃ = √(p/3) · Z      (phase flip, weight p/3)

    Check: K₀†K₀ + K₁†K₁ + K₂†K₂ + K₃†K₃
         = (1-p)I + (p/3)I + (p/3)I + (p/3)I
         = (1-p+p)I = I  ✓
```

Applied to a density matrix ρ:

```
    E(ρ) = (1-p)ρ + (p/3)(XρX + YρY + ZρZ)
```

### Geometric Example: Depolarising as Shrinking the Bloch Sphere

For a single qubit, the state is ρ = (I + r⃗·σ⃗)/2 where r⃗ is the Bloch vector (length ≤ 1).

The depolarising channel maps:

```
    r⃗  →  (1 - 4p/3) · r⃗

    The Bloch ball shrinks uniformly!
```

```
    Before (pure state):         After (p = 0.3):

         ● r⃗                        ● (1-4p/3)r⃗
        /                           /
       /  |r⃗| = 1                  /  |r⃗| = 0.6
      /                           /
     ●───── centre               ●───── centre

    The STATE moves toward the centre (maximally mixed state).
    It doesn't jump or collapse — it continuously shrinks.
    The DIRECTION is preserved. Only the MAGNITUDE changes.
```

This is exactly what you found in the fingerprint analysis: the noise fingerprint direction is stable (cosine ~ 0.87), only the magnitude changes. Depolarising noise is a uniform contraction — it preserves directions while shrinking magnitudes.

### Geometric Example: Amplitude Damping as Asymmetric Flow

Amplitude damping (modelling energy loss, like photon emission) has a different geometry:

```
    K₀ = [[1, 0], [0, √(1-γ)]]       K₁ = [[0, √γ], [0, 0]]

    Bloch sphere effect:
    rₓ → √(1-γ) · rₓ                  (x-component shrinks)
    r_y → √(1-γ) · r_y                 (y-component shrinks)
    r_z → γ + (1-γ) · r_z              (z-component shifts UP)
```

```
    Before:                  After (γ = 0.5):

         |0⟩ ●                    |0⟩ ●  ← everything drifts
              |                        |     toward |0⟩
              |                      ● | ← centre shifts up
     ●────────●────────●        ●──────●──────●
              |                        |
              |                        (bottom compressed)
         |1⟩ ●                    |1⟩ ●

    The sphere becomes an ELLIPSOID shifted toward |0⟩.
    This is NOT uniform shrinking — it's asymmetric flow.
    Different "Kraus structure" → different geometric deformation.
```

**This is what you observed in early experiments:** different noise types produce different "shapes" of decoherence. Depolarising shrinks uniformly; amplitude damping flows toward |0⟩; phase damping squashes the equator. Each channel has a distinct geometric signature — the "reconfiguration" is channel-specific, not random.

---

## 3. "Noise Filters Rather Than Destroys"

### Your Intuition
Decoherence doesn't randomly erase information. It acts like a filter that selectively suppresses some structures while leaving others intact.

### The Formal Physics: Contractivity of Quantum Channels

This intuition is captured by a fundamental theorem:

**Contractivity:** For any CPTP map E and any valid distance measure D on quantum states:

```
    D(E(ρ), E(σ)) ≤ D(ρ, σ)

    "A quantum channel can never increase the distance between two states."
    "Noise can only make states harder to tell apart, never easier."
```

This holds for trace distance, fidelity, relative entropy, and the entire family of **monotone Riemannian metrics** on quantum state space.

### The Math: Trace Distance Contractivity

The trace distance between two states ρ and σ is:

```
    D_tr(ρ, σ) = ½ ||ρ - σ||₁ = ½ Tr|ρ - σ|

    Operational meaning: the maximum probability of correctly
    distinguishing ρ from σ in a single measurement is:

    P_correct = ½(1 + D_tr(ρ, σ))
```

Contractivity says:

```
    D_tr(E(ρ), E(σ)) ≤ D_tr(ρ, σ)    for all CPTP maps E

    Noise COMPRESSES the space of states.
    States that were distinguishable become less distinguishable.
    But the compression is STRUCTURED, not random.
```

### Geometric Example: Filtering in 2D

Think of the Bloch sphere as a ball. A quantum channel maps the ball to a smaller shape inside itself:

```
    Depolarising:              Amplitude damping:         Phase damping:

    ┌─────────────┐           ┌─────────────┐           ┌─────────────┐
    │  ╭───────╮  │           │      ●       │           │  ╭───────╮  │
    │  │ ╭───╮ │  │           │     ╱ ╲      │           │  │       │  │
    │  │ │ ● │ │  │           │    ╱ ● ╲     │           │  │ ╭─●─╮ │  │
    │  │ ╰───╯ │  │           │   ╱     ╲    │           │  │ │   │ │  │
    │  ╰───────╯  │           │  ╰───────╯   │           │  ╰─┤   ├─╯  │
    └─────────────┘           └─────────────┘           └─────────────┘
    Uniform shrink             Teardrop toward |0⟩       Pancake (z preserved,
    (all directions equal)     (asymmetric filter)        x,y compressed)
    ● = maximally mixed        ● = shifted center        ● = shifted center
```

Each channel "filters" the Bloch ball into a different shape. The shape tells you exactly what information survives:
- **Depolarising:** All directions equally suppressed → no preferred information survives
- **Amplitude damping:** z-information partially survives, x/y information suppressed → energy information survives, phase information lost
- **Phase damping:** z-information fully survives, x/y suppressed → bit values survive, phase coherence lost

**This is geometric filtering.** The "filter" is the shape of the channel's contraction.

### Connection to Your Experiment

Your ΔCov fingerprint measures the *difference* in filtering between two channels (correlated vs independent noise). The fact that ΔCov has structure (chain pattern, not random) means the correlated channel filters *differently* from the independent channel — and the difference has the topology of the noise graph.

---

## 4. "Classical Reality Is What's Stable"

### Your Intuition
Classical states aren't fundamental — they're the quantum states that happen to be stable under environmental interaction. Classicality is an emergent property of certain states that survive decoherence.

### The Formal Physics: Einselection and Pointer States

**Environment-induced superselection (einselection)** is Zurek's program that formalises this exactly.

Given a system S interacting with an environment E via Hamiltonian H_SE, the **pointer states** are the system states that are minimally disturbed by the interaction:

```
    |πₖ⟩ is a pointer state if:

    U_SE (|πₖ⟩_S ⊗ |E₀⟩_E) = |πₖ⟩_S ⊗ |Eₖ⟩_E

    The system state is unchanged! Only the environment changes.
    The environment "records" which pointer state the system is in,
    without disturbing the system.
```

Superpositions of pointer states, in contrast, get entangled with the environment and effectively decohere:

```
    U_SE ((α|π₁⟩ + β|π₂⟩)_S ⊗ |E₀⟩_E) = α|π₁⟩_S ⊗ |E₁⟩_E + β|π₂⟩_S ⊗ |E₂⟩_E

    If ⟨E₁|E₂⟩ ≈ 0 (environment states are distinguishable), then
    tracing out E gives:

    ρ_S ≈ |α|²|π₁⟩⟨π₁| + |β|²|π₂⟩⟨π₂|

    The off-diagonal terms (coherence between π₁ and π₂) vanish!
    Only the pointer states survive. That's classical reality.
```

### The Math: Decoherence-Free Subspaces

A **decoherence-free subspace (DFS)** is a subspace of the system Hilbert space where ALL states are pointer states — the entire subspace is immune to the noise:

```
    A subspace S is decoherence-free under Kraus operators {Kᵢ} if:

    Kᵢ|ψ⟩ = cᵢ|ψ⟩    for all |ψ⟩ ∈ S, for all i

    Every Kraus operator acts as a SCALAR on S.
    The subspace is an eigenspace of the noise.
```

For depolarising noise with Kraus operators {√(1-p)I, √(p/3)X, √(p/3)Y, √(p/3)Z}:

```
    Is |0⟩ decoherence-free?
    I|0⟩ = |0⟩   ✓
    X|0⟩ = |1⟩   ✗ (not proportional to |0⟩!)

    No single-qubit state is decoherence-free under depolarising noise.
    But the MAXIMALLY MIXED state ρ = I/2 is a fixed point:

    E(I/2) = (1-p)(I/2) + (p/3)(X(I/2)X + Y(I/2)Y + Z(I/2)Z)
           = (1-p)(I/2) + (p/3)(I/2 + I/2 + I/2)
           = (1-p)(I/2) + p(I/2)
           = I/2  ✓

    The maximally mixed state is the "ultimate classical survivor" —
    it has zero coherence, zero information, maximum entropy.
    Everything flows toward it under depolarising noise.
```

### Geometric Example: Fixed Points as Attractors

```
    Depolarising channel flow on the Bloch sphere:

         |0⟩ ●─ ─ ─ → ─ ─ ─╮
              |                ╲
              |                 ╲
     |+⟩ ●───┼──── → ──── ●───── ● (centre = I/2)
              |                 ╱
              |                ╱
         |1⟩ ●─ ─ ─ → ─ ─ ─╯

    ALL states flow toward the centre.
    The centre (maximally mixed state) is the FIXED POINT.
    It is the only "classically stable" state under this noise.
```

For **phase damping** (dephasing in Z-basis), the fixed points are different:

```
    Phase damping flow:

         |0⟩ ●  ← FIXED (pointer state!)
              │
              │  (equator collapses to z-axis)
     |+⟩ ● ──┼──→ ● centre of z-axis
              │
              │
         |1⟩ ●  ← FIXED (pointer state!)

    The Z-axis states |0⟩ and |1⟩ survive perfectly.
    Superpositions like |+⟩ decohere to mixtures of |0⟩ and |1⟩.
    "Classical reality" = the Z-basis, because that's what the
    environment's interaction Hamiltonian selects.
```

### Connection to Your Experiment

Your Pauli invariance result is a statement about fixed points:

```
    States with uniform Z-basis distribution (|+⟩ⁿ, Cluster):

    Cov(noisy) = Cov(clean)  →  ΔCov = 0

    These states are FIXED POINTS of the measurement statistics
    under Pauli noise. Not because they're "classical" but because
    their Z-basis distribution is already maximally spread —
    the noise has nothing left to compress in that basis.
```

GHZ is the opposite: it's maximally fragile (far from the fixed point), which is exactly why it's a good probe — the noise has maximum room to push it, and the direction of the push reveals the noise topology.

---

## 5. "Decoherence Follows Pathways"

### Your Intuition
Decoherence doesn't happen uniformly. It follows structured pathways determined by the system's entanglement topology and the noise structure.

### The Formal Physics: Lindblad Master Equation

For continuous-time Markovian decoherence, the dynamics are governed by the **Lindblad equation**:

```
    dρ/dt = -i[H, ρ] + Σₖ γₖ (Lₖ ρ Lₖ† - ½{Lₖ†Lₖ, ρ})
            ──────────   ─────────────────────────────────────
            unitary       dissipative (decoherence)
            (Hamiltonian)

    H = system Hamiltonian
    Lₖ = "Lindblad operators" (jump operators)
    γₖ = decoherence rates for each channel
    {A, B} = AB + BA (anticommutator)
```

The Lindblad operators {Lₖ} define the **decoherence pathways** — they specify which transitions the environment drives. Different sets of Lindblad operators give different decoherence structures.

### The Math: How Pathways Emerge from Operators

For your correlated depolarising noise on a chain of qubits:

```
    Independent noise (cs=0):
    L₁ = X₀,  L₂ = Y₀,  L₃ = Z₀     (errors on qubit 0)
    L₄ = X₁,  L₅ = Y₁,  L₆ = Z₁     (errors on qubit 1)
    ...etc, each qubit independently

    Correlated noise (cs>0, chain topology):
    Additional operators like:
    L_corr = X₀ ⊗ X₁     (SAME error on qubits 0 AND 1)
    L_corr = Y₀ ⊗ Y₁     (correlated Y errors on adjacent pair)
    ...only on pairs connected by chain edges

    The chain topology enters through WHICH pairs get
    correlated Lindblad operators. Non-adjacent pairs don't.
```

This is why ΔCov mirrors the chain adjacency: the correlated Lindblad operators act on specific qubit pairs (the chain edges), creating excess covariance exactly on those pairs.

### Geometric Example: Decoherence Pathways in State Space

```
    State space (schematic, 2 qubits):

              |ψ_entangled⟩
                    ●
                   ╱╲
        path 1   ╱  ╲  path 2
        (ZZ)    ╱    ╲  (XX)
               ╱      ╲
              ●        ●
         |00⟩⟨00|   |++⟩⟨++|
         +|11⟩⟨11|  +|--⟩⟨--|
         (Z-basis    (X-basis
          classical)   classical)

    Path 1 (Z-dephasing): drives toward Z-basis classical mixture
    Path 2 (X-dephasing): drives toward X-basis classical mixture

    The "pathway" = which Lindblad operators dominate
                  = which basis the environment monitors
                  = which classical reality emerges
```

Different noise topologies create different pathways through state space. Your fingerprint vectors capture the *direction* of these pathways projected onto the covariance manifold.

---

## 6. "Time Is Emergent from Relational Structure"

### Your Intuition
Time is not a background parameter — it emerges from the relational structure of the quantum state.

### The Formal Physics: Page-Wootters Mechanism

The **Page-Wootters mechanism** shows how time can emerge from a static, timeless quantum state through entanglement:

```
    Consider a "universe" state |Ψ⟩ that satisfies:

    H_total |Ψ⟩ = 0     (the Wheeler-DeWitt equation)

    The total energy is zero — there is NO time evolution
    of the whole universe. It's a static state.

    But decompose the universe into "clock" C and "system" S:

    |Ψ⟩ = Σₜ |t⟩_C ⊗ |ψ(t)⟩_S

    If you CONDITION on the clock reading time t
    (project onto |t⟩_C), the system state is |ψ(t)⟩.

    From the system's perspective, it evolves in time.
    From the universe's perspective, nothing changes.
    Time = entanglement between clock and system.
```

### The Math: How the Schrödinger Equation Emerges

```
    H_total = H_C ⊗ I_S + I_C ⊗ H_S + H_int

    For a simple clock: H_C = -iℏ ∂/∂t  (generates time translations)

    H_total|Ψ⟩ = 0 becomes:

    (-iℏ ∂/∂t ⊗ I_S + I_C ⊗ H_S)|Ψ⟩ = 0

    Project onto clock state ⟨t|:

    iℏ ∂/∂t |ψ(t)⟩_S = H_S |ψ(t)⟩_S

    This IS the Schrödinger equation!
    It emerged from a timeless constraint + entanglement.
```

### Geometric Example: Time as a Correlation

```
    The "block universe" view:

    Clock state:  |t=0⟩    |t=1⟩    |t=2⟩    |t=3⟩
                    |          |          |          |
                    ↓          ↓          ↓          ↓
    System state: |ψ₀⟩      |ψ₁⟩      |ψ₂⟩      |ψ₃⟩

    The total state |Ψ⟩ is a SINGLE object in C⊗S space.
    It's not "evolving" — it just IS.

    "Time passing" = scanning along the clock degree of freedom
                   = a correlation, not a flow

    Geometrically: |Ψ⟩ is a curve on the projective space
    of the total system. "Time" parametrises the curve.
    The curve exists all at once; the parametrisation is relational.
```

This is the most speculative part of SQM, but it has real technical backing. The key insight: if time emerges from entanglement structure, then decoherence (which reshapes entanglement) also reshapes the experienced flow of time. Your experiments don't test this directly, but the framework (entanglement topology → decoherence pathways → emergent structure) is consistent with it.

---

## 7. "The Fingerprint IS a Geometric Invariant"

### Your Intuition (from the experiment, not the original SQM draft)
Different noise topologies produce different geometric signatures that can be distinguished by their direction in a vector space, independent of noise magnitude.

### The Formal Physics: Information-Geometric Invariants

In quantum information geometry, the **tangent space** at a point on the state manifold carries information about how the state can change. The ΔCov fingerprint is closely related to a **tangent vector** on the covariance manifold:

```
    At the baseline state ρ_baseline, the noise channel E_corr
    pushes the covariance in a specific direction:

    ΔCov = Cov(E_corr(ρ)) - Cov(E_indep(ρ))

    This is a DIRECTIONAL DERIVATIVE of the covariance
    along the "correlated noise" direction in channel space.
```

### The Math: Why Direction Is Invariant

For a linear noise model (which correlated depolarising approximately is), the excess covariance decomposes as:

```
    ΔCov(p, cs) ≈ p · cs · M_topology + O(p²cs²)

    where M_topology is a matrix that depends ONLY on:
    - the noise topology (which pairs are correlated)
    - the state (GHZ, W, etc.)
    - NOT on p or cs individually

    Therefore:
    fv(p, cs) ≈ p · cs · m_topology    (fingerprint vector)

    where m_topology = upper_triangle(M_topology)

    Direction: fv̂ = m_topology / ||m_topology||  (independent of p, cs!)
    Magnitude: ||fv|| ≈ p · cs · ||m_topology||  (scales linearly)
```

This explains your experimental finding:

```
    Cosine similarity between fv(p₁,cs₁) and fv(p₂,cs₂):

    cos(θ) = (p₁cs₁ · m) · (p₂cs₂ · m) / (p₁cs₁||m|| · p₂cs₂||m||)
           = ||m||² / ||m||²
           = 1.0    (exactly, in the linear regime!)
```

Your measured mean cosine of 0.874 (not 1.0) reflects higher-order corrections — the noise model isn't perfectly linear, and finite-shot statistics add noise. But the first-order prediction (perfect scaling) is confirmed.

### Geometric Example: The Topology Manifold

```
    The space of noise fingerprint directions:

    Each noise topology T maps to a unit vector m̂_T:

         m̂_chain = [large, 0, 0, 0, 0, large, 0, 0, 0, large, ...]
                    (concentrated on nearest-neighbor pairs)

         m̂_star  = [large, large, large, large, large, 0, 0, 0, ...]
                    (concentrated on hub-spoke pairs from qubit 0)

         m̂_ring  = [large, 0, 0, 0, large, large, 0, 0, 0, large, ...]
                    (chain + wraparound edge)

    These unit vectors live on the 14-dimensional unit sphere S¹⁴
    (15 components, normalised to length 1).

    The angle between topologies:

         θ(chain, star) = arccos(m̂_chain · m̂_star)

    Your PCA showed these angles are large → topologies are
    GEOMETRICALLY SEPARABLE on the fingerprint sphere.

                    ↑ m̂_star
                    |
                    |  θ ≈ 70-80°
                    | ╱
                    |╱
         ──────────●──────── → m̂_chain
                    |
                    |
                    ↓

    If you added m̂_ring, m̂_grid, m̂_all-to-all, you'd get
    a constellation of points on the sphere. The question:
    is the constellation low-dimensional (few PCs needed)
    or does it fill the sphere? Your 2-topology data says
    2D is enough. More topologies would test this.
```

---

## 8. Summary: SQM → Formalism Bridge

| SQM Intuition | Formal Object | Key Equation | Your Experiment |
|---------------|--------------|--------------|-----------------|
| Structure, not substance | Projective Hilbert space CP^n | d_FS = arccos(\|⟨ψ\|φ⟩\|) | Cosine similarity measures relational angle |
| Decoherence reconfigures | CPTP maps, Stinespring dilation | E(ρ) = Tr_E[U(ρ⊗\|0⟩⟨0\|)U†] | ΔCov shows structured reconfiguration |
| Noise filters | Contractivity | D(E(ρ),E(σ)) ≤ D(ρ,σ) | Fingerprint norms shrink with noise |
| Classical = stable | Pointer states, einselection | U\|πₖ⟩\|E₀⟩ = \|πₖ⟩\|Eₖ⟩ | Pauli-invariant states are fixed points |
| Pathways not randomness | Lindblad operators | dρ/dt = -i[H,ρ] + Σ γₖ(LₖρLₖ† - ½{Lₖ†Lₖ,ρ}) | ΔCov mirrors noise adjacency |
| Time is emergent | Page-Wootters mechanism | H_total\|Ψ⟩ = 0 → iℏ∂ₜ\|ψ(t)⟩ = H\|ψ(t)⟩ | Not directly tested |
| Fingerprint = invariant | Tangent vector on covariance manifold | fv ≈ p·cs·m_topology | Direction stable (cos=0.874), magnitude scales |

---

## 9. What to Study Next (in order)

1. **3Blue1Brown "Essence of Linear Algebra"** (3-4 hours)
   - Vectors, inner products, matrices as transformations
   - After this, the Fubini-Study metric and Kraus operators will click

2. **Density matrices** — understand ρ = |ψ⟩⟨ψ| for pure states and ρ = Σ pᵢ|ψᵢ⟩⟨ψᵢ| for mixed states
   - The Bloch sphere parameterisation ρ = (I + r⃗·σ⃗)/2 ties everything together
   - Try: compute ρ for |+⟩, for |0⟩, for the 50/50 mixture of |0⟩ and |1⟩

3. **Kraus operators** — apply the depolarising channel by hand to a 2x2 density matrix
   - Verify that E(I/2) = I/2 (fixed point)
   - Verify that E(|0⟩⟨0|) has shrunk Bloch vector

4. **Tensor products** — understand |ψ⟩_A ⊗ |φ⟩_B and why entangled states can't be factored
   - This is the bridge to multi-qubit systems and why GHZ is special

5. **The Lindblad equation** — once you have density matrices and Kraus operators, Lindblad is the continuous-time version
   - The jump operators Lₖ define the decoherence pathways
