"""
Simple state repository interface - abstracts state persistence.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class StateRepository(ABC):
    """Simple interface for state persistence."""

    @abstractmethod
    def save_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        """Save state for a thread."""
        pass

    @abstractmethod
    def load_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Load state for a thread."""
        pass

    @abstractmethod
    def delete_state(self, thread_id: str) -> bool:
        """Delete state for a thread."""
        pass

    @abstractmethod
    def list_threads(self) -> list[str]:
        """List all thread IDs."""
        pass

    def get_name(self) -> str:
        """Get repository name."""
        return self.__class__.__name__
