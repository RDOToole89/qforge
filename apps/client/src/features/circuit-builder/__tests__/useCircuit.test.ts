/**
 * Tests for the pure circuit reducer and gate-placement validation. These cover
 * the non-math circuit-editing logic (moment/gate list manipulation), not the
 * statevector simulator.
 */
import { describe, expect, it } from "vitest";
import { circuitReducer, validateGatePlacement } from "../hooks/useCircuit";
import type { Circuit } from "../types";

const emptyCircuit = (numQubits = 3): Circuit => ({ numQubits, moments: [] });

/** Add a gate via the reducer and return [newState, placedGate]. */
function addGate(state: Circuit, gateType: Parameters<typeof validateGatePlacement>[0], qubit: number, momentIndex: number) {
  const next = circuitReducer(state, { type: "ADD_GATE", gateType, qubit, momentIndex });
  const gate = next.moments[momentIndex].gates.at(-1)!;
  return [next, gate] as const;
}

describe("validateGatePlacement", () => {
  it("accepts a single-qubit gate on an existing qubit", () => {
    expect(validateGatePlacement("H", 0, 3)).toBeNull();
  });

  it("rejects a 2-qubit gate when the circuit has fewer than 2 qubits", () => {
    expect(validateGatePlacement("CNOT", 0, 1)).toMatch(/2 qubits|control and a target/);
  });

  it("rejects a Toffoli when the circuit has fewer than 3 qubits", () => {
    expect(validateGatePlacement("Toffoli", 0, 2)).toMatch(/Toffoli|3 distinct qubits/);
  });

  it("accepts multi-qubit gates once enough qubits exist", () => {
    expect(validateGatePlacement("CNOT", 1, 2)).toBeNull();
    expect(validateGatePlacement("Toffoli", 2, 3)).toBeNull();
  });
});

describe("circuitReducer", () => {
  it("ADD_GATE places a single-qubit gate and grows the moment list", () => {
    const [s, gate] = addGate(emptyCircuit(3), "H", 0, 0);
    expect(s.moments).toHaveLength(1);
    expect(gate.gateType).toBe("H");
    expect(gate.qubits).toEqual([0]);
    expect(gate.id).toBeTruthy();
  });

  it("ADD_GATE assigns control/target qubits for a 2-qubit gate", () => {
    const [, gate] = addGate(emptyCircuit(3), "CNOT", 1, 0);
    // control above target: [0, 1]
    expect(gate.qubits).toEqual([0, 1]);
  });

  it("ADD_GATE pads intermediate moments with empties", () => {
    const [s] = addGate(emptyCircuit(3), "X", 0, 2);
    expect(s.moments).toHaveLength(3);
    expect(s.moments[0].gates).toEqual([]);
    expect(s.moments[1].gates).toEqual([]);
    expect(s.moments[2].gates).toHaveLength(1);
  });

  it("REMOVE_GATE drops the gate and trims trailing empty moments", () => {
    let s = emptyCircuit(3);
    const [s1, g] = addGate(s, "H", 0, 0);
    s = s1;
    s = circuitReducer(s, { type: "REMOVE_GATE", gateId: g.id });
    expect(s.moments).toHaveLength(0);
  });

  it("SET_PARAMS updates only the matching gate's params", () => {
    const [s1, g] = addGate(emptyCircuit(3), "Rx", 0, 0);
    const s2 = circuitReducer(s1, { type: "SET_PARAMS", gateId: g.id, params: [1.5] });
    expect(s2.moments[0].gates[0].params).toEqual([1.5]);
  });

  it("SET_CONTROL changes the control qubit but keeps the target last", () => {
    const [s1, g] = addGate(emptyCircuit(3), "CNOT", 1, 0); // [0, 1]
    const s2 = circuitReducer(s1, { type: "SET_CONTROL", gateId: g.id, controlQubit: 2 });
    expect(s2.moments[0].gates[0].qubits).toEqual([2, 1]);
  });

  it("SET_NUM_QUBITS removes gates that reference now-invalid qubits", () => {
    let s = emptyCircuit(3);
    s = addGate(s, "X", 0, 0)[0];
    s = circuitReducer(s, { type: "ADD_GATE", gateType: "X", qubit: 2, momentIndex: 1 });
    const shrunk = circuitReducer(s, { type: "SET_NUM_QUBITS", numQubits: 1 });
    expect(shrunk.numQubits).toBe(1);
    // Only the qubit-0 gate survives; the qubit-2 gate is dropped.
    const allGates = shrunk.moments.flatMap((m) => m.gates);
    expect(allGates).toHaveLength(1);
    expect(allGates[0].qubits).toEqual([0]);
  });

  it("MOVE_GATE relocates a single-qubit gate to a new qubit and moment", () => {
    const [s1, g] = addGate(emptyCircuit(3), "H", 0, 0);
    const s2 = circuitReducer(s1, { type: "MOVE_GATE", gateId: g.id, qubit: 2, momentIndex: 1 });
    const moved = s2.moments.flatMap((m) => m.gates).find((x) => x.id === g.id)!;
    expect(moved.qubits).toEqual([2]);
    expect(s2.moments[1].gates.some((x) => x.id === g.id)).toBe(true);
  });

  it("MOVE_GATE is a no-op for an unknown gate id", () => {
    const [s1] = addGate(emptyCircuit(3), "H", 0, 0);
    const s2 = circuitReducer(s1, { type: "MOVE_GATE", gateId: "nope", qubit: 1, momentIndex: 1 });
    expect(s2).toBe(s1);
  });

  it("CLEAR empties the moments but preserves the qubit count", () => {
    const [s1] = addGate(emptyCircuit(4), "H", 0, 0);
    const s2 = circuitReducer(s1, { type: "CLEAR" });
    expect(s2).toEqual({ numQubits: 4, moments: [] });
  });

  it("LOAD_PRESET replaces the whole circuit", () => {
    const preset: Circuit = {
      numQubits: 2,
      moments: [{ gates: [{ id: "p1", gateType: "H", qubits: [0] }] }],
    };
    const s = circuitReducer(emptyCircuit(3), { type: "LOAD_PRESET", circuit: preset });
    expect(s).toEqual(preset);
  });
});
