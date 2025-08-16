# Engine First Research Support - Comprehensive Implementation Plan

**Objective**: Create a completely decoupled quantum experiment engine that supports structured decoherence research and can interface with any frontend (CLI, programmatic Python, React web app, etc.).

## 🎯 Vision: Universal Quantum Experiment Interface

```python
# Programmatic Usage (Python scripts, Jupyter notebooks)
from qiskit_experiments.engine import run_experiment, run_sweep

result = run_experiment({
    "num_qubits": 3,
    "state_type": "GHZ",
    "enable_research_metrics": True,
    "research_type": "structured_decoherence"
})

# CLI Usage (unchanged externally)
python main.py --config config.json

# Future React Frontend
POST /api/experiments → Engine API → WebSocket progress → Results
```

## 📋 Phase 1: Engine Research Foundation (Current Priority)

### Step 1.1: Update Engine Models with Research Support
**Files**: `src/engine/models.py`

**Add Research Parameters to ExperimentConfig:**
```python
class ExperimentConfig(BaseModel):
    # ... existing fields ...
    
    # Research Parameters
    enable_research_metrics: bool = False
    research_type: Optional[Literal[
        "structured_decoherence", 
        "parameter_sweep", 
        "noise_comparison",
        "control", 
        "scaling", 
        "convergence", 
        "batch_sweep"
    ]] = None
    multiple_runs: int = Field(default=1, ge=1)
    track_convergence: bool = False
    visualization_type: Literal[
        "histogram", 
        "density_matrix", 
        "research", 
        "plot", 
        "none"
    ] = "histogram"
```

**Add Structured Decoherence Results:**
```python
class StructuredDecoherenceMetrics(BaseModel):
    asymmetry_index: float = Field(ge=0, description="AI: Deviation from uniform distribution")
    pathway_concentration_ratio: float = Field(ge=0, description="PCR: Top vs bottom pathway concentration")
    entanglement_error_correlation: float = Field(ge=-1, le=1, description="EEC: Topology-error correlation")
    temporal_pathway_stability: Optional[float] = Field(default=None, ge=0, le=1, description="TPS: Consistency across conditions")
    complexity_emergence_score: Optional[float] = Field(default=None, ge=0, description="CES: Emergence threshold")
    
    # Analysis metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    pathway_analysis: Dict[str, Any] = Field(default_factory=dict)

class ExperimentResult(BaseModel):
    # ... existing fields ...
    structured_decoherence_metrics: Optional[StructuredDecoherenceMetrics] = None
```

### Step 1.2: Integrate Structured Decoherence into Engine API  
**Files**: `src/engine/api.py`

**Import Research Analysis:**
```python
from src.core.analysis.structured_decoherence.pathway_analysis import compute_all_pathway_metrics
```

**Update run() function:**
```python
def run(config: ExperimentConfig | Dict[str, Any], ctx: Optional[AppContext] = None) -> ExperimentResult:
    # ... existing logic ...
    
    # Add structured decoherence metrics if enabled
    if cfg_model.enable_research_metrics:
        from src.core.analysis.structured_decoherence.pathway_analysis import compute_all_pathway_metrics
        
        # Extract counts from raw result
        counts = _extract_counts_from_result(raw)
        
        # Compute structured decoherence metrics
        pathway_metrics = compute_all_pathway_metrics(
            counts=counts,
            state_type=cfg_model.state_type,
            num_qubits=cfg_model.num_qubits
        )
        
        result.structured_decoherence_metrics = StructuredDecoherenceMetrics(**pathway_metrics)
    
    return result
```

### Step 1.3: Update SweepManifest for Research
**Files**: `src/engine/models.py`

**Enhance SweepManifest:**
```python
class SweepManifest(BaseModel):
    # ... existing fields ...
    
    # Override parameters for sweep-specific settings
    override: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Parameters to override in base configuration"
    )
    
    # Research sweep metadata
    research_metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional metadata for research sweeps"
    )
```

### Step 1.4: Create Engine Test Suite
**Files**: `tests/engine/test_research_integration.py`

**Test Research Integration:**
```python
def test_engine_research_experiment():
    """Test that engine API can run research experiments."""
    config = {
        "num_qubits": 3,
        "state_type": "GHZ",
        "noise_type": "depolarizing",
        "noise_enabled": True,
        "error_rate": 0.05,
        "enable_research_metrics": True,
        "research_type": "structured_decoherence"
    }
    
    result = run(config)
    assert result.structured_decoherence_metrics is not None
    assert result.structured_decoherence_metrics.asymmetry_index >= 0

def test_engine_research_sweep():
    """Test that engine API can run research sweeps."""
    manifest = {
        "base_config": {
            "state_type": "GHZ",
            "enable_research_metrics": True,
            "research_type": "parameter_sweep"
        },
        "parameter_ranges": {
            "num_qubits": [3, 4],
            "error_rate": [0.0, 0.05]
        }
    }
    
    results = sweep(manifest)
    assert len(results) == 4  # 2x2 combinations
    for result in results:
        assert result.structured_decoherence_metrics is not None
```

### Step 1.5: Update CLI to Use Engine API
**Files**: `src/cli/headless/run.py`, `src/cli/headless/sweep.py`

**Modify run.py:**
```python
def headless_run_experiment(args, logger):
    """Run single experiment using engine API."""
    from src.engine.api import run
    from src.engine.context import AppContext
    
    # Convert CLI args to engine config
    config = _cli_args_to_engine_config(args)
    
    # Run via engine
    ctx = AppContext()
    result = run(config, ctx)
    
    # Save and display results
    _save_and_display_result(result, args, logger)
```

**Modify sweep.py:**
```python
def headless_sweep(args, logger):
    """Run parameter sweep using engine API."""
    from src.engine.api import sweep
    from src.engine.context import AppContext
    
    # Load and validate manifest
    manifest_path = Path(args.manifest_file)
    manifest_data = _load_manifest(manifest_path)
    
    # Run sweep via engine
    ctx = AppContext()
    results = sweep(manifest_data, ctx)
    
    # Process and save results
    _process_sweep_results(results, args, logger)
```

## 📋 Phase 2: Complete Engine Autonomy

### Step 2.1: Move Core Quantum Logic to Engine
**Target Structure:**
```
src/engine/
├── api.py                    # Public interface
├── models.py                 # Pydantic models
├── context.py               # Application context
├── events.py                # Progress events
├── storage.py               # File management
├── quantum/                 # Pure quantum logic
│   ├── states/             # State preparation (moved from core)
│   ├── noise/              # Noise models (moved from core)
│   └── simulator.py        # Simulation engine
├── analysis/               # Analysis modules
│   ├── structured_decoherence/  # Research metrics
│   ├── information_theory/     # Core analysis
│   └── statistics.py          # Statistical validation
└── runner.py               # Execution engine
```

### Step 2.2: Create Pure Engine Runner
**Files**: `src/engine/runner.py`

**Replace thin wrapper with complete implementation:**
```python
class QuantumExperimentEngine:
    """Pure quantum experiment execution engine."""
    
    def __init__(self, context: AppContext):
        self.context = context
        self.event_bus = SimpleEventBus()
        
    def execute_experiment(self, config: ExperimentConfig) -> ExperimentResult:
        """Execute quantum experiment with full orchestration."""
        # 1. Prepare quantum circuit
        circuit = self._prepare_circuit(config)
        
        # 2. Configure simulation
        backend = self._setup_backend(config)
        
        # 3. Run simulation
        raw_result = self._run_simulation(circuit, backend, config)
        
        # 4. Analyze results
        analysis = self._analyze_results(raw_result, config)
        
        # 5. Compute research metrics if enabled
        if config.enable_research_metrics:
            analysis = self._add_research_metrics(analysis, config)
        
        # 6. Package result
        return self._package_result(analysis, config)
```

### Step 2.3: Event-Driven Progress System
**Files**: `src/engine/events.py`

**Enhanced Event System for Real-Time Updates:**
```python
class ExperimentEvents:
    # Experiment lifecycle
    EXPERIMENT_STARTED = "experiment.started"
    CIRCUIT_PREPARED = "experiment.circuit_prepared"
    SIMULATION_STARTED = "experiment.simulation_started"
    SIMULATION_PROGRESS = "experiment.simulation_progress"
    ANALYSIS_STARTED = "experiment.analysis_started"
    EXPERIMENT_COMPLETED = "experiment.completed"
    
    # Sweep lifecycle
    SWEEP_STARTED = "sweep.started"
    SWEEP_EXPERIMENT_STARTED = "sweep.experiment_started"
    SWEEP_EXPERIMENT_COMPLETED = "sweep.experiment_completed"
    SWEEP_PROGRESS = "sweep.progress"
    SWEEP_COMPLETED = "sweep.completed"
    
    # Error events
    EXPERIMENT_ERROR = "experiment.error"
    SWEEP_ERROR = "sweep.error"

class ProgressTracker:
    """Track and broadcast experiment progress."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
    def track_experiment(self, config: ExperimentConfig):
        """Context manager for experiment progress tracking."""
        return ExperimentProgressContext(self.event_bus, config)
```

### Step 2.4: Storage Service Enhancement
**Files**: `src/engine/storage.py`

**Deterministic, Research-Optimized Storage:**
```python
class ResearchStorage:
    """Research-optimized storage with deterministic paths."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self._ensure_research_structure()
    
    def _ensure_research_structure(self):
        """Create research-specific directory structure."""
        dirs = [
            "experiments",           # Individual experiments
            "sweeps",               # Parameter sweeps
            "campaigns",            # Long-term research campaigns
            "analysis",             # Cross-experiment analysis
            "visualizations",       # Generated plots
            "exports"               # Publication-ready exports
        ]
        for dir_name in dirs:
            (self.base_dir / dir_name).mkdir(exist_ok=True)
    
    def save_experiment_result(self, result: ExperimentResult, config: ExperimentConfig) -> Path:
        """Save experiment with research-optimized naming."""
        # Generate deterministic filename
        filename = self._generate_experiment_filename(result, config)
        
        # Choose appropriate subdirectory
        subdir = self._choose_subdirectory(config)
        
        # Save with metadata
        filepath = self.base_dir / subdir / filename
        self._save_with_metadata(result, filepath, config)
        
        return filepath
```

## 📋 Phase 3: Frontend Interface Layer

### Step 3.1: WebSocket Progress Interface
**Files**: `src/engine/interfaces/websocket.py`

**Real-Time Progress for React Frontend:**
```python
class WebSocketProgressHandler:
    """Handle WebSocket connections for real-time progress."""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.connections = {}
    
    async def handle_experiment_request(self, websocket, config_data):
        """Handle experiment request with real-time updates."""
        experiment_id = str(uuid.uuid4())
        self.connections[experiment_id] = websocket
        
        try:
            # Subscribe to events for this experiment
            self.event_bus.subscribe(f"experiment.{experiment_id}.*", 
                                   lambda event: self._send_progress(websocket, event))
            
            # Run experiment
            config = ExperimentConfig(**config_data)
            result = await self._run_experiment_async(config, experiment_id)
            
            # Send final result
            await websocket.send(json.dumps({
                "type": "experiment_completed",
                "experiment_id": experiment_id,
                "result": result.model_dump()
            }))
            
        finally:
            del self.connections[experiment_id]
```

### Step 3.2: REST API Layer
**Files**: `src/engine/interfaces/rest.py`

**HTTP API for Web Frontends:**
```python
from fastapi import FastAPI, BackgroundTasks
from fastapi.websockets import WebSocket

app = FastAPI(title="Quantum Experiment Engine API")

@app.post("/api/experiments")
async def create_experiment(
    config: ExperimentConfig,
    background_tasks: BackgroundTasks
):
    """Create and run experiment."""
    experiment_id = str(uuid.uuid4())
    
    # Run in background
    background_tasks.add_task(run_experiment_task, experiment_id, config)
    
    return {"experiment_id": experiment_id, "status": "started"}

@app.websocket("/api/experiments/{experiment_id}/progress")
async def experiment_progress(websocket: WebSocket, experiment_id: str):
    """WebSocket for real-time experiment progress."""
    await websocket.accept()
    # Connect to event bus and stream progress
    await stream_experiment_progress(websocket, experiment_id)

@app.post("/api/sweeps")
async def create_sweep(manifest: SweepManifest):
    """Create and run parameter sweep."""
    # Similar to experiments but for sweeps
    pass
```

### Step 3.3: TypeScript Interface Generation
**Files**: `scripts/generate_typescript_interfaces.py`

**Auto-Generate TypeScript from Pydantic:**
```python
def generate_typescript_interfaces():
    """Generate TypeScript interfaces from Pydantic models."""
    
    models = [ExperimentConfig, ExperimentResult, SweepManifest, StructuredDecoherenceMetrics]
    
    typescript_content = "// Auto-generated TypeScript interfaces\n\n"
    
    for model in models:
        typescript_content += pydantic_to_typescript(model)
        typescript_content += "\n\n"
    
    # Write to frontend directory
    output_path = Path("frontend/src/types/quantum-engine.ts")
    output_path.write_text(typescript_content)
```

## 📋 Phase 4: Testing & Validation

### Step 4.1: Comprehensive Test Suite
**Files**: `tests/engine/`

**Test Categories:**
- **Unit Tests**: Individual engine components
- **Integration Tests**: End-to-end experiment flows
- **Research Tests**: Structured decoherence metric validation
- **Performance Tests**: Large sweep handling
- **Interface Tests**: WebSocket and REST API functionality

### Step 4.2: Backward Compatibility Validation
**Files**: `tests/compatibility/`

**Ensure CLI Still Works:**
```python
def test_cli_compatibility():
    """Ensure CLI commands still work with engine backend."""
    # Test all existing CLI commands
    pass

def test_config_compatibility():
    """Ensure existing config files still work."""
    # Test with legacy config formats
    pass
```

### Step 4.3: Performance Benchmarking
**Files**: `tests/performance/`

**Benchmark Engine Performance:**
```python
def benchmark_single_experiment():
    """Benchmark single experiment performance."""
    pass

def benchmark_large_sweep():
    """Benchmark large parameter sweep performance."""
    pass

def benchmark_real_time_progress():
    """Benchmark WebSocket progress performance."""
    pass
```

## 🎯 Success Criteria

### Phase 1 Complete When:
- ✅ Engine API supports all research parameters
- ✅ Structured decoherence metrics integrated
- ✅ CLI uses engine API exclusively
- ✅ All existing functionality preserved
- ✅ Research experiments work end-to-end

### Phase 2 Complete When:
- ✅ Engine is completely autonomous (no core dependencies)
- ✅ All quantum logic moved to engine
- ✅ Event system provides real-time progress
- ✅ Storage system optimized for research

### Phase 3 Complete When:
- ✅ WebSocket interface provides real-time updates
- ✅ REST API supports all operations
- ✅ TypeScript interfaces auto-generated
- ✅ React frontend can connect successfully

### Phase 4 Complete When:
- ✅ 100% test coverage for engine components
- ✅ Performance benchmarks meet targets
- ✅ Backward compatibility confirmed
- ✅ Documentation complete

## 🚀 Implementation Timeline

**Week 1**: Phase 1 (Engine Research Foundation)
**Week 2**: Phase 2 (Complete Engine Autonomy)  
**Week 3**: Phase 3 (Frontend Interface Layer)
**Week 4**: Phase 4 (Testing & Validation)

## 📁 Final Directory Structure

```
src/
├── engine/                          # Complete autonomous engine
│   ├── api.py                      # Public interface (run, sweep)
│   ├── models.py                   # Pydantic models with research support
│   ├── runner.py                   # Pure execution engine
│   ├── quantum/                    # Quantum logic (moved from core)
│   ├── analysis/                   # Analysis modules (moved from core)
│   ├── interfaces/                 # WebSocket, REST, etc.
│   └── storage.py                  # Research-optimized storage
├── cli/                            # CLI wrapper (uses engine API)
├── core/                           # Legacy (will be empty after migration)
└── visualization/                  # Simplified (matplotlib only)
```

## 🎯 Usage Examples After Implementation

**Research Scientist (Python):**
```python
from qiskit_experiments.engine import run_experiment

result = run_experiment({
    "num_qubits": 5,
    "state_type": "GHZ",
    "enable_research_metrics": True,
    "shots": 10000
})

print(f"Asymmetry Index: {result.structured_decoherence_metrics.asymmetry_index}")
```

**CLI User (unchanged):**
```bash
python main.py --config research_config.json
```

**React Frontend Developer:**
```typescript
const experiment: ExperimentConfig = {
  num_qubits: 3,
  state_type: "GHZ",
  enable_research_metrics: true,
  research_type: "structured_decoherence"
};

const response = await fetch('/api/experiments', {
  method: 'POST',
  body: JSON.stringify(experiment)
});

const { experiment_id } = await response.json();

// Real-time progress
const ws = new WebSocket(`/api/experiments/${experiment_id}/progress`);
ws.onmessage = (event) => {
  const progress = JSON.parse(event.data);
  updateProgressBar(progress.completion);
};
```

This plan creates a completely decoupled, interface-agnostic quantum experiment engine optimized for structured decoherence research!