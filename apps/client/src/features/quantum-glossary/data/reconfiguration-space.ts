import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "reconfiguration_space",
  name: "Reconfiguration Space",
  icon: "compass",
  color: "#8b5cf6",
  description:
    "Theoretical framework for predictable decoherence trajectories in fingerprint space",
};

export const terms: GlossaryTerm[] = [
  {
    id: "reconfiguration_space",
    name: "Reconfiguration Space",
    formalDefinition:
      "The manifold of possible (subspace, embedding) configurations that a quantum system can occupy. Formally, if S is the ideal subspace and H is the full Hilbert space with entanglement structure E, then the reconfiguration space is R = {(S, E) : S ⊂ H, E ∈ Topologies}. Decoherence traces a path through R determined by the interaction geometry between entanglement topology and noise topology.",
    intuitiveExplanation:
      "Instead of asking 'how much did the state decay?', reconfiguration space asks 'WHERE did it go?'. When noise hits a quantum state, it doesn't randomly collapse — it reconfigures along paths determined by the entanglement structure. The reconfiguration space is the map of all possible paths the state can take as it interacts with its environment.",
    relatedTerms: [
      "delta_cov_fingerprint",
      "fiber_bundle",
      "einselection",
      "structured_decoherence",
      "constructor_theory",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "delta_cov_fingerprint",
    name: "ΔCov Fingerprint",
    formalDefinition:
      "The excess covariance matrix ΔCov = Cov(noisy) − Cov(ideal), projected to the n(n−1)/2 dimensional vector space of the upper triangle of pairwise qubit covariances. For n=6 qubits, this is a 15-dimensional vector. Key properties: (1) direction encodes noise topology, (2) magnitude encodes noise severity, (3) cosine similarity between fingerprints at different error rates ≈ 0.874, confirming directional stability.",
    intuitiveExplanation:
      "A fingerprint of how noise affected a quantum state. Instead of a single number ('how bad is the noise'), it's a vector that captures WHICH qubit pairs were affected and how strongly. Chain noise and star noise produce fingerprints pointing in different directions — like different fingerprints at a crime scene telling you who did it.",
    symbol: "ΔCov",
    keyEquation:
      "\\Delta\\text{Cov} = \\text{Cov}(\\text{noisy}) - \\text{Cov}(\\text{ideal}) \\in \\mathbb{R}^{n(n-1)/2}",
    formulaExplanation:
      "Subtract the ideal covariance matrix from the noisy one to isolate what noise changed. The upper triangle gives a vector in n(n-1)/2 dimensions — for 6 qubits that's a 15D fingerprint. The direction tells you WHICH qubit pairs noise affected; the magnitude tells you HOW MUCH.",
    relatedTerms: [
      "reconfiguration_space",
      "covariance_matrix",
      "mutual_information",
      "structure_score",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "fingerprint_trajectory",
    name: "Fingerprint Trajectory",
    formalDefinition:
      "The curve f(d) in ΔCov space traced by the fingerprint as circuit depth d increases under constant noise. Key measurables: (1) trajectory smoothness = mean consecutive cosine similarity, (2) velocity = ||f(d+1) − f(d)||, (3) curvature = second derivative of the trajectory. A smooth trajectory (cosine sim > 0.95) implies predictable decoherence dynamics.",
    intuitiveExplanation:
      "As a quantum state experiences more and more noise (deeper circuit), its fingerprint traces a path through fingerprint space. If this path is a smooth curve (not random zigzag), then decoherence is predictable. If we know where the fingerprint is now and where it's heading, we can forecast where it'll be next — error forecasting instead of error correction.",
    keyEquation:
      "f(d) \\in \\mathbb{R}^{n(n-1)/2}, \\quad \\cos(f(d), f(d+1)) > 0.95 \\implies \\text{predictable}",
    formulaExplanation:
      "The fingerprint f at each circuit depth d traces a curve through fingerprint space. If consecutive fingerprints point in nearly the same direction (cosine similarity > 0.95), the trajectory is smooth and decoherence is predictable — you can forecast where the state is heading.",
    relatedTerms: [
      "delta_cov_fingerprint",
      "reconfiguration_space",
      "decoherence_flow_generator",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "decoherence_flow_generator",
    name: "Decoherence Flow Generator",
    formalDefinition:
      "The matrix A in the linear dynamical system f(d+1) = A · f(d), where f(d) is the ΔCov fingerprint at depth d. If A exists with stable eigenvectors, those eigenvectors are the 'natural directions' of decoherence in fingerprint space. A encodes the reconfiguration dynamics: given any fingerprint, A tells you which direction it will move next. Its eigendecomposition A = VΛV⁻¹ separates the decoherence into independent modes with characteristic rates (eigenvalues).",
    intuitiveExplanation:
      "The 'rules of motion' for decoherence. If you can fit a matrix A that predicts how the fingerprint evolves from one depth to the next, A captures the physics of how noise moves through the entanglement structure. Its eigenvectors are the fundamental decoherence directions — the river channels that noise flows along.",
    symbol: "A",
    keyEquation: "f(d+1) = A \\cdot f(d), \\quad A = V\\Lambda V^{-1}",
    formulaExplanation:
      "A linear map that predicts the next fingerprint from the current one. Its eigendecomposition separates decoherence into independent modes: eigenvectors V are the natural directions of noise flow, eigenvalues \u039B are the rates. Each mode evolves independently — the river has separate channels.",
    relatedTerms: [
      "fingerprint_trajectory",
      "delta_cov_fingerprint",
      "reconfiguration_space",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "einselection",
    name: "Einselection (Environment-Induced Superselection)",
    formalDefinition:
      "Zurek's mechanism by which the system-environment interaction Hamiltonian H_SE selects a preferred 'pointer basis' {|sᵢ⟩} for decoherence. States in this basis are robust (survive decoherence); superpositions of pointer states decohere rapidly. Formally, pointer states satisfy: H_SE|sᵢ⟩|E₀⟩ = |sᵢ⟩|Eᵢ⟩ — they don't entangle with the environment, they just correlate. The pointer basis depends on H_SE, not on the system or environment alone.",
    intuitiveExplanation:
      "Why does Schrödinger's cat end up alive OR dead, never in superposition? Because the environment 'selects' certain states as stable — the pointer basis. States not in this basis get rapidly entangled with the environment and become classical. Einselection is the environment choosing which quantum states survive, like natural selection but for quantum states. Our ΔCov fingerprints might be measuring einselection in action — watching the environment select the decoherence basis in real time.",
    relatedTerms: [
      "decoherence",
      "pointer_basis",
      "reconfiguration_space",
      "open_quantum_system",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "pointer_basis",
    name: "Pointer Basis",
    formalDefinition:
      "The basis {|sᵢ⟩} selected by einselection in which the reduced density matrix of the system becomes (approximately) diagonal after decoherence: ρ_S → Σᵢ pᵢ|sᵢ⟩⟨sᵢ|. For a qubit interacting with a thermal bath, the pointer basis is typically the energy eigenbasis. For position-sensitive environments (e.g., photon scattering), it's the position basis. The pointer basis is what makes quantum measurements produce definite outcomes.",
    intuitiveExplanation:
      "The 'preferred language' that the environment forces on a quantum system. Just as you can describe a vector in any basis, a quantum state can be written in any basis — but the environment 'picks' one. States in this basis look classical; everything else gets smeared out by decoherence. The pointer basis is why we see cats as alive or dead, never both.",
    relatedTerms: ["einselection", "decoherence", "density_matrix"],
    categoryId: "reconfiguration_space",
  },
  {
    id: "fiber_bundle",
    name: "Fiber Bundle (Quantum Geometric Phase)",
    formalDefinition:
      "A mathematical structure (E, B, π, F) where E is the total space, B is the base space, π: E → B is the projection, and F is the fiber. In the reconfiguration context: B = space of entanglement topologies, F = space of quantum states at each topology, the connection defines parallel transport (how states change as topology evolves), and curvature = Berry phase (geometric information from cyclic topology evolution). The ΔCov fingerprint trajectory is a projected section of this bundle.",
    intuitiveExplanation:
      "Imagine a space where each 'point' is an entanglement topology, and at each point there's a whole universe of quantum states with that topology. Moving between topologies (changing entanglement structure) causes the quantum state to pick up geometric phase — information encoded in the path, not just the endpoints. This is exactly the mathematical framework for reconfiguration space: the base space is topologies, the fibers are quantum states, and decoherence trajectories are curves through this structured space.",
    relatedTerms: [
      "berry_phase",
      "reconfiguration_space",
      "geometric_phase",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "berry_phase",
    name: "Berry Phase (Geometric Phase)",
    formalDefinition:
      "A phase γ = i∮⟨ψ(R)|∇_R|ψ(R)⟩·dR acquired by a quantum state when parameters R are adiabatically cycled around a closed loop. Depends only on the geometry of the loop in parameter space, not the speed. In the fiber bundle language, it's the holonomy of the connection — the 'twist' accumulated by parallel transporting around a loop. Berry phase is gauge-invariant and physically measurable.",
    intuitiveExplanation:
      "When you slowly change the conditions of a quantum system in a loop (back to where you started), the state picks up an extra phase that depends on the PATH, not just the start and end points. It's like walking around the Earth and finding you're facing a different direction — the curvature of the space you traveled through changed your orientation. This geometric phase shows up in many physical effects (Aharonov-Bohm, molecular dynamics) and is the mathematical object connecting topology to quantum evolution.",
    symbol: "γ",
    keyEquation:
      "\\gamma = i \\oint \\langle\\psi(R)|\\nabla_R|\\psi(R)\\rangle \\cdot dR",
    formulaExplanation:
      "Integrate the 'quantum connection' (how the state changes with parameters) around a closed loop. The result is a phase that depends only on the geometry of the loop — not the speed of traversal. This geometric phase is the physical signature of curvature in parameter space.",
    relatedTerms: ["fiber_bundle", "adiabatic_evolution", "holonomy"],
    categoryId: "reconfiguration_space",
  },
  {
    id: "constructor_theory",
    name: "Constructor Theory",
    formalDefinition:
      "A meta-theory of physics (Deutsch & Marletto, 2014) that reformulates physical laws in terms of which transformations (tasks) are possible, which are impossible, and why — rather than predicting what will happen given initial conditions. A constructor is an entity that can cause a task to occur repeatedly while retaining its ability to do so. The fundamental dichotomy: every task is either possible (a constructor exists) or impossible (no constructor exists, with a law of physics explaining why).",
    intuitiveExplanation:
      "Instead of asking 'what happens when I drop a ball?' (dynamics), constructor theory asks 'CAN a ball go up? CAN it go down? What transformations are POSSIBLE?' This reframe is powerful because it captures conservation laws, thermodynamics, and quantum theory in a unified language. For our work: the allowed decoherence pathways ARE the possible tasks. The entanglement topology determines which reconfigurations are constructors (possible) and which are forbidden. Structured decoherence means the set of possible transformations has non-trivial structure.",
    relatedTerms: [
      "reconfiguration_space",
      "einselection",
      "structured_decoherence",
    ],
    categoryId: "reconfiguration_space",
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
      "The most general physically allowed transformation of a quantum state. Each Kraus operator E\u2096 is one way the environment can act; the sum covers all possibilities. The completeness relation ensures probability conservation.",
    relatedTerms: [
      "kraus_operators",
      "density_matrix",
      "stinespring_dilation",
      "choi_matrix",
    ],
    categoryId: "reconfiguration_space",
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
      "Each operator E\u2096 'sandwiches' the density matrix, representing one possible noise event. The completeness condition guarantees total probability stays at 1. Different Kraus sets can describe the same channel — the decomposition is not unique.",
    relatedTerms: ["cptp_map", "density_matrix", "decoherence"],
    categoryId: "reconfiguration_space",
  },
  {
    id: "open_quantum_system",
    name: "Open Quantum System",
    formalDefinition:
      "A quantum system S coupled to an environment E, described jointly by H_total = H_S ⊗ I_E + I_S ⊗ H_E + H_SE, where H_SE is the interaction Hamiltonian. The system's evolution is obtained by tracing out the environment: ρ_S(t) = Tr_E[U(t)(ρ_S ⊗ ρ_E)U†(t)]. This trace operation is what produces CPTP maps and decoherence. The Lindblad master equation dρ/dt = −i[H,ρ] + Σₖ(LₖρLₖ† − ½{Lₖ†Lₖ, ρ}) governs Markovian open system dynamics.",
    intuitiveExplanation:
      "A quantum system that's NOT isolated — it interacts with the outside world. Every real quantum computer is an open system. The 'closed to open' transition you've been thinking about is exactly this: when we prepare a quantum state, we try to isolate it (closed system). Noise opens it up to the environment. Decoherence is what happens when information flows from the system to the environment through H_SE. Your reconfiguration space hypothesis is about the STRUCTURE of this information flow — does it follow predictable paths or scatter randomly?",
    keyEquation:
      "\\rho_S(t) = \\text{Tr}_E\\left[ U(t)(\\rho_S \\otimes \\rho_E) U^\\dagger(t) \\right]",
    formulaExplanation:
      "The system and environment evolve together unitarily (U), but we only see the system. Tracing out the environment gives the system's effective evolution — which is generally non-unitary and irreversible. This is the mathematical origin of decoherence.",
    relatedTerms: [
      "decoherence",
      "lindblad_equation",
      "cptp_map",
      "einselection",
      "reconfiguration_space",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "lindblad_equation",
    name: "Lindblad Master Equation",
    formalDefinition:
      "The most general Markovian evolution equation for an open quantum system: dρ/dt = −i[H, ρ] + Σₖ γₖ(LₖρLₖ† − ½{Lₖ†Lₖ, ρ}). The first term is unitary (Hamiltonian) evolution. The Lₖ are Lindblad (jump) operators describing specific decoherence channels. The γₖ are decay rates. The anti-commutator {·,·} ensures trace preservation. Equivalently: dρ/dt = L[ρ] where L is the Lindbladian superoperator.",
    intuitiveExplanation:
      "The equation of motion for a quantum state that's leaking information to its environment. The Hamiltonian part (−i[H,ρ]) is the normal quantum evolution. The Lindblad operators Lₖ are the 'channels' through which information leaks out — each one describes a specific way the environment can disturb the system. The rates γₖ control how fast each channel operates. THIS is where your structured decoherence hypothesis connects to standard physics: if the Lindblad operators have structure related to the entanglement topology, the decoherence pathways are structured too.",
    symbol: "L",
    keyEquation:
      "\\frac{d\\rho}{dt} = -i[H, \\rho] + \\sum_k \\gamma_k \\left( L_k \\rho L_k^\\dagger - \\frac{1}{2}\\{L_k^\\dagger L_k, \\rho\\} \\right)",
    formulaExplanation:
      "The commutator [H,\u03C1] drives reversible rotation; the Lindblad operators L\u2096 drive irreversible dissipation at rates \u03B3\u2096. The anticommutator ensures trace preservation. If the L\u2096 structure mirrors the entanglement topology, decoherence pathways are structured.",
    relatedTerms: [
      "open_quantum_system",
      "cptp_map",
      "decoherence",
      "markovian",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "hilbert_space",
    name: "Hilbert Space",
    formalDefinition:
      "A complete inner product space over the complex numbers ℂ. For n qubits, the Hilbert space is H = (ℂ²)⊗ⁿ = ℂ^(2ⁿ), a 2ⁿ-dimensional complex vector space with inner product ⟨ψ|φ⟩ = Σᵢ ψᵢ*φᵢ. Completeness means every Cauchy sequence converges — important for infinite-dimensional systems. Pure quantum states are unit vectors |ψ⟩ in H (or equivalently, rays in projective Hilbert space P(H) since global phase is unphysical).",
    intuitiveExplanation:
      "The 'arena' where quantum mechanics happens. Every possible state of a quantum system is a point (vector) in this space. For 1 qubit it's 2D complex space, for 2 qubits it's 4D, for n qubits it's 2ⁿ-dimensional — growing exponentially. This exponential growth is both the power of quantum computing (huge space to compute in) and the challenge (huge space for noise to push you around in). Your reconfiguration space lives INSIDE Hilbert space — it's the submanifold of structured decoherence paths.",
    symbol: "H",
    keyEquation:
      "\\mathcal{H} = (\\mathbb{C}^2)^{\\otimes n} = \\mathbb{C}^{2^n}",
    formulaExplanation:
      "The state space for n qubits is the n-fold tensor product of single-qubit spaces. Each qubit doubles the dimension: 1 qubit = 2D, 2 = 4D, 10 = 1024D, 300 qubits = more dimensions than atoms in the universe.",
    relatedTerms: [
      "quantum_state",
      "inner_product",
      "density_matrix",
      "reconfiguration_space",
    ],
    categoryId: "reconfiguration_space",
  },
  {
    id: "pauli_transfer_matrix",
    name: "Pauli Transfer Matrix (PTM)",
    formalDefinition:
      "A real 4×4 (single qubit) or 4ⁿ×4ⁿ (n qubits) matrix representing a quantum channel in the Pauli basis. For a channel Φ, the PTM elements are Rᵢⱼ = Tr(σᵢ Φ(σⱼ)) / d, where σᵢ are Pauli operators (I, X, Y, Z). Advantages over Kraus: (1) composition is matrix multiplication, (2) all entries are real, (3) unitaries correspond to orthogonal matrices. The PTM of a depolarizing channel is (1−p)I + p|0⟩⟨0| (shrinks toward identity row).",
    intuitiveExplanation:
      "A real-valued matrix that tells you exactly what a noise channel does to each component of a quantum state. Instead of working with complex Kraus operators, you get a clean 4×4 matrix where each entry tells you: 'if the input has X polarization, how much Z polarization does the output have?' The Bloch sphere visualizer shows PTMs as heatmaps — the orange/blue pattern reveals the structure of the noise at a glance.",
    symbol: "R",
    keyEquation:
      "R_{ij} = \\frac{1}{d}\\text{Tr}(\\sigma_i \\, \\Phi(\\sigma_j))",
    formulaExplanation:
      "Each entry measures how much Pauli component j is transformed into Pauli component i by the channel \u03A6. The result is a real matrix — no complex numbers needed. The diagonal entries show how much each Bloch vector component shrinks; off-diagonal entries show mixing between components.",
    relatedTerms: ["cptp_map", "bloch_sphere", "kraus_operators"],
    categoryId: "reconfiguration_space",
  },
];
