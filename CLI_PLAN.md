# CLI Overhaul Plan (Tracking)

Framework goals: research-grade, modular, extensible. CLI must be intuitive for independent researchers, support headless/server use, and produce reproducible, provenance-rich outputs.

## High-level capabilities

- [x] Unified presets as source of truth (`src/experiments/presets/**`)
- [x] Curated Quick Start drawing from presets (incl. research anchor)
- [x] Selection UX with numbers/hotkeys/defaults; Enter accepts default
- [x] Organized save paths via SaveManager; real-data visualizations
- [ ] Headless commands (`qexp`) for server/batch use
- [ ] Results JSON schema v1 with provenance + docs

## Current CLI structure

- Main menu: Browse Presets, Quick Start, Build Custom, Recent Results, Settings
- Presets Browser: filters (category/difficulty), free-text search, selection
- Custom Wizard: basic (state → custom source when CUSTOM → noise → sim → viz)
- Recent Results: list last N JSON files
- Settings: read-only defaults (editing pending)

---

## Detailed checklist (prioritized next)

### Selection & inputs

- [x] Numeric/hotkey selections for: Main menu, State, Noise, Sim mode, Visualization
- [x] Numeric inputs accept Enter defaults (no `None` prompts)
- [x] Global “?” help hotkey on prompts (basic glossary popover)
- [x] Arrow-key navigation (soft-dependency) with fallback to current menus

### Presets

- [x] Load unified presets from registry (all levels, incl. research)
- [x] Filters by category/difficulty
- [x] Free-text search by name/description/tags
- [x] Preset detail pane before run (state/noise/sim/viz, expected outputs, time estimate)
- [x] Clone & Edit flow (preset → editable parameters, then run)
- [ ] Tagging/labels: state types, noise models, research tags

### Quick Start

- [x] Curated list from presets (incl. `ghz_structured_decoherence_ref`)
- [ ] Curations by profile (beginner/research)

### Custom Wizard

- [x] Basic path for CUSTOM (gates/builder/openqasm)
- [x] Templates (e.g., Bell/W/Cluster), parameterized (initial set)
- [x] Validators & schema checks for gates/builder/qasm (via CustomState.create path)
- [x] Preview (text circuit summary)
- [x] Parameter normalization: hide noise fields when disabled; set to None
- [x] Constraints: enforce state↔qubits, physics (T2 ≤ 2\*T1), compatible sim/noise

### Recent Results

- [x] List last N JSON files
- [x] Actions: re-open visualization
- [x] Actions: re-run with same params
- [x] Compare two runs (diff metrics/plots) – basic metrics table
- [x] Compare: add TVD/KL vs ideal deltas; optional small chart (metrics table; chart pending)

### Settings

- [x] Read-only view of defaults
- [ ] Editing: error_rate, shots, default backend, SaveManager base dir
- [ ] Profiles: save/load named configurations

### Help & Glossary

- [x] `Help` main menu with searchable glossary (noise models, metrics, objects)
- [x] Inline `?` hotkey: show short definition + examples (basic)
- [ ] Link to local markdown docs / external references

### Headless/Server alignment

- [ ] CLI subcommands: `run --preset`, `run --config`, `sweep --manifest`, `viz --from results.json`
- [x] Visualize from saved JSON (`--viz <file> --type ...`)
- [ ] Manifest format (JSON/YAML) for batches/sweeps; deterministic runs with seeds
- [ ] Streaming progress and structured logs for server use

### Results schema & provenance

- [ ] JSON schema v1 with: schema_version, timestamp, software_versions, rng_seed, transpile settings, device/simulator info
- [ ] Attach normalized experiment_config, raw results, derived metrics, artifact paths, insights
- [ ] Deterministic filenames (timestamp + short config hash)

### Visualization & Insights

- [ ] Professional “Experiment Report” panel: Key Insights, expand Details, Save report
- [x] Re-introduce Density Matrix sim mode and align viz prompts

### Cleanup & tests

- [ ] Deprecate/remove `src/config/quick_experiments` after migration
- [ ] Tests: CLI smoke (menus, selections), schema validation, presets registry sanity, sweep manifest, recent results actions

---

## Status snapshot (today)

- Completed: unified presets, curated quick start, filters/search, selection UX, numeric defaults, recent results list, settings (read-only).
- Next to implement: preset detail pane, improved Custom wizard (templates/validators/preview), recent results actions, settings editing, help/glossary overlay, headless commands, JSON schema v1, tests, and retire old quick configs.

---

## UX blueprint (world‑class CLI)

- **Presets list (compact, fast)**

  - One table: #, Name, State, Q, Noise, Sim, Shots, Diff, Cat
  - Select by number; minimal hotkeys: r=run, e=edit, b=back, ?=help
  - Arrow keys in TTY, numbers otherwise; Enter=default
  - Top chips show filters; "/" to fuzzy search; "f" to toggle filters

- **Preset details (clear actions)**

  - Always-visible: Run [r], Edit [e], Back [b]
  - If "Proceed?" = n → open Edit pre-filled (no bounce to menu)
  - Quick keys: l=circuit preview, v=choose visualization pipeline, h=help

- **Edit wizard (guided)**

  - Breadcrumbs: Preset → Params → Viz → Review
  - Progressive disclosure; hide noise fields when disabled
  - Defaults visible; "s" keep default; inline validation & autofix
  - Physics guards (e.g., BELL ↔ 2 qubits) with one-key fix

- **Keyboard model (consistent)**

  - Enter=default; Esc=back; numbers=items; arrows (TTY); "/"=search; ?=help; q=quit
  - Footer key hints; no repeated hotkeys in every row

- **Recent results (research-centric)**

  - Table: Name, Time, State, Q, Noise, Sim, Shots, Key metric
  - Actions: Open [o], Re-run [r], Compare [c], Report [p]
  - Compare: metrics diff; toggle delta vs ideal (TVD/KL); optional overlay chart

- **Reports & outputs**

  - Key Insights panel; toggle Detailed Metrics; Save report (HTML/MD)
  - Quiet (-q) and JSON-only (-J) modes; verbose (-v)
  - Color modes: standard, high-contrast, no-emoji

- **Help & glossary**

  - Global ? popover; F1 or Help menu → searchable glossary
  - Noise Types quick sheet with practical tips

- **Persistence & profiles**

  - Remember last selections; profiles save/load
  - Export/import manifest; deterministic seeds for reproducibility

- **Headless parity**
  - Subcommands mirror interactive: run, sweep, viz-from
  - Same validation, filenames, and reports

---

## Comprehensive TODO checklist (actionable)

### Presets UI

- [ ] Replace list with compact table (#, Name, State, Q, Noise, Sim, Shots, Diff, Cat)
- [ ] Restore concise hotkeys (r/e/b/?) with footer hints
- [ ] Add top filter chips and "/" fuzzy search in browser
- [ ] Remove verbose "Value" column from displays

### Details & flow

- [ ] Make detail pane actions explicit: Run [r], Edit [e], Back [b]
- [ ] Auto-open Edit when "Proceed?" = n (pre-filled)
- [ ] Add quick keys: l=circuit preview, v=viz pipeline, h=help

### Wizard UX

- [ ] Breadcrumb header (Preset → Params → Viz → Review)
- [ ] "s" to keep default on prompts; show defaults inline
- [ ] Inline autofix prompts for constraint violations (e.g., set BELL→2 qubits)
- [ ] Density mode: skip measurement-only prompts; show context note
- [ ] Hide noise fields when disabled; normalize params to None

### Keyboard model

- [ ] Standardize Enter/Esc/numbers/arrows/"/"/"?"/q across all screens
- [ ] Footer key-hints component shared by menus and wizards

### Recent results

- [ ] Replace list with compact table incl. Key metric column
- [ ] Actions: Open [o], Re-run [r], Compare [c], Report [p]
- [ ] Compare: metrics diff view; toggle ideal deltas (TVD/KL)
- [ ] Optional small overlay chart in compare

### Reports & outputs

- [ ] Save Experiment Report (HTML + Markdown) with artifact links
- [ ] CLI flags: -q (quiet), -J (JSON-only), -v (verbose)
- [ ] Color modes: standard/high-contrast/no-emoji

### Help & glossary

- [ ] Global ? popover component; consistent placement
- [ ] Integrate Help into main menu; searchable glossary
- [ ] Noise Types quick reference panel with tips
- [ ] Link-out to local docs/external references

### Headless/server

- [ ] Subcommands: run --preset, run --config, sweep --manifest, viz --from
- [ ] Manifest (JSON/YAML) schema for batches/sweeps; seeds
- [ ] Structured logs + streaming progress for server mode

### Results schema & provenance (TODOs)

- [ ] JSON schema v1: schema_version, timestamp, software_versions, rng_seed, transpile, simulator/device
- [ ] Include normalized experiment_config, raw results, derived metrics, artifact paths, insights
- [ ] Deterministic filenames (timestamp + short config hash)

### Visualization

- [ ] Pipeline chooser (matplotlib/plotly) from detail pane [v]
- [ ] Ensure SaveManager paths for all artifacts (PNG/HTML/MP4)
- [ ] Add Bloch animation trigger from Recent Results when density-series present

### Cleanup & tests (TODOs)

- [ ] Deprecate/remove `src/config/quick_experiments` after full migration
- [ ] Tests: CLI smoke (menus/hotkeys/defaults), presets registry sanity, recent results actions, compare deltas
- [ ] Tests: headless subcommands, manifest validation, JSON schema validation
- [ ] TTY detection and arrow-key fallback tests
