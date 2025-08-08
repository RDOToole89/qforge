"""
Example Plugin for Quantum Experiment Framework.

This demonstrates how to create a plugin that adds custom experiments
to the framework.
"""

from typing import Dict, Any, List
import numpy as np
from qiskit import QuantumCircuit


class BellVariationsPlugin:
    """
    Plugin that adds Bell state variations and analysis experiments.
    
    This plugin demonstrates:
    - Adding custom experiments
    - Custom state preparation 
    - Plugin-specific analysis
    - Integration with existing framework
    """
    
    def __init__(self):
        self.plugin_name = "bell_variations"
        self.version = "1.0.0"
        self.author = "Quantum Research Team"
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Return plugin metadata."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "Bell state variations and entanglement analysis",
            "experiments_count": len(self.get_experiments())
        }
    
    def get_experiments(self) -> Dict[str, Dict[str, Any]]:
        """Return plugin experiments."""
        return {
            "bell_phi_plus": {
                "name": "Bell Φ+ State Analysis",
                "description": "Φ+ = (|00⟩ + |11⟩)/√2 - standard Bell state",
                "category": "plugin_bell",
                "difficulty": "intermediate", 
                "source": "plugin",
                "plugin": self.plugin_name,
                "config": {
                    "num_qubits": 2,
                    "state_type": "BELL",
                    "noise_type": "DEPOLARIZING",
                    "noise_enabled": False,
                    "shots": 2048,
                    "sim_mode": "qasm",
                    "custom_params": {"variant": "phi_plus"},
                    "enable_research_metrics": True,
                }
            },
            "bell_phi_minus": {
                "name": "Bell Φ- State Analysis", 
                "description": "Φ- = (|00⟩ - |11⟩)/√2 - phase-flipped Bell state",
                "category": "plugin_bell",
                "difficulty": "intermediate",
                "source": "plugin", 
                "plugin": self.plugin_name,
                "config": {
                    "num_qubits": 2,
                    "state_type": "BELL",
                    "noise_type": "DEPOLARIZING", 
                    "noise_enabled": False,
                    "shots": 2048,
                    "sim_mode": "qasm",
                    "custom_params": {"variant": "phi_minus"},
                    "enable_research_metrics": True,
                }
            },
            "bell_entanglement_sweep": {
                "name": "Bell Entanglement Decoherence Sweep",
                "description": "Study how different noise levels affect Bell state entanglement",
                "category": "plugin_research",
                "difficulty": "research",
                "source": "plugin",
                "plugin": self.plugin_name,
                "research_type": "entanglement_decoherence",
                "config": {
                    "num_qubits": 2,
                    "state_type": "BELL", 
                    "noise_type": "DEPOLARIZING",
                    "noise_enabled": True,
                    "shots": 4096,
                    "sim_mode": "qasm",
                    "error_rate": 0.05,
                    "custom_params": {"variant": "phi_plus"},
                    "enable_research_metrics": True,
                    "multiple_runs": 3,
                }
            },
            "bell_vs_ghz": {
                "name": "Bell vs GHZ Entanglement Comparison",
                "description": "Compare entanglement properties of 2-qubit Bell vs 3-qubit GHZ",
                "category": "plugin_research", 
                "difficulty": "research",
                "source": "plugin",
                "plugin": self.plugin_name,
                "research_type": "entanglement_comparison",
                "config": {
                    "num_qubits": 2,  # Will run both 2q Bell and 3q GHZ
                    "state_type": "BELL",
                    "noise_type": "DEPOLARIZING",
                    "noise_enabled": True, 
                    "shots": 4096,
                    "sim_mode": "qasm",
                    "error_rate": 0.05,
                    "custom_params": {"variant": "phi_plus", "compare_with_ghz": True},
                    "enable_research_metrics": True,
                }
            }
        }
    
    def get_custom_components(self) -> List[Any]:
        """Return custom components provided by this plugin."""
        return [
            BellAnalysisComponent(),
            EntanglementComparisonComponent()
        ]


class BellAnalysisComponent:
    """Custom analysis component for Bell states."""
    
    def __init__(self):
        self.name = "bell_analysis" 
        self.version = "1.0.0"
    
    def analyze_bell_fidelity(self, counts: Dict[str, int], variant: str = "phi_plus") -> float:
        """
        Calculate fidelity with ideal Bell state.
        
        Args:
            counts: Measurement counts
            variant: Bell state variant (phi_plus, phi_minus, psi_plus, psi_minus)
            
        Returns:
            Fidelity with ideal Bell state
        """
        total_shots = sum(counts.values())
        if total_shots == 0:
            return 0.0
        
        # Define ideal outcomes for each Bell variant
        ideal_outcomes = {
            "phi_plus": {"00": 0.5, "11": 0.5},
            "phi_minus": {"00": 0.5, "11": 0.5},  
            "psi_plus": {"01": 0.5, "10": 0.5},
            "psi_minus": {"01": 0.5, "10": 0.5}
        }
        
        if variant not in ideal_outcomes:
            return 0.0
            
        ideal = ideal_outcomes[variant]
        
        # Calculate fidelity (simplified)
        fidelity = 0.0
        for outcome, ideal_prob in ideal.items():
            actual_prob = counts.get(outcome, 0) / total_shots
            fidelity += np.sqrt(ideal_prob * actual_prob)
        
        return fidelity ** 2
    
    def detect_entanglement_loss(self, counts: Dict[str, int]) -> Dict[str, float]:
        """Detect and quantify entanglement degradation."""
        total_shots = sum(counts.values())
        
        # Calculate probabilities
        probs = {k: v/total_shots for k, v in counts.items()}
        
        # Simple entanglement measures
        correlation_00_11 = probs.get("00", 0) + probs.get("11", 0)
        correlation_01_10 = probs.get("01", 0) + probs.get("10", 0)
        
        return {
            "phi_correlation": correlation_00_11,
            "psi_correlation": correlation_01_10, 
            "entanglement_strength": max(correlation_00_11, correlation_01_10),
            "classical_mixture": 1 - max(correlation_00_11, correlation_01_10)
        }


class EntanglementComparisonComponent:
    """Component for comparing different entangled states."""
    
    def __init__(self):
        self.name = "entanglement_comparison"
        self.version = "1.0.0"
    
    def compare_entanglement_types(self, bell_counts: Dict[str, int], 
                                 ghz_counts: Dict[str, int]) -> Dict[str, Any]:
        """Compare Bell and GHZ entanglement characteristics.""" 
        
        bell_analysis = BellAnalysisComponent()
        
        # Analyze Bell state
        bell_entanglement = bell_analysis.detect_entanglement_loss(bell_counts)
        bell_fidelity = bell_analysis.analyze_bell_fidelity(bell_counts)
        
        # Analyze GHZ state (simplified)
        ghz_total = sum(ghz_counts.values())
        ghz_correlation = (ghz_counts.get("000", 0) + ghz_counts.get("111", 0)) / ghz_total if ghz_total > 0 else 0
        
        return {
            "bell_state": {
                "fidelity": bell_fidelity,
                "entanglement_strength": bell_entanglement["entanglement_strength"],
                "qubits": 2
            },
            "ghz_state": {
                "correlation": ghz_correlation,
                "entanglement_strength": ghz_correlation,  # Simplified
                "qubits": 3
            },
            "comparison": {
                "bell_vs_ghz_strength": bell_entanglement["entanglement_strength"] / ghz_correlation if ghz_correlation > 0 else float('inf'),
                "multipartite_advantage": ghz_correlation > bell_entanglement["entanglement_strength"]
            }
        }


# Plugin registration function
def get_plugin():
    """Factory function to create plugin instance."""
    return BellVariationsPlugin()


# Plugin metadata for discovery
PLUGIN_METADATA = {
    "name": "bell_variations",
    "version": "1.0.0", 
    "author": "Quantum Research Team",
    "description": "Bell state variations and entanglement analysis experiments",
    "entry_point": "get_plugin"
}