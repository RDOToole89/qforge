import type { Complex, SimSnapshot } from "../types";

export interface IdealState {
  id: string;
  name: string;
  numQubits: number;
  description: string;
  /** Returns the state vector amplitudes */
  amplitudes: () => Complex[];
}

const S2 = 1 / Math.SQRT2;
const S3 = 1 / Math.sqrt(3);

export const IDEAL_STATES: IdealState[] = [
  // ── 1-qubit ──
  {
    id: "zero", name: "|0\u27E9", numQubits: 1,
    description: "Ground state \u2014 north pole of the Bloch sphere.",
    amplitudes: () => [[1, 0], [0, 0]],
  },
  {
    id: "one", name: "|1\u27E9", numQubits: 1,
    description: "Excited state \u2014 south pole of the Bloch sphere.",
    amplitudes: () => [[0, 0], [1, 0]],
  },
  {
    id: "plus", name: "|+\u27E9", numQubits: 1,
    description: "(|0\u27E9 + |1\u27E9)/\u221A2 \u2014 equator, +X direction.",
    amplitudes: () => [[S2, 0], [S2, 0]],
  },
  {
    id: "minus", name: "|\u2212\u27E9", numQubits: 1,
    description: "(|0\u27E9 \u2212 |1\u27E9)/\u221A2 \u2014 equator, \u2212X direction.",
    amplitudes: () => [[S2, 0], [-S2, 0]],
  },
  {
    id: "plus_i", name: "|+i\u27E9", numQubits: 1,
    description: "(|0\u27E9 + i|1\u27E9)/\u221A2 \u2014 equator, +Y direction.",
    amplitudes: () => [[S2, 0], [0, S2]],
  },

  // ── 2-qubit Bell states ──
  {
    id: "bell_phi_plus", name: "Bell |\u03A6\u207A\u27E9", numQubits: 2,
    description: "(|00\u27E9 + |11\u27E9)/\u221A2 \u2014 maximally entangled, correlated.",
    amplitudes: () => [[S2, 0], [0, 0], [0, 0], [S2, 0]],
  },
  {
    id: "bell_phi_minus", name: "Bell |\u03A6\u207B\u27E9", numQubits: 2,
    description: "(|00\u27E9 \u2212 |11\u27E9)/\u221A2 \u2014 maximally entangled, correlated with phase.",
    amplitudes: () => [[S2, 0], [0, 0], [0, 0], [-S2, 0]],
  },
  {
    id: "bell_psi_plus", name: "Bell |\u03A8\u207A\u27E9", numQubits: 2,
    description: "(|01\u27E9 + |10\u27E9)/\u221A2 \u2014 maximally entangled, anti-correlated.",
    amplitudes: () => [[0, 0], [S2, 0], [S2, 0], [0, 0]],
  },
  {
    id: "bell_psi_minus", name: "Bell |\u03A8\u207B\u27E9 (singlet)", numQubits: 2,
    description: "(|01\u27E9 \u2212 |10\u27E9)/\u221A2 \u2014 singlet state. Rotationally invariant.",
    amplitudes: () => [[0, 0], [S2, 0], [-S2, 0], [0, 0]],
  },

  // ── 3-qubit entangled ──
  {
    id: "ghz3", name: "GHZ (3Q)", numQubits: 3,
    description: "(|000\u27E9 + |111\u27E9)/\u221A2 \u2014 maximal 3-tangle, zero pairwise concurrence.",
    amplitudes: () => [[S2, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [S2, 0]],
  },
  {
    id: "w3", name: "W (3Q)", numQubits: 3,
    description: "(|001\u27E9 + |010\u27E9 + |100\u27E9)/\u221A3 \u2014 zero 3-tangle, maximal pairwise concurrence.",
    amplitudes: () => [[0, 0], [S3, 0], [S3, 0], [0, 0], [S3, 0], [0, 0], [0, 0], [0, 0]],
  },
  {
    id: "ghz3_minus", name: "GHZ\u207B (3Q)", numQubits: 3,
    description: "(|000\u27E9 \u2212 |111\u27E9)/\u221A2 \u2014 GHZ with relative minus sign.",
    amplitudes: () => [[S2, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [-S2, 0]],
  },
  {
    id: "dicke_3_2", name: "Dicke D(3,2)", numQubits: 3,
    description: "(|011\u27E9 + |101\u27E9 + |110\u27E9)/\u221A3 \u2014 2-excitation Dicke state.",
    amplitudes: () => [[0, 0], [0, 0], [0, 0], [S3, 0], [0, 0], [S3, 0], [S3, 0], [0, 0]],
  },

  // ── 4-qubit ──
  {
    id: "ghz4", name: "GHZ (4Q)", numQubits: 4,
    description: "(|0000\u27E9 + |1111\u27E9)/\u221A2 \u2014 4-qubit cat state.",
    amplitudes: () => {
      const sv: Complex[] = Array.from({ length: 16 }, (): Complex => [0, 0]);
      sv[0] = [S2, 0];
      sv[15] = [S2, 0];
      return sv;
    },
  },
  {
    id: "w4", name: "W (4Q)", numQubits: 4,
    description: "(|0001\u27E9 + |0010\u27E9 + |0100\u27E9 + |1000\u27E9)/2 \u2014 4-qubit W state.",
    amplitudes: () => {
      const sv: Complex[] = Array.from({ length: 16 }, (): Complex => [0, 0]);
      sv[1] = [0.5, 0]; sv[2] = [0.5, 0]; sv[4] = [0.5, 0]; sv[8] = [0.5, 0];
      return sv;
    },
  },
  {
    id: "cluster4_ideal", name: "Cluster (4Q)", numQubits: 4,
    description: "Linear cluster state \u2014 CZ graph on |+\u27E9\u2297\u2074. Resource for measurement-based QC.",
    amplitudes: () => {
      // |cluster⟩ = CZ₂₃ CZ₁₂ CZ₀₁ |+⟩⊗4
      // Manually computed: equal amplitudes with specific sign pattern
      const a = 0.25;
      return [
        [a, 0], [a, 0], [a, 0], [-a, 0],   // 0000,0001,0010,0011
        [a, 0], [a, 0], [-a, 0], [a, 0],    // 0100,0101,0110,0111
        [a, 0], [a, 0], [-a, 0], [a, 0],    // 1000,1001,1010,1011
        [a, 0], [a, 0], [a, 0], [-a, 0],    // 1100,1101,1110,1111
      ];
    },
  },
];

/** Convert an IdealState to a SimSnapshot */
export function idealStateToSnapshot(state: IdealState): SimSnapshot {
  const sv = state.amplitudes();
  const dim = sv.length;
  const n = Math.log2(dim);
  const labels = Array.from({ length: dim }, (_, i) =>
    "|" + i.toString(2).padStart(n, "0") + "\u27E9",
  );
  return {
    stateVector: sv,
    probabilities: sv.map(([re, im]) => re * re + im * im),
    labels,
  };
}
