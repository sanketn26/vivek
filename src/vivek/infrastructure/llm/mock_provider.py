"""
Mock LLM provider for testing and development.
"""

from .llm_provider import LLMProvider


class MockLLMProvider(LLMProvider):
    """Mock LLM provider that returns predictable responses."""

    def __init__(self, model_name: str = "mock-model"):
        """
        Initialize mock provider.

        Args:
            model_name: Name to use for the mock model
        """
        super().__init__(model_name)
        self._responses = []
        self._call_count = 0

    def set_responses(self, responses: list[str]) -> None:
        """
        Set predefined responses for testing.

        Args:
            responses: List of responses to return in order
        """
        self._responses = responses
        self._call_count = 0

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """
        Generate mock response.

        Args:
            prompt: Input prompt (used in response if no predefined responses)
            temperature: Ignored in mock

        Returns:
            Mock response
        """
        if self._responses and self._call_count < len(self._responses):
            response = self._responses[self._call_count]
            self._call_count += 1
            return response

        # Default mock response
        return f"Mock response to: {prompt[:100]}..."

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def reset(self) -> None:
        """Reset call count and responses."""
        self._call_count = 0
        self._responses = []
