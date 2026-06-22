/**
 * Pure (render-free) configuration logic for the experiment configurator.
 *
 * These functions are extracted from `useExperimentConfig` so the validation
 * and config-assembly decisions can be unit-tested without rendering the hook.
 * The hook owns the React state; this module owns the pure transforms.
 */

import type {
  StateType,
  NoiseType,
  SimMode,
  ResearchType,
  ExperimentConfig,
} from "../../lib/types";

export interface ConfigWarning {
  level: "error" | "warning" | "info";
  message: string;
}

/** Plain snapshot of the configurator state used by the pure transforms. */
export interface ConfigState {
  stateType: StateType;
  numQubits: number;
  simMode: SimMode;
  shots: number;
  rngSeed: number | null;
  noiseEnabled: boolean;
  noiseType: NoiseType;
  errorRate: number;
  t1: number | null;
  t2: number | null;
  readoutErrorRate: number | null;
  balanceCircuit: boolean;
  metricsEnabled: boolean;
  metricsMode: "profile" | "individual";
  selectedProfile: string;
  selectedMetrics: string[];
  researchType: ResearchType | null;
  multipleRuns: number;
  trackConvergence: boolean;
  backendName: string;
  optimizationLevel: number;
  hardwareSession: boolean;
}

/** Compute the validation banner rows for the current config state. */
export function computeConfigWarnings(s: ConfigState): ConfigWarning[] {
  const w: ConfigWarning[] = [];

  if (s.simMode === "statevector" && s.noiseEnabled) {
    w.push({ level: "info", message: "Noise auto-disabled: statevector mode is noiseless by design." });
  }
  if (s.simMode === "hardware" && s.noiseEnabled) {
    w.push({ level: "info", message: "Noise auto-disabled: real hardware has physical noise." });
  }
  if (s.errorRate > 0.5) {
    w.push({ level: "warning", message: "High error rate — quantum advantage may be lost." });
  }
  if (s.simMode === "density_matrix" && s.numQubits > 10) {
    w.push({ level: "warning", message: "Dense simulation: may be slow for >10 qubits." });
  }
  if (s.shots < 100 && s.metricsEnabled) {
    w.push({ level: "warning", message: "Too few shots for reliable metrics." });
  }
  if (s.simMode === "hardware" && s.shots > 100000) {
    w.push({ level: "error", message: "Exceeds IBM Quantum limit (100,000 shots)." });
  }
  if (s.readoutErrorRate !== null && s.readoutErrorRate > 0.3) {
    w.push({ level: "warning", message: "Unusually high readout error." });
  }
  if (s.stateType === "BELL" && s.numQubits !== 2) {
    w.push({ level: "error", message: "Bell states require exactly 2 qubits." });
  }

  return w;
}

/** Whether the config has no blocking ("error") warnings. */
export function isConfigValid(warnings: ConfigWarning[]): boolean {
  return !warnings.some((w) => w.level === "error");
}

/** Reason simulated noise is unavailable for the current sim mode, or null. */
export function noiseDisabledReason(simMode: SimMode): string | null {
  if (simMode === "statevector") {
    return "Statevector mode is noiseless by design. Use Density Matrix for noisy simulations.";
  }
  if (simMode === "hardware") {
    return "Real hardware has physical noise. Simulated noise cannot be applied.";
  }
  return null;
}

/** Assemble the backend ExperimentConfig payload from the config state. */
export function buildExperimentConfig(s: ConfigState): ExperimentConfig {
  const config: ExperimentConfig = {
    num_qubits: s.numQubits,
    state_type: s.stateType,
    shots: s.shots,
    noise_enabled: s.noiseEnabled,
    sim_mode: s.simMode,
    visualization_type: "none",
  };

  // Noise params (only when enabled).
  if (s.noiseEnabled) {
    config.noise_type = s.noiseType;
    config.error_rate = s.errorRate;

    if (s.readoutErrorRate !== null) {
      config.readout_error_rate = s.readoutErrorRate;
    }

    if (s.noiseType === "thermal_relaxation") {
      if (s.t1 !== null) config.t1 = s.t1;
      if (s.t2 !== null) config.t2 = s.t2;
    }
  }

  // Metrics.
  if (s.metricsEnabled) {
    config.metrics =
      s.metricsMode === "profile" ? s.selectedProfile : s.selectedMetrics;
  }

  // Research type.
  if (s.researchType !== null) {
    config.research_type = s.researchType;
  }

  // Balance circuit.
  if (s.balanceCircuit) {
    config.balance_circuit = "gate_count";
  }

  // RNG seed (not applicable for hardware).
  if (s.rngSeed !== null && s.simMode !== "hardware") {
    config.rng_seed = s.rngSeed;
  }

  // Multiple runs / convergence.
  if (s.multipleRuns > 1) {
    config.multiple_runs = s.multipleRuns;
  }
  if (s.trackConvergence) {
    config.track_convergence = true;
  }

  // Hardware params.
  if (s.simMode === "hardware") {
    if (s.backendName) {
      config.backend_name = s.backendName;
    }
    config.optimization_level = s.optimizationLevel;
    if (s.hardwareSession) {
      config.hardware_session = true;
    }
  }

  return config;
}
