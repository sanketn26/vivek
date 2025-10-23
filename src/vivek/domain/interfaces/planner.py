from abc import abstractmethod
from typing import Protocol

from vivek.domain.planning.models.plan import Plan


class IPlannerService(Protocol):
    """Interface for planning service."""

    @abstractmethod
    async def create_plan(self, user_request: str, project_context: str) -> Plan:
        """Create execution plan from user request.

        Args:
            user_request: What user wants to implement
            project_context: Project information

        Returns:
            Plan with 3-5 work items
        """
        ...
