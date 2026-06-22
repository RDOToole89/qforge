import type { GlossaryCategory, GlossaryTerm } from "../types";
import { viz } from "@/src/design/tokens";

export const category: GlossaryCategory = {
  id: "density_matrices",
  name: "Density Matrices & Mixed States",
  icon: "th",
  color: viz.gate.teal,
  description: "The density operator formalism for open quantum systems",
};

export const terms: GlossaryTerm[] = [
  {
    id: "density_matrix",
    name: "Density Matrix",
    formalDefinition:
      "A positive semi-definite, Hermitian operator ρ with Tr(ρ) = 1 that completely describes a quantum state (pure or mixed). For a pure state: ρ = |ψ⟩⟨ψ|. For a mixture: ρ = Σᵢ pᵢ|ψᵢ⟩⟨ψᵢ|. Also called the density operator or state operator.",
    intuitiveExplanation:
      "A matrix that encodes everything about a quantum state, including classical uncertainty. State vectors can only describe pure states; density matrices handle mixtures too. Essential for describing noisy, real-world quantum systems.",
    symbol: "ρ",
    keyEquation:
      "\\rho = \\sum_i p_i |\\psi_i\\rangle\\langle\\psi_i|, \\quad \\text{Tr}(\\rho) = 1, \\quad \\rho \\geq 0",
    formulaExplanation:
      "The density matrix is a weighted mixture of pure state projectors. The weights p\u1d62 are classical probabilities summing to 1. The trace-1 condition ensures total probability is conserved, and positive semi-definiteness ensures no negative probabilities.",
    relatedTerms: ["pure_state", "mixed_state", "partial_trace", "purity"],
    categoryId: "density_matrices",
  },
  {
    id: "trace",
    name: "Trace",
    formalDefinition:
      "The sum of diagonal elements of a matrix: Tr(A) = Σᵢ Aᵢᵢ. For density matrices, Tr(ρ) = 1 (normalization). The trace is cyclic: Tr(ABC) = Tr(CAB). Expectation values are computed as ⟨O⟩ = Tr(ρO).",
    intuitiveExplanation:
      "A single number summarizing a matrix. In quantum mechanics, the trace of the density matrix must always equal 1 (total probability = 100%). The trace lets you compute expectation values without explicit state vectors.",
    symbol: "Tr(·)",
    keyEquation:
      "\\text{Tr}(A) = \\sum_i A_{ii}, \\quad \\langle O \\rangle = \\text{Tr}(\\rho \\, O)",
    formulaExplanation:
      "The trace sums the diagonal entries of a matrix. In quantum mechanics, the expected value of any observable O is simply Tr(\u03c1O) \u2014 this single formula replaces the need for explicit state vectors when computing measurements.",
    relatedTerms: ["density_matrix", "partial_trace", "trace_preserving"],
    categoryId: "density_matrices",
  },
  {
    id: "partial_trace",
    name: "Partial Trace",
    formalDefinition:
      "An operation that reduces a composite system's density matrix to a subsystem's density matrix: ρ_A = Tr_B(ρ_AB) = Σᵢ (I_A ⊗ ⟨i|_B) ρ_AB (I_A ⊗ |i⟩_B). The quantum analogue of marginalizing a joint probability distribution.",
    intuitiveExplanation:
      "Mathematically 'forgetting' about some qubits to focus on the rest. If you have two entangled qubits and trace out qubit B, you get the reduced state of qubit A — which is typically mixed even if the joint state was pure.",
    symbol: "Tr_B(·)",
    keyEquation:
      "\\rho_A = \\text{Tr}_B(\\rho_{AB}) = \\sum_i (I_A \\otimes \\langle i|_B)\\, \\rho_{AB}\\, (I_A \\otimes |i\\rangle_B)",
    formulaExplanation:
      "To get the state of subsystem A, sum over all basis states of subsystem B. This 'traces out' B, leaving only A's perspective. If A and B were entangled, \u03c1_A will be mixed even if \u03c1_AB was pure.",
    relatedTerms: ["density_matrix", "entanglement_entropy", "reduced_state"],
    categoryId: "density_matrices",
  },
  {
    id: "purity",
    name: "Purity",
    formalDefinition:
      "A measure of how pure a quantum state is: γ = Tr(ρ²). Ranges from 1/d (maximally mixed, d = dimension) to 1 (pure state). Purity decreases under decoherence and is invariant under unitary evolution.",
    intuitiveExplanation:
      "How 'clean' a quantum state is. Purity = 1 means a perfect pure state (on the Bloch sphere surface). Purity = 1/2 for a single qubit means maximally mixed (center of the Bloch ball). Noise always decreases purity.",
    symbol: "γ = Tr(ρ²)",
    keyEquation:
      "\\gamma = \\text{Tr}(\\rho^2), \\quad \\frac{1}{d} \\leq \\gamma \\leq 1",
    formulaExplanation:
      "Purity measures how close a state is to being pure. The trace of \u03c1\u00b2 equals 1 for a pure state and 1/d for the maximally mixed state in d dimensions. Decoherence drives purity down; unitary evolution preserves it.",
    relatedTerms: ["pure_state", "mixed_state", "density_matrix", "decoherence"],
    categoryId: "density_matrices",
  },
  {
    id: "reduced_state",
    name: "Reduced State",
    formalDefinition:
      "The density matrix of a subsystem obtained by partial tracing over the complementary subsystem: ρ_A = Tr_B(ρ_AB). The reduced state of a maximally entangled state is maximally mixed (ρ_A = I/d).",
    intuitiveExplanation:
      "What one qubit 'looks like' when you ignore its partners. For a GHZ or Bell state, each individual qubit appears maximally mixed — all the information is in the correlations, not the individual qubits.",
    symbol: "ρ_A",
    relatedTerms: ["partial_trace", "density_matrix", "entanglement"],
    categoryId: "density_matrices",
  },
  {
    id: "trace_preserving",
    name: "Trace-Preserving",
    formalDefinition:
      "A quantum channel ε is trace-preserving if Tr(ε(ρ)) = Tr(ρ) = 1 for all ρ. Combined with complete positivity, this gives the CPTP (Completely Positive, Trace-Preserving) condition — the fundamental requirement for a physically valid quantum operation.",
    intuitiveExplanation:
      "Probability is conserved — the total probability stays at 100% after any physical operation. You can lose coherence, lose entanglement, but you can't lose probability. This is why the first row of a PTM is always [1, 0, 0, 0].",
    relatedTerms: ["cptp_map", "ptm", "kraus_operators"],
    categoryId: "density_matrices",
  },
  {
    id: "separable_state",
    name: "Separable State",
    formalDefinition:
      "A multi-partite state ρ that can be written as a convex combination of product states: ρ = Σᵢ pᵢ ρ_A^(i) ⊗ ρ_B^(i). A state that is not separable is entangled. Determining separability is NP-hard in general.",
    intuitiveExplanation:
      "A state that can be prepared using only local operations and classical communication (LOCC) — no quantum entanglement needed. Classically correlated but not quantumly correlated.",
    keyEquation:
      "\\rho_{\\text{sep}} = \\sum_i p_i \\, \\rho_A^{(i)} \\otimes \\rho_B^{(i)}",
    formulaExplanation:
      "A separable state is a classical mixture of product states \u2014 each term is an uncorrelated state of A and B weighted by classical probability p\u1d62. If a state can't be written this way, it must be entangled.",
    relatedTerms: ["entanglement", "product_state", "density_matrix"],
    categoryId: "density_matrices",
  },
];
