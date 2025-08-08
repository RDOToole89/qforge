## Engine‑First Refactor Plan (V1 Hardening & Web‑Ready)

### Objectives

- Decouple core execution from the CLI; make the engine a clean importable library.
- Stabilize data models (config, result, provenance) and storage contracts.
- Keep a thin, reliable CLI adapter now; enable an easy web adapter later.
- Preserve working behavior while reducing complexity and global state.

### Non‑Goals (this phase)

- No feature expansion; simplify what exists.
- No full rewrite; incremental extraction and cleanup.
- No new visualization features (beyond wiring to the new engine).

### Principles

- Single responsibility per module; avoid god‑objects.
- Explicit dependencies: pass context instead of reading globals.
- Validated boundaries: configs/results are validated at adapter boundaries.
- Deterministic outputs and reproducible runs (seeds, config hash).
- Backward‑compatible paths for current presets and headless commands.

---

## Target Architecture

### Layers & Responsibilities

- Engine (pure core)
  - API: `run(config) -> ExperimentResult`, `sweep(manifest) -> list[ExperimentResult]`.
  - Orchestrates state prep → noise → transpile → simulate.
  - Emits structured events via an event bus interface.
  - Delegates persistence to a storage interface (for results/artifacts).
- Models
  - `ExperimentConfig`, `ExperimentResult`, `Provenance`, `ArtifactRef` (pydantic/dataclasses).
  - JSON schema parity maintained; validation centralized.
- Storage
  - Result writer with deterministic filenames; SaveManager consolidated here.
  - Pluggable target (local FS now; later object storage).
- Adapters
  - CLI (interactive + headless): parse → validate → call Engine → display/save.
  - Web (future FastAPI/SSE): same engine, same events, different transport.
- Plugins
  - State preparation, noise models, and viz backends behind simple interfaces.

### Proposed Module Layout

```
src/
  engine/
    api.py                 # run(config)->ExperimentResult, sweep(manifest)->list[ExperimentResult]
    models.py              # Pydantic models: ExperimentConfig, SweepManifest, ExperimentResult, Provenance, ArtifactRef
    context.py             # AppContext (paths, viz backend, logging mode)
    events.py              # Event bus interfaces + event types
    storage.py             # Storage interface + LocalStorage impl (path policy, writes, artifact registry)
    runner.py              # Thin orchestrator using core (state->noise->transpile->simulate)
    hashing.py             # Canonicalization + config hash
    upgrader.py            # Back/forward compatibility loaders

  core/
    __init__.py
    qiskit_integration/
      __init__.py
      transpile.py         # transpilation wrapper, seed, time capture
      simulate.py          # qasm/statevector/density methods, backend options
      backends.py          # simulator info discovery
    state_prep/
      __init__.py
      base.py              # protocol for state preparation
      ghz.py
      w_state.py
      bell.py
      cluster.py
      custom.py
      factory.py           # maps config -> concrete state preparer
      state_constants.py
    noise/
      __init__.py
      base.py              # protocol for noise channels/models
      depolarizing.py
      amplitude_damping.py
      phase_damping.py
      bit_flip.py
      phase_flip.py
      thermal_relaxation.py
      factory.py           # maps config -> noise model
      validators.py        # physics constraints (CPTP, T2 ≤ 2*T1, bounds)
    analysis/
      __init__.py
      metrics/
        __init__.py
        entropy.py         # Shannon/normalized
        distance.py        # TVD, KL, Fubini-Study, etc.
        correlations.py
        information_theory.py
      dynamics/
        __init__.py
        decoherence.py
        transitions.py
        clustering.py
      symmetry/
        __init__.py
        symmetry.py
    research/
      __init__.py
      handler.py           # derive metrics from raw result, assemble ExperimentResult (no saving)

  visualization/
    __init__.py
    adapters/
      __init__.py
      base.py              # VisualizationAdapter protocol, VizKind enum
      matplotlib_adapter.py
      plotly_adapter.py
      webjson_adapter.py   # optional; JSON payloads for web
    service.py             # VisualizationService (adapter registry/orchestration)
    report/
      __init__.py
      renderer.py          # Markdown/HTML report generation
      templates/
        report_template.html

  experiments/
    __init__.py
    registry.py            # central registry of presets (metadata + config builders)
    presets/
      __init__.py
      beginner.py
      intermediate.py
      advanced.py
      research.py
      ghz_structured_decoherence.py

  cli/
    __init__.py
    headless.py            # argparse subcommands: run/sweep/viz/report
    interactive.py         # thin interactive menus; calls engine.api + visualization.service
    display.py
    help.py

  config/
    __init__.py
    settings.py            # default paths, default viz backend, etc. (read into AppContext)
    profiles.py            # save/load/apply profiles -> AppContext
    params.py              # adapter-level input normalization (uses engine.models for validation)

  utils/
    __init__.py
    logger.py              # setup + structured formatting
    input_handler.py
    messages.py
    glossary.py
    path_utils.py
    json_io.py
    tty.py
```

---

## Data Models (first‑class)

- ExperimentConfig
  - num_qubits, state_type, sim_mode, shots, noise_enabled, noise_type, error_rate, rng_seed, extra_params
- ExperimentResult
  - raw (counts/statevector/density), metrics, artifacts, config_hash, timestamp
- Provenance
  - versions, host_info, git_sha, simulator_info, transpilation_summary, rng_seed
- ArtifactRef
  - kind, path, metadata

Validation: pydantic models mirroring `schemas/*.json`.

---

## Incremental Roadmap

### Phase 0: Hygiene & Freeze (1 day)

- Create `engine/api.py`, `engine/models.py`, `engine/context.py` skeletons.
- Keep all behavior intact; no deletions yet.
- Add smoke API tests for `engine.api.run` using current runner under the hood.

### Phase 1: Engine Facade (1–2 days)

- Wrap `ExperimentRunner` and `ResearchExperimentHandler` in `engine.api.run`.
- Introduce `AppContext` (logging/save dirs/viz backend) and pass explicitly.
- Move config validation to `engine.models` (pydantic) at the facade.
- CLI calls engine.api; headless flags remain as‑is.

### Phase 2: Storage Split (1–2 days)

- Move filename and save logic from `research_handler` + `visualization.save_manager` into `engine.storage`.
- Unify results/artifact saving under one storage API.
- Keep file layout and names stable.

### Phase 3: Event Bus (1 day)

- Define event types (run*start, run_progress, run_end, sweep*\*).
- Adapter: CLI subscribes to events to render progress/JSON stream.

### Phase 4: CLI Simplification (1–2 days)

- Interactive: presets + import config/custom file only.
- Move advanced custom sources (builder/OpenQASM) to headless configs.
- Clean hotkeys and validation; keep menus shallow.

---

## Cleanup Plan (Safe by Default)

- Do not delete tests. Instead:
  - Mark legacy CLI tests as `@pytest.mark.legacy_cli` and exclude by default.
  - Or move to `tests_legacy/` and run separately in CI.
- Remove generated artifacts from version control:
  - Purge `logs/*` (keep `.gitkeep`), `results/*` (keep dir structure).
  - Keep a few golden sample results if they are used in examples/tests.
- Deprecate `src/config/quick_experiments.py` (replace via presets/engine API).

Suggested commands (pending approval):

```
rm -rf logs/* results/*
mkdir -p logs results/structured_decoherence results/parameter_sweeps results/visualizations
touch logs/.gitkeep results/.gitkeep
```

---

## Backward Compatibility

- Presets: callable unchanged; CLI continues to expose current presets.
- Headless: `run --preset`, `run --config`, `sweep --manifest`, `report --from` remain, but now call `engine.api`.
- Results schema: fields preserved; provenance filled by engine.

---

## Testing Strategy

- Keep current test suite as a guardrail.
- Add tests:
  - `tests/engine/test_api.py`: run() returns stable metrics and artifacts.
  - `tests/engine/test_storage.py`: deterministic paths, artifact writes.
  - `tests/engine/test_models.py`: pydantic validation paths.
- Mark brittle interactive tests as legacy; focus on engine unit tests.

---

## Risks & Mitigations

- Risk: Breaking CLI flows during extraction → Mitigation: adapter shims and parallel tests.
- Risk: Hidden globals (settings/save manager) → Mitigation: `AppContext` threading and gradual removal.
- Risk: Over‑refactor → Mitigation: ship each phase green (tests + headless smoke).

---

## Acceptance Criteria

- `engine.api.run` and `engine.api.sweep` are the only entry points used by CLI.
- Results and reports identical to pre‑refactor for the same configs.
- No direct core access to global settings; context passed explicitly.
- Storage provides deterministic file paths; artifacts listed in results.

---

## Timeline (estimate)

- Phases 0–1: 2–3 days
- Phase 2: 1–2 days
- Phase 3: 1 day
- Phase 4: 1–2 days

---

## Next Actions

1. Approve cleanup approach (purge artifacts; keep tests, mark legacy where needed).
2. Implement Phase 0 skeleton and smoke tests.
3. Migrate CLI calls to `engine.api` behind a feature flag; flip default when green.

---

## Visualization Adapters (Decoupled from Engine)

### Goals

- Engine is visualization-agnostic (no imports of plotting libs).
- Adapters consume stable result/model contracts and produce artifacts.
- Pluggable: multiple backends (matplotlib/plotly/web) via registry.

### Design

- Engine outputs `ExperimentResult` with raw data + metrics; it never calls visualization.
- A separate `VisualizationService` coordinates adapters and storage.
- Adapters advertise capabilities (e.g., `histogram`, `density_matrix`, `hypergraph`, `report`).

Proposed modules

```
src/visualization/
  adapters/
    base.py            # VisualizationAdapter protocol + VizKind enum
    matplotlib_adapter.py
    plotly_adapter.py
    webjson_adapter.py # optional; produces JSON payloads for web
  service.py           # VisualizationService (adapter lookup, orchestration)
```

### Interfaces (sketch)

```python
# src/visualization/adapters/base.py
from typing import Protocol, Iterable, Mapping, Any
from enum import Enum
from src.engine.models import ExperimentResult, ArtifactRef

class VizKind(str, Enum):
    histogram = "histogram"
    density_matrix = "density_matrix"
    hypergraph = "hypergraph"
    report = "report"

class VisualizationAdapter(Protocol):
    name: str
    supported_kinds: set[VizKind]

    def render(
        self,
        result: ExperimentResult,
        kind: VizKind,
        options: Mapping[str, Any] | None = None,
    ) -> list[ArtifactRef]:
        ...
```

```python
# src/visualization/service.py
from src.visualization.adapters.base import VisualizationAdapter, VizKind
from src.engine.storage import Storage

class VisualizationService:
    def __init__(self, adapters: list[VisualizationAdapter], storage: Storage):
        self._by_name = {a.name: a for a in adapters}
        self._storage = storage

    def render(self, adapter_name: str, kind: VizKind, result, options=None):
        adapter = self._by_name[adapter_name]
        artifacts = adapter.render(result, kind, options or {})
        # Storage is responsible for paths; adapters return ArtifactRef with paths
        for a in artifacts:
            self._storage.register_artifact(a)
        return artifacts
```

### Data Contracts (inputs/outputs)

- Inputs: `ExperimentResult` (raw counts/density matrix + derived metrics)
- Outputs: list of `ArtifactRef` with paths/metadata; storage handles path policy
- Options: adapter-specific dict (e.g., color map, resolution)

### Registry & Selection

- Default adapter configurable via `AppContext` (`viz_backend`)
- Capability-based fallback: if adapter doesn’t support `VizKind`, raise clear error
- CLI picks adapter from context/flag and calls `VisualizationService`
- Web adapter can output JSON payloads (no images) for client-side rendering

### Storage boundary

- Adapters do not decide directories; they request paths via storage or return in-memory bytes for storage to persist.
- Ensures consistent file layout and deterministic filenames.

### Migration steps

- Keep existing `src/visualization/backends/*` as initial adapters, moved/renamed to `adapters/` and made to implement the `VisualizationAdapter` protocol.
- Move SaveManager responsibilities under `engine.storage` and make adapters rely on storage for path policy.
- Update CLI to use `VisualizationService` instead of importing backends directly.

---

## Schemas and Validation (Source of Truth)

### Goals

- Single source of truth for config/result shapes
- Strong runtime validation at boundaries
- Back/forward compatible evolution with semantic versioning
- Auto-generated JSON Schemas for docs and external tooling

### What to model

- ExperimentConfig
- SweepManifest
- ExperimentResult
  - Provenance
  - ArtifactRef
  - Metrics (extensible)

### Source of truth

- Use Pydantic models in `src/engine/models.py` as the authoritative definitions.
- Auto-generate `schemas/*.json` from these models; do not hand-edit JSON Schemas.

### Versioning

- Embed semantic version in payloads:
  - `ExperimentResult.provenance.schema_version` (e.g., "1.0.0")
  - Optional `SweepManifest.schema_version`
- Patch = additive non-breaking; minor/major = breaking.
- Provide an upgrader to read older results and normalize in-memory.

### Validation points

- Input: adapters (CLI/headless/web) parse JSON/YAML and instantiate Pydantic `ExperimentConfig`/`SweepManifest`.
- Engine API: accept only validated models (not raw dicts).
- Output: engine returns `ExperimentResult` model; serialize to JSON.
- Optional: secondary CI validation with `fastjsonschema` against generated schemas.

### Canonicalization and hashing

- Deterministic config hash for filenames:
  - Use `model_dump(mode="json", exclude_none=True, by_alias=True)`
  - Sort keys, stable float formatting
  - Hash with SHA1/256 of the canonical JSON string

### Schema generation (tool)

```python
# tools/gen_schemas.py
from pathlib import Path
import json
from src.engine.models import ExperimentConfig, SweepManifest, ExperimentResult

SCHEMAS = {
    "schemas/experiment_config.schema.json": ExperimentConfig,
    "schemas/manifest.schema.json": SweepManifest,
    "schemas/results.schema.json": ExperimentResult,
}

def main():
    root = Path(__file__).resolve().parents[1]
    for path, model in SCHEMAS.items():
        schema = model.model_json_schema()
        out = root / path
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(schema, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
```

### Testing

- Round-trip: Model → JSON → Model equality (ignoring derived/transient fields).
- Fixture conformance: validate golden config/result files against generated schemas.
- Backward compatibility: load old results via upgrader, assert key invariants.
- Hash determinism: same config → same hash; permuted-key dict → same hash.

### Migration plan

- v1: Implement Pydantic models mirroring existing schemas.
- Switch validators to use models; keep existing JSON Schemas but mark as generated.
- Add schema generation script and CI check to ensure schemas match models.
- Replace `src/utils/schema.py` to delegate to models; optionally retain `fastjsonschema` behind a flag for external validation.

### File layout

- `src/engine/models.py` (Pydantic models)
- `schemas/experiment_config.schema.json`
- `schemas/manifest.schema.json`
- `schemas/results.schema.json`
- `tools/gen_schemas.py` (schema generator)

---

## Coding Standards & Scientific Accuracy

### General principles

- Keep files small and modular: prefer modules ≤ 300 lines; functions ≤ 50–80 lines; split logic rather than nesting.
- Single responsibility per module/class/function. Compose via clear interfaces.
- No implicit globals in core paths; pass `AppContext` or explicit parameters.
- Strong typing everywhere (PEP 484). Public APIs and models must be fully typed.

### Naming & structure

- Descriptive names over abbreviations (e.g., `prepare_cluster_state`, not `prep_clst`).
- Functions are verbs; classes are nouns. Avoid one-letter variables.
- Prefer pure functions for analysis/metrics; side-effects only in adapters/storage.

### Docstrings

- Every public module, class, and function must have a docstring.
- Include: purpose, parameters, returns, raises, and examples where helpful.
- Quantum-specific functions must state assumptions and references:
  - State preparation: target state (Dirac form), qubit order, entangling pattern, reference.
  - Noise models: channel definition (Kraus/superoperator), constraints (e.g., T2 ≤ 2·T1), references.
  - Metrics: definition (equation), domain, limitations.

### Scientific correctness

- Validate state preparations against expected statevectors/density matrices in tests (tolerances explicit).
- Enforce physical constraints (CPTP, positivity) in noise models; reject invalid parameters with clear errors.
- Reproducibility: propagate RNG seeds and document stochastic components.
- Provenance: record simulator backend/method/options and transpilation summary.

### Error handling & logging

- Fail fast with precise exceptions; avoid broad `except`.
- No `print` in engine; use structured events/logging via event bus.
- User-facing messages only in adapters (CLI/web).

### Dependencies & boundaries

- Engine must not import CLI or visualization; visualization goes through adapters.
- Storage (paths, filenames) is centralized; adapters do not decide directories.
- Validation happens at boundaries (Pydantic models) before entering engine.

### Testing

- Unit tests per module; avoid cross-coupled tests.
- Round-trip tests for models and deterministic hashing.
- Physics tests: expected states, channel properties, metric invariants.
- Golden fixtures for results (small, curated); avoid huge binaries in repo.

### Tooling

- Format: Black (line length 100) and isort.
- Lint: Ruff (or flake8) with strict rules for unused imports/vars and complexity.
- Types: mypy (strict for engine/models; gradual elsewhere).
- Pre-commit hooks: run black, isort, ruff, mypy on changed files.

### Performance

- Avoid unnecessary copies; prefer vectorized operations (NumPy) where appropriate.
- Be explicit about algorithmic complexity in docstrings when > O(n^2).
- Provide configuration to downsample large visualizations.

### API stability

- `src/engine/api.py` is the stable entry point; changes require deprecation path.
- Semantic versioning for result schemas; document breaking changes.

### Import style

- Absolute imports within `src` (no relative up-level hacks); no wildcard imports.

### Review checklist (PRs)

- Does the change reduce or maintain complexity? If not, why?
- Are engine boundaries respected (no CLI/viz leaks)?
- Are models and schemas updated with version bumps if needed?
- Are docstrings and references provided for quantum logic?
- Tests: added/updated; run green locally and in CI.

---

## Alignment with ROADMAP (Vision, Modular Design, Physics Compliance)

### Vision & Philosophy

- Science‑First: Engine produces faithful, reproducible results with full provenance; tests assert physics properties and metric correctness.
- Modular Excellence: Engine core, adapters (CLI/web/viz/storage), and plugins (state, noise, viz) are cleanly separated with stable interfaces.
- User Empowerment: Extension points documented (adapters, plugins) so researchers can add capabilities without touching engine code.
- Research Integrity: Strong validation (Pydantic), deterministic hashing, versioned schemas, and event/provenance capture.
- Educational Value: Docstrings with equations/assumptions, runnable examples, and clear architecture docs.

### Modular Design

- Clean separation: CLI, engine core, visualization adapters, storage, utilities.
- Composable components: simple interfaces for state prep, noise models, and metrics; assembled in `engine.api`.
- Plugin‑ready: registry patterns for visualization and state/noise providers; minimal contracts.
- Factory patterns: explicit factories for states/noise; no hidden globals.

### Physics Compliance

- Quantum constraints enforced:
  - Noise: CPTP/positivity checks; parameter bounds (e.g., T2 ≤ 2·T1); clear error messages.
  - State prep: validated against expected statevectors/density matrices within tolerances.
- Hardware realism (optional fields): backend timing/method, temperature/thermal populations, gate durations captured in provenance when available.
- Metrics: documented definitions (e.g., KL, TVD, Fubini‑Study) with references; domain limitations spelled out.

---

## Proposed src/ layout (file-level)

```text
src/
  __init__.py
  version.py

  engine/
    __init__.py
    api.py                 # run(config)->ExperimentResult, sweep(manifest)->list[ExperimentResult]
    models.py              # Pydantic models: ExperimentConfig, SweepManifest, ExperimentResult, Provenance, ArtifactRef
    context.py             # AppContext (paths, viz backend, logging mode)
    events.py              # Event bus interfaces + event types
    storage.py             # Storage interface + LocalStorage impl (path policy, writes, artifact registry)
    runner.py              # Thin orchestrator using core (state->noise->transpile->simulate)
    hashing.py             # Canonicalization + config hash
    upgrader.py            # Back/forward compatibility loaders

  core/
    __init__.py
    qiskit_integration/
      __init__.py
      transpile.py         # transpilation wrapper, seed, time capture
      simulate.py          # qasm/statevector/density methods, backend options
      backends.py          # simulator info discovery
    state_prep/
      __init__.py
      base.py              # protocol for state preparation
      ghz.py
      w_state.py
      bell.py
      cluster.py
      custom.py
      factory.py           # maps config -> concrete state preparer
      state_constants.py
    noise/
      __init__.py
      base.py              # protocol for noise channels/models
      depolarizing.py
      amplitude_damping.py
      phase_damping.py
      bit_flip.py
      phase_flip.py
      thermal_relaxation.py
      factory.py           # maps config -> noise model
      validators.py        # physics constraints (CPTP, T2 ≤ 2*T1, bounds)
    analysis/
      __init__.py
      metrics/
        __init__.py
        entropy.py         # Shannon/normalized
        distance.py        # TVD, KL, Fubini-Study, etc.
        correlations.py
        information_theory.py
      dynamics/
        __init__.py
        decoherence.py
        transitions.py
        clustering.py
      symmetry/
        __init__.py
        symmetry.py
    research/
      __init__.py
      handler.py           # derive metrics from raw result, assemble ExperimentResult (no saving)

  visualization/
    __init__.py
    adapters/
      __init__.py
      base.py              # VisualizationAdapter protocol, VizKind enum
      matplotlib_adapter.py
      plotly_adapter.py
      webjson_adapter.py   # optional; JSON payloads for web
    service.py             # VisualizationService (adapter registry/orchestration)
    report/
      __init__.py
      renderer.py          # Markdown/HTML report generation
      templates/
        report_template.html

  experiments/
    __init__.py
    registry.py            # central registry of presets (metadata + config builders)
    presets/
      __init__.py
      beginner.py
      intermediate.py
      advanced.py
      research.py
      ghz_structured_decoherence.py

  cli/
    __init__.py
    headless.py            # argparse subcommands: run/sweep/viz/report
    interactive.py         # thin interactive menus; calls engine.api + visualization.service
    display.py
    help.py

  config/
    __init__.py
    settings.py            # default paths, default viz backend, etc. (read into AppContext)
    profiles.py            # save/load/apply profiles -> AppContext
    params.py              # adapter-level input normalization (uses engine.models for validation)

  utils/
    __init__.py
    logger.py              # setup + structured formatting
    input_handler.py
    messages.py
    glossary.py
    path_utils.py
    json_io.py
    tty.py
```

---

## Detailed Step‑by‑Step Refactor Plan (execution checklist)

This is the definitive, ordered plan. Each step includes tasks, acceptance criteria, and a rollback note. Ship each step green before advancing.

### 0. Preparation (branching, guards)

- Tasks
  - Create feature branch: `feature/engine-first-refactor`
  - Add a feature flag/env: `QEXP_USE_ENGINE_API=0|1` (default 0)
  - Ensure CI runs tests with and without the flag (matrix)
- Acceptance
  - Branch created; CI passing on current main
- Rollback
  - Delete branch; no code changes merged

### 1. Engine skeleton (no behavior change)

- Tasks
  - Create files: `src/engine/{__init__.py,api.py,models.py,context.py,events.py,storage.py,runner.py,hashing.py,upgrader.py}` with stubs and docstrings
  - Wire `AppContext` structure (paths, viz backend, logging mode) with defaults sourced from `config.settings`
  - Add unit test placeholders: `tests/engine/test_api_skeleton.py`
- Acceptance
  - Tests compile; stubs import; no runtime behavior altered
- Rollback
  - Remove engine directory files

### 2. Models and schemas (Pydantic as source of truth)

- Tasks
  - Implement Pydantic models in `engine/models.py`: `ExperimentConfig`, `SweepManifest`, `ExperimentResult`, `Provenance`, `ArtifactRef`
  - Add canonical dump + hashing in `engine/hashing.py`
  - Create `tools/gen_schemas.py`; generate `schemas/*.json` from models
  - Replace `src/utils/schema.py` internals to delegate to Pydantic (keep API stable)
  - Tests: model round‑trips, schema generation parity, hash determinism
- Acceptance
  - Generated schemas committed; model tests pass; existing schema tests still green
- Rollback
  - Revert model imports to previous utils-based validators; remove generator

### 3. Engine facade wrapping current core

- Tasks
  - Implement `engine/runner.py` that calls existing `core.experiment_runner` and returns a raw result payload
  - Implement `engine/api.run(config: ExperimentConfig, ctx: AppContext) -> ExperimentResult` using `core.research_handler` for metrics and assembling the result
  - Move provenance assembly into engine (leave saving for later)
  - Add smoke tests calling `engine.api.run` for GHZ baseline
- Acceptance
  - `engine.api.run` returns a result equivalent to current path (metrics, fields)
- Rollback
  - Keep facade in place but unused; adapters still use old path

### 4. Storage split and deterministic paths

- Tasks
  - Implement `engine/storage.py` with interfaces: `Storage`, `LocalStorage`
  - Move filename policy and artifact registration from `research_handler` and `visualization.save_manager` into storage
  - `engine.api.run` uses storage to persist result JSON; returns `ExperimentResult`
  - Tests: deterministic paths, artifact registration, existing visualization path tests updated to call storage
- Acceptance
  - Results saved via storage; file names identical (or approved delta) and tests green
- Rollback
  - Switch engine to in‑memory only and let legacy save manager handle persistence

### 5. Event bus (progress/logging decoupling)

- Tasks
  - Define event types in `engine/events.py` (run*start, run_progress, run_end, sweep*\*)
  - Emit events from engine; provide a no‑op default subscriber
  - Adapter (CLI) subscribes to render progress/JSON stream; guard behind feature flag
  - Tests: event emission order, subscriber callbacks
- Acceptance
  - Events visible in CLI when flag is on; no change when off; tests pass
- Rollback
  - Keep event interfaces dormant; disable in adapters

### 6. CLI adapter switch (feature‑flagged)

- Tasks
  - Update headless subcommands to: parse → instantiate `ExperimentConfig` → call `engine.api.run`/`sweep`
  - Interactive flow calls engine for run; visualization still via legacy pathway for now
  - Add `--use-engine` flag (or respect env) to toggle
  - Tests: headless CLI tests run with flag on; outputs consistent
- Acceptance
  - Headless parity proven; interactive unchanged; tests pass in both modes
- Rollback
  - Default flag off; revert CLI call sites to legacy functions

### 7. Visualization adapters and service

- Tasks
  - Create `visualization/adapters/base.py` (protocol, `VizKind`)
  - Wrap existing backends as adapters under `visualization/adapters/*`
  - Add `VisualizationService` and route CLI `viz --from` to use service when engine flag is on.
  - Delegate all path policy to storage; adapters return `ArtifactRef`s
  - Tests: adapter registration, capability errors, artifact creation
- Acceptance
  - Viz artifacts produced through service; paths controlled by storage; tests green
- Rollback
  - Keep service present but leave CLI pointing to legacy backends

### 8. Interactive CLI simplification

- Tasks
  - Limit visible presets to the curated set; remove difficulty; keep family/tags
  - Custom: “Import config from file” only; advanced modes moved to headless
  - Ensure menu layers are shallow and hotkeys unique; keep copy concise
  - Tests: smoke path for menus, non‑TTY behavior, unique hotkeys
- Acceptance
  - Simplified UX validated; tests green
- Rollback
  - Keep previous interactive module; toggle via env flag

### 9. Profiles and settings → AppContext

- Tasks
  - Route profile load/save to produce `AppContext`
  - Remove direct global settings reads from core paths; adapters pass context explicitly
  - Tests: profile application changes context; storage/viz pick up new paths/backends
- Acceptance
  - No core reads globals; context required; tests green
- Rollback
  - Keep context layer but allow fallback to settings for a release

### 10. Cleanup and deprecations

- Tasks
  - Deprecate/remove `src/config/quick_experiments.py`
  - Archive legacy presets under `presets/legacy.py`
  - Purge generated artifacts: `logs/*`, `results/*` (keep dir scaffolding)
  - Docs: update README, examples, and add engine usage guide
  - Pre‑commit: add black/isort/ruff/mypy hooks; fix offenders
- Acceptance
  - Repo clean; docs current; CI with linters and types green
- Rollback
  - Restore files from Git; keep deprecation warnings for one release

### 11. Final flip & release

- Tasks
  - Default `QEXP_USE_ENGINE_API=1`
  - Remove legacy code paths after one release cycle (with deprecation notes)
  - Tag version; update CHANGELOG
- Acceptance
  - All tests green; users can run via engine/CLI; release notes published
- Rollback
  - Revert default flag; hotfix release if needed

### CI & quality gates (applies to all phases)

- Test matrix: engine‑on/engine‑off (until final flip)
- Lint/type: ruff + mypy required for engine/models; gradual elsewhere
- Schema generation check: schemas match models
- Artifacts check: no large binaries committed

### Communication

- Keep `docs/ENGINE_FIRST_REFACTOR_PLAN.md` updated at each phase
- Add ADR (Architecture Decision Record) for engine‑first and visualization adapters
- Provide migration notes for contributors (presets, viz adapters)

---

## Progress Update (to date)

- Phase 0: DONE — Engine skeleton (`api`, `context`, `events`, `storage`, `runner`, `hashing`) and minimal tests.
- Phase 1: DONE — Pydantic models (`ExperimentConfig`, `SweepManifest`, `ExperimentResult`, `Provenance`, `ArtifactRef`), schema generator, `schemas/*.json` generated.
- Phase 3: DONE — Engine facade wired to legacy core; `engine.api.run()` returns `ExperimentResult` parity with legacy metrics.
- Phase 4: DONE — Unified storage; results saved via `LocalStorage.save_analysis` with legacy-compatible paths; artifact recorded in result.
- Phase 5: DONE — Basic event bus; `run/sweep` emit `RUN_START/RUN_END` and `SWEEP_START/SWEEP_END`.
- Tests: 44 passed.

## Revised Next Steps

- Phase 6: CLI adapter switch (feature-flagged)
  - Headless subcommands build `ExperimentConfig` and call `engine.api.run/sweep`.
  - Flag: `QEXP_USE_ENGINE_API=1` or `--use-engine` to toggle; keep interactive unchanged initially.
  - Tests for parity on headless paths.
- Phase 7: Visualization adapters + `VisualizationService`
  - DONE (initial): Added `src/engine/viz_service.py` with `VisualizationService` and `VisualizationRequest`.
  - Adapters wrap existing matplotlib histogram/density/hypergraph functions and return `ArtifactRef`s.
  - Tests added: `tests/engine/test_viz_service.py` (histogram + hypergraph) and `tests/cli/test_cli_viz_engine_flag.py` for CLI wiring under engine flag.
  - CLI: `viz --from` routed through service when `QEXP_USE_ENGINE_API=1`.
  - Next: add Plotly adapter support and surface backend/output-dir flags on CLI.
- Phase 8: Interactive simplification
  - Curated minimal presets; “Import config from file” for custom; shallow menus.
- Phase 9: Profiles → `AppContext`
  - Profiles produce `AppContext`; remove core reads of globals.
- Phase 10: Cleanup & deprecations
  - Deprecate `quick_experiments`, archive legacy presets, purge artifacts, docs/examples, pre-commit tooling.
- Phase 11: Flip default & release
  - Default engine on; deprecate legacy paths with notice; changelog.

### Cross-cutting additions

- Packaging (`pyproject.toml`, extras), plugin entry points, deep provenance (env snapshot), artifact checksums in manifest, perf benchmarks in CI, and security posture for custom builders (off by default).
