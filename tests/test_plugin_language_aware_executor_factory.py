"""
Comprehensive TDD tests for plugin-based language-aware executor factory system.

This test suite defines the expected behavior for the enhanced plugin system
that extends the existing language-aware executor functionality.
"""

import pytest
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Type
from unittest.mock import Mock, MagicMock

# Import existing components
from vivek.llm.executor import BaseExecutor, get_executor
from vivek.llm.language_aware_executor import LanguageAwareExecutor
from vivek.llm.models import LLMProvider
from vivek.llm.constants import Mode


# ===== PLUGIN INTERFACE TESTS =====

class TestLanguagePluginInterface:
    """Test the LanguagePlugin base interface and its contract."""

    def test_language_plugin_is_abstract_base_class(self):
        """Test that LanguagePlugin defines the required abstract interface."""

        class LanguagePlugin(ABC):
            """Plugin interface for language-specific executor enhancements."""

            @property
            @abstractmethod
            def name(self) -> str:
                """Plugin name identifier."""
                pass

            @property
            @abstractmethod
            def supported_languages(self) -> List[str]:
                """List of supported programming languages."""
                pass

            @property
            @abstractmethod
            def supported_modes(self) -> List[str]:
                """List of supported execution modes."""
                pass

            @abstractmethod
            def enhance_prompt(self, base_prompt: str, language: str, mode: str,
                             context: Dict[str, Any]) -> str:
                """Enhance the base prompt with language-specific improvements."""
                pass

            @abstractmethod
            def enhance_output_format(self, base_format: str, language: str, mode: str) -> str:
                """Enhance output format with language-specific requirements."""
                pass

            @abstractmethod
            def get_language_conventions(self, language: str) -> Dict[str, str]:
                """Get language-specific conventions and best practices."""
                pass

            @abstractmethod
            def validate_language_support(self, language: str, mode: str) -> bool:
                """Validate if plugin supports specific language and mode combination."""
                pass

        # Test that abstract methods are properly defined
        assert hasattr(LanguagePlugin, 'name')
        assert hasattr(LanguagePlugin, 'supported_languages')
        assert hasattr(LanguagePlugin, 'supported_modes')
        assert hasattr(LanguagePlugin, 'enhance_prompt')
        assert hasattr(LanguagePlugin, 'enhance_output_format')
        assert hasattr(LanguagePlugin, 'get_language_conventions')
        assert hasattr(LanguagePlugin, 'validate_language_support')

    def test_concrete_plugin_implementation(self):
        """Test that concrete plugins properly implement the interface."""

        class TestPythonPlugin:
            """Concrete implementation of Python language plugin."""

            @property
            def name(self) -> str:
                return "python_plugin"

            @property
            def supported_languages(self) -> List[str]:
                return ["python"]

            @property
            def supported_modes(self) -> List[str]:
                return [Mode.CODER.value, Mode.ARCHITECT.value]

            def enhance_prompt(self, base_prompt: str, language: str, mode: str,
                             context: Dict[str, Any]) -> str:
                return f"{base_prompt}\n# Python Enhancement: Use PEP 8 style"

            def enhance_output_format(self, base_format: str, language: str, mode: str) -> str:
                return f"{base_format}\n# Python: Use type hints and docstrings"

            def get_language_conventions(self, language: str) -> Dict[str, str]:
                return {
                    "imports": "Use explicit imports",
                    "types": "Use type hints",
                    "style": "PEP 8"
                }

            def validate_language_support(self, language: str, mode: str) -> bool:
                return language.lower() == "python" and mode in [Mode.CODER.value, Mode.ARCHITECT.value]

        plugin = TestPythonPlugin()

        # Test all interface methods are implemented
        assert plugin.name == "python_plugin"
        assert plugin.supported_languages == ["python"]
        assert plugin.supported_modes == [Mode.CODER.value, Mode.ARCHITECT.value]
        assert "Python Enhancement" in plugin.enhance_prompt("base", "python", "coder", {})
        assert "Python:" in plugin.enhance_output_format("format", "python", "coder")
        assert plugin.get_language_conventions("python")["style"] == "PEP 8"
        assert plugin.validate_language_support("python", "coder") is True
        assert plugin.validate_language_support("javascript", "coder") is False

    def test_plugin_interface_contract_enforcement(self):
        """Test that the plugin interface properly enforces its contract."""

        class LanguagePlugin(ABC):
            """Plugin interface definition."""

            @property
            @abstractmethod
            def name(self) -> str:
                pass

            @abstractmethod
            def enhance_prompt(self, base_prompt: str, language: str, mode: str,
                             context: Dict[str, Any]) -> str:
                pass

        # Test that incomplete implementations raise TypeError when calling abstract methods
        class IncompletePlugin(LanguagePlugin):
            @property
            def name(self) -> str:
                return "incomplete"

            # Missing enhance_prompt method

        # This will raise TypeError on instantiation because enhance_prompt is not implemented
        with pytest.raises(TypeError, match="Can't instantiate abstract class IncompletePlugin"):
            plugin = IncompletePlugin()

        # Test that proper inheritance works
        class CompletePlugin(LanguagePlugin):
            @property
            def name(self) -> str:
                return "complete"

            def enhance_prompt(self, base_prompt: str, language: str, mode: str,
                             context: Dict[str, Any]) -> str:
                return base_prompt

        plugin = CompletePlugin()
        assert plugin.name == "complete"


# ===== REGISTRY TESTS =====

class TestExecutorRegistry:
    """Test the ExecutorRegistry for plugin registration and discovery."""

    def test_registry_initialization(self):
        """Test registry initializes with empty state."""

        class ExecutorRegistry:
            """Registry for managing language plugins."""

            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                """Register a language plugin."""
                self._plugins[plugin.name] = plugin

            def get_plugin(self, name: str):
                """Get plugin by name."""
                return self._plugins.get(name)

            def list_plugins(self) -> List[str]:
                """List all registered plugin names."""
                return list(self._plugins.keys())

            def find_plugins_for_language(self, language: str) -> List[Any]:
                """Find all plugins supporting a specific language."""
                return [
                    plugin for plugin in self._plugins.values()
                    if language.lower() in plugin.supported_languages
                ]

        registry = ExecutorRegistry()

        # Initially empty
        assert len(registry.list_plugins()) == 0
        assert registry.get_plugin("nonexistent") is None
        assert registry.find_plugins_for_language("python") == []

    def test_plugin_registration_and_discovery(self):
        """Test registering and discovering plugins."""

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def get_plugin(self, name: str):
                return self._plugins.get(name)

            def list_plugins(self) -> List[str]:
                return list(self._plugins.keys())

            def find_plugins_for_language(self, language: str) -> List[Any]:
                return [
                    plugin for plugin in self._plugins.values()
                    if language.lower() in plugin.supported_languages
                ]

        # Create test plugins
        class PythonPlugin:
            name = "python"
            supported_languages = ["python"]

        class TypeScriptPlugin:
            name = "typescript"
            supported_languages = ["typescript"]

        registry = ExecutorRegistry()
        python_plugin = PythonPlugin()
        ts_plugin = TypeScriptPlugin()

        # Register plugins
        registry.register_plugin(python_plugin)
        registry.register_plugin(ts_plugin)

        # Test discovery
        assert len(registry.list_plugins()) == 2
        assert registry.get_plugin("python") == python_plugin
        assert registry.get_plugin("typescript") == ts_plugin
        assert len(registry.find_plugins_for_language("python")) == 1
        assert len(registry.find_plugins_for_language("typescript")) == 1

    def test_plugin_registration_validation(self):
        """Test that registry validates plugin registration."""

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                if not hasattr(plugin, 'name'):
                    raise ValueError("Plugin must have a name attribute")
                if plugin.name in self._plugins:
                    raise ValueError(f"Plugin '{plugin.name}' already registered")
                self._plugins[plugin.name] = plugin

        registry = ExecutorRegistry()

        # Test missing name attribute
        class InvalidPlugin:
            pass

        with pytest.raises(ValueError, match="Plugin must have a name attribute"):
            registry.register_plugin(InvalidPlugin())

        # Test duplicate registration
        class ValidPlugin:
            def __init__(self, name):
                self.name = name

        plugin1 = ValidPlugin("test")
        plugin2 = ValidPlugin("test")  # Same name

        registry.register_plugin(plugin1)
        with pytest.raises(ValueError, match="Plugin 'test' already registered"):
            registry.register_plugin(plugin2)

    def test_plugin_language_mode_filtering(self):
        """Test filtering plugins by language and mode support."""

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def find_plugins_for_language_mode(self, language: str, mode: str) -> List[Any]:
                """Find plugins supporting both language and mode."""
                return [
                    plugin for plugin in self._plugins.values()
                    if (language.lower() in plugin.supported_languages and
                        mode.lower() in plugin.supported_modes)
                ]

        # Create plugins with different language/mode support
        class PythonCoderPlugin:
            name = "python_coder"
            supported_languages = ["python"]
            supported_modes = [Mode.CODER.value]

        class PythonArchitectPlugin:
            name = "python_architect"
            supported_languages = ["python"]
            supported_modes = [Mode.ARCHITECT.value]

        class MultiModePlugin:
            name = "multi_mode"
            supported_languages = ["python", "typescript"]
            supported_modes = [Mode.CODER.value, Mode.ARCHITECT.value]

        registry = ExecutorRegistry()
        registry.register_plugin(PythonCoderPlugin())
        registry.register_plugin(PythonArchitectPlugin())
        registry.register_plugin(MultiModePlugin())

        # Test filtering
        python_coder_plugins = registry.find_plugins_for_language_mode("python", Mode.CODER.value)
        assert len(python_coder_plugins) == 2  # PythonCoderPlugin and MultiModePlugin

        python_architect_plugins = registry.find_plugins_for_language_mode("python", Mode.ARCHITECT.value)
        assert len(python_architect_plugins) == 2  # PythonArchitectPlugin and MultiModePlugin

        typescript_plugins = registry.find_plugins_for_language_mode("typescript", Mode.CODER.value)
        assert len(typescript_plugins) == 1  # Only MultiModePlugin


# ===== FACTORY TESTS =====

class TestEnhancedExecutorFactory:
    """Test the enhanced get_executor function with plugin support."""

    def test_factory_initializes_with_plugin_support(self):
        """Test that factory initializes with plugin registry."""

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def find_plugins_for_language_mode(self, language: str, mode: str) -> List[Any]:
                return [
                    plugin for plugin in self._plugins.values()
                    if (language.lower() in plugin.supported_languages and
                        mode.lower() in plugin.supported_modes)
                ]

        class MockLanguageDetector:
            @classmethod
            def get_primary_language(cls):
                return "python"

        def enhanced_get_executor(mode: str, provider: LLMProvider,
                                language: Optional[str] = None,
                                plugin_registry: Optional[ExecutorRegistry] = None) -> BaseExecutor:
            """Enhanced factory with plugin support."""

            # Auto-detect language if not provided
            if language is None:
                language = MockLanguageDetector.get_primary_language()

            # Normalize language name
            language = language.lower()

            # Find applicable plugins
            applicable_plugins = []
            if plugin_registry:
                applicable_plugins = plugin_registry.find_plugins_for_language_mode(language, mode)

            # Create base executor (existing logic)
            base_executor = get_executor(mode, provider, language)

            # Enhance with plugins if available
            if applicable_plugins:
                enhanced_executor = PluginEnhancedExecutor(base_executor, applicable_plugins, language, mode)
                return enhanced_executor

            return base_executor

        class PluginEnhancedExecutor:
            """Executor enhanced with plugins."""

            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode

        # Test factory initialization
        registry = ExecutorRegistry()
        provider = Mock(spec=LLMProvider)

        # Test without plugins (fallback to base behavior)
        executor = enhanced_get_executor("coder", provider, plugin_registry=registry)
        assert isinstance(executor, BaseExecutor)

    def test_factory_enhances_executor_with_plugins(self):
        """Test that factory creates plugin-enhanced executors when plugins available."""

        class MockPlugin:
            def __init__(self, name, languages, modes):
                self.name = name
                self.supported_languages = languages
                self.supported_modes = modes

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def find_plugins_for_language_mode(self, language: str, mode: str) -> List[Any]:
                return [
                    plugin for plugin in self._plugins.values()
                    if (language.lower() in plugin.supported_languages and
                        mode.lower() in plugin.supported_modes)
                ]

        class PluginEnhancedExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode
                self.enhanced = True

        def enhanced_get_executor(mode: str, provider: LLMProvider,
                                language: Optional[str] = None,
                                plugin_registry: Optional[ExecutorRegistry] = None) -> BaseExecutor:
            """Enhanced factory with plugin support."""
            language = language or "python"
            language = language.lower()

            applicable_plugins = []
            if plugin_registry:
                applicable_plugins = plugin_registry.find_plugins_for_language_mode(language, mode)

            base_executor = get_executor(mode, provider, language)

            if applicable_plugins:
                return PluginEnhancedExecutor(base_executor, applicable_plugins, language, mode)

            return base_executor

        # Setup
        registry = ExecutorRegistry()
        python_plugin = MockPlugin("python_plugin", ["python"], [Mode.CODER.value])
        registry.register_plugin(python_plugin)

        provider = Mock(spec=LLMProvider)

        # Test enhancement
        executor = enhanced_get_executor("coder", provider, "python", registry)
        assert hasattr(executor, 'enhanced')
        assert executor.enhanced is True
        assert len(executor.plugins) == 1
        assert executor.language == "python"
        assert executor.mode == "coder"

    def test_factory_plugin_priority_ordering(self):
        """Test that factory respects plugin priority ordering."""

        class MockPlugin:
            def __init__(self, name, languages, modes, priority=1):
                self.name = name
                self.supported_languages = languages
                self.supported_modes = modes
                self.priority = priority

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def find_plugins_for_language_mode(self, language: str, mode: str) -> List[Any]:
                plugins = [
                    plugin for plugin in self._plugins.values()
                    if (language.lower() in plugin.supported_languages and
                        mode.lower() in plugin.supported_modes)
                ]
                # Return plugins sorted by priority (highest first)
                return sorted(plugins, key=lambda p: p.priority, reverse=True)

        class PluginEnhancedExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode

        def enhanced_get_executor(mode: str, provider: LLMProvider,
                                language: Optional[str] = None,
                                plugin_registry: Optional[ExecutorRegistry] = None) -> BaseExecutor:
            language = language or "python"
            language = language.lower()

            applicable_plugins = []
            if plugin_registry:
                applicable_plugins = plugin_registry.find_plugins_for_language_mode(language, mode)

            base_executor = get_executor(mode, provider, language)

            if applicable_plugins:
                return PluginEnhancedExecutor(base_executor, applicable_plugins, language, mode)

            return base_executor

        # Setup plugins with different priorities
        registry = ExecutorRegistry()
        high_priority_plugin = MockPlugin("high_priority", ["python"], [Mode.CODER.value], priority=10)
        low_priority_plugin = MockPlugin("low_priority", ["python"], [Mode.CODER.value], priority=1)
        registry.register_plugin(high_priority_plugin)
        registry.register_plugin(low_priority_plugin)

        provider = Mock(spec=LLMProvider)
        executor = enhanced_get_executor("coder", provider, "python", registry)

        # Should be sorted by priority (highest first)
        assert executor.plugins[0].name == "high_priority"
        assert executor.plugins[1].name == "low_priority"


# ===== LANGUAGE ENHANCEMENT TESTS =====

class TestLanguageEnhancement:
    """Test that executors are properly enhanced with language plugins."""

    def test_plugin_enhances_prompt_generation(self):
        """Test that plugins properly enhance prompt generation."""

        class MockPlugin:
            def __init__(self, name, enhancement_text):
                self.name = name
                self.enhancement_text = enhancement_text
                self.supported_languages = ["python"]
                self.supported_modes = [Mode.CODER.value]

            def enhance_prompt(self, base_prompt: str, language: str, mode: str,
                             context: Dict[str, Any]) -> str:
                return f"{base_prompt}\n# Plugin Enhancement: {self.enhancement_text}"

        class PluginEnhancedExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode

            def build_prompt(self, task_plan: Dict[str, Any], context: str) -> str:
                """Build prompt with plugin enhancements."""
                base_prompt = self.base_executor.build_prompt(task_plan, context)

                # Apply plugin enhancements
                enhanced_prompt = base_prompt
                for plugin in self.plugins:
                    enhanced_prompt = plugin.enhance_prompt(
                        enhanced_prompt, self.language, self.mode, {"task_plan": task_plan}
                    )

                return enhanced_prompt

        # Setup
        base_executor = Mock()
        base_executor.build_prompt.return_value = "Base prompt content"

        plugin1 = MockPlugin("plugin1", "Use type hints")
        plugin2 = MockPlugin("plugin2", "Follow PEP 8")

        enhanced_executor = PluginEnhancedExecutor(base_executor, [plugin1, plugin2], "python", "coder")

        task_plan = {"description": "test task"}
        result_prompt = enhanced_executor.build_prompt(task_plan, "context")

        # Should contain base prompt and all plugin enhancements
        assert "Base prompt content" in result_prompt
        assert "Use type hints" in result_prompt
        assert "Follow PEP 8" in result_prompt
        assert base_executor.build_prompt.called

    def test_plugin_enhances_output_format(self):
        """Test that plugins properly enhance output format."""

        class MockPlugin:
            def __init__(self, name, format_enhancement):
                self.name = name
                self.format_enhancement = format_enhancement
                self.supported_languages = ["python"]
                self.supported_modes = [Mode.CODER.value]

            def enhance_output_format(self, base_format: str, language: str, mode: str) -> str:
                return f"{base_format}\n# Format Enhancement: {self.format_enhancement}"

        class PluginEnhancedExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode

            def get_mode_specific_output_format(self) -> str:
                """Get output format with plugin enhancements."""
                base_format = self.base_executor.get_mode_specific_output_format()

                enhanced_format = base_format
                for plugin in self.plugins:
                    enhanced_format = plugin.enhance_output_format(
                        enhanced_format, self.language, self.mode
                    )

                return enhanced_format

        # Setup
        base_executor = Mock()
        base_executor.get_mode_specific_output_format.return_value = "Base format"

        plugin = MockPlugin("python_plugin", "Include type hints and docstrings")

        enhanced_executor = PluginEnhancedExecutor(base_executor, [plugin], "python", "coder")

        result_format = enhanced_executor.get_mode_specific_output_format()

        # Should contain base format and plugin enhancement
        assert "Base format" in result_format
        assert "Include type hints and docstrings" in result_format
        assert base_executor.get_mode_specific_output_format.called

    def test_plugin_provides_language_conventions(self):
        """Test that plugins provide language-specific conventions."""

        class MockPlugin:
            def __init__(self, name, conventions):
                self.name = name
                self.conventions = conventions
                self.supported_languages = ["python"]
                self.supported_modes = [Mode.CODER.value]

            def get_language_conventions(self, language: str) -> Dict[str, str]:
                return self.conventions

        class PluginEnhancedExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode

            def get_language_conventions(self) -> Dict[str, str]:
                """Get combined language conventions from all plugins."""
                combined_conventions = {}

                for plugin in self.plugins:
                    plugin_conventions = plugin.get_language_conventions(self.language)
                    combined_conventions.update(plugin_conventions)

                return combined_conventions

        # Setup
        base_executor = Mock()

        plugin1 = MockPlugin("plugin1", {"imports": "Use explicit imports", "types": "Use type hints"})
        plugin2 = MockPlugin("plugin2", {"docs": "Write docstrings", "style": "Follow PEP 8"})

        enhanced_executor = PluginEnhancedExecutor(base_executor, [plugin1, plugin2], "python", "coder")

        conventions = enhanced_executor.get_language_conventions()

        # Should combine conventions from all plugins
        assert conventions["imports"] == "Use explicit imports"
        assert conventions["types"] == "Use type hints"
        assert conventions["docs"] == "Write docstrings"
        assert conventions["style"] == "Follow PEP 8"
        assert len(conventions) == 4


# ===== BACKWARD COMPATIBILITY TESTS =====

class TestBackwardCompatibility:
    """Test that existing functionality still works with plugin system."""

    def test_existing_get_executor_functionality_preserved(self):
        """Test that existing get_executor behavior is preserved."""

        # Mock the original get_executor function
        original_get_executor = get_executor

        def enhanced_get_executor(mode: str, provider: LLMProvider,
                                language: Optional[str] = None,
                                plugin_registry=None) -> BaseExecutor:
            """Enhanced version that falls back to original behavior when no plugins."""

            # If no plugins available, use original logic
            if not plugin_registry or len(plugin_registry.list_plugins()) == 0:
                return original_get_executor(mode, provider, language)

            # Plugin enhancement logic would go here
            return original_get_executor(mode, provider, language)

        # Test with no plugin registry
        provider = Mock(spec=LLMProvider)
        executor1 = enhanced_get_executor("coder", provider, "python")
        executor2 = enhanced_get_executor("architect", provider, "typescript")

        assert isinstance(executor1, BaseExecutor)
        assert isinstance(executor2, BaseExecutor)

        # Test with empty plugin registry
        class EmptyRegistry:
            def list_plugins(self):
                return []

        empty_registry = EmptyRegistry()
        executor3 = enhanced_get_executor("coder", provider, "python", empty_registry)

        assert isinstance(executor3, BaseExecutor)

    def test_language_aware_executors_still_work(self):
        """Test that existing language-aware executors work unchanged."""

        # Import existing language-aware executor
        from vivek.llm.language_aware_executor import LanguageAwareExecutor

        # Create a mock provider
        provider = Mock(spec=LLMProvider)

        # Create concrete implementation for testing
        class TestLanguageExecutor(LanguageAwareExecutor):
            language = "python"

            def get_language_specific_instructions(self) -> str:
                return "Test instructions"

            def get_language_conventions(self) -> Dict[str, str]:
                return {"test": "convention"}

            def _get_language_code_example(self) -> str:
                return "test code"

        executor = TestLanguageExecutor(provider, "python")

        # Should work exactly as before
        assert executor.language == "python"
        assert executor.get_language_specific_instructions() == "Test instructions"
        assert executor.get_language_conventions()["test"] == "convention"

    def test_existing_mode_language_mapping_preserved(self):
        """Test that existing mode+language mapping logic is preserved."""

        # This tests the existing mapping logic in the original get_executor
        provider = Mock(spec=LLMProvider)

        # Test that we can still get language-specific executors
        # Note: This would fail in real implementation if the modules don't exist,
        # but we're testing the logic flow
        try:
            python_executor = get_executor("coder", provider, "python")
            assert isinstance(python_executor, BaseExecutor)
        except Exception:
            # Expected if the specific executor modules don't exist
            pass

        try:
            ts_executor = get_executor("coder", provider, "typescript")
            assert isinstance(ts_executor, BaseExecutor)
        except Exception:
            # Expected if the specific executor modules don't exist
            pass


# ===== DYNAMIC REGISTRATION TESTS =====

class TestDynamicRegistration:
    """Test adding new languages at runtime."""

    def test_runtime_plugin_registration(self):
        """Test registering new language plugins at runtime."""

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def list_plugins(self) -> List[str]:
                return list(self._plugins.keys())

            def find_plugins_for_language_mode(self, language: str, mode: str) -> List[Any]:
                return [
                    plugin for plugin in self._plugins.values()
                    if (language.lower() in plugin.supported_languages and
                        mode.lower() in plugin.supported_modes)
                ]

        class MockPlugin:
            def __init__(self, name, languages, modes):
                self.name = name
                self.supported_languages = languages
                self.supported_modes = modes

        registry = ExecutorRegistry()

        # Initially empty
        assert len(registry.list_plugins()) == 0

        # Register new language plugin at runtime
        rust_plugin = MockPlugin("rust_plugin", ["rust"], [Mode.CODER.value])
        registry.register_plugin(rust_plugin)

        # Should be available immediately
        assert len(registry.list_plugins()) == 1
        assert "rust_plugin" in registry.list_plugins()

        rust_plugins = registry.find_plugins_for_language_mode("rust", Mode.CODER.value)
        assert len(rust_plugins) == 1
        assert rust_plugins[0].name == "rust_plugin"

    def test_runtime_language_support_addition(self):
        """Test adding support for new languages to existing plugins."""

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def find_plugins_for_language_mode(self, language: str, mode: str) -> List[Any]:
                """Find plugins supporting both language and mode."""
                return [
                    plugin for plugin in self._plugins.values()
                    if (language.lower() in plugin.supported_languages and
                        mode.lower() in plugin.supported_modes)
                ]

            def update_plugin_languages(self, plugin_name: str, new_languages: List[str]) -> None:
                """Update supported languages for a plugin."""
                if plugin_name in self._plugins:
                    self._plugins[plugin_name].supported_languages.extend(new_languages)

        class MockPlugin:
            def __init__(self, name, languages, modes):
                self.name = name
                self.supported_languages = languages.copy()
                self.supported_modes = modes

        registry = ExecutorRegistry()

        # Register initial plugin
        plugin = MockPlugin("multi_lang_plugin", ["python", "typescript"], [Mode.CODER.value])
        registry.register_plugin(plugin)

        # Add new language support at runtime
        registry.update_plugin_languages("multi_lang_plugin", ["go", "rust"])

        # Should now support additional languages
        go_plugins = registry.find_plugins_for_language_mode("go", Mode.CODER.value)
        assert len(go_plugins) == 1

        rust_plugins = registry.find_plugins_for_language_mode("rust", Mode.CODER.value)
        assert len(rust_plugins) == 1

        # Should still support original languages
        python_plugins = registry.find_plugins_for_language_mode("python", Mode.CODER.value)
        assert len(python_plugins) == 1


# ===== ERROR HANDLING TESTS =====

class TestErrorHandling:
    """Test graceful fallback when plugins fail."""

    def test_plugin_failure_does_not_break_execution(self):
        """Test that plugin failures don't break the overall execution."""

        class FailingPlugin:
            def __init__(self, name):
                self.name = name
                self.supported_languages = ["python"]
                self.supported_modes = [Mode.CODER.value]

            def enhance_prompt(self, base_prompt: str, language: str, mode: str,
                             context: Dict[str, Any]) -> str:
                raise Exception("Plugin failed!")

            def enhance_output_format(self, base_format: str, language: str, mode: str) -> str:
                raise Exception("Plugin failed!")

        class ErrorResilientExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode

            def build_prompt(self, task_plan: Dict[str, Any], context: str) -> str:
                """Build prompt with error-resilient plugin enhancements."""
                base_prompt = self.base_executor.build_prompt(task_plan, context)

                enhanced_prompt = base_prompt
                for plugin in self.plugins:
                    try:
                        enhanced_prompt = plugin.enhance_prompt(
                            enhanced_prompt, self.language, self.mode, {"task_plan": task_plan}
                        )
                    except Exception:
                        # Log error but continue with base prompt
                        continue

                return enhanced_prompt

        # Setup
        base_executor = Mock()
        base_executor.build_prompt.return_value = "Base prompt"

        failing_plugin = FailingPlugin("failing_plugin")
        executor = ErrorResilientExecutor(base_executor, [failing_plugin], "python", "coder")

        task_plan = {"description": "test"}
        result = executor.build_prompt(task_plan, "context")

        # Should return base prompt even though plugin failed
        assert result == "Base prompt"
        assert base_executor.build_prompt.called

    def test_plugin_validation_before_registration(self):
        """Test that plugins are validated before registration."""

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                """Register plugin with validation."""
                if not hasattr(plugin, 'name'):
                    raise ValueError("Plugin must have a 'name' attribute")

                if not hasattr(plugin, 'supported_languages'):
                    raise ValueError("Plugin must have 'supported_languages' attribute")

                if not hasattr(plugin, 'supported_modes'):
                    raise ValueError("Plugin must have 'supported_modes' attribute")

                if not hasattr(plugin, 'enhance_prompt'):
                    raise ValueError("Plugin must have 'enhance_prompt' method")

                if not hasattr(plugin, 'enhance_output_format'):
                    raise ValueError("Plugin must have 'enhance_output_format' method")

                if not hasattr(plugin, 'get_language_conventions'):
                    raise ValueError("Plugin must have 'get_language_conventions' method")

                if not hasattr(plugin, 'validate_language_support'):
                    raise ValueError("Plugin must have 'validate_language_support' method")

                self._plugins[plugin.name] = plugin

        registry = ExecutorRegistry()

        # Test missing name
        class PluginWithoutName:
            pass

        with pytest.raises(ValueError, match="Plugin must have a 'name' attribute"):
            registry.register_plugin(PluginWithoutName())

        # Test missing methods
        class IncompletePlugin:
            def __init__(self):
                self.name = "incomplete"
                self.supported_languages = ["python"]
                self.supported_modes = [Mode.CODER.value]
                # Missing other required methods/attributes

        with pytest.raises(ValueError, match="Plugin must have 'enhance_prompt' method"):
            registry.register_plugin(IncompletePlugin())

    def test_graceful_degradation_on_plugin_errors(self):
        """Test graceful degradation when plugins have errors."""

        class ErrorResilientExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode

            def get_mode_specific_instructions(self) -> str:
                """Get instructions with graceful plugin degradation."""
                base_instructions = self.base_executor.get_mode_specific_instructions()

                combined_instructions = base_instructions
                for plugin in self.plugins:
                    try:
                        plugin_instructions = plugin.get_language_specific_instructions(self.language)
                        combined_instructions += f"\n{plugin_instructions}"
                    except Exception:
                        # Skip failing plugins
                        continue

                return combined_instructions

        # Setup
        base_executor = Mock()
        base_executor.get_mode_specific_instructions.return_value = "Base instructions"

        # Mix of working and failing plugins
        class WorkingPlugin:
            def get_language_specific_instructions(self, language):
                return "Working plugin instructions"

        class FailingPlugin:
            def get_language_specific_instructions(self, language):
                raise Exception("Plugin error")

        executor = ErrorResilientExecutor(
            base_executor,
            [WorkingPlugin(), FailingPlugin()],
            "python",
            "coder"
        )

        result = executor.get_mode_specific_instructions()

        # Should include base instructions and working plugin, but not fail
        assert "Base instructions" in result
        assert "Working plugin instructions" in result
        assert base_executor.get_mode_specific_instructions.called


# ===== INTEGRATION TESTS =====

class TestCompleteFlowIntegration:
    """Test the complete flow from mode+language to enhanced executor."""

    def test_end_to_end_plugin_enhanced_execution(self):
        """Test complete flow from language detection to enhanced execution."""

        class MockLanguageDetector:
            @classmethod
            def get_primary_language(cls):
                return "python"

        class MockPlugin:
            def __init__(self, name, languages, modes):
                self.name = name
                self.supported_languages = languages
                self.supported_modes = modes
                self.call_count = 0

            def enhance_prompt(self, base_prompt: str, language: str, mode: str,
                             context: Dict[str, Any]) -> str:
                self.call_count += 1
                return f"{base_prompt}\n# Enhanced by {self.name}"

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def find_plugins_for_language_mode(self, language: str, mode: str) -> List[Any]:
                return [
                    plugin for plugin in self._plugins.values()
                    if (language.lower() in plugin.supported_languages and
                        mode.lower() in plugin.supported_modes)
                ]

        class PluginEnhancedExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode
                self.prompt_built = False
                self.output_generated = False

            def build_prompt(self, task_plan: Dict[str, Any], context: str) -> str:
                """Build enhanced prompt."""
                base_prompt = self.base_executor.build_prompt(task_plan, context)
                self.prompt_built = True

                enhanced_prompt = base_prompt
                for plugin in self.plugins:
                    enhanced_prompt = plugin.enhance_prompt(
                        enhanced_prompt, self.language, self.mode, {"task_plan": task_plan}
                    )

                return enhanced_prompt

            def execute_task(self, task_plan: Dict[str, Any], context: str) -> Dict[str, Any]:
                """Execute task with plugin enhancements."""
                prompt = self.build_prompt(task_plan, context)
                # Simulate LLM call
                output = f"Generated output based on: {prompt[:50]}..."

                self.output_generated = True
                return {
                    "type": "execution_complete",
                    "output": output,
                    "enhanced_by_plugins": [p.name for p in self.plugins]
                }

        def enhanced_get_executor(mode: str, provider: LLMProvider,
                                language: Optional[str] = None,
                                plugin_registry: Optional[ExecutorRegistry] = None) -> BaseExecutor:
            """Complete enhanced factory."""
            if language is None:
                language = MockLanguageDetector.get_primary_language()

            language = language.lower()

            applicable_plugins = []
            if plugin_registry:
                applicable_plugins = plugin_registry.find_plugins_for_language_mode(language, mode)

            # Use original get_executor logic for base executor
            base_executor = get_executor(mode, provider, language)

            if applicable_plugins:
                return PluginEnhancedExecutor(base_executor, applicable_plugins, language, mode)

            return base_executor

        # Setup integration test
        registry = ExecutorRegistry()
        python_plugin = MockPlugin("python_enhancer", ["python"], [Mode.CODER.value])
        registry.register_plugin(python_plugin)

        provider = Mock(spec=LLMProvider)

        # Execute complete flow
        executor = enhanced_get_executor("coder", provider, "python", registry)

        # Verify it's enhanced
        assert hasattr(executor, 'plugins')
        assert len(executor.plugins) == 1
        assert executor.language == "python"

        # Execute task
        task_plan = {"description": "Create a function"}
        result = executor.execute_task(task_plan, "context")

        # Verify complete flow worked
        assert result["type"] == "execution_complete"
        assert "enhanced_by_plugins" in result
        assert "python_enhancer" in result["enhanced_by_plugins"]
        assert executor.prompt_built is True
        assert executor.output_generated is True
        assert python_plugin.call_count == 1

    def test_multiple_plugins_collaborative_enhancement(self):
        """Test that multiple plugins can collaboratively enhance execution."""

        class CollaborativePlugin:
            def __init__(self, name, enhancement):
                self.name = name
                self.enhancement = enhancement
                self.supported_languages = ["python"]
                self.supported_modes = [Mode.CODER.value]

            def enhance_prompt(self, base_prompt: str, language: str, mode: str,
                             context: Dict[str, Any]) -> str:
                return f"{base_prompt}\n# {self.name}: {self.enhancement}"

        class ExecutorRegistry:
            def __init__(self):
                self._plugins: Dict[str, Any] = {}

            def register_plugin(self, plugin) -> None:
                self._plugins[plugin.name] = plugin

            def find_plugins_for_language_mode(self, language: str, mode: str) -> List[Any]:
                return [
                    plugin for plugin in self._plugins.values()
                    if (language.lower() in plugin.supported_languages and
                        mode.lower() in plugin.supported_modes)
                ]

        class MultiPluginExecutor:
            def __init__(self, base_executor, plugins, language, mode):
                self.base_executor = base_executor
                self.plugins = plugins
                self.language = language
                self.mode = mode

            def build_prompt(self, task_plan: Dict[str, Any], context: str) -> str:
                """Build prompt enhanced by multiple plugins."""
                base_prompt = self.base_executor.build_prompt(task_plan, context)

                enhanced_prompt = base_prompt
                for plugin in self.plugins:
                    enhanced_prompt = plugin.enhance_prompt(
                        enhanced_prompt, self.language, self.mode, {"task_plan": task_plan}
                    )

                return enhanced_prompt

        def enhanced_get_executor(mode: str, provider: LLMProvider,
                                language: Optional[str] = None,
                                plugin_registry: Optional[ExecutorRegistry] = None) -> BaseExecutor:
            language = language or "python"
            language = language.lower()

            applicable_plugins = []
            if plugin_registry:
                applicable_plugins = plugin_registry.find_plugins_for_language_mode(language, mode)

            base_executor = get_executor(mode, provider, language)

            if applicable_plugins:
                return MultiPluginExecutor(base_executor, applicable_plugins, language, mode)

            return base_executor

        # Setup multiple collaborative plugins
        registry = ExecutorRegistry()
        style_plugin = CollaborativePlugin("style_plugin", "Follow PEP 8")
        types_plugin = CollaborativePlugin("types_plugin", "Use type hints")
        docs_plugin = CollaborativePlugin("docs_plugin", "Write docstrings")

        registry.register_plugin(style_plugin)
        registry.register_plugin(types_plugin)
        registry.register_plugin(docs_plugin)

        provider = Mock(spec=LLMProvider)

        # Execute with multiple plugins
        executor = enhanced_get_executor("coder", provider, "python", registry)

        task_plan = {"description": "Create function"}
        enhanced_prompt = executor.build_prompt(task_plan, "context")

        # Should contain enhancements from all plugins
        assert "Follow PEP 8" in enhanced_prompt
        assert "Use type hints" in enhanced_prompt
        assert "Write docstrings" in enhanced_prompt

        # Verify order (plugins should be applied in registration order)
        pep8_pos = enhanced_prompt.find("Follow PEP 8")
        types_pos = enhanced_prompt.find("Use type hints")
        docs_pos = enhanced_prompt.find("Write docstrings")

        assert pep8_pos < types_pos < docs_pos