/**
 * Bloch sphere dot configurations for quantum glossary terms.
 * Each entry maps a glossary term ID to the dots and caption shown on its mini Bloch sphere.
 *
 * Dot colors are physics/data colors and come exclusively from the `viz`
 * design-token palette (single source of truth) — never hard-coded hex.
 */

import { viz } from "@/src/design/tokens";

/** A dot rendered on the Bloch sphere */
export interface BlochDot {
  rx: number;
  ry: number;
  rz: number;
  color: string;
  label?: string;
}

export const STATE_BLOCH_CONFIGS: Record<string, { dots: BlochDot[]; caption: string }> = {
  // ── Quantum States ──
  ghz_state: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: viz.indigo, label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  w_state: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: viz.emerald, label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  bell_states: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: viz.pink, label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  cluster_state: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: viz.amber, label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  product_state: {
    dots: [{ rx: 1, ry: 0, rz: 0, color: viz.sky, label: "|+⟩" }],
    caption: "Pure |+⟩ state",
  },
  pure_state: {
    dots: [{ rx: 0, ry: 0, rz: 1, color: viz.violet, label: "|0⟩" }],
    caption: "On surface: pure",
  },
  mixed_state: {
    dots: [{ rx: 0.3, ry: 0.2, rz: 0.3, color: viz.muted, label: "ρ" }],
    caption: "Inside ball: mixed",
  },
  graph_state: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: viz.amber, label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  epr_pair: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: viz.pink, label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  separable_state: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.sky, label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.amber, label: "|1⟩" },
    ],
    caption: "Independent qubits",
  },

  // ── Fundamentals ──
  qubit: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "|1⟩" },
      { rx: 0.7, ry: 0, rz: 0.7, color: viz.sky, label: "|ψ⟩" },
    ],
    caption: "Any point on surface",
  },
  superposition: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "|+⟩" },
      { rx: -1, ry: 0, rz: 0, color: viz.amber, label: "|−⟩" },
    ],
    caption: "Equator = superposition",
  },
  born_rule: {
    dots: [
      { rx: 0.5, ry: 0, rz: 0.87, color: viz.violet, label: "|ψ⟩" },
    ],
    caption: "P(0) = cos²(θ/2)",
  },
  probability_amplitude: {
    dots: [
      { rx: 0.71, ry: 0.71, rz: 0, color: viz.indigo, label: "α,β" },
    ],
    caption: "|α|² + |β|² = 1",
  },

  // ── Gates (show rotation axis) ──
  pauli_x: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.mutedDim, label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "X|0⟩" },
    ],
    caption: "π rotation about X",
  },
  pauli_y: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.mutedDim, label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.emerald, label: "Y|0⟩" },
    ],
    caption: "π rotation about Y",
  },
  pauli_z: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "|+⟩" },
      { rx: -1, ry: 0, rz: 0, color: viz.amber, label: "Z|+⟩" },
    ],
    caption: "π rotation about Z",
  },
  hadamard: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.mutedDim, label: "|0⟩" },
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "H|0⟩" },
    ],
    caption: "Maps Z→X axis",
  },
  cnot: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "ctrl" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "tgt" },
    ],
    caption: "Entangling gate",
  },
  cz_gate: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "q₀" },
      { rx: 0, ry: 0, rz: 1, color: viz.amber, label: "q₁" },
    ],
    caption: "Symmetric phase",
  },

  // ── Bloch Sphere ──
  bloch_sphere: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "|1⟩" },
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "|+⟩" },
    ],
    caption: "ρ = (I + r·σ)/2",
  },
  bloch_vector: {
    dots: [
      { rx: 0.6, ry: 0.3, rz: 0.74, color: viz.indigo, label: "r" },
    ],
    caption: "|r| ≤ 1",
  },
  ptm: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0, color: viz.sky, label: "in" },
      { rx: 0.5, ry: 0, rz: 0, color: viz.pink, label: "out" },
    ],
    caption: "Maps Bloch vectors",
  },
  contractivity: {
    dots: [
      { rx: 0.9, ry: 0, rz: 0, color: viz.sky, label: "before" },
      { rx: 0.5, ry: 0, rz: 0, color: viz.pink, label: "after" },
    ],
    caption: "Ball contracts",
  },

  // ── Density Matrices ──
  density_matrix: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "pure" },
      { rx: 0, ry: 0, rz: 0, color: viz.muted, label: "I/2" },
    ],
    caption: "ρ encodes state",
  },
  purity: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "γ=1" },
      { rx: 0.4, ry: 0.2, rz: 0.3, color: viz.muted, label: "γ<1" },
    ],
    caption: "γ = Tr(ρ²)",
  },
  partial_trace: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.indigo, label: "ρ_A" },
    ],
    caption: "Trace out B",
  },
  trace: {
    dots: [
      { rx: 0, ry: 0, rz: 0.8, color: viz.violet, label: "Tr=1" },
    ],
    caption: "Tr(ρ) = 1",
  },

  // ── Entanglement Measures ──
  entanglement: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.pink, label: "ρ_A" },
    ],
    caption: "Subsystem is mixed",
  },
  concurrence: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.pink, label: "C=1" },
      { rx: 0, ry: 0, rz: 1, color: viz.sky, label: "C=0" },
    ],
    caption: "0→pure, 1→max ent.",
  },
  entanglement_entropy: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.pink, label: "S=1" },
      { rx: 0, ry: 0, rz: 1, color: viz.sky, label: "S=0" },
    ],
    caption: "S(ρ_A) entropy",
  },
  zz_correlator: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "↑↑" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "↑↓" },
    ],
    caption: "⟨Z₁Z₂⟩ = ±1",
  },

  // ── Decoherence ──
  t1_time: {
    dots: [
      { rx: 0.5, ry: 0.5, rz: 0.7, color: viz.sky, label: "t=0" },
      { rx: 0, ry: 0, rz: 1, color: viz.pink, label: "t→∞" },
    ],
    caption: "Decays to |0⟩",
  },
  t2_time: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "t=0" },
      { rx: 0, ry: 0, rz: 0, color: viz.pink, label: "t→∞" },
    ],
    caption: "Coherence → 0",
  },

  // ── Noise Channels ──
  depolarizing_channel: {
    dots: [
      { rx: 0.9, ry: 0, rz: 0, color: viz.sky, label: "in" },
      { rx: 0.3, ry: 0, rz: 0, color: viz.pink, label: "out" },
      { rx: 0, ry: 0, rz: 0, color: viz.muted, label: "I/2" },
    ],
    caption: "Shrinks to center",
  },
  bit_flip_channel: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.sky, label: "in" },
      { rx: 0, ry: 0, rz: 0.4, color: viz.pink, label: "out" },
    ],
    caption: "Z shrinks, X kept",
  },
  phase_flip_channel: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "in" },
      { rx: 0.4, ry: 0, rz: 0, color: viz.pink, label: "out" },
    ],
    caption: "X,Y shrink, Z kept",
  },

  // ── Structured Decoherence Metrics ──
  automorphism_invariance: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: viz.indigo, label: "AI" },
    ],
    caption: "Error asymmetry",
  },
  statistical_strength: {
    dots: [
      { rx: 0.5, ry: 0.3, rz: 0.5, color: viz.emerald, label: "SS" },
      { rx: 0, ry: 0, rz: 0, color: viz.muted, label: "null" },
    ],
    caption: "JSD from null",
  },
  peak_concentration_ratio: {
    dots: [
      { rx: 0, ry: 0, rz: 0.9, color: viz.amber, label: "peak" },
      { rx: 0, ry: 0, rz: -0.1, color: viz.muted, label: "tail" },
    ],
    caption: "Top vs bottom 25%",
  },
  empirical_error_correlation: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0, color: viz.pink, label: "MI" },
      { rx: 0, ry: 0.8, rz: 0, color: viz.indigo, label: "topo" },
    ],
    caption: "r(MI, topology)",
  },
  coherence_index: {
    dots: [
      { rx: 0, ry: 0, rz: 0.8, color: viz.violet, label: "CI" },
    ],
    caption: "Eigenvalue spread",
  },

  // ── Linear Algebra ──
  tensor_product: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "q₀" },
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "q₁" },
    ],
    caption: "Combined system",
  },
  unitary: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: viz.sky, label: "in" },
      { rx: -0.7, ry: 0, rz: 0.7, color: viz.pink, label: "U·in" },
    ],
    caption: "Rotation on surface",
  },
  hermitian: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "λ₁" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "λ₂" },
    ],
    caption: "Real eigenvalues",
  },
  eigenvalue: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "|e₁⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "|e₂⟩" },
    ],
    caption: "A|e⟩ = λ|e⟩",
  },
  inner_product: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: viz.sky, label: "|ψ⟩" },
      { rx: 0.5, ry: 0.5, rz: 0.7, color: viz.pink, label: "|φ⟩" },
    ],
    caption: "⟨φ|ψ⟩ = overlap",
  },
  spectral_decomposition: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "λ₁" },
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "λ₂" },
    ],
    caption: "A = Σλ|e⟩⟨e|",
  },
  commutator: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "X" },
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "Z" },
    ],
    caption: "[X,Z] ≠ 0",
  },
  dirac_notation: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "|ψ⟩" },
    ],
    caption: "Bra-ket notation",
  },

  // ── Measurement ──
  projective_measurement: {
    dots: [
      { rx: 0.5, ry: 0.3, rz: 0.8, color: viz.sky, label: "pre" },
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "post" },
    ],
    caption: "Projects to pole",
  },
  observable: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "+1" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "−1" },
    ],
    caption: "Eigenvalues = outcomes",
  },
  povm: {
    dots: [
      { rx: 0.6, ry: 0, rz: 0.8, color: viz.sky, label: "E₁" },
      { rx: -0.6, ry: 0, rz: -0.8, color: viz.pink, label: "E₂" },
    ],
    caption: "Generalized meas.",
  },

  // ── Information Theory ──
  shannon_entropy: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.muted, label: "H=1" },
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "H=0" },
    ],
    caption: "Max at center",
  },
  von_neumann_entropy: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.muted, label: "S=1" },
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "S=0" },
    ],
    caption: "S(ρ) = −Tr(ρlnρ)",
  },
  mutual_information: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.pink, label: "ρ_AB" },
    ],
    caption: "I(A:B) = shared info",
  },
  jensen_shannon_divergence: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: viz.sky, label: "P" },
      { rx: -0.7, ry: 0, rz: 0.7, color: viz.pink, label: "Q" },
    ],
    caption: "JSD(P‖Q)",
  },
  total_correlation: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.indigo, label: "TC" },
    ],
    caption: "Multi-information",
  },
  trace_distance: {
    dots: [
      { rx: 0.6, ry: 0, rz: 0.6, color: viz.sky, label: "ρ" },
      { rx: -0.6, ry: 0, rz: 0.6, color: viz.pink, label: "σ" },
    ],
    caption: "D(ρ,σ) = distance",
  },
  fidelity: {
    dots: [
      { rx: 0.5, ry: 0, rz: 0.87, color: viz.sky, label: "ρ" },
      { rx: 0.6, ry: 0.1, rz: 0.8, color: viz.pink, label: "σ" },
    ],
    caption: "F(ρ,σ) = overlap",
  },

  // ── Noise & Channels ──
  amplitude_damping: {
    dots: [
      { rx: 0.5, ry: 0.5, rz: -0.7, color: viz.sky, label: "t=0" },
      { rx: 0, ry: 0, rz: 1, color: viz.pink, label: "t→∞" },
    ],
    caption: "Decays to |0⟩",
  },
  dephasing: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "t=0" },
      { rx: 0, ry: 0, rz: 0, color: viz.pink, label: "t→∞" },
    ],
    caption: "X,Y → 0",
  },
  pauli_channel: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0.6, color: viz.sky, label: "in" },
      { rx: 0.3, ry: 0, rz: 0.3, color: viz.pink, label: "out" },
    ],
    caption: "Random Pauli errors",
  },
  bit_flip: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.sky, label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "flipped" },
    ],
    caption: "X error: |0⟩↔|1⟩",
  },
  phase_flip: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "|+⟩" },
      { rx: -1, ry: 0, rz: 0, color: viz.pink, label: "flipped" },
    ],
    caption: "Z error: phase flip",
  },
  kraus_operators: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0.6, color: viz.sky, label: "ρ" },
      { rx: 0.4, ry: 0, rz: 0.4, color: viz.pink, label: "ε(ρ)" },
    ],
    caption: "ε(ρ) = ΣK_i ρ K_i†",
  },
  cptp_map: {
    dots: [
      { rx: 0.9, ry: 0, rz: 0, color: viz.sky, label: "in" },
      { rx: 0.6, ry: 0, rz: 0, color: viz.pink, label: "out" },
    ],
    caption: "Trace-preserving",
  },
  open_quantum_system: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "system" },
      { rx: 0, ry: 0, rz: 0, color: viz.muted, label: "→mixed" },
    ],
    caption: "System + environment",
  },
  lindblad_equation: {
    dots: [
      { rx: 0.7, ry: 0.7, rz: 0, color: viz.sky, label: "t=0" },
      { rx: 0.2, ry: 0.2, rz: 0, color: viz.pink, label: "t>0" },
    ],
    caption: "dρ/dt = L[ρ]",
  },
  quantum_zeno_effect: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "frozen" },
    ],
    caption: "Frequent meas. freezes",
  },

  // ── Structured Decoherence (extra) ──
  structure_score: {
    dots: [
      { rx: 0.6, ry: 0.3, rz: 0.5, color: viz.emerald, label: "SS" },
      { rx: 0, ry: 0, rz: 0, color: viz.muted, label: "null" },
    ],
    caption: "JSD from null",
  },
  delta_cov_fingerprint: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0, color: viz.indigo, label: "ΔCov" },
    ],
    caption: "Error signature",
  },
  fingerprint_trajectory: {
    dots: [
      { rx: 0.9, ry: 0, rz: 0, color: viz.sky, label: "t₁" },
      { rx: 0.5, ry: 0.3, rz: 0, color: viz.indigo, label: "t₂" },
      { rx: 0.2, ry: 0.1, rz: 0, color: viz.pink, label: "t₃" },
    ],
    caption: "Path through space",
  },
  decoherence_flow_generator: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0.6, color: viz.sky, label: "flow" },
      { rx: 0, ry: 0, rz: 0, color: viz.muted, label: "sink" },
    ],
    caption: "Decoherence flow",
  },
  correlators: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "⟨ZZ⟩" },
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "⟨XX⟩" },
    ],
    caption: "Pauli correlators",
  },

  // ── Algorithms ──
  grover_search: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: viz.muted, label: "start" },
      { rx: 0, ry: 0, rz: 1, color: viz.emerald, label: "target" },
    ],
    caption: "Amplitude boost",
  },
  quantum_fourier_transform: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.sky, label: "|x⟩" },
      { rx: 0.7, ry: 0.7, rz: 0, color: viz.pink, label: "QFT|x⟩" },
    ],
    caption: "Phase encoding",
  },
  quantum_simulation: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: viz.indigo, label: "H" },
    ],
    caption: "e^{−iHt} evolution",
  },
  vqe: {
    dots: [
      { rx: 0.5, ry: 0.3, rz: 0.8, color: viz.emerald, label: "θ*" },
    ],
    caption: "Variational ansatz",
  },

  // ── Error Correction ──
  stabilizer: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "+1" },
    ],
    caption: "S|ψ⟩ = +|ψ⟩",
  },
  logical_qubit: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.emerald, label: "|0_L⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "|1_L⟩" },
    ],
    caption: "Encoded in n qubits",
  },
  threshold_theorem: {
    dots: [
      { rx: 0, ry: 0, rz: 0.95, color: viz.emerald, label: "below" },
      { rx: 0, ry: 0, rz: 0.3, color: viz.pink, label: "above" },
    ],
    caption: "p < p_th → correctable",
  },

  // ── Hardware ──
  quantum_volume: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: viz.indigo, label: "QV" },
    ],
    caption: "Device benchmark",
  },
  gate_fidelity: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: viz.sky, label: "ideal" },
      { rx: 0.6, ry: 0.1, rz: 0.6, color: viz.pink, label: "actual" },
    ],
    caption: "F(U_ideal, U_real)",
  },

  // ── Misc ──
  berry_phase: {
    dots: [
      { rx: 0.7, ry: 0.7, rz: 0, color: viz.indigo, label: "path" },
    ],
    caption: "Geometric phase",
  },
  bell_inequality: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.pink, label: "ρ_AB" },
    ],
    caption: "S > 2 → entangled",
  },
  chsh: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: viz.pink, label: "ρ_AB" },
    ],
    caption: "S ≤ 2√2",
  },
  pauli_transfer_matrix: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0, color: viz.sky, label: "in" },
      { rx: 0.5, ry: 0, rz: 0, color: viz.pink, label: "out" },
    ],
    caption: "4×4 real matrix",
  },
  hilbert_space: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.violet, label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: viz.pink, label: "|1⟩" },
      { rx: 1, ry: 0, rz: 0, color: viz.sky, label: "|+⟩" },
    ],
    caption: "ℂ^{2ⁿ} state space",
  },

  // ── Reconfiguration Space ──
  sx_gate: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: viz.mutedDim, label: "|0⟩" },
      { rx: 0, ry: -1, rz: 0, color: viz.pink, label: "√X|0⟩" },
    ],
    caption: "π/2 rotation about X",
  },
};
