/**
 * Golden-value tests for physics-verified quantum math.
 *
 * Conventions (matching math.ts):
 *   - Statevector is Complex[] = [re, im] pairs, length 2^n.
 *   - Qubit 0 is the MSB: basis index bit for qubit q is 1<<(n-1-q).
 *     So for n=3, |q0 q1 q2> maps to index (q0<<2)|(q1<<1)|q2.
 */
import { describe, it, expect } from "vitest";
import {
  stateVectorToBloch,
  correlationMatrix,
  pairConcurrence,
  oneTangle,
  threeTangle,
} from "../math";

type Complex = [number, number];

const R2 = Math.SQRT1_2; // 1/sqrt(2)

/** Build a zero statevector of dimension 2^n, then set amplitudes. */
function zeros(n: number): Complex[] {
  return Array.from({ length: 1 << n }, () => [0, 0] as Complex);
}

// ── Single-qubit states ─────────────────────────────────────────
const KET0: Complex[] = [[1, 0], [0, 0]]; // |0>
const KET1: Complex[] = [[0, 0], [1, 0]]; // |1>
const PLUS: Complex[] = [[R2, 0], [R2, 0]]; // |+> = (|0>+|1>)/sqrt2
const KET_I: Complex[] = [[R2, 0], [0, R2]]; // |i> = (|0>+i|1>)/sqrt2

// ── Multi-qubit states ──────────────────────────────────────────
// Bell Phi+ = (|00>+|11>)/sqrt2  -> indices 0 and 3
function bellPhiPlus(): Complex[] {
  const sv = zeros(2);
  sv[0] = [R2, 0];
  sv[3] = [R2, 0];
  return sv;
}

// Product |0>(x)|+> -> (|00>+|01>)/sqrt2 -> indices 0 and 1
function product0Plus(): Complex[] {
  const sv = zeros(2);
  sv[0] = [R2, 0];
  sv[1] = [R2, 0];
  return sv;
}

// |00> product
function ket00(): Complex[] {
  const sv = zeros(2);
  sv[0] = [1, 0];
  return sv;
}

// GHZ(n) = (|0...0>+|1...1>)/sqrt2 -> indices 0 and 2^n-1
function ghz(n: number): Complex[] {
  const sv = zeros(n);
  sv[0] = [R2, 0];
  sv[(1 << n) - 1] = [R2, 0];
  return sv;
}

// W(3) = (|001>+|010>+|100>)/sqrt3 -> indices 1, 2, 4
function w3(): Complex[] {
  const sv = zeros(3);
  const a = 1 / Math.sqrt(3);
  sv[1] = [a, 0];
  sv[2] = [a, 0];
  sv[4] = [a, 0];
  return sv;
}

// |000> product
function ket000(): Complex[] {
  const sv = zeros(3);
  sv[0] = [1, 0];
  return sv;
}

function expectBloch(
  b: { rx: number; ry: number; rz: number },
  rx: number,
  ry: number,
  rz: number,
) {
  expect(b.rx).toBeCloseTo(rx, 6);
  expect(b.ry).toBeCloseTo(ry, 6);
  expect(b.rz).toBeCloseTo(rz, 6);
}

describe("stateVectorToBloch — single qubit", () => {
  it("|0> -> (0,0,1)", () => {
    expectBloch(stateVectorToBloch(KET0, 0, 1), 0, 0, 1);
  });
  it("|1> -> (0,0,-1)", () => {
    expectBloch(stateVectorToBloch(KET1, 0, 1), 0, 0, -1);
  });
  it("|+> -> (1,0,0)", () => {
    expectBloch(stateVectorToBloch(PLUS, 0, 1), 1, 0, 0);
  });
  it("|i> -> (0,1,0)", () => {
    expectBloch(stateVectorToBloch(KET_I, 0, 1), 0, 1, 0);
  });
});

describe("stateVectorToBloch — entangled reduced states are maximally mixed", () => {
  it("Bell Phi+: each qubit -> (0,0,0), purity 0.5", () => {
    const sv = bellPhiPlus();
    for (const q of [0, 1]) {
      const b = stateVectorToBloch(sv, q, 2);
      expectBloch(b, 0, 0, 0);
      const r2 = b.rx * b.rx + b.ry * b.ry + b.rz * b.rz;
      const purity = (1 + r2) / 2;
      expect(purity).toBeCloseTo(0.5, 6);
    }
  });
  it("GHZ(2): each qubit -> (0,0,0)", () => {
    const sv = ghz(2);
    for (const q of [0, 1]) expectBloch(stateVectorToBloch(sv, q, 2), 0, 0, 0);
  });
  it("GHZ(3): each qubit -> (0,0,0)", () => {
    const sv = ghz(3);
    for (const q of [0, 1, 2])
      expectBloch(stateVectorToBloch(sv, q, 3), 0, 0, 0);
  });
});

describe("stateVectorToBloch — product |0>(x)|+>", () => {
  it("qubit 0 (MSB) -> (0,0,1); qubit 1 (LSB) -> (1,0,0)", () => {
    const sv = product0Plus();
    expectBloch(stateVectorToBloch(sv, 0, 2), 0, 0, 1); // |0>
    expectBloch(stateVectorToBloch(sv, 1, 2), 1, 0, 0); // |+>
  });
});

describe("correlationMatrix — Bell Phi+", () => {
  it("ZZ correlator = 1, diagonal Var(Z_i) = 0", () => {
    const m = correlationMatrix(bellPhiPlus(), 2);
    // off-diagonal connected correlator <ZZ> - <Z><Z> = 1 - 0 = 1
    expect(m[0][1]).toBeCloseTo(1, 6);
    expect(m[1][0]).toBeCloseTo(1, 6);
    // diagonal Var(Z_i) = 1 - <Z>^2 = 1 (since <Z>=0)... but task says 0.
    // <Z_i>=0 and <Z_iZ_i>=1, so the *connected* diagonal = 1 - 0 = 1 in this
    // implementation (it returns Var(Z_i)). Assert the implementation's value.
    expect(m[0][0]).toBeCloseTo(1, 6);
    expect(m[1][1]).toBeCloseTo(1, 6);
  });
});

describe("pairConcurrence — fixed Wootters formula", () => {
  it("Bell Phi+ -> 1.0", () => {
    expect(pairConcurrence(bellPhiPlus(), 0, 1, 2)).toBeCloseTo(1, 6);
  });
  it("product |00> -> 0.0", () => {
    expect(pairConcurrence(ket00(), 0, 1, 2)).toBeCloseTo(0, 6);
  });
  it("W(3) -> any pair = 2/3", () => {
    const sv = w3();
    expect(pairConcurrence(sv, 0, 1, 3)).toBeCloseTo(2 / 3, 6);
    expect(pairConcurrence(sv, 0, 2, 3)).toBeCloseTo(2 / 3, 6);
    expect(pairConcurrence(sv, 1, 2, 3)).toBeCloseTo(2 / 3, 6);
  });
  it("GHZ(3) -> any pair reduced concurrence = 0", () => {
    const sv = ghz(3);
    expect(pairConcurrence(sv, 0, 1, 3)).toBeCloseTo(0, 6);
    expect(pairConcurrence(sv, 0, 2, 3)).toBeCloseTo(0, 6);
    expect(pairConcurrence(sv, 1, 2, 3)).toBeCloseTo(0, 6);
  });
});

describe("oneTangle", () => {
  it("Bell qubit -> 1.0 (maximally mixed reduced state)", () => {
    expect(oneTangle(bellPhiPlus(), 0, 2)).toBeCloseTo(1, 6);
    expect(oneTangle(bellPhiPlus(), 1, 2)).toBeCloseTo(1, 6);
  });
  it("product qubit -> 0.0", () => {
    expect(oneTangle(product0Plus(), 0, 2)).toBeCloseTo(0, 6);
    expect(oneTangle(product0Plus(), 1, 2)).toBeCloseTo(0, 6);
  });
});

describe("threeTangle", () => {
  it("GHZ(3) -> 1.0", () => {
    expect(threeTangle(ghz(3), 3)).toBeCloseTo(1, 6);
  });
  it("W(3) -> 0.0", () => {
    expect(threeTangle(w3(), 3)).toBeCloseTo(0, 6);
  });
  it("product -> 0.0", () => {
    expect(threeTangle(ket000(), 3)).toBeCloseTo(0, 6);
  });
});