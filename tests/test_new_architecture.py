"""
Tests for the new clean architecture.
Following SOLID principles and DRY - uses centralized mocks from tests.mocks
"""

import pytest
from tests.mocks import MockLLMProvider, MockStateRepository

from vivek import (
    Task, TaskStatus, TaskComplexity,
    Workflow, WorkflowStatus,
    TaskPlan, PlanStatus,
    ServiceContainer,
    SimpleOrchestrator,
    VivekApplicationService
)
from vivek.domain.workflow.repositories.workflow_repository import InMemoryWorkflowRepository
from vivek.domain.planning.repositories.plan_repository import InMemoryPlanRepository
from vivek.domain.workflow.services.workflow_service import WorkflowService
from vivek.domain.planning.services.planning_service import PlanningService


class TestTaskModel:
    """Test the rich Task domain model."""

    def test_task_creation(self):
        """Test creating a task."""
        task = Task(id="test_1", description="Test task")
        assert task.id == "test_1"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.created_at is not None

    def test_task_lifecycle(self):
        """Test task state transitions."""
        task = Task(id="t1", description="Test task")
        task.start()
        assert task.status == TaskStatus.IN_PROGRESS

        task.complete(result="Success")
        assert task.status == TaskStatus.COMPLETED
        assert task.result == "Success"

    def test_task_validation(self):
        """Test task validation."""
        valid_task = Task(id="t1", description="Valid task")
        errors = valid_task.validate()
        assert len(errors) == 0


class TestDIContainer:
    """Test dependency injection container."""

    def test_container_provides_services(self):
        """Test container provides all services."""
        config = {"llm_provider": "mock", "state_storage": "memory"}
        container = ServiceContainer(config)

        assert container.get_workflow_service() is not None
        assert container.get_planning_service() is not None
        assert container.get_llm_provider() is not None
        assert container.get_state_repository() is not None


class TestApplicationService:
    """Test application service."""

    @pytest.fixture
    def app_service(self):
        """Create application service with mocks."""
        container = ServiceContainer({
            "llm_provider": "mock",
            "state_storage": "memory"
        })

        return VivekApplicationService(
            workflow_service=container.get_workflow_service(),
            planning_service=container.get_planning_service(),
            llm_provider=container.get_llm_provider(),
            state_repository=container.get_state_repository()
        )

    def test_task_execution(self, app_service):
        """Test task execution with LLM."""
        task = Task(id="t1", description="Test task")
        result = app_service.execute_task_with_llm(task)

        assert result is not None
        assert task.status == TaskStatus.COMPLETED


class TestOrchestrator:
    """Test orchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator with mocks."""
        container = ServiceContainer({
            "llm_provider": "mock",
            "state_storage": "memory"
        })

        app_service = VivekApplicationService(
            workflow_service=container.get_workflow_service(),
            planning_service=container.get_planning_service(),
            llm_provider=container.get_llm_provider(),
            state_repository=container.get_state_repository()
        )

        return SimpleOrchestrator(app_service)

    def test_process_user_request(self, orchestrator):
        """Test processing a user request."""
        result = orchestrator.process_user_request("Create a simple function")

        assert result["status"] == "completed"
        assert "workflow_id" in result
        assert result["tasks_executed"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
