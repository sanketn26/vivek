"""File operations service."""

from pathlib import Path

from vivek.domain.exceptions.exception import ExecutionException
from vivek.domain.interfaces.file_service import IFileService


class FileService(IFileService):
    """Handle file operations using pathlib."""

    def read_file(self, file_path: str) -> str:
        """Read file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            return path.read_text()
        except Exception as e:
            raise ExecutionException(f"Failed to read file: {e}")

    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to file."""
        try:
            path = Path(file_path)
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return True
        except Exception as e:
            raise ExecutionException(f"Failed to write file: {e}")

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()

    def create_directory(self, dir_path: str) -> bool:
        """Create directory."""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            raise ExecutionException(f"Failed to create directory: {e}")
