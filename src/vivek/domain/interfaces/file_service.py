"""File service interface."""

from abc import abstractmethod
from pathlib import Path
from typing import Protocol


class IFileService(Protocol):
    """Interface for file operations."""

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """Read file content."""
        ...

    @abstractmethod
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to file."""
        ...

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        ...
