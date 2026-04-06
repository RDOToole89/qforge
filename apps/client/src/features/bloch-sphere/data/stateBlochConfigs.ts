/**
 * Bloch sphere dot configurations for quantum glossary terms.
 * Each entry maps a glossary term ID to the dots and caption shown on its mini Bloch sphere.
 */

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
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#818cf8", label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  w_state: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#34d399", label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  bell_states: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  cluster_state: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#fb923c", label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  product_state: {
    dots: [{ rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "|+⟩" }],
    caption: "Pure |+⟩ state",
  },
  pure_state: {
    dots: [{ rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "|0⟩" }],
    caption: "On surface: pure",
  },
  mixed_state: {
    dots: [{ rx: 0.3, ry: 0.2, rz: 0.3, color: "#94a3b8", label: "ρ" }],
    caption: "Inside ball: mixed",
  },
  graph_state: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#fb923c", label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  epr_pair: {
    dots: [{ rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "mixed" }],
    caption: "Each qubit: I/2",
  },
  separable_state: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#38bdf8", label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#fb923c", label: "|1⟩" },
    ],
    caption: "Independent qubits",
  },

  // ── Fundamentals ──
  qubit: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "|1⟩" },
      { rx: 0.7, ry: 0, rz: 0.7, color: "#38bdf8", label: "|ψ⟩" },
    ],
    caption: "Any point on surface",
  },
  superposition: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "|+⟩" },
      { rx: -1, ry: 0, rz: 0, color: "#fb923c", label: "|−⟩" },
    ],
    caption: "Equator = superposition",
  },
  born_rule: {
    dots: [
      { rx: 0.5, ry: 0, rz: 0.87, color: "#a78bfa", label: "|ψ⟩" },
    ],
    caption: "P(0) = cos²(θ/2)",
  },
  probability_amplitude: {
    dots: [
      { rx: 0.71, ry: 0.71, rz: 0, color: "#818cf8", label: "α,β" },
    ],
    caption: "|α|² + |β|² = 1",
  },

  // ── Gates (show rotation axis) ──
  pauli_x: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#64748b", label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "X|0⟩" },
    ],
    caption: "π rotation about X",
  },
  pauli_y: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#64748b", label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#34d399", label: "Y|0⟩" },
    ],
    caption: "π rotation about Y",
  },
  pauli_z: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "|+⟩" },
      { rx: -1, ry: 0, rz: 0, color: "#fb923c", label: "Z|+⟩" },
    ],
    caption: "π rotation about Z",
  },
  hadamard: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#64748b", label: "|0⟩" },
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "H|0⟩" },
    ],
    caption: "Maps Z→X axis",
  },
  cnot: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "ctrl" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "tgt" },
    ],
    caption: "Entangling gate",
  },
  cz_gate: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "q₀" },
      { rx: 0, ry: 0, rz: 1, color: "#fb923c", label: "q₁" },
    ],
    caption: "Symmetric phase",
  },

  // ── Bloch Sphere ──
  bloch_sphere: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "|1⟩" },
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "|+⟩" },
    ],
    caption: "ρ = (I + r·σ)/2",
  },
  bloch_vector: {
    dots: [
      { rx: 0.6, ry: 0.3, rz: 0.74, color: "#818cf8", label: "r" },
    ],
    caption: "|r| ≤ 1",
  },
  ptm: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0, color: "#38bdf8", label: "in" },
      { rx: 0.5, ry: 0, rz: 0, color: "#f472b6", label: "out" },
    ],
    caption: "Maps Bloch vectors",
  },
  contractivity: {
    dots: [
      { rx: 0.9, ry: 0, rz: 0, color: "#38bdf8", label: "before" },
      { rx: 0.5, ry: 0, rz: 0, color: "#f472b6", label: "after" },
    ],
    caption: "Ball contracts",
  },

  // ── Density Matrices ──
  density_matrix: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "pure" },
      { rx: 0, ry: 0, rz: 0, color: "#94a3b8", label: "I/2" },
    ],
    caption: "ρ encodes state",
  },
  purity: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "γ=1" },
      { rx: 0.4, ry: 0.2, rz: 0.3, color: "#94a3b8", label: "γ<1" },
    ],
    caption: "γ = Tr(ρ²)",
  },
  partial_trace: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#818cf8", label: "ρ_A" },
    ],
    caption: "Trace out B",
  },
  trace: {
    dots: [
      { rx: 0, ry: 0, rz: 0.8, color: "#a78bfa", label: "Tr=1" },
    ],
    caption: "Tr(ρ) = 1",
  },

  // ── Entanglement Measures ──
  entanglement: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "ρ_A" },
    ],
    caption: "Subsystem is mixed",
  },
  concurrence: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "C=1" },
      { rx: 0, ry: 0, rz: 1, color: "#38bdf8", label: "C=0" },
    ],
    caption: "0→pure, 1→max ent.",
  },
  entanglement_entropy: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "S=1" },
      { rx: 0, ry: 0, rz: 1, color: "#38bdf8", label: "S=0" },
    ],
    caption: "S(ρ_A) entropy",
  },
  zz_correlator: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "↑↑" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "↑↓" },
    ],
    caption: "⟨Z₁Z₂⟩ = ±1",
  },

  // ── Decoherence ──
  t1_time: {
    dots: [
      { rx: 0.5, ry: 0.5, rz: 0.7, color: "#38bdf8", label: "t=0" },
      { rx: 0, ry: 0, rz: 1, color: "#f472b6", label: "t→∞" },
    ],
    caption: "Decays to |0⟩",
  },
  t2_time: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "t=0" },
      { rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "t→∞" },
    ],
    caption: "Coherence → 0",
  },

  // ── Noise Channels ──
  depolarizing_channel: {
    dots: [
      { rx: 0.9, ry: 0, rz: 0, color: "#38bdf8", label: "in" },
      { rx: 0.3, ry: 0, rz: 0, color: "#f472b6", label: "out" },
      { rx: 0, ry: 0, rz: 0, color: "#94a3b8", label: "I/2" },
    ],
    caption: "Shrinks to center",
  },
  bit_flip_channel: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#38bdf8", label: "in" },
      { rx: 0, ry: 0, rz: 0.4, color: "#f472b6", label: "out" },
    ],
    caption: "Z shrinks, X kept",
  },
  phase_flip_channel: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "in" },
      { rx: 0.4, ry: 0, rz: 0, color: "#f472b6", label: "out" },
    ],
    caption: "X,Y shrink, Z kept",
  },

  // ── Structured Decoherence Metrics ──
  automorphism_invariance: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: "#818cf8", label: "AI" },
    ],
    caption: "Error asymmetry",
  },
  statistical_strength: {
    dots: [
      { rx: 0.5, ry: 0.3, rz: 0.5, color: "#34d399", label: "SS" },
      { rx: 0, ry: 0, rz: 0, color: "#94a3b8", label: "null" },
    ],
    caption: "JSD from null",
  },
  peak_concentration_ratio: {
    dots: [
      { rx: 0, ry: 0, rz: 0.9, color: "#fb923c", label: "peak" },
      { rx: 0, ry: 0, rz: -0.1, color: "#94a3b8", label: "tail" },
    ],
    caption: "Top vs bottom 25%",
  },
  empirical_error_correlation: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0, color: "#f472b6", label: "MI" },
      { rx: 0, ry: 0.8, rz: 0, color: "#818cf8", label: "topo" },
    ],
    caption: "r(MI, topology)",
  },
  coherence_index: {
    dots: [
      { rx: 0, ry: 0, rz: 0.8, color: "#a78bfa", label: "CI" },
    ],
    caption: "Eigenvalue spread",
  },

  // ── Linear Algebra ──
  tensor_product: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "q₀" },
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "q₁" },
    ],
    caption: "Combined system",
  },
  unitary: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: "#38bdf8", label: "in" },
      { rx: -0.7, ry: 0, rz: 0.7, color: "#f472b6", label: "U·in" },
    ],
    caption: "Rotation on surface",
  },
  hermitian: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "λ₁" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "λ₂" },
    ],
    caption: "Real eigenvalues",
  },
  eigenvalue: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "|e₁⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "|e₂⟩" },
    ],
    caption: "A|e⟩ = λ|e⟩",
  },
  inner_product: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: "#38bdf8", label: "|ψ⟩" },
      { rx: 0.5, ry: 0.5, rz: 0.7, color: "#f472b6", label: "|φ⟩" },
    ],
    caption: "⟨φ|ψ⟩ = overlap",
  },
  spectral_decomposition: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "λ₁" },
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "λ₂" },
    ],
    caption: "A = Σλ|e⟩⟨e|",
  },
  commutator: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "X" },
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "Z" },
    ],
    caption: "[X,Z] ≠ 0",
  },
  dirac_notation: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "|ψ⟩" },
    ],
    caption: "Bra-ket notation",
  },

  // ── Measurement ──
  projective_measurement: {
    dots: [
      { rx: 0.5, ry: 0.3, rz: 0.8, color: "#38bdf8", label: "pre" },
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "post" },
    ],
    caption: "Projects to pole",
  },
  observable: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "+1" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "−1" },
    ],
    caption: "Eigenvalues = outcomes",
  },
  povm: {
    dots: [
      { rx: 0.6, ry: 0, rz: 0.8, color: "#38bdf8", label: "E₁" },
      { rx: -0.6, ry: 0, rz: -0.8, color: "#f472b6", label: "E₂" },
    ],
    caption: "Generalized meas.",
  },

  // ── Information Theory ──
  shannon_entropy: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#94a3b8", label: "H=1" },
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "H=0" },
    ],
    caption: "Max at center",
  },
  von_neumann_entropy: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#94a3b8", label: "S=1" },
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "S=0" },
    ],
    caption: "S(ρ) = −Tr(ρlnρ)",
  },
  mutual_information: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "ρ_AB" },
    ],
    caption: "I(A:B) = shared info",
  },
  jensen_shannon_divergence: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: "#38bdf8", label: "P" },
      { rx: -0.7, ry: 0, rz: 0.7, color: "#f472b6", label: "Q" },
    ],
    caption: "JSD(P‖Q)",
  },
  total_correlation: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#818cf8", label: "TC" },
    ],
    caption: "Multi-information",
  },
  trace_distance: {
    dots: [
      { rx: 0.6, ry: 0, rz: 0.6, color: "#38bdf8", label: "ρ" },
      { rx: -0.6, ry: 0, rz: 0.6, color: "#f472b6", label: "σ" },
    ],
    caption: "D(ρ,σ) = distance",
  },
  fidelity: {
    dots: [
      { rx: 0.5, ry: 0, rz: 0.87, color: "#38bdf8", label: "ρ" },
      { rx: 0.6, ry: 0.1, rz: 0.8, color: "#f472b6", label: "σ" },
    ],
    caption: "F(ρ,σ) = overlap",
  },

  // ── Noise & Channels ──
  amplitude_damping: {
    dots: [
      { rx: 0.5, ry: 0.5, rz: -0.7, color: "#38bdf8", label: "t=0" },
      { rx: 0, ry: 0, rz: 1, color: "#f472b6", label: "t→∞" },
    ],
    caption: "Decays to |0⟩",
  },
  dephasing: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "t=0" },
      { rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "t→∞" },
    ],
    caption: "X,Y → 0",
  },
  pauli_channel: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0.6, color: "#38bdf8", label: "in" },
      { rx: 0.3, ry: 0, rz: 0.3, color: "#f472b6", label: "out" },
    ],
    caption: "Random Pauli errors",
  },
  bit_flip: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#38bdf8", label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "flipped" },
    ],
    caption: "X error: |0⟩↔|1⟩",
  },
  phase_flip: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "|+⟩" },
      { rx: -1, ry: 0, rz: 0, color: "#f472b6", label: "flipped" },
    ],
    caption: "Z error: phase flip",
  },
  kraus_operators: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0.6, color: "#38bdf8", label: "ρ" },
      { rx: 0.4, ry: 0, rz: 0.4, color: "#f472b6", label: "ε(ρ)" },
    ],
    caption: "ε(ρ) = ΣK_i ρ K_i†",
  },
  cptp_map: {
    dots: [
      { rx: 0.9, ry: 0, rz: 0, color: "#38bdf8", label: "in" },
      { rx: 0.6, ry: 0, rz: 0, color: "#f472b6", label: "out" },
    ],
    caption: "Trace-preserving",
  },
  open_quantum_system: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "system" },
      { rx: 0, ry: 0, rz: 0, color: "#94a3b8", label: "→mixed" },
    ],
    caption: "System + environment",
  },
  lindblad_equation: {
    dots: [
      { rx: 0.7, ry: 0.7, rz: 0, color: "#38bdf8", label: "t=0" },
      { rx: 0.2, ry: 0.2, rz: 0, color: "#f472b6", label: "t>0" },
    ],
    caption: "dρ/dt = L[ρ]",
  },
  quantum_zeno_effect: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "frozen" },
    ],
    caption: "Frequent meas. freezes",
  },

  // ── Structured Decoherence (extra) ──
  structure_score: {
    dots: [
      { rx: 0.6, ry: 0.3, rz: 0.5, color: "#34d399", label: "SS" },
      { rx: 0, ry: 0, rz: 0, color: "#94a3b8", label: "null" },
    ],
    caption: "JSD from null",
  },
  delta_cov_fingerprint: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0, color: "#818cf8", label: "ΔCov" },
    ],
    caption: "Error signature",
  },
  fingerprint_trajectory: {
    dots: [
      { rx: 0.9, ry: 0, rz: 0, color: "#38bdf8", label: "t₁" },
      { rx: 0.5, ry: 0.3, rz: 0, color: "#818cf8", label: "t₂" },
      { rx: 0.2, ry: 0.1, rz: 0, color: "#f472b6", label: "t₃" },
    ],
    caption: "Path through space",
  },
  decoherence_flow_generator: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0.6, color: "#38bdf8", label: "flow" },
      { rx: 0, ry: 0, rz: 0, color: "#94a3b8", label: "sink" },
    ],
    caption: "Decoherence flow",
  },
  correlators: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "⟨ZZ⟩" },
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "⟨XX⟩" },
    ],
    caption: "Pauli correlators",
  },

  // ── Algorithms ──
  grover_search: {
    dots: [
      { rx: 1, ry: 0, rz: 0, color: "#94a3b8", label: "start" },
      { rx: 0, ry: 0, rz: 1, color: "#34d399", label: "target" },
    ],
    caption: "Amplitude boost",
  },
  quantum_fourier_transform: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#38bdf8", label: "|x⟩" },
      { rx: 0.7, ry: 0.7, rz: 0, color: "#f472b6", label: "QFT|x⟩" },
    ],
    caption: "Phase encoding",
  },
  quantum_simulation: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: "#818cf8", label: "H" },
    ],
    caption: "e^{−iHt} evolution",
  },
  vqe: {
    dots: [
      { rx: 0.5, ry: 0.3, rz: 0.8, color: "#34d399", label: "θ*" },
    ],
    caption: "Variational ansatz",
  },

  // ── Error Correction ──
  stabilizer: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "+1" },
    ],
    caption: "S|ψ⟩ = +|ψ⟩",
  },
  logical_qubit: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#34d399", label: "|0_L⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "|1_L⟩" },
    ],
    caption: "Encoded in n qubits",
  },
  threshold_theorem: {
    dots: [
      { rx: 0, ry: 0, rz: 0.95, color: "#34d399", label: "below" },
      { rx: 0, ry: 0, rz: 0.3, color: "#f472b6", label: "above" },
    ],
    caption: "p < p_th → correctable",
  },

  // ── Hardware ──
  quantum_volume: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: "#818cf8", label: "QV" },
    ],
    caption: "Device benchmark",
  },
  gate_fidelity: {
    dots: [
      { rx: 0.7, ry: 0, rz: 0.7, color: "#38bdf8", label: "ideal" },
      { rx: 0.6, ry: 0.1, rz: 0.6, color: "#f472b6", label: "actual" },
    ],
    caption: "F(U_ideal, U_real)",
  },

  // ── Misc ──
  berry_phase: {
    dots: [
      { rx: 0.7, ry: 0.7, rz: 0, color: "#818cf8", label: "path" },
    ],
    caption: "Geometric phase",
  },
  bell_inequality: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "ρ_AB" },
    ],
    caption: "S > 2 → entangled",
  },
  chsh: {
    dots: [
      { rx: 0, ry: 0, rz: 0, color: "#f472b6", label: "ρ_AB" },
    ],
    caption: "S ≤ 2√2",
  },
  pauli_transfer_matrix: {
    dots: [
      { rx: 0.8, ry: 0, rz: 0, color: "#38bdf8", label: "in" },
      { rx: 0.5, ry: 0, rz: 0, color: "#f472b6", label: "out" },
    ],
    caption: "4×4 real matrix",
  },
  hilbert_space: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#a78bfa", label: "|0⟩" },
      { rx: 0, ry: 0, rz: -1, color: "#f472b6", label: "|1⟩" },
      { rx: 1, ry: 0, rz: 0, color: "#38bdf8", label: "|+⟩" },
    ],
    caption: "ℂ^{2ⁿ} state space",
  },

  // ── Reconfiguration Space ──
  sx_gate: {
    dots: [
      { rx: 0, ry: 0, rz: 1, color: "#64748b", label: "|0⟩" },
      { rx: 0, ry: -1, rz: 0, color: "#f472b6", label: "√X|0⟩" },
    ],
    caption: "π/2 rotation about X",
  },
};
