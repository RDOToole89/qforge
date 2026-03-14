import type { GlossaryCategory, GlossaryTerm } from "../types";

export const category: GlossaryCategory = {
  id: "bloch_sphere",
  name: "The Bloch Sphere",
  icon: "globe",
  color: "#8b5cf6",
  description: "Geometric representation of single-qubit states",
};

export const terms: GlossaryTerm[] = [
  {
    id: "bloch_sphere",
    name: "Bloch Sphere",
    formalDefinition:
      "A unit sphere in ℝ³ that provides a geometric representation of a single qubit's state. Pure states lie on the surface, mixed states in the interior. Any single-qubit density matrix can be written ρ = (I + r·σ)/2 where r is the Bloch vector and σ = (σₓ, σᵧ, σ_z).",
    intuitiveExplanation:
      "A 3D globe where every point represents a possible qubit state. North pole = |0⟩, south pole = |1⟩, equator = equal superpositions with different phases. Noise shrinks the sphere inward (toward the maximally mixed center).",
    symbol: "S²",
    relatedTerms: ["bloch_vector", "pure_state", "mixed_state", "pauli_x"],
    categoryId: "bloch_sphere",
  },
  {
    id: "bloch_vector",
    name: "Bloch Vector",
    formalDefinition:
      "A real 3-vector r = (rₓ, rᵧ, r_z) = (⟨X⟩, ⟨Y⟩, ⟨Z⟩) that uniquely identifies a single-qubit state. For pure states |r| = 1 (surface of Bloch sphere), for mixed states |r| < 1 (interior). The maximally mixed state has r = (0,0,0).",
    intuitiveExplanation:
      "The 'address' of a qubit state on the Bloch sphere. Its three components are the expectation values of the Pauli operators. Noise shrinks the vector toward the origin.",
    symbol: "r = (rₓ, rᵧ, r_z)",
    relatedTerms: ["bloch_sphere", "pauli_x", "pauli_y", "pauli_z", "purity"],
    categoryId: "bloch_sphere",
  },
  {
    id: "bloch_ball",
    name: "Bloch Ball",
    formalDefinition:
      "The solid ball of radius 1 in ℝ³ that represents all possible single-qubit states (pure and mixed). The surface (Bloch sphere) contains pure states; the interior contains mixed states. CPTP maps contract or preserve the Bloch ball.",
    intuitiveExplanation:
      "The full 3D volume inside the Bloch sphere. Pure states are on the skin; as noise increases, states move inward. CPTP maps can only shrink or preserve this ball — never expand it. This is the contractivity property.",
    relatedTerms: ["bloch_sphere", "cptp_map", "mixed_state", "contractivity"],
    categoryId: "bloch_sphere",
  },
  {
    id: "poles",
    name: "Poles of the Bloch Sphere",
    formalDefinition:
      "The north pole (0,0,1) represents |0⟩ and the south pole (0,0,-1) represents |1⟩ on the Z-axis. The ±X poles represent |+⟩ and |−⟩; the ±Y poles represent |+i⟩ and |−i⟩. Each axis pair corresponds to eigenstates of a Pauli operator.",
    intuitiveExplanation:
      "The six special points on the Bloch sphere: Z-axis = computational basis (|0⟩/|1⟩), X-axis = Hadamard basis (|+⟩/|−⟩), Y-axis = circular basis. Each Pauli gate rotates 180° around its axis.",
    relatedTerms: ["bloch_sphere", "basis_states", "pauli_x", "pauli_z"],
    categoryId: "bloch_sphere",
  },
  {
    id: "ptm",
    name: "Pauli Transfer Matrix",
    formalDefinition:
      "A 4×4 real matrix representing a single-qubit quantum channel in the Pauli basis {I, X, Y, Z}. For a channel ε, the PTM elements are Rᵢⱼ = Tr(σᵢ ε(σⱼ))/2. The first row is always [1,0,0,0] for trace-preserving maps.",
    intuitiveExplanation:
      "A compact way to see what a noise channel does to each Bloch sphere direction. The diagonal tells you how much each axis shrinks; off-diagonal elements show mixing between axes. In our visualizer, you can watch the PTM update as you change the error rate.",
    symbol: "R",
    relatedTerms: ["cptp_map", "bloch_vector", "depolarizing_channel"],
    categoryId: "bloch_sphere",
  },
  {
    id: "contractivity",
    name: "Contractivity",
    formalDefinition:
      "A property of CPTP maps: they cannot increase the trace distance between any two quantum states. Geometrically, CPTP maps map the Bloch ball into a subset of itself (never expanding it).",
    intuitiveExplanation:
      "Quantum noise can only shrink or preserve the Bloch ball — never inflate it. This is why the orange (noisy) point cloud in the visualizer is always inside the blue (original) cloud.",
    relatedTerms: ["cptp_map", "bloch_ball", "trace_distance"],
    categoryId: "bloch_sphere",
  },
];
