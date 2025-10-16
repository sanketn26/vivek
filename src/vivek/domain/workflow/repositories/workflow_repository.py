"""
Repository for workflow persistence.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
from vivek.domain.workflow.models.workflow import Workflow


class WorkflowRepository(ABC):
    """Abstract repository for workflow storage."""

    @abstractmethod
    def save(self, workflow: Workflow) -> None:
        """Save or update a workflow."""
        pass

    @abstractmethod
    def get_by_id(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[Workflow]:
        """Get all workflows."""
        pass

    @abstractmethod
    def delete(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        pass


class InMemoryWorkflowRepository(WorkflowRepository):
    """Simple in-memory workflow storage."""

    def __init__(self):
        """Initialize with empty storage."""
        self._workflows: dict[str, Workflow] = {}

    def save(self, workflow: Workflow) -> None:
        """Save or update a workflow."""
        self._workflows[workflow.id] = workflow

    def get_by_id(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID."""
        return self._workflows.get(workflow_id)

    def get_all(self) -> List[Workflow]:
        """Get all workflows."""
        return list(self._workflows.values())

    def delete(self, workflow_id: str) -> bool:
        """Delete a workflow."""
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            return True
        return False
