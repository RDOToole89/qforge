import type { GlossaryCategory, GlossaryTerm } from "../types";
import { viz } from "@/src/design/tokens";

export const category: GlossaryCategory = {
  id: "states",
  name: "Quantum States",
  icon: "layer-group",
  color: viz.emeraldDeep,
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
    keyEquation:
      "|\\Phi^\\pm\\rangle = \\frac{|00\\rangle \\pm |11\\rangle}{\\sqrt{2}}, \\quad |\\Psi^\\pm\\rangle = \\frac{|01\\rangle \\pm |10\\rangle}{\\sqrt{2}}",
    formulaExplanation:
      "Four maximally entangled two-qubit states. Φ states have matching bits (00 and 11), Ψ states have opposite bits (01 and 10). The ± sign is a relative phase — invisible to Z-basis measurement but physically distinct.",
    symbolAnnotations: {
      "Φ": "Phi — Bell states where both qubits match (00 and 11)",
      "Ψ": "Psi — Bell states where qubits differ (01 and 10)",
      "±": "Relative phase — invisible to Z-measurement but physically distinct",
      "00": "Both qubits measured as 0",
      "11": "Both qubits measured as 1",
      "01": "First qubit 0, second qubit 1",
      "10": "First qubit 1, second qubit 0",
      "√2": "Normalization factor — ensures probabilities sum to 1",
    },
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
    keyEquation:
      "|\\text{GHZ}\\rangle = \\frac{|00\\cdots0\\rangle + |11\\cdots1\\rangle}{\\sqrt{2}}",
    formulaExplanation:
      "An equal superposition of all-zeros and all-ones. Only two terms out of 2\u207F possibilities — maximally entangled but also maximally fragile. A single bit flip on any qubit is detectable because it breaks the all-same pattern.",
    symbolAnnotations: {
      "GHZ": "Greenberger–Horne–Zeilinger: the discoverers of this state",
      "00⋯0": "All n qubits in state 0 — one branch of the superposition",
      "11⋯1": "All n qubits in state 1 — the other branch",
      "√2": "Normalization factor — ensures total probability sums to 1",
    },
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
    keyEquation:
      "|W\\rangle = \\frac{1}{\\sqrt{n}}(|10\\cdots0\\rangle + |01\\cdots0\\rangle + \\cdots + |00\\cdots1\\rangle)",
    formulaExplanation:
      "Exactly one qubit is |1\u27E9, spread equally across all positions. The 1/\u221An normalization ensures probabilities sum to 1. Losing one qubit leaves the rest still entangled — unlike GHZ, which collapses entirely.",
    symbolAnnotations: {
      "W": "The W state — named for its shape when written for 3 qubits",
      "√n": "Normalization: dividing by √n ensures probabilities sum to 1",
      "10⋯0": "First qubit excited (|1⟩), all others ground (|0⟩)",
      "01⋯0": "Second qubit excited, all others ground",
      "00⋯1": "Last qubit excited, all others ground",
      "⋯": "All n permutations with exactly one qubit in |1⟩",
    },
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
    keyEquation:
      "|C\\rangle = \\prod_{(a,b) \\in E} CZ_{ab} \\, |+\\rangle^{\\otimes n}",
    formulaExplanation:
      "Start with all qubits in |+\u27E9 (equal superposition), then apply CZ gates along each edge of a graph. The entanglement pattern mirrors the graph structure. This is the universal resource for measurement-based quantum computing.",
    symbolAnnotations: {
      "CZ": "Controlled-Z gate — entangles two qubits via a phase flip",
      "ab": "Qubit pair (a, b) connected by an edge in the graph",
      "∈E": "For every edge in the graph's edge set E",
      "⊗n": "Tensor product of n copies — one |+⟩ per qubit",
    },
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
    keyEquation:
      "\\rho = |\\psi\\rangle\\langle\\psi|, \\quad \\text{Tr}(\\rho^2) = 1",
    formulaExplanation:
      "A pure state's density matrix is a rank-1 projector — it projects onto a single direction in Hilbert space. Purity Tr(\u03C1\u00B2) = 1 confirms there's no classical uncertainty. Any point on the Bloch sphere surface is a pure state.",
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
    keyEquation:
      "\\rho = \\sum_i p_i |\\psi_i\\rangle\\langle\\psi_i|, \\quad \\text{Tr}(\\rho^2) < 1",
    formulaExplanation:
      "A classical mixture of pure states weighted by probabilities p\u1D62. The purity is strictly less than 1, meaning there's genuine classical uncertainty about which pure state the system is in. Represented by points inside the Bloch ball.",
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
