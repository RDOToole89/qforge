# AGENTS.md — Bloch Sphere CPTP Visualizer

Quick reference for AI agents working on this component.

## What This Is

An interactive 3D visualization of quantum noise channels on the Bloch sphere, integrated into an Expo app. Two modes:

- **Built-in mode**: Hardcoded educational examples showing how probe states (GHZ, W, Cluster, etc.) respond to noise channels and topologies
- **Experiment mode**: Live data from the Python experiment pipeline — per-qubit Bloch vectors from partial traces, real correlators, mutual information, and animated decoherence sweeps

## UI Layout

The interface follows a **tab-based full-screen** design:

```
[Header: [Built-in|Experiment] | 1-Qubit | 2-Qubit | PTM | Data | Config btn]
[Left Sidebar]  [        Full-screen 3D Scene          ]  [Right Sidebar]
[State buttons] [   BlochScene OR TwoQubitScene         ]  [Context panels]
[Channel btns ] [   (drag to rotate)                    ]  [Kraus/PTM/etc]
[Controls     ] [                                       ]  [Insight text ]
```

- **Mode toggle**: switches between Built-in (hardcoded) and Experiment (live data) modes
- Left sidebar: in built-in mode, button-style selectors; in experiment mode, result picker + sweep controls
- Center: single full-screen Three.js scene (NOT split view)
- Right sidebar: info panels that change per tab and mode (includes educational explainers in experiment mode)
- Config button opens a modal overlay with JSON editor

## File Map

```
types.ts              Types only. No logic. Change here first when adding new data shapes.
                      Includes ExperimentalDataEntry for fingerprint loading.
config.ts             DEFAULT_CONFIG. All probe states, channels, topologies defined here.
                      To add a state/channel/topology: add an entry, it auto-appears in UI.
math.ts               Pure functions. V3(), spherePoints(), compileBlochMap(), buildRuntime(),
                      stateVectorToBloch() (partial trace → Pauli expectations),
                      blochToThree() (canonical coordinate swap),
                      correlationMatrix() (ΔCov), pairConcurrence() (Wootters formula),
                      threeTangle() (CKW), multipartiteTangle(), oneTangle().
                      compileBlochMap() uses new Function() to compile string expressions
                      like "(1-p)*rx" into executable Bloch map functions.
                      buildRuntime() takes config.channels and returns RuntimeChannel objects
                      with compiled apply() and ptm() methods.
experimentAdapter.ts  Pure functions converting BlochVisualizerData (API response) into
                      existing component prop shapes (ProbeStateConfig, etc.).
                      Functions: blochDataToStateCfg(), blochDataToAllQubits(),
                      blochDataToPairCfg(), blochDataToFingerprints(), getQubitPairs().
                      Also exports QUBIT_COLORS palette for per-qubit coloring.
BlochSphereScreen.tsx  Main orchestrator. Manages all state: tab, mode (builtin/experiment),
                      selected state/channel/topo, strength, animation, drag rotation,
                      experiment result selection, sweep config/animation.
                      Contains inline MIMatrixHeatmap component.
                      USE DOM component.
data/
  stateBlochConfigs.ts  90+ BlochDot configs for glossary terms (extracted from old MiniBlochSphere).
                        Maps glossary term IDs to {dots, caption} for mini Bloch sphere rendering.

components/
  UnifiedBlochSphere.tsx  Single Bloch sphere component serving ALL use cases via discriminated
                          union props (mode: "glossary" | "visualizer" | "circuit").
                          - glossary: auto-rotate, drag-to-spin, expand, dot glow meshes
                          - visualizer: external rotation, point clouds, channel transforms
                          - circuit: gentle auto-rotate, dots updated via refs (no rebuild)
                          Replaces both old BlochScene.tsx and MiniBlochSphere.tsx. USE DOM.
  TwoQubitScene.tsx    Three.js scene: 3-axis correlator space (ZI, IZ, ZZ).
                      Multiple topology clouds with distinct colors. Supports "all" mode.
                      Controlled rotation via parent. USE DOM.
  PTMHeatmap.tsx       4x4 grid showing Pauli Transfer Matrix values. Orange=positive, blue=negative.
                      Takes runtimeCh + channel key + strength. Accepts optional rawMatrix
                      prop to render directly without computing from channel. Pure HTML/CSS.
  CorrelatorBars.tsx   Delta-correlator horizontal bars with center-line style.
                      Takes stateCfg + topology + strength. Generates sample points internally.
                      Accepts optional experimentCorrelators prop to show actual measured
                      Pauli expectation values (ZI, IZ, ZZ, XX, YY) instead of deltas.
  FingerprintViewer.tsx Displays loaded ExperimentalDataEntry[] with norms bars + cosine
                      similarity matrix. Color-coded by topology.
  ConfigEditor.tsx     Modal overlay with JSON editor. Tabs: States, Channels, Exp. Data,
                      Topologies. Apply/Export/Import/Reset buttons.
  ReducedStateExplainer.tsx  Educational panel for experiment mode. Four contexts:
                      "single" (reduced density matrix), "diagonal_warning" (Z-basis only),
                      "multi_qubit_insight" (per-qubit decoherence), "multi" (two-qubit
                      correlators). Explains partial traces, purity, and measurement limits.
```

## Critical Implementation Details

### `'use dom'` Components

Files with `'use dom'` as the first line are **web-only**. They use HTML elements (div, span, input), NOT React Native primitives (View, Text). On native, Expo renders them in an automatic webview. Do NOT import React Native modules in these files.

### Drag-to-Rotate

The 3D scenes do NOT auto-rotate. Rotation is controlled by the parent via `rotation` prop. `BlochSphereScreen` handles pointer events (drag) and passes the rotation angle down. Both `BlochScene` and `TwoQubitScene` use refs to read the rotation value in their animation loops without re-mounting.

### Bloch Map Compilation

`compileBlochMap()` in `math.ts` takes string expressions and compiles them into functions:

```typescript
// Config defines: blochMap: { rx: "(1-p)*rx", ry: "(1-p)*ry", rz: "(1-p)*rz" }
// At runtime, this becomes: (r, p) => Vector3(...)
const apply = compileBlochMap(channel.blochMap);
const transformed = apply({ x: 0.5, y: 0, z: 0.8 }, 0.3); // applies depolarizing at p=0.3
```

Available variables in expressions: `rx`, `ry`, `rz`, `p`, `sqrt()`.

### Three.js Coordinate Swap

Three.js uses Y-up. Bloch sphere uses Z-up. The scenes swap Y<->Z:
```typescript
// Bloch (x, y, z) -> Three.js (x, z, y)
position[i*3] = pt.x;     // Three.js X = Bloch X
position[i*3+1] = pt.z;   // Three.js Y = Bloch Z (up)
position[i*3+2] = pt.y;   // Three.js Z = Bloch Y
```

### State Types and Z-Basis Signal

Each probe state has a `zBasisSignal` field: `"strong"`, `"weak"`, or `"zero"`. This categorizes how visible noise is in Z-basis measurement statistics:
- `"strong"` = correlated noise is clearly visible in Z-basis correlators (GHZ, Bell)
- `"weak"` = marginal visibility (W)
- `"zero"` = Pauli invariant, invisible to Z-basis measurement (Cluster, Superposition)

### 2-Qubit Correlator Model

The 2-qubit view uses a simplified noise model (not full Qiskit simulation):
- `singleQubitDecay`: how fast individual Pauli expectations shrink
- `corrGrowZZ/XX/YY`: how fast 2-body correlators grow (topology effect)
- `preserveZ`: if true, Z-component doesn't decay (models pure dephasing)

This is a pedagogical approximation. For quantitative results, use the Python engine or experiment mode.

### Experiment Mode Architecture

In experiment mode, data flows: **Python engine → `/api/bloch` endpoints → `experimentAdapter.ts` → existing components**.

The adapter converts `BlochVisualizerData` (API response) into `ProbeStateConfig` and other existing prop shapes so that `BlochScene`, `CorrelatorBars`, `FingerprintViewer`, etc. work unchanged.

Key state in `BlochSphereScreen`:
- `mode`: `"builtin" | "experiment"` — controls which sidebar/controls are shown
- `blochData` / `sweepData`: raw API responses
- `_activeBloch`: computed as `sweepSnapshot ?? blochData` — all derived data uses this single source
- `sweepProgress`: 0–1 float controlling the interpolation position across sweep snapshots

### Sweep Interpolation

The sweep animates by linearly interpolating between `BlochVisualizerData` snapshots:
- Bloch vectors: lerp per-component (rx, ry, rz)
- Purity: lerp scalar
- Correlators: lerp per-component (zi, iz, zz, xx, yy)
- MI matrix: lerp per-cell
- The `sweepSnapshot` useMemo produces a synthetic `BlochVisualizerData` at any fractional position

### Animation Loop Pattern

Both scenes use refs to read current props inside `requestAnimationFrame` loops. This avoids re-mounting the WebGL context on every prop change:

```typescript
const pRef = useRef(props);
useEffect(() => { pRef.current = props; }); // update ref every render

// In animation loop:
const animate = () => {
  const pr = pRef.current; // always current values
  // ... use pr.rotation, pr.strength, etc.
};
```

### Backend: `apps/api/routes/bloch.py`

Contains the quantum math (NumPy) and two FastAPI endpoints:
- `GET /{filename:path}` — transforms stored result into BlochVisualizerData
- `POST /sweep` — runs experiments at multiple error rates, returns snapshot array

Key math: `partial_trace_single_qubit` and `partial_trace_two_qubit` use `np.einsum` to trace out qubits. `density_matrix_to_bloch` extracts Bloch vector via Pauli traces. `mutual_information_from_rho` computes von Neumann entropy-based MI.

## How to Extend

### Add a probe state
Edit `config.ts` -> `DEFAULT_CONFIG.states`. Required fields:
```typescript
myState: {
  name: "My State",
  desc: "Description",
  bloch: { rx: 0, ry: 0, rz: 0 },       // single-qubit reduced state Bloch vector
  correlators: { zi: 0, iz: 0, zz: 0, xx: 0, yy: 0 },  // 2-qubit correlator signature
  color: "#hexcolor",
  zBasisSignal: "strong" | "weak" | "zero",
  insight: "Why this state is interesting.",
  uniform: false,                          // true if Z-basis distribution is uniform
}
```

### Add a noise channel
Edit `config.ts` -> `DEFAULT_CONFIG.channels`. The `blochMap` uses string expressions:
```typescript
myChannel: {
  name: "My Channel",
  desc: "Short description",
  formula: "rx -> f(rx, p)  ry -> f(ry, p)  rz -> f(rz, p)",
  blochMap: { rx: "(1-2*p)*rx", ry: "(1-2*p)*ry", rz: "rz" },
  kraus: "K0=... K1=...",
  geometry: "Sphere -> shape description",
  insight: "Physical interpretation.",
}
```

### Add a noise topology
Edit `config.ts` -> `DEFAULT_CONFIG.topologies`:
```typescript
myTopology: {
  name: "My Topology",
  desc: "Description",
  corrGrowXX: 0, corrGrowYY: 0, corrGrowZZ: 0.5,
  singleQubitDecay: 1.0,
  preserveZ: false,
}
```

### Load experimental data
The Data tab accepts JSON arrays of fingerprint entries via the Config modal:
```json
[{
  "label": "GHZ chain p=0.1",
  "noiseStrength": 0.1,
  "topology": "chain",
  "fingerprint": [15 floats for 6-qubit delta-covariance vector]
}]
```

## What NOT to Do

- Do NOT import React Native components (View, Text, etc.) in `'use dom'` files
- Do NOT try to render full multi-qubit PTMs (16x16+) as heatmaps — they're unreadable
- Do NOT add hardware noise model import — it's out of scope for this visualizer
- Do NOT replace button-style selectors with dropdowns — the button layout is intentional for visual density
- Do NOT split the center 3D scene into side-by-side views — the full-screen scene is a deliberate design choice
- Do NOT move quantum math (partial traces, Bloch vectors) to the frontend — it must stay in Python/NumPy for scientific rigor
- Do NOT use `encodeURIComponent` on filenames passed to `/api/bloch/` — the `{filename:path}` route parameter expects literal slashes

## Next Priority

Frozen until the Python package is installable as `qforge`. Do not add renderers, presets, or native-app work. Parked item when the freeze lifts:

**Measurement basis toggle** (v5.1) — adding X/Y basis to the 2-qubit view so Cluster states show non-zero correlators. Tracked as **FE-4** in `apps/AGENTS.md`.
