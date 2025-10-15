"""
Workflow domain model - represents a complete workflow process.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from .task import Task


class WorkflowStatus(Enum):
    """Simple workflow states."""

    PLANNING = "planning"
    EXECUTING = "executing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Workflow:
    """A simple workflow that manages tasks."""

    id: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PLANNING
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def add_task(self, task: Task):
        """Add a task to the workflow."""
        self.tasks.append(task)

    def get_pending_tasks(self) -> List[Task]:
        """Get all pending tasks."""
        return [task for task in self.tasks if task.status == "pending"]

    def get_completed_tasks(self) -> List[Task]:
        """Get all completed tasks."""
        return [task for task in self.tasks if task.status == "completed"]

    def is_completed(self) -> bool:
        """Check if workflow is completed."""
        return all(task.status == "completed" for task in self.tasks)

    def mark_completed(self):
        """Mark workflow as completed."""
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.now()
