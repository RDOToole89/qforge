# Bloch Sphere CPTP Visualizer

Interactive 3D visualization of quantum noise channels, probe state sensitivity, and structured decoherence — built to work with the QForge's research data.

## What This Component Does

This is a **research visualization tool** that makes abstract quantum concepts tangible:

- **See** how CPTP (Completely Positive, Trace-Preserving) maps deform the Bloch sphere in real-time
- **Compare** how different probe states respond to the same noise channel
- **Understand** why GHZ detects correlated noise while Cluster states are blind in Z-basis
- **Explore** 2-qubit correlator space to see topology-dependent noise fingerprints
- **Load** experimental data from the framework's analysis pipeline
- **Visualize** real experiment results with per-qubit Bloch vectors from partial traces
- **Animate** decoherence sweeps — watch Bloch vectors shrink as error rate increases

Two operating modes:
- **Built-in mode**: Hardcoded educational examples (5 states, 5 channels, 3 topologies)
- **Experiment mode**: Live data from the Python experiment pipeline via the `/api/bloch` endpoints

---

## Architecture

```
src/features/bloch-sphere/
  types.ts                  # All TypeScript interfaces (inc. ExperimentalDataEntry)
  config.ts                 # DEFAULT_CONFIG (5 states, 5 channels, 3 topologies)
  math.ts                   # Three.js helpers, point generation, Bloch map compilation
  styles.ts                 # Shared style constants (LS, bdr, cS, cT)
  experimentAdapter.ts      # Pure functions: BlochVisualizerData → component prop shapes
  index.ts                  # Barrel export
  BlochSphereScreen.tsx     # Main orchestrator (~230 lines): composes hooks + components

  hooks/
    useBuiltInMode.ts       # Built-in mode state: config, channel, strength, animation
    useExperimentMode.ts    # Experiment mode state: result selection, Bloch data, derived memos
    useSweepMode.ts         # Sweep state: config form, interpolation, sweep animation
    useDragRotation.ts      # Pointer drag rotation handling

  components/
    Header.tsx              # Mode toggle (builtin/experiment) + tab buttons
    BuiltinSidebar.tsx      # Built-in mode left panel: state/channel/topology selectors
    ExperimentSidebar.tsx   # Experiment mode left panel: result picker, sweep controls
    DataPanel.tsx           # Right sidebar: state info, metrics, fingerprints, PTM
    BlochScene.tsx          # Single-qubit 3D Bloch sphere with pole dots, great circles
    TwoQubitScene.tsx       # 2-qubit correlator space with multi-topology clouds
    MIMatrixHeatmap.tsx     # Mutual information matrix heatmap
    PTMHeatmap.tsx          # 4x4 Pauli Transfer Matrix heatmap (orange/blue)
    CorrelatorBars.tsx      # Delta-correlator bar chart with center-line style
    FingerprintViewer.tsx   # Experimental fingerprint norms + cosine similarity matrix
    ConfigEditor.tsx        # Modal JSON editor with import/export/reset
    ReducedStateExplainer.tsx  # Educational panel for experiment mode contexts
```

### Platform Strategy

The entire screen is a `'use dom'` component. On web it renders natively; on React Native it runs inside an automatic webview via Expo's DOM component system. This is the right tradeoff — Three.js requires WebGL, and the visualization is inherently a web-first experience.

### UI Design

The interface uses a **dark hacker aesthetic** (#08090e background, #ff9933 orange accents, IBM Plex Sans font) with a tab-based layout:

- **Header**: Title + tab buttons (1-Qubit, 2-Qubit, PTM, Data) + Config button
- **Left sidebar**: Button-style selectors with colored dots and Z-basis badges. Shows state/channel/topology selectors contextually based on active tab. Includes strength slider, animate button, and view mode toggle.
- **Center**: Full-screen 3D scene (drag to rotate). Shows BlochScene or TwoQubitScene depending on tab.
- **Right sidebar**: Context-dependent info panels — Kraus operators, Bloch map formulas, PTM heatmap, delta-correlator bars, fingerprint viewer, research insights.
- **Config modal**: Full JSON editor for states, channels, topologies, and experimental data.

---

## Features (v5)

### Experiment Mode

Toggle between **Built-in** and **Experiment** mode via the header toggle.

**Single result viewing:**
- Select a stored experiment result from the dropdown
- Per-qubit Bloch vectors computed via partial traces of the density matrix
- "All" view shows all qubit vectors on a single sphere with per-qubit colors
- Correlator bars show actual measured Pauli expectation values
- Mutual information matrix heatmap for qubit-pair entanglement structure
- Metrics from the analysis pipeline (fidelity, asymmetry index, etc.)

**Decoherence sweep animation:**
- Configure state type, qubit count, and noise type
- Runs experiments at multiple error rates via `POST /api/bloch/sweep`
- Scrub through error rates with a slider or auto-animate
- Bloch vectors smoothly interpolate between snapshots
- Watch decoherence progression: pure states shrink toward the origin as noise increases

**Educational context:**
- `ReducedStateExplainer` panel explains reduced density matrices, partial traces, and what purity means
- Diagonal estimate warning when only Z-basis measurements are available
- Multi-qubit insight explaining non-uniform decoherence across the register

### 1-Qubit View: Bloch Sphere Deformation

- **5 probe states** preconfigured: GHZ, Bell, W, Cluster, Superposition
  - Each with Bloch vector, Z-basis signal strength badge, and research insight text
  - States marked as Z-uniform show the Pauli invariance warning
- **5 noise channels**: Depolarizing, Amplitude Damping, Dephasing, Bit Flip, Phase Flip
  - Each with Kraus operators, Bloch map formula, and geometric description
- **Real-time deformation**: Drag the error rate slider and watch the point cloud contract
  - Blue cloud = original state, Orange cloud = after channel application
  - "Full Sphere" mode shows the entire Bloch ball; "State View" clusters points around the state's Bloch vector
  - Toggle original/transformed clouds independently
- **Animate button**: Cycles error rate 0 -> 1 -> 0 to show the full decoherence trajectory
- **Drag to rotate** the 3D scene manually
- **Sphere details**: Wireframe, great circles, pole dots, state Bloch vector arrow

### PTM View: Pauli Transfer Matrix

- 4x4 heatmap showing how each Pauli component (I, X, Y, Z) maps through the channel
- Color-coded: orange = positive transfer, blue = negative, blank = zero
- Axis labels colored per Pauli operator
- Updates in real-time with the error rate slider
- Annotates when a state is Z-uniform (Z-row entries produce no measurable signal)

### 2-Qubit View: Correlator Space

- Axes: ZI, IZ, ZZ (the Z-basis correlators)
- **3 noise topologies**: Chain (correlated), Star (independent), Correlated ZZ
- Each topology renders as a distinctly colored point cloud
- **"All" mode**: Shows all topologies simultaneously for comparison
- Shows how different topologies deform the correlator signature differently
- **Delta-correlator bars**: Quantitative readout of how much each correlator shifts
- Switch between probe states to see why GHZ shows strong Delta-ZZ while Cluster shows zero

### Data View: Experimental Fingerprints

- Load fingerprint vectors (15-dimensional for 6 qubits) from the framework's analysis pipeline
- Displays fingerprint norms as bar charts (color-coded by topology)
- Computes and displays cosine similarity matrix between all loaded fingerprints
- Up to 12 entries supported in the similarity matrix view

### Config Editor (Modal)

- Opens as a full-screen overlay via the Config button
- Tabs: States, Channels, Exp. Data, Topologies
- Edit any section as raw JSON
- Import/export full configuration files
- Reset to defaults
- Click outside to dismiss

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

Open Config modal -> Exp. Data tab. The format:

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

## Backend API

The experiment mode connects to two endpoints on the FastAPI server:

### `GET /api/bloch/{filename:path}`

Transforms a stored experiment result into `BlochVisualizerData`. The filename is the path relative to `results/` (e.g., `2026-03-07/GHZ_3q_depolarizing/analysis.json`). The backend computes partial traces, Bloch vectors, correlators, and mutual information using NumPy.

### `POST /api/bloch/sweep`

Runs experiments at multiple error rates and returns an array of `BlochVisualizerData` snapshots. Request body (`BlochSweepRequest`):

```json
{
  "state_type": "GHZ",
  "num_qubits": 3,
  "noise_type": "depolarizing",
  "error_rates": [0, 0.02, 0.05, 0.1, 0.2, 0.3],
  "sim_mode": "density_matrix",
  "shots": 4096,
  "rng_seed": 42
}
```

Backend source: `apps/api/routes/bloch.py`

---

## Roadmap

### v5.1 — Measurement Basis Toggle (High Priority)

This maps directly to the framework's highest-priority experiment (X-basis measurement for Cluster states).

- [ ] Add X/Y/Z basis selector to the 2-qubit correlator view
- [ ] When X-basis is selected, show XZ/ZX correlators instead of ZI/IZ/ZZ
- [ ] Cluster state should "wake up" (show non-zero correlators) in X-basis
- [ ] Side-by-side Z-basis vs X-basis comparison mode

### v5.2 — Fingerprint Atlas

- [ ] PCA projection of loaded fingerprints in PC1/PC2 space
- [ ] Color-code points by noise topology (chain=orange, star=purple)
- [ ] Visually confirm the "scaling not shifting" finding (points along a line, not a cloud)
- [ ] Hover to see condition labels

### v5.3 — Diff Mode

- [ ] Pick two states (e.g. GHZ vs Cluster) and see fingerprint responses side-by-side under identical noise
- [ ] Direct visual of Finding 1 (state sensitivity ordering)
- [ ] Overlay delta-correlator bars for comparison

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
- Volta pins Node.js to 20.18.1 (required for Expo SDK 54)

### Adding a New Probe State

1. Add the state definition to `config.ts` -> `DEFAULT_CONFIG.states`
2. Provide: `name`, `desc`, `bloch` vector, `correlators` signature, `color`, `zBasisSignal`, `insight`, `uniform`
3. The state automatically appears in the sidebar selector

### Adding a New Channel

1. Add the channel definition to `config.ts` -> `DEFAULT_CONFIG.channels`
2. Provide: `name`, `desc`, `formula`, `blochMap` (string expressions using rx, ry, rz, p, sqrt), `kraus`, `geometry`, `insight`
3. The Bloch map expressions are compiled at runtime into executable functions

### Adding a New Topology

1. Add to `config.ts` -> `DEFAULT_CONFIG.topologies`
2. Provide: `name`, `desc`, `corrGrowXX/YY/ZZ`, `singleQubitDecay`, optional `preserveZ`
3. Appears in the 2-qubit topology selector
