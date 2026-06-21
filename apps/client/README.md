# Quantum Experiment Visualizer

A React Native (Expo) app providing interactive visualization and exploration of quantum experiments. Runs on web (primary), iOS, and Android via Expo's universal platform.

---

## Quick Start

```bash
cd apps/client
npm install
npm run web        # Launch in browser (recommended)
npm run ios        # iOS simulator
npm run android    # Android emulator
```

To connect to the Python API server (required for experiment mode):

```bash
# From the project root, in a separate terminal (requires uv: https://docs.astral.sh/uv/):
uv run uvicorn apps.api.main:app --reload --port 8000
```

---

## Features

### Bloch Sphere Visualizer (`src/features/bloch-sphere/`)

Interactive 3D visualization of CPTP (noise channel) maps on the Bloch sphere. Two operating modes:

- **Built-in mode**: 5 hardcoded noise channels, 5 probe states, 3 topologies. Drag to rotate, adjust error rate with a slider, animate decoherence. Educational: see how depolarizing noise shrinks the Bloch ball while amplitude damping pulls states toward |0>.
- **Experiment mode**: Load real experiment results from the Python engine. Per-qubit Bloch vectors from partial traces, correlator bars, MI heatmaps. Run decoherence sweeps with animated interpolation.

Four visualization tabs: 1-Qubit (Bloch sphere), 2-Qubit (correlator space), PTM (Pauli Transfer Matrix heatmap), Data (metrics + fingerprints).

See `src/features/bloch-sphere/README.md` for full architecture and component details.

### Quantum Glossary (`src/features/quantum-glossary/`)

Searchable reference of 100+ quantum computing terms across 16 categories:

- Fundamentals, States, Gates, Entanglement, Measurement
- Noise, Decoherence, Error Correction, Algorithms
- Information Theory, Linear Algebra, Hardware
- Bloch Sphere, Density Matrices, Structured Decoherence

Each term includes: formal definition, intuitive explanation, key equations (with LaTeX rendering), symbol annotations, related term links, and research context.

---

## Tech Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| Expo SDK | 54 | Universal platform |
| React Native | 0.81 | Cross-platform UI |
| React | 19 | Component framework |
| TypeScript | 5.9 | Type safety |
| Three.js | 0.183 | 3D Bloch sphere rendering |
| Expo Router | File-based | Tab navigation |

---

## Project Structure

```
apps/client/
  app/                        Expo Router pages
    _layout.tsx                 Root layout (fonts, theme)
    (tabs)/
      _layout.tsx               Tab navigation layout
      configure.tsx             Experiment configuration form
      results.tsx               Result history and details
      visualizer.tsx            Bloch sphere visualizer (default tab)
      registry.tsx              Experiment program registry
      glossary.tsx              Quantum glossary
  src/
    features/
      bloch-sphere/             3D CPTP visualization (has its own README)
        hooks/                    useBuiltInMode, useExperimentMode, useSweepMode, useDragRotation
        components/               Header, BuiltinSidebar, ExperimentSidebar, DataPanel, BlochScene, ...
      quantum-glossary/         Quantum term reference
        data/                     Term definitions by category (16 files)
        components/               TermCard, SearchBar, CategoryHeader
    components/                 Shared UI components (ExperimentCard, etc.)
    hooks/                      Custom React hooks (useApi, etc.)
    lib/
      api.ts                    Typed API client for Python backend
      types.ts                  TypeScript interfaces matching Pydantic models
    constants/
      Colors.ts                 Theme colors
```

---

## API Endpoints

The app connects to the FastAPI backend at `apps/api/`. Key endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/experiments/registry` | List available experiment programs |
| POST | `/api/experiments/run` | Run an experiment from config |
| GET | `/api/results?limit=N&offset=M` | List stored results |
| GET | `/api/bloch/{filename}` | Get Bloch visualization data for a result |
| POST | `/api/bloch/sweep` | Run a decoherence sweep (multiple error rates) |
