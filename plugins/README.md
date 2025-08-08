# 🔌 Quantum Experiments Plugin System

## 📁 **Plugin Directory Structure**

```
qiskit-experiments/
├── src/experiments/plugins/    # 🔧 Plugin system implementation (framework code)
│   └── __init__.py            # Plugin loading and discovery engine
└── plugins/                   # 📦 Plugin storage directory (user plugins go here!)
    ├── README.md              # This file
    ├── example_plugin.py      # Advanced example plugin
    └── simple_demo.py         # Minimal example plugin
```

**This directory (`/plugins/`) contains plugins that extend the Quantum Experiment Framework with custom experiments and analysis tools.**

**The plugin system code lives in `/src/experiments/plugins/` - you don't need to modify that unless you're extending the plugin system itself.**

## 🚀 How to Create a Plugin

### 1. **Basic Plugin Structure**

Create a Python file in the `plugins/` directory:

```python
# plugins/my_plugin.py

class MyCustomPlugin:
    """My custom quantum experiment plugin."""
    
    def __init__(self):
        self.plugin_name = "my_plugin"
        self.version = "1.0.0"
        self.author = "Your Name"
    
    def get_plugin_info(self):
        """Return plugin metadata."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "My awesome quantum experiments"
        }
    
    def get_experiments(self):
        """Return experiments provided by this plugin."""
        return {
            "my_experiment": {
                "name": "My Custom Experiment",
                "description": "Does something quantum",
                "category": "plugin_custom",
                "difficulty": "intermediate",
                "config": {
                    "num_qubits": 3,
                    "state_type": "GHZ", 
                    "noise_enabled": False,
                    "shots": 1024,
                    "sim_mode": "qasm"
                }
            }
        }

# Factory function (required)
def get_plugin():
    return MyCustomPlugin()
```

### 2. **Advanced Plugin with Custom Components**

```python
# plugins/advanced_plugin.py

class AdvancedPlugin:
    def get_experiments(self):
        return {
            "advanced_analysis": {
                "name": "Advanced Quantum Analysis",
                "description": "Custom analysis with plugin components", 
                "category": "plugin_research",
                "difficulty": "research",
                "config": {
                    "num_qubits": 4,
                    "state_type": "CUSTOM",
                    "enable_research_metrics": True,
                    "custom_params": {
                        "use_plugin_analysis": True
                    }
                }
            }
        }
    
    def get_custom_components(self):
        """Return custom analysis components."""
        return [MyCustomAnalyzer()]

class MyCustomAnalyzer:
    """Custom analysis component."""
    
    def analyze(self, counts, config):
        # Your custom analysis logic here
        return {
            "custom_metric": 0.95,
            "analysis_type": "plugin_custom"
        }

def get_plugin():
    return AdvancedPlugin()
```

## 🛠️ Plugin Features

### **Supported Plugin Capabilities**

1. **Custom Experiments**: Add new preset experiments
2. **Custom Categories**: Create new experiment categories  
3. **Custom Analysis**: Provide specialized analysis components
4. **Research Integration**: Fully compatible with research-grade features
5. **Metadata**: Rich plugin and experiment metadata

### **Plugin Configuration Options**

All standard experiment configurations are supported:

```python
"config": {
    # Basic parameters
    "num_qubits": 3,
    "state_type": "GHZ|W|BELL|CLUSTER|CUSTOM",
    "shots": 1024,
    "sim_mode": "qasm|density",
    
    # Noise modeling
    "noise_enabled": True,
    "noise_type": "DEPOLARIZING|PHASE_DAMPING|...",
    "error_rate": 0.05,
    
    # Advanced features
    "enable_research_metrics": True,
    "multiple_runs": 3,
    "custom_params": {
        # Your custom parameters
    }
}
```

## 📁 Plugin Discovery

Plugins are automatically discovered from:
- `plugins/*.py` files
- Factory function `get_plugin()` 
- Plugin class with `get_experiments()` method

## 🧪 Testing Your Plugin

1. **Create your plugin**: Save as `plugins/my_plugin.py`

2. **Test discovery**:
```bash
python3 -c "
from src.experiments.plugins import get_plugin_info
for plugin in get_plugin_info():
    print(f'Plugin: {plugin[\"name\"]} v{plugin[\"version\"]}')
"
```

3. **List experiments**:
```bash
python3 main.py --list
# Look for your plugin experiments in new categories
```

4. **Run plugin experiment**:
```bash
python3 main.py --run my_experiment
```

## 🎯 Example Plugin Use Cases

### **Research Extensions**
- Custom decoherence models
- Novel entanglement measures  
- Hardware-specific noise models
- Advanced statistical analysis

### **Educational Tools**
- Interactive quantum tutorials
- Visualization experiments
- Step-by-step quantum algorithms
- Beginner-friendly explanations

### **Hardware Integration**
- Real quantum device backends
- Hardware-specific calibrations
- Device characterization experiments
- Performance benchmarking

## 📊 Plugin Best Practices

1. **Naming**: Use descriptive, unique experiment IDs
2. **Categories**: Create logical groupings with `plugin_` prefix
3. **Documentation**: Provide clear descriptions and metadata
4. **Error Handling**: Handle edge cases gracefully
5. **Testing**: Validate experiments work across different configurations

## 🔄 Plugin Lifecycle

1. **Discovery**: Framework scans `plugins/` directory
2. **Loading**: Imports and instantiates plugin classes
3. **Integration**: Merges plugin experiments with built-in catalog
4. **Execution**: Runs plugin experiments through standard framework

Your plugins integrate seamlessly with the existing experiment management, research analysis, and visualization systems!