"""
Plugin system for the Quantum Experiment Framework.

This module provides a plugin system for extending the framework
with custom experiments and analysis tools.
"""

import sys
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger("QuantumExperiment.Plugins")


class ExperimentPlugin:
    """Base class for experiment plugins."""
    
    def __init__(self):
        self.plugin_name = "unknown"
        self.version = "1.0.0"
        self.author = "Unknown"
    
    def get_plugin_info(self) -> Dict[str, Any]:
        """Return plugin metadata."""
        return {
            "name": self.plugin_name,
            "version": self.version,
            "author": self.author,
            "description": "No description provided"
        }
    
    def get_experiments(self) -> Dict[str, Dict[str, Any]]:
        """Return experiments provided by this plugin."""
        return {}
    
    def get_custom_components(self) -> List[Any]:
        """Return custom components provided by this plugin."""
        return []


def discover_plugins(plugin_dir: str = "plugins") -> List[Path]:
    """
    Discover plugin files in the plugin directory.
    
    Args:
        plugin_dir: Directory to search for plugins
        
    Returns:
        List of plugin file paths
    """
    plugin_path = Path(plugin_dir)
    if not plugin_path.exists():
        logger.info(f"Plugin directory {plugin_dir} does not exist")
        return []
    
    plugin_files = []
    for file_path in plugin_path.glob("*.py"):
        if file_path.name != "__init__.py":
            plugin_files.append(file_path)
    
    logger.info(f"Discovered {len(plugin_files)} plugin files")
    return plugin_files


def load_plugin_from_file(plugin_file: Path) -> Optional[ExperimentPlugin]:
    """
    Load a plugin from a Python file.
    
    Args:
        plugin_file: Path to the plugin file
        
    Returns:
        Plugin instance or None if loading failed
    """
    try:
        # Create module spec
        module_name = f"plugin_{plugin_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        
        if spec is None or spec.loader is None:
            logger.error(f"Could not create spec for plugin {plugin_file}")
            return None
        
        # Load the module
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Try to get plugin instance using factory function
        if hasattr(module, 'get_plugin'):
            plugin = module.get_plugin()
            if isinstance(plugin, ExperimentPlugin) or hasattr(plugin, 'get_experiments'):
                logger.info(f"Loaded plugin: {plugin_file.stem}")
                return plugin
            else:
                logger.warning(f"Plugin {plugin_file.stem} get_plugin() didn't return valid plugin")
        
        # Fallback: look for plugin classes
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type) and 
                attr != ExperimentPlugin and 
                (issubclass(attr, ExperimentPlugin) or hasattr(attr, 'get_experiments'))):
                plugin = attr()
                logger.info(f"Loaded plugin class: {attr_name} from {plugin_file.stem}")
                return plugin
        
        logger.warning(f"No valid plugin found in {plugin_file}")
        return None
        
    except Exception as e:
        logger.error(f"Failed to load plugin {plugin_file}: {e}")
        return None


def load_plugins(plugin_dir: str = "plugins") -> Dict[str, Dict[str, Any]]:
    """
    Load all plugins and return their experiments.
    
    Args:
        plugin_dir: Directory containing plugin files
        
    Returns:
        Dictionary of experiments from all loaded plugins
    """
    all_experiments = {}
    plugin_files = discover_plugins(plugin_dir)
    
    if not plugin_files:
        logger.info("No plugin files found")
        return all_experiments
    
    loaded_plugins = []
    
    for plugin_file in plugin_files:
        plugin = load_plugin_from_file(plugin_file)
        if plugin:
            loaded_plugins.append(plugin)
            
            # Get experiments from the plugin
            try:
                plugin_experiments = plugin.get_experiments()
                
                # Add plugin metadata to each experiment
                for exp_id, exp_config in plugin_experiments.items():
                    exp_config["plugin_source"] = plugin_file.stem
                    if hasattr(plugin, 'get_plugin_info'):
                        exp_config["plugin_info"] = plugin.get_plugin_info()
                    
                    all_experiments[exp_id] = exp_config
                
                logger.info(f"Plugin {plugin_file.stem} contributed {len(plugin_experiments)} experiments")
                
            except Exception as e:
                logger.error(f"Failed to get experiments from plugin {plugin_file.stem}: {e}")
    
    logger.info(f"Successfully loaded {len(loaded_plugins)} plugins with {len(all_experiments)} total experiments")
    
    return all_experiments


def get_plugin_info(plugin_dir: str = "plugins") -> List[Dict[str, Any]]:
    """
    Get information about all available plugins.
    
    Args:
        plugin_dir: Directory containing plugin files
        
    Returns:
        List of plugin information dictionaries
    """
    plugin_info = []
    plugin_files = discover_plugins(plugin_dir)
    
    for plugin_file in plugin_files:
        plugin = load_plugin_from_file(plugin_file)
        if plugin:
            info = {
                "file": plugin_file.name,
                "path": str(plugin_file)
            }
            
            if hasattr(plugin, 'get_plugin_info'):
                info.update(plugin.get_plugin_info())
            
            plugin_info.append(info)
    
    return plugin_info


__all__ = [
    "ExperimentPlugin",
    "load_plugins",
    "discover_plugins", 
    "load_plugin_from_file",
    "get_plugin_info"
]
