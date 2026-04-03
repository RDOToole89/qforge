import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "gates",
  name: "Quantum Gates & Circuits",
  icon: "microchip",
  color: "#f59e0b",
  description: "Operations on qubits and their circuit representations",
};

export const terms: GlossaryTerm[] = [
  {
    id: "pauli_x",
    name: "Pauli-X Gate",
    formalDefinition:
      "A single-qubit gate represented by the matrix σₓ = [[0,1],[1,0]]. It maps |0⟩ → |1⟩ and |1⟩ → |0⟩. Equivalent to a π rotation about the X-axis of the Bloch sphere.",
    intuitiveExplanation:
      "The quantum NOT gate — it flips |0⟩ to |1⟩ and vice versa. On the Bloch sphere, it's a 180° rotation around the X-axis.",
    symbol: "X, σₓ",
    keyEquation: "X = \\begin{pmatrix} 0 & 1 \\\\ 1 & 0 \\end{pmatrix}",
    formulaExplanation:
      "A 2x2 matrix that swaps the |0⟩ and |1⟩ components. The off-diagonal 1s perform the flip — it's the quantum equivalent of a NOT gate.",
    relatedTerms: ["pauli_y", "pauli_z", "bloch_sphere", "bit_flip"],
    categoryId: "gates",
  },
  {
    id: "pauli_y",
    name: "Pauli-Y Gate",
    formalDefinition:
      "A single-qubit gate represented by σᵧ = [[0,−i],[i,0]]. Maps |0⟩ → i|1⟩ and |1⟩ → −i|0⟩. Equivalent to a π rotation about the Y-axis of the Bloch sphere.",
    intuitiveExplanation:
      "Flips the qubit like X but also adds a phase factor. On the Bloch sphere, it's a 180° rotation around the Y-axis. Less commonly used alone but fundamental to the Pauli group.",
    symbol: "Y, σᵧ",
    keyEquation: "Y = \\begin{pmatrix} 0 & -i \\\\ i & 0 \\end{pmatrix}",
    formulaExplanation:
      "Like the X gate but with imaginary entries. The i and -i introduce a 90-degree phase shift while flipping, combining a bit flip with a phase flip in one operation.",
    relatedTerms: ["pauli_x", "pauli_z", "bloch_sphere"],
    categoryId: "gates",
  },
  {
    id: "pauli_z",
    name: "Pauli-Z Gate",
    formalDefinition:
      "A single-qubit gate represented by σ_z = [[1,0],[0,−1]]. Leaves |0⟩ unchanged and maps |1⟩ → −|1⟩. Equivalent to a π rotation about the Z-axis of the Bloch sphere.",
    intuitiveExplanation:
      "Adds a minus sign to the |1⟩ component — a 'phase flip'. It doesn't change measurement probabilities in the Z-basis but rotates the phase. This is why Z-errors are invisible to Z-basis measurement.",
    symbol: "Z, σ_z",
    keyEquation: "Z = \\begin{pmatrix} 1 & 0 \\\\ 0 & -1 \\end{pmatrix}",
    formulaExplanation:
      "A diagonal matrix that leaves |0⟩ alone and multiplies |1⟩ by -1. Since it's diagonal, it only changes phases — measurement probabilities in the Z-basis are unchanged.",
    relatedTerms: ["pauli_x", "pauli_y", "phase_flip", "dephasing"],
    categoryId: "gates",
  },
  {
    id: "hadamard",
    name: "Hadamard Gate",
    formalDefinition:
      "A single-qubit gate H = (1/√2)[[1,1],[1,−1]]. Maps |0⟩ → |+⟩ = (|0⟩+|1⟩)/√2 and |1⟩ → |−⟩ = (|0⟩−|1⟩)/√2. Creates equal superposition from basis states.",
    intuitiveExplanation:
      "The 'superposition creator'. Apply it to |0⟩ and you get an equal blend of 0 and 1. It's the most common first step in quantum algorithms — putting qubits into superposition so they can explore multiple possibilities at once.",
    symbol: "H",
    keyEquation: "H = \\frac{1}{\\sqrt{2}} \\begin{pmatrix} 1 & 1 \\\\ 1 & -1 \\end{pmatrix}",
    formulaExplanation:
      "The factor 1/\u221A2 ensures normalization. The symmetric structure creates equal superposition from |0\u27E9, while the minus sign in the bottom-right creates the opposite superposition from |1\u27E9 \u2014 this asymmetry is what enables interference.",
    relatedTerms: ["superposition", "basis_states", "interference", "measurement_basis"],
    categoryId: "gates",
  },
  {
    id: "cnot",
    name: "CNOT Gate",
    formalDefinition:
      "A two-qubit gate that flips the target qubit if and only if the control qubit is |1⟩. In the computational basis: |00⟩→|00⟩, |01⟩→|01⟩, |10⟩→|11⟩, |11⟩→|10⟩. Also called controlled-X (CX).",
    intuitiveExplanation:
      "A quantum 'if-then' gate: IF the first qubit is 1, THEN flip the second. It's the primary tool for creating entanglement — apply Hadamard then CNOT and you get a Bell state.",
    symbol: "CX",
    keyEquation: "\\text{CNOT} = |0\\rangle\\langle 0| \\otimes I + |1\\rangle\\langle 1| \\otimes X",
    formulaExplanation:
      "Reads as: 'if control is |0\u27E9, do nothing (I) to target; if control is |1\u27E9, apply X (flip) to target.' This projector decomposition shows explicitly how the gate conditions on the control qubit.",
    relatedTerms: ["cz_gate", "entanglement", "bell_states", "universal_gate_set"],
    categoryId: "gates",
  },
  {
    id: "cz_gate",
    name: "CZ Gate",
    formalDefinition:
      "A two-qubit gate that applies a Z phase to the target qubit when the control is |1⟩. Symmetric between control and target: CZ|11⟩ = −|11⟩, all other basis states unchanged. Diagonal in the computational basis.",
    intuitiveExplanation:
      "Adds a minus sign only when both qubits are |1⟩. Unlike CNOT, it's symmetric — neither qubit is special. CZ is the entangling gate used to build cluster states. Because it's diagonal, it commutes with Z-basis measurements — key to the Pauli invariance theorem.",
    symbol: "CZ",
    keyEquation: "CZ = |0\\rangle\\langle 0| \\otimes I + |1\\rangle\\langle 1| \\otimes Z",
    formulaExplanation:
      "If control is |0\u27E9, do nothing; if control is |1\u27E9, apply Z (phase flip) to target. Because Z is diagonal, CZ is symmetric between control and target \u2014 neither qubit is 'special'.",
    relatedTerms: ["cnot", "cluster_state", "pauli_invariance"],
    categoryId: "gates",
  },
  {
    id: "toffoli",
    name: "Toffoli Gate (CCX)",
    formalDefinition:
      "A three-qubit gate that flips the target qubit if and only if both control qubits are |1⟩. It is universal for classical reversible computation and, combined with Hadamard, universal for quantum computation.",
    intuitiveExplanation:
      "A quantum AND gate: flip the target only when both controls are 1. It can simulate any classical logic gate, proving that quantum computers can do everything classical computers can — and more.",
    symbol: "CCX",
    relatedTerms: ["cnot", "universal_gate_set"],
    categoryId: "gates",
  },
  {
    id: "universal_gate_set",
    name: "Universal Gate Set",
    formalDefinition:
      "A finite set of quantum gates from which any unitary operation can be approximated to arbitrary precision. Common examples: {H, T, CNOT} or {Rz, Ry, CNOT}. The Solovay-Kitaev theorem guarantees efficient approximation.",
    intuitiveExplanation:
      "A 'quantum alphabet' — a small set of gates that can build ANY quantum operation, just like you can spell any word with 26 letters. Different hardware uses different universal sets, but they're all equivalent in power.",
    relatedTerms: ["hadamard", "cnot", "circuit_depth"],
    categoryId: "gates",
  },
  {
    id: "circuit_depth",
    name: "Circuit Depth",
    formalDefinition:
      "The number of time steps (layers of parallel gates) required to execute a quantum circuit. Depth determines the circuit's vulnerability to decoherence — deeper circuits accumulate more noise.",
    intuitiveExplanation:
      "How many 'ticks of the clock' a quantum circuit takes. Shallower circuits finish faster and lose less information to noise. In NISQ-era computing, circuit depth is the main bottleneck.",
    relatedTerms: ["decoherence", "nisq", "transpilation"],
    categoryId: "gates",
  },
];
