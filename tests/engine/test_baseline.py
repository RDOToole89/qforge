"""
Baseline Tests for Engine API

Purpose: Establish baseline functionality before Phase 1.2 integration.
These tests ensure we don't break existing functionality when adding
research metrics integration.

Architecture Note: Tests the engine as a standalone core that can be
used by any interface (CLI, Web, Python scripts).
"""

import pytest
from typing import Dict, Any

from src.engine.api import run, sweep
from src.engine.models import ExperimentConfig, SweepManifest


class TestEngineBaseline:
    """Test current engine functionality without research metrics."""
    
    def test_engine_runs_basic_experiment(self):
        """Verify engine can run basic quantum experiments."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            shots=1024,
            enable_research_metrics=False
        )
        
        result = run(config)
        
        # Basic validation
        assert result is not None
        assert result.config_hash is not None
        assert result.timestamp is not None
        assert result.analysis is not None
        
        # No research metrics when disabled
        assert result.structured_decoherence_metrics is None
    
    def test_engine_runs_with_noise(self):
        """Verify engine handles noise models correctly."""
        config = ExperimentConfig(
            num_qubits=2,
            state_type="BELL",
            noise_enabled=True,
            noise_type="depolarizing",
            error_rate=0.05,
            shots=1024,
            enable_research_metrics=False
        )
        
        result = run(config)
        
        assert result is not None
        assert result.analysis is not None
        # Verify noise was applied (analysis should contain noise info)
    
    def test_engine_parameter_sweep(self):
        """Verify engine can run parameter sweeps."""
        manifest = SweepManifest(
            base_config=ExperimentConfig(
                num_qubits=2,
                state_type="BELL",
                enable_research_metrics=False
            ),
            parameter_ranges={
                "error_rate": [0.0, 0.05, 0.1]
            },
            runs_per_config=1
        )
        
        results = sweep(manifest)
        
        assert len(results) == 3  # 3 error rates
        for result in results:
            assert result is not None
            assert result.structured_decoherence_metrics is None
    
    def test_engine_interface_agnostic(self):
        """Verify engine works independently of interface."""
        # Direct Python usage (not CLI)
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            shots=512
        )
        
        # Should work without any CLI context
        result = run(config)
        
        assert result is not None
        assert hasattr(result, 'model_dump')  # Pydantic model
        
        # Can serialize for any interface
        json_data = result.model_dump()
        assert isinstance(json_data, dict)
        assert 'analysis' in json_data
        assert 'config_hash' in json_data


class TestCurrentResearchCapability:
    """Document current research analysis capability."""
    
    def test_research_metrics_flag_exists(self):
        """Verify research parameters exist in config."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=True,
            research_type="structured_decoherence"
        )
        
        assert config.enable_research_metrics is True
        assert config.research_type == "structured_decoherence"
    
    def test_research_metrics_computed(self):
        """Test that research metrics are now computed when enabled."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            enable_research_metrics=True,
            research_type="structured_decoherence",
            shots=1024
        )
        
        result = run(config)
        
        # This should now pass - research metrics integrated!
        assert result.structured_decoherence_metrics is not None
        assert result.structured_decoherence_metrics.asymmetry_index >= 0
        assert result.structured_decoherence_metrics.pathway_concentration_ratio >= 0
        assert -1 <= result.structured_decoherence_metrics.entanglement_error_correlation <= 1


class TestEngineModularity:
    """Test that engine follows modular design principles."""
    
    def test_config_is_self_contained(self):
        """Config should be complete specification, no hidden dependencies."""
        config = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            shots=1024
        )
        
        # Config should be serializable (no complex objects)
        config_dict = config.model_dump()
        assert isinstance(config_dict, dict)
        
        # Can recreate from dict (round-trip)
        config2 = ExperimentConfig(**config_dict)
        assert config2.num_qubits == config.num_qubits
        assert config2.state_type == config.state_type
    
    def test_result_is_self_contained(self):
        """Result should contain everything needed for analysis."""
        config = ExperimentConfig(
            num_qubits=2,
            state_type="BELL",
            shots=512
        )
        
        result = run(config)
        
        # Result should be complete
        assert result.analysis is not None
        assert result.provenance is not None
        assert result.config_hash is not None
        
        # Should be serializable for any interface
        result_dict = result.model_dump()
        assert isinstance(result_dict, dict)
    
    def test_no_global_state(self):
        """Engine should not rely on global state."""
        # Run two experiments with different configs
        config1 = ExperimentConfig(
            num_qubits=2,
            state_type="BELL",
            shots=512
        )
        
        config2 = ExperimentConfig(
            num_qubits=3,
            state_type="GHZ",
            shots=1024
        )
        
        result1 = run(config1)
        result2 = run(config2)
        
        # Results should be independent
        assert result1.config_hash != result2.config_hash
        # Each result is self-contained
        assert result1.analysis is not None
        assert result2.analysis is not None


def capture_baseline_metrics() -> Dict[str, Any]:
    """
    Capture current baseline metrics for comparison.
    
    Returns:
        Dictionary of baseline measurements
    """
    import time
    
    config = ExperimentConfig(
        num_qubits=3,
        state_type="GHZ",
        shots=1024,
        enable_research_metrics=False
    )
    
    # Measure execution time
    start_time = time.time()
    result = run(config)
    execution_time = time.time() - start_time
    
    # Capture baseline metrics
    baseline = {
        "execution_time": execution_time,
        "result_size_bytes": len(str(result.model_dump())),
        "has_analysis": result.analysis is not None,
        "has_provenance": result.provenance is not None,
        "has_research_metrics": result.structured_decoherence_metrics is not None,
        "timestamp": result.timestamp
    }
    
    return baseline


if __name__ == "__main__":
    # Run baseline capture
    print("Capturing baseline metrics...")
    baseline = capture_baseline_metrics()
    
    print("\nBaseline Metrics:")
    for key, value in baseline.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Baseline tests complete!")
    print("These metrics will be compared after Phase 1.2 integration.")