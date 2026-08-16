/**
 * Default configuration for the Bloch Sphere CPTP Visualizer.
 *
 * Two-qubit correlator signatures are backend-owned facts. ALL states source
 * their zi/iz/zz/xx/yy correlators from the generated catalog (STATE_CORRELATORS
 * in src/generated/catalog.ts), which the Python backend computes via
 * bloch_math.two_qubit_correlators on the prepared states. This is the single
 * source of truth — there are no competing hardcoded physics values here.
 *
 * The only local correlator terms are Cluster's xz/zx entries: the backend's
 * two_qubit_correlators does not compute the off-axis xz/zx Pauli terms, so they
 * are kept as explicit pedagogical placeholders (see the comment at that entry),
 * not as a divergent second source for the terms the backend does compute.
 *
 * Regenerate the catalog with:
 *   uv run python scripts/gen_frontend_constants.py
 */
import { STATE_CORRELATORS } from "@/src/generated/catalog";
import { chrome, viz } from "@/src/design/tokens";
import type { BlochConfig } from "./types";

export const DEFAULT_CONFIG: BlochConfig = {
  states: {
    ghz: {
      name: "GHZ",
      desc: "Greenberger-Horne-Zeilinger",
      bloch: { rx: 0, ry: 0, rz: 0 },
      correlators: { ...STATE_CORRELATORS.ghz.correlators },
      color: viz.orange,
      zBasisSignal: "strong",
      insight:
        "GHZ has maximal ZZ correlation. Z-basis measurement sees the full correlation structure — noise that disrupts ZZ shows up immediately. This is why GHZ is your best Z-basis probe.",
      uniform: false,
    },
    bell: {
      name: "Bell (|\u03A6+\u27E9)",
      desc: "Maximally entangled pair",
      bloch: { rx: 0, ry: 0, rz: 0 },
      correlators: { ...STATE_CORRELATORS.bell.correlators },
      color: viz.aqua,
      zBasisSignal: "strong",
      insight:
        "Bell state = 2-qubit GHZ. Same correlator structure, same noise sensitivity.",
      uniform: false,
    },
    w_state: {
      name: "W",
      desc: "W state (single-excitation superposition)",
      bloch: { rx: 0, ry: 0, rz: 0.33 },
      correlators: { ...STATE_CORRELATORS.w_state.correlators },
      color: viz.green,
      zBasisSignal: "weak",
      insight:
        "W state has non-uniform Z-marginals but relatively weak two-qubit correlations, so it is a poor Z-basis probe.",
      uniform: false,
    },
    cluster: {
      name: "Cluster",
      desc: "Graph state (CZ entanglement)",
      bloch: { rx: 0, ry: 0, rz: 0 },
      correlators: {
        // zi/iz/zz/xx/yy come from the backend (all zero for the cluster
        // state's reduced 2-qubit marginal). xz/zx are intentional pedagogical
        // placeholders: bloch_math.two_qubit_correlators does not compute the
        // off-axis xz/zx Pauli terms, and the cluster state's stabilizer
        // structure lives precisely in those terms. They are NOT a competing
        // source for the backend-computed terms above.
        ...STATE_CORRELATORS.cluster.correlators,
        xz: 1.0,
        zx: 1.0,
      },
      color: viz.purple,
      zBasisSignal: "zero",
      insight:
        "Cluster state: exactly zero in the Z-basis — its correlations live in the off-axis (X-Z) Pauli terms.",
      uniform: true,
    },
    superposition: {
      name: "Equal Superposition",
      desc: "|+\u27E9\u2297n (product state)",
      bloch: { rx: 1, ry: 0, rz: 0 },
      correlators: { ...STATE_CORRELATORS.superposition.correlators },
      color: viz.rose,
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
        "K\u2081 maps |1\u27E9\u21920\u27E9 — energy relaxation written directly as a Kraus operator.",
    },
    phase_damping: {
      name: "Dephasing",
      desc: "T\u2082 coherence loss",
      formula: "rx\u2192(1\u2212p)rx  ry\u2192(1\u2212p)ry  rz\u2192rz",
      blochMap: { rx: "(1-p)*rx", ry: "(1-p)*ry", rz: "rz" },
      kraus: "K\u2080=\u221A(1\u2212p/2)\u00B7I  K\u2081=\u221A(p/2)\u00B7Z",
      geometry: "Sphere \u2192 pancake (Z preserved)",
      insight:
        "Z-basis sees nothing for Z-symmetric states (Pauli invariance under dephasing).",
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
  display: { pointCount: 350, backgroundColor: chrome.bg.primary },
};
