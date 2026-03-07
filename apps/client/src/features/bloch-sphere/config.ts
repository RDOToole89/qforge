/**
 * Default configuration for the Bloch Sphere CPTP Visualizer.
 */
import type { BlochConfig } from "./types";

export const DEFAULT_CONFIG: BlochConfig = {
  states: {
    ghz: {
      name: "GHZ",
      desc: "Greenberger-Horne-Zeilinger",
      bloch: { rx: 0, ry: 0, rz: 0 },
      correlators: {
        zi: 0,
        iz: 0,
        zz: 1.0,
        xx: 1.0,
        yy: -1.0,
      },
      color: "#ff9933",
      zBasisSignal: "strong",
      insight:
        "GHZ has maximal ZZ correlation. Z-basis measurement sees the full correlation structure — noise that disrupts ZZ shows up immediately. This is why GHZ is your best Z-basis probe.",
      uniform: false,
    },
    bell: {
      name: "Bell (|\u03A6+\u27E9)",
      desc: "Maximally entangled pair",
      bloch: { rx: 0, ry: 0, rz: 0 },
      correlators: { zi: 0, iz: 0, zz: 1.0, xx: 1.0, yy: -1.0 },
      color: "#44ddff",
      zBasisSignal: "strong",
      insight:
        "Bell state = 2-qubit GHZ. Same correlator structure, same noise sensitivity.",
      uniform: false,
    },
    w_state: {
      name: "W",
      desc: "W state (single-excitation superposition)",
      bloch: { rx: 0, ry: 0, rz: 0.33 },
      correlators: {
        zi: 0.33,
        iz: 0.33,
        zz: -0.11,
        xx: 0.22,
        yy: 0.22,
      },
      color: "#44ff88",
      zBasisSignal: "weak",
      insight:
        "W state has non-uniform Z-marginals but WEAK correlations. Your data: 0/9 detections.",
      uniform: false,
    },
    cluster: {
      name: "Cluster",
      desc: "Graph state (CZ entanglement)",
      bloch: { rx: 0, ry: 0, rz: 0 },
      correlators: {
        zi: 0,
        iz: 0,
        zz: 0,
        xx: 0,
        yy: 0,
        xz: 1.0,
        zx: 1.0,
      },
      color: "#b48cff",
      zBasisSignal: "zero",
      insight:
        "Cluster state: EXACTLY zero in Z-basis. Your Pauli invariance theorem.",
      uniform: true,
    },
    superposition: {
      name: "Equal Superposition",
      desc: "|+\u27E9\u2297n (product state)",
      bloch: { rx: 1, ry: 0, rz: 0 },
      correlators: { zi: 0, iz: 0, zz: 0, xx: 0, yy: 0 },
      color: "#ff4466",
      zBasisSignal: "zero",
      insight:
        "Equal superposition is a PRODUCT state — no entanglement, no correlations. Z-basis gives uniform distribution.",
      uniform: true,
    },
  },
  channels: {
    depolarizing: {
      name: "Depolarizing",
      desc: "Uniform shrinkage",
      formula: "r \u2192 (1\u2212p)\u00B7r",
      blochMap: {
        rx: "(1-p)*rx",
        ry: "(1-p)*ry",
        rz: "(1-p)*rz",
      },
      kraus: "K\u2080=\u221A(1\u22123p/4)\u00B7I  K\u2081=\u221A(p/4)\u00B7X  K\u2082=\u221A(p/4)\u00B7Y  K\u2083=\u221A(p/4)\u00B7Z",
      geometry: "Sphere \u2192 smaller sphere",
      insight: "Isotropic filter — all directions contract equally.",
    },
    amplitude_damping: {
      name: "Amplitude Damping",
      desc: "T\u2081 relaxation toward |0\u27E9",
      formula:
        "rx\u2192\u221A(1\u2212\u03B3)rx  ry\u2192\u221A(1\u2212\u03B3)ry  rz\u2192\u03B3+(1\u2212\u03B3)rz",
      blochMap: {
        rx: "sqrt(1-p)*rx",
        ry: "sqrt(1-p)*ry",
        rz: "p+(1-p)*rz",
      },
      kraus: "K\u2080=[[1,0],[0,\u221A(1\u2212\u03B3)]]  K\u2081=[[0,\u221A\u03B3],[0,0]]",
      geometry: "Sphere \u2192 ellipsoid shifted to |0\u27E9",
      insight:
        "K\u2081 maps |1\u27E9\u21920\u27E9 — the pathway IS the Kraus operator.",
    },
    phase_damping: {
      name: "Dephasing",
      desc: "T\u2082 coherence loss",
      formula: "rx\u2192(1\u2212p)rx  ry\u2192(1\u2212p)ry  rz\u2192rz",
      blochMap: { rx: "(1-p)*rx", ry: "(1-p)*ry", rz: "rz" },
      kraus: "K\u2080=\u221A(1\u2212p/2)\u00B7I  K\u2081=\u221A(p/2)\u00B7Z",
      geometry: "Sphere \u2192 pancake (Z preserved)",
      insight:
        "Z-basis sees nothing for Z-symmetric states. Your Pauli invariance.",
    },
    bit_flip: {
      name: "Bit Flip",
      desc: "Random X errors",
      formula: "rx\u2192rx  ry\u2192(1\u22122p)ry  rz\u2192(1\u22122p)rz",
      blochMap: {
        rx: "rx",
        ry: "(1-2*p)*ry",
        rz: "(1-2*p)*rz",
      },
      kraus: "K\u2080=\u221A(1\u2212p)\u00B7I  K\u2081=\u221Ap\u00B7X",
      geometry: "Sphere \u2192 pancake (X preserved)",
      insight: "X-eigenstates are pointer states — einselection along X.",
    },
    phase_flip: {
      name: "Phase Flip",
      desc: "Random Z errors",
      formula:
        "rx\u2192(1\u22122p)rx  ry\u2192(1\u22122p)ry  rz\u2192rz",
      blochMap: {
        rx: "(1-2*p)*rx",
        ry: "(1-2*p)*ry",
        rz: "rz",
      },
      kraus: "K\u2080=\u221A(1\u2212p)\u00B7I  K\u2081=\u221Ap\u00B7Z",
      geometry: "Sphere \u2192 pancake (Z preserved)",
      insight: "Same geometry as dephasing. Z-eigenstates survive.",
    },
  },
  topologies: {
    chain: {
      name: "Chain (correlated depol)",
      desc: "Same Pauli on A\u2194B edge",
      corrGrowXX: 0.33,
      corrGrowYY: 0.33,
      corrGrowZZ: 0.33,
      singleQubitDecay: 1.0,
    },
    star: {
      name: "Star (independent)",
      desc: "Separate depol per qubit",
      corrGrowXX: 0,
      corrGrowYY: 0,
      corrGrowZZ: 0,
      singleQubitDecay: 1.0,
    },
    corr_zz: {
      name: "Correlated ZZ",
      desc: "ZZ dephasing on edge",
      corrGrowXX: 0,
      corrGrowYY: 0,
      corrGrowZZ: 0.8,
      singleQubitDecay: 0.7,
      preserveZ: true,
    },
  },
  experimentalData: [] as import("./types").ExperimentalDataEntry[],
  display: { pointCount: 350, backgroundColor: "#08090e" },
};
