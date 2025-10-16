"""
Planning domain service - creates and manages task plans.
"""

from typing import List, Optional
from vivek.domain.planning.models.task_plan import TaskPlan
from vivek.domain.planning.repositories.plan_repository import PlanRepository
from vivek.domain.workflow.models.task import Task


class PlanningService:
    """Service for creating and managing task plans."""

    def __init__(self, repository: PlanRepository):
        """
        Initialize with repository.

        Args:
            repository: Plan repository for persistence
        """
        self.repository = repository

    def create_plan(self, id: str, description: str) -> TaskPlan:
        """
        Create a new task plan.

        Args:
            id: Unique plan identifier
            description: Plan description

        Returns:
            Created plan

        Raises:
            ValueError: If plan with ID already exists
        """
        if not id or not id.strip():
            raise ValueError("Plan ID cannot be empty")
        if not description or not description.strip():
            raise ValueError("Plan description cannot be empty")

        # Check if plan already exists
        existing = self.repository.get_by_id(id)
        if existing:
            raise ValueError(f"Plan with ID '{id}' already exists")

        plan = TaskPlan(id=id, description=description)
        self.repository.save(plan)
        return plan

    def get_plan(self, plan_id: str) -> Optional[TaskPlan]:
        """
        Get a plan by ID.

        Args:
            plan_id: Plan identifier

        Returns:
            Plan if found, None otherwise
        """
        return self.repository.get_by_id(plan_id)

    def add_task_to_plan(self, plan_id: str, task: Task) -> bool:
        """
        Add a task to a plan.

        Args:
            plan_id: Plan identifier
            task: Task to add

        Returns:
            True if successful, False if plan not found
        """
        plan = self.repository.get_by_id(plan_id)
        if plan:
            plan.add_task(task)
            self.repository.save(plan)  # Persist changes
            return True
        return False

    def get_executable_tasks(
        self, plan_id: str, completed_task_ids: List[str]
    ) -> List[Task]:
        """
        Get tasks that can be executed now.

        Args:
            plan_id: Plan identifier
            completed_task_ids: List of completed task IDs

        Returns:
            List of executable tasks
        """
        plan = self.repository.get_by_id(plan_id)
        if plan:
            return plan.get_executable_tasks(completed_task_ids)
        return []

    def mark_plan_completed(self, plan_id: str) -> bool:
        """
        Mark a plan as completed if all tasks are done.

        Args:
            plan_id: Plan identifier

        Returns:
            True if marked completed, False otherwise
        """
        plan = self.repository.get_by_id(plan_id)
        if plan and plan.is_completed():
            plan.mark_completed()
            self.repository.save(plan)  # Persist changes
            return True
        return False

    def get_pending_task_count(self, plan_id: str) -> int:
        """
        Get count of pending tasks in a plan.

        Args:
            plan_id: Plan identifier

        Returns:
            Count of pending tasks
        """
        plan = self.repository.get_by_id(plan_id)
        if plan:
            return plan.get_pending_count()
        return 0

    def get_all_plans(self) -> List[TaskPlan]:
        """
        Get all plans.

        Returns:
            List of all plans
        """
        return self.repository.get_all()

    def delete_plan(self, plan_id: str) -> bool:
        """
        Delete a plan.

        Args:
            plan_id: Plan identifier

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(plan_id)
