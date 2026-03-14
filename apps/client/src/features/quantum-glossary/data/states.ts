import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "states",
  name: "Quantum States",
  icon: "layer-group",
  color: "#10b981",
  description: "Important multi-qubit states and their properties",
};

export const terms: GlossaryTerm[] = [
  {
    id: "bell_states",
    name: "Bell States",
    formalDefinition:
      "The four maximally entangled two-qubit states: |Φ+⟩ = (|00⟩+|11⟩)/√2, |Φ−⟩ = (|00⟩−|11⟩)/√2, |Ψ+⟩ = (|01⟩+|10⟩)/√2, |Ψ−⟩ = (|01⟩−|10⟩)/√2. They form an orthonormal basis for the two-qubit Hilbert space.",
    intuitiveExplanation:
      "The simplest entangled states — two qubits perfectly correlated. Measure one and you instantly know the other. |Φ+⟩ is the most common: both qubits always agree (both 0 or both 1).",
    symbol: "|Φ+⟩, |Ψ−⟩",
    relatedTerms: ["entanglement", "ghz_state", "cnot", "epr_pair"],
    categoryId: "states",
  },
  {
    id: "ghz_state",
    name: "GHZ State",
    formalDefinition:
      "The Greenberger-Horne-Zeilinger state for n qubits: |GHZ⟩ = (|00...0⟩ + |11...1⟩)/√2. A maximally entangled state with perfect ZZ correlations. The multi-qubit generalization of the Bell state |Φ+⟩.",
    intuitiveExplanation:
      "All qubits are either ALL 0 or ALL 1 — nothing in between. This extreme correlation makes GHZ the best probe for detecting Z-basis noise. In our framework, GHZ achieved 9/9 detections of correlated noise.",
    symbol: "|GHZ⟩",
    relatedTerms: ["bell_states", "w_state", "entanglement", "zz_correlator"],
    categoryId: "states",
  },
  {
    id: "w_state",
    name: "W State",
    formalDefinition:
      "An entangled n-qubit state with exactly one excitation distributed equally: |W⟩ = (|100...0⟩ + |010...0⟩ + ... + |000...1⟩)/√n. Unlike GHZ, W-state entanglement is robust to single-qubit loss.",
    intuitiveExplanation:
      "Exactly one qubit is 'excited' (|1⟩) but you don't know which — the excitation is spread evenly. W states are resilient: lose one qubit and the rest stay entangled. However, their weak ZZ correlations make them poor Z-basis noise probes (0/9 detections in our study).",
    symbol: "|W⟩",
    relatedTerms: ["ghz_state", "entanglement", "hamming_weight"],
    categoryId: "states",
  },
  {
    id: "cluster_state",
    name: "Cluster State",
    formalDefinition:
      "A graph state created by applying CZ gates between qubits connected by edges of a graph, starting from |+⟩⊗n. Stabilized by operators Kₐ = Xₐ∏_{b∈N(a)} Z_b. The resource state for measurement-based quantum computation.",
    intuitiveExplanation:
      "Qubits entangled in a grid pattern via CZ gates. The entanglement lives in 'stabilizer' correlators (XZ, ZXZ) rather than simple ZZ — which is why cluster states show exactly ZERO signal in Z-basis measurements. This is the Pauli invariance theorem in action.",
    symbol: "|C⟩",
    relatedTerms: ["cz_gate", "pauli_invariance", "stabilizer", "graph_state"],
    categoryId: "states",
  },
  {
    id: "product_state",
    name: "Product State",
    formalDefinition:
      "A multi-qubit state that can be written as a tensor product of individual qubit states: |ψ⟩ = |ψ₁⟩ ⊗ |ψ₂⟩ ⊗ ... ⊗ |ψₙ⟩. Contains no entanglement between any subsystems.",
    intuitiveExplanation:
      "Each qubit is independent — knowing about one tells you nothing about the others. The equal superposition state |+⟩⊗n is a product state: every qubit is in its own superposition, with no correlations.",
    relatedTerms: ["entanglement", "tensor_product", "separable_state"],
    categoryId: "states",
  },
  {
    id: "pure_state",
    name: "Pure State",
    formalDefinition:
      "A quantum state that can be described by a single state vector |ψ⟩ ∈ ℋ. Equivalently, a state with density matrix ρ = |ψ⟩⟨ψ| satisfying Tr(ρ²) = 1 (maximum purity).",
    intuitiveExplanation:
      "A state with no classical uncertainty — you know exactly what quantum state the system is in. A qubit pointing at a specific spot on the Bloch sphere surface is pure. Noise turns pure states into mixed states.",
    symbol: "|ψ⟩",
    relatedTerms: ["mixed_state", "density_matrix", "purity", "bloch_sphere"],
    categoryId: "states",
  },
  {
    id: "mixed_state",
    name: "Mixed State",
    formalDefinition:
      "A statistical ensemble of pure states, described by a density matrix ρ = Σᵢ pᵢ|ψᵢ⟩⟨ψᵢ| where pᵢ are classical probabilities. Satisfies Tr(ρ²) < 1 (except for pure states). Cannot be represented by a single state vector.",
    intuitiveExplanation:
      "A state with classical uncertainty — you don't know which pure state the system is in. Inside the Bloch ball (not on the surface). The maximally mixed state ρ = I/2 is at the center of the Bloch ball, representing complete ignorance.",
    symbol: "ρ",
    relatedTerms: ["pure_state", "density_matrix", "purity", "decoherence"],
    categoryId: "states",
  },
  {
    id: "graph_state",
    name: "Graph State",
    formalDefinition:
      "A quantum state associated with a graph G = (V, E), prepared by initializing all qubits in |+⟩ and applying CZ gates along each edge. Stabilized by Kᵥ = Xᵥ ∏_{u∈N(v)} Z_u for each vertex v.",
    intuitiveExplanation:
      "A state whose entanglement structure mirrors a graph — qubits are nodes, CZ gates create edges. Cluster states are graph states on a grid. The graph determines which correlators are non-zero.",
    relatedTerms: ["cluster_state", "cz_gate", "stabilizer", "entanglement_topology"],
    categoryId: "states",
  },
];
