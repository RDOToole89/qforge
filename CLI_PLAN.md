# CLI Overhaul Plan (Tracking)

Framework goals: research-grade, modular, extensible. CLI must be intuitive for independent researchers, support headless/server use, and produce reproducible, provenance-rich outputs.

## High-level capabilities

- [x] Unified presets as source of truth (`src/experiments/presets/**`)
- [x] Curated Quick Start drawing from presets (incl. research anchor)
- [x] Selection UX with numbers/hotkeys/defaults; Enter accepts default
- [x] Organized save paths via SaveManager; real-data visualizations
- [ ] Headless commands (`qexp`) for server/batch use
- [x] Results JSON schema v1 with provenance (initial) + docs (pending)

## Current CLI structure

- Main menu: Browse Presets, Quick Start, Build Custom, Recent Results, Settings
- Presets Browser: filters (category/difficulty), free-text search, selection, active filter chips, compact list
- Custom Wizard: basic (state → custom source when CUSTOM → noise → sim → viz)
- Recent Results: list last N JSON files
- [x] Settings: read-only defaults; basic editing (shots, error_rate, backend, save dir)

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
- [x] Active filter chips + '/' search hint
- [x] Compact list (no Value column in menus)

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
- [x] Compact selections (no Value column)

### Settings

- [x] Read-only view of defaults
- [ ] Editing: error_rate, shots, default backend, SaveManager base dir
- [ ] Profiles: save/load named configurations
- [x] Actions stub (profiles/back) with footer hints

### Help & Glossary

- [x] `Help` main menu with searchable glossary (noise models, metrics, objects)
- [x] Inline `?` hotkey: show short definition + examples (basic)
- [ ] Link to local markdown docs / external references
- [x] Preset details footer hints and Actions (r/e/l/b)

### Headless/Server alignment

- [x] CLI subcommands: `run --preset`, `run --config`, `sweep --manifest`, `viz --from results.json`
- [x] Visualize from saved JSON (`--viz <file> --type ...`)
- [x] Streaming structured logs flag (`--stream-logs`) for headless/server
- [ ] Manifest format (JSON/YAML) for batches/sweeps; deterministic runs with seeds
- [ ] Streaming progress and structured logs for server use

### Results schema & provenance

- [x] JSON schema v1 fields: schema_version, timestamp, software_versions; rng_seed/transpile/simulator (partial)
- [x] Attach normalized experiment_config, raw results, derived metrics, artifact paths, insights (initial)
- [x] Deterministic filenames (timestamp + short config hash)

### Visualization & Insights

- [ ] Professional “Experiment Report” panel: Key Insights, expand Details, Save report
- [x] Footer key hints added in major screens
- [x] Re-introduce Density Matrix sim mode and align viz prompts

### Cleanup & tests

- [ ] Deprecate/remove `src/config/quick_experiments` after migration
- [ ] Tests: CLI smoke (menus, selections), schema validation, presets registry sanity, sweep manifest, recent results actions

---

## Status snapshot (today)

- Completed: unified presets, curated quick start, filters/search with active chips, compact menus (no Value column) across CLI, numeric defaults and 's' shortcut, preset details with Actions and ASCII preview, auto-Edit on 'n', recent results (list/open/rerun/compare + compact), settings read-only with actions stub, footer key hints on main screens.
- Next to implement: profiles save/load, headless commands, JSON schema v1, report export, tests (CLI smoke/schema/presets/manifest), tagging/labels, compact results key metric column, and retire old quick configs.

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

- [x] Replace list with compact table (#, Name, State, Q, Noise, Sim, Shots, Diff, Cat)
- [x] Restore concise hotkeys (r/e/b/?) with footer hints
- [x] Add top filter chips and "/" fuzzy search in browser
- [x] Remove verbose "Value" column from displays

### Details & flow

- [x] Make detail pane actions explicit: Run [r], Edit [e], Back [b], Preview [l]
- [x] Auto-open Edit when "Proceed?" = n (pre-filled)
- [x] Add quick key: l=circuit preview (ASCII)

### Wizard UX

- [ ] Breadcrumb header (Preset → Params → Viz → Review)
- [x] "s" to keep default on prompts; show defaults inline
- [ ] Inline autofix prompts for constraint violations (e.g., set BELL→2 qubits)
- [ ] Density mode: skip measurement-only prompts; show context note
- [ ] Hide noise fields when disabled; normalize params to None

### Keyboard model

- [x] Standardize Enter/Numbers/?/q across key screens (TTY arrows soft-dep)
- [x] Footer key-hints component used in main menus and presets

### Recent results

- [ ] Replace list with compact table incl. Key metric column
- [x] Actions: Open [o], Re-run [r], Compare [c]
- [x] Compare: metrics diff view; ideal deltas (TVD/KL)
- [x] Optional small overlay chart in compare (mini entropy bar)

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

- [x] Subcommands: run --preset, run --config, sweep --manifest, viz --from
- [x] Manifest (JSON) minimal schema; seeds partially supported
- [x] Structured logs + streaming flag for server mode

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
