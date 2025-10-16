"""
Simple orchestrator - coordinates high-level workflow execution.

Follows Open/Closed Principle: Uses PlanningService dynamically instead of hard-coded tasks.
"""

from typing import Dict, Any, List, Optional
from vivek.application.services.vivek_application_service import VivekApplicationService
from vivek.domain.workflow.models.task import Task


class SimpleOrchestrator:
    """
    Orchestrates the complete workflow from user request to execution.

    Responsibilities:
    - Convert user input into tasks (via planning)
    - Execute tasks in order
    - Track conversation state
    - Return final results
    """

    def __init__(self, app_service: VivekApplicationService):
        """
        Initialize with application service.

        Args:
            app_service: Application service for coordination
        """
        self.app_service = app_service

    def process_user_request(
        self, user_input: str, thread_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Process a user request end-to-end.

        Args:
            user_input: User's request
            thread_id: Conversation thread ID

        Returns:
            Dict with execution results
        """
        # Save conversation state
        self.app_service.save_conversation_state(
            thread_id, {"user_input": user_input}
        )

        # Create workflow and plan
        workflow_id = f"wf_{thread_id}_{hash(user_input) % 10000}"
        plan_id = f"plan_{thread_id}_{hash(user_input) % 10000}"

        try:
            workflow = self.app_service.workflow_service.create_workflow(
                workflow_id, user_input
            )
        except ValueError:
            # Workflow already exists, get it
            workflow = self.app_service.workflow_service.get_workflow(workflow_id)

        try:
            plan = self.app_service.planning_service.create_plan(plan_id, user_input)
        except ValueError:
            # Plan already exists, get it
            plan = self.app_service.planning_service.get_plan(plan_id)

        # Generate tasks using planning (for now, use simple heuristic)
        tasks = self._generate_tasks_from_request(user_input)

        # Add tasks to plan and workflow
        for task in tasks:
            self.app_service.planning_service.add_task_to_plan(plan_id, task)
            self.app_service.workflow_service.add_task_to_workflow(workflow_id, task)

        # Execute tasks
        results = []
        completed_task_ids = []

        for task in tasks:
            # Check if task can execute (dependencies met)
            if not task.can_execute(completed_task_ids):
                results.append(
                    {
                        "task_id": task.id,
                        "status": "blocked",
                        "message": "Dependencies not met",
                    }
                )
                continue

            try:
                response = self.app_service.execute_task_with_llm(task)
                results.append(
                    {"task_id": task.id, "status": "completed", "result": response}
                )
                completed_task_ids.append(task.id)
            except Exception as e:
                results.append(
                    {"task_id": task.id, "status": "failed", "error": str(e)}
                )
                break  # Stop on first failure

        # Get final workflow status
        workflow = self.app_service.workflow_service.get_workflow(workflow_id)
        if workflow:
            workflow_status = {
                "id": workflow.id,
                "status": workflow.status.value,
                "total_tasks": len(workflow.tasks),
                "pending": len(workflow.get_pending_tasks()),
                "completed": len(workflow.get_completed_tasks()),
            }
        else:
            workflow_status = {"error": "Workflow not found"}

        return {
            "status": "completed",
            "workflow_id": workflow_id,
            "plan_id": plan_id,
            "tasks_executed": len(completed_task_ids),
            "workflow_status": workflow_status,
            "results": results,
        }

    def _generate_tasks_from_request(self, user_input: str) -> List[Task]:
        """
        Generate tasks from user request.

        This is a simple heuristic. In a full implementation,
        this would use an LLM to analyze the request and generate tasks.

        Args:
            user_input: User's request

        Returns:
            List of tasks
        """
        # Simple heuristic based on keywords
        tasks = []

        if any(keyword in user_input.lower() for keyword in ["create", "implement", "build", "add"]):
            tasks.append(
                Task(
                    id="task_analyze",
                    description=f"Analyze requirements for: {user_input}",
                )
            )
            tasks.append(
                Task(
                    id="task_implement",
                    description=f"Implement the requested changes",
                    dependencies=["task_analyze"],
                )
            )
        elif any(keyword in user_input.lower() for keyword in ["fix", "bug", "error"]):
            tasks.append(
                Task(id="task_diagnose", description=f"Diagnose the issue: {user_input}")
            )
            tasks.append(
                Task(
                    id="task_fix",
                    description="Apply the fix",
                    dependencies=["task_diagnose"],
                )
            )
        else:
            # Default: single task
            tasks.append(Task(id="task_execute", description=user_input))

        return tasks

    def get_conversation_history(self, thread_id: str) -> Optional[Dict[str, Any]]:
        """
        Get conversation history for a thread.

        Args:
            thread_id: Thread ID

        Returns:
            Conversation state if found
        """
        return self.app_service.load_conversation_state(thread_id)

    def list_conversations(self) -> List[str]:
        """
        List all conversation threads.

        Returns:
            List of thread IDs
        """
        return self.app_service.list_conversation_threads()
