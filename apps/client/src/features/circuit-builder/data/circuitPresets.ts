import type { CircuitPreset } from "../types";

export const CIRCUIT_PRESETS: CircuitPreset[] = [
  // ── Bell State (|Φ+⟩) ──
  {
    id: "bell",
    name: "Bell State",
    description: "Creates maximally entangled |Φ+⟩ = (|00⟩ + |11⟩)/√2. The simplest entangled state.",
    learns: "Entanglement, Hadamard gate, CNOT gate",
    steps: [
      "Hadamard on q0 creates equal superposition (|0⟩ + |1⟩)/√2 — the qubit is now on the equator of the Bloch sphere.",
      "CNOT entangles q0 and q1: if q0 is |1⟩, flip q1. The result (|00⟩ + |11⟩)/√2 cannot be written as a product — the qubits are now correlated.",
    ],
    applications: [
      "Foundation of quantum key distribution (QKD) protocols like BB84 and E91",
      "Quantum teleportation requires a shared Bell pair as a resource",
      "Superdense coding: send 2 classical bits using 1 qubit + shared Bell pair",
      "Bell inequality tests to rule out local hidden variable theories",
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
      ],
    },
  },

  // ── GHZ State (3-qubit) ──
  {
    id: "ghz3",
    name: "GHZ State (3Q)",
    description: "Greenberger-Horne-Zeilinger state: (|000⟩ + |111⟩)/√2. Maximally entangled 3-qubit state.",
    learns: "Multi-qubit entanglement, GHZ states",
    steps: [
      "Hadamard on q0 creates superposition — q0 is now in |+⟩ while q1, q2 remain |0⟩.",
      "CNOT q0→q1 spreads the superposition: state is now (|00⟩ + |11⟩)|0⟩ on q0-q1, with q2 still |0⟩.",
      "CNOT q0→q2 extends entanglement to all three qubits: (|000⟩ + |111⟩)/√2. All qubits are maximally entangled.",
    ],
    applications: [
      "Quantum metrology: GHZ states achieve Heisenberg-limited precision in phase estimation",
      "Quantum secret sharing: information is split so no single party can reconstruct it alone",
      "Testing quantum mechanics: GHZ paradox provides an all-or-nothing test of local realism",
    ],
    circuit: {
      numQubits: 3,
      moments: [
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "p3", gateType: "CNOT", qubits: [0, 2] }] },
      ],
    },
  },

  // ── Quantum Teleportation ──
  {
    id: "teleportation",
    name: "Quantum Teleportation",
    description: "Teleports the state of q0 to q2 using a Bell pair (q1, q2) as a channel. The canonical quantum communication protocol.",
    learns: "Teleportation protocol, Bell measurement, classical correction",
    steps: [
      "Prepare the state to teleport: H on q0 puts it in |+⟩.",
      "Create the Bell channel: H on q1 followed by CNOT q1→q2 creates a shared entangled pair between q1 and q2.",
      "CNOT q1→q2 completes the Bell pair — q1 and q2 are now in (|00⟩ + |11⟩)/√2.",
      "Begin Bell measurement: CNOT q0→q1 entangles the message qubit with the channel.",
      "H on q0 completes the Bell measurement — q0 and q1 are now in a Bell basis state.",
      "Classical correction: CNOT q1→q2 applies X correction based on q1's measurement outcome.",
      "CZ q0→q2 applies Z correction based on q0's measurement outcome. q2 now holds the original state of q0.",
    ],
    applications: [
      "Quantum internet: transferring quantum states between distant nodes",
      "Quantum computing: moving qubits between non-adjacent positions in a processor",
      "Quantum repeaters: extending entanglement over long distances by chaining teleportation",
    ],
    circuit: {
      numQubits: 3,
      moments: [
        // Prepare state to teleport: put q0 in |+⟩
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        // Create Bell pair between q1 and q2
        { gates: [{ id: "p2", gateType: "H", qubits: [1] }] },
        { gates: [{ id: "p3", gateType: "CNOT", qubits: [1, 2] }] },
        // Bell measurement on q0, q1
        { gates: [{ id: "p4", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "p5", gateType: "H", qubits: [0] }] },
        // Classical corrections (represented as conditional gates)
        { gates: [{ id: "p6", gateType: "CNOT", qubits: [1, 2] }] },
        { gates: [{ id: "p7", gateType: "CZ", qubits: [0, 2] }] },
      ],
    },
  },

  // ── Quantum Fourier Transform (2-qubit) ──
  {
    id: "qft2",
    name: "QFT (2-qubit)",
    description: "2-qubit Quantum Fourier Transform. Converts computational basis to frequency basis. Building block of Shor's algorithm.",
    learns: "QFT, phase gates, SWAP",
    steps: [
      "H on q0 creates superposition of the most significant bit — the first step of the butterfly pattern.",
      "CZ between q0 and q1 applies a controlled phase rotation, encoding frequency information between the qubits.",
      "H on q1 completes the Fourier transform on the second qubit.",
      "SWAP reverses the bit order — QFT outputs are in reversed order, so this corrects the qubit labeling.",
    ],
    applications: [
      "Shor's algorithm: QFT extracts the period of modular exponentiation for integer factoring",
      "Quantum phase estimation: reads out eigenphases encoded in a quantum register",
      "Quantum simulation: efficient basis transforms for Hamiltonian simulation",
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "CZ", qubits: [0, 1] }] },
        { gates: [{ id: "p3", gateType: "H", qubits: [1] }] },
        { gates: [{ id: "p4", gateType: "SWAP", qubits: [0, 1] }] },
      ],
    },
  },

  // ── Superdense Coding ──
  {
    id: "superdense",
    name: "Superdense Coding",
    description: "Sends 2 classical bits using 1 qubit by pre-sharing a Bell pair. Alice applies X to encode '10'.",
    learns: "Superdense coding, Bell basis, entanglement as a resource",
    steps: [
      "Create shared Bell pair: H on q0 puts it in superposition.",
      "CNOT q0→q1 completes the Bell pair. Alice holds q0, Bob holds q1.",
      "Alice encodes her message '10' by applying X to her qubit. Different messages use I (00), X (10), Z (01), or XZ (11).",
      "Bob decodes: CNOT q0→q1 undoes the entanglement conditional on Alice's encoding.",
      "H on q0 completes the decoding. Measuring both qubits now reveals Alice's 2-bit message.",
    ],
    applications: [
      "Quantum communication: doubles the classical capacity of a quantum channel",
      "Demonstrates entanglement as a physical resource that can be consumed",
      "Foundation for quantum dense coding in quantum networks",
    ],
    circuit: {
      numQubits: 2,
      moments: [
        // Create shared Bell pair
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
        // Alice encodes message '10' with X gate
        { gates: [{ id: "p3", gateType: "X", qubits: [0] }] },
        // Bob decodes
        { gates: [{ id: "p4", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "p5", gateType: "H", qubits: [0] }] },
      ],
    },
  },

  // ── W State (3-qubit) ──
  {
    id: "w_state",
    name: "W State (3Q)",
    description: "W state: (|001⟩ + |010⟩ + |100⟩)/√3. Unlike GHZ, tracing out one qubit preserves entanglement.",
    learns: "W states, robustness of entanglement, Ry rotations",
    circuit: {
      numQubits: 3,
      moments: [
        // Ry(arccos(1/√3)) on q0 to get amplitude √(1/3)
        { gates: [{ id: "p1", gateType: "Ry", qubits: [0], params: [Math.acos(1 / Math.sqrt(3)) * 2] }] },
        // Controlled rotation + CNOT cascade
        { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "p3", gateType: "Ry", qubits: [1], params: [Math.PI / 2] }] },
        { gates: [{ id: "p4", gateType: "CNOT", qubits: [1, 2] }] },
        // Fix phases
        { gates: [{ id: "p5", gateType: "X", qubits: [0] }] },
        { gates: [{ id: "p6", gateType: "X", qubits: [1] }] },
      ],
    },
  },

  // ── Deutsch-Jozsa (2-qubit, balanced oracle) ──
  {
    id: "deutsch_jozsa",
    name: "Deutsch-Jozsa",
    description: "Determines if a function is constant or balanced in one query. Uses a balanced oracle (CNOT). Result: |1⟩ means balanced.",
    learns: "Quantum advantage, oracles, interference",
    steps: [
      "X on q1 prepares the ancilla in |1⟩ — this is the phase kickback target.",
      "H on both qubits creates equal superposition. q0 queries all inputs simultaneously; q1 in |−⟩ enables phase kickback.",
      "Oracle (CNOT): the balanced function f(x) = x flips the phase of |1⟩ via kickback. This marks the input without measuring.",
      "H on q0 interferes the marked and unmarked paths. If f is balanced, constructive interference yields |1⟩; if constant, |0⟩.",
    ],
    applications: [
      "First proof that quantum computers can solve certain problems exponentially faster than classical",
      "Teaches the concept of quantum parallelism and interference-based computation",
      "Template for oracle-based quantum algorithms (Grover, Simon, Shor)",
    ],
    circuit: {
      numQubits: 2,
      moments: [
        // Prepare |01⟩ then Hadamard both
        { gates: [{ id: "p1", gateType: "X", qubits: [1] }] },
        { gates: [
          { id: "p2", gateType: "H", qubits: [0] },
          { id: "p3", gateType: "H", qubits: [1] },
        ] },
        // Oracle (balanced): CNOT
        { gates: [{ id: "p4", gateType: "CNOT", qubits: [0, 1] }] },
        // Hadamard on input qubit and measure
        { gates: [{ id: "p5", gateType: "H", qubits: [0] }] },
      ],
    },
  },

  // ── Grover's Search (2-qubit, target |11⟩) ──
  {
    id: "grover2",
    name: "Grover's Search (2Q)",
    description: "Searches for |11⟩ among 4 states in 1 iteration. Demonstrates quadratic speedup.",
    learns: "Grover's algorithm, oracle, diffusion operator",
    steps: [
      "H on both qubits creates uniform superposition over all 4 basis states — each has amplitude 1/2.",
      "Oracle (CZ): marks the target |11⟩ by flipping its phase to −1/2. All other amplitudes stay at +1/2.",
      "Diffusion step begins: H gates transform back to computational basis for the inversion-about-mean operation.",
      "X gates flip all qubits — this maps |00⟩ ↔ |11⟩, setting up the conditional phase flip.",
      "CZ applies a phase flip to |11⟩ (which was |00⟩ before the X gates) — completing the reflection about the mean.",
      "X gates undo the flip, restoring the original labeling.",
      "Final H gates complete the diffusion operator. The target |11⟩ now has amplitude 1 (certainty), all others have amplitude 0.",
    ],
    applications: [
      "Unstructured database search with quadratic speedup: O(√N) vs O(N)",
      "Amplitude amplification: general technique used as subroutine in many quantum algorithms",
      "Optimization: quantum approximate optimization (QAOA) builds on Grover-like ideas",
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [
          { id: "p1", gateType: "H", qubits: [0] },
          { id: "p2", gateType: "H", qubits: [1] },
        ] },
        { gates: [{ id: "p3", gateType: "CZ", qubits: [0, 1] }] },
        { gates: [
          { id: "p4", gateType: "H", qubits: [0] },
          { id: "p5", gateType: "H", qubits: [1] },
        ] },
        { gates: [
          { id: "p6", gateType: "X", qubits: [0] },
          { id: "p7", gateType: "X", qubits: [1] },
        ] },
        { gates: [{ id: "p8", gateType: "CZ", qubits: [0, 1] }] },
        { gates: [
          { id: "p9", gateType: "X", qubits: [0] },
          { id: "p10", gateType: "X", qubits: [1] },
        ] },
        { gates: [
          { id: "p11", gateType: "H", qubits: [0] },
          { id: "p12", gateType: "H", qubits: [1] },
        ] },
      ],
    },
  },

  // ═══════════════════════════════════════════════════════════════
  // EXOTIC STATES
  // ═══════════════════════════════════════════════════════════════

  // ── All four Bell states ──
  {
    id: "bell_psi_minus",
    name: "Bell |Ψ\u207B\u27E9",
    description: "The singlet state (|01⟩ \u2212 |10⟩)/\u221A2. Anti-correlated Bell pair used in entanglement swapping and quantum key distribution.",
    learns: "Bell state variants, singlet state, anti-correlation",
    steps: [
      "X on q0 flips it to |1⟩ — starting from |10⟩ instead of |00⟩ selects a different Bell state.",
      "H on q0 creates (|0⟩ − |1⟩)/√2 — note the minus sign from applying H to |1⟩.",
      "CNOT q0→q1 entangles: the result is (|01⟩ − |10⟩)/√2. Measuring one qubit always gives the opposite of the other.",
    ],
    applications: [
      "E91 quantum key distribution protocol uses singlet correlations for provably secure communication",
      "Entanglement swapping in quantum repeaters",
      "The singlet is rotationally invariant — it looks the same in any measurement basis",
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "p1", gateType: "X", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p3", gateType: "CNOT", qubits: [0, 1] }] },
      ],
    },
  },

  // ── 4-qubit GHZ ──
  {
    id: "ghz4",
    name: "GHZ State (4Q)",
    description: "(|0000⟩ + |1111⟩)/\u221A2. Four-qubit cat state used in quantum metrology and multi-party entanglement experiments.",
    learns: "Scaling entanglement, fragility of GHZ states",
    circuit: {
      numQubits: 4,
      moments: [
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "p3", gateType: "CNOT", qubits: [0, 2] }] },
        { gates: [{ id: "p4", gateType: "CNOT", qubits: [0, 3] }] },
      ],
    },
  },

  // ── Linear Cluster State (4-qubit) ──
  {
    id: "cluster4",
    name: "Cluster State (4Q)",
    description: "Linear 4-qubit cluster state. Resource state for measurement-based quantum computing (MBQC). Created by CZ gates on a chain of |+⟩ states.",
    learns: "Cluster states, MBQC, graph states, CZ entanglement",
    steps: [
      "H on all 4 qubits puts each in |+⟩ — the starting point for any graph state.",
      "CZ on q0-q1 creates a controlled-phase bond. Unlike CNOT, CZ is symmetric — neither qubit is 'control' or 'target'.",
      "CZ on q1-q2 extends the chain. The entanglement structure now mirrors a linear graph.",
      "CZ on q2-q3 completes the 4-qubit linear cluster. Each qubit is entangled with its neighbors but not directly with distant qubits.",
    ],
    applications: [
      "Measurement-based quantum computing (one-way QC): computation by measuring qubits in sequence",
      "Topological quantum error correction uses 2D cluster states as surface codes",
      "Photonic quantum computing platforms naturally create cluster states",
    ],
    circuit: {
      numQubits: 4,
      moments: [
        { gates: [
          { id: "p1", gateType: "H", qubits: [0] },
          { id: "p2", gateType: "H", qubits: [1] },
          { id: "p3", gateType: "H", qubits: [2] },
          { id: "p4", gateType: "H", qubits: [3] },
        ] },
        { gates: [{ id: "p5", gateType: "CZ", qubits: [0, 1] }] },
        { gates: [{ id: "p6", gateType: "CZ", qubits: [1, 2] }] },
        { gates: [{ id: "p7", gateType: "CZ", qubits: [2, 3] }] },
      ],
    },
  },

  // ── Entanglement Swapping ──
  {
    id: "entanglement_swapping",
    name: "Entanglement Swapping",
    description: "Creates entanglement between q0 and q3 that never directly interacted. Two Bell pairs (q0-q1, q2-q3) are connected via Bell measurement on q1-q2. Foundation of quantum repeaters.",
    learns: "Entanglement swapping, quantum repeaters, non-local correlations",
    steps: [
      "H on q0 and q2 simultaneously begins creating two independent Bell pairs.",
      "CNOT q0→q1 and CNOT q2→q3 complete both Bell pairs. q0-q1 are entangled, q2-q3 are entangled, but the pairs are independent.",
      "CNOT q1→q2 begins the Bell measurement on the 'middle' qubits — entangling the two previously separate pairs.",
      "H on q1 completes the Bell measurement. The outcome of measuring q1-q2 determines corrections needed.",
      "CNOT q2→q3 applies X correction to q3 based on q2's state.",
      "CZ q1→q3 applies Z correction. q0 and q3 are now entangled despite never having interacted directly.",
    ],
    applications: [
      "Quantum repeaters: extend entanglement across continental distances by chaining swaps",
      "Quantum internet architecture: nodes share entanglement via intermediate stations",
      "Demonstrated in numerous photonic experiments confirming non-local entanglement creation",
    ],
    circuit: {
      numQubits: 4,
      moments: [
        // Bell pair 1: q0-q1
        { gates: [
          { id: "p1", gateType: "H", qubits: [0] },
          { id: "p2", gateType: "H", qubits: [2] },
        ] },
        { gates: [
          { id: "p3", gateType: "CNOT", qubits: [0, 1] },
          { id: "p4", gateType: "CNOT", qubits: [2, 3] },
        ] },
        // Bell measurement on q1-q2
        { gates: [{ id: "p5", gateType: "CNOT", qubits: [1, 2] }] },
        { gates: [{ id: "p6", gateType: "H", qubits: [1] }] },
        // Classical corrections
        { gates: [{ id: "p7", gateType: "CNOT", qubits: [2, 3] }] },
        { gates: [{ id: "p8", gateType: "CZ", qubits: [1, 3] }] },
      ],
    },
  },

  // ═══════════════════════════════════════════════════════════════
  // REAL HARDWARE EXPERIMENTS
  // ═══════════════════════════════════════════════════════════════

  // ── Quantum Phase Estimation (2+1 qubits) ──
  {
    id: "qpe_t_gate",
    name: "Phase Estimation (T gate)",
    description: "Estimates the eigenphase of a T gate (\u03C0/4). Uses 2 counting qubits to read out the phase. Core subroutine of Shor's algorithm.",
    learns: "QPE, controlled rotations, inverse QFT, eigenvalues",
    circuit: {
      numQubits: 3,
      moments: [
        // Eigenstate: |1⟩ on target qubit
        { gates: [{ id: "p1", gateType: "X", qubits: [2] }] },
        // Hadamard on counting qubits
        { gates: [
          { id: "p2", gateType: "H", qubits: [0] },
          { id: "p3", gateType: "H", qubits: [1] },
        ] },
        // Controlled-T on q1→q2 (one application)
        { gates: [{ id: "p4", gateType: "CZ", qubits: [1, 2] }] },
        // Controlled-T² on q0→q2 (two applications ≈ controlled-S)
        { gates: [{ id: "p5", gateType: "CZ", qubits: [0, 2] }] },
        { gates: [{ id: "p6", gateType: "CZ", qubits: [0, 2] }] },
        // Inverse QFT on counting register
        { gates: [{ id: "p7", gateType: "SWAP", qubits: [0, 1] }] },
        { gates: [{ id: "p8", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p9", gateType: "CZ", qubits: [0, 1] }] },
        { gates: [{ id: "p10", gateType: "H", qubits: [1] }] },
      ],
    },
  },

  // ── Bernstein-Vazirani (3-qubit, secret = 101) ──
  {
    id: "bernstein_vazirani",
    name: "Bernstein-Vazirani (s=101)",
    description: "Finds the secret string s=101 in one query. Generalization of Deutsch-Jozsa. Regularly demonstrated on IBM Quantum hardware.",
    learns: "BV algorithm, inner-product oracle, single-query advantage",
    circuit: {
      numQubits: 4,
      moments: [
        // Ancilla in |1⟩
        { gates: [{ id: "p1", gateType: "X", qubits: [3] }] },
        // Hadamard all
        { gates: [
          { id: "p2", gateType: "H", qubits: [0] },
          { id: "p3", gateType: "H", qubits: [1] },
          { id: "p4", gateType: "H", qubits: [2] },
          { id: "p5", gateType: "H", qubits: [3] },
        ] },
        // Oracle for s=101: CNOT from bit positions where s_i=1
        { gates: [{ id: "p6", gateType: "CNOT", qubits: [0, 3] }] },
        { gates: [{ id: "p7", gateType: "CNOT", qubits: [2, 3] }] },
        // Hadamard input register
        { gates: [
          { id: "p8", gateType: "H", qubits: [0] },
          { id: "p9", gateType: "H", qubits: [1] },
          { id: "p10", gateType: "H", qubits: [2] },
        ] },
      ],
    },
  },

  // ── Quantum Error Detection (bit-flip code) ──
  {
    id: "bit_flip_code",
    name: "Bit-Flip Code",
    description: "Encodes 1 logical qubit into 3 physical qubits. Detects and corrects single bit-flip (X) errors. The simplest quantum error correction code.",
    learns: "QEC, encoding, syndrome measurement, error correction",
    steps: [
      "H on q0 prepares the logical state |+⟩ — we'll encode and protect this superposition.",
      "CNOT q0→q1 copies the logical state: |+⟩|0⟩ becomes (|00⟩ + |11⟩)/√2.",
      "CNOT q0→q2 completes the encoding: logical |+⟩ is now spread across 3 qubits as (|000⟩ + |111⟩)/√2.",
      "X on q1 simulates a bit-flip error on the second qubit — this is the 'noise' we want to correct.",
      "CNOT q0→q1 extracts syndrome: compares q0 with q1 to detect if they differ.",
      "CNOT q0→q2 extracts second syndrome bit: compares q0 with q2.",
      "Toffoli (q1, q2 → q0) corrects the error: if both syndromes flag q0 as the odd one out, flip it back.",
    ],
    applications: [
      "Foundation of all quantum error correction — the simplest code that corrects 1 error",
      "Demonstrated on IBM Quantum, Google Sycamore, and trapped-ion processors",
      "Stepping stone to surface codes and fault-tolerant quantum computing",
    ],
    circuit: {
      numQubits: 3,
      moments: [
        // Prepare |+⟩ as logical state
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        // Encode: spread to 3 qubits
        { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "p3", gateType: "CNOT", qubits: [0, 2] }] },
        // Simulate error on qubit 1
        { gates: [{ id: "p4", gateType: "X", qubits: [1] }] },
        // Syndrome extraction + correction
        { gates: [{ id: "p5", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "p6", gateType: "CNOT", qubits: [0, 2] }] },
        { gates: [{ id: "p7", gateType: "Toffoli", qubits: [1, 2, 0] }] },
      ],
    },
  },

  // ── CHSH Inequality Test ──
  {
    id: "chsh",
    name: "CHSH Inequality",
    description: "Prepares the state and measurement settings that maximally violate the CHSH Bell inequality (S = 2\u221A2). Run on IBM Quantum to demonstrate non-locality.",
    learns: "Bell inequality, CHSH, non-locality, measurement bases",
    steps: [
      "H on q0 begins Bell pair creation.",
      "CNOT q0→q1 creates |Φ+⟩ = (|00⟩ + |11⟩)/√2 — the maximally entangled resource state.",
      "Ry(π/4) on q0 rotates Alice's measurement basis by 22.5° — the optimal CHSH angle.",
      "Ry(π/8) on q1 rotates Bob's measurement basis by 11.25° — together with Alice's rotation, this maximizes the CHSH correlator.",
    ],
    applications: [
      "Experimental tests of Bell's theorem — performed by Aspect (1982), awarded Nobel Prize 2022",
      "Device-independent quantum key distribution relies on CHSH violation as a security guarantee",
      "Certifying genuine quantum computation in verification protocols",
    ],
    circuit: {
      numQubits: 2,
      moments: [
        // Create Bell pair
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
        // Rotate to optimal CHSH measurement basis
        // Alice: measure in \u03C0/4 rotated basis
        { gates: [{ id: "p3", gateType: "Ry", qubits: [0], params: [Math.PI / 4] }] },
        // Bob: measure in \u03C0/8 rotated basis
        { gates: [{ id: "p4", gateType: "Ry", qubits: [1], params: [Math.PI / 8] }] },
      ],
    },
  },

  // ── Quantum Random Walk (4 steps) ──
  {
    id: "quantum_walk",
    name: "Quantum Random Walk",
    description: "4-step discrete quantum walk on a line. Uses a coin qubit (q0) and 3 position qubits. Demonstrates quadratic speedup over classical random walks.",
    learns: "Quantum walks, interference in position space, coin operator",
    circuit: {
      numQubits: 4,
      moments: [
        // Initial position: |0001⟩ (start at position 1)
        { gates: [{ id: "p1", gateType: "X", qubits: [3] }] },
        // Step 1: coin flip + conditional shift
        { gates: [{ id: "p2", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p3", gateType: "CNOT", qubits: [0, 1] }] },
        // Step 2
        { gates: [{ id: "p4", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p5", gateType: "CNOT", qubits: [0, 2] }] },
        // Step 3
        { gates: [{ id: "p6", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p7", gateType: "CNOT", qubits: [0, 3] }] },
        // Step 4
        { gates: [{ id: "p8", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p9", gateType: "CNOT", qubits: [0, 1] }] },
      ],
    },
  },

  // ── Toffoli Decomposition ──
  {
    id: "toffoli_decomposed",
    name: "Toffoli Gate",
    description: "The Toffoli (CCX) gate: flips q2 only when both q0 and q1 are |1⟩. Fundamental for reversible and quantum computing. Prepare |110⟩ to see it flip the target.",
    learns: "Toffoli gate, reversible computing, controlled-controlled operations",
    circuit: {
      numQubits: 3,
      moments: [
        // Prepare |110⟩
        { gates: [
          { id: "p1", gateType: "X", qubits: [0] },
          { id: "p2", gateType: "X", qubits: [1] },
        ] },
        // Apply Toffoli
        { gates: [{ id: "p3", gateType: "Toffoli", qubits: [0, 1, 2] }] },
      ],
    },
  },

  // ── Quantum Adder (half adder) ──
  {
    id: "quantum_half_adder",
    name: "Quantum Half Adder",
    description: "Adds two single-bit numbers (q0 + q1) into sum (q2) and carry (q3) using Toffoli and CNOT. Demonstrates reversible arithmetic.",
    learns: "Quantum arithmetic, reversible logic, carry propagation",
    circuit: {
      numQubits: 4,
      moments: [
        // Input: 1 + 1 (set both inputs to |1⟩)
        { gates: [
          { id: "p1", gateType: "X", qubits: [0] },
          { id: "p2", gateType: "X", qubits: [1] },
        ] },
        // Carry = q0 AND q1 (Toffoli)
        { gates: [{ id: "p3", gateType: "Toffoli", qubits: [0, 1, 3] }] },
        // Sum = q0 XOR q1 (CNOT)
        { gates: [{ id: "p4", gateType: "CNOT", qubits: [0, 2] }] },
        { gates: [{ id: "p5", gateType: "CNOT", qubits: [1, 2] }] },
      ],
    },
  },

  // ── Hardy's Paradox State ──
  {
    id: "hardy",
    name: "Hardy's Paradox",
    description: "Prepares Hardy's non-maximally entangled state that violates local realism without inequalities. Demonstrated experimentally in photonic and superconducting systems.",
    learns: "Hardy's paradox, non-maximally entangled states, foundations of QM",
    circuit: {
      numQubits: 2,
      moments: [
        // Ry to create non-maximal superposition
        { gates: [{ id: "p1", gateType: "Ry", qubits: [0], params: [2 * Math.atan(1 / Math.sqrt(Math.sqrt(5)))] }] },
        { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
        // Partial rotation on q1 conditional on entanglement
        { gates: [{ id: "p3", gateType: "Ry", qubits: [1], params: [Math.PI / 3] }] },
        { gates: [{ id: "p4", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "p5", gateType: "Ry", qubits: [0], params: [-Math.PI / 6] }] },
      ],
    },
  },

  // ── QFT 3-qubit ──
  {
    id: "qft3",
    name: "QFT (3-qubit)",
    description: "3-qubit Quantum Fourier Transform. Used in Shor's algorithm for period-finding. Maps computational basis to phase-encoded frequency basis.",
    learns: "QFT at scale, controlled phase gates, bit reversal",
    circuit: {
      numQubits: 3,
      moments: [
        // Prepare an interesting input state |101⟩
        { gates: [
          { id: "p1", gateType: "X", qubits: [0] },
          { id: "p2", gateType: "X", qubits: [2] },
        ] },
        // QFT
        { gates: [{ id: "p3", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p4", gateType: "CZ", qubits: [0, 1] }] },
        { gates: [{ id: "p5", gateType: "CZ", qubits: [0, 2] }] },
        { gates: [{ id: "p6", gateType: "H", qubits: [1] }] },
        { gates: [{ id: "p7", gateType: "CZ", qubits: [1, 2] }] },
        { gates: [{ id: "p8", gateType: "H", qubits: [2] }] },
        // Bit reversal
        { gates: [{ id: "p9", gateType: "SWAP", qubits: [0, 2] }] },
      ],
    },
  },

  // ── Quantum State Tomography Prep (6 Pauli eigenstates) ──
  {
    id: "tomo_prep",
    name: "Tomography Basis States",
    description: "Prepares |+i⟩ = (|0⟩ + i|1⟩)/\u221A2 on q0 using S\u00B7H. Used as calibration state in quantum state tomography on real hardware.",
    learns: "State tomography, Pauli Y eigenstate, S gate phase",
    circuit: {
      numQubits: 1,
      moments: [
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "S", qubits: [0] }] },
      ],
    },
  },

  // ── Randomized Benchmarking Sequence ──
  {
    id: "rb_sequence",
    name: "Clifford RB Sequence",
    description: "A short Clifford randomized benchmarking sequence. In real experiments, random Clifford sequences of increasing length measure gate fidelity. This 6-gate sequence should return to |0⟩.",
    learns: "Randomized benchmarking, Clifford group, gate fidelity",
    circuit: {
      numQubits: 1,
      moments: [
        { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p2", gateType: "S", qubits: [0] }] },
        { gates: [{ id: "p3", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p4", gateType: "S", qubits: [0] }] },
        { gates: [{ id: "p5", gateType: "S", qubits: [0] }] },
        // Inversion: undo the sequence
        { gates: [{ id: "p6", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "p7", gateType: "S", qubits: [0] }] },
        { gates: [{ id: "p8", gateType: "H", qubits: [0] }] },
      ],
    },
  },

  // ── Swap Test ──
  {
    id: "swap_test",
    name: "SWAP Test",
    description: "Measures the overlap |⟨\u03C8|\u03C6\u27E9|\u00B2 between two states without tomography. Ancilla q0 reads 0 with probability (1+|\u27E8\u03C8|\u03C6\u27E9|\u00B2)/2. Used in quantum ML.",
    learns: "SWAP test, state comparison, quantum fingerprinting",
    circuit: {
      numQubits: 3,
      moments: [
        // Prepare two states to compare: q1=|+⟩, q2=|0⟩
        { gates: [{ id: "p1", gateType: "H", qubits: [1] }] },
        // SWAP test circuit
        { gates: [{ id: "p2", gateType: "H", qubits: [0] }] },
        // Controlled-SWAP (Fredkin) = CNOT cascade approximation
        { gates: [{ id: "p3", gateType: "CNOT", qubits: [2, 1] }] },
        { gates: [{ id: "p4", gateType: "Toffoli", qubits: [0, 1, 2] }] },
        { gates: [{ id: "p5", gateType: "CNOT", qubits: [2, 1] }] },
        { gates: [{ id: "p6", gateType: "H", qubits: [0] }] },
      ],
    },
  },
];
