"""
LLM infrastructure abstractions - simple and clear interfaces.
"""

from .llm_provider import LLMProvider
from .ollama_provider import OllamaProvider
from .mock_provider import MockLLMProvider

__all__ = ["LLMProvider", "OllamaProvider", "MockLLMProvider"]
