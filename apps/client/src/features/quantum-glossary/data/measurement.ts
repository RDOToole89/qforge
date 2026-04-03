import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "measurement",
  name: "Measurement Theory",
  icon: "crosshairs",
  color: "#06b6d4",
  description: "Quantum measurement formalisms and their physical implications",
};

export const terms: GlossaryTerm[] = [
  {
    id: "projective_measurement",
    name: "Projective Measurement",
    formalDefinition:
      "A measurement described by a set of orthogonal projectors {Πₘ} with Σₘ Πₘ = I and Πₘ² = Πₘ. Outcome m occurs with probability P(m) = Tr(Πₘρ) and the post-measurement state is ΠₘρΠₘ/P(m). Also called von Neumann measurement.",
    intuitiveExplanation:
      "The standard textbook measurement. You project the state onto one of a set of orthogonal directions. After measurement, the state is in the projected direction. Repeated measurement always gives the same result — the state has 'collapsed'.",
    symbol: "{Πₘ}",
    keyEquation:
      "P(m) = \\text{Tr}(\\Pi_m \\rho), \\quad \\rho \\to \\frac{\\Pi_m \\rho \\Pi_m}{P(m)}",
    formulaExplanation:
      "The probability of outcome m is the trace of the projector times the state. After measurement, the state collapses to the projected subspace, normalized by the outcome probability. This is the standard 'textbook collapse' postulate.",
    relatedTerms: ["measurement", "born_rule", "povm", "observable"],
    categoryId: "measurement",
  },
  {
    id: "povm",
    name: "POVM",
    formalDefinition:
      "Positive Operator-Valued Measure: a set of positive semi-definite operators {Eₘ} with Σₘ Eₘ = I. More general than projective measurement — elements need not be orthogonal or projectors. Probability of outcome m is P(m) = Tr(Eₘρ).",
    intuitiveExplanation:
      "The most general measurement allowed by quantum mechanics. Unlike projective measurements, POVMs can have more outcomes than the dimension of the system and don't require orthogonal projectors. Useful for optimizing state discrimination.",
    symbol: "{Eₘ}",
    keyEquation:
      "P(m) = \\text{Tr}(E_m \\rho), \\quad \\sum_m E_m = I, \\quad E_m \\geq 0",
    formulaExplanation:
      "POVM elements Eₘ are positive operators that sum to the identity. They give measurement probabilities without specifying the post-measurement state. More outcomes than dimensions are possible — useful for optimal state discrimination.",
    relatedTerms: ["projective_measurement", "measurement", "born_rule"],
    categoryId: "measurement",
  },
  {
    id: "observable",
    name: "Observable",
    formalDefinition:
      "A Hermitian operator O = O† whose eigenvalues are the possible measurement outcomes and whose eigenstates are the post-measurement states. The expectation value is ⟨O⟩ = Tr(ρO). The Pauli operators {X, Y, Z} are the fundamental single-qubit observables.",
    intuitiveExplanation:
      "A physical quantity you can measure — like position, spin, or energy. In quantum mechanics, each observable is a matrix, and measurement 'picks' one of its eigenvalues. The Pauli matrices X, Y, Z are the three directions you can measure a qubit along.",
    symbol: "O",
    keyEquation:
      "\\langle O \\rangle = \\text{Tr}(\\rho \\, O) = \\sum_i \\lambda_i \\, P(\\lambda_i)",
    formulaExplanation:
      "The expected value of measuring O is the trace of ρO, which equals the weighted average of eigenvalues λᵢ. Each eigenvalue is a possible measurement outcome, weighted by its probability.",
    relatedTerms: ["measurement", "hermitian", "eigenvalue", "pauli_x"],
    categoryId: "measurement",
  },
  {
    id: "measurement_basis",
    name: "Measurement Basis",
    formalDefinition:
      "The orthonormal basis in which a projective measurement is performed. The computational basis {|0⟩, |1⟩} corresponds to Z-measurement; the Hadamard basis {|+⟩, |−⟩} corresponds to X-measurement. Basis choice determines which information is accessible.",
    intuitiveExplanation:
      "Which 'angle' you measure a qubit from. Measuring in Z-basis (computational basis) gives 0 or 1. Measuring in X-basis gives + or −. The choice matters enormously — cluster states are invisible in Z-basis but reveal structure in X-basis.",
    relatedTerms: ["basis_states", "hadamard", "pauli_invariance", "cluster_state"],
    categoryId: "measurement",
  },
  {
    id: "weak_measurement",
    name: "Weak Measurement",
    formalDefinition:
      "A measurement with weak coupling between system and measurement apparatus, extracting partial information while minimally disturbing the state. The measurement strength can be continuously tuned from zero (no measurement) to full (projective measurement).",
    intuitiveExplanation:
      "A 'gentle peek' at a quantum system — you learn a little bit about the state without fully collapsing it. Like reading a thermometer that barely touches the object being measured. Useful for quantum feedback and monitoring.",
    relatedTerms: ["measurement", "projective_measurement", "quantum_zeno_effect"],
    categoryId: "measurement",
  },
  {
    id: "correlators",
    name: "Correlation Functions",
    formalDefinition:
      "Expectation values of products of operators on different subsystems: ⟨O_A O_B⟩ = Tr(ρ · O_A ⊗ O_B). The connected correlator ⟨O_A O_B⟩_c = ⟨O_A O_B⟩ − ⟨O_A⟩⟨O_B⟩ measures genuine correlation beyond individual expectations.",
    intuitiveExplanation:
      "Quantifies how much two parts of a quantum system are correlated. If ⟨ZZ⟩ ≠ ⟨Z⟩⟨Z⟩, the qubits are correlated. In the framework's 2-qubit visualizer, the three axes (ZI, IZ, ZZ) are exactly these correlators.",
    symbol: "⟨O_A O_B⟩",
    keyEquation:
      "\\langle O_A O_B \\rangle_c = \\langle O_A O_B \\rangle - \\langle O_A \\rangle \\langle O_B \\rangle",
    formulaExplanation:
      "The connected correlator subtracts the product of individual expectations. If this is nonzero, the subsystems are genuinely correlated — knowing about A tells you something about B beyond what their individual statistics reveal.",
    relatedTerms: ["zz_correlator", "entanglement", "mutual_information"],
    categoryId: "measurement",
  },
];
