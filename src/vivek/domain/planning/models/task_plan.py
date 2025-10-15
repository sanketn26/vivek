"""
TaskPlan domain model - represents a plan for completing tasks.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

# Import with path setup for execution context
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from domain.workflow.models.work_item import WorkItem


@dataclass
class TaskPlan:
    """A simple plan for completing tasks."""

    id: str
    description: str
    work_items: List[WorkItem] = field(default_factory=list)
    created_at: Optional[datetime] = None
    status: str = "draft"  # draft, approved, executing, completed

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def add_work_item(self, work_item: WorkItem):
        """Add a work item to the plan."""
        self.work_items.append(work_item)

    def get_executable_items(self, completed_items: List[str]) -> List[WorkItem]:
        """Get work items that can be executed now."""
        return [item for item in self.work_items if item.can_execute(completed_items)]

    def is_completed(self) -> bool:
        """Check if all work items are completed."""
        return all(item.status == "completed" for item in self.work_items)

    def get_pending_count(self) -> int:
        """Get count of pending work items."""
        return len([item for item in self.work_items if item.status == "pending"])
