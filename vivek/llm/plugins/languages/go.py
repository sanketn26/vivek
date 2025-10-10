"""Go Language Plugin implementation."""

from typing import Dict, Any, Optional, Type
from dataclasses import dataclass, field

from vivek.llm.plugins.base.language_plugin import LanguagePlugin, LanguageConventions
from vivek.llm.models import LLMProvider
from vivek.llm.constants import Mode


@dataclass
class GoConventions(LanguageConventions):
    """Go-specific conventions (simplified)."""

    def __post_init__(self):
        if not self.language:
            self.language = "go"
        if not self.extensions:
            self.extensions = [".go"]


class GoLanguagePlugin(LanguagePlugin):
    """Go language plugin with comprehensive Go-specific behavior."""

    def __init__(self):
        super().__init__("go")

    @property
    def supported_languages(self) -> list[str]:
        """List of language identifiers this plugin supports."""
        return ["go", "golang"]

    @property
    def supported_modes(self) -> list[str]:
        """List of execution modes this plugin supports."""
        return [
            Mode.CODER.value,
            Mode.ARCHITECT.value,
            Mode.PEER.value,
            Mode.SDET.value,
        ]

    @property
    def name(self) -> str:
        """Human-readable name for this plugin."""
        return "Go Language Assistant"

    @property
    def version(self) -> str:
        """Plugin version string."""
        return "1.0.0"

    def get_conventions(self) -> GoConventions:
        """Get Go-specific conventions for this plugin."""
        if not self._conventions:
            self._conventions = GoConventions(language=self.language)
        return self._conventions

    def create_executor(self, provider: LLMProvider, mode: str, **kwargs) -> Any:
        """Create a Go and mode-specific executor instance."""
        from vivek.llm.coder_executor import CoderExecutor
        from vivek.llm.architect_executor import ArchitectExecutor
        from vivek.llm.peer_executor import PeerExecutor
        from vivek.llm.sdet_executor import SDETExecutor

        mode_lower = mode.lower()

        class GoLanguageExecutor:
            """Go-aware executor wrapper with language-specific prompts."""

            def __init__(self, base_executor, language_plugin):
                self.base_executor = base_executor
                self.language_plugin = language_plugin
                self.language = "go"
                self.mode = mode_lower

                # Set language-specific prompt
                if hasattr(base_executor, "mode_prompt"):
                    base_executor.mode_prompt = f"Go {mode_lower.title()} Mode: {self._get_mode_specific_prompt(mode_lower)}"

            def _get_mode_specific_prompt(self, mode: str) -> str:
                """Get Go-specific prompt for the mode."""
                mode_instructions = (
                    self.language_plugin.get_language_specific_instructions(mode)
                )
                return f"Follow Go best practices. {mode_instructions}"

            def __getattr__(self, name):
                """Delegate all other attributes to the base executor."""
                return getattr(self.base_executor, name)

        if mode_lower == Mode.CODER.value:
            base_executor = CoderExecutor(provider)
            return GoLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.ARCHITECT.value:
            base_executor = ArchitectExecutor(provider)
            return GoLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.PEER.value:
            base_executor = PeerExecutor(provider)
            return GoLanguageExecutor(base_executor, self)
        elif mode_lower == Mode.SDET.value:
            base_executor = SDETExecutor(provider)
            return GoLanguageExecutor(base_executor, self)
        else:
            raise ValueError(f"Unsupported mode for Go plugin: {mode}")

    def get_language_specific_instructions(self, mode: str) -> str:
        """Get Go-specific instructions for the given mode."""
        base_instructions = f"""**Go Language Requirements for {mode.title()} Mode:**

Follow Go conventions:
- Use gofmt for consistent formatting and go vet for common mistakes
- Handle errors explicitly, never ignore them
- Use interfaces for abstraction and testability
- Follow Go naming conventions (CamelCase for exported identifiers)
- Write clear, idiomatic Go code

"""

        mode_lower = mode.lower()

        if mode_lower == Mode.CODER.value:
            return (
                base_instructions
                + """
**Coding Requirements:**
- Use explicit error handling with error returns
- Implement interfaces for better testability
- Use struct composition and embedding appropriately
- Write comprehensive tests for all public functions
- Follow the standard Go project layout"""
            )
        elif mode_lower == Mode.ARCHITECT.value:
            return (
                base_instructions
                + """
**Architecture Requirements:**
- Design concurrent programs using goroutines and channels
- Plan for scalability with proper package organization
- Consider context.Context for cancellation and timeouts
- Document public APIs and design patterns
- Consider deployment and containerization strategies"""
            )
        elif mode_lower == Mode.PEER.value:
            return (
                base_instructions
                + """
**Code Review Requirements:**
- Check for proper error handling and no ignored errors
- Verify idiomatic Go code patterns and conventions
- Ensure comprehensive test coverage
- Review for security vulnerabilities and race conditions
- Check for appropriate use of interfaces and abstractions"""
            )
        elif mode_lower == Mode.SDET.value:
            return (
                base_instructions
                + """
**Testing Requirements:**
- Write comprehensive unit tests using the testing package
- Include benchmark tests for performance-critical code
- Test error conditions and edge cases thoroughly
- Use table-driven tests for multiple scenarios
- Aim for >80% test coverage"""
            )
        else:
            return base_instructions
