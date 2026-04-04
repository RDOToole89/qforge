import { useMemo } from "react";
import type { Circuit, SimSnapshot, Moment, PlacedGate } from "../types";
import { recognizeState } from "./useSimulator";
import { stateVectorToBloch } from "@/src/features/bloch-sphere/math";

export interface StepNarrative {
  /** Contextual explanation of what this step does */
  explanation: string;
  /** Key insight or "aha" moment for the learner */
  insight?: string;
}

/**
 * Generate dynamic step-by-step narratives for any circuit,
 * based on the gates applied and the resulting state.
 */
export function generateNarrative(
  moment: Moment,
  stepIndex: number,
  prevSnapshot: SimSnapshot,
  currentSnapshot: SimSnapshot,
  circuit: Circuit,
): StepNarrative {
  const { numQubits } = circuit;
  const gates = moment.gates;
  const parts: string[] = [];
  let insight: string | undefined;

  for (const gate of gates) {
    parts.push(describeGate(gate, prevSnapshot, currentSnapshot, numQubits, stepIndex, circuit));
  }

  // Check for emergent properties
  insight = detectInsight(gates, prevSnapshot, currentSnapshot, numQubits, stepIndex, circuit);

  return {
    explanation: parts.join(" "),
    insight,
  };
}

function describeGate(
  gate: PlacedGate,
  prev: SimSnapshot,
  curr: SimSnapshot,
  numQubits: number,
  _stepIndex: number,
  circuit: Circuit,
): string {
  const { gateType, qubits, params } = gate;
  const q = qubits[qubits.length - 1]; // target qubit

  // Get the Bloch vector of the target qubit before and after
  const before = stateVectorToBloch(prev.stateVector, q, numQubits);
  const after = stateVectorToBloch(curr.stateVector, q, numQubits);

  const wasAtPole = (v: { rz: number }) => Math.abs(Math.abs(v.rz) - 1) < 0.05;
  const isAtOrigin = (v: { rx: number; ry: number; rz: number }) =>
    Math.sqrt(v.rx * v.rx + v.ry * v.ry + v.rz * v.rz) < 0.15;
  const wasAtOrigin = isAtOrigin(before);
  const nowAtOrigin = isAtOrigin(after);

  switch (gateType) {
    case "H": {
      if (wasAtPole(before) && before.rz > 0) {
        return `H on q${q}: takes |0\u27E9 to |+\u27E9 \u2014 creates equal superposition. The qubit moves from the north pole to the equator of the Bloch sphere.`;
      }
      if (wasAtPole(before) && before.rz < 0) {
        return `H on q${q}: takes |1\u27E9 to |\u2212\u27E9 \u2014 creates superposition with a relative minus sign.`;
      }
      if (Math.abs(before.rx) > 0.9) {
        return `H on q${q}: maps back from the equator to a pole \u2014 converts superposition basis back to computational basis. This is the key step in interference-based algorithms.`;
      }
      if (wasAtOrigin) {
        return `H on q${q}: this qubit is maximally mixed (entangled with others), so H rotates its local basis but doesn't change the entanglement structure.`;
      }
      return `H on q${q}: applies a Hadamard rotation, swapping the X and Z axes of the Bloch sphere.`;
    }

    case "X": {
      if (wasAtPole(before) && before.rz > 0) {
        return `X on q${q}: flips |0\u27E9 to |1\u27E9 \u2014 a quantum NOT gate. The Bloch vector flips from north to south pole.`;
      }
      if (wasAtPole(before) && before.rz < 0) {
        return `X on q${q}: flips |1\u27E9 back to |0\u27E9. Undoes a previous bit flip.`;
      }
      return `X on q${q}: applies a \u03C0 rotation around the X-axis, flipping the computational basis.`;
    }

    case "Y":
      return `Y on q${q}: applies a \u03C0 rotation around the Y-axis \u2014 combines a bit flip with a phase flip.`;

    case "Z": {
      if (Math.abs(before.rx) > 0.5 || Math.abs(before.ry) > 0.5) {
        return `Z on q${q}: flips the phase of the superposition. On the Bloch sphere, the equatorial component rotates by 180\u00B0. This is invisible if you only measure in the Z basis.`;
      }
      if (wasAtPole(before)) {
        return `Z on q${q}: adds a global phase to |1\u27E9. Since the qubit is in a Z eigenstate, the only effect is a phase factor \u2014 no observable change in probabilities.`;
      }
      return `Z on q${q}: applies a phase flip, rotating by \u03C0 around the Z-axis.`;
    }

    case "S":
      return `S on q${q}: adds a 90\u00B0 phase rotation around Z. Moves the equatorial component from X toward Y. Two S gates = one Z gate.`;

    case "T":
      return `T on q${q}: adds a 45\u00B0 phase (\u03C0/4). This is the non-Clifford gate that makes universal quantum computation possible. It's the most expensive gate on real hardware.`;

    case "SX":
      return `\u221AX on q${q}: half of an X rotation. Moves the qubit halfway from pole to equator. Common in transpiled IBM circuits.`;

    case "Rx": {
      const theta = params?.[0] ?? Math.PI / 2;
      const deg = (theta * 180 / Math.PI).toFixed(0);
      return `Rx(${deg}\u00B0) on q${q}: rotates around the X-axis by ${deg}\u00B0. ${Math.abs(theta - Math.PI) < 0.05 ? "At \u03C0, this is equivalent to the X gate." : `Tunes the superposition amplitude continuously.`}`;
    }

    case "Ry": {
      const theta = params?.[0] ?? Math.PI / 2;
      const deg = (theta * 180 / Math.PI).toFixed(0);
      return `Ry(${deg}\u00B0) on q${q}: rotates around the Y-axis by ${deg}\u00B0. ${Math.abs(theta - Math.PI) < 0.05 ? "At \u03C0, this is equivalent to the Y gate." : "This creates real-valued superpositions (no imaginary components)."}`;
    }

    case "Rz": {
      const theta = params?.[0] ?? Math.PI / 2;
      const deg = (theta * 180 / Math.PI).toFixed(0);
      return `Rz(${deg}\u00B0) on q${q}: rotates the phase by ${deg}\u00B0 around Z. ${Math.abs(theta - Math.PI) < 0.05 ? "At \u03C0, this equals a Z gate." : Math.abs(theta - Math.PI / 2) < 0.05 ? "At 90\u00B0, this equals an S gate." : "Adjusts the relative phase between |0\u27E9 and |1\u27E9."}`;
    }

    case "CNOT": {
      const ctrl = qubits[0], tgt = qubits[1];
      const ctrlBefore = stateVectorToBloch(prev.stateVector, ctrl, numQubits);
      const ctrlInSuperposition = Math.abs(ctrlBefore.rx) > 0.3 || Math.abs(ctrlBefore.ry) > 0.3;
      const ctrlIsEntangled = isAtOrigin(ctrlBefore);

      if (ctrlInSuperposition && wasAtPole(stateVectorToBloch(prev.stateVector, tgt, numQubits))) {
        if (nowAtOrigin) {
          return `CNOT q${ctrl}\u2192q${tgt}: the control is in superposition, so the target gets conditionally flipped \u2014 this creates entanglement. Both qubits are now correlated: measuring one instantly determines the other.`;
        }
        return `CNOT q${ctrl}\u2192q${tgt}: the control is in superposition, creating a conditional flip on the target. The qubits become correlated.`;
      }
      if (ctrlIsEntangled) {
        return `CNOT q${ctrl}\u2192q${tgt}: the control qubit is already entangled, so this CNOT spreads that entanglement to q${tgt}. The entanglement network grows.`;
      }
      if (wasAtPole(ctrlBefore) && ctrlBefore.rz > 0) {
        return `CNOT q${ctrl}\u2192q${tgt}: control q${ctrl} is |0\u27E9, so nothing happens \u2014 the target is unchanged. CNOT only acts when the control is |1\u27E9.`;
      }
      if (wasAtPole(ctrlBefore) && ctrlBefore.rz < 0) {
        return `CNOT q${ctrl}\u2192q${tgt}: control q${ctrl} is |1\u27E9, so the target q${tgt} is flipped. This is a classical-like conditional operation.`;
      }
      return `CNOT q${ctrl}\u2192q${tgt}: flips q${tgt} conditionally on q${ctrl}. This is the primary entangling gate in circuit-model quantum computing.`;
    }

    case "CZ": {
      const q0 = qubits[0], q1 = qubits[1];
      const b0 = stateVectorToBloch(prev.stateVector, q0, numQubits);
      const b1 = stateVectorToBloch(prev.stateVector, q1, numQubits);
      const bothSuperposition = (Math.abs(b0.rx) > 0.3 || Math.abs(b0.ry) > 0.3) &&
                                 (Math.abs(b1.rx) > 0.3 || Math.abs(b1.ry) > 0.3);

      if (bothSuperposition) {
        return `CZ q${q0}\u2013q${q1}: both qubits are in superposition, so CZ creates a phase entanglement \u2014 the |11\u27E9 component gets a minus sign. Unlike CNOT, CZ is symmetric: neither qubit is "control" or "target."`;
      }
      return `CZ q${q0}\u2013q${q1}: applies a \u22121 phase when both qubits are |1\u27E9. This creates phase-based correlations between the qubits.`;
    }

    case "SWAP": {
      const q0 = qubits[0], q1 = qubits[1];
      return `SWAP q${q0}\u2194q${q1}: exchanges the complete quantum states of the two qubits. Any entanglement or superposition is transferred, not destroyed.`;
    }

    case "Toffoli": {
      const c0 = qubits[0], c1 = qubits[1], tgt = qubits[2];
      return `Toffoli q${c0},q${c1}\u2192q${tgt}: flips q${tgt} only when both q${c0} and q${c1} are |1\u27E9. This is a quantum AND gate \u2014 it's universal for classical reversible computation.`;
    }

    default:
      return `Applied ${gateType} on q${qubits.join(",")}.`;
  }
}

function detectInsight(
  gates: PlacedGate[],
  prev: SimSnapshot,
  curr: SimSnapshot,
  numQubits: number,
  stepIndex: number,
  circuit: Circuit,
): string | undefined {
  // Check if entanglement was just created
  const prevEntangled = countEntangledPairs(prev, numQubits);
  const currEntangled = countEntangledPairs(curr, numQubits);

  if (currEntangled > prevEntangled) {
    const newPairs = currEntangled - prevEntangled;
    if (prevEntangled === 0) {
      return `Entanglement created! ${newPairs === 1 ? "One pair of qubits is" : `${newPairs} pairs of qubits are`} now quantum-correlated. Their individual Bloch vectors have moved toward the center of the sphere \u2014 the information is now in correlations, not individual qubit states.`;
    }
    return `Entanglement network expanded \u2014 ${newPairs} new correlated ${newPairs === 1 ? "pair" : "pairs"}.`;
  }

  if (currEntangled < prevEntangled && currEntangled === 0) {
    return "Entanglement broken \u2014 all qubits are now separable (product state). Each qubit has a definite Bloch vector again.";
  }

  // Check if state became recognizable
  const stateName = recognizeState(curr);
  const prevStateName = recognizeState(prev);
  if (stateName && stateName !== prevStateName) {
    return `This step produced a ${stateName}!`;
  }

  // Check if we went to uniform superposition
  const dim = curr.stateVector.length;
  const expectedUniform = 1 / dim;
  let isUniform = true;
  for (let i = 0; i < dim; i++) {
    const p = curr.probabilities[i];
    if (Math.abs(p - expectedUniform) > 0.02) { isUniform = false; break; }
  }
  let wasUniform = true;
  for (let i = 0; i < dim; i++) {
    const p = prev.probabilities[i];
    if (Math.abs(p - expectedUniform) > 0.02) { wasUniform = false; break; }
  }
  if (isUniform && !wasUniform) {
    return "All outcomes are now equally likely \u2014 the state is in uniform superposition across all computational basis states.";
  }

  // Check if a qubit became maximally mixed (entangled)
  for (const gate of gates) {
    if (gate.gateType === "CNOT" || gate.gateType === "CZ") {
      for (const q of gate.qubits) {
        const bAfter = stateVectorToBloch(curr.stateVector, q, numQubits);
        const bBefore = stateVectorToBloch(prev.stateVector, q, numQubits);
        const lenAfter = Math.sqrt(bAfter.rx ** 2 + bAfter.ry ** 2 + bAfter.rz ** 2);
        const lenBefore = Math.sqrt(bBefore.rx ** 2 + bBefore.ry ** 2 + bBefore.rz ** 2);
        if (lenBefore > 0.7 && lenAfter < 0.2) {
          return `q${q}'s Bloch vector collapsed to the center \u2014 it's now maximally mixed. This means q${q} is maximally entangled with other qubits. You can't describe its state independently anymore.`;
        }
      }
    }
  }

  return undefined;
}

/** Count qubit pairs with significant entanglement (Bloch vector at origin) */
function countEntangledPairs(snapshot: SimSnapshot, numQubits: number): number {
  if (numQubits < 2) return 0;
  let count = 0;
  for (let i = 0; i < numQubits; i++) {
    const b = stateVectorToBloch(snapshot.stateVector, i, numQubits);
    const len = Math.sqrt(b.rx ** 2 + b.ry ** 2 + b.rz ** 2);
    if (len < 0.3) count++;
  }
  // Rough: if N qubits are mixed, there are ~N*(N-1)/2 entangled pairs
  return Math.floor(count * (count - 1) / 2);
}

/**
 * React hook: generate narratives for all steps in a circuit.
 */
export function useNarrative(circuit: Circuit, snapshots: SimSnapshot[]): StepNarrative[] {
  return useMemo(() => {
    const narratives: StepNarrative[] = [];
    for (let i = 0; i < circuit.moments.length; i++) {
      if (i + 1 >= snapshots.length) break;
      narratives.push(
        generateNarrative(circuit.moments[i], i, snapshots[i], snapshots[i + 1], circuit),
      );
    }
    return narratives;
  }, [circuit, snapshots]);
}
