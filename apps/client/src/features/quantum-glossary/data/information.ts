import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "information",
  name: "Quantum Information Theory",
  icon: "info-circle",
  color: "#3b82f6",
  description: "Entropy, information measures, and distance metrics",
};

export const terms: GlossaryTerm[] = [
  {
    id: "von_neumann_entropy",
    name: "Von Neumann Entropy",
    formalDefinition:
      "The quantum generalization of Shannon entropy: S(ρ) = −Tr(ρ log₂ ρ) = −Σᵢ λᵢ log₂ λᵢ where λᵢ are eigenvalues of ρ. Ranges from 0 (pure state) to log₂ d (maximally mixed state in d dimensions).",
    intuitiveExplanation:
      "Measures the 'quantum uncertainty' in a state. A pure state has zero entropy (you know exactly what state it is). A maximally mixed qubit has entropy 1 bit. When used on a reduced state, it quantifies entanglement.",
    symbol: "S(ρ)",
    relatedTerms: ["density_matrix", "entanglement_entropy", "mutual_information", "purity"],
    categoryId: "information",
  },
  {
    id: "mutual_information",
    name: "Quantum Mutual Information",
    formalDefinition:
      "A measure of total correlations (classical + quantum) between subsystems A and B: I(A:B) = S(ρ_A) + S(ρ_B) − S(ρ_AB). Non-negative and zero iff ρ_AB = ρ_A ⊗ ρ_B (product state).",
    intuitiveExplanation:
      "How much knowing about subsystem A tells you about subsystem B — and vice versa. Captures both classical and quantum correlations. For a Bell state, I(A:B) = 2 bits — the maximum for two qubits.",
    symbol: "I(A:B)",
    relatedTerms: ["von_neumann_entropy", "total_correlation", "entanglement"],
    categoryId: "information",
  },
  {
    id: "total_correlation",
    name: "Total Correlation",
    formalDefinition:
      "Multi-partite generalization of mutual information: TC = Σᵢ S(ρᵢ) − S(ρ). Measures the total amount of correlation across all subsystems. Also called multi-information. One of the 8 structured decoherence metrics in the framework.",
    intuitiveExplanation:
      "How much total 'connectedness' exists among all qubits simultaneously. Higher TC means more structure in the distribution. In the framework, TC helps distinguish structured decoherence from random noise.",
    symbol: "TC",
    relatedTerms: ["mutual_information", "von_neumann_entropy", "structure_score"],
    categoryId: "information",
  },
  {
    id: "fidelity",
    name: "Fidelity",
    formalDefinition:
      "A measure of closeness between quantum states: F(ρ, σ) = (Tr√(√ρ σ √ρ))². For pure states: F(|ψ⟩, |φ⟩) = |⟨ψ|φ⟩|². Ranges from 0 (orthogonal) to 1 (identical). Related to Bures distance.",
    intuitiveExplanation:
      "How 'similar' two quantum states are — a quantum version of overlap. Fidelity = 1 means identical states; fidelity = 0 means completely distinguishable. Used to assess how well a noisy experiment reproduces the ideal state.",
    symbol: "F(ρ, σ)",
    relatedTerms: ["trace_distance", "density_matrix"],
    categoryId: "information",
  },
  {
    id: "trace_distance",
    name: "Trace Distance",
    formalDefinition:
      "A metric on quantum states: D(ρ, σ) = ½Tr|ρ − σ| = ½Σᵢ|λᵢ| where λᵢ are eigenvalues of (ρ − σ). Equals the maximum probability of distinguishing ρ from σ with a single measurement. Satisfies 0 ≤ D ≤ 1.",
    intuitiveExplanation:
      "The maximum probability of telling two quantum states apart in a single experiment. Trace distance = 0 means the states are identical; = 1 means perfectly distinguishable. CPTP maps can only decrease trace distance (contractivity).",
    symbol: "D(ρ, σ)",
    relatedTerms: ["fidelity", "contractivity", "cptp_map"],
    categoryId: "information",
  },
  {
    id: "shannon_entropy",
    name: "Shannon Entropy",
    formalDefinition:
      "The classical information entropy: H(X) = −Σᵢ pᵢ log₂ pᵢ where pᵢ are probabilities of outcomes. Measures the average 'surprise' of a random variable. The quantum generalization is von Neumann entropy.",
    intuitiveExplanation:
      "How much uncertainty is in a probability distribution. A fair coin has H = 1 bit (maximum surprise). A loaded coin has H < 1 bit. Used in the framework's metrics for analyzing measurement outcome distributions.",
    symbol: "H(X)",
    relatedTerms: ["von_neumann_entropy", "born_rule"],
    categoryId: "information",
  },
  {
    id: "jensen_shannon_divergence",
    name: "Jensen-Shannon Divergence",
    formalDefinition:
      "A symmetrized, bounded divergence measure: JSD(P||Q) = ½KL(P||M) + ½KL(Q||M) where M = ½(P+Q) and KL is the Kullback-Leibler divergence. Ranges from 0 (identical) to 1 (fully distinguishable) when using log₂.",
    intuitiveExplanation:
      "A smooth way to measure how different two probability distributions are. Unlike KL divergence, it's symmetric and always finite. The framework uses JSD as the basis for the Structure Score metric.",
    symbol: "JSD(P||Q)",
    relatedTerms: ["structure_score", "shannon_entropy"],
    categoryId: "information",
  },
];
