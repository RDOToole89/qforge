import type { GlossaryCategory, GlossaryTerm } from "../types";
import { viz } from "@/src/design/tokens";

export const category: GlossaryCategory = {
  id: "open_quantum_systems",
  name: "Open Quantum Systems",
  icon: "compass",
  color: viz.gate.violet,
  description:
    "How quantum systems interact with their environment — channels, master equations, and decoherence",
};

export const terms: GlossaryTerm[] = [
  {
    id: "einselection",
    name: "Einselection (Environment-Induced Superselection)",
    formalDefinition:
      "Zurek's mechanism by which the system-environment interaction Hamiltonian H_SE selects a preferred 'pointer basis' {|sᵢ⟩} for decoherence. States in this basis are robust (survive decoherence); superpositions of pointer states decohere rapidly. Formally, pointer states satisfy: H_SE|sᵢ⟩|E₀⟩ = |sᵢ⟩|Eᵢ⟩ — they don't entangle with the environment, they just correlate. The pointer basis depends on H_SE, not on the system or environment alone.",
    intuitiveExplanation:
      "Why does Schrödinger's cat end up alive OR dead, never in superposition? Because the environment 'selects' certain states as stable — the pointer basis. States not in this basis get rapidly entangled with the environment and become classical. Einselection is the environment choosing which quantum states survive, like natural selection but for quantum states.",
    relatedTerms: ["decoherence", "pointer_basis", "open_quantum_system"],
    categoryId: "open_quantum_systems",
  },
  {
    id: "pointer_basis",
    name: "Pointer Basis",
    formalDefinition:
      "The basis {|sᵢ⟩} selected by einselection in which the reduced density matrix of the system becomes (approximately) diagonal after decoherence: ρ_S → Σᵢ pᵢ|sᵢ⟩⟨sᵢ|. For a qubit interacting with a thermal bath, the pointer basis is typically the energy eigenbasis. For position-sensitive environments (e.g., photon scattering), it's the position basis. The pointer basis is what makes quantum measurements produce definite outcomes.",
    intuitiveExplanation:
      "The 'preferred language' that the environment forces on a quantum system. Just as you can describe a vector in any basis, a quantum state can be written in any basis — but the environment 'picks' one. States in this basis look classical; everything else gets smeared out by decoherence. The pointer basis is why we see cats as alive or dead, never both.",
    relatedTerms: ["einselection", "decoherence", "density_matrix"],
    categoryId: "open_quantum_systems",
  },
  {
    id: "berry_phase",
    name: "Berry Phase (Geometric Phase)",
    formalDefinition:
      "A phase γ = i∮⟨ψ(R)|∇_R|ψ(R)⟩·dR acquired by a quantum state when parameters R are adiabatically cycled around a closed loop. Depends only on the geometry of the loop in parameter space, not the speed. It is the holonomy of the underlying connection — the 'twist' accumulated by parallel transporting around a loop. Berry phase is gauge-invariant and physically measurable.",
    intuitiveExplanation:
      "When you slowly change the conditions of a quantum system in a loop (back to where you started), the state picks up an extra phase that depends on the PATH, not just the start and end points. It's like walking around the Earth and finding you're facing a different direction — the curvature of the space you traveled through changed your orientation. This geometric phase shows up in many physical effects (Aharonov-Bohm, molecular dynamics).",
    symbol: "γ",
    keyEquation:
      "\\gamma = i \\oint \\langle\\psi(R)|\\nabla_R|\\psi(R)\\rangle \\cdot dR",
    formulaExplanation:
      "Integrate the 'quantum connection' (how the state changes with parameters) around a closed loop. The result is a phase that depends only on the geometry of the loop — not the speed of traversal. This geometric phase is the physical signature of curvature in parameter space.",
    relatedTerms: ["adiabatic_evolution", "holonomy"],
    categoryId: "open_quantum_systems",
  },
  {
    id: "cptp_map",
    name: "CPTP Map (Quantum Channel)",
    formalDefinition:
      "A Completely Positive, Trace-Preserving linear map Φ: ρ → Φ(ρ) acting on density matrices. 'Completely positive' means Φ ⊗ I maps positive operators to positive operators (physical even when the system is entangled with an ancilla). 'Trace-preserving' means Tr(Φ(ρ)) = 1 (probabilities sum to 1). Equivalent representations: (1) Kraus: Φ(ρ) = ΣₖEₖρEₖ† with ΣₖEₖ†Eₖ = I, (2) Stinespring: Φ(ρ) = Tr_E[U(ρ⊗|0⟩⟨0|)U†], (3) Choi matrix: C_Φ = (Φ⊗I)(|Ω⟩⟨Ω|) where |Ω⟩ = Σᵢ|ii⟩/√d.",
    intuitiveExplanation:
      "The most general thing that can happen to a quantum state — including noise, measurement, and unitary evolution. CPTP maps are to quantum states what functions are to numbers. Every noise model (depolarizing, amplitude damping, etc.) is a CPTP map. The Bloch sphere visualizer shows how CPTP maps deform the sphere — a depolarizing channel shrinks it uniformly, amplitude damping squashes it toward |0⟩, and dephasing flattens it into a disk.",
    symbol: "Φ",
    keyEquation:
      "\\Phi(\\rho) = \\sum_k E_k \\rho E_k^\\dagger, \\quad \\sum_k E_k^\\dagger E_k = I",
    formulaExplanation:
      "The most general physically allowed transformation of a quantum state. Each Kraus operator Eₖ is one way the environment can act; the sum covers all possibilities. The completeness relation ensures probability conservation.",
    relatedTerms: ["kraus_operators", "density_matrix", "stinespring_dilation", "choi_matrix"],
    categoryId: "open_quantum_systems",
  },
  {
    id: "kraus_operators",
    name: "Kraus Operators (Operator-Sum Representation)",
    formalDefinition:
      "A set of operators {Eₖ} satisfying ΣₖEₖ†Eₖ = I that define a CPTP map via Φ(ρ) = ΣₖEₖρEₖ†. Not unique — any unitary mixing of Kraus operators gives the same channel. The number of Kraus operators needed is at most d² (d = dimension). Examples: depolarizing channel has 4 Kraus operators (I, X, Y, Z with appropriate weights); amplitude damping has 2 (E₀ = |0⟩⟨0| + √(1−γ)|1⟩⟨1|, E₁ = √γ|0⟩⟨1|).",
    intuitiveExplanation:
      "A recipe for noise. Each Kraus operator is one possible thing the environment does to the qubit. The qubit experiences a random mixture of all of them — but crucially, we don't know WHICH one happened (that information leaked to the environment). The sum over all Kraus operators gives the overall noise effect. It's like rolling multiple dice and averaging the outcomes, but in quantum matrix form.",
    symbol: "Eₖ",
    keyEquation:
      "\\Phi(\\rho) = \\sum_k E_k \\rho E_k^\\dagger, \\quad \\sum_k E_k^\\dagger E_k = I",
    formulaExplanation:
      "Each operator Eₖ 'sandwiches' the density matrix, representing one possible noise event. The completeness condition guarantees total probability stays at 1. Different Kraus sets can describe the same channel — the decomposition is not unique.",
    relatedTerms: ["cptp_map", "density_matrix", "decoherence"],
    categoryId: "open_quantum_systems",
  },
  {
    id: "open_quantum_system",
    name: "Open Quantum System",
    formalDefinition:
      "A quantum system S coupled to an environment E, described jointly by H_total = H_S ⊗ I_E + I_S ⊗ H_E + H_SE, where H_SE is the interaction Hamiltonian. The system's evolution is obtained by tracing out the environment: ρ_S(t) = Tr_E[U(t)(ρ_S ⊗ ρ_E)U†(t)]. This trace operation is what produces CPTP maps and decoherence. The Lindblad master equation dρ/dt = −i[H,ρ] + Σₖ(LₖρLₖ† − ½{Lₖ†Lₖ, ρ}) governs Markovian open system dynamics.",
    intuitiveExplanation:
      "A quantum system that's NOT isolated — it interacts with the outside world. Every real quantum computer is an open system. When we prepare a quantum state, we try to isolate it (closed system). Noise opens it up to the environment. Decoherence is what happens when information flows from the system to the environment through H_SE.",
    keyEquation:
      "\\rho_S(t) = \\text{Tr}_E\\left[ U(t)(\\rho_S \\otimes \\rho_E) U^\\dagger(t) \\right]",
    formulaExplanation:
      "The system and environment evolve together unitarily (U), but we only see the system. Tracing out the environment gives the system's effective evolution — which is generally non-unitary and irreversible. This is the mathematical origin of decoherence.",
    relatedTerms: ["decoherence", "lindblad_equation", "cptp_map", "einselection"],
    categoryId: "open_quantum_systems",
  },
  {
    id: "lindblad_equation",
    name: "Lindblad Master Equation",
    formalDefinition:
      "The most general Markovian evolution equation for an open quantum system: dρ/dt = −i[H, ρ] + Σₖ γₖ(LₖρLₖ† − ½{Lₖ†Lₖ, ρ}). The first term is unitary (Hamiltonian) evolution. The Lₖ are Lindblad (jump) operators describing specific decoherence channels. The γₖ are decay rates. The anti-commutator {·,·} ensures trace preservation. Equivalently: dρ/dt = L[ρ] where L is the Lindbladian superoperator.",
    intuitiveExplanation:
      "The equation of motion for a quantum state that's leaking information to its environment. The Hamiltonian part (−i[H,ρ]) is the normal quantum evolution. The Lindblad operators Lₖ are the 'channels' through which information leaks out — each one describes a specific way the environment can disturb the system. The rates γₖ control how fast each channel operates.",
    symbol: "L",
    keyEquation:
      "\\frac{d\\rho}{dt} = -i[H, \\rho] + \\sum_k \\gamma_k \\left( L_k \\rho L_k^\\dagger - \\frac{1}{2}\\{L_k^\\dagger L_k, \\rho\\} \\right)",
    formulaExplanation:
      "The commutator [H,ρ] drives reversible rotation; the Lindblad operators Lₖ drive irreversible dissipation at rates γₖ. The anticommutator ensures trace preservation.",
    relatedTerms: ["open_quantum_system", "cptp_map", "decoherence", "markovian"],
    categoryId: "open_quantum_systems",
  },
  {
    id: "hilbert_space",
    name: "Hilbert Space",
    formalDefinition:
      "A complete inner product space over the complex numbers ℂ. For n qubits, the Hilbert space is H = (ℂ²)⊗ⁿ = ℂ^(2ⁿ), a 2ⁿ-dimensional complex vector space with inner product ⟨ψ|φ⟩ = Σᵢ ψᵢ*φᵢ. Completeness means every Cauchy sequence converges — important for infinite-dimensional systems. Pure quantum states are unit vectors |ψ⟩ in H (or equivalently, rays in projective Hilbert space P(H) since global phase is unphysical).",
    intuitiveExplanation:
      "The 'arena' where quantum mechanics happens. Every possible state of a quantum system is a point (vector) in this space. For 1 qubit it's 2D complex space, for 2 qubits it's 4D, for n qubits it's 2ⁿ-dimensional — growing exponentially. This exponential growth is both the power of quantum computing (huge space to compute in) and the challenge (huge space for noise to push you around in).",
    symbol: "H",
    keyEquation:
      "\\mathcal{H} = (\\mathbb{C}^2)^{\\otimes n} = \\mathbb{C}^{2^n}",
    formulaExplanation:
      "The state space for n qubits is the n-fold tensor product of single-qubit spaces. Each qubit doubles the dimension: 1 qubit = 2D, 2 = 4D, 10 = 1024D, 300 qubits = more dimensions than atoms in the universe.",
    relatedTerms: ["quantum_state", "inner_product", "density_matrix"],
    categoryId: "open_quantum_systems",
  },
  {
    id: "pauli_transfer_matrix",
    name: "Pauli Transfer Matrix (PTM)",
    formalDefinition:
      "A real 4×4 (single qubit) or 4ⁿ×4ⁿ (n qubits) matrix representing a quantum channel in the Pauli basis. For a channel Φ, the PTM elements are Rᵢⱼ = Tr(σᵢ Φ(σⱼ)) / d, where σᵢ are Pauli operators (I, X, Y, Z). Advantages over Kraus: (1) composition is matrix multiplication, (2) all entries are real, (3) unitaries correspond to orthogonal matrices.",
    intuitiveExplanation:
      "A real-valued matrix that tells you exactly what a noise channel does to each component of a quantum state. Instead of working with complex Kraus operators, you get a clean 4×4 matrix where each entry tells you: 'if the input has X polarization, how much Z polarization does the output have?' The Bloch sphere visualizer shows PTMs as heatmaps — the pattern reveals the structure of the noise at a glance.",
    symbol: "R",
    keyEquation:
      "R_{ij} = \\frac{1}{d}\\text{Tr}(\\sigma_i \\, \\Phi(\\sigma_j))",
    formulaExplanation:
      "Each entry measures how much Pauli component j is transformed into Pauli component i by the channel Φ. The result is a real matrix — no complex numbers needed. The diagonal entries show how much each Bloch vector component shrinks; off-diagonal entries show mixing between components.",
    relatedTerms: ["cptp_map", "bloch_sphere", "kraus_operators"],
    categoryId: "open_quantum_systems",
  },
];
