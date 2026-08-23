/**
 * Configuration constants for the experiment configure screen.
 *
 * Backend-owned facts (the valid id sets, per-state qubit bounds, and the
 * metric-profile -> metric-list mappings) are imported from the generated
 * catalog (the Python backend is the single source of truth). Only purely-UI
 * metadata (labels, descriptions, ordering subsets) is declared locally here.
 *
 * Regenerate the catalog with:
 *   uv run python scripts/gen_frontend_constants.py
 */
import {
  STATE_TYPES as CATALOG_STATE_TYPES,
  SIM_MODES as CATALOG_SIM_MODES,
  NOISE_TYPES as CATALOG_NOISE_TYPES,
  EXPERIMENT_TYPES as CATALOG_EXPERIMENT_TYPES,
  METRIC_NAMES as CATALOG_METRIC_NAMES,
  METRIC_PROFILES as CATALOG_METRIC_PROFILES,
} from "@/src/generated/catalog";

// ── Local UI metadata (labels / descriptions only) keyed by backend id ──

const STATE_UI: Record<string, { label: string; description: string }> = {
  GHZ:           { label: "GHZ",           description: "Maximal entanglement across all qubits" },
  W:             { label: "W",             description: "Symmetric single-excitation entanglement" },
  CLUSTER:       { label: "Cluster",       description: "Nearest-neighbor graph state" },
  BELL:          { label: "Bell",          description: "Maximal 2-qubit entanglement" },
  SUPERPOSITION: { label: "Superposition", description: "Unentangled product state (control baseline)" },
};

const SIM_MODE_UI: Record<string, { label: string; description: string }> = {
  qasm:           { label: "QASM",           description: "Shot-based simulation. Supports noise. Fast." },
  statevector:    { label: "Statevector",    description: "Exact noiseless state. No noise support." },
  density_matrix: { label: "Density Matrix", description: "Full mixed-state simulation. Supports noise. Slow for >8 qubits." },
  hardware:       { label: "Hardware",       description: "Real IBM Quantum device. Requires API credentials." },
};

const NOISE_UI: Record<string, { label: string; description: string }> = {
  depolarizing:            { label: "Depolarizing",            description: "Symmetric random Pauli errors on each gate." },
  amplitude_damping:       { label: "Amplitude Damping",       description: "Energy loss to the environment (T1 decay)." },
  phase_damping:           { label: "Phase Damping",           description: "Dephasing without energy loss (T2 process)." },
  bit_flip:                { label: "Bit Flip",                description: "Classical bit-flip errors (X channel)." },
  phase_flip:              { label: "Phase Flip",              description: "Phase-flip errors (Z channel)." },
  thermal_relaxation:      { label: "Thermal Relaxation",      description: "Combined T1/T2 relaxation with gate-time modeling." },
  correlated_depolarizing: { label: "Correlated Depolarizing", description: "Multi-qubit correlated Pauli errors on entangling gates." },
};

// Experiment types shown in the UI. The catalog also exposes "batch_sweep"; it is
// intentionally omitted from this picker (no UI label -> not rendered).
const EXPERIMENT_TYPE_UI: Record<string, { label: string }> = {
  parameter_sweep:        { label: "Parameter Sweep" },
  noise_comparison:       { label: "Noise Comparison" },
  control:                { label: "Control" },
  scaling:                { label: "Scaling" },
  convergence:            { label: "Convergence" },
};

const PROFILE_UI: Record<string, { label: string; description: string }> = {
  structure:          { label: "Structure",          description: "Distribution-structure metric suite" },
  quick:              { label: "Quick",              description: "Fast overview with 2 key metrics" },
  information_theory: { label: "Information Theory", description: "Information-theoretic analysis" },
};

const METRIC_UI: Record<string, { label: string; description: string }> = {
  structure_score:                { label: "Structure Score",                description: "Jensen-Shannon divergence from factorized null model" },
  entanglement_error_correlation: { label: "Entanglement-Error Correlation", description: "Pearson correlation between topology and MI matrices" },
  concentration_index:            { label: "Concentration Index",            description: "Top-vs-bottom quartile probability ratio" },
  pathway_persistence:            { label: "Pathway Persistence",            description: "Rank correlation consistency across conditions" },
  complexity_emergence_score:     { label: "Complexity Emergence",           description: "Logistic emergence threshold detection" },
  total_correlation:              { label: "Total Correlation",              description: "Multi-information across all qubits" },
};

// ── Derived constants: backend facts + local UI metadata ──

export const STATE_TYPES = CATALOG_STATE_TYPES.map((s) => ({
  id: s.id,
  label: STATE_UI[s.id].label,
  minQubits: s.minQubits,
  maxQubits: s.maxQubits,
  description: STATE_UI[s.id].description,
}));

export const SIM_MODES = CATALOG_SIM_MODES.map((id) => ({
  id,
  label: SIM_MODE_UI[id].label,
  description: SIM_MODE_UI[id].description,
}));

export const NOISE_TYPES = CATALOG_NOISE_TYPES.map((id) => ({
  id,
  label: NOISE_UI[id].label,
  description: NOISE_UI[id].description,
}));

export const SHOT_PRESETS = [1024, 4096, 8192, 16384] as const;

export const METRIC_PROFILES = Object.entries(CATALOG_METRIC_PROFILES).map(
  ([id, metrics]) => ({
    id,
    label: PROFILE_UI[id].label,
    metrics,
    description: PROFILE_UI[id].description,
  }),
);

export const INDIVIDUAL_METRICS = CATALOG_METRIC_NAMES.map((id) => ({
  id,
  label: METRIC_UI[id].label,
  description: METRIC_UI[id].description,
}));

export const EXPERIMENT_TYPES = CATALOG_EXPERIMENT_TYPES.filter(
  (id) => id in EXPERIMENT_TYPE_UI,
).map((id) => ({ id, label: EXPERIMENT_TYPE_UI[id].label }));

// Hardware backends are NOT hardcoded here: the live list comes from the
// backend (`GET /api/hardware/backends`) via useHardwareValidation, which is the
// single source of truth. When credentials are absent the picker falls back to
// manual entry (clearly flagged in the UI).

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
      "GHZ states create maximal entanglement across all qubits. W states spread a single " +
      "excitation symmetrically and respond to noise differently due to their topology. " +
      "Cluster states use nearest-neighbor CZ gates and form " +
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
    title: "Analysis Metrics",
    content:
      "Profiles select curated sets of metrics for the question you are asking. The Structure " +
      "profile computes 6 metrics: Structure Score (JSD from null model), " +
      "Entanglement-Error Correlation (topology vs mutual information), Concentration Index " +
      "(Gini-like concentration measure), Pathway Persistence (rank stability across conditions), " +
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
