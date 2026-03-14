/**
 * Converts BlochVisualizerData (from the Python backend) into the existing
 * component prop shapes so BlochScene, TwoQubitScene, etc. work unchanged.
 */

import type { BlochVisualizerData } from "../../lib/types";
import type {
  ProbeStateConfig,
  CorrelatorSignature,
  ExperimentalDataEntry,
} from "./types";

/** Per-qubit color palette (up to 8 qubits) */
const QUBIT_COLORS = [
  "#ff9933", "#44ddff", "#44ff88", "#b48cff",
  "#ff4466", "#ffdd44", "#44ffdd", "#ff88cc",
];

/**
 * Convert one qubit's reduced state into a ProbeStateConfig for BlochScene.
 */
export function blochDataToStateCfg(
  data: BlochVisualizerData,
  qubitIndex: number,
): ProbeStateConfig {
  const qubit = data.qubits[qubitIndex];
  if (!qubit) {
    throw new Error(`Qubit ${qubitIndex} not found in data`);
  }

  const { rx, ry, rz } = qubit.bloch_vector;
  const bLen = Math.sqrt(rx * rx + ry * ry + rz * rz);

  let insight = `Q${qubitIndex} reduced state — purity: ${qubit.purity.toFixed(3)}`;
  if (data.source_mode === "diagonal_estimate") {
    insight += " (diagonal estimate: X,Y components unavailable from Z-basis measurements)";
  }
  if (qubit.purity < 0.6) {
    insight += ". Significantly mixed — this qubit is entangled with others or has decohered.";
  } else if (qubit.purity > 0.95) {
    insight += ". Nearly pure — this qubit retains most of its coherence.";
  }

  return {
    name: `Q${qubitIndex} (${data.state_type})`,
    desc: `Reduced state of qubit ${qubitIndex}`,
    bloch: { rx, ry, rz },
    correlators: {},
    color: QUBIT_COLORS[qubitIndex % QUBIT_COLORS.length],
    zBasisSignal: bLen < 0.05 ? "zero" : bLen < 0.5 ? "weak" : "strong",
    insight,
    uniform: false,
  };
}

/**
 * Build an array of {bloch, color, label} for the "All qubits" multi-dot view.
 */
export function blochDataToAllQubits(
  data: BlochVisualizerData,
): Array<{ bloch: { rx: number; ry: number; rz: number }; color: string; label: string }> {
  return data.qubits.map((q) => ({
    bloch: q.bloch_vector,
    color: QUBIT_COLORS[q.qubit_index % QUBIT_COLORS.length],
    label: `Q${q.qubit_index}`,
  }));
}

/**
 * Convert a qubit pair into a ProbeStateConfig with correlator data
 * for use with TwoQubitScene / CorrelatorBars.
 */
export function blochDataToPairCfg(
  data: BlochVisualizerData,
  qubitI: number,
  qubitJ: number,
): { stateCfg: ProbeStateConfig; correlators: CorrelatorSignature; mutualInfo: number } {
  const pair = data.pairs.find(
    (p) => (p.qubit_i === qubitI && p.qubit_j === qubitJ) ||
           (p.qubit_i === qubitJ && p.qubit_j === qubitI),
  );

  const corrs: CorrelatorSignature = pair
    ? { ...pair.correlators }
    : { zi: 0, iz: 0, zz: 0, xx: 0, yy: 0 };

  const mi = pair?.mutual_information ?? 0;

  const stateCfg: ProbeStateConfig = {
    name: `Q${qubitI}-Q${qubitJ} (${data.state_type})`,
    desc: `Two-qubit correlators`,
    bloch: { rx: 0, ry: 0, rz: 0 },
    correlators: corrs,
    color: QUBIT_COLORS[qubitI % QUBIT_COLORS.length],
    zBasisSignal: Math.abs(corrs.zz ?? 0) > 0.1 ? "strong" : "weak",
    insight: `MI(Q${qubitI}:Q${qubitJ}) = ${mi.toFixed(4)} bits`,
    uniform: false,
  };

  return { stateCfg, correlators: corrs, mutualInfo: mi };
}

/**
 * Convert metrics into ExperimentalDataEntry[] for FingerprintViewer.
 */
export function blochDataToFingerprints(
  data: BlochVisualizerData,
): ExperimentalDataEntry[] {
  if (!data.metrics) return [];

  const metricNames = Object.keys(data.metrics);
  if (metricNames.length === 0) return [];

  // Create a single fingerprint entry from all metric values
  const fingerprint = metricNames.map((name) => data.metrics![name].value);

  return [{
    label: `${data.state_type} ${data.num_qubits}q ${data.noise_type ?? "clean"}`,
    noiseStrength: data.error_rate ?? 0,
    topology: data.noise_type ?? "none",
    fingerprint,
  }];
}

/**
 * Get all valid qubit pairs from the data.
 */
export function getQubitPairs(data: BlochVisualizerData): [number, number][] {
  return data.pairs.map((p) => [p.qubit_i, p.qubit_j] as [number, number]);
}
