import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "noise",
  name: "Quantum Channels & Noise",
  icon: "bolt",
  color: "#f97316",
  description: "CPTP maps, Kraus operators, and noise models",
};

export const terms: GlossaryTerm[] = [
  {
    id: "cptp_map",
    name: "CPTP Map",
    formalDefinition:
      "A Completely Positive, Trace-Preserving linear map ε: ρ → ε(ρ). Any physically realizable quantum operation (including noise) is a CPTP map. Equivalent representations: Kraus operators, Stinespring dilation, Choi matrix.",
    intuitiveExplanation:
      "The most general kind of 'thing that can happen' to a quantum state. Every noise process, every measurement, every gate — they're all CPTP maps. The two constraints are: keep probabilities positive (CP) and keep total probability at 100% (TP).",
    symbol: "ε(ρ)",
    relatedTerms: ["kraus_operators", "ptm", "contractivity", "trace_preserving"],
    categoryId: "noise",
  },
  {
    id: "kraus_operators",
    name: "Kraus Operators",
    formalDefinition:
      "A set of matrices {K₁, K₂, ..., Kₙ} satisfying Σᵢ Kᵢ†Kᵢ = I that define a CPTP map via ε(ρ) = Σᵢ Kᵢ ρ Kᵢ†. Also called operation elements. The Kraus decomposition is not unique.",
    intuitiveExplanation:
      "The 'building blocks' of a noise channel. Each Kraus operator represents one possible thing that can happen to the qubit. For depolarizing noise: K₀ = √(1−3p/4)·I (nothing happens), K₁ = √(p/4)·X (bit flip), K₂ = √(p/4)·Y (both flip), K₃ = √(p/4)·Z (phase flip).",
    symbol: "{Kᵢ}",
    relatedTerms: ["cptp_map", "depolarizing_channel", "amplitude_damping"],
    categoryId: "noise",
  },
  {
    id: "depolarizing_channel",
    name: "Depolarizing Channel",
    formalDefinition:
      "A noise channel that replaces the state with the maximally mixed state with probability p: ε(ρ) = (1−p)ρ + p·I/2. On the Bloch sphere, it uniformly contracts: r → (1−p)r. All three Bloch components shrink equally.",
    intuitiveExplanation:
      "The 'fog machine' of quantum noise — it shrinks the Bloch sphere uniformly in all directions. At p=0 nothing happens; at p=1 everything becomes maximally mixed. In the visualizer, watch the sphere shrink to a point as you increase p.",
    symbol: "ε_dep(ρ)",
    relatedTerms: ["cptp_map", "bloch_sphere", "kraus_operators", "dephasing"],
    categoryId: "noise",
  },
  {
    id: "amplitude_damping",
    name: "Amplitude Damping",
    formalDefinition:
      "A noise channel modeling energy relaxation (T₁ decay): K₀ = [[1,0],[0,√(1−γ)]], K₁ = [[0,√γ],[0,0]]. The Bloch sphere deforms into an ellipsoid shifted toward |0⟩. Drives any state toward the ground state.",
    intuitiveExplanation:
      "The qubit loses energy and relaxes toward |0⟩ — like a ball rolling downhill. On the Bloch sphere, the sphere squishes and drifts toward the north pole. Unlike depolarizing noise, this is asymmetric — it has a preferred direction.",
    symbol: "ε_AD(ρ)",
    relatedTerms: ["t1_time", "kraus_operators", "cptp_map"],
    categoryId: "noise",
  },
  {
    id: "dephasing",
    name: "Dephasing (Phase Damping)",
    formalDefinition:
      "A noise channel that destroys off-diagonal coherence without affecting populations: ε(ρ) has ρ₀₁ → (1−p)ρ₀₁ while ρ₀₀, ρ₁₁ unchanged. On the Bloch sphere: rₓ → (1−p)rₓ, rᵧ → (1−p)rᵧ, r_z → r_z. Models T₂ decoherence.",
    intuitiveExplanation:
      "The Z-component survives but X and Y shrink — the sphere collapses into a 'pancake' aligned with the Z-axis. This is why Z-basis measurements see nothing when dephasing acts on Z-symmetric states (Pauli invariance).",
    symbol: "ε_deph(ρ)",
    relatedTerms: ["t2_time", "pauli_z", "pauli_invariance", "phase_flip"],
    categoryId: "noise",
  },
  {
    id: "bit_flip",
    name: "Bit Flip Channel",
    formalDefinition:
      "A noise channel that flips |0⟩↔|1⟩ with probability p: ε(ρ) = (1−p)ρ + pXρX. Kraus operators: K₀ = √(1−p)·I, K₁ = √p·X. On the Bloch sphere: rₓ preserved, rᵧ → (1−2p)rᵧ, r_z → (1−2p)r_z.",
    intuitiveExplanation:
      "Random NOT errors — the qubit flips between 0 and 1 with some probability. X-eigenstates (|+⟩, |−⟩) are immune because X doesn't change them. The Bloch sphere squishes along Y and Z, preserving X — a 'pancake' aligned with the X-axis.",
    symbol: "ε_BF(ρ)",
    relatedTerms: ["pauli_x", "phase_flip", "kraus_operators", "einselection"],
    categoryId: "noise",
  },
  {
    id: "phase_flip",
    name: "Phase Flip Channel",
    formalDefinition:
      "A noise channel that applies a Z gate with probability p: ε(ρ) = (1−p)ρ + pZρZ. Kraus operators: K₀ = √(1−p)·I, K₁ = √p·Z. On the Bloch sphere: r_z preserved, rₓ → (1−2p)rₓ, rᵧ → (1−2p)rᵧ.",
    intuitiveExplanation:
      "Random phase errors — the relative sign between |0⟩ and |1⟩ gets scrambled. Z-eigenstates are immune. Same geometry as dephasing. In Z-basis measurements, phase flips are invisible — this is the root of the Pauli invariance theorem.",
    symbol: "ε_PF(ρ)",
    relatedTerms: ["pauli_z", "dephasing", "bit_flip", "pauli_invariance"],
    categoryId: "noise",
  },
  {
    id: "pauli_channel",
    name: "Pauli Channel",
    formalDefinition:
      "A noise channel that applies random Pauli errors: ε(ρ) = (1−pₓ−pᵧ−p_z)ρ + pₓXρX + pᵧYρY + p_zZρZ. Encompasses depolarizing (pₓ=pᵧ=p_z=p/3), bit flip (pᵧ=p_z=0), and phase flip (pₓ=pᵧ=0) as special cases.",
    intuitiveExplanation:
      "The general 'random Pauli error' channel — each type of error (X, Y, Z) happens with its own probability. Most common noise models are special cases. On the Bloch sphere, it creates an ellipsoid whose axes depend on the error probabilities.",
    relatedTerms: ["depolarizing_channel", "bit_flip", "phase_flip", "kraus_operators"],
    categoryId: "noise",
  },
];
