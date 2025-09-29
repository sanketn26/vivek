"""
Tests for LLM model functionality in Vivek project.
"""
import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from vivek.llm.models import (
    LLMProvider, OllamaProvider, PlannerModel, ExecutorModel
)


class TestLLMProvider:
    """Test cases for the base LLMProvider class."""

    def test_llm_provider_is_abstract(self):
        """Test that LLMProvider is properly abstract."""
        with pytest.raises(TypeError):
            LLMProvider()  # Should raise TypeError since it's abstract

    def test_llm_provider_generate_method(self):
        """Test that LLMProvider defines generate method."""
        # Check that the abstract method exists
        assert hasattr(LLMProvider, 'generate')
        assert callable(getattr(LLMProvider, 'generate'))


class TestOllamaProvider:
    """Test cases for OllamaProvider class."""

    def test_ollama_provider_initialization(self):
        """Test OllamaProvider is properly initialized."""
        model_name = "qwen2.5-coder:7b"
        provider = OllamaProvider(model_name)

        assert provider.model_name == model_name

    def test_ollama_provider_generate_success(self, mock_ollama_dependency):
        """Test successful generation with OllamaProvider."""
        provider = OllamaProvider("test-model")

        with patch('ollama.generate') as mock_generate:
            mock_generate.return_value = {"response": "Generated response"}

            response = provider.generate("Test prompt")

            assert response == "Generated response"
            mock_generate.assert_called_once()

            # Check that the call was made with correct parameters
            call_args = mock_generate.call_args
            assert call_args[1]['model'] == "test-model"
            assert call_args[1]['prompt'] == "Test prompt"
            assert 'options' in call_args[1]

    def test_ollama_provider_generate_with_options(self, mock_ollama_dependency):
        """Test generation with custom options."""
        provider = OllamaProvider("test-model")

        with patch('ollama.generate') as mock_generate:
            mock_generate.return_value = {"response": "Response with options"}

            response = provider.generate(
                "Test prompt",
                temperature=0.5,
                top_p=0.8,
                max_tokens=1000
            )

            assert response == "Response with options"

            # Check that options were passed correctly
            call_args = mock_generate.call_args
            options = call_args[1]['options']
            assert options['temperature'] == 0.5
            assert options['top_p'] == 0.8
            assert options['num_predict'] == 1000

    def test_ollama_provider_generate_error(self, mock_ollama_dependency):
        """Test error handling in OllamaProvider."""
        provider = OllamaProvider("test-model")

        with patch('ollama.generate') as mock_generate:
            mock_generate.side_effect = Exception("Connection failed")

            response = provider.generate("Test prompt")

            assert "Error generating response" in response
            assert "Connection failed" in response

    def test_ollama_provider_generate_ollama_error(self, mock_ollama_dependency):
        """Test handling of Ollama-specific errors."""
        provider = OllamaProvider("test-model")

        with patch('ollama.generate') as mock_generate:
            # Simulate Ollama returning an error response
            mock_generate.return_value = {"error": "Model not found"}

            response = provider.generate("Test prompt")

            # Should still work and return the error message
            assert "Model not found" in response


class TestPlannerModel:
    """Test cases for PlannerModel class."""

    def test_planner_model_initialization(self, mock_ollama_provider):
        """Test PlannerModel is properly initialized."""
        planner = PlannerModel(mock_ollama_provider)

        assert planner.provider == mock_ollama_provider
        assert "Planning Brain" in planner.system_prompt
        assert "peer|architect|sdet|coder" in planner.system_prompt

    def test_analyze_request_success(self, planner_model, sample_task_plan):
        """Test successful request analysis."""
        user_input = "Create comprehensive unit tests"
        context = '{"project_summary": "Test project", "current_mode": "peer"}'

        # Mock the provider response
        planner_model.provider.generate.return_value = json.dumps({
            "description": "Create unit tests for the project",
            "mode": "sdet",
            "steps": ["Analyze code", "Write tests", "Run tests"],
            "relevant_files": ["test_file.py"],
            "priority": "high"
        })

        result = planner_model.analyze_request(user_input, context)

        assert result["description"] == "Create unit tests for the project"
        assert result["mode"] == "sdet"
        assert result["steps"] == ["Analyze code", "Write tests", "Run tests"]
        assert result["relevant_files"] == ["test_file.py"]
        assert result["priority"] == "high"

    def test_analyze_request_fallback_on_error(self, planner_model):
        """Test fallback behavior when JSON parsing fails."""
        user_input = "Test request"
        context = "Test context"

        # Mock provider to return invalid JSON
        planner_model.provider.generate.return_value = "Invalid JSON response"

        result = planner_model.analyze_request(user_input, context)

        # Should return fallback values
        assert result["description"] == "Code implementation task"
        assert result["mode"] == "coder"
        assert result["steps"] == ["Implement the requested functionality"]
        assert result["relevant_files"] == []
        assert result["priority"] == "normal"

    def test_analyze_request_partial_json(self, planner_model):
        """Test handling of partial JSON responses."""
        user_input = "Test request"
        context = "Test context"

        # Mock provider to return response with some JSON
        planner_model.provider.generate.return_value = """
        Here's some text before JSON
        {
            "description": "Partial test",
            "mode": "coder"
        }
        And some text after
        """

        result = planner_model.analyze_request(user_input, context)

        # Should extract the valid JSON part
        assert result["description"] == "Partial test"
        assert result["mode"] == "coder"
        assert result["steps"] == ["Implement the requested functionality"]  # fallback

    def test_review_output_success(self, planner_model):
        """Test successful output review."""
        task_description = "Create unit tests"
        executor_output = "Created comprehensive test suite"

        # Mock provider response
        planner_model.provider.generate.return_value = json.dumps({
            "quality_score": 0.9,
            "needs_iteration": False,
            "feedback": "Excellent test coverage",
            "suggestions": ["Add integration tests", "Include edge cases"]
        })

        result = planner_model.review_output(task_description, executor_output)

        assert result["quality_score"] == 0.9
        assert result["needs_iteration"] is False
        assert result["feedback"] == "Excellent test coverage"
        assert len(result["suggestions"]) == 2

    def test_review_output_fallback_on_error(self, planner_model):
        """Test fallback behavior when review parsing fails."""
        task_description = "Test task"
        executor_output = "Test output"

        # Mock provider to return invalid JSON
        planner_model.provider.generate.return_value = "Invalid review response"

        result = planner_model.review_output(task_description, executor_output)

        # Should return fallback values
        assert result["quality_score"] == 0.7
        assert result["needs_iteration"] is False
        assert result["feedback"] == "Review completed"
        assert result["suggestions"] == []

    def test_review_output_with_iteration_needed(self, planner_model):
        """Test review output that requires iteration."""
        task_description = "Implement feature"
        executor_output = "Basic implementation"

        planner_model.provider.generate.return_value = json.dumps({
            "quality_score": 0.4,
            "needs_iteration": True,
            "feedback": "Needs significant improvement",
            "suggestions": ["Add error handling", "Improve performance", "Add tests"]
        })

        result = planner_model.review_output(task_description, executor_output)

        assert result["quality_score"] == 0.4
        assert result["needs_iteration"] is True
        assert len(result["suggestions"]) == 3


class TestExecutorModel:
    """Test cases for ExecutorModel class."""

    def test_executor_model_initialization(self, mock_ollama_provider):
        """Test ExecutorModel is properly initialized."""
        executor = ExecutorModel(mock_ollama_provider)

        assert executor.provider == mock_ollama_provider
        assert "mode_prompts" in dir(executor)
        assert len(executor.mode_prompts) == 4  # Should have 4 modes

        # Check that all required modes are present
        expected_modes = ["peer", "architect", "sdet", "coder"]
        for mode in expected_modes:
            assert mode in executor.mode_prompts

    def test_mode_prompts_content(self, mock_ollama_provider):
        """Test that mode prompts contain appropriate content."""
        executor = ExecutorModel(mock_ollama_provider)

        # Check that each mode has appropriate keywords
        assert "collaborative" in executor.mode_prompts["peer"]
        assert "design patterns" in executor.mode_prompts["architect"]
        assert "testing strategies" in executor.mode_prompts["sdet"]
        assert "clean, efficient implementation" in executor.mode_prompts["coder"]

    def test_execute_task_success(self, executor_model, sample_task_plan):
        """Test successful task execution."""
        context = '{"project_summary": "Test project"}'

        # Mock provider response
        executor_model.provider.generate.return_value = "Successfully implemented the requested feature"

        result = executor_model.execute_task(sample_task_plan, context)

        assert "Successfully implemented" in result

        # Verify the provider was called with correct prompt structure
        call_args = executor_model.provider.generate.call_args
        prompt = call_args[0][0]  # First positional argument

        assert sample_task_plan["description"] in prompt
        assert sample_task_plan["mode"] in prompt
        assert context in prompt
        assert "Steps to complete:" in prompt

    def test_execute_task_different_modes(self, executor_model):
        """Test task execution in different modes."""
        context = "Test context"

        # Test each mode
        for mode in ["peer", "architect", "sdet", "coder"]:
            task_plan = {
                "description": f"Test {mode} task",
                "mode": mode,
                "steps": [f"Step for {mode}"],
                "relevant_files": [],
                "priority": "normal"
            }

            executor_model.provider.generate.return_value = f"{mode} mode response"

            result = executor_model.execute_task(task_plan, context)

            # Verify correct mode instruction was used
            call_args = executor_model.provider.generate.call_args
            prompt = call_args[0][0]
            assert mode in prompt

    def test_execute_task_fallback_mode(self, executor_model):
        """Test task execution with unknown mode falls back to coder."""
        context = "Test context"
        task_plan = {
            "description": "Test task",
            "mode": "unknown_mode",  # Invalid mode
            "steps": ["Step"],
            "relevant_files": [],
            "priority": "normal"
        }

        executor_model.provider.generate.return_value = "Coder mode response"

        result = executor_model.execute_task(task_plan, context)

        # Should still work and use coder mode as fallback
        assert result == "Coder mode response"

        # Verify coder mode instruction was used
        call_args = executor_model.provider.generate.call_args
        prompt = call_args[0][0]
        assert "clean, efficient implementation" in prompt

    def test_execute_task_with_temperature(self, executor_model, sample_task_plan):
        """Test that appropriate temperature is used for task execution."""
        context = "Test context"

        executor_model.provider.generate.return_value = "Response with temperature"

        result = executor_model.execute_task(sample_task_plan, context)

        # Check that temperature was set to 0.2 (creative but focused)
        call_args = executor_model.provider.generate.call_args
        kwargs = call_args[1]
        assert kwargs.get("temperature") == 0.2


class TestIntegration:
    """Integration tests for LLM models."""

    def test_planner_executor_integration(self, mock_ollama_provider):
        """Test integration between Planner and Executor models."""
        planner = PlannerModel(mock_ollama_provider)
        executor = ExecutorModel(mock_ollama_provider)

        # Mock responses
        planner.provider.generate.return_value = json.dumps({
            "description": "Integration test",
            "mode": "coder",
            "steps": ["Step 1", "Step 2"],
            "relevant_files": ["test.py"],
            "priority": "normal"
        })

        executor.provider.generate.return_value = "Implementation complete"

        # Test the workflow
        user_input = "Test integration"
        context = "Test context"

        task_plan = planner.analyze_request(user_input, context)
        result = executor.execute_task(task_plan, context)

        assert result == "Implementation complete"
        assert task_plan["mode"] == "coder"

    def test_error_handling_integration(self, mock_ollama_provider):
        """Test error handling across model integration."""
        planner = PlannerModel(mock_ollama_provider)
        executor = ExecutorModel(mock_ollama_provider)

        # Mock error responses
        planner.provider.generate.return_value = "Invalid JSON"
        executor.provider.generate.return_value = "Error in execution"

        # Should handle errors gracefully
        task_plan = planner.analyze_request("Test", "Context")
        result = executor.execute_task(task_plan, "Context")

        assert result == "Error in execution"
        # Should fallback to coder mode
        assert task_plan["mode"] == "coder"

    def test_provider_error_propagation(self, mock_ollama_provider):
        """Test that provider errors are properly handled."""
        provider = OllamaProvider("test-model")

        # Test with connection error
        with patch('ollama.generate') as mock_generate:
            mock_generate.side_effect = Exception("Network error")

            response = provider.generate("Test prompt")
            assert "Error generating response" in response
            assert "Network error" in response

    def test_json_parsing_edge_cases(self, mock_ollama_provider):
        """Test JSON parsing with various edge cases."""
        planner = PlannerModel(mock_ollama_provider)

        edge_cases = [
            "",  # Empty string
            "No JSON here",  # No JSON
            "{invalid json}",  # Invalid JSON
            '{"valid": "json",}',  # Trailing comma (invalid)
            "Text { \"valid\": \"json\" } more text",  # JSON in middle
        ]

        for case in edge_cases:
            planner.provider.generate.return_value = case

            # Should not raise exception, should use fallbacks
            result = planner.analyze_request("Test", "Context")

            # Should have valid fallback structure
            assert "description" in result
            assert "mode" in result
            assert "steps" in result
            assert "relevant_files" in result
            assert "priority" in result

    def test_model_initialization_with_different_providers(self):
        """Test model initialization with different provider types."""
        # This would test if we had multiple provider types
        # For now, just test that initialization works
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = "Mock response"

        planner = PlannerModel(mock_provider)
        executor = ExecutorModel(mock_provider)

        assert planner.provider == mock_provider
        assert executor.provider == mock_provider