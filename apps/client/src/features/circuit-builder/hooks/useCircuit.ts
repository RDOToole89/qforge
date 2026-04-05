import { useReducer, useCallback } from "react";
import type { Circuit, CircuitAction, GateType, PlacedGate, Moment } from "../types";
import { getGateDef } from "../data/gateLibrary";

let nextId = 1;
function genId(): string {
  return `g${nextId++}`;
}

function createGate(gateType: GateType, qubit: number, numQubits: number, params?: number[]): PlacedGate {
  const def = getGateDef(gateType);
  let qubits: number[];

  if (def.numQubits === 1) {
    qubits = [qubit];
  } else if (def.numQubits === 2) {
    // Control above target, but ensure they're different qubits
    const control = qubit > 0 ? qubit - 1 : qubit + 1;
    qubits = [Math.min(control, numQubits - 1), qubit];
    // If still the same (only 1 qubit in circuit), this will be caught by validation
  } else {
    // Toffoli: two controls above target
    const c1 = qubit > 1 ? qubit - 2 : (qubit + 1 < numQubits ? qubit + 1 : qubit);
    const c2 = qubit > 0 ? qubit - 1 : (qubit + 2 < numQubits ? qubit + 2 : qubit);
    qubits = [c1, c2, qubit];
  }

  // Ensure all qubits are distinct
  const unique = [...new Set(qubits)];
  if (unique.length < qubits.length) {
    // Reassign to fill distinct qubits
    qubits = [];
    let next = 0;
    for (let i = 0; i < def.numQubits; i++) {
      while (qubits.includes(next) && next < numQubits) next++;
      if (next < numQubits) qubits.push(next);
      next++;
    }
    // Target is always last
    if (!qubits.includes(qubit) && qubits.length > 0) {
      qubits[qubits.length - 1] = qubit;
    }
  }

  return {
    id: genId(),
    gateType,
    qubits,
    params: params ?? def.defaultParams,
  };
}

/** Validate whether a gate can be placed. Returns error message or null if valid. */
export function validateGatePlacement(
  gateType: GateType,
  qubit: number,
  numQubits: number,
): string | null {
  const def = getGateDef(gateType);

  if (def.numQubits > numQubits) {
    return `${def.name} requires ${def.numQubits} qubits, but the circuit only has ${numQubits}. Increase the qubit count first.`;
  }

  if (def.numQubits === 2 && numQubits < 2) {
    return `${def.name} is a 2-qubit gate \u2014 it needs a control and a target on different qubits. Add at least 2 qubits to your circuit.`;
  }

  if (def.numQubits === 3 && numQubits < 3) {
    return `${def.name} (Toffoli) needs 3 distinct qubits \u2014 two controls and one target. Add at least 3 qubits to your circuit.`;
  }

  return null;
}

function circuitReducer(state: Circuit, action: CircuitAction): Circuit {
  switch (action.type) {
    case "ADD_GATE": {
      const gate = createGate(action.gateType, action.qubit, state.numQubits, action.params);
      const moments = [...state.moments];

      // Ensure enough moments exist
      while (moments.length <= action.momentIndex) {
        moments.push({ gates: [] });
      }

      moments[action.momentIndex] = {
        gates: [...moments[action.momentIndex].gates, gate],
      };

      return { ...state, moments };
    }

    case "REMOVE_GATE": {
      const moments = state.moments
        .map((m) => ({
          gates: m.gates.filter((g) => g.id !== action.gateId),
        }))
        .filter((m, i, arr) => {
          // Keep moment if it has gates, or if it's not trailing
          if (m.gates.length > 0) return true;
          // Remove trailing empty moments
          return arr.slice(i + 1).some((later) => later.gates.length > 0);
        });

      return { ...state, moments };
    }

    case "MOVE_GATE": {
      // Find and remove the gate from its current position
      let movedGate: PlacedGate | null = null;
      let moments = state.moments.map((m) => {
        const found = m.gates.find((g) => g.id === action.gateId);
        if (found) {
          // Recompute qubits: shift the target to the new qubit,
          // adjust control qubits relative to the new target
          const def = getGateDef(found.gateType);
          let newQubits: number[];
          if (def.numQubits === 1) {
            newQubits = [action.qubit];
          } else {
            // Preserve the offset pattern between control and target
            const oldTarget = found.qubits[found.qubits.length - 1];
            const shift = action.qubit - oldTarget;
            newQubits = found.qubits.map((q) => {
              const nq = q + shift;
              return Math.max(0, Math.min(nq, state.numQubits - 1));
            });
            // Ensure uniqueness
            const unique = [...new Set(newQubits)];
            if (unique.length < newQubits.length) {
              // Fallback: use createGate logic
              const fresh = createGate(found.gateType, action.qubit, state.numQubits, found.params);
              newQubits = fresh.qubits;
            }
          }
          movedGate = { ...found, qubits: newQubits };
          return { gates: m.gates.filter((g) => g.id !== action.gateId) };
        }
        return m;
      });

      if (!movedGate) return state;

      // Place in new position
      while (moments.length <= action.momentIndex) {
        moments.push({ gates: [] });
      }
      moments[action.momentIndex] = {
        gates: [...moments[action.momentIndex].gates, movedGate],
      };

      // Clean trailing empties
      while (moments.length > 0 && moments[moments.length - 1].gates.length === 0) {
        moments = moments.slice(0, -1);
      }

      return { ...state, moments };
    }

    case "SET_PARAMS": {
      const moments = state.moments.map((m) => ({
        gates: m.gates.map((g) =>
          g.id === action.gateId ? { ...g, params: action.params } : g
        ),
      }));
      return { ...state, moments };
    }

    case "SET_CONTROL": {
      const moments = state.moments.map((m) => ({
        gates: m.gates.map((g) => {
          if (g.id !== action.gateId) return g;
          const target = g.qubits[g.qubits.length - 1];
          return { ...g, qubits: [action.controlQubit, target] };
        }),
      }));
      return { ...state, moments };
    }

    case "SET_NUM_QUBITS": {
      // Remove any gates that reference qubits beyond the new count
      const moments = state.moments
        .map((m) => ({
          gates: m.gates.filter((g) =>
            g.qubits.every((q) => q < action.numQubits)
          ),
        }))
        .filter((m) => m.gates.length > 0);

      return { numQubits: action.numQubits, moments };
    }

    case "CLEAR":
      return { numQubits: state.numQubits, moments: [] };

    case "LOAD_PRESET":
      return { ...action.circuit };

    default:
      return state;
  }
}

const INITIAL_CIRCUIT: Circuit = {
  numQubits: 2,
  moments: [],
};

export function useCircuit() {
  const [circuit, dispatch] = useReducer(circuitReducer, INITIAL_CIRCUIT);

  const addGate = useCallback(
    (gateType: GateType, qubit: number, momentIndex?: number): { error: string } | { placed: { qubits: number[]; momentIndex: number } } | null => {
      // Validate placement
      const error = validateGatePlacement(gateType, qubit, circuit.numQubits);
      if (error) return { error };

      if (momentIndex !== undefined) {
        dispatch({ type: "ADD_GATE", gateType, qubit, momentIndex });
        const testGate = createGate(gateType, qubit, circuit.numQubits);
        return { placed: { qubits: testGate.qubits, momentIndex } };
      }

      // Compute which qubits this gate will occupy
      const testGate = createGate(gateType, qubit, circuit.numQubits);
      const gateQubits = testGate.qubits;

      // Find the latest moment where any of this gate's qubits are used,
      // then place at the next moment. This preserves circuit ordering.
      let latestUsed = -1;
      for (let mi = 0; mi < circuit.moments.length; mi++) {
        const usedQubits = new Set(
          circuit.moments[mi].gates.flatMap((g) => g.qubits),
        );
        if (gateQubits.some((q) => usedQubits.has(q))) {
          latestUsed = mi;
        }
      }

      // Try to share the moment after latestUsed if those qubits are free there
      let targetMoment = latestUsed + 1;

      // If targetMoment exists and has room, use it; otherwise append
      if (targetMoment < circuit.moments.length) {
        const usedInTarget = new Set(
          circuit.moments[targetMoment].gates.flatMap((g) => g.qubits),
        );
        if (!gateQubits.every((q) => !usedInTarget.has(q))) {
          // Conflict — use a new moment at the end
          targetMoment = circuit.moments.length;
        }
      }

      dispatch({ type: "ADD_GATE", gateType, qubit, momentIndex: targetMoment });
      return { placed: { qubits: testGate.qubits, momentIndex: targetMoment } };
    },
    [circuit.moments, circuit.numQubits],
  );

  const removeGate = useCallback((gateId: string) => {
    dispatch({ type: "REMOVE_GATE", gateId });
  }, []);

  const setParams = useCallback((gateId: string, params: number[]) => {
    dispatch({ type: "SET_PARAMS", gateId, params });
  }, []);

  const setControl = useCallback((gateId: string, controlQubit: number) => {
    dispatch({ type: "SET_CONTROL", gateId, controlQubit });
  }, []);

  const setNumQubits = useCallback((n: number) => {
    dispatch({ type: "SET_NUM_QUBITS", numQubits: n });
  }, []);

  const clear = useCallback(() => {
    dispatch({ type: "CLEAR" });
  }, []);

  const moveGate = useCallback((gateId: string, qubit: number, momentIndex: number) => {
    dispatch({ type: "MOVE_GATE", gateId, qubit, momentIndex });
  }, []);

  const loadPreset = useCallback((c: Circuit) => {
    dispatch({ type: "LOAD_PRESET", circuit: c });
  }, []);

  return {
    circuit,
    addGate,
    removeGate,
    moveGate,
    setParams,
    setControl,
    setNumQubits,
    clear,
    loadPreset,
  };
}
