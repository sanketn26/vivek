"""Execution result data model."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionResult:
    """Result of executing a work item.

    Attributes:
        work_item_id: ID of work item executed
        success: Whether execution succeeded
        code: Generated code (if successful)
        file_path: Where code was written
        errors: List of error messages
        warnings: List of warning messages
        metadata: Additional metadata (tokens used, time taken, etc.)
    """

    work_item_id: str
    success: bool
    code: Optional[str] = None
    file_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
