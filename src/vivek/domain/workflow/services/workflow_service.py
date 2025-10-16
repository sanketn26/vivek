"""
Workflow domain service - manages workflows and their tasks.
"""

from typing import List, Optional
from vivek.domain.workflow.models.workflow import Workflow, WorkflowStatus
from vivek.domain.workflow.models.task import Task
from vivek.domain.workflow.repositories.workflow_repository import WorkflowRepository


class WorkflowService:
    """Service for managing workflows."""

    def __init__(self, repository: WorkflowRepository):
        """
        Initialize with repository.

        Args:
            repository: Workflow repository for persistence
        """
        self.repository = repository

    def create_workflow(self, id: str, description: str) -> Workflow:
        """
        Create a new workflow.

        Args:
            id: Unique workflow identifier
            description: Workflow description

        Returns:
            Created workflow

        Raises:
            ValueError: If workflow with ID already exists
        """
        if not id or not id.strip():
            raise ValueError("Workflow ID cannot be empty")
        if not description or not description.strip():
            raise ValueError("Workflow description cannot be empty")

        # Check if workflow already exists
        existing = self.repository.get_by_id(id)
        if existing:
            raise ValueError(f"Workflow with ID '{id}' already exists")

        workflow = Workflow(id=id, description=description)
        self.repository.save(workflow)
        return workflow

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """
        Get a workflow by ID.

        Args:
            workflow_id: Workflow identifier

        Returns:
            Workflow if found, None otherwise
        """
        return self.repository.get_by_id(workflow_id)

    def add_task_to_workflow(self, workflow_id: str, task: Task) -> bool:
        """
        Add a task to a workflow.

        Args:
            workflow_id: Workflow identifier
            task: Task to add

        Returns:
            True if successful, False if workflow not found
        """
        workflow = self.repository.get_by_id(workflow_id)
        if workflow:
            workflow.add_task(task)
            self.repository.save(workflow)  # Persist changes
            return True
        return False

    def get_pending_tasks(self, workflow_id: str) -> List[Task]:
        """
        Get all pending tasks for a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            List of pending tasks (empty if workflow not found)
        """
        workflow = self.repository.get_by_id(workflow_id)
        if workflow:
            return workflow.get_pending_tasks()
        return []

    def mark_workflow_completed(self, workflow_id: str) -> bool:
        """
        Mark a workflow as completed if all tasks are done.

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if marked completed, False otherwise
        """
        workflow = self.repository.get_by_id(workflow_id)
        if workflow and workflow.is_completed():
            workflow.mark_completed()
            self.repository.save(workflow)  # Persist changes
            return True
        return False

    def get_all_workflows(self) -> List[Workflow]:
        """
        Get all workflows.

        Returns:
            List of all workflows
        """
        return self.repository.get_all()

    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow.

        Args:
            workflow_id: Workflow identifier

        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(workflow_id)
