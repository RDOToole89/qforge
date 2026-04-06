/** Gate type identifiers matching Qiskit gate names for backend serialization */
export type GateType =
  | "H"
  | "X"
  | "Y"
  | "Z"
  | "S"
  | "T"
  | "SX"
  | "Rx"
  | "Ry"
  | "Rz"
  | "CNOT"
  | "CZ"
  | "SWAP"
  | "Toffoli";

/** A gate placed on the circuit */
export interface PlacedGate {
  id: string;
  gateType: GateType;
  /** Ordered qubit indices: [target] for 1-qubit, [control, target] for 2-qubit, [c1, c2, target] for 3-qubit */
  qubits: number[];
  /** Rotation angle(s) for parametric gates (Rx, Ry, Rz) */
  params?: number[];
}

/** A vertical slice of the circuit — gates that execute simultaneously */
export interface Moment {
  gates: PlacedGate[];
}

/** The full circuit state */
export interface Circuit {
  numQubits: number;
  moments: Moment[];
}

/** Complex number as [real, imaginary] */
export type Complex = [number, number];

/** Simulation result at a moment boundary */
export interface SimSnapshot {
  /** Complex amplitudes, length 2^n */
  stateVector: Complex[];
  /** |amplitude|^2 for each basis state */
  probabilities: number[];
  /** Basis state labels: "|00>", "|01>", etc. */
  labels: string[];
}

/** Gate definition metadata for the palette and info panels */
export interface GateDefinition {
  type: GateType;
  name: string;
  /** Number of qubits this gate acts on */
  numQubits: 1 | 2 | 3;
  /** Whether the gate takes rotation parameters */
  parametric: boolean;
  paramLabels?: string[];
  /** Default parameter values */
  defaultParams?: number[];
  /** LaTeX representation of the matrix */
  matrixLatex: string;
  /** Plain-English description */
  description: string;
  /** Accent color for the gate block */
  color: string;
  /** Short label shown on the SVG gate block */
  label: string;
  /** Link to existing glossary term ID */
  glossaryTermId?: string;
  /** Qiskit gate name for backend serialization */
  qiskitName: string;
}

/** A preset circuit with educational context */
export interface CircuitPreset {
  id: string;
  name: string;
  description: string;
  /** What the student will learn */
  learns: string;
  circuit: Circuit;
  /** Plain-English explanation of what each moment does */
  steps?: string[];
  /** Real-world applications and use cases */
  applications?: string[];
}

/** Pattern-matched educational narrative */
export interface NarrativeStep {
  momentIndex: number;
  /** Dirac notation of the state */
  diracNotation: string;
  /** Plain-English explanation */
  explanation: string;
  /** Glossary term IDs relevant to this step */
  glossaryTermIds: string[];
}

/** Circuit reducer actions */
export type CircuitAction =
  | { type: "ADD_GATE"; gateType: GateType; qubit: number; momentIndex: number; params?: number[] }
  | { type: "REMOVE_GATE"; gateId: string }
  | { type: "MOVE_GATE"; gateId: string; qubit: number; momentIndex: number }
  | { type: "SET_PARAMS"; gateId: string; params: number[] }
  | { type: "SET_CONTROL"; gateId: string; controlQubit: number }
  | { type: "SET_NUM_QUBITS"; numQubits: number }
  | { type: "CLEAR" }
  | { type: "LOAD_PRESET"; circuit: Circuit };
