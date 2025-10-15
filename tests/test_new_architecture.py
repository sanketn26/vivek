"""
Tests for the new simplified Vivek architecture.

This test file focuses on testing the core functionality of the new
Domain-Driven Design architecture.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock
from click.testing import CliRunner

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from vivek.domain.workflow.models.task import Task
from vivek.domain.workflow.models.workflow import Workflow, WorkflowStatus
from vivek.domain.workflow.services.workflow_service import WorkflowService
from vivek.domain.planning.services.planning_service import PlanningService
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.infrastructure.persistence.state_repository import StateRepository
from vivek.application.services.vivek_application_service import VivekApplicationService
from vivek.application.orchestrators.simple_orchestrator import SimpleOrchestrator
from vivek.cli import cli, init, chat


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing."""

    def __init__(self):
        super().__init__("mock-model")

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        return f"Mock response to: {prompt[:50]}..."

    def is_available(self) -> bool:
        return True


class MockStateRepository(StateRepository):
    """Mock state repository for testing."""

    def __init__(self):
        self.storage = {}

    def save_state(self, thread_id: str, state: dict) -> None:
        self.storage[thread_id] = state

    def load_state(self, thread_id: str) -> dict | None:
        return self.storage.get(thread_id)

    def delete_state(self, thread_id: str) -> bool:
        if thread_id in self.storage:
            del self.storage[thread_id]
            return True
        return False

    def list_threads(self) -> list[str]:
        return list(self.storage.keys())


class TestNewArchitecture:
    """Test cases for the new simplified architecture."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(id="test_1", description="Test task")
        assert task.id == "test_1"
        assert task.description == "Test task"
        assert task.status == "pending"
        assert task.created_at is not None

    def test_task_mark_completed(self):
        """Test marking a task as completed."""
        task = Task(id="test_1", description="Test task")
        task.mark_completed()
        assert task.status == "completed"
        assert task.completed_at is not None

    def test_workflow_creation(self):
        """Test creating a workflow."""
        workflow = Workflow(id="wf_1", description="Test workflow")
        assert workflow.id == "wf_1"
        assert workflow.description == "Test workflow"
        assert workflow.status == WorkflowStatus.PLANNING
        assert len(workflow.tasks) == 0

    def test_workflow_add_task(self):
        """Test adding tasks to a workflow."""
        workflow = Workflow(id="wf_1", description="Test workflow")
        task = Task(id="task_1", description="Test task")

        workflow.add_task(task)
        assert len(workflow.tasks) == 1
        assert workflow.tasks[0] == task

    def test_workflow_service(self):
        """Test workflow service functionality."""
        service = WorkflowService()

        # Create workflow
        workflow = service.create_workflow("test_wf", "Test workflow")
        assert workflow.id == "test_wf"

        # Add task
        task = Task(id="task_1", description="Test task")
        success = service.add_task_to_workflow("test_wf", task)
        assert success is True

        # Get pending tasks
        pending = service.get_pending_tasks("test_wf")
        assert len(pending) == 1

    def test_planning_service(self):
        """Test planning service functionality."""
        service = PlanningService()

        # Create plan
        plan = service.create_plan("test_plan", "Test plan")
        assert plan.id == "test_plan"

        # Check pending work
        pending = service.get_pending_work_count("test_plan")
        assert pending == 0

    def test_vivek_application_service(self):
        """Test the main application service."""
        workflow_service = WorkflowService()
        planning_service = PlanningService()
        llm_provider = MockLLMProvider()
        state_repository = MockStateRepository()

        app_service = VivekApplicationService(
            workflow_service=workflow_service,
            planning_service=planning_service,
            llm_provider=llm_provider,
            state_repository=state_repository
        )

        # Test creating new project
        result = app_service.create_new_project("Test project")
        assert "workflow_id" in result
        assert "plan_id" in result
        assert result["status"] == "created"

        # Test executing task
        task = Task(id="task_1", description="Test task")
        result = app_service.execute_task(result["workflow_id"], task)
        assert result["status"] == "completed"

    def test_simple_orchestrator(self):
        """Test the simple orchestrator."""
        workflow_service = WorkflowService()
        planning_service = PlanningService()
        llm_provider = MockLLMProvider()
        state_repository = MockStateRepository()

        app_service = VivekApplicationService(
            workflow_service=workflow_service,
            planning_service=planning_service,
            llm_provider=llm_provider,
            state_repository=state_repository
        )

        orchestrator = SimpleOrchestrator(app_service)

        # Test processing request
        result = orchestrator.process_user_request("Test request")
        assert result["status"] == "completed"
        assert "project_id" in result
        assert "tasks_executed" in result


class TestNewCLI:
    """Test cases for the new simplified CLI."""

    def test_cli_group_creation(self):
        """Test that the CLI group is properly created."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Vivek - Your AI Coding Assistant" in result.output

    def test_init_command(self):
        """Test the init command."""
        runner = CliRunner()
        result = runner.invoke(init, ["--model", "test-model"])
        assert result.exit_code == 0
        assert "Vivek 2.0 initialized successfully" in result.output
        assert "test-model" in result.output

    def test_chat_command_without_config(self, tmp_path):
        """Test chat command when no config exists."""
        import os
        runner = CliRunner()

        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(chat)
            # Should show error about missing config
            assert (
                "No vivek configuration found" in result.output or
                result.exit_code != 0
            )
        finally:
            os.chdir(original_dir)


if __name__ == "__main__":
    # Run basic tests
    print("🧪 Testing new architecture components...")

    # Test task creation
    task = Task(id="test", description="Test task")
    print(f"✅ Task created: {task.id}")

    # Test workflow creation
    workflow = Workflow(id="wf_test", description="Test workflow")
    print(f"✅ Workflow created: {workflow.id}")

    # Test services
    workflow_service = WorkflowService()
    wf = workflow_service.create_workflow("test", "Test")
    print(f"✅ WorkflowService works: {wf.id}")

    print("\n🎉 New architecture tests passed!")