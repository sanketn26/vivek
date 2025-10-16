"""
Task domain model - represents a single unit of work with full business logic.

This model combines the concepts of Task and WorkItem into a unified,
rich domain model following Domain-Driven Design principles.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task execution states."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskComplexity(Enum):
    """Estimated task complexity."""

    TRIVIAL = "trivial"  # < 10 lines of change
    SIMPLE = "simple"  # 10-50 lines
    MODERATE = "moderate"  # 50-200 lines
    COMPLEX = "complex"  # > 200 lines


@dataclass
class Task:
    """
    A task represents a single unit of work.

    Rich domain model with business logic for task management,
    dependency tracking, and complexity estimation.
    """

    # Core identity
    id: str
    description: str

    # Optional execution details
    file_path: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)

    # Status tracking
    status: TaskStatus = TaskStatus.PENDING
    created_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Results and changes
    result: Optional[str] = None
    code_changes: Optional[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        """Initialize computed fields."""
        if self.created_at is None:
            self.created_at = datetime.now()

    # ===== Business Logic: State Transitions =====

    def start(self) -> None:
        """
        Start working on this task.

        Business rule: Can only start pending tasks.
        """
        if self.status != TaskStatus.PENDING:
            raise ValueError(
                f"Cannot start task in {self.status.value} state. Must be pending."
            )
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete(self, result: Optional[str] = None, code_changes: Optional[str] = None) -> None:
        """
        Mark task as successfully completed.

        Business rule: Can only complete in-progress tasks.

        Args:
            result: Description of what was accomplished
            code_changes: Actual code changes made (if applicable)
        """
        if self.status != TaskStatus.IN_PROGRESS:
            raise ValueError(
                f"Cannot complete task in {self.status.value} state. Must be in progress."
            )
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self.code_changes = code_changes

    def fail(self, error_message: str) -> None:
        """
        Mark task as failed.

        Business rule: Can fail from any non-completed state.

        Args:
            error_message: Description of why the task failed
        """
        if self.status == TaskStatus.COMPLETED:
            raise ValueError("Cannot fail an already completed task")
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message

    def block(self, reason: Optional[str] = None) -> None:
        """
        Mark task as blocked.

        Business rule: Usually happens when dependencies aren't met.

        Args:
            reason: Optional reason why task is blocked
        """
        self.status = TaskStatus.BLOCKED
        if reason:
            self.error_message = f"Blocked: {reason}"

    def reset(self) -> None:
        """
        Reset task to pending state.

        Business rule: Allows retry of failed tasks.
        """
        self.status = TaskStatus.PENDING
        self.started_at = None
        self.completed_at = None
        self.error_message = None

    # ===== Business Logic: Dependencies =====

    def can_execute(self, completed_task_ids: List[str]) -> bool:
        """
        Check if this task can be executed now.

        Business rule: All dependencies must be completed.

        Args:
            completed_task_ids: List of task IDs that are completed

        Returns:
            True if task can be executed, False otherwise
        """
        if self.status != TaskStatus.PENDING:
            return False
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)

    def add_dependency(self, task_id: str) -> None:
        """
        Add a dependency to this task.

        Business rule: Cannot add dependencies to started tasks.

        Args:
            task_id: ID of the task this depends on
        """
        if self.status not in [TaskStatus.PENDING, TaskStatus.BLOCKED]:
            raise ValueError(
                f"Cannot add dependencies to task in {self.status.value} state"
            )
        if task_id not in self.dependencies:
            self.dependencies.append(task_id)

    def remove_dependency(self, task_id: str) -> None:
        """
        Remove a dependency from this task.

        Args:
            task_id: ID of the dependency to remove
        """
        if task_id in self.dependencies:
            self.dependencies.remove(task_id)

    # ===== Business Logic: Analysis =====

    def estimate_complexity(self) -> TaskComplexity:
        """
        Estimate task complexity based on description.

        Business rule: Heuristic-based complexity estimation.

        Returns:
            Estimated complexity level
        """
        desc_lower = self.description.lower()

        # Trivial indicators
        trivial_keywords = ["fix typo", "update comment", "rename", "format"]
        if any(keyword in desc_lower for keyword in trivial_keywords):
            return TaskComplexity.TRIVIAL

        # Complex indicators
        complex_keywords = [
            "refactor",
            "redesign",
            "architecture",
            "implement system",
            "integrate",
        ]
        if any(keyword in desc_lower for keyword in complex_keywords):
            return TaskComplexity.COMPLEX

        # Moderate indicators
        moderate_keywords = ["add feature", "implement", "create", "build"]
        if any(keyword in desc_lower for keyword in moderate_keywords):
            return TaskComplexity.MODERATE

        # Default to simple
        return TaskComplexity.SIMPLE

    def duration(self) -> Optional[float]:
        """
        Calculate task duration in seconds.

        Returns:
            Duration in seconds if task is completed, None otherwise
        """
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def is_completed(self) -> bool:
        """Check if task is successfully completed."""
        return self.status == TaskStatus.COMPLETED

    def is_failed(self) -> bool:
        """Check if task failed."""
        return self.status == TaskStatus.FAILED

    def is_in_progress(self) -> bool:
        """Check if task is currently being worked on."""
        return self.status == TaskStatus.IN_PROGRESS

    def is_pending(self) -> bool:
        """Check if task is waiting to be started."""
        return self.status == TaskStatus.PENDING

    def is_blocked(self) -> bool:
        """Check if task is blocked."""
        return self.status == TaskStatus.BLOCKED

    # ===== Business Logic: Validation =====

    def validate(self) -> List[str]:
        """
        Validate task for completeness.

        Business rule: Tasks must have proper setup.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.id or not self.id.strip():
            errors.append("Task ID cannot be empty")

        if not self.description or not self.description.strip():
            errors.append("Task description cannot be empty")

        if len(self.description) < 5:
            errors.append("Task description is too short (minimum 5 characters)")

        if self.status == TaskStatus.COMPLETED and not self.completed_at:
            errors.append("Completed task must have completion timestamp")

        if self.status == TaskStatus.FAILED and not self.error_message:
            errors.append("Failed task must have error message")

        # Check for circular dependencies (self-reference)
        if self.id in self.dependencies:
            errors.append(f"Task cannot depend on itself: {self.id}")

        return errors

    def __repr__(self) -> str:
        """String representation for debugging."""
        return (
            f"Task(id={self.id!r}, status={self.status.value}, "
            f"description={self.description[:50]!r}...)"
        )
