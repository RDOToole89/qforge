/** TypeScript types matching the Pydantic models in src/engine/models/. */

// ── Config (what the user tunes) ──────────────────────────────────────

export type StateType =
  | "GHZ"
  | "W"
  | "CLUSTER"
  | "BELL"
  | "SUPERPOSITION"
  | "CUSTOM";

export type NoiseType =
  | "depolarizing"
  | "amplitude_damping"
  | "phase_damping"
  | "bit_flip"
  | "phase_flip"
  | "thermal_relaxation"
  | "correlated_depolarizing";

export interface ExperimentConfig {
  num_qubits: number;
  state_type: StateType;
  shots: number;
  noise_enabled: boolean;
  noise_type?: NoiseType;
  error_rate?: number;
  metrics?: string | string[] | null;
  research_type?: string;
  balance_circuit?: string;
  rng_seed?: number;
  visualization_type?: "histogram" | "none";
}

// ── Metrics ──────────────────────────────────────────────────────────

export interface MetricEntry {
  value: number;
  ci95: [number, number] | null;
  status: string;
  extras: Record<string, unknown>;
}

export interface AnalysisMetadata {
  state_type: string;
  num_qubits: number;
  total_shots: number;
  unique_outcomes: number;
  analysis_timestamp: string;
}

export interface MetricsBundle {
  metrics: Record<string, MetricEntry>;
  profile: string | null;
  metadata: AnalysisMetadata;
}

// ── Results ───────────────────────────────────────────────────────────

export interface CircuitStatistics {
  depth: number;
  num_gates: number;
  num_qubits: number;
  gate_types: Record<string, number>;
  two_qubit_gate_count: number | null;
}

export interface MeasurementResults {
  raw_counts: Record<string, number>;
  total_shots: number;
  unique_outcomes: number;
  outcome_probabilities: Record<string, number>;
}

export interface ExperimentAnalysis {
  experiment_metadata: {
    experiment_id: string;
    timestamp: string;
    framework_version: string;
    research_type: string | null;
  };
  experiment_parameters: Record<string, unknown>;
  circuit_statistics: CircuitStatistics;
  measurement_results: MeasurementResults;
}

export interface ExperimentResult {
  analysis: ExperimentAnalysis;
  metrics_bundle: MetricsBundle | null;
  config_hash: string;
  timestamp: string;
  status: string;
}

// ── Bloch Visualizer Data (from /bloch-data endpoint) ────────────────

export interface QubitBlochData {
  qubit_index: number;
  bloch_vector: { rx: number; ry: number; rz: number };
  purity: number;
}

export interface PairCorrelatorData {
  qubit_i: number;
  qubit_j: number;
  correlators: { zi: number; iz: number; zz: number; xx: number; yy: number };
  mutual_information: number;
}

export interface BlochVisualizerData {
  experiment_id: string;
  state_type: string;
  num_qubits: number;
  noise_type: string | null;
  error_rate: number | null;
  fidelity: number | null;
  source_mode: "density_matrix" | "statevector" | "diagonal_estimate";
  qubits: QubitBlochData[];
  pairs: PairCorrelatorData[];
  mi_matrix: number[][];
  metrics: Record<string, { value: number; ci95: [number, number] | null }> | null;
}

// ── Bloch Sweep (animated decoherence progression) ───────────────────

export interface BlochSweepRequest {
  state_type: string;
  num_qubits: number;
  noise_type: string;
  error_rates: number[];
  sim_mode?: string;
  shots?: number;
  rng_seed?: number | null;
}

export interface BlochSweepResponse {
  state_type: string;
  num_qubits: number;
  noise_type: string;
  sim_mode: string;
  error_rates: number[];
  snapshots: BlochVisualizerData[];
}

// ── Registry ──────────────────────────────────────────────────────────

export interface RegistryEntry {
  name: string;
  description: string;
}

// ── Stored results listing ────────────────────────────────────────────

export interface StoredResultEntry {
  filename: string;
  size_bytes?: number;
  modified?: number;
  experiment_id?: string;
  num_qubits?: number;
  state_type?: string;
  error?: string;
}
