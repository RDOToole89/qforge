/**
 * Interactive Learn Mode — Lesson Content
 *
 * 4 modules, 18 lessons, progressive difficulty.
 * Each lesson has a demo circuit, explanatory content, and things to watch for
 * on the Bloch sphere during playback.
 */
import type { Circuit } from "../types";

export interface LessonSection {
  type: "text" | "insight" | "watch" | "formula";
  content: string;
}

export interface Lesson {
  id: string;
  module: number;
  order: number;
  title: string;
  subtitle: string;
  content: LessonSection[];
  circuit: Circuit;
  interpMode?: "direct" | "ideal";
  glossaryLinks: string[];
  prerequisites: string[];
}

export interface LessonModule {
  id: number;
  title: string;
  icon: string;
  description: string;
  prerequisiteModules: number[];
}

export const MODULES: LessonModule[] = [
  { id: 1, title: "The Bloch Sphere", icon: "\uD83C\uDF10", description: "Understand how qubits are represented as points on a sphere", prerequisiteModules: [] },
  { id: 2, title: "Single-Qubit Gates", icon: "\uD83D\uDD04", description: "Master the rotations that transform individual qubits", prerequisiteModules: [1] },
  { id: 3, title: "Entanglement", icon: "\uD83D\uDD17", description: "Discover how multi-qubit gates create quantum correlations", prerequisiteModules: [1, 2] },
  { id: 4, title: "Quantum Algorithms", icon: "\uD83D\uDE80", description: "See how gates combine into algorithms that outperform classical computers", prerequisiteModules: [1, 2, 3] },
];

export const LESSONS: Lesson[] = [
  // ═══════════════════════════════════════════════════════════════
  // MODULE 1: THE BLOCH SPHERE
  // ═══════════════════════════════════════════════════════════════

  {
    id: "1-1-qubit",
    module: 1,
    order: 1,
    title: "What is a Qubit?",
    subtitle: "The quantum bit lives on a sphere",
    content: [
      { type: "text", content: "A classical bit is either 0 or 1. A qubit can be both at the same time \u2014 this is called superposition." },
      { type: "text", content: "We visualize a qubit's state as a point on the Bloch sphere. The north pole is |0\u27E9 (measuring gives 0 with certainty), and the south pole is |1\u27E9 (measuring gives 1 with certainty)." },
      { type: "watch", content: "Both qubits start at the north pole (|0\u27E9). The X gate on q0 flips it to the south pole (|1\u27E9). Watch how the dot travels from top to bottom." },
      { type: "insight", content: "Any point on the sphere's surface represents a valid qubit state. The closer to the north pole, the more likely you are to measure 0. The closer to the south pole, the more likely to measure 1." },
      { type: "text", content: "Points on the equator represent equal superposition \u2014 50/50 chance of measuring 0 or 1. But different points on the equator differ in their phase, which affects how the qubit interacts with other gates." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "X", qubits: [0] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["qubit", "bloch_sphere", "pure_state"],
    prerequisites: [],
  },

  {
    id: "1-2-superposition",
    module: 1,
    order: 2,
    title: "Superposition",
    subtitle: "Being in two states at once",
    content: [
      { type: "text", content: "The Hadamard gate (H) is the most important single-qubit gate. It takes |0\u27E9 to |+\u27E9 = (|0\u27E9 + |1\u27E9)/\u221A2 \u2014 an equal superposition." },
      { type: "watch", content: "Watch q0 move from the north pole to the equator when H is applied. q1 stays at the north pole for reference." },
      { type: "formula", content: "H|0\u27E9 = (|0\u27E9 + |1\u27E9)/\u221A2 = |+\u27E9" },
      { type: "insight", content: "On the equator, the qubit is in equal superposition \u2014 50% chance of measuring 0, 50% chance of measuring 1. But the state is NOT random \u2014 it's a precise quantum state that can be reversed by applying H again." },
      { type: "text", content: "This is the key difference from classical randomness: a coin flip is irreversible, but superposition is a precise, controllable state." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["superposition", "hadamard", "born_rule"],
    prerequisites: ["1-1-qubit"],
  },

  {
    id: "1-3-phase",
    module: 1,
    order: 3,
    title: "Phase",
    subtitle: "The invisible quantum property",
    content: [
      { type: "text", content: "Phase is the most subtle and important concept in quantum computing. Two states can have identical measurement probabilities but different phases \u2014 and this difference is what makes quantum algorithms work." },
      { type: "watch", content: "First, H puts q0 on the equator (|+\u27E9). Then S rotates it 90\u00B0 around the Z-axis to |+i\u27E9. The dot moves ALONG the equator \u2014 same probabilities, different phase." },
      { type: "formula", content: "S|+\u27E9 = (|0\u27E9 + i|1\u27E9)/\u221A2 = |+i\u27E9" },
      { type: "insight", content: "Phase is invisible if you only measure in the Z-basis (computational basis). But it becomes visible when you apply another gate first. This is why phase matters \u2014 it determines interference outcomes in quantum algorithms." },
      { type: "text", content: "Think of phase as the 'direction' of the superposition on the equator. |+\u27E9 points toward +X, |\u2212\u27E9 points toward \u2212X, and |+i\u27E9 points toward +Y. All have 50/50 measurement probabilities, but they're physically different states." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "S", qubits: [0] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["bloch_vector", "pauli_z", "contractivity"],
    prerequisites: ["1-2-superposition"],
  },

  // ═══════════════════════════════════════════════════════════════
  // MODULE 2: SINGLE-QUBIT GATES
  // ═══════════════════════════════════════════════════════════════

  {
    id: "2-1-x-gate",
    module: 2,
    order: 1,
    title: "X Gate (Quantum NOT)",
    subtitle: "\u03C0 rotation around the X-axis",
    content: [
      { type: "text", content: "The Pauli-X gate is the quantum version of the classical NOT gate. It flips |0\u27E9 to |1\u27E9 and vice versa. On the Bloch sphere, it's a 180\u00B0 rotation around the X-axis." },
      { type: "watch", content: "q0 starts in a tilted state (from Ry rotation), then X flips it across the equator. Notice how both the 'up' and 'down' components are swapped." },
      { type: "formula", content: "X = [[0, 1], [1, 0]]  \u2014  X|0\u27E9 = |1\u27E9,  X|1\u27E9 = |0\u27E9" },
      { type: "insight", content: "Unlike a classical NOT, X also works on superpositions: X(a|0\u27E9 + b|1\u27E9) = b|0\u27E9 + a|1\u27E9. It swaps the amplitudes without destroying the superposition." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "Ry", qubits: [0], params: [Math.PI / 3] }] },
        { gates: [{ id: "l2", gateType: "X", qubits: [0] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["pauli_x", "bit_flip"],
    prerequisites: ["1-1-qubit"],
  },

  {
    id: "2-2-z-gate",
    module: 2,
    order: 2,
    title: "Z Gate (Phase Flip)",
    subtitle: "The invisible gate that changes everything",
    content: [
      { type: "text", content: "The Z gate adds a minus sign to the |1\u27E9 component: Z|1\u27E9 = \u2212|1\u27E9. On the Bloch sphere, it's a 180\u00B0 rotation around the Z-axis." },
      { type: "watch", content: "First H creates |+\u27E9 (equator). Then Z flips it to |\u2212\u27E9. The dot jumps to the opposite side of the equator. The measurement probabilities are IDENTICAL \u2014 still 50/50!" },
      { type: "formula", content: "Z|+\u27E9 = Z(|0\u27E9 + |1\u27E9)/\u221A2 = (|0\u27E9 \u2212 |1\u27E9)/\u221A2 = |\u2212\u27E9" },
      { type: "insight", content: "If you applied Z to |0\u27E9 directly, NOTHING visible would happen \u2014 the dot wouldn't move. Phase gates only have visible effects on superposition states. This is the deepest idea in quantum computing: invisible transformations that become visible through interference." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "Z", qubits: [0] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["pauli_z", "phase_flip"],
    prerequisites: ["1-3-phase"],
  },

  {
    id: "2-3-hadamard",
    module: 2,
    order: 3,
    title: "Hadamard Deep Dive",
    subtitle: "The bridge between Z and X",
    content: [
      { type: "text", content: "Hadamard is special because it converts between the Z-basis (|0\u27E9, |1\u27E9) and the X-basis (|+\u27E9, |\u2212\u27E9). It's also its own inverse: applying H twice returns to the original state." },
      { type: "watch", content: "Watch q0: H takes it from |0\u27E9 to |+\u27E9 (north pole to equator). Then H again takes it back to |0\u27E9 (equator to north pole). The round trip is exact." },
      { type: "formula", content: "H\u00B2 = I  \u2014  applying Hadamard twice gives the identity" },
      { type: "insight", content: "This is why H appears at both the beginning AND end of most quantum algorithms. The first H creates superposition (exploring all possibilities). The final H converts phase differences into probability differences that we can measure. This is quantum interference." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "H", qubits: [0] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["hadamard", "superposition", "interference"],
    prerequisites: ["1-2-superposition"],
  },

  {
    id: "2-4-s-t-gates",
    module: 2,
    order: 4,
    title: "S and T Gates",
    subtitle: "Fractional phase rotations",
    content: [
      { type: "text", content: "S adds 90\u00B0 of phase (quarter turn around Z). T adds 45\u00B0 (eighth turn). They're the 'fine adjustment knobs' for phase control." },
      { type: "watch", content: "Starting from |+\u27E9, S rotates q0 by 90\u00B0 on the equator to |+i\u27E9. Then T on q1 (also from |+\u27E9) rotates by only 45\u00B0 \u2014 a smaller step." },
      { type: "formula", content: "S = Z^(1/2),  T = S^(1/2) = Z^(1/4)" },
      { type: "insight", content: "The T gate is special: it's the gate that makes quantum computation UNIVERSAL. With just H, CNOT, and T, you can approximate ANY quantum operation to arbitrary precision. T is also the most expensive gate on real hardware \u2014 it requires 'magic state distillation' in error-corrected systems." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [
          { id: "l1", gateType: "H", qubits: [0] },
          { id: "l1b", gateType: "H", qubits: [1] },
        ] },
        { gates: [{ id: "l2", gateType: "S", qubits: [0] }] },
        { gates: [{ id: "l3", gateType: "T", qubits: [1] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["bloch_vector", "contractivity"],
    prerequisites: ["1-3-phase"],
  },

  {
    id: "2-5-rotations",
    module: 2,
    order: 5,
    title: "Rotation Gates",
    subtitle: "Continuous control over the qubit",
    content: [
      { type: "text", content: "Rx, Ry, and Rz rotate the qubit by any angle around the X, Y, or Z axis respectively. Unlike the fixed gates (X, Z, S, T), these give you continuous control." },
      { type: "watch", content: "Ry(\u03C0/3) on q0 tilts it 60\u00B0 from the north pole toward the equator \u2014 creating a specific superposition. Rx(\u03C0/2) on q1 rotates around a different axis." },
      { type: "formula", content: "Ry(\u03B8)|0\u27E9 = cos(\u03B8/2)|0\u27E9 + sin(\u03B8/2)|1\u27E9" },
      { type: "insight", content: "Real quantum hardware (IBM, Google) actually uses these rotation gates natively. When you write a circuit with H or X, the compiler converts them to Rz and \u221AX rotations that the physical qubits can execute. Understanding rotations = understanding the hardware." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "Ry", qubits: [0], params: [Math.PI / 3] }] },
        { gates: [{ id: "l2", gateType: "Rx", qubits: [1], params: [Math.PI / 2] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["bloch_sphere", "unitary"],
    prerequisites: ["2-1-x-gate"],
  },

  {
    id: "2-6-sequences",
    module: 2,
    order: 6,
    title: "Gate Sequences",
    subtitle: "Combining gates to create new operations",
    content: [
      { type: "text", content: "Any single-qubit operation can be built by combining rotations. The sequence H\u2192S\u2192H is equivalent to Rx(\u03C0/2) \u2014 a 90\u00B0 rotation around X. This is how quantum compilers work." },
      { type: "watch", content: "Watch q0 go through three gates: H takes it to the equator, S rotates the phase by 90\u00B0, then H converts that phase back into a probability change. The net effect is a rotation around X." },
      { type: "formula", content: "H \u00B7 S \u00B7 H = Rx(\u03C0/2)  (up to global phase)" },
      { type: "insight", content: "This is the power of the Clifford+T gate set: H, S, T, and CNOT can approximate ANY quantum operation. Quantum compilers use this to convert your ideal circuit into something the hardware can actually execute." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "S", qubits: [0] }] },
        { gates: [{ id: "l3", gateType: "H", qubits: [0] }] },
      ],
    },
    interpMode: "ideal",
    glossaryLinks: ["unitary", "hadamard"],
    prerequisites: ["2-4-s-t-gates"],
  },

  // ═══════════════════════════════════════════════════════════════
  // MODULE 3: ENTANGLEMENT
  // ═══════════════════════════════════════════════════════════════

  {
    id: "3-1-cnot",
    module: 3,
    order: 1,
    title: "CNOT Gate",
    subtitle: "The entanglement machine",
    content: [
      { type: "text", content: "CNOT (Controlled-NOT) flips the target qubit IF the control qubit is |1\u27E9. When the control is in superposition, something magical happens \u2014 the qubits become entangled." },
      { type: "watch", content: "H puts q0 in |+\u27E9. Then CNOT with q0 as control: because q0 is in superposition, both qubits become entangled. Watch both dots collapse toward the CENTER of the sphere \u2014 they've lost their individual identities." },
      { type: "formula", content: "CNOT(|+\u27E9|0\u27E9) = (|00\u27E9 + |11\u27E9)/\u221A2 = |\u03A6+\u27E9" },
      { type: "insight", content: "When qubits are entangled, their individual Bloch vectors move to the CENTER of the sphere (mixed state). This is NOT because we've lost information \u2014 the information has moved from the individual qubits into the CORRELATIONS between them. Check the \u0394Cov tab to see it light up!" },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "CNOT", qubits: [0, 1] }] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["cnot", "entanglement", "bell_states"],
    prerequisites: ["2-3-hadamard"],
  },

  {
    id: "3-2-entanglement",
    module: 3,
    order: 2,
    title: "What is Entanglement?",
    subtitle: "Correlations that can't exist classically",
    content: [
      { type: "text", content: "Entanglement means the qubits are correlated in a way that has no classical explanation. Measuring one qubit INSTANTLY determines the other, no matter how far apart they are." },
      { type: "watch", content: "This is the Bell state |\u03A6+\u27E9 = (|00\u27E9 + |11\u27E9)/\u221A2. Both dots are at the center (maximally mixed individually). But look at the \u0394Cov heatmap: it shows +1.00 correlation \u2014 they ALWAYS agree." },
      { type: "insight", content: "Einstein called this 'spooky action at a distance' and thought it proved quantum mechanics was wrong. In 2022, the Nobel Prize in Physics was awarded for experiments proving entanglement is real. It's now used in quantum cryptography, teleportation, and computing." },
      { type: "text", content: "Switch to the Concurrence tab to see the entanglement measure: C = 1.0 means maximally entangled. Switch to Tangle to see it's pairwise, not multipartite (there are only 2 qubits)." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "CNOT", qubits: [0, 1] }] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["entanglement", "concurrence", "bell_inequality"],
    prerequisites: ["3-1-cnot"],
  },

  {
    id: "3-3-cz",
    module: 3,
    order: 3,
    title: "CZ Gate",
    subtitle: "Symmetric phase entanglement",
    content: [
      { type: "text", content: "CZ (Controlled-Z) applies a phase flip when BOTH qubits are |1\u27E9. Unlike CNOT, CZ is perfectly symmetric \u2014 there's no 'control' or 'target'. Both qubits are equal partners." },
      { type: "watch", content: "Both qubits start in |+\u27E9. CZ creates phase entanglement \u2014 the |11\u27E9 component gets a minus sign. Watch how the dots move on the Bloch sphere." },
      { type: "formula", content: "CZ|++\u27E9 = (|00\u27E9 + |01\u27E9 + |10\u27E9 \u2212 |11\u27E9)/2" },
      { type: "insight", content: "CZ is the gate used to build cluster states \u2014 the resource states for measurement-based quantum computing. A chain of CZ gates on |+\u27E9 states creates a 'quantum graph' where entanglement follows the graph structure." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [
          { id: "l1", gateType: "H", qubits: [0] },
          { id: "l1b", gateType: "H", qubits: [1] },
        ] },
        { gates: [{ id: "l2", gateType: "CZ", qubits: [0, 1] }] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["cz_gate", "cluster_state"],
    prerequisites: ["3-1-cnot"],
  },

  {
    id: "3-4-bell-states",
    module: 3,
    order: 4,
    title: "The Four Bell States",
    subtitle: "All maximally entangled, all different",
    content: [
      { type: "text", content: "There are exactly four maximally entangled 2-qubit states, called the Bell states. They form a complete basis for 2-qubit entanglement." },
      { type: "text", content: "|\u03A6+\u27E9 = (|00\u27E9+|11\u27E9)/\u221A2 \u2014 correlated, same phase\n|\u03A6\u207B\u27E9 = (|00\u27E9\u2212|11\u27E9)/\u221A2 \u2014 correlated, opposite phase\n|\u03A8+\u27E9 = (|01\u27E9+|10\u27E9)/\u221A2 \u2014 anti-correlated, same phase\n|\u03A8\u207B\u27E9 = (|01\u27E9\u2212|10\u27E9)/\u221A2 \u2014 the singlet (anti-correlated, opposite phase)" },
      { type: "watch", content: "This circuit creates |\u03A8\u207B\u27E9 \u2014 the singlet state. X flips q0 to |1\u27E9 first, then H creates superposition, then CNOT entangles. The singlet is special: it's rotationally invariant." },
      { type: "insight", content: "The singlet |\u03A8\u207B\u27E9 is used in E91 quantum key distribution because its correlations are the strongest possible violation of the Bell inequality. This is the state used to prove quantum mechanics can't be explained by hidden variables." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "X", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l3", gateType: "CNOT", qubits: [0, 1] }] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["bell_states", "epr_pair", "bell_inequality"],
    prerequisites: ["3-2-entanglement"],
  },

  {
    id: "3-5-monogamy",
    module: 3,
    order: 5,
    title: "Entanglement Monogamy",
    subtitle: "GHZ vs W \u2014 two kinds of multipartite entanglement",
    content: [
      { type: "text", content: "Entanglement obeys monogamy: the more entangled two qubits are with each other, the less they can be entangled with a third. This leads to two fundamentally different types of 3-qubit entanglement." },
      { type: "text", content: "GHZ = (|000\u27E9 + |111\u27E9)/\u221A2: ALL entanglement is genuinely tripartite. Pairwise concurrence = 0, but 3-tangle = 1. Losing one qubit destroys ALL entanglement." },
      { type: "watch", content: "This is the GHZ state. All three dots collapse to the center simultaneously. Check the Tangle tab: \u03C4\u2083 = 1.000. Now check Concurrence: all pairs show 0. The entanglement exists between ALL THREE qubits collectively, not in any pair." },
      { type: "insight", content: "Compare this with the W state (load it from presets): W has \u03C4\u2083 = 0 but pairwise concurrence \u2248 0.67. ALL entanglement is pairwise. Losing one qubit preserves entanglement between the other two. These are the only two classes of genuine 3-qubit entanglement." },
    ],
    circuit: {
      numQubits: 3,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "l3", gateType: "CNOT", qubits: [0, 2] }] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["ghz_state", "w_state", "total_correlation"],
    prerequisites: ["3-2-entanglement"],
  },

  // ═══════════════════════════════════════════════════════════════
  // MODULE 4: QUANTUM ALGORITHMS
  // ═══════════════════════════════════════════════════════════════

  {
    id: "4-1-interference",
    module: 4,
    order: 1,
    title: "Quantum Interference",
    subtitle: "How phase becomes probability",
    content: [
      { type: "text", content: "The Deutsch-Jozsa algorithm demonstrates the core mechanism of ALL quantum algorithms: (1) create superposition, (2) accumulate phase, (3) interfere to convert phase into measurable probability." },
      { type: "watch", content: "Step 1: X+H prepare the qubits. Step 2: H creates superposition on the input qubit. Step 3: The CNOT oracle marks the target state with a phase flip (via kickback). Step 4: Final H converts the phase difference into a definite measurement outcome." },
      { type: "insight", content: "The key moment is the final Hadamard: it takes the invisible phase difference and converts it into a visible probability difference. If the oracle was balanced, you get |1\u27E9 with certainty. If constant, |0\u27E9 with certainty. One query solves what classically requires two. This is quantum speedup." },
      { type: "text", content: "Every quantum algorithm follows this same three-step pattern: superposition \u2192 phase accumulation \u2192 interference. Grover, Shor, and all the others are elaborations on this idea." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [{ id: "l1", gateType: "X", qubits: [1] }] },
        { gates: [
          { id: "l2", gateType: "H", qubits: [0] },
          { id: "l3", gateType: "H", qubits: [1] },
        ] },
        { gates: [{ id: "l4", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "l5", gateType: "H", qubits: [0] }] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["superposition", "interference", "hadamard"],
    prerequisites: ["3-1-cnot"],
  },

  {
    id: "4-2-teleportation",
    module: 4,
    order: 2,
    title: "Quantum Teleportation",
    subtitle: "Transmitting quantum states using entanglement",
    content: [
      { type: "text", content: "Quantum teleportation transfers a qubit's state from one location to another using a pre-shared Bell pair and classical communication. No physical qubit travels \u2014 only the state is transmitted." },
      { type: "watch", content: "Steps 1-3: Create Bell pair between q1 and q2 (the 'channel'). q0 holds the state to teleport (|+\u27E9). Steps 4-5: Bell measurement on q0,q1. Steps 6-7: Classical corrections on q2. The end state of q2 should match the original state of q0." },
      { type: "insight", content: "Teleportation doesn't violate special relativity because you need to send 2 classical bits alongside the quantum channel. Without the classical correction, Bob's qubit is just random noise. This is the foundation of quantum networking and the quantum internet." },
      { type: "text", content: "Teleportation is also used INSIDE quantum computers to move qubit states between non-adjacent physical qubits on the chip. It's a practical engineering tool, not just a thought experiment." },
    ],
    circuit: {
      numQubits: 3,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "H", qubits: [1] }] },
        { gates: [{ id: "l3", gateType: "CNOT", qubits: [1, 2] }] },
        { gates: [{ id: "l4", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "l5", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l6", gateType: "CNOT", qubits: [1, 2] }] },
        { gates: [{ id: "l7", gateType: "CZ", qubits: [0, 2] }] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["bell_states", "entanglement"],
    prerequisites: ["3-2-entanglement"],
  },

  {
    id: "4-3-grover",
    module: 4,
    order: 3,
    title: "Grover's Search",
    subtitle: "Finding needles in quantum haystacks",
    content: [
      { type: "text", content: "Grover's algorithm searches an unsorted database of N items in \u221AN steps instead of N. For 4 items (2 qubits), it finds the answer in just 1 step with 100% certainty." },
      { type: "watch", content: "Step 1: H\u2297H creates uniform superposition (all 4 states equally likely). Step 2: CZ oracle marks |11\u27E9 with a phase flip. Steps 3-7: The diffusion operator amplifies the marked state. Final result: |11\u27E9 with certainty." },
      { type: "insight", content: "The magic is in the diffusion operator (steps 3-7): it reflects amplitudes about the mean. The marked state has negative amplitude (from the oracle), so after reflection it becomes positive and LARGER than the others. This is amplitude amplification \u2014 the workhorse of quantum search." },
      { type: "text", content: "Grover's speedup is quadratic (\u221AN), not exponential. But it's provably optimal \u2014 no quantum algorithm can do better for unstructured search. It's used as a subroutine in many other quantum algorithms." },
    ],
    circuit: {
      numQubits: 2,
      moments: [
        { gates: [
          { id: "l1", gateType: "H", qubits: [0] },
          { id: "l2", gateType: "H", qubits: [1] },
        ] },
        { gates: [{ id: "l3", gateType: "CZ", qubits: [0, 1] }] },
        { gates: [
          { id: "l4", gateType: "H", qubits: [0] },
          { id: "l5", gateType: "H", qubits: [1] },
        ] },
        { gates: [
          { id: "l6", gateType: "X", qubits: [0] },
          { id: "l7", gateType: "X", qubits: [1] },
        ] },
        { gates: [{ id: "l8", gateType: "CZ", qubits: [0, 1] }] },
        { gates: [
          { id: "l9", gateType: "X", qubits: [0] },
          { id: "l10", gateType: "X", qubits: [1] },
        ] },
        { gates: [
          { id: "l11", gateType: "H", qubits: [0] },
          { id: "l12", gateType: "H", qubits: [1] },
        ] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["grover_search", "superposition"],
    prerequisites: ["4-1-interference"],
  },

  {
    id: "4-4-error-correction",
    module: 4,
    order: 4,
    title: "Quantum Error Correction",
    subtitle: "Protecting quantum information from noise",
    content: [
      { type: "text", content: "Quantum states are fragile \u2014 they decohere from noise. Error correction encodes one logical qubit into multiple physical qubits so errors can be detected and fixed without measuring (and destroying) the quantum state." },
      { type: "watch", content: "Steps 1-3: Encode |+\u27E9 across 3 qubits. Step 4: A bit-flip error (X) hits q1 \u2014 this is the 'noise'. Steps 5-7: Syndrome extraction and correction via Toffoli gate. The error is fixed!" },
      { type: "insight", content: "The key insight is that you can detect errors WITHOUT measuring the encoded state. The syndrome measurements (CNOTs) extract ONLY the error information, not the quantum data. This is what makes fault-tolerant quantum computing possible." },
      { type: "text", content: "The bit-flip code is the simplest QEC code. Real systems use the surface code, which can correct both bit-flips AND phase-flips. Google, IBM, and others are actively building error-corrected quantum computers using this approach." },
    ],
    circuit: {
      numQubits: 3,
      moments: [
        { gates: [{ id: "l1", gateType: "H", qubits: [0] }] },
        { gates: [{ id: "l2", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "l3", gateType: "CNOT", qubits: [0, 2] }] },
        { gates: [{ id: "l4", gateType: "X", qubits: [1] }] },
        { gates: [{ id: "l5", gateType: "CNOT", qubits: [0, 1] }] },
        { gates: [{ id: "l6", gateType: "CNOT", qubits: [0, 2] }] },
        { gates: [{ id: "l7", gateType: "Toffoli", qubits: [1, 2, 0] }] },
      ],
    },
    interpMode: "direct",
    glossaryLinks: ["stabilizer", "logical_qubit", "threshold_theorem"],
    prerequisites: ["3-1-cnot"],
  },
];
