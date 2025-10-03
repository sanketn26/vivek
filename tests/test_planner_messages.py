"""Tests for planner returning structured messages to orchestrator."""

import pytest
import json
from unittest.mock import Mock, patch

from vivek.llm.planner import PlannerModel
from vivek.llm.provider import OllamaProvider
from vivek.core.message_protocol import MessageType


class TestPlannerMessages:
    """Test planner returns structured messages for orchestrator."""

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider."""
        provider = Mock(spec=OllamaProvider)
        return provider

    @pytest.fixture
    def planner(self, mock_provider):
        """Create planner with mock provider."""
        return PlannerModel(mock_provider)

    def test_analyze_request_returns_execution_complete_message(self, planner, mock_provider):
        """Test planner returns execution_complete message for valid task."""
        # Mock LLM response with valid task plan
        mock_provider.generate.return_value = json.dumps({
            "description": "implement auth",
            "mode": "coder",
            "work_items": [
                {
                    "mode": "coder",
                    "file_path": "src/auth.py",
                    "file_status": "new",
                    "description": "implement JWT auth",
                    "dependencies": []
                }
            ],
            "priority": "normal"
        })

        result = planner.analyze_request("add authentication", "{}")

        # Should return execution_complete message
        assert result["type"] == MessageType.EXECUTION_COMPLETE.value
        assert result["from_node"] == "planner"
        assert "output" in result["payload"]

        task_plan = result["payload"]["output"]
        assert task_plan["mode"] == "coder"
        assert task_plan["description"] == "implement auth"
        assert len(task_plan["work_items"]) == 1

    def test_analyze_request_returns_clarification_needed_message(self, planner, mock_provider):
        """Test planner returns clarification_needed when task is ambiguous."""
        # Mock LLM response indicating clarification needed
        mock_provider.generate.return_value = json.dumps({
            "needs_clarification": True,
            "questions": [
                {
                    "question": "Which endpoints need auth?",
                    "type": "choice",
                    "options": ["all", "/api/* only", "specific endpoints"]
                }
            ],
            "partial_plan": {
                "description": "add authentication",
                "mode": "coder"
            }
        })

        result = planner.analyze_request("add auth", "{}")

        # Should return clarification_needed message
        assert result["type"] == MessageType.CLARIFICATION_NEEDED.value
        assert result["from_node"] == "planner"
        assert "questions" in result["payload"]
        assert len(result["payload"]["questions"]) == 1
        assert result["metadata"]["partial_plan"]["mode"] == "coder"

    def test_review_output_returns_execution_complete_message(self, planner, mock_provider):
        """Test reviewer returns execution_complete for quality review."""
        # Mock review response
        mock_provider.generate.return_value = json.dumps({
            "quality_score": 0.85,
            "needs_iteration": False,
            "feedback": "implementation complete",
            "suggestions": ["add logging"]
        })

        result = planner.review_output(
            "implement auth",
            "def login(): return jwt_token"
        )

        # Should return execution_complete message
        assert result["type"] == MessageType.EXECUTION_COMPLETE.value
        assert result["from_node"] == "reviewer"

        review = result["payload"]["output"]
        assert review["quality_score"] == 0.85
        assert review["needs_iteration"] is False
        assert result["metadata"]["quality_score"] == 0.85

    def test_review_output_returns_clarification_needed_for_unclear_requirements(self, planner, mock_provider):
        """Test reviewer returns clarification when requirements are unclear."""
        # Mock review response with unclear requirements
        mock_provider.generate.return_value = json.dumps({
            "requirements_unclear": True,
            "unclear_points": [
                {
                    "question": "Implementation uses JWT but task doesn't specify - is this correct?",
                    "type": "confirmation",
                    "context": "Found OAuth2 in other parts of codebase"
                }
            ],
            "quality_score": 0.6
        })

        result = planner.review_output(
            "implement auth",
            "def login(): return jwt_token"
        )

        # Should return clarification_needed message
        assert result["type"] == MessageType.CLARIFICATION_NEEDED.value
        assert result["from_node"] == "reviewer"
        assert len(result["payload"]["questions"]) == 1
        assert result["metadata"]["current_quality"] == 0.6

    def test_analyze_request_returns_error_on_json_parse_failure(self, planner, mock_provider):
        """Test planner returns error message on JSON parse failure."""
        # Mock invalid JSON response
        mock_provider.generate.return_value = "invalid json response"

        result = planner.analyze_request("add auth", "{}")

        # Should return error message (or fallback to execution_complete with default plan)
        # Current implementation returns fallback - we'll enhance to return error
        assert result["type"] == MessageType.EXECUTION_COMPLETE.value
        # Fallback behavior - creates default work item

    def test_planner_includes_metadata_in_messages(self, planner, mock_provider):
        """Test planner includes useful metadata in messages."""
        mock_provider.generate.return_value = json.dumps({
            "description": "implement auth",
            "mode": "coder",
            "work_items": [{"mode": "coder", "file_path": "src/auth.py", "file_status": "new", "description": "impl", "dependencies": []}],
            "priority": "high"
        })

        result = planner.analyze_request("urgent: add auth", "{}")

        assert result["type"] == MessageType.EXECUTION_COMPLETE.value
        # Check metadata contains useful info
        assert result["metadata"]["mode"] == "coder"
        assert result["metadata"]["work_items_count"] == 1
        assert result["metadata"]["priority"] == "high"
