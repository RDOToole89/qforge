# Bloch Sphere CPTP Visualizer

Interactive 3D visualization of quantum noise channels, probe state sensitivity, and structured decoherence — built to work with the Qiskit Experiment Framework's research data.

## What This Component Does

This is a **research visualization tool** that makes abstract quantum concepts tangible:

- **See** how CPTP (Completely Positive, Trace-Preserving) maps deform the Bloch sphere in real-time
- **Compare** how different probe states respond to the same noise channel
- **Understand** why GHZ detects correlated noise while Cluster states are blind in Z-basis
- **Explore** 2-qubit correlator space to see topology-dependent noise fingerprints
- **Load** experimental data from the framework's analysis pipeline

The core loop: **state x channel x topology -> visual + quantitative output**, all configurable.

---

## Architecture

```
src/features/bloch-sphere/
  types.ts                  # All TypeScript interfaces
  config.ts                 # DEFAULT_CONFIG (5 states, 5 channels, 3 topologies)
  math.ts                   # Three.js helpers, point generation, Bloch map compilation
  index.ts                  # Barrel export
  BlochSphereScreen.tsx     # Main composition component (use dom)
  components/
    BlochScene.tsx          # Single-qubit 3D Bloch sphere (Three.js, use dom)
    TwoQubitScene.tsx       # 2-qubit correlator space visualization (Three.js, use dom)
    PTMHeatmap.tsx          # 4x4 Pauli Transfer Matrix heatmap
    CorrelatorBars.tsx      # Delta-correlator bar chart (clean vs noisy)
    FingerprintViewer.tsx   # Experimental fingerprint norms + cosine similarity
    ConfigEditor.tsx        # State/channel/topology selector with error rate slider
```

### Platform Strategy

The entire screen is a `'use dom'` component. On web it renders natively; on React Native it runs inside an automatic webview via Expo's DOM component system. This is the right tradeoff — Three.js requires WebGL, and the visualization is inherently a web-first experience.

---

## Features (v4)

### 1-Qubit View: Bloch Sphere Deformation

- **5 probe states** preconfigured: GHZ, Bell, W, Cluster, Superposition
  - Each with Bloch vector, Z-basis signal strength badge, and research insight text
  - States marked as Z-uniform show the Pauli invariance warning
- **5 noise channels**: Depolarizing, Amplitude Damping, Dephasing, Bit Flip, Phase Flip
  - Each with Kraus operators, Bloch map formula, and geometric description
- **Real-time deformation**: Drag the error rate slider and watch the point cloud contract
  - Blue cloud = original state, Orange cloud = after channel application
  - "Full Sphere" mode shows the entire Bloch ball; "State View" clusters points around the state's Bloch vector
- **Animate button**: Cycles error rate 0 -> 1 -> 0 to show the full decoherence trajectory
- **Drag to rotate** the 3D scene

### PTM View: Pauli Transfer Matrix

- 4x4 heatmap showing how each Pauli component (I, X, Y, Z) maps through the channel
- Color-coded: orange = positive transfer, blue = negative, blank = zero
- Updates in real-time with the error rate slider
- Annotates when a state is Z-uniform (Z-row entries produce no measurable signal)

### 2-Qubit View: Correlator Space

- Axes: ZI, IZ, ZZ (the Z-basis correlators)
- **3 noise topologies**: Chain (correlated), Star (independent), Correlated ZZ
- Shows how different topologies deform the correlator signature differently
- **Delta-correlator bars**: Quantitative readout of how much each correlator shifts
- Switch between probe states to see why GHZ shows strong Delta-ZZ while Cluster shows zero

### Data View: Experimental Fingerprints

- Load fingerprint vectors (15-dimensional for 6 qubits) from the framework's analysis pipeline
- Displays fingerprint norms as bar charts
- Computes and displays cosine similarity matrix between all loaded fingerprints
- Color-coded by noise topology

### Config Editor

- Edit probe states, channels, topologies, and experimental data as JSON
- Import/export full configuration files
- Reset to defaults

---

## Connection to Research Findings

This visualizer directly illustrates the framework's key results:

| Finding | How to See It |
|---------|---------------|
| **GHZ detects correlated noise** | Select GHZ in 2-qubit view, watch Delta-ZZ grow with error rate under Chain topology |
| **Cluster is Z-basis blind** | Select Cluster — correlator bars stay at zero regardless of noise |
| **Pauli invariance theorem** | Cluster and Superposition show "Z-basis blind" badge; dephasing channel preserves Z component |
| **Fingerprints scale not shift** | Load multiple fingerprint conditions in Data tab, check cosine similarity matrix |
| **Topology matching** | Compare Chain vs Star topology in 2-qubit view with GHZ state |
| **Amplitude damping asymmetry** | Switch to Amplitude Damping in 1-qubit view — sphere shifts toward |0>, not symmetric shrinkage |

---

## Preconfigured Probe States

| State | Bloch Vector | ZZ Correlator | Z-Basis Signal | Key Property |
|-------|-------------|---------------|----------------|-------------|
| **GHZ** | Origin (mixed) | +1.0 | Strong | Maximal ZZ correlation makes Z-basis noise visible |
| **Bell** | Origin (mixed) | +1.0 | Strong | 2-qubit GHZ, same correlator structure |
| **W** | (0, 0, 0.33) | -0.11 | Weak | Non-uniform Z-marginals but weak correlations |
| **Cluster** | Origin (mixed) | 0.0 | Zero | Correlations live in XZ/ZX stabilizer sector, invisible to Z |
| **Superposition** | (1, 0, 0) | 0.0 | Zero | Product state, no correlations at all |

---

## Data Integration

### Loading Experimental Data

The Data tab accepts fingerprint entries in this format:

```json
[
  {
    "label": "GHZ chain p=0.1 cs=0.3",
    "noiseStrength": 0.1,
    "topology": "chain",
    "fingerprint": [0.012, 0.008, 0.015, ...]
  }
]
```

The `fingerprint` array contains the flattened upper-triangular delta-covariance vector (15 values for 6 qubits, corresponding to the 15 unique qubit pairs).

### Generating Fingerprints from the Framework

```python
# In the Python framework
from src.core.analysis.core.correlations import compute_fingerprint_vector

# From experiment results
fingerprint = compute_fingerprint_vector(
    counts_noisy=noisy_counts,
    counts_baseline=baseline_counts,
    num_qubits=6
)
# fingerprint is a 15-element list ready to paste into the visualizer config
```

---

## Roadmap

### v4.1 — Real Data Pipeline (Next)

- [ ] Load analysis.json files directly from the framework's results directory
- [ ] Auto-extract fingerprint vectors from stored experiment results
- [ ] Batch import: point at a results folder and load all conditions at once

### v4.2 — Measurement Basis Toggle (High Priority)

This maps directly to the framework's highest-priority experiment (X-basis measurement for Cluster states).

- [ ] Add X/Y/Z basis selector to the 2-qubit correlator view
- [ ] When X-basis is selected, show XZ/ZX correlators instead of ZI/IZ/ZZ
- [ ] Cluster state should "wake up" (show non-zero correlators) in X-basis
- [ ] Side-by-side Z-basis vs X-basis comparison mode

This is the **big missing piece** — but better to add after confirming Z-basis data loads cleanly.

### v4.3 — Fingerprint Atlas

- [ ] PCA projection of loaded fingerprints in PC1/PC2 space
- [ ] Color-code points by noise topology (chain=orange, star=purple)
- [ ] Visually confirm the "scaling not shifting" finding (points along a line, not a cloud)
- [ ] Hover to see condition labels

### v4.4 — Diff Mode

- [ ] Pick two states (e.g. GHZ vs Cluster) and see fingerprint responses side-by-side under identical noise
- [ ] Direct visual of Finding 1 (state sensitivity ordering)
- [ ] Overlay delta-correlator bars for comparison

### v4.5 — Live Experiment Integration

- [ ] Connect to the Python engine API (via the existing FastAPI server)
- [ ] Run experiments from the visualizer and see results update in real-time
- [ ] Parameter sweep visualization: animate through error rates with live data

### Explicitly Not Planned

- Full state tomography visualization (not useful at this stage)
- Multi-qubit PTMs (16x16 or 64x64 matrices are unreadable as heatmaps)
- Hardware noise model import (rabbit hole that doesn't serve current research questions)

---

## Development

### Running Locally

```bash
cd apps/client
npx expo start --web
```

Navigate to the "Visualizer" tab.

### Key Dependencies

- `three` — WebGL 3D rendering
- `@types/three` — TypeScript definitions
- Expo SDK 54 with `use dom` for native webview rendering

### Adding a New Probe State

1. Add the state definition to `config.ts` → `DEFAULT_CONFIG.states`
2. Provide: `name`, `desc`, `bloch` vector, `correlators` signature, `color`, `zBasisSignal`, `insight`, `uniform`
3. The state automatically appears in the sidebar selector

### Adding a New Channel

1. Add the channel definition to `config.ts` → `DEFAULT_CONFIG.channels`
2. Provide: `name`, `desc`, `formula`, `blochMap` (string expressions using rx, ry, rz, p, sqrt), `kraus`, `geometry`, `insight`
3. The Bloch map expressions are compiled at runtime into executable functions

### Adding a New Topology

1. Add to `config.ts` → `DEFAULT_CONFIG.topologies`
2. Provide: `name`, `desc`, `corrGrowXX/YY/ZZ`, `singleQubitDecay`, optional `preserveZ`
3. Appears in the 2-qubit topology selector
