"""
Pytest configuration and fixtures for Vivek project tests.
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
from typing import Dict, Any
from click.testing import CliRunner

from vivek.core.orchestrator import VivekOrchestrator, SessionContext, TaskPlan, ReviewResult
from vivek.llm.models import PlannerModel, ExecutorModel, OllamaProvider


@pytest.fixture
def project_root(tmp_path) -> Path:
    """Create a temporary project root directory for testing."""
    return tmp_path


@pytest.fixture
def session_context(project_root) -> SessionContext:
    """Create a SessionContext instance for testing."""
    return SessionContext(str(project_root))


@pytest.fixture
def mock_ollama_provider() -> Mock:
    """Create a mock OllamaProvider for testing."""
    mock_provider = Mock(spec=OllamaProvider)
    mock_provider.generate.return_value = "Mock response from LLM"
    return mock_provider


@pytest.fixture
def planner_model(mock_ollama_provider) -> PlannerModel:
    """Create a PlannerModel with mocked provider."""
    return PlannerModel(mock_ollama_provider)


@pytest.fixture
def executor_model(mock_ollama_provider) -> ExecutorModel:
    """Create an ExecutorModel with mocked provider."""
    return ExecutorModel(mock_ollama_provider)


@pytest.fixture
def sample_task_plan() -> Dict[str, Any]:
    """Create a sample task plan for testing."""
    return {
        "description": "Create unit tests for the project",
        "mode": "sdet",
        "steps": [
            "Analyze project structure",
            "Create test files",
            "Implement test cases",
            "Run tests to verify"
        ],
        "relevant_files": ["vivek/core/orchestrator.py", "vivek/llm/models.py"],
        "priority": "normal"
    }


@pytest.fixture
def sample_review_result() -> Dict[str, Any]:
    """Create a sample review result for testing."""
    return {
        "quality_score": 0.85,
        "needs_iteration": False,
        "feedback": "Tests look comprehensive and well-structured",
        "suggestions": ["Add more edge case tests", "Include integration tests"]
    }


@pytest.fixture
def mock_orchestrator(mock_ollama_provider, project_root) -> VivekOrchestrator:
    """Create a VivekOrchestrator with mocked dependencies."""
    orchestrator = VivekOrchestrator(
        project_root=str(project_root),
        planner_model="test-model",
        executor_model="test-model"
    )

    # Mock the planner and executor models to avoid actual LLM calls
    orchestrator.planner = Mock(spec=PlannerModel)
    orchestrator.executor = Mock(spec=ExecutorModel)

    return orchestrator


@pytest.fixture
def event_loop():
    """Create an asyncio event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def mock_ollama_dependency(monkeypatch):
    """Automatically mock ollama dependency for all tests."""
    mock_ollama = Mock()
    mock_ollama.generate.return_value = {"response": "Mock response"}
    mock_ollama.list.return_value = {"models": []}
    mock_ollama.pull.return_value = None
    monkeypatch.setattr("ollama.generate", mock_ollama.generate)
    monkeypatch.setattr("ollama.list", mock_ollama.list)
    monkeypatch.setattr("ollama.pull", mock_ollama.pull)


@pytest.fixture
def temp_config_file(tmp_path) -> Path:
    """Create a temporary Vivek config file for testing."""
    config_dir = tmp_path / ".vivek"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "config.yml"
    config_content = {
        'project_settings': {
            'language': ['Python'],
            'framework': ['FastAPI'],
            'test_framework': ['pytest'],
            'package_manager': ['pip']
        },
        'llm_configuration': {
            'mode': 'local',
            'planner_model': 'qwen2.5-coder:7b',
            'executor_model': 'qwen2.5-coder:7b',
            'fallback_enabled': True,
            'auto_switch': True
        },
        'preferences': {
            'default_mode': 'peer',
            'search_enabled': True,
            'auto_index': True,
            'privacy_mode': False
        }
    }

    import yaml
    with open(config_file, 'w') as f:
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
        "Optimize the database queries for better performance"
    ]


@pytest.fixture
def sample_cli_args() -> Dict[str, Any]:
    """Provide sample CLI arguments for testing."""
    return {
        'mode': 'local',
        'planner_model': 'qwen2.5-coder:7b',
        'executor_model': 'qwen2.5-coder:7b'
    }


@pytest.fixture
def runner() -> CliRunner:
    """Create a CliRunner for testing CLI commands."""
    return CliRunner()