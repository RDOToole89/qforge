"""
Simple Demo Plugin - Minimal example for learning.

This shows the absolute minimum needed for a working plugin.
"""

class SimpleDemo:
    """Minimal plugin example."""
    
    def get_experiments(self):
        """Return a simple experiment."""
        return {
            "hello_quantum": {
                "name": "Hello Quantum World",
                "description": "Your first plugin experiment - 2-qubit GHZ state",
                "category": "plugin_demo",
                "difficulty": "beginner",
                "config": {
                    "num_qubits": 2,
                    "state_type": "GHZ",
                    "noise_enabled": False,
                    "shots": 1024,
                    "sim_mode": "qasm"
                }
            },
            "noisy_hello": {
                "name": "Noisy Hello Quantum",
                "description": "Same experiment but with 10% noise",
                "category": "plugin_demo", 
                "difficulty": "beginner",
                "config": {
                    "num_qubits": 2,
                    "state_type": "GHZ",
                    "noise_enabled": True,
                    "noise_type": "DEPOLARIZING",
                    "error_rate": 0.10,
                    "shots": 1024,
                    "sim_mode": "qasm"
                }
            }
        }

# Factory function
def get_plugin():
    return SimpleDemo()