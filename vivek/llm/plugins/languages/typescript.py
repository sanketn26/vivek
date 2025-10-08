"""TypeScript Language Plugin implementation."""

from typing import Dict, Any, Optional, Type
from dataclasses import dataclass, field

from vivek.llm.plugins.base.language_plugin import LanguagePlugin, LanguageConventions
from vivek.llm.models import LLMProvider
from vivek.llm.constants import Mode


@dataclass
class TypeScriptConventions(LanguageConventions):
    """TypeScript-specific conventions (simplified)."""

    def __post_init__(self):
        if not self.language:
            self.language = "typescript"
        if not self.extensions:
            self.extensions = [".ts", ".tsx", ".js", ".jsx"]


class TypeScriptLanguagePlugin(LanguagePlugin):
    """TypeScript language plugin with comprehensive TypeScript-specific behavior."""

    def __init__(self):
        super().__init__("typescript")

    @property
    def supported_languages(self) -> list[str]:
        """List of language identifiers this plugin supports."""
        return ["typescript", "ts", "tsx", "javascript", "js", "jsx"]

    @property
    def supported_modes(self) -> list[str]:
        """List of execution modes this plugin supports."""
        return [Mode.CODER.value, Mode.ARCHITECT.value, Mode.PEER.value, Mode.SDET.value]

    @property
    def name(self) -> str:
        """Human-readable name for this plugin."""
        return "TypeScript Language Assistant"

    @property
    def version(self) -> str:
        """Plugin version string."""
        return "1.0.0"

    def get_conventions(self) -> TypeScriptConventions:
        """Get TypeScript-specific conventions for this plugin."""
        if not self._conventions:
            self._conventions = TypeScriptConventions(language=self.language)
        return self._conventions

    def create_executor(self, provider: LLMProvider, mode: str, **kwargs) -> Any:
        """Create a TypeScript and mode-specific executor instance."""
        from vivek.llm.coder_executor import CoderExecutor
        from vivek.llm.architect_executor import ArchitectExecutor
        from vivek.llm.peer_executor import PeerExecutor
        from vivek.llm.sdet_executor import SDETExecutor

        mode_lower = mode.lower()

        class TypeScriptLanguageExecutor:
            """TypeScript-aware executor wrapper with language-specific prompts."""

            def __init__(self, base_executor, language_plugin):
                self.base_executor = base_executor
                self.language_plugin = language_plugin
                self.language = "typescript"
                self.mode = mode_lower

                # Set language-specific prompt
                if hasattr(base_executor, 'mode_prompt'):
                    base_executor.mode_prompt = f"TypeScript {mode_lower.title()} Mode: {self._get_mode_specific_prompt(mode_lower)}"

            def _get_mode_specific_prompt(self, mode: str) -> str:
                """Get TypeScript-specific prompt for the mode."""
                mode_instructions = self.language_plugin.get_language_specific_instructions(mode)
                return f"Follow TypeScript best practices. {mode_instructions}"

            def __getattr__(self, name):
                """Delegate all other attributes to the base executor."""
                return getattr(self.base_executor, name)

        if mode_lower == Mode.CODER.value:
            base_executor = CoderExecutor(provider)
            return TypeScriptLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.ARCHITECT.value:
            base_executor = ArchitectExecutor(provider)
            return TypeScriptLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.PEER.value:
            base_executor = PeerExecutor(provider)
            return TypeScriptLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.SDET.value:
            base_executor = SDETExecutor(provider)
            return TypeScriptLanguageExecutor(base_executor, self)
        else:
            raise ValueError(f"Unsupported mode for TypeScript plugin: {mode}")

    def get_language_specific_instructions(self, mode: str) -> str:
        """Get TypeScript-specific instructions for the given mode."""
        base_instructions = f"""**TypeScript Language Requirements for {mode.title()} Mode:**

Follow TypeScript conventions:
- Use strict type checking with no implicit any types
- Define interfaces for object shapes and API responses
- Include JSDoc comments for public APIs
- Handle async/await patterns correctly
- Use ES6+ features (const/let, arrow functions, destructuring)

"""

        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return base_instructions + """
**Coding Requirements:**
- Use explicit type annotations for function parameters and return values
- Implement proper error handling with typed errors
- Use generic types for reusable components and utilities
- Follow the single responsibility principle
- Write unit tests for all functions"""
        elif mode_lower == Mode.ARCHITECT.value:
            return base_instructions + """
**Architecture Requirements:**
- Design type-safe APIs and data contracts
- Consider module boundaries and dependency injection
- Plan for scalability with proper abstractions
- Document API interfaces and integration patterns
- Consider deployment and build strategies"""
        elif mode_lower == Mode.PEER.value:
            return base_instructions + """
**Code Review Requirements:**
- Check for type safety and proper TypeScript usage
- Verify proper error handling and edge cases
- Ensure comprehensive JSDoc coverage
- Review for security vulnerabilities (input validation, XSS prevention)
- Check for appropriate testing coverage"""
        elif mode_lower == Mode.SDET.value:
            return base_instructions + """
**Testing Requirements:**
- Write comprehensive unit tests using Jest or similar framework
- Include integration and end-to-end tests
- Test edge cases and error conditions with proper mocking
- Use type-safe test utilities and fixtures
- Aim for >80% test coverage"""
        else:
            return base_instructions

