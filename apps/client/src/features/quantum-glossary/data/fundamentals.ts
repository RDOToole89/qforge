import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "fundamentals",
  name: "Quantum Fundamentals",
  icon: "atom",
  color: "#6366f1",
  description: "Core concepts of quantum mechanics and quantum computing",
};

export const terms: GlossaryTerm[] = [
  {
    id: "qubit",
    name: "Qubit",
    formalDefinition:
      "A two-level quantum system described by a state vector |ψ⟩ = α|0⟩ + β|1⟩ where |α|² + |β|² = 1. The coefficients α and β are complex probability amplitudes.",
    intuitiveExplanation:
      "The quantum version of a classical bit. Unlike a regular bit that must be 0 or 1, a qubit can exist in a superposition of both states simultaneously until measured.",
    symbol: "|ψ⟩",
    keyEquation: "|\\psi\\rangle = \\alpha|0\\rangle + \\beta|1\\rangle, \\quad |\\alpha|^2 + |\\beta|^2 = 1",
    formulaExplanation:
      "A qubit state is a weighted combination of |0⟩ and |1⟩. The weights α and β are complex numbers whose squared magnitudes must add to 1 — ensuring total probability is conserved.",
    relatedTerms: ["superposition", "bloch_sphere", "measurement", "hilbert_space"],
    categoryId: "fundamentals",
  },
  {
    id: "superposition",
    name: "Superposition",
    formalDefinition:
      "A fundamental principle of quantum mechanics where a quantum system exists in a linear combination of multiple basis states simultaneously. For a qubit: |ψ⟩ = α|0⟩ + β|1⟩ with α, β ∈ ℂ.",
    intuitiveExplanation:
      "A quantum system can be in multiple states at once — not uncertain, but genuinely in all of them. Measurement forces it to 'pick' one outcome probabilistically.",
    symbol: "α|0⟩ + β|1⟩",
    keyEquation: "|\\psi\\rangle = \\sum_{i} c_i |e_i\\rangle, \\quad \\sum_{i} |c_i|^2 = 1",
    formulaExplanation:
      "Any quantum state can be written as a sum over basis states |eᵢ⟩ with complex coefficients cᵢ. The squared magnitudes of all coefficients must sum to 1 — this is the normalization condition that preserves probability.",
    relatedTerms: ["qubit", "measurement", "born_rule", "interference"],
    categoryId: "fundamentals",
  },
  {
    id: "measurement",
    name: "Quantum Measurement",
    formalDefinition:
      "An irreversible operation that projects a quantum state onto one of the eigenstates of the measurement observable. The outcome is probabilistic, governed by the Born rule, and the state collapses to the measured eigenstate.",
    intuitiveExplanation:
      "The act of 'looking' at a quantum system. Before measurement, the system can be in superposition; after measurement, it's in a definite state. You can't undo it.",
    symbol: "M",
    relatedTerms: ["born_rule", "projective_measurement", "povm", "observable"],
    categoryId: "fundamentals",
  },
  {
    id: "born_rule",
    name: "Born Rule",
    formalDefinition:
      "The probability of measuring outcome |m⟩ from state |ψ⟩ is P(m) = |⟨m|ψ⟩|². This postulate connects the mathematical formalism of quantum mechanics to experimental observations.",
    intuitiveExplanation:
      "The recipe for calculating probabilities in quantum mechanics: square the absolute value of the amplitude. If a qubit has amplitude 1/√2 for |0⟩, the probability of measuring 0 is (1/√2)² = 1/2.",
    symbol: "P(m) = |⟨m|ψ⟩|²",
    keyEquation: "P(m) = |\\langle m | \\psi \\rangle|^2",
    formulaExplanation:
      "The probability of getting outcome m equals the squared magnitude of the inner product (overlap) between the measurement state ⟨m| and the quantum state |ψ⟩. This is the bridge between quantum math and experimental results.",
    relatedTerms: ["measurement", "superposition", "probability_amplitude"],
    categoryId: "fundamentals",
  },
  {
    id: "hilbert_space",
    name: "Hilbert Space",
    formalDefinition:
      "A complete inner product space that serves as the state space of a quantum system. For n qubits, the Hilbert space is ℂ^(2ⁿ), a 2ⁿ-dimensional complex vector space with an inner product ⟨φ|ψ⟩.",
    intuitiveExplanation:
      "The mathematical 'arena' where quantum states live. A single qubit lives in a 2D space; two qubits live in a 4D space. The dimension doubles with each added qubit — this exponential growth is what makes quantum computing powerful.",
    symbol: "ℋ",
    keyEquation: "\\mathcal{H} = \\mathbb{C}^{2^n}, \\quad \\dim(\\mathcal{H}) = 2^n",
    formulaExplanation:
      "The state space for n qubits is a 2ⁿ-dimensional complex vector space. Each added qubit doubles the dimension — 1 qubit = 2D, 2 qubits = 4D, 10 qubits = 1024D. This exponential scaling is both the power and the challenge of quantum computing.",
    relatedTerms: ["qubit", "basis_states", "inner_product", "tensor_product"],
    categoryId: "fundamentals",
  },
  {
    id: "basis_states",
    name: "Basis States",
    formalDefinition:
      "A set of orthonormal vectors {|e₁⟩, |e₂⟩, ...} that span the Hilbert space. The computational basis for a qubit is {|0⟩, |1⟩}. Any state can be expressed as a linear combination of basis states.",
    intuitiveExplanation:
      "The 'coordinate axes' of quantum state space. For a qubit, |0⟩ and |1⟩ are the standard basis — like North and East on a map. Every qubit state is some combination of these two directions.",
    symbol: "{|0⟩, |1⟩}",
    relatedTerms: ["qubit", "hilbert_space", "superposition", "measurement_basis"],
    categoryId: "fundamentals",
  },
  {
    id: "probability_amplitude",
    name: "Probability Amplitude",
    formalDefinition:
      "A complex number α whose squared modulus |α|² gives the probability of a measurement outcome. Amplitudes can interfere constructively or destructively, unlike classical probabilities.",
    intuitiveExplanation:
      "The 'hidden variable' behind quantum probabilities. Unlike classical probabilities that only add up, amplitudes are complex numbers that can cancel each other out (destructive interference) or reinforce (constructive interference).",
    symbol: "α, β ∈ ℂ",
    keyEquation: "\\alpha = |\\alpha|\\, e^{i\\theta}, \\quad P = |\\alpha|^2",
    formulaExplanation:
      "An amplitude is a complex number with a magnitude and a phase angle θ. The probability comes from squaring the magnitude — but the phase is what enables interference. Two paths with opposite phases cancel; same phases reinforce.",
    relatedTerms: ["born_rule", "superposition", "interference"],
    categoryId: "fundamentals",
  },
  {
    id: "interference",
    name: "Quantum Interference",
    formalDefinition:
      "The phenomenon where probability amplitudes from different quantum paths combine, leading to enhanced (constructive) or suppressed (destructive) probabilities. A direct consequence of the superposition principle.",
    intuitiveExplanation:
      "Quantum states can 'cancel out' or 'reinforce' each other like waves in water. This is the engine behind quantum algorithms — they arrange for wrong answers to cancel and right answers to amplify.",
    relatedTerms: ["probability_amplitude", "superposition", "hadamard"],
    categoryId: "fundamentals",
  },
];
