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

## 9. Foundation: Linear Algebra at Depth

This is the prerequisite everything else rests on. Without it, the equations above are symbols; with it, they're pictures.

### 9.1 Vectors, Bases, and Linear Maps

A quantum state |ψ⟩ is a **vector** in a complex vector space. For one qubit, the space is C² (two complex numbers):

```
    |ψ⟩ = α|0⟩ + β|1⟩ = [α]     where α, β ∈ ℂ and |α|² + |β|² = 1
                          [β]
```

A **basis** is a set of vectors that spans the space. The Z-basis {|0⟩, |1⟩} and the X-basis {|+⟩, |-⟩} are two different bases for the same space:

```
    Z-basis:                    X-basis:

    |0⟩ = [1]    |1⟩ = [0]     |+⟩ = [1/√2]    |-⟩ = [ 1/√2]
          [0]          [1]           [1/√2]           [-1/√2]
```

Every state can be written in either basis:

```
    |0⟩ = (1/√2)|+⟩ + (1/√2)|-⟩      (Z-basis state in X-basis)
    |+⟩ = (1/√2)|0⟩ + (1/√2)|1⟩      (X-basis state in Z-basis)
```

A **linear map** (matrix) transforms vectors. In quantum mechanics, gates are linear maps:

```
    Hadamard gate:  H = (1/√2) [1   1]    maps |0⟩ → |+⟩
                               [1  -1]    maps |1⟩ → |-⟩

    Pauli X gate:   X = [0  1]            maps |0⟩ → |1⟩
                        [1  0]            maps |1⟩ → |0⟩

    Pauli Z gate:   Z = [1   0]           maps |0⟩ → |0⟩
                        [0  -1]           maps |1⟩ → -|1⟩
```

**Geometric meaning:** A matrix is a transformation of space. It stretches, rotates, and/or reflects vectors. On the Bloch sphere, single-qubit gates are rotations:

```
    H = 180° rotation around the axis halfway between X and Z:

         |0⟩ ●──── H ────→ ●|+⟩
              |                |
              |   (rotate      |
              |    around      |
              |    (X+Z)/√2    |
              |    axis)       |
         |1⟩ ●──── H ────→ ●|-⟩
```

### 9.2 Inner Products and Orthogonality

The **inner product** ⟨ψ|φ⟩ is the fundamental operation in quantum mechanics:

```
    ⟨ψ|φ⟩ = α₁*β₁ + α₂*β₂     (conjugate-multiply and sum)

    where |ψ⟩ = [α₁]    |φ⟩ = [β₁]
                [α₂]          [β₂]

    The * means complex conjugate: (a + bi)* = a - bi
```

Examples:

```
    ⟨0|1⟩ = [1 0] · [0] = 1·0 + 0·1 = 0     (orthogonal!)
                      [1]

    ⟨0|+⟩ = [1 0] · [1/√2] = 1/√2            (45° angle)
                      [1/√2]

    ⟨0|0⟩ = [1 0] · [1] = 1                   (parallel — same state)
                      [0]
```

**|⟨ψ|φ⟩|² is the probability** of measuring |φ⟩ when you have |ψ⟩:

```
    P(measure |1⟩ | state is |+⟩) = |⟨1|+⟩|² = |1/√2|² = 1/2    ✓
    P(measure |0⟩ | state is |0⟩) = |⟨0|0⟩|² = |1|² = 1          ✓
    P(measure |1⟩ | state is |0⟩) = |⟨1|0⟩|² = |0|² = 0          ✓
```

**Orthogonality means perfectly distinguishable.** If ⟨ψ|φ⟩ = 0, you can always design a measurement that tells them apart with certainty. If not, there's an irreducible probability of confusing them. This is why the Fubini-Study metric (Section 1) is about |⟨ψ|φ⟩| — distinguishability IS geometry.

### 9.3 Basis Change as Rotation

Changing basis is a rotation of your coordinate system. The physics doesn't change — only your description of it:

```
    State |0⟩ in Z-basis: "definitely 0"
    State |0⟩ in X-basis: "50/50 between + and -"

    Same state, different descriptions.

    Z-basis measurement:                X-basis measurement:
    (asking "up or down?")              (asking "left or right?")

         |0⟩ ● ← definite answer           |0⟩ ● ← uncertain!
              |                                  |
              |                         |+⟩ ●────┼────● |-⟩
              |                                  |
         |1⟩ ●                              |1⟩ ●

    The measurement basis determines what question you ask.
    Different questions → different certainties.
```

**This is why measurement basis matters for your experiment:** Z-basis measurement asks about bit values. States that are "uncertain" in Z-basis (like |+⟩ⁿ — uniform distribution) can't be disturbed by noise in a way Z-measurement would see. You'd need to rotate to X-basis to see the disturbance.

---

## 10. Foundation: Spectral Theory (Eigenvalues and Diagonalisation)

This is the mathematical heart of quantum mechanics. Every observable, every measurement, every stable state is about eigenvalues.

### 10.1 Eigenvalues and Eigenvectors

An **eigenvector** of a matrix A is a vector that only gets scaled (not rotated) when A acts on it:

```
    A|v⟩ = λ|v⟩

    |v⟩ = eigenvector (the direction that survives)
    λ   = eigenvalue (the scale factor)
```

**Physical meaning in QM:**

```
    If A is an observable (like energy H or spin Z):
    - Eigenvectors = states with DEFINITE values of that observable
    - Eigenvalues = the values you'd measure with certainty

    Z = [1   0]     Z|0⟩ = +1·|0⟩    eigenvalue +1 ("spin up")
        [0  -1]     Z|1⟩ = -1·|1⟩    eigenvalue -1 ("spin down")

    X = [0  1]      X|+⟩ = +1·|+⟩    eigenvalue +1 ("spin right")
        [1  0]      X|-⟩ = -1·|-⟩    eigenvalue -1 ("spin left")
```

**The Z operator's eigenvectors are {|0⟩, |1⟩} — the Z-basis.**
**The X operator's eigenvectors are {|+⟩, |-⟩} — the X-basis.**

Every Hermitian operator defines its own basis of eigenvectors. Measuring an observable means projecting onto its eigenbasis.

### 10.2 Diagonalisation: Finding the Natural Basis

A matrix is **diagonal** in its eigenbasis — it just scales each eigenvector:

```
    In Z-basis, Z is already diagonal:     In Z-basis, X is off-diagonal:

    Z = [1   0]  (diagonal — Z-basis      X = [0  1]  (off-diagonal — Z-basis
        [0  -1]   is "natural" for Z)          [1  0]   is NOT natural for X)

    But in X-basis, X becomes diagonal:

    X = [1   0]  (in the {|+⟩, |-⟩} basis)
        [0  -1]
```

**Diagonalisation** means: find the basis where a matrix becomes diagonal. Physically: find the states that have definite values of the observable.

```
    Any Hermitian matrix A can be written:

    A = U D U†

    where D = diagonal matrix of eigenvalues = [λ₁  0   0 ]
                                                [0   λ₂  0 ]
                                                [0   0   λ₃]

    and U = matrix whose columns are the eigenvectors

    This is called the SPECTRAL DECOMPOSITION.
```

### 10.3 Why Eigenvalues Matter for Decoherence

The Lindblad equation (Section 5) drives the density matrix toward states that are **eigenstates of the Lindblad operators**. These are the pointer states — the survivors of decoherence.

```
    Phase damping Lindblad operator: L = Z = [1   0]
                                              [0  -1]

    Eigenstates of Z: |0⟩ (eigenvalue +1) and |1⟩ (eigenvalue -1)

    → Phase damping drives everything toward mixtures of |0⟩ and |1⟩
    → The Z-eigenbasis is the "pointer basis" for phase damping
    → Classical reality (in this noise model) = the Z-basis states
```

For depolarising noise, the Lindblad operators are {X, Y, Z}. These three operators **don't share eigenstates** (X-eigenstates ≠ Z-eigenstates). That's why depolarising noise drives everything toward the maximally mixed state I/2 rather than toward any particular basis — no basis is preferred.

### 10.4 Spectral Decomposition of Density Matrices

A density matrix ρ is Hermitian and positive, so it has a spectral decomposition:

```
    ρ = Σᵢ pᵢ |ψᵢ⟩⟨ψᵢ|

    pᵢ = eigenvalues (probabilities, sum to 1)
    |ψᵢ⟩ = eigenvectors (orthogonal pure states)
```

This tells you: ρ is a probabilistic mixture of its eigenstates with weights pᵢ.

```
    Pure state:     ρ = |ψ⟩⟨ψ|         eigenvalues: {1, 0, 0, ...}
                                        (one eigenvalue = 1, rest = 0)

    Maximally mixed: ρ = I/d            eigenvalues: {1/d, 1/d, ..., 1/d}
                                        (all equal — maximum uncertainty)

    Partially mixed: ρ = 0.7|0⟩⟨0| + 0.3|1⟩⟨1|   eigenvalues: {0.7, 0.3}
                                        (some structure remains)
```

**The von Neumann entropy** measures how mixed a state is:

```
    S(ρ) = -Σᵢ pᵢ log₂(pᵢ)

    Pure state:   S = 0           (zero uncertainty)
    Max mixed:    S = log₂(d)     (maximum uncertainty)
```

### Geometric Example: Eigenvalues on the Bloch Sphere

For a single qubit, the eigenvalues of ρ = (I + r⃗·σ⃗)/2 are:

```
    λ± = (1 ± |r⃗|) / 2

    |r⃗| = 1 (surface):  λ = {1, 0}     → pure state
    |r⃗| = 0 (centre):   λ = {½, ½}     → maximally mixed
    |r⃗| = 0.6 (inside): λ = {0.8, 0.2} → partially mixed
```

```
         ● |r⃗| = 1  →  eigenvalues {1, 0}  →  pure, S = 0
        /
       /  |r⃗| = 0.6  →  eigenvalues {0.8, 0.2}  →  S = 0.72 bits
      /
     ●───── |r⃗| = 0  →  eigenvalues {0.5, 0.5}  →  S = 1 bit

    The Bloch vector LENGTH = how pure the state is
    The Bloch vector DIRECTION = which basis it's closest to
    Eigenvalues encode both pieces of information
```

Decoherence shrinks |r⃗| toward 0, moving eigenvalues toward {½, ½}. The *direction* of r⃗ (which eigenbasis dominates) is determined by the pointer basis — the eigenbasis of the Lindblad operators.

---

## 11. Foundation: Complex Vector Spaces and Projective Geometry

### 11.1 Why Complex Numbers?

Quantum amplitudes are complex: α = a + bi where i² = -1. This isn't a mathematical convenience — it's physically necessary because quantum mechanics requires **interference**.

```
    Real numbers can add constructively:     3 + 5 = 8
    Real numbers can add to zero:            3 + (-3) = 0

    Complex numbers can do both AND can PARTIALLY cancel:

    (1+i) + (1-i) = 2        (imaginary parts cancel)
    (1+i) + (-1-i) = 0       (complete cancellation)
    (1+i) + (i-1) = 2i       (real parts cancel!)

    This partial cancellation IS quantum interference.
```

### 11.2 Interference as Geometry in C²

On the Bloch sphere, the **phase** of a superposition determines where on the equator it sits:

```
    |ψ⟩ = (1/√2)(|0⟩ + e^(iφ)|1⟩)

    φ = 0:    |+⟩ = (|0⟩ + |1⟩)/√2     → positive X axis
    φ = π:    |-⟩ = (|0⟩ - |1⟩)/√2     → negative X axis
    φ = π/2:  |+i⟩ = (|0⟩ + i|1⟩)/√2   → positive Y axis
    φ = -π/2: |-i⟩ = (|0⟩ - i|1⟩)/√2   → negative Y axis
```

```
                |0⟩
                 ●
                /|\
               / | \
              /  |  \
    |-⟩  ●───── ●|+i⟩    All these states give P(0) = P(1) = ½
    φ=π    \  |  /        They ONLY differ in phase φ
            \ | /         Z-measurement can't tell them apart
             \|/          X-measurement CAN (it's sensitive to phase)
              ●
             |1⟩

    The equator = the orbit of phase variation
    Phase = the COMPLEX part of quantum mechanics
    Real QM would only have |+⟩ and |-⟩ (north and south on X-axis)
    Complex QM fills in the whole equator
```

### 11.3 Projective Geometry: Why Global Phase Doesn't Matter

Two vectors that differ by a global phase are the same quantum state:

```
    |ψ⟩ and e^(iθ)|ψ⟩ are physically identical for any θ

    Example:  |0⟩  and  i|0⟩  and  -|0⟩  and  e^(i·0.37)|0⟩
              are ALL the same state.

    This means the state space is NOT C² (a 4D real space).
    It's C² with the phase equivalence modded out:

    CP¹ = C² \ {0} / ~    where |ψ⟩ ~ e^(iθ)|ψ⟩

    For n+1 complex dimensions: CP^n has 2n REAL dimensions.
    For 1 qubit: CP¹ has 2 real dimensions = the Bloch sphere.
    For 2 qubits: CP³ has 6 real dimensions (can't visualise!).
```

### 11.4 Multi-Qubit Projective Space and Entanglement

For n qubits, the Hilbert space is C^(2ⁿ) and the projective space is CP^(2ⁿ - 1):

```
    1 qubit:  CP¹  (2 real dims — the Bloch sphere)
    2 qubits: CP³  (6 real dims)
    3 qubits: CP⁷  (14 real dims)
    6 qubits: CP⁶³ (126 real dims!)
```

**Entanglement is a property of this projective geometry.** A product state |ψ⟩⊗|φ⟩ lives on a special submanifold (the Segre embedding). Entangled states are points OFF this submanifold:

```
    CP³ (2-qubit projective space):

    ┌─────────────────────────────────────────┐
    │                                         │
    │     ● |GHZ⟩ = (|00⟩+|11⟩)/√2          │
    │         (entangled — OFF the product    │
    │          submanifold)                    │
    │                                         │
    │   ╭─────────────────────╮               │
    │   │  Product states      │               │
    │   │  |ψ⟩⊗|φ⟩            │               │
    │   │     ● |00⟩           │               │
    │   │     ● |+0⟩           │               │
    │   │     ● |+⟩⊗|-⟩       │               │
    │   ╰─────────────────────╯               │
    │   (Segre submanifold ≅ CP¹ × CP¹)      │
    │                                         │
    └─────────────────────────────────────────┘

    The DISTANCE from a state to the product submanifold
    is a measure of its entanglement.
    GHZ is maximally far → maximally entangled.
```

This is the deepest version of "structure not substance": entanglement isn't a thing states *have*, it's a geometric property — their *position* relative to the product submanifold in projective space.

### 11.5 The Fubini-Study Metric in Coordinates

In the Z-basis, any 1-qubit state (up to global phase) can be written:

```
    |ψ⟩ = cos(θ/2)|0⟩ + e^(iφ) sin(θ/2)|1⟩

    θ ∈ [0, π]    (polar angle on Bloch sphere — "how much |1⟩?")
    φ ∈ [0, 2π)   (azimuthal angle — "what phase?")
```

The Fubini-Study metric in these coordinates is:

```
    ds²_FS = ¼(dθ² + sin²θ · dφ²)

    This is exactly the metric of a sphere of radius ½!
    (The Bloch sphere has radius 1 in the standard convention,
     but the Fubini-Study distance from pole to pole is π/2, not π.)
```

For n qubits, the Fubini-Study metric on CP^(2ⁿ-1) generalises to:

```
    ds²_FS = ⟨dψ|dψ⟩ - |⟨ψ|dψ⟩|²

    First term: total change in the vector
    Second term: subtract the component along the current state
                 (removes global phase changes)
    Result: only the "physical" change — perpendicular to the ray
```

This is the metric your cosine similarity approximates in the fingerprint space: it measures perpendicular change (direction shift) while ignoring parallel change (magnitude scaling).

---

## 12. Revised Study Path (in order)

### Phase 1: Visual Linear Algebra (1-2 weeks, light)

1. **3Blue1Brown "Essence of Linear Algebra"** — full series (3-4 hours)
   - Vectors as arrows, matrices as transformations, determinants as area scaling
   - Key episodes: "Linear transformations", "Matrix multiplication as composition", "Eigenvectors and eigenvalues"

2. **Exercises with Pauli matrices** — do these by hand on paper:
   - Multiply X·Z and Z·X. Are they equal? (No: XZ = -iY, ZX = +iY. Non-commutativity!)
   - Verify X² = Y² = Z² = I (each Pauli squares to identity)
   - Find eigenvalues/eigenvectors of X, Y, Z (you already know the answers — now derive them)
   - Compute H·Z·H and verify it equals X (basis change by conjugation)

### Phase 2: Spectral Theory Applied to QM (2-3 weeks)

3. **Diagonalisation practice:**
   - Diagonalise X = UDU† by finding U (the matrix of eigenvectors)
   - Verify: U = (1/√2)[[1,1],[1,-1]] = H, D = [[1,0],[0,-1]] = Z, so X = HZH†
   - Physical meaning: X in its own basis looks like Z. Measuring X = rotate to X-basis, then measure Z.

4. **Density matrix exercises:**
   - Compute ρ = |+⟩⟨+| as a 2×2 matrix. Verify Tr(ρ) = 1, ρ² = ρ (pure state).
   - Compute ρ_mixed = ½|0⟩⟨0| + ½|1⟩⟨1| = I/2. Verify ρ² ≠ ρ (mixed!), Tr(ρ²) = ½.
   - Compute the Bloch vector for each: |r⃗| = 1 for pure, |r⃗| = 0 for mixed.
   - Find eigenvalues of both ρ matrices. Verify they match the formula λ± = (1±|r⃗|)/2.

5. **Spectral decomposition of noise:**
   - Apply the depolarising channel to ρ = |0⟩⟨0| = [[1,0],[0,0]] with p=0.1
   - E(ρ) = 0.9·ρ + (0.1/3)(XρX + YρY + ZρZ)
   - Work it out: XρX = [[0,0],[0,1]], ZρZ = [[1,0],[0,0]], YρY = [[0,0],[0,1]]
   - Result: E(ρ) = [[0.933, 0], [0, 0.067]]. The Bloch vector shrunk from [0,0,1] to [0,0,0.867].

### Phase 3: Tensor Products and Entanglement (2-3 weeks)

6. **Tensor products:**
   - Compute |0⟩⊗|0⟩ = [1,0,0,0]ᵀ (a 4-element vector for 2 qubits)
   - Compute |+⟩⊗|0⟩ = [1/√2, 0, 1/√2, 0]ᵀ
   - Compute |Bell⟩ = (|00⟩+|11⟩)/√2 = [1/√2, 0, 0, 1/√2]ᵀ
   - Try to factor |Bell⟩ as |a⟩⊗|b⟩. You can't — that's entanglement.

7. **Partial trace** — the operation that creates mixed states from entangled pure states:
   - For |Bell⟩ = (|00⟩+|11⟩)/√2, compute ρ_AB = |Bell⟩⟨Bell| (a 4×4 matrix)
   - Trace out qubit B: ρ_A = Tr_B(ρ_AB) = ½|0⟩⟨0| + ½|1⟩⟨1| = I/2
   - Qubit A alone is maximally mixed, even though the joint state is pure!

### Phase 4: Channels and Geometry (when ready)

8. **Kraus operators in multi-qubit systems:**
   - Apply X₀⊗I₁ to |Bell⟩. What happens?
   - Apply Z₀⊗Z₁ to |GHZ₃⟩. Why is GHZ fragile to correlated Z-errors?

9. **Connect to your experiment:**
   - Re-derive why ΔCov mirrors the noise adjacency using the Kraus/Lindblad formalism
   - Prove the Pauli invariance theorem using density matrix algebra (not just the counting argument)
   - Show that the fingerprint direction m_topology is the off-diagonal structure of Σ_edges (L_corr ρ L_corr† - independent contribution)

### Resources

| Resource | Covers | Time | Style |
|----------|--------|------|-------|
| 3Blue1Brown "Essence of Linear Algebra" | Vectors, transforms, eigenvalues | 3-4 hrs | Visual, exactly your style |
| 3Blue1Brown "Quantum Mechanics" series (if available) | Spin, measurement, complex amplitudes | 2-3 hrs | Visual |
| Hidary "Quantum Computing: An Applied Approach" Ch 1-4 | Linear algebra for QC, density matrices | 1-2 weeks | Code-heavy, practical |
| Nielsen & Chuang Ch 2 (just Ch 2!) | Postulates of QM, density matrices, spectral theorem | 1 week | Dense but definitive |
| Preskill lecture notes Ch 3 | Open systems, channels, Kraus, Lindblad | 1-2 weeks | Free online, excellent |
