"""
Composable experiment implementations using the building block system.

Provides concrete implementations of experiments built using the
modular component architecture for easy customization and extension.
"""

from typing import Dict, Any, List
import logging

from .base import BaseExperiment
from .mixins import ComposableMixin

logger = logging.getLogger("QuantumExperiment.Components.ComposableExperiments")


class ComposableQuantumExperiment(BaseExperiment, ComposableMixin):
    """
    A fully composable quantum experiment using all available mixins.
    
    This experiment class demonstrates how to combine the base experiment
    framework with all available mixins to create a flexible, feature-rich
    quantum experiment.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str = "",
                 state_type: str = "GHZ",
                 num_qubits: int = 3,
                 shots: int = 4096,
                 **kwargs):
        """
        Initialize the composable quantum experiment.
        
        Args:
            name: Experiment name
            description: Experiment description
            state_type: Type of quantum state to prepare
            num_qubits: Number of qubits
            shots: Number of measurement shots
            **kwargs: Additional configuration parameters
        """
        # Initialize base experiment
        super().__init__(name=name, description=description, **kwargs)
        
        # Set experiment parameters
        self.config.update({
            "state_type": state_type,
            "num_qubits": num_qubits,
            "shots": shots,
            "sim_mode": "qasm"
        })
        
        # Configure experiment as research-grade by default
        self.configure_research(
            research_type="quantum_experiment",
            enable_research_metrics=True,
            statistical_validation=True
        )
        
        logger.info(f"Initialized composable experiment: {name} ({num_qubits} qubits, {shots} shots)")
        
    def configure(self) -> None:
        """Configure the experiment pipeline with standard components."""
        # This would be implemented to add actual quantum circuit components
        # For now, we define the interface
        logger.info("Configuring experiment pipeline...")
        
    def quick_configure_structured_decoherence(self,
                                              noise_levels: List[float] = None,
                                              noise_type: str = "DEPOLARIZING") -> 'ComposableQuantumExperiment':
        """
        Quick configuration for structured decoherence research.
        
        Args:
            noise_levels: List of noise levels for parameter sweeps
            noise_type: Type of noise to apply
            
        Returns:
            Self for method chaining
        """
        if noise_levels is None:
            noise_levels = [0.01, 0.05, 0.10, 0.20]
            
        # Configure noise
        self.configure_noise(
            noise_type=noise_type,
            error_rate=noise_levels[0],  # Default to first level
            enabled=True
        )
        
        # Configure research mode
        self.configure_research(
            research_type="structured_decoherence",
            enable_research_metrics=True,
            statistical_validation=True
        )
        
        # Configure analysis
        self.configure_analysis([
            "shannon_entropy",
            "kl_divergence", 
            "total_variation_distance",
            "mutual_information",
            "qubit_wise_bias"
        ])
        
        # Configure visualization
        self.configure_visualization(
            visualization_type="research_dashboard",
            output_formats=["plot", "save"]
        )
        
        # Enable high precision
        self.enable_high_precision(shots=4096, runs_per_config=3)
        
        # Store noise levels for parameter sweeps
        self.config["parameter_ranges"] = {
            "error_rate": noise_levels
        }
        
        logger.info(f"Configured for structured decoherence research with noise levels: {noise_levels}")
        return self
        
    def quick_configure_entanglement_study(self,
                                          state_types: List[str] = None) -> 'ComposableQuantumExperiment':
        """
        Quick configuration for entanglement studies.
        
        Args:
            state_types: List of quantum state types to study
            
        Returns:
            Self for method chaining
        """
        if state_types is None:
            state_types = ["BELL", "GHZ", "W"]
            
        # Configure analysis for entanglement metrics
        self.configure_analysis([
            "entanglement_entropy",
            "concurrence",
            "negativity",
            "schmidt_decomposition"
        ])
        
        # Configure visualization for entanglement
        self.configure_visualization(
            visualization_type="entanglement_dashboard",
            output_formats=["plot", "save"]
        )
        
        # Store state types for sweeps
        self.config["parameter_ranges"] = {
            "state_type": state_types
        }
        
        logger.info(f"Configured for entanglement study with states: {state_types}")
        return self
        
    def to_preset_format(self) -> Dict[str, Any]:
        """
        Convert the experiment to the preset format used by the experiment manager.
        
        Returns:
            Dictionary in the format expected by the preset experiment system
        """
        return {
            "name": self.metadata.name,
            "description": self.metadata.description,
            "category": self.metadata.category,
            "difficulty": self.metadata.difficulty,
            "research_type": self.metadata.research_type,
            "config": {
                **self.config,
                **self.get_full_config()
            }
        }


def create_structured_decoherence_experiment(name: str = "Composable Structured Decoherence",
                                           num_qubits: int = 3,
                                           shots: int = 4096) -> ComposableQuantumExperiment:
    """
    Factory function to create a structured decoherence experiment.
    
    Args:
        name: Experiment name
        num_qubits: Number of qubits
        shots: Number of shots
        
    Returns:
        Configured structured decoherence experiment
    """
    experiment = ComposableQuantumExperiment(
        name=name,
        description=f"Structured decoherence study on {num_qubits}-qubit GHZ states",
        state_type="GHZ",
        num_qubits=num_qubits,
        shots=shots
    )
    
    experiment.quick_configure_structured_decoherence()
    return experiment


def create_entanglement_experiment(name: str = "Composable Entanglement Study",
                                 num_qubits: int = 3,
                                 shots: int = 4096) -> ComposableQuantumExperiment:
    """
    Factory function to create an entanglement study experiment.
    
    Args:
        name: Experiment name  
        num_qubits: Number of qubits
        shots: Number of shots
        
    Returns:
        Configured entanglement study experiment
    """
    experiment = ComposableQuantumExperiment(
        name=name,
        description=f"Entanglement study on {num_qubits}-qubit systems",
        state_type="GHZ", 
        num_qubits=num_qubits,
        shots=shots
    )
    
    experiment.quick_configure_entanglement_study()
    return experiment