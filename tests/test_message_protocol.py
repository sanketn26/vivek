"""Tests for message protocol."""

import pytest
from vivek.core.message_protocol import (
    MessageType,
    execution_complete,
    clarification_needed,
    error_occurred,
    partial_result,
)


class TestMessageProtocol:
    """Test standardized message protocol."""

    def test_execution_complete_basic(self):
        """Test basic execution complete message."""
        msg = execution_complete(
            output="task completed",
            from_node="planner"
        )

        assert msg["type"] == MessageType.EXECUTION_COMPLETE.value
        assert msg["payload"]["output"] == "task completed"
        assert msg["from_node"] == "planner"
        assert msg["metadata"] == {}

    def test_execution_complete_with_metadata(self):
        """Test execution complete with metadata."""
        msg = execution_complete(
            output={"code": "print('hello')"},
            from_node="executor_coder",
            files_modified=["src/main.py"],
            tests_run=5,
            tests_passed=4
        )

        assert msg["type"] == MessageType.EXECUTION_COMPLETE.value
        assert msg["payload"]["output"]["code"] == "print('hello')"
        assert msg["from_node"] == "executor_coder"
        assert msg["metadata"]["files_modified"] == ["src/main.py"]
        assert msg["metadata"]["tests_run"] == 5
        assert msg["metadata"]["tests_passed"] == 4

    def test_clarification_needed_basic(self):
        """Test basic clarification needed message."""
        questions = [
            {
                "id": "q1",
                "question": "Which file to modify?",
                "type": "choice",
                "options": ["file_a.py", "file_b.py"]
            }
        ]

        msg = clarification_needed(
            questions=questions,
            from_node="executor_coder"
        )

        assert msg["type"] == MessageType.CLARIFICATION_NEEDED.value
        assert msg["payload"]["questions"] == questions
        assert msg["from_node"] == "executor_coder"
        assert msg["metadata"] == {}

    def test_clarification_needed_with_context(self):
        """Test clarification with partial work context."""
        questions = [
            {
                "question": "Authentication method?",
                "type": "choice",
                "options": ["JWT", "OAuth2", "Session"]
            }
        ]

        msg = clarification_needed(
            questions=questions,
            from_node="executor_coder",
            partial_work="implemented skeleton",
            analysis="found 3 auth patterns in codebase"
        )

        assert msg["type"] == MessageType.CLARIFICATION_NEEDED.value
        assert msg["payload"]["questions"] == questions
        assert msg["metadata"]["partial_work"] == "implemented skeleton"
        assert msg["metadata"]["analysis"] == "found 3 auth patterns in codebase"

    def test_error_occurred_basic(self):
        """Test basic error message."""
        msg = error_occurred(
            error="File not found: src/main.py",
            from_node="executor_coder"
        )

        assert msg["type"] == MessageType.ERROR.value
        assert msg["payload"]["error"] == "File not found: src/main.py"
        assert msg["from_node"] == "executor_coder"

    def test_error_occurred_with_context(self):
        """Test error with stack trace and context."""
        msg = error_occurred(
            error="JSON parse error",
            from_node="planner",
            stack_trace="...",
            task_plan={"mode": "coder"}
        )

        assert msg["type"] == MessageType.ERROR.value
        assert msg["payload"]["error"] == "JSON parse error"
        assert msg["metadata"]["stack_trace"] == "..."
        assert msg["metadata"]["task_plan"]["mode"] == "coder"

    def test_partial_result_basic(self):
        """Test partial result message."""
        msg = partial_result(
            output="step 1 complete",
            from_node="executor_coder",
            progress=0.33
        )

        assert msg["type"] == MessageType.PARTIAL_RESULT.value
        assert msg["payload"]["output"] == "step 1 complete"
        assert msg["payload"]["progress"] == 0.33
        assert msg["from_node"] == "executor_coder"

    def test_partial_result_with_metadata(self):
        """Test partial result with step info."""
        msg = partial_result(
            output="tests written",
            from_node="executor_coder",
            progress=0.5,
            current_step="write_tests",
            completed_steps=["analyze", "design", "write_tests"]
        )

        assert msg["type"] == MessageType.PARTIAL_RESULT.value
        assert msg["payload"]["output"] == "tests written"
        assert msg["payload"]["progress"] == 0.5
        assert msg["metadata"]["current_step"] == "write_tests"
        assert len(msg["metadata"]["completed_steps"]) == 3

    def test_message_types_enum(self):
        """Test all message types are defined."""
        assert MessageType.EXECUTION_COMPLETE.value == "execution_complete"
        assert MessageType.CLARIFICATION_NEEDED.value == "clarification_needed"
        assert MessageType.ERROR.value == "error"
        assert MessageType.PARTIAL_RESULT.value == "partial_result"
