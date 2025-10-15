"""
Workflow domain service - manages workflows and their tasks.
"""

from typing import List, Optional
from ..models.workflow import Workflow, WorkflowStatus
from ..models.task import Task


class WorkflowService:
    """Simple service that manages workflows."""

    def __init__(self):
        """Initialize with empty workflow list."""
        self.workflows: List[Workflow] = []

    def create_workflow(self, id: str, description: str) -> Workflow:
        """Create a new workflow."""
        workflow = Workflow(id=id, description=description)
        self.workflows.append(workflow)
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get a workflow by ID."""
        return next((wf for wf in self.workflows if wf.id == workflow_id), None)

    def add_task_to_workflow(self, workflow_id: str, task: Task) -> bool:
        """Add a task to a workflow."""
        workflow = self.get_workflow(workflow_id)
        if workflow:
            workflow.add_task(task)
            return True
        return False

    def get_pending_tasks(self, workflow_id: str) -> List[Task]:
        """Get all pending tasks for a workflow."""
        workflow = self.get_workflow(workflow_id)
        if workflow:
            return workflow.get_pending_tasks()
        return []

    def mark_workflow_completed(self, workflow_id: str) -> bool:
        """Mark a workflow as completed if all tasks are done."""
        workflow = self.get_workflow(workflow_id)
        if workflow and workflow.is_completed():
            workflow.mark_completed()
            return True
        return False

    def get_all_workflows(self) -> List[Workflow]:
        """Get all workflows."""
        return self.workflows.copy()
