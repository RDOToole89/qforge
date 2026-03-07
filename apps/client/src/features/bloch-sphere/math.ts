/**
 * Math utilities for Bloch sphere visualization.
 * Includes vector helpers, point generation, channel compilation, and noise application.
 */
import * as THREE from "three";
import type {
  BlochMapDef,
  BlochMapFn,
  PTMFn,
  RuntimeChannel,
  ChannelConfig,
  ProbeStateConfig,
  TopologyConfig,
  TwoQubitPoint,
  NoisedTwoQubitPoint,
} from "./types";

/** Shorthand for creating a THREE.Vector3 */
export const V3 = (x: number, y: number, z: number): THREE.Vector3 =>
  new THREE.Vector3(x, y, z);

/** Full circle in radians */
export const TAU = Math.PI * 2;

/** Linear interpolation */
export const lerp = (a: number, b: number, t: number): number =>
  a + (b - a) * t;

/**
 * Generate evenly-distributed points on a unit sphere using the golden angle.
 */
export function spherePoints(n = 350): THREE.Vector3[] {
  const pts: THREE.Vector3[] = [];
  const ga = Math.PI * (3 - Math.sqrt(5));
  for (let i = 0; i < n; i++) {
    const y = 1 - (i / (n - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const t = ga * i;
    pts.push(V3(r * Math.cos(t), y, r * Math.sin(t)));
  }
  return pts;
}

/**
 * Generate sample points representing a quantum state on the Bloch sphere.
 * For maximally mixed states (bloch ~ 0), generates a small cloud at the origin.
 * For pure/partially-mixed states, generates a cluster around the Bloch vector.
 */
export function statePoints(
  stateCfg: ProbeStateConfig,
  n = 350,
): THREE.Vector3[] {
  const { rx, ry, rz } = stateCfg.bloch;
  const bLen = Math.sqrt(rx * rx + ry * ry + rz * rz);

  if (bLen < 0.01) {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i < n; i++) {
      const r = 0.12 * Math.cbrt(Math.random());
      const t = Math.acos(2 * Math.random() - 1);
      const ph = TAU * Math.random();
      pts.push(
        V3(
          r * Math.sin(t) * Math.cos(ph),
          r * Math.sin(t) * Math.sin(ph),
          r * Math.cos(t),
        ),
      );
    }
    return pts;
  }

  const pts: THREE.Vector3[] = [];
  const center = V3(rx, ry, rz);
  for (let i = 0; i < n; i++) {
    const spread = 0.15;
    const pt = center.clone().add(
      V3(
        (Math.random() - 0.5) * spread,
        (Math.random() - 0.5) * spread,
        (Math.random() - 0.5) * spread,
      ),
    );
    if (pt.length() > 1) pt.normalize();
    pts.push(pt);
  }
  return pts;
}

/**
 * Generate 2-qubit sample points from a probe state's correlator signature.
 */
export function generate2QFromState(
  stateCfg: ProbeStateConfig,
  n = 400,
): TwoQubitPoint[] {
  const c = stateCfg.correlators;
  const pts: TwoQubitPoint[] = [];
  for (let i = 0; i < n; i++) {
    const spread = 0.15;
    pts.push({
      r1: V3(0, 0, 0),
      r2: V3(0, 0, 0),
      zi: (c.zi ?? 0) + (Math.random() - 0.5) * spread,
      iz: (c.iz ?? 0) + (Math.random() - 0.5) * spread,
      zz: (c.zz ?? 0) + (Math.random() - 0.5) * spread,
      xx: (c.xx ?? 0) + (Math.random() - 0.5) * spread,
      yy: (c.yy ?? 0) + (Math.random() - 0.5) * spread,
    });
  }
  return pts;
}

/**
 * Apply 2-qubit noise to correlator samples given a topology and error rate.
 */
export function apply2QNoise(
  pts: TwoQubitPoint[],
  topo: TopologyConfig,
  p: number,
): NoisedTwoQubitPoint[] {
  const decay = topo.singleQubitDecay ?? 1;
  const pZ = topo.preserveZ;
  return pts.map((pt) => {
    const s = pZ ? 1 : 1 - decay * p;
    const nzi = s * pt.zi;
    const niz = s * pt.iz;
    const base = s * s * pt.zz;
    const zz =
      base + (topo.corrGrowZZ ?? 0) * p * (1 - Math.abs(base));
    return { zi: nzi, iz: niz, zz };
  });
}

/**
 * Compile a Bloch map definition (string expressions) into an executable function.
 * Uses Function constructor to evaluate expressions with rx, ry, rz, p, sqrt.
 */
export function compileBlochMap(mapDef: BlochMapDef): BlochMapFn {
  const mk = (expr: string) => {
    return (rx: number, ry: number, rz: number, p: number): number => {
      try {
        return new Function(
          "rx",
          "ry",
          "rz",
          "p",
          "sqrt",
          `"use strict"; return (${expr});`,
        )(rx, ry, rz, p, Math.sqrt) as number;
      } catch {
        return 0;
      }
    };
  };

  const fRx = mk(mapDef.rx);
  const fRy = mk(mapDef.ry);
  const fRz = mk(mapDef.rz);

  return (r, p) =>
    V3(fRx(r.x, r.y, r.z, p), fRy(r.x, r.y, r.z, p), fRz(r.x, r.y, r.z, p));
}

/**
 * Compile a Bloch map into a Pauli Transfer Matrix (PTM) generator.
 * The PTM is computed by probing the channel with basis vectors.
 */
export function compilePTM(mapDef: BlochMapDef): PTMFn {
  return (p: number): number[][] => {
    const fn = compileBlochMap(mapDef);
    const o = fn({ x: 0, y: 0, z: 0 }, p);
    const ex = fn({ x: 1, y: 0, z: 0 }, p);
    const ey = fn({ x: 0, y: 1, z: 0 }, p);
    const ez = fn({ x: 0, y: 0, z: 1 }, p);
    return [
      [1, 0, 0, 0],
      [o.x, ex.x - o.x, ey.x - o.x, ez.x - o.x],
      [o.y, ex.y - o.y, ey.y - o.y, ez.y - o.y],
      [o.z, ex.z - o.z, ey.z - o.z, ez.z - o.z],
    ];
  };
}

/**
 * Build runtime channels by compiling all Bloch map definitions
 * into executable apply/ptm functions.
 */
export function buildRuntime(
  channels: Record<string, ChannelConfig>,
): Record<string, RuntimeChannel> {
  const result: Record<string, RuntimeChannel> = {};
  for (const [k, ch] of Object.entries(channels)) {
    result[k] = {
      ...ch,
      apply: compileBlochMap(ch.blochMap),
      ptm: compilePTM(ch.blochMap),
    };
  }
  return result;
}
