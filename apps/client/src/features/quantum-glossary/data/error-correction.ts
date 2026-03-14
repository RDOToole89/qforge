import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "error_correction",
  name: "Quantum Error Correction",
  icon: "shield",
  color: "#22c55e",
  description: "Protecting quantum information from noise",
};

export const terms: GlossaryTerm[] = [
  {
    id: "stabilizer",
    name: "Stabilizer",
    formalDefinition:
      "An element of the stabilizer group S of a quantum code: S is an abelian subgroup of the n-qubit Pauli group such that every state |ψ⟩ in the code space satisfies g|ψ⟩ = |ψ⟩ for all g ∈ S. Stabilizer measurement detects errors without collapsing the encoded state.",
    intuitiveExplanation:
      "An operator that 'checks' whether errors have occurred without revealing the encoded information. Like a parity check in classical coding — it tells you something went wrong without telling you the message. Cluster state correlators (XZ, ZXZ) are stabilizers.",
    relatedTerms: ["syndrome", "cluster_state", "surface_code", "logical_qubit"],
    categoryId: "error_correction",
  },
  {
    id: "syndrome",
    name: "Error Syndrome",
    formalDefinition:
      "The pattern of stabilizer measurement outcomes that identifies which error occurred. For an n-qubit stabilizer code with k logical qubits, there are n−k syndrome bits. Different errors produce different syndromes, enabling correction.",
    intuitiveExplanation:
      "A 'diagnosis' of what went wrong. Measure the stabilizers and the pattern of +1s and −1s tells you which error happened — like symptoms telling a doctor the disease. Then you can apply the right correction.",
    relatedTerms: ["stabilizer", "logical_qubit"],
    categoryId: "error_correction",
  },
  {
    id: "logical_qubit",
    name: "Logical Qubit",
    formalDefinition:
      "A qubit encoded in a multi-qubit error-correcting code. The logical |0⟩_L and |1⟩_L are states in the code space (common +1 eigenspace of all stabilizers). Protected against errors up to the code distance d: can correct ⌊(d−1)/2⌋ errors.",
    intuitiveExplanation:
      "A 'armored' qubit made from many physical qubits. The redundancy allows detecting and correcting errors. Like writing a message on three pieces of paper — if one gets smudged, the other two can reconstruct the original.",
    symbol: "|0⟩_L, |1⟩_L",
    relatedTerms: ["stabilizer", "surface_code", "threshold_theorem"],
    categoryId: "error_correction",
  },
  {
    id: "surface_code",
    name: "Surface Code",
    formalDefinition:
      "A topological stabilizer code defined on a 2D lattice. Uses X-type and Z-type stabilizers on faces and vertices. Code distance d requires a d×d lattice. Threshold error rate ~1%. Leading candidate for fault-tolerant quantum computing.",
    intuitiveExplanation:
      "The leading error correction scheme — qubits arranged in a grid with stabilizer checks on every face and vertex. If errors are rare enough (below ~1% per gate), the surface code can correct them faster than they occur. This is the path to large-scale quantum computing.",
    relatedTerms: ["stabilizer", "threshold_theorem", "logical_qubit"],
    categoryId: "error_correction",
  },
  {
    id: "threshold_theorem",
    name: "Threshold Theorem",
    formalDefinition:
      "If the error rate per gate is below a threshold p_th, arbitrary-length quantum computations can be performed with arbitrary accuracy using polynomial overhead in the number of physical qubits. For the surface code, p_th ≈ 1%.",
    intuitiveExplanation:
      "The 'existence proof' for reliable quantum computing. Below a critical noise rate, you can make computations as long and accurate as you want by adding more physical qubits. Above the threshold, errors multiply faster than you can correct them.",
    symbol: "p < p_th",
    relatedTerms: ["surface_code", "logical_qubit", "decoherence"],
    categoryId: "error_correction",
  },
  {
    id: "code_distance",
    name: "Code Distance",
    formalDefinition:
      "The minimum weight of a non-trivial logical operator in a quantum error-correcting code. A code with distance d can detect up to d−1 errors and correct up to ⌊(d−1)/2⌋ errors. Often denoted in the [[n, k, d]] notation.",
    intuitiveExplanation:
      "How many physical qubits an error must corrupt to cause an undetectable logical error. Higher distance = more protection, but requires more physical qubits. A distance-3 code corrects any single-qubit error.",
    symbol: "d",
    relatedTerms: ["logical_qubit", "stabilizer", "surface_code"],
    categoryId: "error_correction",
  },
];
