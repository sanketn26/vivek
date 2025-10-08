"""Plugin registry system for language-specific executors."""

import importlib
import inspect
import logging
from typing import Dict, List, Optional, Type, Any, Set
from pathlib import Path
import pkgutil

from .language_plugin import LanguagePlugin, LanguageConventions
from vivek.llm.models import LLMProvider


logger = logging.getLogger(__name__)


class ExecutorRegistry:
    """Registry for managing language-specific executor plugins.

    Provides plugin discovery, registration, and retrieval functionality
    for dynamic language support in the executor system.
    """

    def __init__(self):
        """Initialize the plugin registry."""
        self._plugins: Dict[str, LanguagePlugin] = {}
        self._language_mode_map: Dict[str, Dict[str, List[str]]] = {}
        self._loaded_modules: Set[str] = set()

    def register_plugin(self, plugin: LanguagePlugin) -> bool:
        """Register a language plugin.

        Args:
            plugin: LanguagePlugin instance to register

        Returns:
            True if registration successful, False otherwise
        """
        # Validate plugin
        if not isinstance(plugin, LanguagePlugin):
            logger.error(f"Invalid plugin type: {type(plugin)}")
            return False

        # Check for existing registration
        plugin_key = f"{plugin.language}_{plugin.name}"
        if plugin_key in self._plugins:
            logger.warning(f"Plugin {plugin_key} already registered. Overwriting.")

        try:
            # Register plugin
            self._plugins[plugin_key] = plugin

            # Update language-mode mapping
            for language in plugin.supported_languages:
                if language not in self._language_mode_map:
                    self._language_mode_map[language] = {}

                for mode in plugin.supported_modes:
                    if mode not in self._language_mode_map[language]:
                        self._language_mode_map[language][mode] = []
                    self._language_mode_map[language][mode].append(plugin_key)

            logger.info(f"Successfully registered plugin: {plugin_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to register plugin {plugin_key}: {e}")
            return False

    def unregister_plugin(self, language: str, plugin_name: str) -> bool:
        """Unregister a language plugin.

        Args:
            language: Language identifier
            plugin_name: Name of the plugin to unregister

        Returns:
            True if unregistration successful, False otherwise
        """
        plugin_key = f"{language}_{plugin_name}"

        if plugin_key not in self._plugins:
            logger.warning(f"Plugin {plugin_key} not found in registry")
            return False

        try:
            plugin = self._plugins[plugin_key]

            # Remove from main registry
            del self._plugins[plugin_key]

            # Update language-mode mapping
            for lang in plugin.supported_languages:
                if lang in self._language_mode_map:
                    for mode in plugin.supported_modes:
                        if mode in self._language_mode_map[lang]:
                            # Remove plugin from mode list
                            mode_plugins = self._language_mode_map[lang][mode]
                            if plugin_key in mode_plugins:
                                mode_plugins.remove(plugin_key)

                            # Clean up empty mode/language entries
                            if not mode_plugins:
                                del self._language_mode_map[lang][mode]
                    if not self._language_mode_map[lang]:
                        del self._language_mode_map[lang]

            logger.info(f"Successfully unregistered plugin: {plugin_key}")
            return True

        except Exception as e:
            logger.error(f"Failed to unregister plugin {plugin_key}: {e}")
            return False

    def discover_plugins(self, search_paths: Optional[List[str]] = None) -> int:
        """Discover and auto-register plugins from search paths.

        Args:
            search_paths: List of directory paths to search for plugins.
                         If None, searches in default plugin directories.

        Returns:
            Number of plugins discovered and registered
        """
        if search_paths is None:
            # Default search paths
            search_paths = [
                str(Path(__file__).parent.parent),  # vivek/llm/plugins/
                str(Path(__file__).parent.parent / "languages"),  # vivek/llm/plugins/languages/
            ]

        discovered_count = 0

        for search_path in search_paths:
            try:
                path = Path(search_path)
                if not path.exists():
                    continue

                # Search for Python files that might contain plugins
                for py_file in path.rglob("*.py"):
                    if py_file.name.startswith("__"):
                        continue

                    # Convert file path to module path
                    # __file__ is .../vivek/llm/plugins/base/registry.py
                    # We need to go up to the PROJECT ROOT (not package root)
                    # parent x5 = project root containing vivek/ package
                    project_root = Path(__file__).parent.parent.parent.parent.parent
                    relative_path = py_file.relative_to(project_root)
                    module_path = str(relative_path.with_suffix("")).replace("/", ".")

                    try:
                        # Import the module
                        if module_path not in self._loaded_modules:
                            module = importlib.import_module(module_path)
                            self._loaded_modules.add(module_path)

                            # Find plugin classes in the module
                            for name, obj in inspect.getmembers(module):
                                if (inspect.isclass(obj) and
                                    issubclass(obj, LanguagePlugin) and
                                    obj != LanguagePlugin):

                                    try:
                                        # Instantiate the plugin (no-arg constructor)
                                        plugin_instance = obj()
                                        if self.register_plugin(plugin_instance):
                                            discovered_count += 1
                                            logger.info(f"Auto-discovered plugin: {obj.__name__}")

                                    except Exception as e:
                                        logger.warning(f"Failed to instantiate plugin {name}: {e}")

                    except Exception as e:
                        logger.warning(f"Failed to import module {module_path}: {e}")

            except Exception as e:
                logger.error(f"Error searching path {search_path}: {e}")

        logger.info(f"Plugin discovery complete. Registered {discovered_count} plugins.")
        return discovered_count

    def get_plugin(self, language: str, plugin_name: Optional[str] = None) -> Optional[LanguagePlugin]:
        """Get a specific plugin by language and name.

        Args:
            language: Language identifier
            plugin_name: Optional plugin name for disambiguation

        Returns:
            LanguagePlugin instance or None if not found
        """
        if plugin_name:
            plugin_key = f"{language}_{plugin_name}"
            return self._plugins.get(plugin_key)

        # If no specific name, return the first available plugin for the language
        for plugin_key, plugin in self._plugins.items():
            if language in plugin.supported_languages:
                return plugin

        return None

    def get_plugins_for_language_mode(self, language: str, mode: str) -> List[LanguagePlugin]:
        """Get all plugins that support a specific language-mode combination.

        Args:
            language: Language identifier
            mode: Mode identifier

        Returns:
            List of compatible LanguagePlugin instances
        """
        plugins = []

        if language not in self._language_mode_map:
            return plugins

        if mode not in self._language_mode_map[language]:
            return plugins

        plugin_keys = self._language_mode_map[language][mode]

        for plugin_key in plugin_keys:
            plugin = self._plugins.get(plugin_key)
            if plugin:
                plugins.append(plugin)

        return plugins

    def get_best_plugin(self, language: str, mode: str) -> Optional[LanguagePlugin]:
        """Get the best available plugin for a language-mode combination.

        Args:
            language: Language identifier
            mode: Mode identifier

        Returns:
            Best LanguagePlugin instance or None if none available
        """
        plugins = self.get_plugins_for_language_mode(language, mode)

        if not plugins:
            return None

        # For now, return the first plugin. In the future, this could
        # implement more sophisticated selection logic (e.g., by priority, version, etc.)
        return plugins[0]

    def create_executor(self, language: str, mode: str, provider: LLMProvider,
                       plugin_name: Optional[str] = None, **kwargs) -> Optional[Any]:
        """Create an executor using the plugin system.

        Args:
            language: Language identifier
            mode: Mode identifier
            provider: LLM provider instance
            plugin_name: Optional specific plugin name to use
            **kwargs: Additional arguments for executor creation

        Returns:
            Executor instance or None if no suitable plugin found
        """
        # Get the appropriate plugin
        if plugin_name:
            plugin = self.get_plugin(language, plugin_name)
        else:
            plugin = self.get_best_plugin(language, mode)

        if not plugin:
            logger.warning(f"No plugin found for language={language}, mode={mode}")
            return None

        # Validate compatibility
        if not plugin.is_compatible(language, mode):
            logger.warning(f"Plugin {plugin.name} is not compatible with {language}/{mode}")
            return None

        try:
            # Create and return the executor
            return plugin.create_executor(provider, mode, **kwargs)
        except Exception as e:
            logger.error(f"Failed to create executor using plugin {plugin.name}: {e}")
            return None

    def list_plugins(self) -> Dict[str, Dict[str, Any]]:
        """List all registered plugins with their information.

        Returns:
            Dictionary mapping plugin keys to plugin information
        """
        return {key: plugin.get_plugin_info() for key, plugin in self._plugins.items()}

    def list_supported_combinations(self) -> Dict[str, List[str]]:
        """List all supported language-mode combinations.

        Returns:
            Dictionary mapping languages to lists of supported modes
        """
        combinations = {}

        for language, modes in self._language_mode_map.items():
            combinations[language] = list(modes.keys())

        return combinations

    def clear_registry(self) -> int:
        """Clear all registered plugins from the registry.

        Returns:
            Number of plugins that were cleared
        """
        count = len(self._plugins)
        self._plugins.clear()
        self._language_mode_map.clear()
        self._loaded_modules.clear()
        logger.info(f"Cleared {count} plugins from registry")
        return count

    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics and information.

        Returns:
            Dictionary containing registry statistics
        """
        return {
            "total_plugins": len(self._plugins),
            "supported_languages": len(self._language_mode_map),
            "loaded_modules": len(self._loaded_modules),
            "language_mode_combinations": sum(
                len(modes) for modes in self._language_mode_map.values()
            ),
            "plugins": self.list_plugins()
        }


# Global registry instance
_global_registry = ExecutorRegistry()


def get_registry() -> ExecutorRegistry:
    """Get the global plugin registry instance.

    Returns:
        Global ExecutorRegistry instance
    """
    return _global_registry


def register_plugin(plugin: LanguagePlugin) -> bool:
    """Register a plugin with the global registry.

    Args:
        plugin: LanguagePlugin instance to register

    Returns:
        True if registration successful, False otherwise
    """
    return _global_registry.register_plugin(plugin)


def discover_plugins(search_paths: Optional[List[str]] = None) -> int:
    """Discover and register plugins using the global registry.

    Args:
        search_paths: Optional list of paths to search for plugins

    Returns:
        Number of plugins discovered and registered
    """
    return _global_registry.discover_plugins(search_paths)


def create_executor(language: str, mode: str, provider: LLMProvider,
                   plugin_name: Optional[str] = None, **kwargs) -> Optional[Any]:
    """Create an executor using the global plugin registry.

    Args:
        language: Language identifier
        mode: Mode identifier
        provider: LLM provider instance
        plugin_name: Optional specific plugin name to use
        **kwargs: Additional arguments for executor creation

    Returns:
        Executor instance or None if no suitable plugin found
    """
    return _global_registry.create_executor(language, mode, provider, plugin_name, **kwargs)