import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "decoherence",
  name: "Decoherence & Open Systems",
  icon: "water",
  color: "#ef4444",
  description: "How quantum systems lose coherence through environmental interaction",
};

export const terms: GlossaryTerm[] = [
  {
    id: "decoherence",
    name: "Decoherence",
    formalDefinition:
      "The process by which a quantum system loses coherence (off-diagonal elements of the density matrix) through interaction with its environment. Transforms pure superpositions into classical-looking mixtures. The primary obstacle to quantum computation.",
    intuitiveExplanation:
      "Quantum information 'leaking' into the environment. The qubit doesn't disappear — it just becomes entangled with everything around it, making it look classical from the inside. This is what our framework studies: does decoherence follow structured pathways or happen randomly?",
    relatedTerms: ["dephasing", "t1_time", "t2_time", "einselection", "structured_decoherence"],
    categoryId: "decoherence",
  },
  {
    id: "t1_time",
    name: "T₁ Time (Relaxation)",
    formalDefinition:
      "The characteristic time for a qubit to relax from |1⟩ to |0⟩ through energy exchange with the environment. Governs amplitude damping: P(1→0) ∝ 1 − e^(−t/T₁). Also called the longitudinal relaxation time.",
    intuitiveExplanation:
      "How long before an excited qubit loses its energy and drops to |0⟩. Longer T₁ = better qubit. Modern superconducting qubits have T₁ ~ 100μs. On the Bloch sphere, T₁ decay drives the state toward the north pole.",
    symbol: "T₁",
    relatedTerms: ["amplitude_damping", "t2_time", "decoherence"],
    categoryId: "decoherence",
  },
  {
    id: "t2_time",
    name: "T₂ Time (Dephasing)",
    formalDefinition:
      "The characteristic time for loss of phase coherence: off-diagonal density matrix elements decay as e^(−t/T₂). Always satisfies T₂ ≤ 2T₁. Combines energy relaxation and pure dephasing: 1/T₂ = 1/(2T₁) + 1/T_φ.",
    intuitiveExplanation:
      "How long before the qubit's phase information scrambles. Even if the qubit stays excited (T₁ is long), the relative phase between |0⟩ and |1⟩ can randomize. On the Bloch sphere, T₂ collapses the equatorial components.",
    symbol: "T₂",
    relatedTerms: ["dephasing", "t1_time", "decoherence"],
    categoryId: "decoherence",
  },
  {
    id: "lindblad_equation",
    name: "Lindblad Master Equation",
    formalDefinition:
      "The most general Markovian master equation: dρ/dt = −i[H,ρ] + Σₖ γₖ(LₖρLₖ† − ½{Lₖ†Lₖ, ρ}). The first term is unitary evolution; the sum describes dissipative processes through Lindblad (jump) operators Lₖ with rates γₖ.",
    intuitiveExplanation:
      "The equation governing how an open quantum system evolves in time. The Hamiltonian part rotates the state; the Lindblad operators describe the noise. Different choices of Lₖ give different noise channels (L=σ₋ for amplitude damping, L=σ_z for dephasing).",
    symbol: "dρ/dt = L(ρ)",
    relatedTerms: ["decoherence", "cptp_map", "amplitude_damping", "dephasing"],
    categoryId: "decoherence",
  },
  {
    id: "einselection",
    name: "Einselection",
    formalDefinition:
      "Environment-induced superselection: the process by which the environment selects a preferred basis (pointer basis) of the system. States in the pointer basis are robust against decoherence; superpositions of pointer states decohere rapidly.",
    intuitiveExplanation:
      "Why we don't see quantum superpositions in everyday life. The environment 'watches' the system in a specific basis, effectively measuring it continuously. The states that survive this scrutiny become the classical states we observe.",
    relatedTerms: ["pointer_states", "decoherence", "measurement_basis"],
    categoryId: "decoherence",
  },
  {
    id: "pointer_states",
    name: "Pointer States",
    formalDefinition:
      "The eigenstates of the system-environment interaction Hamiltonian that are most robust against decoherence. They form the environmentally selected (einselected) basis. For bit flip noise, the pointer states are X-eigenstates {|+⟩, |−⟩}.",
    intuitiveExplanation:
      "The 'survivors' of decoherence — quantum states that the environment doesn't destroy. For bit-flip noise, |+⟩ and |−⟩ are pointer states because X flips don't affect them. In the Bloch sphere visualizer, the preserved axis reveals the pointer states.",
    relatedTerms: ["einselection", "decoherence", "bit_flip"],
    categoryId: "decoherence",
  },
  {
    id: "quantum_zeno_effect",
    name: "Quantum Zeno Effect",
    formalDefinition:
      "The suppression of quantum evolution by frequent measurement. For a system evolving under Hamiltonian H, the survival probability after N measurements in time t approaches 1 as N → ∞: P_survive → 1 − (t/N)² × const.",
    intuitiveExplanation:
      "A watched pot never boils — quantum version. Measuring a quantum system frequently enough prevents it from evolving away from its initial state. Each measurement 'resets' the system, and the evolution between measurements becomes negligibly small.",
    relatedTerms: ["measurement", "decoherence"],
    categoryId: "decoherence",
  },
];
