/**
 * Pure snapshot-interpolation logic for the decoherence sweep animation.
 *
 * Extracted from `useSweepMode` so the interpolation can be unit-tested without
 * rendering the hook. Given an ordered list of backend snapshots and a progress
 * value in [0, 1], it linearly interpolates a synthetic in-between snapshot.
 */

import type { BlochVisualizerData } from "../../lib/types";

/** Linear interpolation between `x` and `y` by factor `t` in [0, 1]. */
export function lerp(x: number, y: number, t: number): number {
  return x + (y - x) * t;
}

/**
 * Interpolate between sweep snapshots based on `progress` (0..1).
 *
 * Returns null when there are no snapshots. With a single snapshot, that
 * snapshot is returned unchanged. Otherwise progress maps onto the snapshot
 * index space and the bracketing pair is blended component-wise.
 */
export function interpolateSnapshot(
  snapshots: BlochVisualizerData[],
  progress: number,
): BlochVisualizerData | null {
  if (snapshots.length === 0) return null;
  if (snapshots.length === 1) return snapshots[0];

  // Map progress to snapshot index (fractional).
  const fIdx = progress * (snapshots.length - 1);
  const lo = Math.floor(fIdx);
  const hi = Math.min(lo + 1, snapshots.length - 1);
  const t = fIdx - lo; // interpolation factor 0..1

  if (lo === hi) return snapshots[lo];
  const a = snapshots[lo];
  const b = snapshots[hi];

  const mix = (x: number, y: number) => lerp(x, y, t);

  // Interpolate qubits.
  const qubits = a.qubits.map((qa, i) => {
    const qb = b.qubits[i];
    return {
      qubit_index: qa.qubit_index,
      bloch_vector: {
        rx: mix(qa.bloch_vector.rx, qb.bloch_vector.rx),
        ry: mix(qa.bloch_vector.ry, qb.bloch_vector.ry),
        rz: mix(qa.bloch_vector.rz, qb.bloch_vector.rz),
      },
      purity: mix(qa.purity, qb.purity),
    };
  });

  // Interpolate pairs.
  const pairs = a.pairs.map((pa, i) => {
    const pb = b.pairs[i];
    return {
      qubit_i: pa.qubit_i,
      qubit_j: pa.qubit_j,
      correlators: {
        zi: mix(pa.correlators.zi, pb.correlators.zi),
        iz: mix(pa.correlators.iz, pb.correlators.iz),
        zz: mix(pa.correlators.zz, pb.correlators.zz),
        xx: mix(pa.correlators.xx, pb.correlators.xx),
        yy: mix(pa.correlators.yy, pb.correlators.yy),
      },
      mutual_information: mix(pa.mutual_information, pb.mutual_information),
    };
  });

  // Interpolate MI matrix.
  const mi_matrix = a.mi_matrix.map((row, i) =>
    row.map((v, j) => mix(v, b.mi_matrix[i][j])),
  );

  return {
    ...a,
    error_rate: mix(a.error_rate ?? 0, b.error_rate ?? 0),
    fidelity:
      a.fidelity != null && b.fidelity != null
        ? mix(a.fidelity, b.fidelity)
        : null,
    qubits,
    pairs,
    mi_matrix,
  };
}
