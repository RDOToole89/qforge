/**
 * Entanglement measures: Wootters concurrence and multipartite tangles.
 *
 * Pure, framework-free (no `three`, no `react`). Uses `ml-matrix` purely as an
 * eigensolver for the exact Wootters concurrence. Single source of truth for
 * the client's entanglement quantities.
 *
 * Convention: qubit 0 = MSB (bit = 1<<(n-1-q)), consistent with `density.ts`.
 */
import { Matrix, EigenvalueDecomposition } from "ml-matrix";
import type { Complex } from "./complex";
import { stateVectorToBloch } from "./density";

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
