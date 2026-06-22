/**
 * Math utilities for Bloch sphere visualization.
 * Includes vector helpers, point generation, channel compilation, and noise application.
 */
import * as THREE from "three";
import { Matrix, EigenvalueDecomposition } from "ml-matrix";
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

// ── State vector to Bloch coordinates ───────────────────────────

/** Complex number as [real, imaginary], matching circuit-builder convention */
type Complex = [number, number];

/**
 * Extract single-qubit Bloch vector from an n-qubit state vector
 * via partial trace over all other qubits.
 *
 * Given |ψ⟩ in C^{2^n}, computes the reduced density matrix ρ_k for qubit k,
 * then returns Pauli expectations: rx = Tr(ρσ_x), ry = Tr(ρσ_y), rz = Tr(ρσ_z).
 *
 * Uses MSB qubit convention matching useSimulator.ts.
 */
export function stateVectorToBloch(
  sv: Complex[],
  qubitIndex: number,
  numQubits: number,
): { rx: number; ry: number; rz: number } {
  const dim = 1 << numQubits;
  const bit = 1 << (numQubits - 1 - qubitIndex);

  // Accumulate 2x2 reduced density matrix elements
  let rho00 = 0;
  let rho01_re = 0;
  let rho01_im = 0;
  let rho11 = 0;

  for (let i = 0; i < dim; i++) {
    if (i & bit) {
      // qubit k is |1⟩ — contributes to ρ_11
      rho11 += sv[i][0] * sv[i][0] + sv[i][1] * sv[i][1];
    } else {
      // qubit k is |0⟩ — contributes to ρ_00 and ρ_01
      rho00 += sv[i][0] * sv[i][0] + sv[i][1] * sv[i][1];
      const j = i | bit; // partner state with qubit k flipped to |1⟩
      // Accumulate conj(sv[i]) * sv[j] = Σ conj(a_{0,rest}) a_{1,rest} = ρ_10.
      rho01_re += sv[i][0] * sv[j][0] + sv[i][1] * sv[j][1]; // Re(ρ_10) = Re(ρ_01)
      rho01_im += sv[i][0] * sv[j][1] - sv[i][1] * sv[j][0]; // Im(ρ_10) = -Im(ρ_01)
    }
  }

  // Note: the accumulators above hold ρ_10 (not ρ_01). Since Re(ρ_10)=Re(ρ_01)
  // and Im(ρ_10)=-Im(ρ_01):
  //   ⟨σ_x⟩ =  2 Re(ρ_01) =  2·rho01_re
  //   ⟨σ_y⟩ = -2 Im(ρ_01) =  2·rho01_im   (the +y eigenstate (|0⟩+i|1⟩)/√2 → +1)
  //   ⟨σ_z⟩ = ρ_00 − ρ_11
  return {
    rx: 2 * rho01_re,
    ry: 2 * rho01_im,
    rz: rho00 - rho11,
  };
}

/**
 * Convert Bloch sphere coordinates to Three.js coordinates.
 * Canonical convention: Three.js Y = Bloch Z (up), Three.js Z = Bloch Y.
 */
export function blochToThree(rx: number, ry: number, rz: number): THREE.Vector3 {
  return new THREE.Vector3(rx, rz, ry);
}

// ── Two-qubit correlations ──────────────────────────────────────

/**
 * Compute ⟨Z_i Z_j⟩ for a qubit pair from an n-qubit state vector.
 * Returns the raw expectation value (not the connected correlator).
 */
export function expectZZ(
  sv: Complex[],
  qi: number,
  qj: number,
  numQubits: number,
): number {
  const dim = 1 << numQubits;
  const bitI = 1 << (numQubits - 1 - qi);
  const bitJ = 1 << (numQubits - 1 - qj);
  let val = 0;
  for (let k = 0; k < dim; k++) {
    const prob = sv[k][0] * sv[k][0] + sv[k][1] * sv[k][1];
    const zi = (k & bitI) ? -1 : 1;
    const zj = (k & bitJ) ? -1 : 1;
    val += zi * zj * prob;
  }
  return val;
}

/**
 * Compute ⟨Z_i⟩ for a single qubit from an n-qubit state vector.
 */
export function expectZ(
  sv: Complex[],
  qi: number,
  numQubits: number,
): number {
  const dim = 1 << numQubits;
  const bit = 1 << (numQubits - 1 - qi);
  let val = 0;
  for (let k = 0; k < dim; k++) {
    const prob = sv[k][0] * sv[k][0] + sv[k][1] * sv[k][1];
    val += ((k & bit) ? -1 : 1) * prob;
  }
  return val;
}

/**
 * Compute the connected correlation matrix ΔCov(i,j) = ⟨Z_i Z_j⟩ - ⟨Z_i⟩⟨Z_j⟩
 * for all qubit pairs. This is zero for product states and nonzero for
 * entangled/correlated states. Diagonal entries are Var(Z_i) = 1 - ⟨Z_i⟩².
 */
export function correlationMatrix(
  sv: Complex[],
  numQubits: number,
): number[][] {
  const zExpects: number[] = [];
  for (let i = 0; i < numQubits; i++) {
    zExpects.push(expectZ(sv, i, numQubits));
  }

  const mat: number[][] = [];
  for (let i = 0; i < numQubits; i++) {
    const row: number[] = [];
    for (let j = 0; j < numQubits; j++) {
      if (i === j) {
        row.push(1 - zExpects[i] * zExpects[i]); // Var(Z_i)
      } else {
        row.push(expectZZ(sv, i, j, numQubits) - zExpects[i] * zExpects[j]);
      }
    }
    mat.push(row);
  }
  return mat;
}

/**
 * Compute the Wootters concurrence of the 2-qubit reduced density matrix for
 * qubits (qi, qj) extracted from an n-qubit pure state vector.
 *
 * This is the exact Wootters formula — no approximations:
 *   1. Partial-trace the statevector over all other qubits to get ρ (4×4).
 *   2. ρ̃ = (σ_y⊗σ_y) ρ* (σ_y⊗σ_y).
 *   3. P = ρ ρ̃ (eigenvalues are real and ≥ 0).
 *   4. Eigenvalues of the complex matrix P are obtained via the real 8×8
 *      embedding E = [[A,-B],[B,A]] where P = A + iB; each eigenvalue of P
 *      appears twice among E's eigenvalues.
 *   5. λ_k = √(max(0, e_k)) sorted descending; deduplicate by taking the
 *      values at indices [0,2,4,6]. Then C = max(0, λ1 − λ2 − λ3 − λ4),
 *      clamped to [0, 1].
 *
 * Uses the MSB qubit convention (qubit 0 = MSB, bit = 1<<(n-1-q)) consistent
 * with stateVectorToBloch.
 */
export function pairConcurrence(
  sv: Complex[],
  qi: number,
  qj: number,
  numQubits: number,
): number {
  if (numQubits < 2) return 0;

  const dim = 1 << numQubits;
  const bitI = 1 << (numQubits - 1 - qi);
  const bitJ = 1 << (numQubits - 1 - qj);

  // Compute 4×4 reduced density matrix ρ_{ij} by partial trace.
  // Basis: |00⟩, |01⟩, |10⟩, |11⟩ for qubits (qi, qj).
  const rho_re: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  const rho_im: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];

  for (let k = 0; k < dim; k++) {
    const row = ((k & bitI) ? 2 : 0) | ((k & bitJ) ? 1 : 0);
    for (let l = 0; l < dim; l++) {
      // Check that k and l agree on all qubits except qi and qj.
      const mask = ~(bitI | bitJ);
      if ((k & mask) !== (l & mask)) continue;
      const col = ((l & bitI) ? 2 : 0) | ((l & bitJ) ? 1 : 0);
      // ρ[row][col] += conj(sv[k]) * sv[l]
      rho_re[row][col] += sv[k][0] * sv[l][0] + sv[k][1] * sv[l][1];
      rho_im[row][col] += sv[k][0] * sv[l][1] - sv[k][1] * sv[l][0];
    }
  }

  // σ_y⊗σ_y is a real matrix in the 00,01,10,11 basis.
  const sysy = [[0,0,0,-1],[0,0,1,0],[0,1,0,0],[-1,0,0,0]];

  // ρ̃ = (σy⊗σy) ρ* (σy⊗σy). conj(ρ) has the same real part and negated imag.
  // Step 1: tmp = ρ* (σy⊗σy)
  const tmp_re: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  const tmp_im: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      for (let k = 0; k < 4; k++) {
        tmp_re[i][j] += rho_re[i][k] * sysy[k][j];
        tmp_im[i][j] += -rho_im[i][k] * sysy[k][j];
      }
    }
  }
  // Step 2: ρ̃ = (σy⊗σy) tmp
  const rtilde_re: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  const rtilde_im: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      for (let k = 0; k < 4; k++) {
        rtilde_re[i][j] += sysy[i][k] * tmp_re[k][j];
        rtilde_im[i][j] += sysy[i][k] * tmp_im[k][j];
      }
    }
  }

  // P = ρ ρ̃ (complex 4×4 matrix multiply). P = A + iB.
  const A: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  const B: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      for (let k = 0; k < 4; k++) {
        A[i][j] += rho_re[i][k] * rtilde_re[k][j] - rho_im[i][k] * rtilde_im[k][j];
        B[i][j] += rho_re[i][k] * rtilde_im[k][j] + rho_im[i][k] * rtilde_re[k][j];
      }
    }
  }

  // Eigenvalues of the complex matrix P via the real 8×8 embedding
  // E = [[A, -B], [B, A]]. Each eigenvalue of P appears twice in E.
  const E: number[][] = Array.from({ length: 8 }, () => new Array(8).fill(0));
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      E[i][j] = A[i][j];          // top-left  A
      E[i][j + 4] = -B[i][j];     // top-right -B
      E[i + 4][j] = B[i][j];      // bottom-left  B
      E[i + 4][j + 4] = A[i][j];  // bottom-right A
    }
  }

  const eig = new EigenvalueDecomposition(new Matrix(E));
  const realEig = eig.realEigenvalues;

  // sqrt(max(0, e)) for each, sorted descending. Eigenvalues are duplicated,
  // so the distinct Wootters λ's live at indices [0, 2, 4, 6].
  const sqrtEig = realEig.map((e) => Math.sqrt(Math.max(0, e)));
  sqrtEig.sort((a, b) => b - a);

  const lambda1 = sqrtEig[0];
  const lambda2 = sqrtEig[2];
  const lambda3 = sqrtEig[4];
  const lambda4 = sqrtEig[6];

  const C = lambda1 - lambda2 - lambda3 - lambda4;
  return Math.min(1, Math.max(0, C));
}

// ── Multipartite entanglement ───────────────────────────────────

/**
 * Compute the 1-tangle (concurrence of qubit i with the rest of the system)
 * for a pure global state. For pure states:
 *   C(i|rest)² = 4 det(ρ_i)
 * where ρ_i is the single-qubit reduced density matrix.
 * This equals the linear entropy S_L = 2(1 - Tr(ρ_i²)).
 */
export function oneTangle(
  sv: Complex[],
  qubitIndex: number,
  numQubits: number,
): number {
  const b = stateVectorToBloch(sv, qubitIndex, numQubits);
  // |r|² for the Bloch vector
  const r2 = b.rx * b.rx + b.ry * b.ry + b.rz * b.rz;
  // For a pure global state, C(i|rest)² = 1 - |r|²
  // (maximally entangled ↔ r=0, separable ↔ |r|=1)
  return Math.max(0, 1 - r2);
}

/**
 * Compute the 3-tangle (Coffman-Kundu-Wootters residual tangle) for
 * a 3-qubit pure state. Measures genuinely tripartite entanglement
 * that cannot be accounted for by pairwise entanglement.
 *
 * τ₃(A,B,C) = C²(A|BC) - C²(A,B) - C²(A,C)
 *
 * By the CKW monogamy inequality, τ₃ ≥ 0 for all 3-qubit pure states.
 *
 * Key examples:
 * - GHZ = (|000⟩ + |111⟩)/√2: τ₃ = 1 (maximal), C(A,B) = C(A,C) = 0
 * - W = (|001⟩ + |010⟩ + |100⟩)/√3: τ₃ = 0, C(A,B) = C(A,C) = 2/3
 * - Product state: τ₃ = 0, all concurrences = 0
 */
export function threeTangle(sv: Complex[], numQubits: number): number {
  if (numQubits !== 3) return 0;

  // C²(A|BC) = 1 - |r_A|² (1-tangle of qubit 0 with rest)
  const cABC_sq = oneTangle(sv, 0, 3);

  // Pairwise concurrences C(A,B) and C(A,C)
  const cAB = pairConcurrence(sv, 0, 1, 3);
  const cAC = pairConcurrence(sv, 0, 2, 3);

  // τ₃ = C²(A|BC) - C²(A,B) - C²(A,C)
  const tau = cABC_sq - cAB * cAB - cAC * cAC;
  return Math.max(0, tau);
}

/**
 * Generalized multipartite entanglement measure for n-qubit pure states.
 * Returns:
 * - For n=2: squared concurrence C²(0,1)
 * - For n=3: 3-tangle τ₃ (CKW residual tangle)
 * - For n≥4: average residual tangle across all qubits
 *   τ_avg = (1/n) Σᵢ [C²(i|rest) - Σⱼ≠ᵢ C²(i,j)]
 *   This generalizes the CKW monogamy idea to larger systems.
 */
export function multipartiteTangle(sv: Complex[], numQubits: number): number {
  if (numQubits < 2) return 0;
  if (numQubits === 2) {
    const c = pairConcurrence(sv, 0, 1, 2);
    return c * c;
  }
  if (numQubits === 3) return threeTangle(sv, numQubits);

  // n ≥ 4: average residual tangle
  let totalResidual = 0;
  for (let i = 0; i < numQubits; i++) {
    const cRest_sq = oneTangle(sv, i, numQubits);
    let pairSum = 0;
    for (let j = 0; j < numQubits; j++) {
      if (j === i) continue;
      const cij = pairConcurrence(sv, i, j, numQubits);
      pairSum += cij * cij;
    }
    totalResidual += Math.max(0, cRest_sq - pairSum);
  }
  return totalResidual / numQubits;
}
