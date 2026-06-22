/**
 * Tests for the pure sweep snapshot-interpolation helpers extracted from
 * useSweepMode.
 */
import { describe, expect, it } from "vitest";
import type { BlochVisualizerData } from "../../../lib/types";
import { interpolateSnapshot, lerp } from "../sweepInterpolation";

function snap(rz: number, mi: number, rate: number, fidelity: number | null): BlochVisualizerData {
  return {
    experiment_id: "exp",
    state_type: "GHZ",
    num_qubits: 2,
    noise_type: "depolarizing",
    error_rate: rate,
    fidelity,
    source_mode: "density_matrix",
    qubits: [
      { qubit_index: 0, bloch_vector: { rx: 0, ry: 0, rz }, purity: rz },
      { qubit_index: 1, bloch_vector: { rx: 0, ry: 0, rz: 0 }, purity: 1 },
    ],
    pairs: [
      {
        qubit_i: 0,
        qubit_j: 1,
        correlators: { zi: 0, iz: 0, zz: rz, xx: 0, yy: 0 },
        mutual_information: mi,
      },
    ],
    mi_matrix: [
      [0, mi],
      [mi, 0],
    ],
    metrics: null,
  };
}

describe("lerp", () => {
  it("interpolates linearly", () => {
    expect(lerp(0, 10, 0)).toBe(0);
    expect(lerp(0, 10, 1)).toBe(10);
    expect(lerp(0, 10, 0.5)).toBe(5);
    expect(lerp(2, 4, 0.25)).toBe(2.5);
  });
});

describe("interpolateSnapshot", () => {
  it("returns null for an empty snapshot list", () => {
    expect(interpolateSnapshot([], 0.5)).toBeNull();
  });

  it("returns the single snapshot unchanged", () => {
    const only = snap(1, 2, 0.1, 0.9);
    expect(interpolateSnapshot([only], 0.7)).toBe(only);
  });

  it("reproduces the endpoint values at progress 0 and 1", () => {
    const a = snap(1, 2, 0, 1);
    const b = snap(0, 0, 0.5, 0.5);
    // progress 0 blends with t=0, yielding a fresh object equal to `a`.
    expect(interpolateSnapshot([a, b], 0)).toEqual(a);
    // progress 1 lands on the final index exactly and returns it by identity.
    expect(interpolateSnapshot([a, b], 1)).toBe(b);
  });

  it("blends qubits, pairs, MI matrix, error_rate, and fidelity at the midpoint", () => {
    const a = snap(1, 2, 0, 1);
    const b = snap(0, 0, 0.5, 0.5);
    const mid = interpolateSnapshot([a, b], 0.5)!;

    expect(mid.qubits[0].bloch_vector.rz).toBeCloseTo(0.5);
    expect(mid.qubits[0].purity).toBeCloseTo(0.5);
    expect(mid.pairs[0].mutual_information).toBeCloseTo(1);
    expect(mid.pairs[0].correlators.zz).toBeCloseTo(0.5);
    expect(mid.mi_matrix[0][1]).toBeCloseTo(1);
    expect(mid.error_rate).toBeCloseTo(0.25);
    expect(mid.fidelity).toBeCloseTo(0.75);
  });

  it("picks the correct bracketing pair for a 3-snapshot sweep", () => {
    const a = snap(0, 0, 0, 1);
    const b = snap(1, 1, 0.25, 0.8);
    const c = snap(2, 2, 0.5, 0.6);
    // progress 0.25 -> fIdx = 0.5 -> between a and b, t=0.5
    const r = interpolateSnapshot([a, b, c], 0.25)!;
    expect(r.qubits[0].bloch_vector.rz).toBeCloseTo(0.5);
    expect(r.error_rate).toBeCloseTo(0.125);
  });

  it("yields null fidelity when either endpoint fidelity is null", () => {
    const a = snap(1, 2, 0, null);
    const b = snap(0, 0, 0.5, 0.5);
    expect(interpolateSnapshot([a, b], 0.5)!.fidelity).toBeNull();
  });

  it("treats missing error_rate as zero", () => {
    const a = { ...snap(1, 2, 0, 1), error_rate: null };
    const b = { ...snap(0, 0, 0, 1), error_rate: 0.4 };
    expect(interpolateSnapshot([a, b], 0.5)!.error_rate).toBeCloseTo(0.2);
  });
});
