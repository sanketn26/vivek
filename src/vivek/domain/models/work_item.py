"""Work item data model."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ExecutionMode(str, Enum):
    """Execution mode for work item."""

    CODER = "coder"  # Generate implementation code
    SDET = "sdet"  # Generate tests


@dataclass
class WorkItem:
    """Unit of work to be executed.

    Attributes:
        id: Unique identifier (UUID)
        file_path: Relative path from project root
        description: What to implement
        mode: Execution mode (coder or sdet)
        language: Programming language
        file_status: "new" or "existing"
        dependencies: IDs of work items this depends on
        context: Additional context for execution
    """

    id: str
    file_path: str
    description: str
    mode: ExecutionMode
    language: str = "python"
    file_status: str = "new"  # "new" or "existing"
    dependencies: List[str] = field(default_factory=list)
    context: Optional[str] = None

    def __post_init__(self):
        """Validate work item."""
        if not self.id:
            raise ValueError("Work item ID cannot be empty")
        if not self.file_path:
            raise ValueError("File path cannot be empty")
        if not self.description:
            raise ValueError("Description cannot be empty")
        if self.file_status not in ("new", "existing"):
            raise ValueError(f"Invalid file_status: {self.file_status}")
