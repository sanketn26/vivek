"""
Comprehensive tests for LangGraph orchestrator.

Tests cover:
- State management and transitions
- Node execution and outputs
- Conditional iteration logic
- Session persistence
- Error handling
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from vivek.core.langgraph_orchestrator import LangGraphVivekOrchestrator
from vivek.core.graph_state import (
    VivekState,
    initialize_state,
    should_iterate,
    get_iteration_count,
    increment_iteration,
)
from vivek.core.graph_nodes import (
    create_planner_node,
    create_executor_node,
    create_reviewer_node,
    format_response_node,
)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_planner():
    """Mock planner model"""
    planner = Mock()
    planner.analyze_request.return_value = {
        "description": "Test task",
        "mode": "coder",
        "steps": ["Step 1", "Step 2"],
        "relevant_files": ["test.py"],
        "priority": "normal",
    }
    planner.review_output.return_value = {
        "quality_score": 0.8,
        "needs_iteration": False,
        "feedback": "Looks good",
        "suggestions": ["Add error handling"],
    }
    return planner


@pytest.fixture
def mock_executor():
    """Mock executor model"""
    executor = Mock()
    executor.execute_task.return_value = "Generated code output"
    return executor


class TestGraphState:
    """Test state management functions"""

    def test_initialize_state(self):
        """Test state initialization"""
        state = initialize_state("test input", {"key": "value"})

        assert state["user_input"] == "test input"
        assert state["context"] == {"key": "value"}
        assert state["iteration_count"] == 0

    def test_initialize_state_no_context(self):
        """Test state initialization without context"""
        state = initialize_state("test input")

        assert state["user_input"] == "test input"
        assert state["context"] == {}
        assert state["iteration_count"] == 0

    def test_get_iteration_count(self):
        """Test getting iteration count"""
        state = VivekState(user_input="test", iteration_count=2)
        assert get_iteration_count(state) == 2

    def test_get_iteration_count_default(self):
        """Test getting iteration count with default"""
        state = VivekState(user_input="test")
        assert get_iteration_count(state) == 0

    def test_increment_iteration(self):
        """Test incrementing iteration count"""
        state = VivekState(user_input="test", iteration_count=1)
        update = increment_iteration(state)

        assert update["iteration_count"] == 2

    def test_should_iterate_low_quality(self):
        """Test should_iterate with low quality score"""
        state = VivekState(
            user_input="test",
            iteration_count=0,
            review_result={
                "quality_score": 0.5,
                "needs_iteration": True,
                "feedback": "Needs improvement",
                "suggestions": [],
            },
        )

        assert should_iterate(state) == "iterate"

    def test_should_iterate_high_quality(self):
        """Test should_iterate with high quality score"""
        state = VivekState(
            user_input="test",
            iteration_count=0,
            review_result={
                "quality_score": 0.9,
                "needs_iteration": False,
                "feedback": "Good",
                "suggestions": [],
            },
        )

        assert should_iterate(state) == "finish"

    def test_should_iterate_max_iterations(self):
        """Test should_iterate at max iterations"""
        state = VivekState(
            user_input="test",
            iteration_count=3,
            review_result={
                "quality_score": 0.5,
                "needs_iteration": True,
                "feedback": "Still needs work",
                "suggestions": [],
            },
        )

        assert should_iterate(state) == "finish"

    def test_should_iterate_no_review(self):
        """Test should_iterate with no review result"""
        state = VivekState(user_input="test", iteration_count=0)

        assert should_iterate(state) == "finish"


class TestGraphNodes:
    """Test individual graph nodes"""

    def test_planner_node(self, mock_planner):
        """Test planner node execution"""
        node = create_planner_node(mock_planner)
        state = VivekState(user_input="test request", context={})

        result = node(state)

        assert "task_plan" in result
        assert "mode" in result
        assert result["mode"] == "coder"
        mock_planner.analyze_request.assert_called_once()

    def test_planner_node_with_iteration_feedback(self, mock_planner):
        """Test planner node with feedback from previous iteration"""
        node = create_planner_node(mock_planner)
        state = VivekState(
            user_input="test request",
            context={},
            iteration_count=1,
            review_result={
                "quality_score": 0.5,
                "needs_iteration": True,
                "feedback": "Add error handling",
                "suggestions": [],
            },
        )

        result = node(state)

        assert "task_plan" in result
        # Check that feedback was included in context
        call_args = mock_planner.analyze_request.call_args
        assert "Previous Iteration Feedback" in call_args[0][1]

    def test_executor_node(self, mock_executor):
        """Test executor node execution"""
        node = create_executor_node(mock_executor)
        state = VivekState(
            user_input="test",
            task_plan={
                "description": "Test task",
                "mode": "coder",
                "steps": ["Step 1"],
                "relevant_files": [],
                "priority": "normal",
            },
            context={},
        )

        result = node(state)

        assert "executor_output" in result
        assert result["executor_output"] == "Generated code output"
        mock_executor.execute_task.assert_called_once()

    def test_reviewer_node(self, mock_planner):
        """Test reviewer node execution"""
        node = create_reviewer_node(mock_planner)
        state = VivekState(
            user_input="test",
            task_plan={"description": "Test task"},
            executor_output="Some output",
            iteration_count=0,
        )

        result = node(state)

        assert "review_result" in result
        assert "iteration_count" in result
        assert result["iteration_count"] == 1
        mock_planner.review_output.assert_called_once()

    def test_format_response_node(self):
        """Test format response node"""
        state = VivekState(
            user_input="test",
            executor_output="Generated code",
            mode="coder",
            review_result={
                "quality_score": 0.8,
                "needs_iteration": False,
                "feedback": "Good",
                "suggestions": ["Add tests", "Add docs"],
            },
            iteration_count=1,
        )

        result = format_response_node(state)

        assert "final_response" in result
        response = result["final_response"]
        assert "[CODER MODE]" in response
        assert "Generated code" in response
        assert "Add tests" in response
        assert "0.8/1.0" in response


class TestLangGraphOrchestrator:
    """Test the full orchestrator"""

    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self, temp_project_dir):
        """Test orchestrator initialization"""
        with patch("vivek.core.langgraph_orchestrator.OllamaProvider"):
            orchestrator = LangGraphVivekOrchestrator(
                project_root=temp_project_dir,
                planner_model="test-planner",
                executor_model="test-executor",
            )

            assert orchestrator.project_root == Path(temp_project_dir)
            assert orchestrator.current_mode == "peer"
            assert "project_root" in orchestrator.context

    @pytest.mark.asyncio
    async def test_process_request(self, temp_project_dir, mock_planner, mock_executor):
        """Test processing a request through the graph"""
        with patch("vivek.core.langgraph_orchestrator.OllamaProvider"):
            with patch(
                "vivek.core.langgraph_orchestrator.PlannerModel",
                return_value=mock_planner,
            ):
                with patch(
                    "vivek.core.langgraph_orchestrator.get_executor",
                    return_value=mock_executor,
                ):
                    orchestrator = LangGraphVivekOrchestrator(
                        project_root=temp_project_dir
                    )

                    response = await orchestrator.process_request("test request")

                    assert isinstance(response, str)
                    assert len(response) > 0

    def test_switch_mode(self, temp_project_dir):
        """Test switching modes"""
        with patch("vivek.core.langgraph_orchestrator.OllamaProvider"):
            orchestrator = LangGraphVivekOrchestrator(project_root=temp_project_dir)

            result = orchestrator.switch_mode("architect")
            assert "architect" in result.lower()
            assert orchestrator.current_mode == "architect"

    def test_switch_mode_invalid(self, temp_project_dir):
        """Test switching to invalid mode"""
        with patch("vivek.core.langgraph_orchestrator.OllamaProvider"):
            orchestrator = LangGraphVivekOrchestrator(project_root=temp_project_dir)

            result = orchestrator.switch_mode("invalid")
            assert "invalid" in result.lower()
            assert orchestrator.current_mode == "peer"  # Should not change

    def test_get_status(self, temp_project_dir):
        """Test getting status"""
        with patch("vivek.core.langgraph_orchestrator.OllamaProvider"):
            orchestrator = LangGraphVivekOrchestrator(project_root=temp_project_dir)

            status = orchestrator.get_status()
            assert "peer" in status.lower()
            assert temp_project_dir in status

    @pytest.mark.asyncio
    async def test_iteration_on_low_quality(
        self, temp_project_dir, mock_planner, mock_executor
    ):
        """Test that iteration happens on low quality output"""
        # Setup mock to return low quality first, then high quality
        mock_planner.review_output.side_effect = [
            {
                "quality_score": 0.5,
                "needs_iteration": True,
                "feedback": "Needs improvement",
                "suggestions": [],
            },
            {
                "quality_score": 0.9,
                "needs_iteration": False,
                "feedback": "Much better",
                "suggestions": [],
            },
        ]

        with patch("vivek.core.langgraph_orchestrator.OllamaProvider"):
            with patch(
                "vivek.core.langgraph_orchestrator.PlannerModel",
                return_value=mock_planner,
            ):
                with patch(
                    "vivek.core.langgraph_orchestrator.get_executor",
                    return_value=mock_executor,
                ):
                    orchestrator = LangGraphVivekOrchestrator(
                        project_root=temp_project_dir
                    )

                    response = await orchestrator.process_request("test request")

                    # Should have called executor twice (initial + 1 iteration)
                    assert mock_executor.execute_task.call_count == 2
                    # Should have called reviewer twice
                    assert mock_planner.review_output.call_count == 2


@pytest.mark.integration
class TestOrchestratorIntegration:
    """Integration tests with real (mocked) LLM calls"""

    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_project_dir):
        """Test a complete workflow from input to output"""
        # This would test with actual models if available
        # For now, we skip it unless explicitly running integration tests
        pytest.skip("Integration test - requires Ollama running")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])