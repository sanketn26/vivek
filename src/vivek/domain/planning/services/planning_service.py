"""
Planning domain service - creates and manages task plans.
"""

from typing import List, Optional
from ..models.task_plan import TaskPlan

# Import with path setup for execution context
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from domain.workflow.models.work_item import WorkItem


class PlanningService:
    """Simple service that creates task plans."""

    def __init__(self):
        """Initialize with empty plan list."""
        self.plans: List[TaskPlan] = []

    def create_plan(self, id: str, description: str) -> TaskPlan:
        """Create a new task plan."""
        plan = TaskPlan(id=id, description=description)
        self.plans.append(plan)
        return plan

    def get_plan(self, plan_id: str) -> Optional[TaskPlan]:
        """Get a plan by ID."""
        return next((plan for plan in self.plans if plan.id == plan_id), None)

    def add_work_item_to_plan(self, plan_id: str, work_item: WorkItem) -> bool:
        """Add a work item to a plan."""
        plan = self.get_plan(plan_id)
        if plan:
            plan.add_work_item(work_item)
            return True
        return False

    def get_executable_work_items(
        self, plan_id: str, completed_items: List[str]
    ) -> List[WorkItem]:
        """Get work items that can be executed now."""
        plan = self.get_plan(plan_id)
        if plan:
            return plan.get_executable_items(completed_items)
        return []

    def mark_plan_completed(self, plan_id: str) -> bool:
        """Mark a plan as completed if all work items are done."""
        plan = self.get_plan(plan_id)
        if plan and plan.is_completed():
            plan.status = "completed"
            return True
        return False

    def get_pending_work_count(self, plan_id: str) -> int:
        """Get count of pending work items in a plan."""
        plan = self.get_plan(plan_id)
        if plan:
            return plan.get_pending_count()
        return 0

    def get_all_plans(self) -> List[TaskPlan]:
        """Get all plans."""
        return self.plans.copy()
