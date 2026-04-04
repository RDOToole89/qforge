/** Configuration constants for the experiment configure screen. */

export const STATE_TYPES = [
  { id: "GHZ",           label: "GHZ",           minQubits: 2, maxQubits: 20, description: "Maximal entanglement across all qubits" },
  { id: "W",             label: "W",             minQubits: 2, maxQubits: 20, description: "Symmetric single-excitation entanglement" },
  { id: "CLUSTER",       label: "Cluster",       minQubits: 2, maxQubits: 20, description: "Nearest-neighbor graph state" },
  { id: "BELL",          label: "Bell",          minQubits: 2, maxQubits: 2,  description: "Maximal 2-qubit entanglement" },
  { id: "SUPERPOSITION", label: "Superposition", minQubits: 1, maxQubits: 20, description: "Unentangled product state (control baseline)" },
] as const;

export const SIM_MODES = [
  { id: "qasm",           label: "QASM",           description: "Shot-based simulation. Supports noise. Fast." },
  { id: "statevector",    label: "Statevector",    description: "Exact noiseless state. No noise support." },
  { id: "density_matrix", label: "Density Matrix", description: "Full mixed-state simulation. Supports noise. Slow for >8 qubits." },
  { id: "hardware",       label: "Hardware",       description: "Real IBM Quantum device. Requires API credentials." },
] as const;

export const NOISE_TYPES = [
  { id: "depolarizing",            label: "Depolarizing",            description: "Symmetric random Pauli errors on each gate." },
  { id: "amplitude_damping",       label: "Amplitude Damping",       description: "Energy loss to the environment (T1 decay)." },
  { id: "phase_damping",           label: "Phase Damping",           description: "Dephasing without energy loss (T2 process)." },
  { id: "bit_flip",                label: "Bit Flip",                description: "Classical bit-flip errors (X channel)." },
  { id: "phase_flip",              label: "Phase Flip",              description: "Phase-flip errors (Z channel)." },
  { id: "thermal_relaxation",      label: "Thermal Relaxation",      description: "Combined T1/T2 relaxation with gate-time modeling." },
  { id: "correlated_depolarizing", label: "Correlated Depolarizing", description: "Multi-qubit correlated Pauli errors on entangling gates." },
] as const;

export const SHOT_PRESETS = [1024, 4096, 8192, 16384] as const;

export const METRIC_PROFILES = [
  {
    id: "structured_decoherence",
    label: "Structured Decoherence",
    metrics: [
      "structure_score",
      "entanglement_error_correlation",
      "concentration_index",
      "pathway_persistence",
      "complexity_emergence_score",
      "total_correlation",
    ],
    description: "Full structured decoherence suite",
  },
  {
    id: "quick",
    label: "Quick",
    metrics: ["structure_score", "concentration_index"],
    description: "Fast overview with 2 key metrics",
  },
  {
    id: "information_theory",
    label: "Information Theory",
    metrics: ["structure_score", "total_correlation", "concentration_index"],
    description: "Information-theoretic analysis",
  },
] as const;

export const INDIVIDUAL_METRICS = [
  { id: "structure_score",                 label: "Structure Score",                description: "Jensen-Shannon divergence from factorized null model" },
  { id: "entanglement_error_correlation",  label: "Entanglement-Error Correlation", description: "Pearson correlation between topology and MI matrices" },
  { id: "concentration_index",             label: "Concentration Index",            description: "Gini-like pathway concentration measure" },
  { id: "pathway_persistence",             label: "Pathway Persistence",            description: "Rank correlation consistency across conditions" },
  { id: "complexity_emergence_score",      label: "Complexity Emergence",           description: "Logistic emergence threshold detection" },
  { id: "total_correlation",               label: "Total Correlation",              description: "Multi-information across all qubits" },
] as const;

export const RESEARCH_TYPES = [
  { id: "structured_decoherence", label: "Structured Decoherence" },
  { id: "parameter_sweep",       label: "Parameter Sweep" },
  { id: "noise_comparison",      label: "Noise Comparison" },
  { id: "control",               label: "Control" },
  { id: "scaling",               label: "Scaling" },
  { id: "convergence",           label: "Convergence" },
] as const;

export const KNOWN_BACKENDS = [
  "ibm_brisbane",
  "ibm_fez",
  "ibm_kyiv",
  "ibm_sherbrooke",
  "ibm_nazca",
] as const;

export const OPTIMIZATION_LEVELS = [
  { level: 0, label: "None",   description: "No optimization" },
  { level: 1, label: "Light",  description: "Basic gate optimization (default)" },
  { level: 2, label: "Medium", description: "Gate cancellation and commutation" },
  { level: 3, label: "Heavy",  description: "Full optimization with noise-aware routing" },
] as const;

export const INFO_TEXT: Record<string, { title: string; content: string }> = {
  state: {
    title: "Quantum State Preparation",
    content:
      "GHZ states create maximal entanglement across all qubits and are the primary probe for " +
      "structured decoherence. W states spread a single excitation symmetrically and decohere " +
      "differently due to their topology. Cluster states use nearest-neighbor CZ gates and form " +
      "graph states useful for measurement-based quantum computing. Bell states are the simplest " +
      "entangled pair (2 qubits only). Superposition creates an unentangled product state " +
      "(H on each qubit) and serves as a control baseline with no entanglement structure.",
  },
  simulation: {
    title: "Simulation Mode",
    content:
      "QASM mode runs a shot-based simulation that samples from the output distribution, " +
      "supporting all noise models. Statevector mode computes the exact quantum state without " +
      "noise (measurements are sampled from the ideal distribution). Density Matrix mode " +
      "represents the full mixed state and supports noise, but scales as O(4^n) in memory. " +
      "Hardware mode sends circuits to a real IBM Quantum device via Qiskit Runtime.",
  },
  noise: {
    title: "Noise Configuration",
    content:
      "Depolarizing noise applies random Pauli errors uniformly. Amplitude damping models " +
      "energy relaxation (T1 process) where |1> decays to |0>. Phase damping models pure " +
      "dephasing (T2 process) without energy loss. Bit-flip and phase-flip are simplified " +
      "single-axis error channels. Thermal relaxation combines T1 and T2 processes with " +
      "explicit time constants — T2 must satisfy T2 <= 2*T1. Correlated depolarizing applies " +
      "multi-qubit Pauli errors to pairs of qubits sharing entangling gates.",
  },
  metrics: {
    title: "Research Metrics",
    content:
      "Profiles select curated sets of metrics for common analysis tasks. The Structured " +
      "Decoherence profile computes all 6 metrics: Structure Score (JSD from null model), " +
      "Entanglement-Error Correlation (topology vs mutual information), Concentration Index " +
      "(Gini-like pathway measure), Pathway Persistence (rank stability across conditions), " +
      "Complexity Emergence (logistic threshold detection), and Total Correlation " +
      "(multi-information). Individual mode lets you pick specific metrics.",
  },
  hardware: {
    title: "Hardware Configuration",
    content:
      "Select a real IBM Quantum backend. Optimization level controls how aggressively the " +
      "transpiler simplifies circuits: Level 0 does no optimization, Level 1 applies basic " +
      "gate merging, Level 2 adds commutation analysis, and Level 3 performs full noise-aware " +
      "routing and optimization. Hardware sessions keep the backend reserved between jobs, " +
      "reducing queue wait times for multi-run experiments.",
  },
};
