import type { GateDefinition, GateType } from "../types";

export const GATE_DEFS: Record<GateType, GateDefinition> = {
  H: {
    type: "H",
    name: "Hadamard",
    numQubits: 1,
    parametric: false,
    matrixLatex: "\\frac{1}{\\sqrt{2}}\\begin{pmatrix}1&1\\\\1&-1\\end{pmatrix}",
    description:
      "Creates equal superposition. Maps |0> to |+> and |1> to |->. The most common first step in quantum algorithms.",
    color: "#6366f1",
    label: "H",
    glossaryTermId: "hadamard",
    qiskitName: "h",
  },
  X: {
    type: "X",
    name: "Pauli-X (NOT)",
    numQubits: 1,
    parametric: false,
    matrixLatex: "\\begin{pmatrix}0&1\\\\1&0\\end{pmatrix}",
    description:
      "Quantum NOT gate. Flips |0> to |1> and vice versa. A 180 degree rotation around the X-axis of the Bloch sphere.",
    color: "#ef4444",
    label: "X",
    glossaryTermId: "pauli_x",
    qiskitName: "x",
  },
  Y: {
    type: "Y",
    name: "Pauli-Y",
    numQubits: 1,
    parametric: false,
    matrixLatex: "\\begin{pmatrix}0&-i\\\\i&0\\end{pmatrix}",
    description:
      "Combines a bit flip with a phase flip. A 180 degree rotation around the Y-axis of the Bloch sphere.",
    color: "#22c55e",
    label: "Y",
    glossaryTermId: "pauli_y",
    qiskitName: "y",
  },
  Z: {
    type: "Z",
    name: "Pauli-Z",
    numQubits: 1,
    parametric: false,
    matrixLatex: "\\begin{pmatrix}1&0\\\\0&-1\\end{pmatrix}",
    description:
      "Phase flip gate. Leaves |0> unchanged and maps |1> to -|1>. Invisible to Z-basis measurement.",
    color: "#3b82f6",
    label: "Z",
    glossaryTermId: "pauli_z",
    qiskitName: "z",
  },
  S: {
    type: "S",
    name: "S Gate (Phase)",
    numQubits: 1,
    parametric: false,
    matrixLatex: "\\begin{pmatrix}1&0\\\\0&i\\end{pmatrix}",
    description:
      "Quarter-turn phase gate. Adds a 90 degree phase to |1>. The square root of Z: S*S = Z.",
    color: "#8b5cf6",
    label: "S",
    qiskitName: "s",
  },
  T: {
    type: "T",
    name: "T Gate",
    numQubits: 1,
    parametric: false,
    matrixLatex: "\\begin{pmatrix}1&0\\\\0&e^{i\\pi/4}\\end{pmatrix}",
    description:
      "Eighth-turn phase gate. Adds a 45 degree phase to |1>. Essential for universal quantum computation. The square root of S.",
    color: "#a855f7",
    label: "T",
    qiskitName: "t",
  },
  Rx: {
    type: "Rx",
    name: "Rx (X-Rotation)",
    numQubits: 1,
    parametric: true,
    paramLabels: ["\u03b8"],
    defaultParams: [Math.PI / 2],
    matrixLatex:
      "\\begin{pmatrix}\\cos\\frac{\\theta}{2}&-i\\sin\\frac{\\theta}{2}\\\\-i\\sin\\frac{\\theta}{2}&\\cos\\frac{\\theta}{2}\\end{pmatrix}",
    description:
      "Rotates the qubit by angle theta around the X-axis of the Bloch sphere. Rx(pi) = X gate.",
    color: "#f97316",
    label: "Rx",
    qiskitName: "rx",
  },
  Ry: {
    type: "Ry",
    name: "Ry (Y-Rotation)",
    numQubits: 1,
    parametric: true,
    paramLabels: ["\u03b8"],
    defaultParams: [Math.PI / 2],
    matrixLatex:
      "\\begin{pmatrix}\\cos\\frac{\\theta}{2}&-\\sin\\frac{\\theta}{2}\\\\\\sin\\frac{\\theta}{2}&\\cos\\frac{\\theta}{2}\\end{pmatrix}",
    description:
      "Rotates the qubit by angle theta around the Y-axis of the Bloch sphere. Ry(pi) = Y gate (up to global phase).",
    color: "#eab308",
    label: "Ry",
    qiskitName: "ry",
  },
  Rz: {
    type: "Rz",
    name: "Rz (Z-Rotation)",
    numQubits: 1,
    parametric: true,
    paramLabels: ["\u03b8"],
    defaultParams: [Math.PI / 2],
    matrixLatex:
      "\\begin{pmatrix}e^{-i\\theta/2}&0\\\\0&e^{i\\theta/2}\\end{pmatrix}",
    description:
      "Rotates the qubit by angle theta around the Z-axis of the Bloch sphere. Rz(pi) = Z gate (up to global phase).",
    color: "#14b8a6",
    label: "Rz",
    qiskitName: "rz",
  },
  CNOT: {
    type: "CNOT",
    name: "CNOT (Controlled-X)",
    numQubits: 2,
    parametric: false,
    matrixLatex:
      "|0\\rangle\\langle0|\\otimes I + |1\\rangle\\langle1|\\otimes X",
    description:
      "If control qubit is |1>, flip the target qubit. The primary tool for creating entanglement. H + CNOT = Bell state.",
    color: "#6366f1",
    label: "CX",
    glossaryTermId: "cnot",
    qiskitName: "cx",
  },
  CZ: {
    type: "CZ",
    name: "CZ (Controlled-Z)",
    numQubits: 2,
    parametric: false,
    matrixLatex:
      "\\text{diag}(1, 1, 1, -1)",
    description:
      "Applies a phase flip when both qubits are |1>. Symmetric between control and target. Used to build cluster states.",
    color: "#3b82f6",
    label: "CZ",
    glossaryTermId: "cz_gate",
    qiskitName: "cz",
  },
  SWAP: {
    type: "SWAP",
    name: "SWAP",
    numQubits: 2,
    parametric: false,
    matrixLatex:
      "\\begin{pmatrix}1&0&0&0\\\\0&0&1&0\\\\0&1&0&0\\\\0&0&0&1\\end{pmatrix}",
    description:
      "Exchanges the states of two qubits. Can be decomposed into three CNOTs.",
    color: "#ec4899",
    label: "SW",
    qiskitName: "swap",
  },
  Toffoli: {
    type: "Toffoli",
    name: "Toffoli (CCX)",
    numQubits: 3,
    parametric: false,
    matrixLatex: "\\text{CCX: flip target iff both controls are } |1\\rangle",
    description:
      "Flips target qubit only when both control qubits are |1>. Universal for classical reversible computation.",
    color: "#f59e0b",
    label: "CCX",
    glossaryTermId: "toffoli",
    qiskitName: "ccx",
  },
};

/** All single-qubit gates */
export const SINGLE_QUBIT_GATES: GateType[] = ["H", "X", "Y", "Z", "S", "T", "Rx", "Ry", "Rz"];

/** All multi-qubit gates */
export const MULTI_QUBIT_GATES: GateType[] = ["CNOT", "CZ", "SWAP", "Toffoli"];

/** Get the GateDefinition for a gate type */
export function getGateDef(gateType: GateType): GateDefinition {
  return GATE_DEFS[gateType];
}
