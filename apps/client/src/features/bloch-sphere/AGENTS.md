# AGENTS.md — Bloch Sphere CPTP Visualizer

Quick reference for AI agents working on this component.

## What This Is

An interactive 3D visualization of quantum noise channels on the Bloch sphere, integrated into an Expo app. It shows how different probe states (GHZ, W, Cluster, etc.) respond to different noise channels and topologies — directly tied to the Qiskit Experiment Framework's structured decoherence research.

## File Map

```
types.ts              Types only. No logic. Change here first when adding new data shapes.
config.ts             DEFAULT_CONFIG. All probe states, channels, topologies defined here.
                      To add a state/channel/topology: add an entry, it auto-appears in UI.
math.ts               Pure functions. V3(), spherePoints(), compileBlochMap(), buildRuntime().
                      compileBlochMap() uses new Function() to compile string expressions
                      like "(1-p)*rx" into executable Bloch map functions.
                      buildRuntime() takes config.channels and returns RuntimeChannel objects
                      with compiled apply() and ptm() methods.
BlochSphereScreen.tsx  Main orchestrator. Manages all state (selected state, channel, topo,
                      error rate). Passes props down to child components. USE DOM component.
components/
  BlochScene.tsx       Three.js scene: wireframe sphere, axes, point clouds (original + transformed).
                      Receives runtimeCh, channel key, strength, showOrig/showTrans, rotation.
                      USE DOM — renders in webview on native.
  TwoQubitScene.tsx    Three.js scene: 3-axis correlator space (ZI, IZ, ZZ).
                      Shows how noise topologies deform correlator signatures differently.
                      USE DOM.
  PTMHeatmap.tsx       4x4 grid showing Pauli Transfer Matrix values. Pure HTML/CSS.
  CorrelatorBars.tsx   Horizontal bars showing delta-correlators (clean - noisy). Pure HTML/CSS.
  FingerprintViewer.tsx Displays loaded fingerprint norms + cosine similarity matrix.
  ConfigEditor.tsx     State/channel/topology selector + error rate range input.
```

## Critical Implementation Details

### `'use dom'` Components

Files with `'use dom'` as the first line are **web-only**. They use HTML elements (div, span, input), NOT React Native primitives (View, Text). On native, Expo renders them in an automatic webview. Do NOT import React Native modules in these files.

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
// Bloch (x, y, z) → Three.js (x, z, y)
position[i*3] = pt.x;     // Three.js X = Bloch X
position[i*3+1] = pt.z;   // Three.js Y = Bloch Z (up)
position[i*3+2] = pt.y;   // Three.js Z = Bloch Y
```

### State Types and Z-Basis Signal

Each probe state has a `zBasisSignal` field: `"strong"`, `"weak"`, or `"zero"`. This directly maps to the framework's research findings:
- `"strong"` = detects correlated noise via NTC (GHZ, Bell)
- `"weak"` = marginal detection (W)
- `"zero"` = Pauli invariant, invisible to Z-basis measurement (Cluster, Superposition)

### 2-Qubit Correlator Model

The 2-qubit view uses a simplified noise model (not full Qiskit simulation):
- `singleQubitDecay`: how fast individual Pauli expectations shrink
- `corrGrowZZ/XX/YY`: how fast 2-body correlators grow (topology effect)
- `preserveZ`: if true, Z-component doesn't decay (models pure dephasing)

This is a pedagogical approximation. For quantitative results, use the Python engine.

## How to Extend

### Add a probe state
Edit `config.ts` → `DEFAULT_CONFIG.states`. Required fields:
```typescript
myState: {
  name: "My State",
  desc: "Description",
  bloch: { rx: 0, ry: 0, rz: 0 },       // single-qubit reduced state Bloch vector
  correlators: { zi: 0, iz: 0, zz: 0, xx: 0, yy: 0 },  // 2-qubit correlator signature
  color: "#hexcolor",
  zBasisSignal: "strong" | "weak" | "zero",
  insight: "Why this state matters for the research.",
  uniform: false,                          // true if Z-basis distribution is uniform
}
```

### Add a noise channel
Edit `config.ts` → `DEFAULT_CONFIG.channels`. The `blochMap` uses string expressions:
```typescript
myChannel: {
  name: "My Channel",
  desc: "Short description",
  formula: "rx → f(rx, p)  ry → f(ry, p)  rz → f(rz, p)",
  blochMap: { rx: "(1-2*p)*rx", ry: "(1-2*p)*ry", rz: "rz" },
  kraus: "K₀=... K₁=...",
  geometry: "Sphere → shape description",
  insight: "Physical interpretation.",
}
```

### Add a noise topology
Edit `config.ts` → `DEFAULT_CONFIG.topologies`:
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
The Data tab accepts JSON arrays of fingerprint entries:
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
- Do NOT add hardware noise model import — it's a rabbit hole for current research stage
- Do NOT use this for quantitative analysis — it's a pedagogical/exploration tool. Use the Python engine for real numbers.

## Next Priority

**Measurement basis toggle** (v4.2) — adding X/Y basis to the 2-qubit view so Cluster states show non-zero correlators. This maps to the framework's highest-priority experiment. See README.md roadmap for details.
