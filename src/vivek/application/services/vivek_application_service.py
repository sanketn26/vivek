"""
Main Vivek application service - coordinates domain services.

Simplified to follow Single Responsibility Principle.
Each method has one clear purpose.
"""

from typing import Dict, Any, List, Optional
from vivek.domain.workflow.services.workflow_service import WorkflowService
from vivek.domain.planning.services.planning_service import PlanningService
from vivek.domain.workflow.models.task import Task
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.infrastructure.persistence.state_repository import StateRepository


class VivekApplicationService:
    """
    Application service for coordinating Vivek workflows.

    Responsibilities:
    - Coordinate between domain services
    - Manage conversation state
    - Execute tasks using LLM
    """

    def __init__(
        self,
        workflow_service: WorkflowService,
        planning_service: PlanningService,
        llm_provider: LLMProvider,
        state_repository: StateRepository,
    ):
        """
        Initialize with injected dependencies.

        Args:
            workflow_service: Service for managing workflows
            planning_service: Service for task planning
            llm_provider: LLM for task execution
            state_repository: Repository for conversation state
        """
        self.workflow_service = workflow_service
        self.planning_service = planning_service
        self.llm_provider = llm_provider
        self.state_repository = state_repository

    def execute_task_with_llm(self, task: Task) -> str:
        """
        Execute a task using the LLM.

        Args:
            task: Task to execute

        Returns:
            LLM response

        Raises:
            RuntimeError: If LLM execution fails
        """
        if not task or not task.description:
            raise ValueError("Task must have a description")

        prompt = self._build_task_prompt(task)

        try:
            task.start()
            response = self.llm_provider.generate(prompt)
            task.complete(result=response)
            return response
        except Exception as e:
            task.fail(str(e))
            raise RuntimeError(f"Task execution failed: {str(e)}") from e

    def _build_task_prompt(self, task: Task) -> str:
        """Build LLM prompt for a task."""
        parts = [f"Execute this task: {task.description}"]

        if task.file_path:
            parts.append(f"File: {task.file_path}")

        return "\n".join(parts)

    def save_conversation_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        """
        Save conversation state.

        Args:
            thread_id: Unique conversation thread ID
            state: State data to save
        """
        self.state_repository.save_state(thread_id, state)

    def load_conversation_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Load conversation state.

        Args:
            thread_id: Conversation thread ID

        Returns:
            State data if found, None otherwise
        """
        return self.state_repository.load_state(thread_id)

    def list_conversation_threads(self) -> List[str]:
        """
        Get all conversation thread IDs.

        Returns:
            List of thread IDs
        """
        return self.state_repository.list_threads()
