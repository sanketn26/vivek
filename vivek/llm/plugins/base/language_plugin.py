"""Plugin interface for language-specific executor implementations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, Type
from vivek.llm.models import LLMProvider


@dataclass
class LanguageConventions:
    """Data class containing essential language-specific information.

    Simplified to only include fields that are actually used by the plugin system.
    All language-specific conventions are now embedded directly in the
    get_language_specific_instructions() method of each plugin.
    """

    # Language identifier
    language: str

    # File extensions associated with this language
    extensions: list[str] = field(default_factory=list)


class LanguagePlugin(ABC):
    """Abstract base class for language-specific executor plugins.

    Language plugins provide language-specific behavior for executors,
    including conventions, best practices, and code generation patterns.
    """

    def __init__(self, language: str):
        """Initialize the language plugin.

        Args:
            language: The programming language this plugin supports
        """
        self.language = language.lower()
        self._conventions = None

    @property
    @abstractmethod
    def supported_languages(self) -> list[str]:
        """List of language identifiers this plugin supports.

        Returns:
            List of supported language strings (e.g., ['python', 'py'])
        """
        pass

    @property
    @abstractmethod
    def supported_modes(self) -> list[str]:
        """List of execution modes this plugin supports.

        Returns:
            List of supported mode strings (e.g., ['coder', 'architect'])
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name for this plugin.

        Returns:
            Plugin name (e.g., 'Python Coder')
        """
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version string.

        Returns:
            Version string (e.g., '1.0.0')
        """
        pass

    @abstractmethod
    def get_conventions(self) -> LanguageConventions:
        """Get language-specific conventions for this plugin.

        Returns:
            LanguageConventions instance with all language-specific settings
        """
        pass

    @abstractmethod
    def create_executor(self, provider: LLMProvider, mode: str, **kwargs) -> Any:
        """Create a language and mode-specific executor instance.

        Args:
            provider: LLM provider to use for the executor
            mode: Execution mode (e.g., 'coder', 'architect')
            **kwargs: Additional arguments for executor creation

        Returns:
            Executor instance configured for the specified language and mode
        """
        pass

    @abstractmethod
    def get_language_specific_instructions(self, mode: str) -> str:
        """Get language-specific instructions for the given mode.

        Args:
            mode: Execution mode requiring instructions

        Returns:
            String containing language-specific guidance and requirements
        """
        pass

    def validate_language_mode_combination(self, language: str, mode: str) -> bool:
        """Validate if the given language and mode combination is supported.

        Args:
            language: Language to validate
            mode: Mode to validate

        Returns:
            True if the combination is supported, False otherwise
        """
        return (
            language.lower() in self.supported_languages and
            mode.lower() in self.supported_modes
        )

    def get_plugin_info(self) -> Dict[str, Any]:
        """Get comprehensive information about this plugin.

        Returns:
            Dictionary containing plugin metadata and capabilities
        """
        return {
            "name": self.name,
            "version": self.version,
            "language": self.language,
            "supported_languages": self.supported_languages,
            "supported_modes": self.supported_modes,
            "conventions": self.get_conventions().__dict__ if self._conventions else None
        }

    def is_compatible(self, language: str, mode: str) -> bool:
        """Check if this plugin is compatible with the given language and mode.

        Args:
            language: Language to check compatibility for
            mode: Mode to check compatibility for

        Returns:
            True if compatible, False otherwise
        """
        return self.validate_language_mode_combination(language, mode)