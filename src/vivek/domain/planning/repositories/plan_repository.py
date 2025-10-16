"""
Repository for plan persistence.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from vivek.domain.planning.models.task_plan import TaskPlan


class PlanRepository(ABC):
    """Abstract repository for plan storage."""

    @abstractmethod
    def save(self, plan: TaskPlan) -> None:
        """Save or update a plan."""
        pass

    @abstractmethod
    def get_by_id(self, plan_id: str) -> Optional[TaskPlan]:
        """Get plan by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[TaskPlan]:
        """Get all plans."""
        pass

    @abstractmethod
    def delete(self, plan_id: str) -> bool:
        """Delete a plan."""
        pass


class InMemoryPlanRepository(PlanRepository):
    """Simple in-memory plan storage."""

    def __init__(self):
        """Initialize with empty storage."""
        self._plans: dict[str, TaskPlan] = {}

    def save(self, plan: TaskPlan) -> None:
        """Save or update a plan."""
        self._plans[plan.id] = plan

    def get_by_id(self, plan_id: str) -> Optional[TaskPlan]:
        """Get plan by ID."""
        return self._plans.get(plan_id)

    def get_all(self) -> List[TaskPlan]:
        """Get all plans."""
        return list(self._plans.values())

    def delete(self, plan_id: str) -> bool:
        """Delete a plan."""
        if plan_id in self._plans:
            del self._plans[plan_id]
            return True
        return False
