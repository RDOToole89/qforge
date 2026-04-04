import { useReducer, useCallback } from "react";
import type { Circuit, CircuitAction, GateType, PlacedGate, Moment } from "../types";
import { getGateDef } from "../data/gateLibrary";

let nextId = 1;
function genId(): string {
  return `g${nextId++}`;
}

function createGate(gateType: GateType, qubit: number, params?: number[]): PlacedGate {
  const def = getGateDef(gateType);
  const qubits: number[] =
    def.numQubits === 1
      ? [qubit]
      : def.numQubits === 2
        ? [Math.max(0, qubit - 1), qubit] // default control = qubit above target
        : [Math.max(0, qubit - 2), Math.max(0, qubit - 1), qubit]; // Toffoli

  return {
    id: genId(),
    gateType,
    qubits,
    params: params ?? def.defaultParams,
  };
}

function circuitReducer(state: Circuit, action: CircuitAction): Circuit {
  switch (action.type) {
    case "ADD_GATE": {
      const gate = createGate(action.gateType, action.qubit, action.params);
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
      // Find and remove the gate
      let movedGate: PlacedGate | null = null;
      let moments = state.moments.map((m) => {
        const found = m.gates.find((g) => g.id === action.gateId);
        if (found) {
          movedGate = { ...found, qubits: [action.qubit] };
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
    (gateType: GateType, qubit: number, momentIndex?: number) => {
      const mi = momentIndex ?? circuit.moments.length;
      dispatch({ type: "ADD_GATE", gateType, qubit, momentIndex: mi });
    },
    [circuit.moments.length]
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

  const loadPreset = useCallback((c: Circuit) => {
    dispatch({ type: "LOAD_PRESET", circuit: c });
  }, []);

  return {
    circuit,
    addGate,
    removeGate,
    setParams,
    setControl,
    setNumQubits,
    clear,
    loadPreset,
  };
}
