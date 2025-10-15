"""
Main Vivek application service - simple orchestration of domain services.
"""

from typing import Dict, Any, List, Optional

# Import for direct execution (python src/vivek/cli.py)
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from domain.workflow.services.workflow_service import WorkflowService
from domain.planning.services.planning_service import PlanningService
from infrastructure.llm.llm_provider import LLMProvider
from infrastructure.persistence.state_repository import StateRepository

# Import for direct execution (python src/vivek/cli.py)
from domain.workflow.models.task import Task
from domain.workflow.models.work_item import WorkItem


class VivekApplicationService:
    """Simple application service that orchestrates all domain services."""

    def __init__(
        self,
        workflow_service: WorkflowService,
        planning_service: PlanningService,
        llm_provider: LLMProvider,
        state_repository: StateRepository,
    ):
        """Initialize with required services."""
        self.workflow_service = workflow_service
        self.planning_service = planning_service
        self.llm_provider = llm_provider
        self.state_repository = state_repository

    def create_new_project(self, user_request: str) -> Dict[str, Any]:
        """Create a new project from user request."""
        # Create workflow for the project
        workflow = self.workflow_service.create_workflow(
            id=f"wf_{user_request[:20]}", description=user_request
        )

        # Create task plan
        plan = self.planning_service.create_plan(
            id=f"plan_{user_request[:20]}", description=user_request
        )

        return {"workflow_id": workflow.id, "plan_id": plan.id, "status": "created"}

    def execute_task(self, workflow_id: str, task: Task) -> Dict[str, Any]:
        """Execute a single task."""
        # Add task to workflow
        success = self.workflow_service.add_task_to_workflow(workflow_id, task)

        if not success:
            return {"status": "error", "message": "Workflow not found"}

        # Generate prompt for LLM
        prompt = f"Execute this task: {task.description}"

        # Execute with LLM
        response = self.llm_provider.generate(prompt)

        # Mark task as completed
        task.mark_completed()

        return {"status": "completed", "task_id": task.id, "result": response}

    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of a workflow."""
        workflow = self.workflow_service.get_workflow(workflow_id)

        if not workflow:
            return {"status": "error", "message": "Workflow not found"}

        pending_tasks = workflow.get_pending_tasks()
        completed_tasks = workflow.get_completed_tasks()

        return {
            "workflow_id": workflow.id,
            "status": workflow.status.value,
            "pending_tasks": len(pending_tasks),
            "completed_tasks": len(completed_tasks),
            "total_tasks": len(workflow.tasks),
        }

    def save_conversation_state(self, thread_id: str, state: Dict[str, Any]) -> None:
        """Save conversation state."""
        self.state_repository.save_state(thread_id, state)

    def load_conversation_state(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Load conversation state."""
        return self.state_repository.load_state(thread_id)

    def get_available_threads(self) -> List[str]:
        """Get all available conversation threads."""
        return self.state_repository.list_threads()
