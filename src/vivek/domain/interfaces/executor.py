"""Executor service interface."""

from abc import abstractmethod
from typing import Protocol

from vivek.domain.models.execution_result import ExecutionResult
from vivek.domain.models.work_item import WorkItem


class IExecutorService(Protocol):
    """Interface for execution service."""

    @abstractmethod
    async def execute(self, work_item: WorkItem) -> ExecutionResult:
        """Execute a work item.

        Args:
            work_item: Work item to execute

        Returns:
            Execution result
        """
        ...
