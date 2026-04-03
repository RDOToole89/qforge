import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "linear_algebra",
  name: "Linear Algebra for QM",
  icon: "calculator",
  color: "#a855f7",
  description: "Mathematical foundations underlying quantum mechanics",
};

export const terms: GlossaryTerm[] = [
  {
    id: "tensor_product",
    name: "Tensor Product",
    formalDefinition:
      "An operation combining two vector spaces V and W into a larger space V ⊗ W. For quantum systems: |ψ⟩_AB = |ψ⟩_A ⊗ |ψ⟩_B. If V has dimension m and W has dimension n, V ⊗ W has dimension mn. The Kronecker product gives the matrix representation.",
    intuitiveExplanation:
      "How you combine two quantum systems into one. A 2D qubit tensor-producted with another 2D qubit gives a 4D two-qubit system. This exponential growth (2ⁿ for n qubits) is both the source of quantum computing's power and the reason classical simulation is hard.",
    symbol: "⊗",
    keyEquation:
      "|\\psi\\rangle_{AB} = |\\psi\\rangle_A \\otimes |\\psi\\rangle_B, \\quad \\dim = \\dim_A \\times \\dim_B",
    formulaExplanation:
      "The tensor product combines two quantum systems into one. The dimension of the combined space is the product of the individual dimensions — this multiplicative growth is why n qubits need 2ⁿ dimensions.",
    relatedTerms: ["hilbert_space", "product_state", "entanglement"],
    categoryId: "linear_algebra",
  },
  {
    id: "unitary",
    name: "Unitary Operator",
    formalDefinition:
      "A matrix U satisfying U†U = UU† = I. Unitary operators preserve inner products (and thus probabilities). All closed-system quantum evolution is unitary: |ψ(t)⟩ = U(t)|ψ(0)⟩. Quantum gates are unitary operators.",
    intuitiveExplanation:
      "A 'reversible rotation' of quantum states. Every quantum gate is unitary — it can be undone by applying U†. Unitary evolution preserves the total probability and the purity of the state. Noise is precisely what happens when evolution stops being unitary.",
    symbol: "U†U = I",
    keyEquation:
      "U^\\dagger U = U U^\\dagger = I, \\quad |\\psi(t)\\rangle = U(t)|\\psi(0)\\rangle",
    formulaExplanation:
      "A unitary operator times its conjugate transpose equals the identity — meaning it's perfectly reversible. All closed-system quantum evolution is a unitary rotation: the state at time t is U(t) applied to the initial state.",
    relatedTerms: ["hermitian", "quantum_gate", "cptp_map"],
    categoryId: "linear_algebra",
  },
  {
    id: "hermitian",
    name: "Hermitian Operator",
    formalDefinition:
      "A matrix H satisfying H = H† (equal to its conjugate transpose). Hermitian operators have real eigenvalues and orthogonal eigenstates. All physical observables in quantum mechanics are Hermitian. The Pauli matrices and the Hamiltonian are Hermitian.",
    intuitiveExplanation:
      "A matrix that equals its own mirror image (conjugate transpose). Its eigenvalues are always real numbers — which is why measurement outcomes are real. Every physical quantity you can measure (energy, spin, position) corresponds to a Hermitian operator.",
    symbol: "H = H†",
    keyEquation:
      "H = H^\\dagger, \\quad H|\\lambda\\rangle = \\lambda|\\lambda\\rangle, \\quad \\lambda \\in \\mathbb{R}",
    formulaExplanation:
      "A Hermitian operator equals its own conjugate transpose, which guarantees all its eigenvalues \u03bb are real numbers. This is why measurement outcomes are real — every observable in physics is a Hermitian operator.",
    relatedTerms: ["observable", "eigenvalue", "unitary"],
    categoryId: "linear_algebra",
  },
  {
    id: "eigenvalue",
    name: "Eigenvalue / Eigenvector",
    formalDefinition:
      "For an operator A, a scalar λ and non-zero vector |v⟩ satisfying A|v⟩ = λ|v⟩. For Hermitian operators, eigenvalues are real and eigenvectors are orthogonal. The eigenvalues of an observable are its possible measurement outcomes.",
    intuitiveExplanation:
      "Special directions that a matrix doesn't rotate — only stretches or flips. Measuring an observable yields one of its eigenvalues, and the state collapses to the corresponding eigenvector. The eigenvalues of σ_z are +1 (for |0⟩) and −1 (for |1⟩).",
    symbol: "A|v⟩ = λ|v⟩",
    keyEquation: "A|v\\rangle = \\lambda|v\\rangle",
    formulaExplanation:
      "When operator A acts on eigenvector |v\u27E9, it simply scales it by \u03bb — no rotation, just stretching. In quantum mechanics, measuring observable A on eigenstate |v\u27E9 always gives result \u03bb with certainty.",
    relatedTerms: ["hermitian", "observable", "spectral_decomposition"],
    categoryId: "linear_algebra",
  },
  {
    id: "spectral_decomposition",
    name: "Spectral Decomposition",
    formalDefinition:
      "Every Hermitian operator A can be written as A = Σᵢ λᵢ|eᵢ⟩⟨eᵢ| where λᵢ are eigenvalues and |eᵢ⟩ are orthonormal eigenvectors. This diagonalizes A in its eigenbasis. Enables computing functions of operators: f(A) = Σᵢ f(λᵢ)|eᵢ⟩⟨eᵢ|.",
    intuitiveExplanation:
      "Breaking a matrix into its 'fundamental vibrations'. Every Hermitian matrix can be expressed as a weighted sum of projectors onto its eigenstates. This is how we compute things like e^(iHt) or log(\u03c1) in quantum mechanics.",
    keyEquation: "A = \\sum_i \\lambda_i |e_i\\rangle\\langle e_i|",
    formulaExplanation:
      "Any Hermitian operator can be decomposed into a sum of its eigenvalues times projectors onto the corresponding eigenstates. This is how we compute matrix functions like e^(iHt) — apply the function to each eigenvalue separately.",
    relatedTerms: ["eigenvalue", "hermitian", "density_matrix"],
    categoryId: "linear_algebra",
  },
  {
    id: "inner_product",
    name: "Inner Product",
    formalDefinition:
      "A function ⟨·|·⟩: ℋ × ℋ → ℂ satisfying conjugate symmetry, linearity in the second argument, and positive-definiteness. In Dirac notation: ⟨φ|ψ⟩. Defines notions of orthogonality, norm, and angle in Hilbert space.",
    intuitiveExplanation:
      "The quantum dot product — measures 'overlap' between two states. If ⟨φ|ψ⟩ = 0, the states are orthogonal (completely distinguishable). If |⟨φ|ψ⟩| = 1, they're the same state (up to a phase). Born rule: P = |⟨m|ψ⟩|².",
    symbol: "⟨φ|ψ⟩",
    keyEquation:
      "\\langle \\varphi | \\psi \\rangle \\in \\mathbb{C}, \\quad \\|\\psi\\| = \\sqrt{\\langle \\psi | \\psi \\rangle}",
    formulaExplanation:
      "The inner product measures the 'overlap' between two quantum states as a complex number. Its absolute value squared gives the probability of one state being found in the other. The norm (length) of a state comes from its inner product with itself.",
    relatedTerms: ["hilbert_space", "born_rule", "basis_states"],
    categoryId: "linear_algebra",
  },
  {
    id: "commutator",
    name: "Commutator",
    formalDefinition:
      "For operators A and B: [A, B] = AB − BA. If [A, B] = 0, the operators commute (share eigenstates and can be measured simultaneously). The Heisenberg uncertainty principle follows from non-commuting observables: ΔA·ΔB ≥ |⟨[A,B]⟩|/2.",
    intuitiveExplanation:
      "Measures whether the order of two operations matters. If [A, B] = 0, doing A then B is the same as B then A. For quantum mechanics, non-commuting observables (like X and Z) can't both be known precisely — this is the uncertainty principle.",
    symbol: "[A, B]",
    keyEquation:
      "[A, B] = AB - BA, \\quad \\Delta A \\cdot \\Delta B \\geq \\frac{|\\langle [A,B] \\rangle|}{2}",
    formulaExplanation:
      "The commutator measures whether the order of operations matters. When [A,B] \u2260 0, the operators don't commute and the uncertainty principle kicks in: you can't know both precisely. The product of their uncertainties has a minimum bound.",
    relatedTerms: ["observable", "pauli_x", "pauli_z"],
    categoryId: "linear_algebra",
  },
  {
    id: "dirac_notation",
    name: "Dirac (Bra-Ket) Notation",
    formalDefinition:
      "A notation system where |ψ⟩ (ket) denotes a column vector in Hilbert space, ⟨ψ| (bra) denotes its conjugate transpose (row vector), and ⟨φ|ψ⟩ denotes the inner product. The outer product |ψ⟩⟨φ| is an operator.",
    intuitiveExplanation:
      "The standard shorthand for quantum mechanics. |0⟩ is a state vector (ket), ⟨0| is its mirror image (bra), ⟨0|1⟩ is the overlap (bracket), and |0⟩⟨1| is a matrix (outer product). Named because ⟨bra|ket⟩ forms a 'bracket'.",
    symbol: "|ψ⟩, ⟨ψ|",
    keyEquation:
      "|\\psi\\rangle \\in \\mathcal{H}, \\quad \\langle\\varphi|\\psi\\rangle \\in \\mathbb{C}, \\quad |\\psi\\rangle\\langle\\varphi| \\in \\mathcal{L}(\\mathcal{H})",
    formulaExplanation:
      "Kets |\u03c8\u27E9 are state vectors in Hilbert space, bra-kets \u27E8\u03c6|\u03c8\u27E9 are complex-valued inner products (overlaps), and outer products |\u03c8\u27E9\u27E8\u03c6| are operators (matrices) that act on states. The notation elegantly encodes all three structures.",
    relatedTerms: ["hilbert_space", "inner_product", "basis_states"],
    categoryId: "linear_algebra",
  },
];
