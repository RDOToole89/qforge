/**
 * Gate matrices, gate application, and circuit simulation.
 *
 * Pure, framework-free (no `three`, no `react`). Single source of truth for the
 * statevector simulator that powers the circuit builder.
 *
 * Conventions (must match the rest of lib/quantum and the backend):
 *   - Statevector is `Complex[]` ([re, im] pairs), length 2^n.
 *   - Qubit 0 is the MSB: the basis-index bit for qubit q is `1 << (n-1-q)`.
 *     So for n=3, |q0 q1 q2> maps to index (q0<<2)|(q1<<1)|q2.
 */
import type { Circuit, SimSnapshot } from "@/src/features/circuit-builder/types";
import { type Complex, cadd, cmul, cabs2 } from "./complex";

// ── Gate matrices (2x2 as [[a,b],[c,d]]) ────────────────────────

/** A 2x2 complex matrix. */
export type Mat2 = [[Complex, Complex], [Complex, Complex]];

export const I2: Mat2 = [[[1, 0], [0, 0]], [[0, 0], [1, 0]]];
export const H_MAT: Mat2 = [
  [[1 / Math.SQRT2, 0], [1 / Math.SQRT2, 0]],
  [[1 / Math.SQRT2, 0], [-1 / Math.SQRT2, 0]],
];
export const X_MAT: Mat2 = [[[0, 0], [1, 0]], [[1, 0], [0, 0]]];
export const Y_MAT: Mat2 = [[[0, 0], [0, -1]], [[0, 1], [0, 0]]];
export const Z_MAT: Mat2 = [[[1, 0], [0, 0]], [[0, 0], [-1, 0]]];
export const S_MAT: Mat2 = [[[1, 0], [0, 0]], [[0, 0], [0, 1]]];
export const T_MAT: Mat2 = [
  [[1, 0], [0, 0]],
  [[0, 0], [Math.cos(Math.PI / 4), Math.sin(Math.PI / 4)]],
];

export function rxMat(theta: number): Mat2 {
  const c = Math.cos(theta / 2);
  const s = Math.sin(theta / 2);
  return [[[c, 0], [0, -s]], [[0, -s], [c, 0]]];
}

export function ryMat(theta: number): Mat2 {
  const c = Math.cos(theta / 2);
  const s = Math.sin(theta / 2);
  return [[[c, 0], [-s, 0]], [[s, 0], [c, 0]]];
}

export function rzMat(theta: number): Mat2 {
  return [
    [[Math.cos(theta / 2), -Math.sin(theta / 2)], [0, 0]],
    [[0, 0], [Math.cos(theta / 2), Math.sin(theta / 2)]],
  ];
}

// ── State vector operations ─────────────────────────────────────

/** Apply a single-qubit gate to qubit `target` in an n-qubit state vector. */
export function applySingleQubit(sv: Complex[], n: number, target: number, mat: Mat2): Complex[] {
  const out: Complex[] = sv.map((c) => [...c] as Complex);
  const dim = 1 << n;
  const bit = 1 << (n - 1 - target); // MSB convention

  for (let i = 0; i < dim; i++) {
    if (i & bit) continue; // only process the i where target bit is 0
    const j = i | bit; // j has target bit = 1
    const a0 = sv[i];
    const a1 = sv[j];
    out[i] = cadd(cmul(mat[0][0], a0), cmul(mat[0][1], a1));
    out[j] = cadd(cmul(mat[1][0], a0), cmul(mat[1][1], a1));
  }
  return out;
}

/** Apply CNOT: flip target bit when control bit is 1. */
export function applyCNOT(sv: Complex[], n: number, control: number, target: number): Complex[] {
  const out: Complex[] = sv.map((c) => [...c] as Complex);
  const dim = 1 << n;
  const cBit = 1 << (n - 1 - control);
  const tBit = 1 << (n - 1 - target);

  for (let i = 0; i < dim; i++) {
    if (!(i & cBit)) continue; // control must be 1
    if (i & tBit) continue; // only process where target is 0
    const j = i | tBit;
    out[i] = sv[j];
    out[j] = sv[i];
  }
  return out;
}

/** Apply CZ: negate amplitude when both control and target are 1. */
export function applyCZ(sv: Complex[], n: number, q1: number, q2: number): Complex[] {
  const out: Complex[] = sv.map((c) => [...c] as Complex);
  const dim = 1 << n;
  const b1 = 1 << (n - 1 - q1);
  const b2 = 1 << (n - 1 - q2);

  for (let i = 0; i < dim; i++) {
    if ((i & b1) && (i & b2)) {
      out[i] = [-sv[i][0], -sv[i][1]];
    }
  }
  return out;
}

/** Apply SWAP: exchange the two qubit positions. */
export function applySWAP(sv: Complex[], n: number, q1: number, q2: number): Complex[] {
  const out: Complex[] = sv.map((c) => [...c] as Complex);
  const dim = 1 << n;
  const b1 = 1 << (n - 1 - q1);
  const b2 = 1 << (n - 1 - q2);

  for (let i = 0; i < dim; i++) {
    const bit1 = (i & b1) ? 1 : 0;
    const bit2 = (i & b2) ? 1 : 0;
    if (bit1 === bit2) continue;
    // Swap amplitudes
    const j = (i ^ b1) ^ b2;
    if (i < j) {
      out[i] = sv[j];
      out[j] = sv[i];
    }
  }
  return out;
}

/** Apply Toffoli: flip target when both controls are 1. */
export function applyToffoli(sv: Complex[], n: number, c1: number, c2: number, target: number): Complex[] {
  const out: Complex[] = sv.map((c) => [...c] as Complex);
  const dim = 1 << n;
  const b1 = 1 << (n - 1 - c1);
  const b2 = 1 << (n - 1 - c2);
  const bt = 1 << (n - 1 - target);

  for (let i = 0; i < dim; i++) {
    if (!(i & b1) || !(i & b2)) continue; // both controls must be 1
    if (i & bt) continue; // only process where target is 0
    const j = i | bt;
    out[i] = sv[j];
    out[j] = sv[i];
  }
  return out;
}

// ── Simulation engine ───────────────────────────────────────────

export function getGateMatrix(gateType: string, params?: number[]): Mat2 {
  switch (gateType) {
    case "H": return H_MAT;
    case "X": return X_MAT;
    case "Y": return Y_MAT;
    case "Z": return Z_MAT;
    case "S": return S_MAT;
    case "T": return T_MAT;
    case "Rx": return rxMat(params?.[0] ?? Math.PI / 2);
    case "Ry": return ryMat(params?.[0] ?? Math.PI / 2);
    case "Rz": return rzMat(params?.[0] ?? Math.PI / 2);
    default: return I2;
  }
}

function basisLabel(index: number, n: number): string {
  return "|" + index.toString(2).padStart(n, "0") + "⟩";
}

/** Simulate the full circuit, returning a snapshot after each moment. */
export function simulateCircuit(circuit: Circuit): SimSnapshot[] {
  const { numQubits, moments } = circuit;
  const dim = 1 << numQubits;
  const labels = Array.from({ length: dim }, (_, i) => basisLabel(i, numQubits));

  // Initial state: |00...0>
  let sv: Complex[] = Array.from({ length: dim }, (_, i): Complex =>
    i === 0 ? [1, 0] : [0, 0]
  );

  const snapshots: SimSnapshot[] = [];

  // Initial snapshot
  snapshots.push({
    stateVector: sv.map((c) => [...c] as Complex),
    probabilities: sv.map(cabs2),
    labels,
  });

  for (const moment of moments) {
    for (const gate of moment.gates) {
      const { gateType, qubits, params } = gate;

      if (gateType === "CNOT" && qubits.length >= 2) {
        sv = applyCNOT(sv, numQubits, qubits[0], qubits[1]);
      } else if (gateType === "CZ" && qubits.length >= 2) {
        sv = applyCZ(sv, numQubits, qubits[0], qubits[1]);
      } else if (gateType === "SWAP" && qubits.length >= 2) {
        sv = applySWAP(sv, numQubits, qubits[0], qubits[1]);
      } else if (gateType === "Toffoli" && qubits.length >= 3) {
        sv = applyToffoli(sv, numQubits, qubits[0], qubits[1], qubits[2]);
      } else {
        // Single-qubit gate
        const mat = getGateMatrix(gateType, params);
        const target = qubits[qubits.length - 1];
        sv = applySingleQubit(sv, numQubits, target, mat);
      }
    }

    snapshots.push({
      stateVector: sv.map((c) => [...c] as Complex),
      probabilities: sv.map(cabs2),
      labels,
    });
  }

  return snapshots;
}

/** Format a state vector as Dirac notation string. */
export function formatDirac(snapshot: SimSnapshot, threshold: number = 0.001): string {
  const terms: string[] = [];

  for (let i = 0; i < snapshot.stateVector.length; i++) {
    const [re, im] = snapshot.stateVector[i];
    const prob = re * re + im * im;
    if (prob < threshold) continue;

    const amp = Math.sqrt(prob);
    const phase = Math.atan2(im, re);

    let coeff: string;
    if (Math.abs(amp - 1) < 0.001) {
      coeff = phase < -0.01 ? "-" : "";
    } else if (Math.abs(amp - 1 / Math.SQRT2) < 0.01) {
      coeff = phase < -0.01 ? "-1/√2" : "1/√2";
    } else {
      coeff = amp.toFixed(3);
      if (phase < -0.01) coeff = "-" + coeff;
    }

    const label = snapshot.labels[i];
    terms.push(
      terms.length > 0 && coeff[0] !== "-"
        ? `+ ${coeff}${label}`
        : `${coeff}${label}`
    );
  }

  return terms.length > 0 ? `|ψ⟩ = ${terms.join(" ")}` : "|ψ⟩ = |0⟩";
}

/**
 * Recognize named quantum states from a state vector.
 * Checks amplitudes AND relative phases to distinguish variants.
 * Returns a human-readable name or null if unrecognized.
 */
export function recognizeState(snapshot: SimSnapshot): string | null {
  const sv = snapshot.stateVector;
  const n = Math.log2(sv.length);
  if (!Number.isInteger(n) || n < 1) return null;
  const dim = sv.length;

  const prob = (i: number) => sv[i][0] * sv[i][0] + sv[i][1] * sv[i][1];
  const phase = (i: number) => Math.atan2(sv[i][1], sv[i][0]);
  const nonzeroIndices: number[] = [];
  for (let i = 0; i < dim; i++) {
    if (prob(i) > 0.001) nonzeroIndices.push(i);
  }

  // ── Single basis state ──
  if (nonzeroIndices.length === 1) {
    const idx = nonzeroIndices[0];
    if (idx === 0) return "|0⟩ (ground state)";
    return `|${idx.toString(2).padStart(n, "0")}⟩`;
  }

  // ── 1-qubit named states ──
  if (n === 1 && nonzeroIndices.length === 2) {
    const p0 = prob(0), p1 = prob(1);
    if (Math.abs(p0 - 0.5) < 0.02 && Math.abs(p1 - 0.5) < 0.02) {
      const relPhase = phase(1) - phase(0);
      const normPhase = ((relPhase % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
      if (normPhase < 0.15 || normPhase > 2 * Math.PI - 0.15) return "|+⟩";
      if (Math.abs(normPhase - Math.PI) < 0.15) return "|−⟩";
      if (Math.abs(normPhase - Math.PI / 2) < 0.15) return "|+i⟩ (Y eigenstate)";
      if (Math.abs(normPhase - 3 * Math.PI / 2) < 0.15) return "|−i⟩ (Y eigenstate)";
      return "Superposition";
    }
  }

  // ── Bell states (2 qubits, phase-resolved) ──
  if (n === 2 && nonzeroIndices.length === 2) {
    const p00 = prob(0), p01 = prob(1), p10 = prob(2), p11 = prob(3);

    // |Φ±⟩ = (|00⟩ ± |11⟩)/√2
    if (Math.abs(p00 - 0.5) < 0.02 && Math.abs(p11 - 0.5) < 0.02 && p01 < 0.02 && p10 < 0.02) {
      const rel = phase(3) - phase(0); // phase of |11⟩ relative to |00⟩
      const norm = ((rel % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
      if (norm < 0.2 || norm > 2 * Math.PI - 0.2) return "Bell |Φ⁺⟩";
      if (Math.abs(norm - Math.PI) < 0.2) return "Bell |Φ⁻⟩";
      return "Bell state (|Φ⟩ variant)";
    }

    // |Ψ±⟩ = (|01⟩ ± |10⟩)/√2
    if (Math.abs(p01 - 0.5) < 0.02 && Math.abs(p10 - 0.5) < 0.02 && p00 < 0.02 && p11 < 0.02) {
      const rel = phase(2) - phase(1); // phase of |10⟩ relative to |01⟩
      const norm = ((rel % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
      if (norm < 0.2 || norm > 2 * Math.PI - 0.2) return "Bell |Ψ⁺⟩";
      if (Math.abs(norm - Math.PI) < 0.2) return "Bell |Ψ⁻⟩ (singlet)";
      return "Bell state (|Ψ⟩ variant)";
    }
  }

  // ── GHZ state: (|00...0⟩ ± |11...1⟩)/√2 ──
  if (n >= 2 && nonzeroIndices.length === 2) {
    if (nonzeroIndices[0] === 0 && nonzeroIndices[1] === dim - 1) {
      if (Math.abs(prob(0) - 0.5) < 0.02 && Math.abs(prob(dim - 1) - 0.5) < 0.02) {
        if (n === 2) {
          // Already handled above as Bell state
        } else {
          const rel = phase(dim - 1) - phase(0);
          const norm = ((rel % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI);
          const sign = (norm < 0.2 || norm > 2 * Math.PI - 0.2) ? "+" : (Math.abs(norm - Math.PI) < 0.2) ? "−" : "±";
          return `GHZ${sign} state (${n}Q)`;
        }
      }
    }
  }

  // ── W state: equal superposition of single-excitation states ──
  if (n >= 2) {
    const expectedProb = 1 / n;
    let isW = true;
    let wCount = 0;
    for (let i = 0; i < dim; i++) {
      const popcount = i.toString(2).split("").filter((b) => b === "1").length;
      if (popcount === 1) {
        if (Math.abs(prob(i) - expectedProb) > 0.03) { isW = false; break; }
        wCount++;
      } else {
        if (prob(i) > 0.02) { isW = false; break; }
      }
    }
    if (isW && wCount === n) return `W state (${n}Q)`;
  }

  // ── Dicke states: equal superposition of k-excitation states ──
  if (n >= 3 && nonzeroIndices.length > 2) {
    // Check if all nonzero states have the same Hamming weight
    const weights = nonzeroIndices.map((i) => i.toString(2).split("").filter((b) => b === "1").length);
    const k = weights[0];
    if (weights.every((w) => w === k)) {
      // Binomial coefficient C(n,k)
      const expectedCount = nonzeroIndices.length;
      const expectedP = 1 / expectedCount;
      const allEqual = nonzeroIndices.every((i) => Math.abs(prob(i) - expectedP) < 0.03);
      if (allEqual && k > 1 && k < n) {
        return `Dicke state D(${n},${k})`;
      }
    }
  }

  // ── Uniform superposition ──
  const expectedUniform = 1 / dim;
  let isUniform = true;
  for (let i = 0; i < dim; i++) {
    if (Math.abs(prob(i) - expectedUniform) > 0.02) { isUniform = false; break; }
  }
  if (isUniform) {
    // Check if it's |+⟩^⊗n (all real positive amplitudes)
    let allRealPositive = true;
    for (let i = 0; i < dim; i++) {
      if (sv[i][0] < -0.01 || Math.abs(sv[i][1]) > 0.01) { allRealPositive = false; break; }
    }
    if (allRealPositive) return `|+⟩⊗${n}`;
    return "Uniform superposition";
  }

  // ── Product state detection: check if state is separable ──
  if (n === 2 && nonzeroIndices.length === 4) {
    // |ψ⟩ = |a⟩⊗|b⟩ iff sv[00]*sv[11] = sv[01]*sv[10] (as complex numbers)
    const lhs_re = sv[0][0] * sv[3][0] - sv[0][1] * sv[3][1];
    const lhs_im = sv[0][0] * sv[3][1] + sv[0][1] * sv[3][0];
    const rhs_re = sv[1][0] * sv[2][0] - sv[1][1] * sv[2][1];
    const rhs_im = sv[1][0] * sv[2][1] + sv[1][1] * sv[2][0];
    if (Math.abs(lhs_re - rhs_re) < 0.02 && Math.abs(lhs_im - rhs_im) < 0.02) {
      return "Product state (separable)";
    }
  }

  return null;
}
