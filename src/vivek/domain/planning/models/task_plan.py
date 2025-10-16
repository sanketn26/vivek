"""
TaskPlan domain model - represents a plan for completing tasks.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum

from vivek.domain.workflow.models.task import Task, TaskStatus


class PlanStatus(Enum):
    """Plan execution states."""

    DRAFT = "draft"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class TaskPlan:
    """A plan for executing multiple tasks in order."""

    id: str
    description: str
    tasks: List[Task] = field(default_factory=list)
    created_at: Optional[datetime] = None
    status: PlanStatus = PlanStatus.DRAFT

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def add_task(self, task: Task) -> None:
        """Add a task to the plan."""
        self.tasks.append(task)

    def get_executable_tasks(self, completed_task_ids: List[str]) -> List[Task]:
        """
        Get tasks that can be executed now.

        Args:
            completed_task_ids: List of task IDs that are completed

        Returns:
            List of tasks ready to execute
        """
        return [task for task in self.tasks if task.can_execute(completed_task_ids)]

    def is_completed(self) -> bool:
        """Check if all tasks in the plan are completed."""
        if not self.tasks:
            return False
        return all(task.status == TaskStatus.COMPLETED for task in self.tasks)

    def get_pending_count(self) -> int:
        """Get count of pending tasks."""
        return len([task for task in self.tasks if task.status == TaskStatus.PENDING])

    def get_completed_count(self) -> int:
        """Get count of completed tasks."""
        return len(
            [task for task in self.tasks if task.status == TaskStatus.COMPLETED]
        )

    def get_failed_count(self) -> int:
        """Get count of failed tasks."""
        return len([task for task in self.tasks if task.status == TaskStatus.FAILED])

    def approve(self) -> None:
        """Approve the plan for execution."""
        if self.status != PlanStatus.DRAFT:
            raise ValueError(f"Cannot approve plan in {self.status.value} state")
        self.status = PlanStatus.APPROVED

    def start_execution(self) -> None:
        """Start executing the plan."""
        if self.status != PlanStatus.APPROVED:
            raise ValueError(
                f"Cannot start execution of plan in {self.status.value} state"
            )
        self.status = PlanStatus.EXECUTING

    def mark_completed(self) -> None:
        """Mark the plan as completed."""
        if not self.is_completed():
            raise ValueError("Cannot mark plan as completed when tasks are pending")
        self.status = PlanStatus.COMPLETED

    def mark_failed(self) -> None:
        """Mark the plan as failed."""
        self.status = PlanStatus.FAILED
