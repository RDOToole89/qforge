/**
 * Reduced density matrices, Bloch vectors, purity, and Z-basis correlators.
 *
 * Pure, framework-free (no `three`, no `react`). Single source of truth for the
 * one- and two-qubit observables derived from an n-qubit pure state vector.
 *
 * Convention (matches the backend `src/engine/bloch_math.py`): qubit 0 is the
 * MSB, so the basis-index bit for qubit q is `1 << (n-1-q)`. Feeding a
 * frontend-convention state vector through these functions yields per-qubit
 * indices that line up exactly with the backend's partial traces.
 */
import type { Complex } from "./complex";

/**
 * Extract single-qubit Bloch vector from an n-qubit state vector
 * via partial trace over all other qubits.
 *
 * Given |ψ⟩ in C^{2^n}, computes the reduced density matrix ρ_k for qubit k,
 * then returns Pauli expectations: rx = Tr(ρσ_x), ry = Tr(ρσ_y), rz = Tr(ρσ_z).
 *
 * Uses MSB qubit convention (qubit 0 = MSB).
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
 * Compute the 2x2 single-qubit reduced density matrix ρ_k for qubit k from an
 * n-qubit state vector, returned as separate real and imaginary 2x2 arrays in
 * the {|0⟩, |1⟩} basis.
 *
 * Uses MSB qubit convention (qubit 0 = MSB).
 */
export function reducedDensityMatrix1Q(
  sv: Complex[],
  qubitIndex: number,
  numQubits: number,
): { re: number[][]; im: number[][] } {
  const dim = 1 << numQubits;
  const bit = 1 << (numQubits - 1 - qubitIndex);

  const re = [[0, 0], [0, 0]];
  const im = [[0, 0], [0, 0]];

  // ρ[a][b] = Σ_rest conj(ψ_{a,rest}) ψ_{b,rest}, a,b ∈ {0,1} for qubit k.
  for (let i = 0; i < dim; i++) {
    const a = (i & bit) ? 1 : 0;
    const partner = i ^ bit; // same as i but with qubit k flipped
    const b = a ^ 1;
    // Diagonal: ρ[a][a] += |ψ_i|^2
    re[a][a] += sv[i][0] * sv[i][0] + sv[i][1] * sv[i][1];
    // Off-diagonal: ρ[a][b] += conj(ψ_i) ψ_partner
    re[a][b] += sv[i][0] * sv[partner][0] + sv[i][1] * sv[partner][1];
    im[a][b] += sv[i][0] * sv[partner][1] - sv[i][1] * sv[partner][0];
  }

  return { re, im };
}

/**
 * Purity Tr(ρ_k²) of the single-qubit reduced density matrix for qubit k.
 *
 * For a 2x2 density matrix with Bloch vector r: Tr(ρ²) = (1 + |r|²)/2. This is
 * exact for any single-qubit state (pure global state → reduced state ranges
 * from 1 when separable to 0.5 when maximally entangled).
 */
export function purity(
  sv: Complex[],
  qubitIndex: number,
  numQubits: number,
): number {
  const b = stateVectorToBloch(sv, qubitIndex, numQubits);
  const r2 = b.rx * b.rx + b.ry * b.ry + b.rz * b.rz;
  return (1 + r2) / 2;
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
