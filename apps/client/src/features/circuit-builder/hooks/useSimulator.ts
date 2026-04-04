import { useMemo } from "react";
import type { Circuit, Complex, SimSnapshot } from "../types";

// ── Complex arithmetic ──────────────────────────────────────────

function cmul(a: Complex, b: Complex): Complex {
  return [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]];
}

function cadd(a: Complex, b: Complex): Complex {
  return [a[0] + b[0], a[1] + b[1]];
}

function cabs2(a: Complex): number {
  return a[0] * a[0] + a[1] * a[1];
}

// ── Gate matrices (2x2 as [[a,b],[c,d]]) ────────────────────────

type Mat2 = [[Complex, Complex], [Complex, Complex]];

const I2: Mat2 = [[[1, 0], [0, 0]], [[0, 0], [1, 0]]];
const H_MAT: Mat2 = [
  [[1 / Math.SQRT2, 0], [1 / Math.SQRT2, 0]],
  [[1 / Math.SQRT2, 0], [-1 / Math.SQRT2, 0]],
];
const X_MAT: Mat2 = [[[0, 0], [1, 0]], [[1, 0], [0, 0]]];
const Y_MAT: Mat2 = [[[0, 0], [0, -1]], [[0, 1], [0, 0]]];
const Z_MAT: Mat2 = [[[1, 0], [0, 0]], [[0, 0], [-1, 0]]];
const S_MAT: Mat2 = [[[1, 0], [0, 0]], [[0, 0], [0, 1]]];
const T_MAT: Mat2 = [
  [[1, 0], [0, 0]],
  [[0, 0], [Math.cos(Math.PI / 4), Math.sin(Math.PI / 4)]],
];

function rxMat(theta: number): Mat2 {
  const c = Math.cos(theta / 2);
  const s = Math.sin(theta / 2);
  return [[[c, 0], [0, -s]], [[0, -s], [c, 0]]];
}

function ryMat(theta: number): Mat2 {
  const c = Math.cos(theta / 2);
  const s = Math.sin(theta / 2);
  return [[[c, 0], [-s, 0]], [[s, 0], [c, 0]]];
}

function rzMat(theta: number): Mat2 {
  return [
    [[Math.cos(theta / 2), -Math.sin(theta / 2)], [0, 0]],
    [[0, 0], [Math.cos(theta / 2), Math.sin(theta / 2)]],
  ];
}

// ── State vector operations ─────────────────────────────────────

/** Apply a single-qubit gate to qubit `target` in an n-qubit state vector */
function applySingleQubit(sv: Complex[], n: number, target: number, mat: Mat2): Complex[] {
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

/** Apply CNOT: flip target bit when control bit is 1 */
function applyCNOT(sv: Complex[], n: number, control: number, target: number): Complex[] {
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

/** Apply CZ: negate amplitude when both control and target are 1 */
function applyCZ(sv: Complex[], n: number, q1: number, q2: number): Complex[] {
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

/** Apply SWAP: exchange the two qubit positions */
function applySWAP(sv: Complex[], n: number, q1: number, q2: number): Complex[] {
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

/** Apply Toffoli: flip target when both controls are 1 */
function applyToffoli(sv: Complex[], n: number, c1: number, c2: number, target: number): Complex[] {
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

function getGateMatrix(gateType: string, params?: number[]): Mat2 {
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
  return "|" + index.toString(2).padStart(n, "0") + "\u27E9";
}

/** Simulate the full circuit, returning a snapshot after each moment */
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

/** Format a state vector as Dirac notation string */
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
      coeff = phase < -0.01 ? "-1/\u221A2" : "1/\u221A2";
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

  return terms.length > 0 ? `|\u03c8\u27E9 = ${terms.join(" ")}` : "|\u03c8\u27E9 = |0\u27E9";
}

/** React hook: simulate whenever circuit changes */
export function useSimulator(circuit: Circuit) {
  const snapshots = useMemo(() => simulateCircuit(circuit), [circuit]);
  const finalSnapshot = snapshots.length > 0 ? snapshots[snapshots.length - 1] : null;

  return { snapshots, finalSnapshot };
}
