# AGENTS.md — Circuit Builder & Bloch Sphere Playback

Quick reference for AI agents working on this feature.

## What This Is

An interactive quantum circuit builder with real-time Bloch sphere visualization, entanglement analysis (ΔCov, concurrence, 3-tangle), dynamic step-by-step narratives, and a library of 22 preset circuits. Two input modes:

- **Circuit Builder**: drag-and-drop gate placement, live state simulation, animated Bloch sphere playback
- **Direct State**: load ideal state vectors (Bell, GHZ, W, Dicke, cluster) or paste custom amplitudes for instant analysis

## UI Layout

Side-by-side design:

```
┌─────────────────────────────────────────┬──────────────────────┐
│ [Circuit Builder | Direct State] [?Tour]│  BLOCH SPHERE  [⛶]  │
│ ────────────────────────────────────────│                      │
│ Toolbar: Qubits [2v] Presets [v] Export │  Three.js sphere     │
│ Gate Palette: H X Y Z S T √X Rx Ry ... │  with qubit dots     │
│ ────────────────────────────────────────│                      │
│ Circuit Canvas (SVG, drag-and-drop)     │  q0 ● q1 ● q2 ●     │
│ ────────────────────────────────────────│  [ΔCov|Conc|Tangle]? │
│ STATE EVOLUTION                         │  Correlation heatmap  │
│   Step 1: H(q0) [q0] Bell |Φ+⟩         │  or tangle gauge     │
│   |ψ⟩ = 1/√2|00⟩ + 1/√2|11⟩           │  ──────────────────  │
│   Contextual narrative...               │  0 ═══════════════ 2 │
│ MEASUREMENT PROBABILITIES               │  Step 0 / 2          │
│ PRESET INFO (if applicable)             │  ⏮ ⏪ ▶ ⏩           │
└─────────────────────────────────────────┴──────────────────────┘
```

## File Map

```
CircuitBuilderScreen.tsx    Main orchestrator. Side-by-side layout, mode toggle
                            (circuit/direct), preset management, onboarding integration.
                            USE DOM component.

types.ts                    All type definitions: Circuit, Moment, PlacedGate, GateType,
                            SimSnapshot (stateVector as Complex[]), CircuitPreset,
                            NarrativeStep, CircuitAction reducer actions.

styles.ts                   Layout constants (wireSpacing: 56, momentWidth: 72,
                            labelWidth: 52, gateSize: 40), color palette, helper
                            functions (momentX, wireY, canvasWidth, canvasHeight).

hooks/
  useCircuit.ts             Reducer-based circuit state. Actions: ADD_GATE, REMOVE_GATE,
                            MOVE_GATE, SET_PARAMS, SET_CONTROL, SET_NUM_QUBITS, CLEAR,
                            LOAD_PRESET. Returns: circuit, addGate, removeGate, loadPreset, etc.

  useSimulator.ts           Pure state vector simulator. Supports all gate types:
                            H, X, Y, Z, S, T, SX, Rx, Ry, Rz, CNOT, CZ, SWAP, Toffoli.
                            simulateCircuit() returns SimSnapshot[] (one per moment boundary).
                            formatDirac() renders Dirac notation.
                            recognizeState() detects known states from amplitudes + phases:
                            Bell (Φ+/Φ-/Ψ+/Ψ-), GHZ±, W, Dicke, |+⟩/|−⟩/|±i⟩,
                            uniform superposition, product states.

  usePlayback.ts            Playback state machine: play/pause/step/seek/scrub/speed control.
                            Uses requestAnimationFrame for smooth animation.
                            Computes per-qubit BlochDots via stateVectorToBloch(),
                            CorrelationData (ΔCov matrix, concurrence matrix, tangle,
                            per-qubit 1-tangles) at each frame.
                            Two interpolation modes: "direct" (lerp — actual reduced state)
                            and "ideal" (slerp — great circle rotation on surface).
                            Slerp handles edge cases: antipodal vectors, mixed states,
                            near-parallel vectors. Ideal mode holds position when qubits
                            become entangled (doesn't collapse to center).

  useNarrative.ts           Dynamic narrative engine. Generates contextual explanations
                            for each circuit step by analyzing:
                            - Gate type + target qubit Bloch vector before/after
                            - Whether entanglement was created/destroyed
                            - Whether a known state was reached
                            - Whether qubits became maximally mixed
                            Falls back gracefully when preset step text exists.

components/
  CircuitToolbar.tsx         Toolbar: qubit count selector, presets dropdown (remembers selection),
                             export button, clear. activePresetId prop tracks selected preset.
  GatePalette.tsx            Gate buttons (click to select, draggable). Split into single/multi-qubit
                             groups with "2Q"/"3Q" badges and thicker bottom border on multi-qubit gates.
  CircuitCanvas.tsx          SVG circuit rendering. Qubit wires, gate blocks, drag-and-drop placement.
                             Uses ResizeObserver for full-width wires.
                             Invisible HTML overlay divs on placed gates enable native drag-to-reposition.
                             Drop handler distinguishes new gates (gate-type) from moves (gate-move-id).
                             Gates snap to closest qubit wire + moment column at drop position.
  GateBlock.tsx              SVG gate rendering: single-qubit boxes, CNOT cross-circles,
                             CZ dots, SWAP X marks.
                             Selection: marching ants animated border (@keyframes marching-ants),
                             subtle scale(1.08) transform, accent glow background.
                             Full bounding box for multi-qubit gates covers connection lines.
                             Right-click context menu via onContextMenu prop.
  ProbabilityDisplay.tsx     Horizontal bar chart of measurement probabilities.
  CircuitViewer.tsx          Read-only circuit viewer (used in configure tab preview).
  BlochPlaybackPanel.tsx     Right-side panel (resizable 280-700px via drag handle):
                             UnifiedBlochSphere in circuit mode (fills available space,
                             auto-fit camera based on aspect ratio, drag-to-rotate,
                             zoom slider, double-click to open fullscreen modal).
                             "Now playing" gate indicator shows current operation.
                             Actual/Ideal interpolation mode toggle with ? info card.
                             Active qubit dots enlarge + glow, decaying with step progress.
                             Qubit labels flash above active dots during animation.
                             Live Bloch state readout: per-qubit (rx,ry,rz) + purity.
                             Qubit legend, correlation heatmap/tangle, transport controls.
                             Custom pointer-event scrubber with continuous 0-1 progress,
                             step tick marks, snap-to-step on release.
                             Speed selector (0.25x-4x).
                             Fullscreen modal with all controls replicated.
                             Right-click context menu on gates (delete, params, control qubit).
                             Placement feedback popovers (success/error).
                             Gate preview: clicking palette gate shows demo on Bloch sphere.
                             Uses data-onboarding attributes for guided tour targeting.
  CorrelationHeatmap.tsx     Heatmap for ΔCov or concurrence matrices. Color scales:
                             blue-to-red (ΔCov), dark-to-magenta (concurrence).
  OnboardingOverlay.tsx      12-step guided tour with spotlight highlighting (CSS clip-path),
                             auto-loaded Bell State, fullscreen modal walkthrough,
                             pulsing expand button animation, viewport-safe positioning.

data/
  gateLibrary.ts             Gate definitions: name, numQubits, parametric, matrix LaTeX,
                             description, color, label, glossaryTermId, qiskitName.
  circuitPresets.ts          22 circuit presets with steps[] and applications[].
                             Categories: foundational (Bell, GHZ, teleportation, QFT, etc.),
                             exotic (cluster, entanglement swapping, Hardy's paradox),
                             real hardware (QPE, Bernstein-Vazirani, CHSH, bit-flip code, etc.)
  idealStates.ts             16 ideal state vectors for Direct State mode.
                             Bell variants, GHZ/W/Dicke at various qubit counts, cluster state.
                             idealStateToSnapshot() converts to SimSnapshot.
  gatePreviewCircuits.ts     Per-gate demo circuits for palette preview. Each gate has a
                             carefully chosen initial state to maximize visual effect:
                             phase gates start in |+⟩, entangling gates start with
                             superposition on control, SWAP uses visually distinct states.
```

## Key Architectural Patterns

### State Vector Simulation

The simulator tracks the full 2^n complex state vector, applying gate matrices via tensor product structure:

```typescript
// Single-qubit: iterate over pairs differing in target bit
for (let i = 0; i < dim; i++) {
  if (i & targetBit) continue;
  const j = i | targetBit;
  // Apply 2x2 matrix to (sv[i], sv[j])
}

// Multi-qubit (CNOT): flip target when control is 1
for (let i = 0; i < dim; i++) {
  if (!(i & controlBit)) continue;
  // Swap sv[i] and sv[i ^ targetBit]
}
```

MSB qubit convention: qubit 0 is the most significant bit. This matches Qiskit's convention.

### Bloch Vector from State Vector

`stateVectorToBloch()` in `bloch-sphere/math.ts` computes single-qubit reduced density matrix via partial trace, then extracts Pauli expectations:

```
rx = 2 Re(ρ₀₁)     — Tr(ρ σx)
ry = -2 Im(ρ₀₁)    — Tr(ρ σy)
rz = ρ₀₀ - ρ₁₁     — Tr(ρ σz)
```

### Correlation Analysis

Three layers of entanglement analysis, all computed from the state vector:

1. **ΔCov(i,j)** = ⟨ZᵢZⱼ⟩ − ⟨Zᵢ⟩⟨Zⱼ⟩ — connected correlation (classical + quantum)
2. **Concurrence** — Wootters formula from 2-qubit reduced density matrix via ρρ̃ eigenvalues
3. **3-Tangle** — Coffman-Kundu-Wootters: τ₃ = C²(A|BC) − C²(A,B) − C²(A,C)

Key insight: GHZ has τ₃=1, C=0 (genuinely tripartite). W has τ₃=0, C≈2/3 (pairwise only).

### Coordinate Convention

Unified across all Bloch sphere rendering (was inconsistent before unification):

```
blochToThree(rx, ry, rz) → Vector3(rx, rz, ry)
// Three.js X = Bloch X
// Three.js Y = Bloch Z (up)
// Three.js Z = Bloch Y
```

### UnifiedBlochSphere Modes

Single component with discriminated union props (`mode: "glossary" | "visualizer" | "circuit"`):

- **glossary**: auto-rotate, drag-to-spin, click-to-expand, dot glow meshes
- **visualizer**: external rotation, point clouds, channel transform animation
- **circuit**: drag-to-rotate, zoom prop, activeQubits highlighting, stepProgress
  decay, qubit label sprites, ResizeObserver for responsive sizing, auto-fit camera
  based on container aspect ratio (1/√aspect distance factor)

### Playback Architecture

```
useSimulator(circuit) → SimSnapshot[]
                              ↓
usePlayback(snapshots, n, interpMode) → { dots, correlations, progress, ... }
                              ↓
BlochPlaybackPanel → UnifiedBlochSphere(mode="circuit", dots, zoom, activeQubits, stepProgress)
                   → "Now playing" gate indicator (label + color)
                   → Actual/Ideal toggle with ? info
                   → Zoom slider
                   → Live state readout (rx, ry, rz, purity)
                   → CorrelationHeatmap / TangleDisplay
                   → Custom scrubber (continuous 0-1, step ticks, snap on release)
                   → Transport controls (play/pause/step/speed)
```

The playback hook uses `requestAnimationFrame` with refs to avoid re-renders during animation.

### Interpolation Modes

- **Actual (lerp)**: Direct linear path through Bloch ball interior. Shows true reduced state.
  When CNOT entangles, dots honestly fall toward the center.
- **Ideal (slerp)**: Spherical interpolation on sphere surface. Shows gate rotation geometry.
  When qubits become entangled (mixed), holds the last pure-state position instead of
  collapsing to center. Renormalizes to surface. Falls back to lerp for mixed states,
  handles antipodal vectors via perpendicular great circle detour.

### Active Qubit Highlighting

During playback, qubits being operated on in the current step:
- Dot scales up (1.35x → 1.0x, decaying with step progress `t`)
- Glow opacity increases (40% → 20%, same decay)
- Label sprite ("q0") appears above dot, fades out as step progresses
- "Now playing" bar shows gate operation (e.g., "CX(q0,q1)") in gate color

### Gate Preview

When clicking a gate in the palette (not placed yet):
- A demo circuit from `gatePreviewCircuits.ts` is simulated
- The Bloch panel switches to show the preview
- Auto-plays the animation
- Each gate's demo uses a carefully chosen initial state for max visual effect
- Deactivates when gate is deselected or a preset is loaded

### Drag-to-Reposition Placed Gates

- Invisible HTML `<div>` overlays positioned on each gate in the canvas
- Natively `draggable` — click-and-hold initiates HTML5 drag
- `gate-move-id` in dataTransfer distinguishes moves from new placements
- Drop handler computes closest qubit wire + moment column
- `MOVE_GATE` reducer preserves multi-qubit offset pattern
- Marching ants selection visible during drag, deselects on drop

### Narrative Engine

`useNarrative` generates contextual explanations by analyzing:
- The gate type and its effect on the specific qubit state (e.g., "H on |0⟩ → creates superposition" vs "H on |+⟩ → maps back to pole")
- Whether the control qubit is in superposition (→ entanglement) or a definite state (→ classical conditional)
- Whether entanglement count changed between snapshots
- Whether a recognized state was reached

Priority: preset `steps[]` text > dynamic narrative > nothing.

### Auto-Detection of Known States

`recognizeState()` checks both amplitudes AND relative phases:
- Distinguishes Bell |Φ+⟩ from |Φ-⟩ (positive vs negative relative phase)
- Detects W states by checking single-excitation subspace occupancy
- Detects Dicke states D(n,k) by Hamming weight analysis
- Checks product state separability for 2 qubits via amplitude factorization

When a manually-built circuit produces a recognized state, the matching preset info panel auto-appears with a green "State recognized" banner. Only triggers for circuits ≤6 moments.

## Onboarding Flow

12-step guided tour using spotlight highlighting:

| Step | Target | Action | Position |
|------|--------|--------|----------|
| 1 | (center) | Loads Bell preset | center |
| 2 | mode-toggle | | below |
| 3 | toolbar | | below |
| 4 | palette | | below |
| 5 | canvas | | below |
| 6 | bloch-sphere | Resets playback | left |
| 7 | expand-bloch | Opens fullscreen | left, pulsing glow + pointer |
| 8 | modal-sphere | | beside modal |
| 9 | modal-controls | | beside modal |
| 10 | modal-correlation | Closes fullscreen | beside modal |
| 11 | state-evolution | | below |
| 12 | (center) | | center |

Implementation:
- `data-onboarding="name"` attributes on UI elements for targeting
- CSS `clip-path` polygon creates spotlight cutout in dark overlay
- Modal steps render overlay behind modal (z-index 9998), tooltip at z-index 10001
- Tooltip positions clamped to viewport with tab bar awareness (60px bottom margin)
- Expand button step uses `@keyframes` pulse animation + pointer emoji
- `OnboardingActions` interface lets the overlay trigger: loadBellPreset, playBloch, resetBloch, openFullscreen, closeFullscreen
- localStorage persistence (`circuit-builder-onboarding-v2`)
- "? Tour" button to re-trigger

## How to Extend

### Add a gate type
1. Add to `GateType` union in `types.ts`
2. Add gate matrix to `useSimulator.ts` (getGateMatrix switch)
3. Add gate definition to `data/gateLibrary.ts`
4. Add rendering logic to `GateBlock.tsx` if it's a new visual pattern

### Add a circuit preset
Add to `data/circuitPresets.ts`:
```typescript
{
  id: "my_circuit",
  name: "My Circuit",
  description: "What it does.",
  learns: "Concepts taught",
  steps: ["Step 1 explanation", "Step 2 explanation"],  // optional
  applications: ["Real-world use 1", "Real-world use 2"],  // optional
  circuit: {
    numQubits: 2,
    moments: [
      { gates: [{ id: "p1", gateType: "H", qubits: [0] }] },
      { gates: [{ id: "p2", gateType: "CNOT", qubits: [0, 1] }] },
    ],
  },
}
```

### Add an ideal state
Add to `data/idealStates.ts`:
```typescript
{
  id: "my_state", name: "|ψ⟩", numQubits: 2,
  description: "What this state is.",
  amplitudes: () => [[0.707, 0], [0, 0], [0, 0], [0.707, 0]],  // Complex[]
}
```

### Add a recognized state
Add detection logic to `recognizeState()` in `useSimulator.ts`. Check amplitudes + phases. Return a human-readable name string. Optionally map it to a preset ID in `CircuitBuilderScreen`'s `stateToPreset` record.

### Add an onboarding step
1. Add a `data-onboarding="my-target"` attribute to the UI element
2. Add the step to the `STEPS` array in `OnboardingOverlay.tsx`
3. If the step needs an action, add it to `OnboardingActions` interface and implement in `CircuitBuilderScreen`

## What NOT to Do

- Do NOT import React Native components in `'use dom'` files
- Do NOT rebuild the Three.js scene on every dot position change — use refs
- Do NOT add noise simulation to the frontend simulator — that's the Python engine's job
- Do NOT hardcode tooltip positions — always use `data-onboarding` + `getBoundingClientRect`
- Do NOT remove the Givens rotation W state circuit — it was carefully verified to produce exact W state (τ₃ = 0)
- Do NOT merge the three correlation modes into one view — ΔCov, concurrence, and tangle measure fundamentally different things
- Do NOT skip the viewport clamping in tooltip positioning — tooltips must never go under the tab bar or off-screen
- Do NOT use `<input type="range">` for the playback scrubber — it doesn't work reliably in `'use dom'` webviews. Use the custom pointer-event scrubber.
- Do NOT use `setPointerCapture` on SVG `<g>` elements — it captures events away from the parent SVG. Use HTML overlay divs for drag interactions.
- Do NOT set `dropEffect` explicitly in `handleDragOver` — let the browser match it to `effectAllowed`. Forcing it breaks palette drag.
- Do NOT use CSS transitions on scrubber elements during playback — causes the thumb to jump instead of tracking smoothly
- Do NOT use slerp when either Bloch vector length < 0.3 — falls back to lerp to prevent normalization flicker on mixed states
- Do NOT slerp antipodal vectors directly — use perpendicular great circle detour (cross product method)
