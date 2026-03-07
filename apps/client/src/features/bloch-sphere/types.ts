/**
 * Type definitions for the Bloch Sphere CPTP Visualizer.
 */

/** 3D Bloch vector coordinates */
export interface BlochVector {
  rx: number;
  ry: number;
  rz: number;
}

/** Two-qubit correlator signature */
export interface CorrelatorSignature {
  zi?: number;
  iz?: number;
  zz?: number;
  xx?: number;
  yy?: number;
  xz?: number;
  zx?: number;
}

/** Configuration for a probe state */
export interface ProbeStateConfig {
  name: string;
  desc: string;
  bloch: BlochVector;
  correlators: CorrelatorSignature;
  color: string;
  zBasisSignal: "strong" | "weak" | "zero";
  insight: string;
  uniform: boolean;
}

/** Bloch map definition using string expressions */
export interface BlochMapDef {
  rx: string;
  ry: string;
  rz: string;
}

/** Configuration for a quantum channel */
export interface ChannelConfig {
  name: string;
  desc: string;
  formula: string;
  blochMap: BlochMapDef;
  kraus: string;
  geometry: string;
  insight: string;
}

/** Configuration for a noise topology */
export interface TopologyConfig {
  name: string;
  desc: string;
  corrGrowXX: number;
  corrGrowYY: number;
  corrGrowZZ: number;
  singleQubitDecay: number;
  preserveZ?: boolean;
}

/** Display configuration */
export interface DisplayConfig {
  pointCount: number;
  backgroundColor: string;
}

/** Experimental data fingerprint entry */
export interface ExperimentalDataEntry {
  label: string;
  noiseStrength: number;
  topology: string;
  fingerprint: number[];
}

/** Top-level Bloch config shape */
export interface BlochConfig {
  states: Record<string, ProbeStateConfig>;
  channels: Record<string, ChannelConfig>;
  topologies: Record<string, TopologyConfig>;
  experimentalData: ExperimentalDataEntry[];
  display: DisplayConfig;
}

/** A compiled Bloch map function: (r, p) => transformed vector */
export type BlochMapFn = (
  r: { x: number; y: number; z: number },
  p: number,
) => import("three").Vector3;

/** A compiled PTM function: (p) => 4x4 matrix */
export type PTMFn = (p: number) => number[][];

/** Runtime channel with compiled apply/ptm functions */
export interface RuntimeChannel extends ChannelConfig {
  apply: BlochMapFn;
  ptm: PTMFn;
}

/** A 2-qubit sample point */
export interface TwoQubitPoint {
  r1: import("three").Vector3;
  r2: import("three").Vector3;
  zi: number;
  iz: number;
  zz: number;
  xx: number;
  yy: number;
}

/** Noised 2-qubit sample (reduced correlators) */
export interface NoisedTwoQubitPoint {
  zi: number;
  iz: number;
  zz: number;
}
