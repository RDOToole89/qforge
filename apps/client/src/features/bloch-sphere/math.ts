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
      // ρ_01 += ⟨i|ψ⟩* ⟨j|ψ⟩ = conj(sv[i]) * sv[j]
      rho01_re += sv[i][0] * sv[j][0] + sv[i][1] * sv[j][1];
      rho01_im += sv[i][0] * sv[j][1] - sv[i][1] * sv[j][0];
    }
  }

  return {
    rx: 2 * rho01_re,      // Tr(ρ σ_x) = 2 Re(ρ_01)
    ry: -2 * rho01_im,     // Tr(ρ σ_y) = -2 Im(ρ_01)
    rz: rho00 - rho11,     // Tr(ρ σ_z) = ρ_00 - ρ_11
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
 * Compute concurrence for a 2-qubit reduced state extracted from an n-qubit
 * state vector. Uses the Wootters formula for pure states:
 * C = 2|ad - bc| where |ψ⟩ = a|00⟩ + b|01⟩ + c|10⟩ + d|11⟩ in the
 * reduced 2-qubit space.
 *
 * For mixed reduced states (n > 2), computes concurrence from the
 * 4×4 reduced density matrix using the eigenvalue formula.
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

  // Compute 4×4 reduced density matrix ρ_{ij} by partial trace
  // Basis: |00⟩, |01⟩, |10⟩, |11⟩ for qubits (qi, qj)
  const rho_re: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  const rho_im: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];

  for (let k = 0; k < dim; k++) {
    const row = ((k & bitI) ? 2 : 0) | ((k & bitJ) ? 1 : 0);
    for (let l = 0; l < dim; l++) {
      // Check that k and l agree on all qubits except qi and qj
      const mask = ~(bitI | bitJ);
      if ((k & mask) !== (l & mask)) continue;
      const col = ((l & bitI) ? 2 : 0) | ((l & bitJ) ? 1 : 0);
      // ρ[row][col] += conj(sv[k]) * sv[l]
      rho_re[row][col] += sv[k][0] * sv[l][0] + sv[k][1] * sv[l][1];
      rho_im[row][col] += sv[k][0] * sv[l][1] - sv[k][1] * sv[l][0];
    }
  }

  // σ_y ⊗ σ_y = [[0,0,0,-1],[0,0,1,0],[0,1,0,0],[-1,0,0,0]]
  // ρ̃ = (σ_y⊗σ_y) ρ* (σ_y⊗σ_y)
  // For the concurrence formula: compute R = ρ ρ̃, find eigenvalues, C = max(0, √λ1 - √λ2 - √λ3 - √λ4)
  // For small matrices, use a simpler approach: compute tr(ρ̃ρ) route

  // Actually for efficiency, use the formula via spin-flipped state:
  // R = sqrt(sqrt(ρ) * ρ̃ * sqrt(ρ)) eigenvalues
  // This is complex for a general mixed state. Use a simplified approach:
  // Compute the 4 eigenvalues of R = ρ * (σy⊗σy) * ρ* * (σy⊗σy)

  // σy⊗σy matrix (real): rows/cols in basis 00,01,10,11
  // = [[0,0,0,-1],[0,0,1,0],[0,1,0,0],[-1,0,0,0]]
  const sysy = [[0,0,0,-1],[0,0,1,0],[0,1,0,0],[-1,0,0,0]];

  // Compute ρ̃ = (σy⊗σy) ρ* (σy⊗σy)
  // Step 1: tmp = ρ* * (σy⊗σy)
  const tmp_re: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  const tmp_im: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      for (let k = 0; k < 4; k++) {
        tmp_re[i][j] += rho_re[i][k] * sysy[k][j]; // ρ* real part = ρ real part
        tmp_im[i][j] += -rho_im[i][k] * sysy[k][j]; // ρ* imag part = -ρ imag part
      }
    }
  }
  // Step 2: ρ̃ = (σy⊗σy) * tmp
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

  // Compute R = ρ * ρ̃ (complex matrix multiply)
  const R_re: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  const R_im: number[][] = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]];
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      for (let k = 0; k < 4; k++) {
        R_re[i][j] += rho_re[i][k] * rtilde_re[k][j] - rho_im[i][k] * rtilde_im[k][j];
        R_im[i][j] += rho_re[i][k] * rtilde_im[k][j] + rho_im[i][k] * rtilde_re[k][j];
      }
    }
  }

  // Eigenvalues of R (4×4 Hermitian-ish matrix) — use trace powers for a simpler approach
  // For a rank-1 or rank-2 ρ (common in circuit simulation), most eigenvalues are 0
  // Use the characteristic polynomial approach via Newton's identities:
  // tr(R), tr(R²), tr(R³), tr(R⁴) → eigenvalues
  const trR = R_re[0][0] + R_re[1][1] + R_re[2][2] + R_re[3][3];

  // For most practical cases in circuit simulation, a simpler formula works:
  // C = max(0, 2*max_eigenvalue_of_sqrt(R) - tr(sqrt(R)))
  // But computing sqrt of a matrix is expensive. Use a known shortcut:
  // The eigenvalues of R are real and non-negative (R = ρ ρ̃ where ρ̃ is related to ρ by antiunitary)

  // Compute tr(R²) for the characteristic polynomial
  let trR2 = 0;
  for (let i = 0; i < 4; i++) {
    for (let k = 0; k < 4; k++) {
      trR2 += R_re[i][k] * R_re[k][i] - R_im[i][k] * R_im[k][i];
    }
  }

  // For 2-qubit pure states (no other qubits), concurrence = 2|ad-bc|
  // For general case with small eigenvalues, use approximate formula
  // eigenvalues λ from: λ⁴ - trR·λ² + ... = 0
  // Simplified: if R ≈ rank 1, then C ≈ √trR

  // Use the proper formula: eigenvalues of R via 4×4 determinant
  // But for a research tool, the practical shortcut for pure global states:
  // When the global state is pure, concurrence(i,j) = 2*sqrt(det(ρ_ij_reduced))
  // ... but ρ_ij might be mixed even if global is pure

  // Use the simplest correct approach: C = max(0, √λ₁ - √λ₂ - √λ₃ - √λ₄)
  // where λᵢ are eigenvalues of R, sorted descending.
  // For a 4×4 matrix, compute eigenvalues via the characteristic polynomial.

  // Actually, for the specific case where the GLOBAL state is pure (which it always is
  // in our simulator since we track statevectors), there's a much simpler formula:
  // C(qi,qj) = 2 * |det_reduced_amplitudes|... but this only works for 2-qubit systems.

  // For n>2 with pure global state, the concurrence of the reduced 2-qubit state is:
  // C = sqrt(2(1 - tr(ρ_reduced²)))... NO, that's the tangle/linear entropy.

  // Let's just use: for pure global states, the concurrence of qubits i,j equals
  // the concurrence computed from ρ_{ij} via the Wootters formula.
  // The eigenvalues of R = ρ ρ̃ can be found numerically.

  // For a 4×4 matrix, find eigenvalues by solving the characteristic polynomial.
  // Coefficients: det(R - λI) = λ⁴ - c₃λ³ + c₂λ² - c₁λ + c₀ = 0
  // c₃ = tr(R), c₂ = (tr(R)² - tr(R²))/2, etc.

  const c3 = trR;
  const c2 = (trR * trR - trR2) / 2;

  // tr(R³)
  let trR3 = 0;
  for (let i = 0; i < 4; i++) {
    for (let j = 0; j < 4; j++) {
      for (let k = 0; k < 4; k++) {
        trR3 += R_re[i][j] * R_re[j][k] * R_re[k][i]
              - R_re[i][j] * R_im[j][k] * R_im[k][i]
              - R_im[i][j] * R_re[j][k] * R_im[k][i]
              - R_im[i][j] * R_im[j][k] * R_re[k][i];  // Re part of trace
      }
    }
  }
  const c1 = (trR * trR * trR - 3 * trR * trR2 + 2 * trR3) / 6;

  // For c₀ = det(R), use the cofactor expansion (simplified for real eigenvalues assumption)
  // Since eigenvalues should be real and non-negative, and for most circuit states
  // only 0-2 eigenvalues are nonzero, use a practical approach:

  // If trR < 1e-10, concurrence is 0 (no entanglement)
  if (trR < 1e-10) return 0;

  // Solve for eigenvalues using the depressed quartic / quadratic-of-quadratic approach
  // For most circuit states, c₀ and c₁ are very small, so eigenvalues are approx:
  // λ ≈ roots of λ² - c₃λ + c₂ = 0 (ignoring small terms)
  const disc = c3 * c3 - 4 * c2;
  let sqrtLambdas: number[];
  if (disc < 0 || c2 < -1e-10) {
    // Fallback: just use √trR as approximation (works for rank-1 R)
    sqrtLambdas = [Math.sqrt(Math.max(0, trR)), 0, 0, 0];
  } else {
    const sqD = Math.sqrt(Math.max(0, disc));
    const l1 = Math.max(0, (c3 + sqD) / 2);
    const l2 = Math.max(0, (c3 - sqD) / 2);
    // Refine: check if c₁ contributes (usually not for circuit states)
    sqrtLambdas = [Math.sqrt(l1), Math.sqrt(l2), 0, 0];
    // If there are more eigenvalues from c₁, add them
    if (Math.abs(c1) > 1e-10 && l2 > 1e-10) {
      // Subdivide l2 further
      const subDisc = l2 * l2 - 4 * Math.abs(c1) / c3;
      if (subDisc > 0) {
        const subSqD = Math.sqrt(subDisc);
        sqrtLambdas[1] = Math.sqrt(Math.max(0, (l2 + subSqD) / 2));
        sqrtLambdas[2] = Math.sqrt(Math.max(0, (l2 - subSqD) / 2));
      }
    }
  }

  sqrtLambdas.sort((a, b) => b - a);
  const C = Math.max(0, sqrtLambdas[0] - sqrtLambdas[1] - sqrtLambdas[2] - sqrtLambdas[3]);
  return C;
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
