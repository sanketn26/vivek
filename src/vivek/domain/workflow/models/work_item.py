"""
WorkItem domain model - represents a specific piece of work to be done.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional


@dataclass
class WorkItem:
    """A specific piece of work that needs to be done."""

    id: str
    file_path: str
    description: str
    dependencies: Optional[List[str]] = None  # IDs of other work items this depends on
    status: str = "pending"  # pending, in_progress, completed, failed
    code_changes: Optional[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

    def can_execute(self, completed_items: List[str]) -> bool:
        """Check if this work item can be executed."""
        if self.dependencies is None:
            return True
        return all(dep in completed_items for dep in self.dependencies)

    def mark_completed(self, code_changes: Optional[str] = None):
        """Mark work item as completed."""
        self.status = "completed"
        if code_changes:
            self.code_changes = code_changes
