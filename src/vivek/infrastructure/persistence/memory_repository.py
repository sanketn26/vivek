"""
In-memory state repository implementation.
Simple storage for development and testing.
"""

from typing import Dict, Any, Optional
from .state_repository import StateRepository


class MemoryStateRepository(StateRepository):
    """Simple in-memory state storage."""

    def __init__(self):
        """Initialize with empty storage."""
        self._storage: Dict[str, Dict[str, Any]] = {}

    def save_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        """
        Save state to memory.

        Args:
            thread_id: Unique thread identifier
            state: State data to save
        """
        if not thread_id or not thread_id.strip():
            raise ValueError("thread_id cannot be empty")
        self._storage[thread_id] = state.copy()

    def load_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Load state from memory.

        Args:
            thread_id: Thread identifier

        Returns:
            State data if found, None otherwise
        """
        return self._storage.get(thread_id)

    def delete_state(self, thread_id: str) -> bool:
        """
        Delete state from memory.

        Args:
            thread_id: Thread identifier

        Returns:
            True if deleted, False if not found
        """
        if thread_id in self._storage:
            del self._storage[thread_id]
            return True
        return False

    def list_threads(self) -> list[str]:
        """
        List all thread IDs.

        Returns:
            List of thread identifiers
        """
        return list(self._storage.keys())

    def clear(self) -> None:
        """Clear all stored state."""
        self._storage.clear()
