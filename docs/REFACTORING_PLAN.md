# Quantum Experiment Framework - Refactoring Plan

## Current Issues

### 1. Architectural Redundancy
- **Engine/Core Duplication**: The `engine` layer acts as a thin wrapper around `core`, creating unnecessary indirection
- **Multiple Runner Implementations**: `engine.runner` wraps `core.experiment_runner` without adding value
- **Duplicated Models**: Data models exist in both layers with mapping logic

### 2. Visualization Sprawl
- **Legacy Pipeline**: `visualization/pipeline.py` (deprecated but retained)
- **New Pipeline Modules**: `visualization/pipeline/` directory with modular components
- **Multiple Adapter Patterns**: `adapters/`, `backends/`, and `plots/` with overlapping responsibilities
- **Duplicate Plotting Logic**: Similar functionality in `analysis/` and `plots/` directories

### 3. CLI Complexity
- **Interactive Mode**: Complex menu system with extensive state management
- **Headless Mode**: Parallel command structure with different entry points
- **Feature Flags**: Mixed old/new paths controlled by environment variables

### 4. Test Coverage Gaps
- Tests spread across 32 files but not aligned with refactored structure
- Missing integration tests for new engine API
- Deprecated test patterns still in use

## Refactoring Strategy

### Phase 1: Core Consolidation ✅
**Goal**: Merge engine wrapper into core, making core the single source of truth

1. **Unify Runner Implementation**
   - Move engine API logic directly into `core.experiment_runner`
   - Eliminate `engine.runner` wrapper
   - Consolidate data models into single location

2. **Simplify Data Flow**
   - Direct core → storage → visualization pipeline
   - Remove intermediate transformations
   - Standardize on Pydantic models throughout

### Phase 2: Visualization Cleanup
**Goal**: Single, clear visualization pipeline

1. **Remove Deprecated Code**
   - Delete `visualization/pipeline.py` 
   - Consolidate pipeline modules into cleaner structure
   - Unify adapter/backend patterns

2. **Streamline Plotting**
   - Merge `analysis/` and `plots/` visualization code
   - Single adapter pattern for multiple backends
   - Clear separation: data processing vs rendering

### Phase 3: CLI Simplification
**Goal**: Unified, maintainable CLI

1. **Merge Interactive/Headless Modes**
   - Single entry point with mode detection
   - Shared command processing logic
   - Simplified menu system

2. **Remove Feature Flags**
   - Complete migration to new API
   - Remove legacy code paths
   - Update documentation

### Phase 4: Test Modernization
**Goal**: Comprehensive, maintainable test suite

1. **Restructure Tests**
   - Align with new architecture
   - Remove deprecated test patterns
   - Add integration tests for full workflows

2. **Improve Coverage**
   - Target 80%+ code coverage
   - Focus on critical paths
   - Add performance benchmarks

## Implementation Order

### Week 1: Core Consolidation
- [ ] Merge engine.api logic into core.experiment_runner
- [ ] Unify data models in core.models
- [ ] Update storage to work directly with core
- [ ] Remove engine.runner wrapper

### Week 2: Visualization Cleanup  
- [ ] Delete deprecated pipeline.py
- [ ] Consolidate visualization modules
- [ ] Unify plotting logic
- [ ] Simplify adapter pattern

### Week 3: CLI & Testing
- [ ] Merge interactive/headless modes
- [ ] Remove feature flags
- [ ] Update all tests
- [ ] Add integration tests

### Week 4: Documentation & Polish
- [ ] Update all documentation
- [ ] Create migration guide
- [ ] Performance optimization
- [ ] Final cleanup

## Success Metrics

1. **Code Reduction**: Target 30% fewer lines of code
2. **Test Coverage**: Achieve 80%+ coverage
3. **Performance**: Maintain or improve execution speed
4. **Maintainability**: Reduce cognitive complexity scores
5. **Documentation**: 100% public API documentation

## Breaking Changes

### API Changes
- `engine.api.run()` → `core.run_experiment()`
- `engine.models.*` → `core.models.*`
- Visualization pipeline API simplified

### Configuration Changes
- Remove `QEXP_USE_ENGINE_API` flag
- Consolidate settings into single config system
- Standardize on single profile format

### Import Changes
```python
# Old
from src.engine.api import run
from src.engine.models import ExperimentConfig

# New  
from src.core import run_experiment
from src.core.models import ExperimentConfig
```

## Risk Mitigation

1. **Backwards Compatibility**: Provide migration shims for 1 release cycle
2. **Testing**: Extensive testing before each phase merge
3. **Documentation**: Clear migration guides for users
4. **Rollback Plan**: Tag releases before each major change
5. **User Communication**: Announce changes in advance

## Timeline

- **Start Date**: Current
- **Phase 1 Completion**: +1 week
- **Phase 2 Completion**: +2 weeks  
- **Phase 3 Completion**: +3 weeks
- **Final Release**: +4 weeks

## Notes

- Prioritize core functionality over features during refactor
- Maintain physics validation throughout changes
- Keep research-grade quality standards
- Document all architectural decisions