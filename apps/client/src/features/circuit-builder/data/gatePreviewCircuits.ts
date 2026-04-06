/**
 * Demo circuits for gate preview: when you click a gate in the palette,
 * the Bloch sphere animates what that gate does to a carefully chosen state.
 *
 * Design principle: each gate's initial state is chosen so the transformation
 * is MAXIMALLY VISIBLE on the Bloch sphere. Phase gates start in |+⟩ (equator)
 * so the phase rotation is visible. Entangling gates start with superposition
 * on the control so entanglement is created.
 */
import type { Circuit, GateType } from "../types";

interface GatePreview {
  caption: string;
  circuit: Circuit;
}

export const GATE_PREVIEW_CIRCUITS: Record<GateType, GatePreview> = {
  // ── Pauli gates: show axis rotations from interesting starting states ──

  H: {
    caption: "Hadamard: |0\u27E9 \u2192 |+\u27E9 \u2014 north pole slides to equator",
    circuit: {
      numQubits: 2,
      moments: [
        // q1 starts at |+⟩ for reference (shows equator position)
        { gates: [{ id: "d0", gateType: "H", qubits: [1] }] },
        // The actual H gate on q0
        { gates: [{ id: "d1", gateType: "H", qubits: [0] }] },
      ],
    },
  },

  X: {
    caption: "Pauli-X: flips |0\u27E9 \u2194 |1\u27E9 \u2014 \u03C0 rotation around X-axis",
    circuit: {
      numQubits: 2,
      moments: [
        // Start q0 at a tilted state so the flip is dramatic
        { gates: [{ id: "d0", gateType: "Ry", qubits: [0], params: [Math.PI / 3] }] },
        // X flips it across the equator
        { gates: [{ id: "d1", gateType: "X", qubits: [0] }] },
      ],
    },
  },

  Y: {
    caption: "Pauli-Y: combines bit flip + phase flip \u2014 \u03C0 rotation around Y",
    circuit: {
      numQubits: 2,
      moments: [
        // Start at |+⟩ so Y's phase effect is visible
        { gates: [{ id: "d0", gateType: "H", qubits: [0] }] },
        // Y rotates from +X to -X with a phase
        { gates: [{ id: "d1", gateType: "Y", qubits: [0] }] },
      ],
    },
  },

  Z: {
    caption: "Pauli-Z: |+\u27E9 \u2192 |\u2212\u27E9 \u2014 phase flip on equator (invisible on poles!)",
    circuit: {
      numQubits: 2,
      moments: [
        // Must start on equator — Z on |0⟩ does nothing visible
        { gates: [{ id: "d0", gateType: "H", qubits: [0] }] },
        // Z flips the X-component sign
        { gates: [{ id: "d1", gateType: "Z", qubits: [0] }] },
      ],
    },
  },

  // ── Phase gates: start on equator so phase rotation is visible ──

  S: {
    caption: "S gate: |+\u27E9 \u2192 |+i\u27E9 \u2014 90\u00B0 phase rotation along equator",
    circuit: {
      numQubits: 2,
      moments: [
        // Put q0 on equator at |+⟩, q1 at |+i⟩ for comparison
        { gates: [
          { id: "d0", gateType: "H", qubits: [0] },
          { id: "d0b", gateType: "H", qubits: [1] },
        ] },
        { gates: [{ id: "d0c", gateType: "S", qubits: [1] }] },
        // Now apply S to q0 — it should end up at same position as q1
        { gates: [{ id: "d1", gateType: "S", qubits: [0] }] },
      ],
    },
  },

  T: {
    caption: "T gate: 45\u00B0 phase rotation \u2014 the key to universal quantum computing",
    circuit: {
      numQubits: 2,
      moments: [
        // q0 on equator, q1 shows the T-rotated position for reference
        { gates: [
          { id: "d0", gateType: "H", qubits: [0] },
          { id: "d0b", gateType: "H", qubits: [1] },
        ] },
        { gates: [{ id: "d0c", gateType: "T", qubits: [1] }] },
        // Apply T to q0
        { gates: [{ id: "d1", gateType: "T", qubits: [0] }] },
      ],
    },
  },

  SX: {
    caption: "\u221AX: half of X rotation \u2014 |0\u27E9 goes halfway to equator",
    circuit: {
      numQubits: 2,
      moments: [
        // q1 at full X position for comparison
        { gates: [{ id: "d0", gateType: "H", qubits: [1] }] },
        // √X on q0 — halfway between |0⟩ and |+⟩
        { gates: [{ id: "d1", gateType: "SX", qubits: [0] }] },
      ],
    },
  },

  // ── Rotation gates: show continuous rotation from a visible starting point ──

  Rx: {
    caption: "Rx(\u03C0/2): 90\u00B0 around X-axis \u2014 tilts from pole toward equator",
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "d1", gateType: "Rx", qubits: [0], params: [Math.PI / 2] }] },
      ],
    },
  },

  Ry: {
    caption: "Ry(\u03C0/3): 60\u00B0 around Y-axis \u2014 creates real-valued superposition",
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "d1", gateType: "Ry", qubits: [0], params: [Math.PI / 3] }] },
      ],
    },
  },

  Rz: {
    caption: "Rz(\u03C0/2) on |+\u27E9: rotates phase along the equator",
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "d0", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "d1", gateType: "Rz", qubits: [0], params: [Math.PI / 2] }] },
      ],
    },
  },

  // ── Entangling gates: show entanglement creation ──

  CNOT: {
    caption: "CNOT: control in |+\u27E9 \u2192 Bell state \u2014 both dots collapse to center (entangled!)",
    circuit: {
      numQubits: 2,
      moments: [
        // Put control in superposition
        { gates: [{ id: "d0", gateType: "H", qubits: [0] }] },
        // CNOT creates entanglement — both qubits become maximally mixed
        { gates: [{ id: "d1", gateType: "CNOT", qubits: [0, 1] }] },
      ],
    },
  },

  CZ: {
    caption: "CZ: both in |+\u27E9 \u2192 phase entanglement (symmetric \u2014 no control/target!)",
    circuit: {
      numQubits: 2,
      moments: [
        // Both qubits in superposition
        { gates: [
          { id: "d0", gateType: "H", qubits: [0] },
          { id: "d0b", gateType: "H", qubits: [1] },
        ] },
        // CZ creates a cluster-like state — dots shift on the sphere
        { gates: [{ id: "d1", gateType: "CZ", qubits: [0, 1] }] },
      ],
    },
  },

  SWAP: {
    caption: "SWAP: q0 at south pole, q1 at equator \u2192 positions exchange",
    circuit: {
      numQubits: 2,
      moments: [
        // Put q0 and q1 in visually distinct states
        { gates: [
          { id: "d0", gateType: "X", qubits: [0] },      // q0 → |1⟩ (south pole)
          { id: "d0b", gateType: "H", qubits: [1] },      // q1 → |+⟩ (equator)
        ] },
        // SWAP — dots exchange positions
        { gates: [{ id: "d1", gateType: "SWAP", qubits: [0, 1] }] },
      ],
    },
  },

  Toffoli: {
    caption: "Toffoli: q2 flips ONLY when both q0 and q1 are |1\u27E9 \u2014 quantum AND",
    circuit: {
      numQubits: 3,
      moments: [
        // Set both controls to |1⟩
        { gates: [
          { id: "d0", gateType: "X", qubits: [0] },
          { id: "d0b", gateType: "X", qubits: [1] },
        ] },
        // Toffoli flips q2 — it moves from north to south pole
        { gates: [{ id: "d1", gateType: "Toffoli", qubits: [0, 1, 2] }] },
      ],
    },
  },
};
