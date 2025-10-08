"""Python Language Plugin implementation."""

from typing import Dict, Any, Optional, Type
from dataclasses import dataclass, field

from vivek.llm.plugins.base.language_plugin import LanguagePlugin, LanguageConventions
from vivek.llm.models import LLMProvider
from vivek.llm.constants import Mode


@dataclass
class PythonConventions(LanguageConventions):
    """Python-specific conventions (simplified)."""

    def __post_init__(self):
        if not self.language:
            self.language = "python"
        if not self.extensions:
            self.extensions = [".py", ".pyi"]


class PythonLanguagePlugin(LanguagePlugin):
    """Python language plugin with comprehensive Python-specific behavior."""

    def __init__(self):
        super().__init__("python")

    @property
    def supported_languages(self) -> list[str]:
        """List of language identifiers this plugin supports."""
        return ["python", "py"]

    @property
    def supported_modes(self) -> list[str]:
        """List of execution modes this plugin supports."""
        return [Mode.CODER.value, Mode.ARCHITECT.value, Mode.PEER.value, Mode.SDET.value]

    @property
    def name(self) -> str:
        """Human-readable name for this plugin."""
        return "Python Language Assistant"

    @property
    def version(self) -> str:
        """Plugin version string."""
        return "1.0.0"

    def get_conventions(self) -> PythonConventions:
        """Get Python-specific conventions for this plugin."""
        if not self._conventions:
            self._conventions = PythonConventions(language=self.language)
        return self._conventions

    def create_executor(self, provider: LLMProvider, mode: str, **kwargs) -> Any:
        """Create a Python and mode-specific executor instance."""
        from vivek.llm.coder_executor import CoderExecutor
        from vivek.llm.architect_executor import ArchitectExecutor
        from vivek.llm.peer_executor import PeerExecutor
        from vivek.llm.sdet_executor import SDETExecutor

        mode_lower = mode.lower()

        class PythonLanguageExecutor:
            """Python-aware executor wrapper with language-specific prompts."""

            def __init__(self, base_executor, language_plugin):
                self.base_executor = base_executor
                self.language_plugin = language_plugin
                self.language = "python"
                self.mode = mode_lower

                # Set language-specific prompt
                if hasattr(base_executor, 'mode_prompt'):
                    base_executor.mode_prompt = f"Python {mode_lower.title()} Mode: {self._get_mode_specific_prompt(mode_lower)}"

            def _get_mode_specific_prompt(self, mode: str) -> str:
                """Get Python-specific prompt for the mode."""
                mode_instructions = self.language_plugin.get_language_specific_instructions(mode)
                return f"Follow Python best practices. {mode_instructions}"

            def __getattr__(self, name):
                """Delegate all other attributes to the base executor."""
                return getattr(self.base_executor, name)

        if mode_lower == Mode.CODER.value:
            base_executor = CoderExecutor(provider)
            return PythonLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.ARCHITECT.value:
            base_executor = ArchitectExecutor(provider)
            return PythonLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.PEER.value:
            base_executor = PeerExecutor(provider)
            return PythonLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.SDET.value:
            base_executor = SDETExecutor(provider)
            return PythonLanguageExecutor(base_executor, self)
        else:
            raise ValueError(f"Unsupported mode for Python plugin: {mode}")

    def get_language_specific_instructions(self, mode: str) -> str:
        """Get Python-specific instructions for the given mode."""
        base_instructions = f"""**Python Language Requirements for {mode.title()} Mode:**

Follow Python conventions:
- Use PEP 8 style guidelines with 4-space indentation
- Include type hints for all function parameters and return values
- Write comprehensive docstrings using Google/NumPy style
- Use pathlib for file operations instead of os.path
- Handle exceptions with specific exception types

"""

        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return base_instructions + """
**Coding Requirements:**
- Use explicit imports at the top of files (no wildcard imports)
- Implement proper error handling with try-except blocks
- Use list/dict comprehensions where appropriate
- Follow the single responsibility principle
- Write unit tests for all functions"""
        elif mode_lower == Mode.ARCHITECT.value:
            return base_instructions + """
**Architecture Requirements:**
- Design for scalability using proper abstractions
- Consider async/await patterns for I/O operations
- Plan for testability with dependency injection
- Document API interfaces and data contracts
- Consider deployment and packaging strategies"""
        elif mode_lower == Mode.PEER.value:
            return base_instructions + """
**Code Review Requirements:**
- Check for adherence to PEP 8 and type hints
- Verify proper error handling and edge cases
- Ensure comprehensive docstring coverage
- Review for security vulnerabilities (input validation, etc.)
- Check for appropriate testing coverage"""
        elif mode_lower == Mode.SDET.value:
            return base_instructions + """
**Testing Requirements:**
- Write comprehensive unit tests using pytest
- Include integration and end-to-end tests
- Test edge cases and error conditions
- Use fixtures for test data and setup
- Aim for >80% test coverage"""
        else:
            return base_instructions
