import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "algorithms",
  name: "Quantum Algorithms",
  icon: "code",
  color: "#8b5cf6",
  description: "Key quantum algorithms and computational primitives",
};

export const terms: GlossaryTerm[] = [
  {
    id: "quantum_teleportation",
    name: "Quantum Teleportation",
    formalDefinition:
      "A protocol transmitting an unknown quantum state |ψ⟩ using a shared Bell pair and two bits of classical communication. Alice performs a Bell measurement, sends the result to Bob, who applies a correction unitary. No faster-than-light communication occurs.",
    intuitiveExplanation:
      "Sending a quantum state from A to B by 'destroying' it at A and 'reconstructing' it at B, using a shared entangled pair and a phone call. The state is never copied (no-cloning theorem) — it's transferred. Foundational for quantum networks.",
    relatedTerms: ["bell_states", "entanglement", "cnot"],
    categoryId: "algorithms",
  },
  {
    id: "grover_search",
    name: "Grover's Algorithm",
    formalDefinition:
      "A quantum search algorithm finding a marked item in an unstructured database of N items using O(√N) queries. Uses amplitude amplification: alternate between the oracle (marks the target) and the diffusion operator (amplifies marked amplitude).",
    intuitiveExplanation:
      "Searching a phone book quantumly — instead of checking every entry (N steps classically), Grover's algorithm finds the answer in √N steps. For a million items, that's 1000 steps instead of 1,000,000. Provides a provably optimal quadratic speedup.",
    keyEquation:
      "O(\\sqrt{N}) \\text{ queries}, \\quad |\\psi\\rangle \\xrightarrow{O(\\sqrt{N})} |\\text{target}\\rangle",
    formulaExplanation:
      "Grover's algorithm finds a marked item in √N steps instead of N. The amplitude of the target state is amplified by ~1/√N per iteration, so after ~(π/4)√N iterations the target has probability near 1. Provably optimal for unstructured search.",
    relatedTerms: ["superposition", "interference", "universal_gate_set"],
    categoryId: "algorithms",
  },
  {
    id: "shor_algorithm",
    name: "Shor's Algorithm",
    formalDefinition:
      "A quantum algorithm for integer factorization in O((log N)³) time, exponentially faster than the best known classical algorithms. Reduces factoring to period-finding via modular exponentiation, then uses the Quantum Fourier Transform to extract the period.",
    intuitiveExplanation:
      "The algorithm that launched quantum computing as a field. Can break RSA encryption by factoring large numbers exponentially faster than any classical computer. A 4096-bit RSA key would require millions of logical qubits — not yet achievable, but a powerful motivator.",
    relatedTerms: ["universal_gate_set", "circuit_depth", "logical_qubit"],
    categoryId: "algorithms",
  },
  {
    id: "vqe",
    name: "Variational Quantum Eigensolver (VQE)",
    formalDefinition:
      "A hybrid quantum-classical algorithm for finding ground state energies. A parameterized quantum circuit (ansatz) prepares a trial state |ψ(θ)⟩; the energy ⟨ψ(θ)|H|ψ(θ)⟩ is measured on quantum hardware; a classical optimizer updates θ to minimize the energy.",
    intuitiveExplanation:
      "Use a quantum computer to prepare trial wavefunctions and a classical computer to optimize them. The quantum part handles the exponentially large Hilbert space; the classical part handles the optimization. Designed for near-term noisy quantum devices.",
    keyEquation:
      "E(\\theta) = \\langle\\psi(\\theta)|H|\\psi(\\theta)\\rangle \\geq E_0",
    formulaExplanation:
      "The variational principle: the energy of any trial state is always above or equal to the true ground state energy E₀. By minimizing E(θ) over circuit parameters θ, VQE converges toward the ground state. The quantum computer evaluates E; the classical computer optimizes θ.",
    relatedTerms: ["hermitian", "eigenvalue", "circuit_depth"],
    categoryId: "algorithms",
  },
  {
    id: "qaoa",
    name: "QAOA",
    formalDefinition:
      "Quantum Approximate Optimization Algorithm: a variational algorithm for combinatorial optimization. Alternates between a problem Hamiltonian H_P and a mixer Hamiltonian H_M with p layers of tunable parameters. Performance improves with depth p.",
    intuitiveExplanation:
      "A recipe for solving optimization problems (like traveling salesman) on a quantum computer. Alternates between 'exploring solutions' and 'focusing on good ones' in p rounds. More rounds = better solutions, but deeper circuits. A leading candidate for quantum advantage.",
    relatedTerms: ["vqe", "universal_gate_set", "circuit_depth"],
    categoryId: "algorithms",
  },
  {
    id: "quantum_fourier_transform",
    name: "Quantum Fourier Transform",
    formalDefinition:
      "The quantum analog of the discrete Fourier transform: QFT|j⟩ = (1/√N) Σₖ e^(2πijk/N)|k⟩. Implemented with O(n²) gates for n qubits. Key subroutine in Shor's algorithm, phase estimation, and quantum simulation.",
    intuitiveExplanation:
      "Transforms quantum states from the 'position' basis to the 'frequency' basis — just like classical Fourier transforms, but exponentially faster. While classical FFT takes O(N log N) steps, QFT takes O(log² N) quantum gates. The engine behind Shor's algorithm.",
    keyEquation:
      "\\text{QFT}|j\\rangle = \\frac{1}{\\sqrt{N}} \\sum_{k=0}^{N-1} e^{2\\pi i jk/N} |k\\rangle",
    formulaExplanation:
      "Each input basis state |j⟩ maps to a uniform superposition of all states, but with phase factors that encode j in the 'frequency domain'. The exponential e^(2πijk/N) is a rotation in the complex plane — different j values produce different phase patterns.",
    relatedTerms: ["shor_algorithm", "circuit_depth", "universal_gate_set"],
    categoryId: "algorithms",
  },
  {
    id: "quantum_simulation",
    name: "Quantum Simulation",
    formalDefinition:
      "Using a controllable quantum system to simulate another quantum system. Digital simulation decomposes time evolution e^(-iHt) into gate sequences via Trotterization. Analog simulation directly engineers the target Hamiltonian. Feynman's original motivation for quantum computing.",
    intuitiveExplanation:
      "The most natural application of quantum computers: simulating quantum physics. Classical computers struggle because quantum states grow exponentially with system size. A quantum computer uses its own quantum nature to simulate other quantum systems efficiently.",
    keyEquation:
      "e^{-iHt} \\approx \\left( \\prod_k e^{-iH_k t/n} \\right)^n",
    formulaExplanation:
      "Trotterization: break the Hamiltonian into simpler pieces Hₖ and alternate small time steps of each. The error shrinks as n increases. This converts continuous-time quantum physics into a discrete gate sequence that a quantum computer can execute.",
    relatedTerms: ["unitary", "circuit_depth", "vqe"],
    categoryId: "algorithms",
  },
];
