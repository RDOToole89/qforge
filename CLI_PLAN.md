## CLI Overhaul Plan (Tracking)

Framework goals: research-grade, modular, extensible. CLI must be intuitive for independent researchers, support headless/server use, and produce reproducible, provenance-rich outputs.

### High-level capabilities

- [x] Unified presets as source of truth (`src/experiments/presets/**`)
- [x] Curated Quick Start drawing from presets (incl. research anchor)
- [x] Selection UX with numbers/hotkeys/defaults; Enter accepts default
- [x] Organized save paths via SaveManager; real-data visualizations
- [ ] Headless commands (`qexp`) for server/batch use
- [ ] Results JSON schema v1 with provenance + docs

### Current CLI structure

- Main menu: Browse Presets, Quick Start, Build Custom, Recent Results, Settings
- Presets Browser: filters (category/difficulty), free-text search, selection
- Custom Wizard: basic (state → custom source when CUSTOM → noise → sim → viz)
- Recent Results: list last N JSON files
- Settings: read-only defaults (editing pending)

---

### Detailed checklist

#### Selection & inputs

- [x] Numeric/hotkey selections for: Main menu, State, Noise, Sim mode, Visualization
- [x] Numeric inputs accept Enter defaults (no `None` prompts)
- [ ] Global “?” help hotkey on every prompt (term popover)

#### Presets

- [x] Load unified presets from registry (all levels, incl. research)
- [x] Filters by category/difficulty
- [x] Free-text search by name/description/tags
- [x] Preset detail pane before run (state/noise/sim/viz, expected outputs, time estimate)
- [x] Clone & Edit flow (preset → editable parameters, then run)
- [ ] Tagging/labels: state types, noise models, research tags

#### Quick Start

- [x] Curated list from presets (incl. `ghz_structured_decoherence_ref`)
- [ ] Curations by profile (beginner/research)

#### Custom Wizard

- [x] Basic path for CUSTOM (gates/builder/openqasm)
- [x] Templates (e.g., Bell/W/Cluster), parameterized (initial set)
- [x] Validators & schema checks for gates/builder/qasm (via CustomState.create path)
- [x] Preview (text circuit summary)

#### Recent Results

- [x] List last N JSON files
- [x] Actions: re-open visualization
- [x] Actions: re-run with same params
- [ ] Compare two runs (diff metrics/plots)

#### Settings

- [x] Read-only view of defaults
- [ ] Editing: error_rate, shots, default backend, SaveManager base dir
- [ ] Profiles: save/load named configurations

#### Help & Glossary

- [ ] `Help` menu with searchable glossary (noise models, metrics, objects)
- [ ] Inline `?` hotkey: show short definition + examples
- [ ] Link to local markdown docs / external references

#### Headless/Server alignment

- [ ] CLI subcommands: `run --preset`, `run --config`, `sweep --manifest`, `viz --from results.json`
- [ ] Manifest format (JSON/YAML) for batches/sweeps; deterministic runs with seeds
- [ ] Streaming progress and structured logs for server use

#### Results schema & provenance

- [ ] JSON schema v1 with: schema_version, timestamp, software_versions, rng_seed, transpile settings, device/simulator info
- [ ] Attach normalized experiment_config, raw results, derived metrics, artifact paths, insights
- [ ] Deterministic filenames (timestamp + short config hash)

#### Cleanup & tests

- [ ] Deprecate/remove `src/config/quick_experiments` after migration
- [ ] Tests: CLI smoke (menus, selections), schema validation, presets registry sanity, sweep manifest, recent results actions

---

### Status snapshot (today)

- Completed: unified presets, curated quick start, filters/search, selection UX, numeric defaults, recent results list, settings (read-only).
- Next to implement: preset detail pane, improved Custom wizard (templates/validators/preview), recent results actions, settings editing, help/glossary overlay, headless commands, JSON schema v1, tests, and retire old quick configs.
