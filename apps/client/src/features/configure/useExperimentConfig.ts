/** Central hook for experiment configuration state, validation, and config assembly. */

import { useState, useMemo, useEffect, useCallback } from "react";
import type {
  StateType,
  NoiseType,
  SimMode,
  ResearchType,
  ExperimentConfig,
} from "../../lib/types";
import {
  buildExperimentConfig,
  computeConfigWarnings,
  isConfigValid,
  noiseDisabledReason as computeNoiseDisabledReason,
  type ConfigState,
  type ConfigWarning,
} from "./configLogic";

export type { ConfigWarning };

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
  // -- State --------------------------------------------------------------
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

  // -- Cross-field side effects -------------------------------------------

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

  // -- Config snapshot for the pure transforms ----------------------------

  const configState = useMemo<ConfigState>(
    () => ({
      stateType,
      numQubits,
      simMode,
      shots,
      rngSeed,
      noiseEnabled,
      noiseType,
      errorRate,
      t1,
      t2,
      readoutErrorRate,
      balanceCircuit,
      metricsEnabled,
      metricsMode,
      selectedProfile,
      selectedMetrics,
      researchType,
      multipleRuns,
      trackConvergence,
      backendName,
      optimizationLevel,
      hardwareSession,
    }),
    [
      stateType, numQubits, simMode, shots, rngSeed, noiseEnabled, noiseType,
      errorRate, t1, t2, readoutErrorRate, balanceCircuit, metricsEnabled,
      metricsMode, selectedProfile, selectedMetrics, researchType, multipleRuns,
      trackConvergence, backendName, optimizationLevel, hardwareSession,
    ],
  );

  // -- Validation warnings ------------------------------------------------

  const warnings = useMemo<ConfigWarning[]>(
    () => computeConfigWarnings(configState),
    [configState],
  );

  // -- Computed properties ------------------------------------------------

  const isValid = useMemo(() => isConfigValid(warnings), [warnings]);

  const noiseDisabledReason = useMemo(
    () => computeNoiseDisabledReason(simMode),
    [simMode],
  );

  const showThermalParams = noiseType === "thermal_relaxation" && noiseEnabled;
  const showHardwareSection = simMode === "hardware";

  // -- Config assembly ----------------------------------------------------

  const buildConfig = useCallback(
    (): ExperimentConfig => buildExperimentConfig(configState),
    [configState],
  );

  // -- Return -------------------------------------------------------------

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
