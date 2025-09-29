"""
Tests for the core orchestrator functionality in Vivek project.
"""
import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path

from vivek.core.orchestrator import (
    VivekOrchestrator, SessionContext, TaskPlan, ReviewResult
)


class TestSessionContext:
    """Test cases for SessionContext class."""

    def test_session_context_initialization(self, project_root):
        """Test SessionContext is properly initialized."""
        context = SessionContext(str(project_root))

        assert context.project_root == project_root
        assert context.current_mode == "peer"
        assert context.search_enabled is True
        assert context.condensed_history == []
        assert context.project_summary == ""
        assert context.working_files == {}
        assert context.key_decisions == []

    def test_add_interaction(self, session_context, sample_task_plan, sample_review_result):
        """Test adding an interaction to session context."""
        user_input = "Create unit tests for the project"
        task_plan = TaskPlan(**sample_task_plan)
        review = ReviewResult(**sample_review_result)
        executor_output = "Created comprehensive unit tests"

        session_context.add_interaction(user_input, task_plan, executor_output, review)

        # Check that interaction was added
        assert len(session_context.condensed_history) == 1

        interaction = session_context.condensed_history[0]
        assert "timestamp" in interaction
        assert interaction["mode"] == "sdet"
        assert interaction["quality"] == 0.85
        assert len(interaction["files_touched"]) == 2

    def test_add_multiple_interactions_history_limit(self, session_context, sample_task_plan, sample_review_result):
        """Test that history is limited to last 10 interactions."""
        user_input = "Create unit tests"
        task_plan = TaskPlan(**sample_task_plan)
        review = ReviewResult(**sample_review_result)
        executor_output = "Created tests"

        # Add 15 interactions
        for i in range(15):
            session_context.add_interaction(f"{user_input} {i}", task_plan, executor_output, review)

        # Should only keep last 10
        assert len(session_context.condensed_history) == 10

    def test_get_relevant_context(self, session_context, sample_task_plan, sample_review_result):
        """Test getting relevant context for interactions."""
        # Add some interactions first
        user_input = "Create unit tests"
        task_plan = TaskPlan(**sample_task_plan)
        review = ReviewResult(**sample_review_result)
        executor_output = "Created tests"

        session_context.add_interaction(user_input, task_plan, executor_output, review)

        context = session_context.get_relevant_context(max_tokens=1000)

        # Parse context as JSON to verify structure
        context_data = json.loads(context)
        assert "project_summary" in context_data
        assert "current_mode" in context_data
        assert "recent_decisions" in context_data
        assert "working_files" in context_data
        assert "recent_history" in context_data

    def test_context_truncation(self, session_context):
        """Test that context is properly truncated when too long."""
        # Create a session context with many interactions
        for i in range(5):
            task_plan = TaskPlan(
                description=f"Task {i}",
                mode="coder",
                steps=[f"Step {i}"],
                relevant_files=[f"file{i}.py"]
            )
            review = ReviewResult(
                quality_score=0.8,
                needs_iteration=False,
                feedback=f"Feedback {i}",
                suggestions=[f"Suggestion {i}"]
            )
            session_context.add_interaction(f"Input {i}", task_plan, f"Output {i}", review)

        # Test with very low token limit to force truncation
        context = session_context.get_relevant_context(max_tokens=10)

        # Should still be valid JSON
        context_data = json.loads(context)
        assert isinstance(context_data, dict)

    def test_extract_intent(self, session_context):
        """Test intent extraction from user input."""
        # Test different types of inputs
        test_cases = [
            ("Create unit tests for the project", "testing"),
            ("Design the system architecture", "architecture"),
            ("Implement user authentication feature", "implementation"),
            ("Review the code quality", "review"),
            ("Some random input without keywords", "general")
        ]

        for user_input, expected_intent in test_cases:
            intent = session_context._extract_intent(user_input)
            assert intent == expected_intent

    def test_extract_changes(self, session_context):
        """Test extracting key changes from executor output."""
        test_cases = [
            ("Added new function to handle user input", ["Added new function to handle user input"]),
            ("Modified existing class and updated tests", ["Modified existing class and updated tests"]),
            ("No changes mentioned in this output", []),
            ("Created multiple files and updated documentation", ["Created multiple files and updated documentation"])
        ]

        for output, expected_changes in test_cases:
            changes = session_context._extract_changes(output)
            assert len(changes) <= 3  # Should limit to top 3
            for expected in expected_changes:
                assert expected in changes

    def test_extract_decisions(self, session_context):
        """Test extracting key decisions from task descriptions."""
        test_cases = [
            ("Implement using factory pattern", "architectural_pattern"),
            ("Use React framework for frontend", "framework_choice"),
            ("Restructure the code organization", "code_structure"),
            ("Add basic logging to the module", "implementation_detail")
        ]

        for description, expected_decision in test_cases:
            decision = session_context._extract_decisions(description)
            assert decision == expected_decision

    def test_update_project_summary(self, session_context, sample_task_plan, sample_review_result):
        """Test project summary updates."""
        # Initially should not update with less than 3 interactions
        session_context._update_project_summary()
        assert session_context.project_summary == ""

        # Add minimum required interactions
        for i in range(3):
            task_plan = TaskPlan(**sample_task_plan)
            review = ReviewResult(**sample_review_result)
            session_context.add_interaction(f"Input {i}", task_plan, f"Output {i}", review)

        # Now summary should be updated
        assert session_context.project_summary != ""

    def test_project_summary_aggregation(self, session_context):
        """Test that project summary properly aggregates recent activity."""
        # Add interactions with different modes and intents
        interactions = [
            ("test", "testing", "sdet"),
            ("implement", "implementation", "coder"),
            ("design", "architecture", "architect"),
            ("test more", "testing", "sdet"),
            ("review", "review", "peer")
        ]

        for intent_keyword, expected_intent, mode in interactions:
            task_plan = TaskPlan(
                description=f"Task with {intent_keyword}",
                mode=mode,
                steps=["Step"],
                relevant_files=["file.py"]
            )
            review = ReviewResult(0.8, False, "Good", ["Suggestion"])
            session_context.add_interaction(f"Input with {intent_keyword}", task_plan, "Output", review)

        # Should identify testing as main focus and sdet as dominant mode
        assert "testing" in session_context.project_summary.lower()
        assert "sdet" in session_context.project_summary.lower()


class TestVivekOrchestrator:
    """Test cases for VivekOrchestrator class."""

    def test_orchestrator_initialization(self, project_root, mock_ollama_provider):
        """Test VivekOrchestrator is properly initialized."""
        with patch('vivek.core.orchestrator.OllamaProvider', return_value=mock_ollama_provider):
            orchestrator = VivekOrchestrator(
                project_root=str(project_root),
                planner_model="test-model",
                executor_model="test-model"
            )

            assert orchestrator.session_context is not None
            assert orchestrator.planner is not None
            assert orchestrator.executor is not None

    def test_orchestrator_initialization_with_defaults(self, mock_ollama_provider):
        """Test VivekOrchestrator initialization with default parameters."""
        with patch('vivek.core.orchestrator.OllamaProvider', return_value=mock_ollama_provider):
            orchestrator = VivekOrchestrator()

            assert orchestrator.session_context.project_root == Path(".")
            assert orchestrator.planner is not None
            assert orchestrator.executor is not None

    @pytest.mark.asyncio
    async def test_process_request_success(self, mock_orchestrator, sample_task_plan):
        """Test successful request processing."""
        user_input = "Create unit tests for the project"

        # Mock the planner response
        mock_orchestrator.planner.analyze_request.return_value = sample_task_plan
        mock_orchestrator.executor.execute_task.return_value = "Created comprehensive unit tests"
        mock_orchestrator.planner.review_output.return_value = {
            "quality_score": 0.85,
            "needs_iteration": False,
            "feedback": "Tests look good",
            "suggestions": ["Add more edge cases"]
        }

        response = await mock_orchestrator.process_request(user_input)

        assert "Created comprehensive unit tests" in response
        assert "SDET MODE" in response
        assert "Suggestions:" in response

    @pytest.mark.asyncio
    async def test_process_request_error_handling(self, mock_orchestrator):
        """Test error handling during request processing."""
        user_input = "Test request that will cause an error"

        # Mock an exception in the planner
        mock_orchestrator.planner.analyze_request.side_effect = Exception("Planner error")

        response = await mock_orchestrator.process_request(user_input)

        assert "Error processing request" in response
        assert "Planner error" in response

    @pytest.mark.asyncio
    async def test_process_request_with_iteration(self, mock_orchestrator, sample_task_plan):
        """Test request processing that requires iteration."""
        user_input = "Create tests"

        # Mock responses that require iteration
        mock_orchestrator.planner.analyze_request.return_value = sample_task_plan
        mock_orchestrator.executor.execute_task.return_value = "Basic tests created"
        mock_orchestrator.planner.review_output.return_value = {
            "quality_score": 0.4,  # Low quality score
            "needs_iteration": True,
            "feedback": "Needs improvement",
            "suggestions": ["Add more test cases"]
        }

        response = await mock_orchestrator.process_request(user_input)

        # Should still return the output even with low quality
        assert "Basic tests created" in response

    def test_switch_mode_valid(self, mock_orchestrator):
        """Test switching to valid modes."""
        valid_modes = ["peer", "architect", "sdet", "coder"]

        for mode in valid_modes:
            result = mock_orchestrator.switch_mode(mode)
            assert f"Switched to {mode} mode" in result
            assert mock_orchestrator.session_context.current_mode == mode

    def test_switch_mode_invalid(self, mock_orchestrator):
        """Test switching to invalid mode."""
        result = mock_orchestrator.switch_mode("invalid_mode")
        assert "Invalid mode" in result
        assert mock_orchestrator.session_context.current_mode != "invalid_mode"

    def test_get_status(self, mock_orchestrator):
        """Test getting current session status."""
        status = mock_orchestrator.get_status()

        assert "Current Status:" in status
        assert "Mode:" in status
        assert "Project:" in status
        assert "Interactions:" in status
        assert "Active files:" in status

    def test_format_response(self, mock_orchestrator, sample_review_result):
        """Test response formatting."""
        output = "Test executor output"
        review = ReviewResult(**sample_review_result)
        mode = "sdet"

        formatted = mock_orchestrator._format_response(output, review, mode)

        assert f"[{mode.upper()} MODE]" in formatted
        assert output in formatted
        assert "Suggestions:" in formatted


class TestIntegration:
    """Integration tests for orchestrator functionality."""

    @pytest.mark.asyncio
    async def test_full_request_processing_pipeline(self, project_root, mock_ollama_provider):
        """Test the complete request processing pipeline."""
        with patch('vivek.core.orchestrator.OllamaProvider', return_value=mock_ollama_provider):
            orchestrator = VivekOrchestrator(project_root=str(project_root))

            # Mock the planner and executor models to avoid actual LLM calls
            orchestrator.planner = Mock()
            orchestrator.executor = Mock()

            # Mock all the LLM calls
            orchestrator.planner.analyze_request.return_value = {
                "description": "Test task",
                "mode": "coder",
                "steps": ["Write code", "Test code"],
                "relevant_files": ["test.py"],
                "priority": "normal"
            }
            orchestrator.executor.execute_task.return_value = "Code implementation complete"
            orchestrator.planner.review_output.return_value = {
                "quality_score": 0.9,
                "needs_iteration": False,
                "feedback": "Excellent work",
                "suggestions": ["Consider adding error handling"]
            }

            response = await orchestrator.process_request("Implement a test feature")

            assert "Code implementation complete" in response
            assert "[CODER MODE]" in response

            # Check that interaction was recorded
            assert len(orchestrator.session_context.condensed_history) == 1

    def test_mode_persistence_across_requests(self, project_root, mock_ollama_provider):
        """Test that mode changes persist across requests."""
        with patch('vivek.core.orchestrator.OllamaProvider', return_value=mock_ollama_provider):
            orchestrator = VivekOrchestrator(project_root=str(project_root))

            # Switch mode
            orchestrator.switch_mode("architect")
            assert orchestrator.session_context.current_mode == "architect"

            # Mode should persist
            assert orchestrator.session_context.current_mode == "architect"

    def test_context_accumulation(self, project_root, mock_ollama_provider):
        """Test that context accumulates across multiple interactions."""
        with patch('vivek.core.orchestrator.OllamaProvider', return_value=mock_ollama_provider):
            orchestrator = VivekOrchestrator(project_root=str(project_root))

            # Mock the planner and executor models to avoid actual LLM calls
            orchestrator.planner = Mock()
            orchestrator.executor = Mock()

            # Simulate multiple interactions
            for i in range(3):
                orchestrator.planner.analyze_request.return_value = {
                    "description": f"Task {i}",
                    "mode": "coder",
                    "steps": [f"Step {i}"],
                    "relevant_files": [f"file{i}.py"],
                    "priority": "normal"
                }
                orchestrator.executor.execute_task.return_value = f"Output {i}"
                orchestrator.planner.review_output.return_value = {
                    "quality_score": 0.8,
                    "needs_iteration": False,
                    "feedback": f"Feedback {i}",
                    "suggestions": []
                }

                # Process request (using asyncio since process_request is async)
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    loop.run_until_complete(orchestrator.process_request(f"Request {i}"))
                finally:
                    loop.close()

            # Should have accumulated interactions
            assert len(orchestrator.session_context.condensed_history) == 3

            # Context should include recent history
            context = orchestrator.session_context.get_relevant_context()
            context_data = json.loads(context)
            assert "recent_history" in context_data
            assert len(context_data["recent_history"]) == 3