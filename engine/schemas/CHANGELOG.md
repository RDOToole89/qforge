---
# Changelog – Quantum Experiment Schema Suite

All notable schema changes will be documented in this file.
This project follows **semantic versioning** across all schemas (core, execution, analysis).
---

## \[1.0.0] – 2025-08-16

### Added

- Initial release of the **Quantum Experiment Schema Suite (v1.0)**.
- Five core schemas established:
  - `core/experiment_spec.schema.json` – experiment design & intent
  - `core/provenance.schema.json` – reproducibility metadata
  - `core/structure_metrics.schema.json` – standardized decoherence & structure metrics
  - `execution/experiment_result.schema.json` – single-run outcomes
  - `execution/sweep_manifest.schema.json` – parameter sweeps
  - `analysis/analysis_result.schema.json` – aggregated results & conclusions

- `schema_index.json` introduced as central registry of schemas.
- Documentation:
  - `README.md` with schema overview, workflow, and relationships.
  - Schema freeze notice marking v1.0 as **stable & research-ready**.

### Notes

- This version is **frozen**: no further changes unless critical.
- Breaking changes will bump to `2.0.0`.
- Non-breaking enhancements (metadata, optional fields) will bump to `1.1.0`.

---

## \[1.1.0] – _TBD_

### Added

- _(Planned: units metadata, cross-experiment references, null models, advanced sweeps, hierarchical analysis, extended provenance.)_

### Changed

- _(TBD – non-breaking refinements only.)_

### Deprecated

- _(TBD – if any fields are marked for phase-out.)_

---

## \[2.0.0] – _TBD_

### Breaking Changes

- _(Reserved for major redesigns or structural overhauls.)_

### Migration Notes

- _(To be provided when/if 2.0.0 is released.)_

---
