/** Central hook for experiment configuration state, validation, and config assembly. */

import { useState, useMemo, useEffect, useCallback } from "react";
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

export interface UseExperimentConfigReturn {
  // State
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

  // Setters
  setStateType: (v: StateType) => void;
  setNumQubits: (v: number) => void;
  setSimMode: (v: SimMode) => void;
  setShots: (v: number) => void;
  setRngSeed: (v: number | null) => void;
  setNoiseEnabled: (v: boolean) => void;
  setNoiseType: (v: NoiseType) => void;
  setErrorRate: (v: number) => void;
  setT1: (v: number | null) => void;
  setT2: (v: number | null) => void;
  setReadoutErrorRate: (v: number | null) => void;
  setBalanceCircuit: (v: boolean) => void;
  setMetricsEnabled: (v: boolean) => void;
  setMetricsMode: (v: "profile" | "individual") => void;
  setSelectedProfile: (v: string) => void;
  setSelectedMetrics: (v: string[]) => void;
  setResearchType: (v: ResearchType | null) => void;
  setMultipleRuns: (v: number) => void;
  setTrackConvergence: (v: boolean) => void;
  setBackendName: (v: string) => void;
  setOptimizationLevel: (v: number) => void;
  setHardwareSession: (v: boolean) => void;

  // Computed
  warnings: ConfigWarning[];
  isValid: boolean;
  noiseDisabledReason: string | null;
  showThermalParams: boolean;
  showHardwareSection: boolean;
  buildConfig: () => ExperimentConfig;
}

export function useExperimentConfig(): UseExperimentConfigReturn {
  // ── State ────────────────────────────────────────────────────────────
  const [stateType, setStateType] = useState<StateType>("GHZ");
  const [numQubits, setNumQubits] = useState(3);
  const [simMode, setSimMode] = useState<SimMode>("qasm");
  const [shots, setShots] = useState(1024);
  const [rngSeed, setRngSeed] = useState<number | null>(null);
  const [noiseEnabled, setNoiseEnabled] = useState(false);
  const [noiseType, setNoiseType] = useState<NoiseType>("depolarizing");
  const [errorRate, setErrorRate] = useState(0.05);
  const [t1, setT1] = useState<number | null>(null);
  const [t2, setT2] = useState<number | null>(null);
  const [readoutErrorRate, setReadoutErrorRate] = useState<number | null>(null);
  const [balanceCircuit, setBalanceCircuit] = useState(false);
  const [metricsEnabled, setMetricsEnabled] = useState(false);
  const [metricsMode, setMetricsMode] = useState<"profile" | "individual">("profile");
  const [selectedProfile, setSelectedProfile] = useState("structured_decoherence");
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>([]);
  const [researchType, setResearchType] = useState<ResearchType | null>(null);
  const [multipleRuns, setMultipleRuns] = useState(1);
  const [trackConvergence, setTrackConvergence] = useState(false);
  const [backendName, setBackendName] = useState("");
  const [optimizationLevel, setOptimizationLevel] = useState(1);
  const [hardwareSession, setHardwareSession] = useState(false);

  // ── Cross-field side effects ─────────────────────────────────────────

  // Statevector and hardware modes do not support simulated noise.
  useEffect(() => {
    if (simMode === "statevector" || simMode === "hardware") {
      setNoiseEnabled(false);
    }
  }, [simMode]);

  // Bell states require exactly 2 qubits.
  useEffect(() => {
    if (stateType === "BELL") {
      setNumQubits(2);
    }
  }, [stateType]);

  // Hardware mode uses physical randomness; RNG seed is meaningless.
  useEffect(() => {
    if (simMode === "hardware") {
      setRngSeed(null);
    }
  }, [simMode]);

  // Clear thermal params when switching away from thermal_relaxation.
  useEffect(() => {
    if (noiseType !== "thermal_relaxation") {
      setT1(null);
      setT2(null);
    }
  }, [noiseType]);

  // Enforce T2 <= 2*T1 physical constraint.
  useEffect(() => {
    if (t1 !== null && t2 !== null && t2 > 2 * t1) {
      setT2(2 * t1);
    }
  }, [t1, t2]);

  // ── Validation warnings ──────────────────────────────────────────────

  const warnings = useMemo<ConfigWarning[]>(() => {
    const w: ConfigWarning[] = [];

    if (simMode === "statevector" && noiseEnabled) {
      w.push({ level: "info", message: "Noise auto-disabled: statevector mode is noiseless by design." });
    }
    if (simMode === "hardware" && noiseEnabled) {
      w.push({ level: "info", message: "Noise auto-disabled: real hardware has physical noise." });
    }
    if (errorRate > 0.5) {
      w.push({ level: "warning", message: "High error rate \u2014 quantum advantage may be lost." });
    }
    if (simMode === "density_matrix" && numQubits > 10) {
      w.push({ level: "warning", message: "Dense simulation: may be slow for >10 qubits." });
    }
    if (shots < 100 && metricsEnabled) {
      w.push({ level: "warning", message: "Too few shots for reliable metrics." });
    }
    if (simMode === "hardware" && shots > 100000) {
      w.push({ level: "error", message: "Exceeds IBM Quantum limit (100,000 shots)." });
    }
    if (readoutErrorRate !== null && readoutErrorRate > 0.3) {
      w.push({ level: "warning", message: "Unusually high readout error." });
    }
    if (stateType === "BELL" && numQubits !== 2) {
      w.push({ level: "error", message: "Bell states require exactly 2 qubits." });
    }

    return w;
  }, [simMode, noiseEnabled, errorRate, numQubits, shots, metricsEnabled, readoutErrorRate, stateType]);

  // ── Computed properties ──────────────────────────────────────────────

  const isValid = useMemo(() => !warnings.some((w) => w.level === "error"), [warnings]);

  const noiseDisabledReason = useMemo(() => {
    if (simMode === "statevector") {
      return "Statevector mode is noiseless by design. Use Density Matrix for noisy simulations.";
    }
    if (simMode === "hardware") {
      return "Real hardware has physical noise. Simulated noise cannot be applied.";
    }
    return null;
  }, [simMode]);

  const showThermalParams = noiseType === "thermal_relaxation" && noiseEnabled;
  const showHardwareSection = simMode === "hardware";

  // ── Config assembly ──────────────────────────────────────────────────

  const buildConfig = useCallback((): ExperimentConfig => {
    const config: ExperimentConfig = {
      num_qubits: numQubits,
      state_type: stateType,
      shots,
      noise_enabled: noiseEnabled,
      sim_mode: simMode,
      visualization_type: "none",
    };

    // Noise params (only when enabled).
    if (noiseEnabled) {
      config.noise_type = noiseType;
      config.error_rate = errorRate;

      if (readoutErrorRate !== null) {
        config.readout_error_rate = readoutErrorRate;
      }

      if (noiseType === "thermal_relaxation") {
        if (t1 !== null) config.t1 = t1;
        if (t2 !== null) config.t2 = t2;
      }
    }

    // Metrics.
    if (metricsEnabled) {
      config.metrics =
        metricsMode === "profile" ? selectedProfile : selectedMetrics;
    }

    // Research type.
    if (researchType !== null) {
      config.research_type = researchType;
    }

    // Balance circuit.
    if (balanceCircuit) {
      config.balance_circuit = "gate_count";
    }

    // RNG seed (not applicable for hardware).
    if (rngSeed !== null && simMode !== "hardware") {
      config.rng_seed = rngSeed;
    }

    // Multiple runs / convergence.
    if (multipleRuns > 1) {
      config.multiple_runs = multipleRuns;
    }
    if (trackConvergence) {
      config.track_convergence = true;
    }

    // Hardware params.
    if (simMode === "hardware") {
      if (backendName) {
        config.backend_name = backendName;
      }
      config.optimization_level = optimizationLevel;
      if (hardwareSession) {
        config.hardware_session = true;
      }
    }

    return config;
  }, [
    numQubits, stateType, shots, noiseEnabled, simMode,
    noiseType, errorRate, readoutErrorRate, t1, t2,
    metricsEnabled, metricsMode, selectedProfile, selectedMetrics,
    researchType, balanceCircuit, rngSeed,
    multipleRuns, trackConvergence,
    backendName, optimizationLevel, hardwareSession,
  ]);

  // ── Return ───────────────────────────────────────────────────────────

  return {
    stateType, setStateType,
    numQubits, setNumQubits,
    simMode, setSimMode,
    shots, setShots,
    rngSeed, setRngSeed,
    noiseEnabled, setNoiseEnabled,
    noiseType, setNoiseType,
    errorRate, setErrorRate,
    t1, setT1,
    t2, setT2,
    readoutErrorRate, setReadoutErrorRate,
    balanceCircuit, setBalanceCircuit,
    metricsEnabled, setMetricsEnabled,
    metricsMode, setMetricsMode,
    selectedProfile, setSelectedProfile,
    selectedMetrics, setSelectedMetrics,
    researchType, setResearchType,
    multipleRuns, setMultipleRuns,
    trackConvergence, setTrackConvergence,
    backendName, setBackendName,
    optimizationLevel, setOptimizationLevel,
    hardwareSession, setHardwareSession,
    warnings,
    isValid,
    noiseDisabledReason,
    showThermalParams,
    showHardwareSection,
    buildConfig,
  };
}
