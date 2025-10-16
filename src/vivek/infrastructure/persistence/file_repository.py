"""
File-based state repository implementation.
Persists state to disk as JSON files.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from .state_repository import StateRepository


class FileStateRepository(StateRepository):
    """File-based state storage using JSON."""

    def __init__(self, storage_dir: str = ".vivek/state"):
        """
        Initialize file-based repository.

        Args:
            storage_dir: Directory to store state files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, thread_id: str) -> Path:
        """Get file path for a thread."""
        # Sanitize thread_id for filesystem
        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in thread_id)
        return self.storage_dir / f"{safe_id}.json"

    def save_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        """
        Save state to a JSON file.

        Args:
            thread_id: Unique thread identifier
            state: State data to save

        Raises:
            ValueError: If thread_id is empty
            IOError: If file write fails
        """
        if not thread_id or not thread_id.strip():
            raise ValueError("thread_id cannot be empty")

        file_path = self._get_file_path(thread_id)
        try:
            with open(file_path, "w") as f:
                json.dump(state, f, indent=2, default=str)
        except Exception as e:
            raise IOError(f"Failed to save state for {thread_id}: {str(e)}") from e

    def load_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Load state from a JSON file.

        Args:
            thread_id: Thread identifier

        Returns:
            State data if found, None otherwise
        """
        file_path = self._get_file_path(thread_id)
        if not file_path.exists():
            return None

        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except Exception:
            # If file is corrupted, return None
            return None

    def delete_state(self, thread_id: str) -> bool:
        """
        Delete state file.

        Args:
            thread_id: Thread identifier

        Returns:
            True if deleted, False if not found
        """
        file_path = self._get_file_path(thread_id)
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def list_threads(self) -> list[str]:
        """
        List all thread IDs.

        Returns:
            List of thread identifiers
        """
        thread_ids = []
        for file_path in self.storage_dir.glob("*.json"):
            # Remove .json extension to get thread_id
            thread_ids.append(file_path.stem)
        return sorted(thread_ids)

    def clear(self) -> None:
        """Delete all state files."""
        for file_path in self.storage_dir.glob("*.json"):
            file_path.unlink()
