import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "entanglement",
  name: "Entanglement & Correlations",
  icon: "link",
  color: "#ec4899",
  description: "Quantum correlations beyond classical physics",
};

export const terms: GlossaryTerm[] = [
  {
    id: "entanglement",
    name: "Quantum Entanglement",
    formalDefinition:
      "A quantum state of multiple particles that cannot be factored into a product of individual particle states. Formally, |ψ⟩_AB ≠ |ψ⟩_A ⊗ |ψ⟩_B. Entangled states exhibit correlations that exceed any classical limit (Bell inequality violation).",
    intuitiveExplanation:
      "Two or more qubits are 'linked' so that measuring one instantly constrains what you'll find when measuring the other — regardless of distance. Not communication, but correlation stronger than anything classical physics allows.",
    relatedTerms: ["bell_states", "epr_pair", "separable_state", "bell_inequality"],
    categoryId: "entanglement",
  },
  {
    id: "epr_pair",
    name: "EPR Pair",
    formalDefinition:
      "A maximally entangled pair of qubits, named after Einstein, Podolsky, and Rosen. Typically refers to the Bell state |Φ+⟩ = (|00⟩+|11⟩)/√2. The EPR paradox argued this implied quantum mechanics was incomplete; Bell's theorem later proved the correlations are genuinely non-classical.",
    intuitiveExplanation:
      "The state Einstein called 'spooky action at a distance'. Two qubits perfectly correlated: both always give the same answer when measured in the same basis, no matter how far apart they are.",
    symbol: "|Φ+⟩",
    relatedTerms: ["bell_states", "entanglement", "bell_inequality"],
    categoryId: "entanglement",
  },
  {
    id: "bell_inequality",
    name: "Bell Inequality",
    formalDefinition:
      "A mathematical inequality that any local hidden variable theory must satisfy. The most common form is the CHSH inequality: |⟨AB⟩ + ⟨AB'⟩ + ⟨A'B⟩ − ⟨A'B'⟩| ≤ 2. Quantum mechanics predicts violations up to 2√2 ≈ 2.828.",
    intuitiveExplanation:
      "A mathematical test that proves entanglement is real and not just hidden classical correlations. Quantum experiments violate this inequality, proving nature is fundamentally non-classical. This closed the debate Einstein started with EPR.",
    symbol: "S ≤ 2",
    relatedTerms: ["entanglement", "epr_pair", "chsh"],
    categoryId: "entanglement",
  },
  {
    id: "chsh",
    name: "CHSH Inequality",
    formalDefinition:
      "The Clauser-Horne-Shimony-Holt inequality: S = |E(a,b) − E(a,b') + E(a',b) + E(a',b')| ≤ 2 for local hidden variable theories. Quantum mechanics achieves S_max = 2√2 with a Bell state and optimal measurement settings.",
    intuitiveExplanation:
      "A specific, experimentally testable version of Bell's inequality. Pick four measurement directions, compute the CHSH value S. If S > 2, you've proven entanglement is present. The maximum quantum value 2√2 is called Tsirelson's bound.",
    symbol: "S ≤ 2√2",
    relatedTerms: ["bell_inequality", "bell_states", "entanglement"],
    categoryId: "entanglement",
  },
  {
    id: "concurrence",
    name: "Concurrence",
    formalDefinition:
      "An entanglement measure for two-qubit states: C(ρ) = max(0, λ₁−λ₂−λ₃−λ₄) where λᵢ are the square roots of eigenvalues of ρ(σᵧ⊗σᵧ)ρ*(σᵧ⊗σᵧ) in decreasing order. C = 0 for separable states, C = 1 for maximally entangled states.",
    intuitiveExplanation:
      "A single number from 0 to 1 that measures 'how entangled' two qubits are. Zero means no entanglement (product state), one means maximally entangled (Bell state). Useful for quantifying how much noise has degraded entanglement.",
    symbol: "C(ρ)",
    relatedTerms: ["entanglement", "entanglement_entropy", "bell_states"],
    categoryId: "entanglement",
  },
  {
    id: "entanglement_entropy",
    name: "Entanglement Entropy",
    formalDefinition:
      "The von Neumann entropy of the reduced density matrix: S(ρ_A) = −Tr(ρ_A log₂ ρ_A) where ρ_A = Tr_B(ρ_AB). For a pure bipartite state, this quantifies entanglement. Maximum value log₂(d) for a d-dimensional subsystem.",
    intuitiveExplanation:
      "How much entanglement is in a bipartite state, measured as the 'surprise' in one half when you trace out the other. A Bell state has 1 ebit (maximum for two qubits). A product state has 0.",
    symbol: "S(ρ_A)",
    relatedTerms: ["von_neumann_entropy", "partial_trace", "entanglement"],
    categoryId: "entanglement",
  },
  {
    id: "zz_correlator",
    name: "ZZ Correlator",
    formalDefinition:
      "The expectation value ⟨Z_i Z_j⟩ measuring the correlation between Z-basis measurements on qubits i and j. For a GHZ state, ⟨ZZ⟩ = 1 (perfect correlation). For a product state, ⟨ZZ⟩ = ⟨Z⟩_i⟨Z⟩_j (no excess correlation).",
    intuitiveExplanation:
      "Measures whether two qubits 'agree' in Z-basis measurements. ⟨ZZ⟩ = 1 means they always agree; ⟨ZZ⟩ = −1 means they always disagree; ⟨ZZ⟩ = 0 means no correlation. This is the key quantity that makes GHZ a good noise probe — noise disrupts the ZZ correlation.",
    symbol: "⟨ZZ⟩",
    relatedTerms: ["ghz_state", "correlators", "pauli_z"],
    categoryId: "entanglement",
  },
];
