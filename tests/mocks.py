"""
Centralized mock classes for testing.

DRY principle: Define mocks once, use everywhere.
"""

from typing import Optional, List, Dict, Any
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.infrastructure.persistence.state_repository import StateRepository


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self, model_name: str = "mock-model"):
        super().__init__(model_name)
        self._responses = []
        self._call_count = 0

    def set_responses(self, responses: List[str]) -> None:
        """Set predefined responses for testing."""
        self._responses = responses
        self._call_count = 0

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate mock response."""
        if self._responses and self._call_count < len(self._responses):
            response = self._responses[self._call_count]
            self._call_count += 1
            return response
        return f"Mock response to: {prompt[:50]}..."

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def reset(self) -> None:
        """Reset call count and responses."""
        self._call_count = 0
        self._responses = []


class MockStateRepository(StateRepository):
    """Mock state repository for testing."""

    def __init__(self):
        self.storage = {}

    def save_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        self.storage[thread_id] = state.copy()

    def load_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        return self.storage.get(thread_id)

    def delete_state(self, thread_id: str) -> bool:
        if thread_id in self.storage:
            del self.storage[thread_id]
            return True
        return False

    def list_threads(self) -> List[str]:
        return list(self.storage.keys())

    def clear(self) -> None:
        """Clear all stored state."""
        self.storage.clear()
