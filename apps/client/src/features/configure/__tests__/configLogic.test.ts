/**
 * Tests for the pure configurator decision logic (validation banner rows and
 * backend config assembly) extracted from useExperimentConfig.
 */
import { describe, expect, it } from "vitest";
import {
  buildExperimentConfig,
  computeConfigWarnings,
  isConfigValid,
  noiseDisabledReason,
  type ConfigState,
} from "../configLogic";

function baseState(over: Partial<ConfigState> = {}): ConfigState {
  return {
    stateType: "GHZ",
    numQubits: 3,
    simMode: "qasm",
    shots: 1024,
    rngSeed: null,
    noiseEnabled: false,
    noiseType: "depolarizing",
    errorRate: 0.05,
    t1: null,
    t2: null,
    readoutErrorRate: null,
    balanceCircuit: false,
    metricsEnabled: false,
    metricsMode: "profile",
    selectedProfile: "structure",
    selectedMetrics: [],
    experimentType: null,
    multipleRuns: 1,
    trackConvergence: false,
    backendName: "",
    optimizationLevel: 1,
    hardwareSession: false,
    ...over,
  };
}

describe("computeConfigWarnings", () => {
  it("returns no warnings for a sensible default config", () => {
    expect(computeConfigWarnings(baseState())).toEqual([]);
  });

  it("flags statevector + noise as an info auto-disable", () => {
    const w = computeConfigWarnings(baseState({ simMode: "statevector", noiseEnabled: true }));
    expect(w).toHaveLength(1);
    expect(w[0].level).toBe("info");
    expect(w[0].message).toContain("statevector");
  });

  it("flags hardware + noise as an info auto-disable", () => {
    const w = computeConfigWarnings(baseState({ simMode: "hardware", noiseEnabled: true }));
    expect(w.some((x) => x.level === "info" && x.message.includes("real hardware"))).toBe(true);
  });

  it("warns about a high error rate", () => {
    const w = computeConfigWarnings(baseState({ errorRate: 0.6 }));
    expect(w.some((x) => x.level === "warning" && x.message.includes("High error rate"))).toBe(true);
  });

  it("warns about slow dense simulation past 10 qubits", () => {
    expect(computeConfigWarnings(baseState({ simMode: "density_matrix", numQubits: 11 }))).toHaveLength(1);
    expect(computeConfigWarnings(baseState({ simMode: "density_matrix", numQubits: 10 }))).toEqual([]);
  });

  it("warns about too few shots only when metrics are enabled", () => {
    expect(computeConfigWarnings(baseState({ shots: 50 }))).toEqual([]);
    const w = computeConfigWarnings(baseState({ shots: 50, metricsEnabled: true }));
    expect(w.some((x) => x.message.includes("Too few shots"))).toBe(true);
  });

  it("errors when hardware shots exceed the IBM limit", () => {
    const w = computeConfigWarnings(baseState({ simMode: "hardware", shots: 200000 }));
    expect(w.some((x) => x.level === "error" && x.message.includes("100,000"))).toBe(true);
  });

  it("warns about unusually high readout error", () => {
    expect(computeConfigWarnings(baseState({ readoutErrorRate: 0.4 })).some((x) => x.message.includes("readout"))).toBe(true);
    expect(computeConfigWarnings(baseState({ readoutErrorRate: 0.3 }))).toEqual([]);
  });

  it("errors when a Bell state does not have exactly 2 qubits", () => {
    const w = computeConfigWarnings(baseState({ stateType: "BELL", numQubits: 3 }));
    expect(w.some((x) => x.level === "error" && x.message.includes("Bell"))).toBe(true);
    expect(computeConfigWarnings(baseState({ stateType: "BELL", numQubits: 2 }))).toEqual([]);
  });
});

describe("isConfigValid", () => {
  it("is false when any error-level warning exists", () => {
    expect(isConfigValid([{ level: "warning", message: "x" }])).toBe(true);
    expect(isConfigValid([{ level: "info", message: "x" }])).toBe(true);
    expect(isConfigValid([{ level: "error", message: "x" }])).toBe(false);
    expect(isConfigValid([])).toBe(true);
  });
});

describe("noiseDisabledReason", () => {
  it("explains why noise is unavailable per sim mode", () => {
    expect(noiseDisabledReason("statevector")).toContain("noiseless by design");
    expect(noiseDisabledReason("hardware")).toContain("physical noise");
    expect(noiseDisabledReason("qasm")).toBeNull();
    expect(noiseDisabledReason("density_matrix")).toBeNull();
  });
});

describe("buildExperimentConfig", () => {
  it("builds a minimal config without optional fields when defaults apply", () => {
    const cfg = buildExperimentConfig(baseState());
    expect(cfg).toEqual({
      num_qubits: 3,
      state_type: "GHZ",
      shots: 1024,
      noise_enabled: false,
      sim_mode: "qasm",
      visualization_type: "none",
    });
  });

  it("includes noise params only when noise is enabled", () => {
    const cfg = buildExperimentConfig(
      baseState({ noiseEnabled: true, noiseType: "depolarizing", errorRate: 0.2, readoutErrorRate: 0.1 }),
    );
    expect(cfg.noise_type).toBe("depolarizing");
    expect(cfg.error_rate).toBe(0.2);
    expect(cfg.readout_error_rate).toBe(0.1);
  });

  it("includes T1/T2 only for thermal relaxation noise", () => {
    const thermal = buildExperimentConfig(
      baseState({ noiseEnabled: true, noiseType: "thermal_relaxation", t1: 100, t2: 80 }),
    );
    expect(thermal.t1).toBe(100);
    expect(thermal.t2).toBe(80);

    const depol = buildExperimentConfig(
      baseState({ noiseEnabled: true, noiseType: "depolarizing", t1: 100, t2: 80 }),
    );
    expect(depol.t1).toBeUndefined();
    expect(depol.t2).toBeUndefined();
  });

  it("selects profile vs individual metrics based on metricsMode", () => {
    expect(buildExperimentConfig(baseState({ metricsEnabled: true, metricsMode: "profile" })).metrics).toBe(
      "structure",
    );
    expect(
      buildExperimentConfig(
        baseState({ metricsEnabled: true, metricsMode: "individual", selectedMetrics: ["ai", "ss"] }),
      ).metrics,
    ).toEqual(["ai", "ss"]);
    expect(buildExperimentConfig(baseState({ metricsEnabled: false })).metrics).toBeUndefined();
  });

  it("omits the RNG seed on hardware but keeps it otherwise", () => {
    expect(buildExperimentConfig(baseState({ rngSeed: 42 })).rng_seed).toBe(42);
    expect(buildExperimentConfig(baseState({ rngSeed: 42, simMode: "hardware" })).rng_seed).toBeUndefined();
  });

  it("includes multiple_runs only when greater than 1", () => {
    expect(buildExperimentConfig(baseState({ multipleRuns: 1 })).multiple_runs).toBeUndefined();
    expect(buildExperimentConfig(baseState({ multipleRuns: 5 })).multiple_runs).toBe(5);
  });

  it("assembles hardware params only in hardware mode", () => {
    const cfg = buildExperimentConfig(
      baseState({ simMode: "hardware", backendName: "ibm_test", optimizationLevel: 3, hardwareSession: true }),
    );
    expect(cfg.backend_name).toBe("ibm_test");
    expect(cfg.optimization_level).toBe(3);
    expect(cfg.hardware_session).toBe(true);

    const nonHw = buildExperimentConfig(baseState({ backendName: "ibm_test", optimizationLevel: 3 }));
    expect(nonHw.backend_name).toBeUndefined();
    expect(nonHw.optimization_level).toBeUndefined();
  });

  it("adds balance_circuit and experiment_type when set", () => {
    const cfg = buildExperimentConfig(
      baseState({ balanceCircuit: true, experimentType: "decoherence" }),
    );
    expect(cfg.balance_circuit).toBe("gate_count");
    expect(cfg.experiment_type).toBe("decoherence");
  });
});
