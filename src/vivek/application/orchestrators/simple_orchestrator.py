"""
Simple orchestrator - demonstrates the new clean architecture.
"""

from typing import Dict, Any, List, Optional

# Import for direct execution (python src/vivek/cli.py)
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from application.services.vivek_application_service import VivekApplicationService

# Import for direct execution (python src/vivek/cli.py)
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from domain.workflow.models.task import Task
from domain.workflow.models.work_item import WorkItem


class SimpleOrchestrator:
    """Simple orchestrator that coordinates the entire workflow."""

    def __init__(self, app_service: VivekApplicationService):
        """Initialize with application service."""
        self.app_service = app_service

    def process_user_request(
        self, user_input: str, thread_id: str = "default"
    ) -> Dict[str, Any]:
        """Process a user request through the simplified workflow."""

        # Save conversation state
        self.app_service.save_conversation_state(thread_id, {"user_input": user_input})

        # Create new project/workflow
        project = self.app_service.create_new_project(user_input)

        # Create sample tasks (in real implementation, this would be done by planning)
        tasks = [
            Task(id="task_1", description="Analyze the user requirements"),
            Task(id="task_2", description="Create implementation plan"),
            Task(id="task_3", description="Execute the requested changes"),
        ]

        # Execute tasks one by one
        results = []
        for task in tasks:
            result = self.app_service.execute_task(project["workflow_id"], task)
            results.append(result)

            # If task failed, stop execution
            if result["status"] == "error":
                break

        # Get final status
        workflow_status = self.app_service.get_workflow_status(project["workflow_id"])

        return {
            "status": "completed",
            "project_id": project["workflow_id"],
            "tasks_executed": len([r for r in results if r["status"] == "completed"]),
            "workflow_status": workflow_status,
            "results": results,
        }

    def get_conversation_history(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation history for a thread."""
        return self.app_service.load_conversation_state(thread_id)

    def list_conversations(self) -> List[str]:
        """List all conversation threads."""
        return self.app_service.get_available_threads()
