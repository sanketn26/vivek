"""Tests for graph routing functions."""

import pytest
from vivek.core.graph_state import VivekState


class TestRoutingFunctions:
    """Test conditional routing functions for LangGraph."""

    def test_route_planner_to_executor_on_success(self):
        """Test route_planner returns 'executor' when no clarification needed."""
        from vivek.core.graph_nodes import route_planner

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "needs_clarification": False,
            "task_plan": {"mode": "coder"}
        }

        next_node = route_planner(state)
        assert next_node == "executor"

    def test_route_planner_to_clarification_when_needed(self):
        """Test route_planner returns 'clarification' when clarification needed."""
        from vivek.core.graph_nodes import route_planner

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "needs_clarification": True,
            "clarification_from": "planner",
            "clarification_questions": [{"question": "test?"}]
        }

        next_node = route_planner(state)
        assert next_node == "clarification"

    def test_route_executor_to_reviewer_on_success(self):
        """Test route_executor returns 'reviewer' when no clarification needed."""
        from vivek.core.graph_nodes import route_executor

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "task_plan": {"mode": "coder"},
            "executor_output": "test output",
            "needs_clarification": False
        }

        next_node = route_executor(state)
        assert next_node == "reviewer"

    def test_route_executor_to_clarification_when_needed(self):
        """Test route_executor returns 'clarification' when clarification needed."""
        from vivek.core.graph_nodes import route_executor

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "task_plan": {"mode": "coder"},
            "needs_clarification": True,
            "clarification_from": "executor_coder"
        }

        next_node = route_executor(state)
        assert next_node == "clarification"

    def test_route_reviewer_to_clarification_when_needed(self):
        """Test route_reviewer returns 'clarification' when clarification needed."""
        from vivek.core.graph_nodes import route_reviewer

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "task_plan": {"mode": "coder"},
            "executor_output": "output",
            "review_result": {"quality_score": 0.8},
            "needs_clarification": True,
            "clarification_from": "reviewer"
        }

        next_node = route_reviewer(state)
        assert next_node == "clarification"

    def test_route_reviewer_to_executor_when_iteration_needed(self):
        """Test route_reviewer returns 'executor' when needs_iteration=true."""
        from vivek.core.graph_nodes import route_reviewer

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "task_plan": {"mode": "coder"},
            "executor_output": "output",
            "review_result": {
                "quality_score": 0.5,
                "needs_iteration": True
            },
            "needs_clarification": False,
            "iteration_count": 1
        }

        next_node = route_reviewer(state)
        assert next_node == "executor"

    def test_route_reviewer_to_format_when_complete(self):
        """Test route_reviewer returns 'format_response' when done."""
        from vivek.core.graph_nodes import route_reviewer

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "task_plan": {"mode": "coder"},
            "executor_output": "output",
            "review_result": {
                "quality_score": 0.9,
                "needs_iteration": False
            },
            "needs_clarification": False
        }

        next_node = route_reviewer(state)
        assert next_node == "format_response"

    def test_route_reviewer_to_format_when_max_iterations_reached(self):
        """Test route_reviewer stops iterating at max iterations."""
        from vivek.core.graph_nodes import route_reviewer

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "task_plan": {"mode": "coder"},
            "executor_output": "output",
            "review_result": {
                "quality_score": 0.5,
                "needs_iteration": True
            },
            "needs_clarification": False,
            "iteration_count": 3  # Max iterations
        }

        next_node = route_reviewer(state)
        # Should stop iterating and format response
        assert next_node == "format_response"


class TestClarificationNode:
    """Test clarification node formatting."""

    def test_clarification_node_formats_single_question(self):
        """Test clarification node formats a single question."""
        from vivek.core.graph_nodes import clarification_node

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "clarification_from": "planner",
            "clarification_questions": [
                {
                    "question": "Which framework to use?",
                    "type": "choice",
                    "options": ["pytest", "unittest"]
                }
            ]
        }

        result = clarification_node(state)

        assert result["needs_clarification"] is True
        assert result["status"] == "paused"
        assert "clarification_output" in result
        output = result["clarification_output"]
        assert "Which framework to use?" in output
        assert "pytest" in output
        assert "unittest" in output

    def test_clarification_node_formats_multiple_questions(self):
        """Test clarification node formats multiple questions."""
        from vivek.core.graph_nodes import clarification_node

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "clarification_from": "executor_coder",
            "clarification_questions": [
                {"question": "Question 1?", "type": "text"},
                {"question": "Question 2?", "type": "choice", "options": ["A", "B"]}
            ]
        }

        result = clarification_node(state)

        output = result["clarification_output"]
        assert "Question 1?" in output
        assert "Question 2?" in output
        assert "A" in output
        assert "B" in output

    def test_clarification_node_includes_context_when_provided(self):
        """Test clarification node includes question context."""
        from vivek.core.graph_nodes import clarification_node

        state: VivekState = {
            "user_input": "test",
            "context": {},
            "clarification_from": "planner",
            "clarification_questions": [
                {
                    "question": "Which one?",
                    "type": "choice",
                    "options": ["A", "B"],
                    "context": "Based on your project structure"
                }
            ]
        }

        result = clarification_node(state)

        output = result["clarification_output"]
        assert "Based on your project structure" in output

    def test_clarification_node_preserves_state_for_resume(self):
        """Test clarification node preserves info needed for resume."""
        from vivek.core.graph_nodes import clarification_node

        state: VivekState = {
            "user_input": "test input",
            "context": {"project": "test"},
            "task_plan": {"mode": "coder"},
            "clarification_from": "executor_coder",
            "clarification_questions": [{"question": "test?"}]
        }

        result = clarification_node(state)

        # Should keep needs_clarification flag for routing
        assert result["needs_clarification"] is True
        # Should indicate it's paused
        assert result["status"] == "paused"
