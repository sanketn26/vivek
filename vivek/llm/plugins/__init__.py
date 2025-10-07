"""Plugin system for language-specific executor support."""

from .base.language_plugin import LanguagePlugin, LanguageConventions
from .base.registry import ExecutorRegistry, get_registry, register_plugin, discover_plugins, create_executor

__all__ = [
    "LanguagePlugin",
    "LanguageConventions",
    "ExecutorRegistry",
    "get_registry",
    "register_plugin",
    "discover_plugins",
    "create_executor"
]