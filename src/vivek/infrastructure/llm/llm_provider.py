"""
Simple LLM provider interface - abstracts external LLM services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class LLMProvider(ABC):
    """Simple interface for LLM services."""

    def __init__(self, model_name: str):
        """Initialize with model name."""
        self.model_name = model_name

    @abstractmethod
    def generate(self, system_prompt: str, prompt: str, temperature: float = 0.7) -> str:
        """Generate text from prompt."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available."""
        pass

    def get_name(self) -> str:
        """Get provider name."""
        return self.__class__.__name__

    def get_model_name(self) -> str:
        """Get model name."""
        return self.model_name
