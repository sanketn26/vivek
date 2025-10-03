"""Tests for orchestrator message routing and clarification flow."""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from vivek.core.langgraph_orchestrator import LangGraphVivekOrchestrator
from vivek.core.graph_state import VivekState
from vivek.core.message_protocol import MessageType


class TestOrchestratorMessageRouting:
    """Test orchestrator routes messages correctly."""

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider."""
        provider = Mock()
        provider.generate = Mock(return_value="test response")
        return provider

    @pytest.fixture
    def orchestrator(self, mock_provider, tmp_path):
        """Create orchestrator with temp checkpoint."""
        # LangGraphVivekOrchestrator uses model names, not providers directly
        # We'll need to patch the provider creation
        with patch('vivek.core.langgraph_orchestrator.OllamaProvider') as mock_ollama:
            mock_ollama.return_value = mock_provider
            orch = LangGraphVivekOrchestrator(
                project_root=str(tmp_path),
                planner_model="test-model",
                executor_model="test-model"
            )
            return orch

    @pytest.mark.asyncio
    async def test_orchestrator_handles_planner_execution_complete(self, orchestrator, mock_provider):
        """Test orchestrator routes planner execution_complete to executor."""
        # Mock planner returning execution_complete
        mock_provider.generate.return_value = json.dumps({
            "description": "test task",
            "mode": "coder",
            "work_items": [{
                "mode": "coder",
                "file_path": "test.py",
                "file_status": "new",
                "description": "create test file",
                "dependencies": []
            }],
            "priority": "normal"
        })

        result = await orchestrator.process_request(
            user_input="create a test file",
            thread_id="test_thread_1"
        )

        # Should complete without asking for clarification
        assert result["status"] == "complete"
        assert "output" in result

    @pytest.mark.asyncio
    async def test_orchestrator_handles_planner_clarification_needed(self, orchestrator, mock_provider):
        """Test orchestrator pauses when planner needs clarification."""
        # Mock planner returning clarification_needed
        # Use side_effect to return same value for all calls (planner, executor, reviewer)
        clarification_json = json.dumps({
            "needs_clarification": True,
            "questions": [
                {
                    "question": "Which framework to use?",
                    "type": "choice",
                    "options": ["pytest", "unittest", "nose"]
                }
            ],
            "partial_plan": {
                "description": "create tests",
                "mode": "sdet"
            }
        })

        # Set up mock to return clarification for planner, then fail for subsequent calls
        # This way if routing works correctly, executor won't be called
        mock_provider.generate.side_effect = [
            clarification_json,  # Planner call
            "ERROR: Should not reach executor",  # Executor (shouldn't be called)
            "ERROR: Should not reach reviewer",  # Reviewer (shouldn't be called)
        ]

        result = await orchestrator.process_request(
            user_input="create tests",
            thread_id="test_thread_2"
        )

        # Should pause for clarification after planner
        assert result["status"] == "awaiting_clarification", f"Expected awaiting_clarification but got {result['status']}"
        assert "questions" in result
        assert len(result["questions"]) == 1
        assert "thread_id" in result
        assert result["from_node"] == "planner"

        # Verify executor was NOT called (should only have 1 call to planner)
        assert mock_provider.generate.call_count == 1, f"Expected 1 call (planner only) but got {mock_provider.generate.call_count}"

    @pytest.mark.asyncio
    async def test_orchestrator_handles_executor_clarification_needed(self, orchestrator, mock_provider):
        """Test orchestrator pauses when executor needs clarification."""
        # First call: planner returns valid plan
        planner_response = json.dumps({
            "description": "modify auth",
            "mode": "coder",
            "work_items": [{
                "mode": "coder",
                "file_path": "auth.py",
                "file_status": "existing",
                "description": "add logging",
                "dependencies": []
            }],
            "priority": "normal"
        })

        # Executor will need clarification (we'll mock this in the executor itself)
        # For now, let's assume executor returns clarification in its message
        mock_provider.generate.side_effect = [
            planner_response,  # Planner
            "CLARIFICATION NEEDED: Found 3 auth.py files"  # Executor (will be caught by ambiguity check)
        ]

        # This test will need executor to have ambiguity detection
        # For now, we'll test the routing mechanism
        # Mark as pending implementation
        pytest.skip("Requires executor ambiguity detection implementation")

    @pytest.mark.asyncio
    async def test_orchestrator_routes_to_reviewer_after_executor(self, orchestrator, mock_provider):
        """Test orchestrator routes executor output to reviewer."""
        # Mock responses in sequence
        mock_provider.generate.side_effect = [
            # Planner
            json.dumps({
                "description": "test task",
                "mode": "coder",
                "work_items": [{"mode": "coder", "file_path": "test.py", "file_status": "new", "description": "test", "dependencies": []}],
                "priority": "normal"
            }),
            # Executor
            "def test(): pass",
            # Reviewer
            json.dumps({
                "quality_score": 0.9,
                "needs_iteration": False,
                "feedback": "looks good",
                "suggestions": []
            })
        ]

        result = await orchestrator.process_request(
            user_input="create test",
            thread_id="test_thread_3"
        )

        # Should complete with high quality score
        assert result["status"] == "complete"
        # Verify all 3 nodes were called (planner, executor, reviewer)
        assert mock_provider.generate.call_count == 3


class TestOrchestratorConditionalRouting:
    """Test conditional edge routing based on message type."""

    @pytest.fixture
    def mock_provider(self):
        provider = Mock()
        provider.generate = Mock()
        return provider

    @pytest.fixture
    async def orchestrator(self, mock_provider, tmp_path):
        checkpoint_db = str(tmp_path / "test_routing.db")
        return LangGraphOrchestrator(
            planner_provider=mock_provider,
            executor_provider=mock_provider,
            checkpoint_db=checkpoint_db
        )

    def test_route_planner_function_returns_correct_nodes(self):
        """Test route_planner function returns correct next node."""
        from vivek.core.graph_nodes import route_planner

        # State with execution_complete -> should go to executor
        state_complete = {"needs_clarification": False}
        assert route_planner(state_complete) == "executor"

        # State with clarification_needed -> should go to clarification
        state_clarify = {"needs_clarification": True}
        assert route_planner(state_clarify) == "clarification"

    def test_route_executor_function_returns_correct_nodes(self):
        """Test route_executor function returns correct next node."""
        from vivek.core.graph_nodes import route_executor

        # State with execution_complete -> should go to reviewer
        state_complete = {"needs_clarification": False}
        assert route_executor(state_complete) == "reviewer"

        # State with clarification_needed -> should go to clarification
        state_clarify = {"needs_clarification": True}
        assert route_executor(state_clarify) == "clarification"

    def test_route_reviewer_function_returns_correct_nodes(self):
        """Test route_reviewer function returns correct next node."""
        from vivek.core.graph_nodes import route_reviewer

        # State with clarification_needed -> clarification
        state_clarify = {"needs_clarification": True}
        assert route_reviewer(state_clarify) == "clarification"

        # State with needs_iteration -> executor
        state_iterate = {
            "needs_clarification": False,
            "review_result": {"needs_iteration": True},
            "iteration_count": 1
        }
        assert route_reviewer(state_iterate) == "executor"

        # State complete -> format_response
        state_done = {
            "needs_clarification": False,
            "review_result": {"needs_iteration": False}
        }
        assert route_reviewer(state_done) == "format_response"


class TestClarificationNode:
    """Test clarification node formatting."""

    def test_clarification_node_formats_questions_from_planner(self):
        """Test clarification node formats planner questions."""
        from vivek.core.graph_nodes import clarification_node

        state = {
            "clarification_from": "planner",
            "clarification_questions": [
                {
                    "question": "Which framework?",
                    "type": "choice",
                    "options": ["pytest", "unittest"],
                    "context": "For testing"
                }
            ]
        }

        result = clarification_node(state)

        assert result["needs_clarification"] is True
        assert result["status"] == "paused"
        assert "clarification_output" in result
        assert "Which framework?" in result["clarification_output"]
        assert "pytest" in result["clarification_output"]
        assert "unittest" in result["clarification_output"]

    def test_clarification_node_formats_questions_from_executor(self):
        """Test clarification node formats executor questions."""
        from vivek.core.graph_nodes import clarification_node

        state = {
            "clarification_from": "executor_coder",
            "clarification_questions": [
                {
                    "question": "Which file to modify?",
                    "type": "choice",
                    "options": ["src/auth.py", "utils/auth.py"]
                }
            ]
        }

        result = clarification_node(state)

        assert result["needs_clarification"] is True
        assert "executor_coder" in result.get("clarification_output", "") or result.get("resume_node") == "executor_coder"
        assert "Which file to modify?" in result["clarification_output"]

    def test_clarification_node_includes_resume_info(self):
        """Test clarification node includes info for resuming."""
        from vivek.core.graph_nodes import clarification_node

        state = {
            "clarification_from": "planner",
            "clarification_questions": [{"question": "test?", "type": "text"}]
        }

        result = clarification_node(state)

        # Should include resume_node for orchestrator to know where to continue
        assert "resume_node" in result or result.get("clarification_from") == "planner"


class TestPauseResume:
    """Test pause and resume functionality with thread_id."""

    @pytest.fixture
    def mock_provider(self):
        provider = Mock()
        provider.generate = Mock()
        return provider

    @pytest.fixture
    def orchestrator(self, mock_provider, tmp_path):
        checkpoint_db = str(tmp_path / "test_pause_resume.db")
        with patch('vivek.core.langgraph_orchestrator.OllamaProvider') as mock_ollama:
            mock_ollama.return_value = mock_provider
            return LangGraphVivekOrchestrator(
                project_root=str(tmp_path),
                planner_model="test-model",
                executor_model="test-model"
            )

    @pytest.mark.asyncio
    async def test_orchestrator_pauses_and_resumes_with_thread_id(self, orchestrator, mock_provider):
        """Test orchestrator can pause for clarification and resume."""
        thread_id = "test_pause_resume_1"

        # First call: planner needs clarification
        mock_provider.generate.return_value = json.dumps({
            "needs_clarification": True,
            "questions": [{"question": "Which language?", "type": "choice", "options": ["Python", "JavaScript"]}],
            "partial_plan": {"description": "create app", "mode": "coder"}
        })

        # First invocation - should pause
        result1 = await orchestrator.process_request(
            user_input="create an app",
            thread_id=thread_id
        )

        assert result1["status"] == "awaiting_clarification"
        assert result1["thread_id"] == thread_id

        # Mock planner response after getting answer
        mock_provider.generate.return_value = json.dumps({
            "description": "create Python app",
            "mode": "coder",
            "work_items": [{"mode": "coder", "file_path": "app.py", "file_status": "new", "description": "create app", "dependencies": []}],
            "priority": "normal"
        })

        # Resume with answers
        answers = {"1": "Python"}
        result2 = await orchestrator.resume_with_answers(thread_id, answers)

        # Should continue execution
        assert "status" in result2
        # State should be updated with answers

    @pytest.mark.asyncio
    async def test_resume_uses_same_checkpoint(self, orchestrator, mock_provider):
        """Test resume loads state from same checkpoint."""
        thread_id = "test_checkpoint_resume"

        # Setup: pause for clarification
        mock_provider.generate.return_value = json.dumps({
            "needs_clarification": True,
            "questions": [{"question": "test?", "type": "text"}],
            "partial_plan": {"mode": "coder"}
        })

        await orchestrator.process_request("test", thread_id)

        # Resume should load checkpoint with same thread_id
        mock_provider.generate.return_value = json.dumps({
            "description": "test",
            "mode": "coder",
            "work_items": [],
            "priority": "normal"
        })

        result = await orchestrator.resume_with_answers(thread_id, {"1": "answer"})

        # Should have context from original request
        assert result is not None
