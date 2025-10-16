"""
Pytest configuration and fixtures for Vivek project tests (New Architecture).
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock
from typing import Dict, Any
from click.testing import CliRunner

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import new simplified architecture components
from vivek.application.orchestrators.simple_orchestrator import SimpleOrchestrator
from vivek.application.services.vivek_application_service import VivekApplicationService
from vivek.domain.workflow.services.workflow_service import WorkflowService
from vivek.domain.planning.services.planning_service import PlanningService
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.infrastructure.persistence.state_repository import StateRepository
from vivek.domain.workflow.models.task import Task


@pytest.fixture
def project_root(tmp_path) -> Path:
    """Create a temporary project root directory for testing."""
    return tmp_path


@pytest.fixture
def mock_llm_provider() -> Mock:
    """Create a mock LLMProvider for testing."""
    mock_provider = Mock(spec=LLMProvider)
    mock_provider.generate.return_value = "Mock response from LLM"
    mock_provider.is_available.return_value = True
    mock_provider.model_name = "test-model"
    return mock_provider


@pytest.fixture
def mock_state_repository() -> Mock:
    """Create a mock StateRepository for testing."""
    mock_repo = Mock(spec=StateRepository)
    mock_repo.save_state.return_value = None
    mock_repo.load_state.return_value = None
    mock_repo.delete_state.return_value = True
    mock_repo.list_threads.return_value = []
    return mock_repo


@pytest.fixture
def sample_task() -> Task:
    """Create a sample Task for testing."""
    return Task(id="test_task_1", description="Create unit tests for the project")


@pytest.fixture
def sample_task_plan() -> Dict[str, Any]:
    """Create a sample task plan for testing."""
    return {
        "description": "Create unit tests for the project",
        "mode": "sdet",
        "work_items": [
            {
                "mode": "sdet",
                "file_path": "tests/test_orchestrator.py",
                "file_status": "new",
                "description": "Create unit tests for simple_orchestrator.py with pytest",
                "dependencies": [],
            },
            {
                "mode": "sdet",
                "file_path": "tests/test_models.py",
                "file_status": "existing",
                "description": "Add additional test cases for new architecture",
                "dependencies": [],
            },
        ],
        "priority": "normal",
    }


@pytest.fixture
def sample_review_result() -> Dict[str, Any]:
    """Create a sample review result for testing."""
    return {
        "quality_score": 0.85,
        "needs_iteration": False,
        "feedback": "Tests look comprehensive and well-structured",
        "suggestions": ["Add more edge case tests", "Include integration tests"],
    }


@pytest.fixture
def workflow_service() -> WorkflowService:
    """Create a WorkflowService for testing."""
    return WorkflowService()


@pytest.fixture
def planning_service() -> PlanningService:
    """Create a PlanningService for testing."""
    return PlanningService()


@pytest.fixture
def vivek_app_service(mock_llm_provider, mock_state_repository) -> VivekApplicationService:
    """Create a VivekApplicationService with mocked dependencies."""
    return VivekApplicationService(
        workflow_service=WorkflowService(),
        planning_service=PlanningService(),
        llm_provider=mock_llm_provider,
        state_repository=mock_state_repository
    )


@pytest.fixture
def simple_orchestrator(vivek_app_service) -> SimpleOrchestrator:
    """Create a SimpleOrchestrator with mocked dependencies."""
    return SimpleOrchestrator(vivek_app_service)


@pytest.fixture
def event_loop():
    """Create an asyncio event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_llm_dependency(monkeypatch):
    """Automatically mock LLM dependencies for all tests."""
    # Mock any external LLM dependencies that tests might encounter
    mock_ollama = Mock()
    mock_ollama.generate.return_value = {"response": "Mock response"}
    mock_ollama.list.return_value = {"models": []}
    mock_ollama.pull.return_value = None

    # Apply mocks only if ollama is actually imported
    try:
        import ollama
        monkeypatch.setattr("ollama.generate", mock_ollama.generate)
        monkeypatch.setattr("ollama.list", mock_ollama.list)
        monkeypatch.setattr("ollama.pull", mock_ollama.pull)
    except ImportError:
        pass  # ollama not available, skip mocking


@pytest.fixture
def temp_config_file(tmp_path) -> Path:
    """Create a temporary Vivek config file for testing."""
    config_dir = tmp_path / ".vivek"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config.yml"
    # Simplified config for new architecture
    config_content = {
        "model": "qwen2.5-coder:7b",
        "version": "2.0-simplified"
    }

    import yaml

    with open(config_file, "w") as f:
        yaml.dump(config_content, f)

    return config_file


@pytest.fixture
def sample_user_inputs() -> list:
    """Provide sample user inputs for testing."""
    return [
        "Create unit tests for the project",
        "Implement a new feature for user authentication",
        "Fix the bug in the data processing module",
        "Add documentation for the API endpoints",
        "Optimize the database queries for better performance",
    ]


@pytest.fixture
def sample_cli_args() -> Dict[str, Any]:
    """Provide sample CLI arguments for testing."""
    return {
        "mode": "local",
        "planner_model": "qwen2.5-coder:7b",
        "executor_model": "qwen2.5-coder:7b",
    }


@pytest.fixture
def runner() -> CliRunner:
    """Create a CliRunner for testing CLI commands."""
    return CliRunner()
