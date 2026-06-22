/**
 * Tests for the BlochVisualizerData -> component-prop adapters. These are pure
 * transforms over the backend payload shape; no rendering involved.
 */
import { describe, expect, it } from "vitest";
import type { BlochVisualizerData } from "../../../lib/types";
import {
  blochDataToAllQubits,
  blochDataToFingerprints,
  blochDataToPairCfg,
  blochDataToStateCfg,
  getQubitPairs,
} from "../experimentAdapter";

function makeData(over: Partial<BlochVisualizerData> = {}): BlochVisualizerData {
  return {
    experiment_id: "exp1",
    state_type: "GHZ",
    num_qubits: 2,
    noise_type: "depolarizing",
    error_rate: 0.1,
    fidelity: 0.9,
    source_mode: "density_matrix",
    qubits: [
      { qubit_index: 0, bloch_vector: { rx: 0, ry: 0, rz: 0.8 }, purity: 0.99 },
      { qubit_index: 1, bloch_vector: { rx: 0, ry: 0, rz: 0 }, purity: 0.5 },
    ],
    pairs: [
      {
        qubit_i: 0,
        qubit_j: 1,
        correlators: { zi: 0.1, iz: 0.2, zz: 0.9, xx: 0.3, yy: -0.3 },
        mutual_information: 1.234,
      },
    ],
    mi_matrix: [
      [0, 1.234],
      [1.234, 0],
    ],
    metrics: {
      asymmetry_index: { value: 0.42, ci95: null },
      structure_score: { value: 0.7, ci95: [0.6, 0.8] },
    },
    ...over,
  };
}

describe("blochDataToStateCfg", () => {
  it("passes through the bloch vector and assigns the per-qubit color", () => {
    const cfg = blochDataToStateCfg(makeData(), 0);
    expect(cfg.bloch).toEqual({ rx: 0, ry: 0, rz: 0.8 });
    expect(cfg.color).toBe("#ff9933"); // QUBIT_COLORS[0]
    expect(cfg.name).toBe("Q0 (GHZ)");
    expect(cfg.uniform).toBe(false);
  });

  it("classifies zBasisSignal by bloch vector length", () => {
    // |r| = 0.8 -> strong
    expect(blochDataToStateCfg(makeData(), 0).zBasisSignal).toBe("strong");
    // |r| = 0 -> zero
    expect(blochDataToStateCfg(makeData(), 1).zBasisSignal).toBe("zero");
    // weak band
    const weak = makeData({
      qubits: [
        { qubit_index: 0, bloch_vector: { rx: 0, ry: 0, rz: 0.3 }, purity: 0.8 },
      ],
    });
    expect(blochDataToStateCfg(weak, 0).zBasisSignal).toBe("weak");
  });

  it("adds a mixed-state note for low purity and a pure note for high purity", () => {
    expect(blochDataToStateCfg(makeData(), 0).insight).toContain("Nearly pure");
    expect(blochDataToStateCfg(makeData(), 1).insight).toContain("Significantly mixed");
  });

  it("notes the diagonal-estimate limitation when source_mode says so", () => {
    const cfg = blochDataToStateCfg(
      makeData({ source_mode: "diagonal_estimate" }),
      0,
    );
    expect(cfg.insight).toContain("diagonal estimate");
  });

  it("throws when the qubit index is out of range", () => {
    expect(() => blochDataToStateCfg(makeData(), 9)).toThrow(/Qubit 9 not found/);
  });
});

describe("blochDataToAllQubits", () => {
  it("maps every qubit to a {bloch, color, label} entry", () => {
    const all = blochDataToAllQubits(makeData());
    expect(all).toHaveLength(2);
    expect(all[0]).toEqual({
      bloch: { rx: 0, ry: 0, rz: 0.8 },
      color: "#ff9933",
      label: "Q0",
    });
    expect(all[1].label).toBe("Q1");
  });
});

describe("blochDataToPairCfg", () => {
  it("finds the pair regardless of argument order", () => {
    const a = blochDataToPairCfg(makeData(), 0, 1);
    const b = blochDataToPairCfg(makeData(), 1, 0);
    expect(a.correlators).toEqual(b.correlators);
    expect(a.mutualInfo).toBeCloseTo(1.234);
  });

  it("copies correlators and formats the MI insight", () => {
    const { stateCfg, correlators, mutualInfo } = blochDataToPairCfg(makeData(), 0, 1);
    expect(correlators.zz).toBe(0.9);
    expect(mutualInfo).toBeCloseTo(1.234);
    expect(stateCfg.zBasisSignal).toBe("strong"); // |zz| = 0.9 > 0.1
    expect(stateCfg.insight).toContain("MI(Q0:Q1) = 1.2340");
  });

  it("falls back to zeroed correlators when the pair is absent", () => {
    const { correlators, mutualInfo } = blochDataToPairCfg(makeData({ pairs: [] }), 0, 1);
    expect(correlators).toEqual({ zi: 0, iz: 0, zz: 0, xx: 0, yy: 0 });
    expect(mutualInfo).toBe(0);
  });
});

describe("blochDataToFingerprints", () => {
  it("builds a single fingerprint entry from metric values", () => {
    const fps = blochDataToFingerprints(makeData());
    expect(fps).toHaveLength(1);
    expect(fps[0].fingerprint).toEqual([0.42, 0.7]);
    expect(fps[0].noiseStrength).toBe(0.1);
    expect(fps[0].topology).toBe("depolarizing");
    expect(fps[0].label).toBe("GHZ 2q depolarizing");
  });

  it("returns an empty array when metrics are null or empty", () => {
    expect(blochDataToFingerprints(makeData({ metrics: null }))).toEqual([]);
    expect(blochDataToFingerprints(makeData({ metrics: {} }))).toEqual([]);
  });

  it("labels clean runs and zeroes noise when noise fields are absent", () => {
    const fps = blochDataToFingerprints(
      makeData({ noise_type: null, error_rate: null }),
    );
    expect(fps[0].topology).toBe("none");
    expect(fps[0].noiseStrength).toBe(0);
    expect(fps[0].label).toBe("GHZ 2q clean");
  });
});

describe("getQubitPairs", () => {
  it("returns the index tuples of every pair", () => {
    expect(getQubitPairs(makeData())).toEqual([[0, 1]]);
  });
});
