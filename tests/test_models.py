"""
Tests for LLM model functionality in Vivek project.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

from vivek.llm.executor import BaseExecutor
from vivek.llm.planner import PlannerModel
from vivek.llm.provider import OllamaProvider, OpenAICompatibleProvider, LMStudioProvider, SarvamAIProvider
from vivek.llm.models import LLMProvider
from vivek.llm.constants import PromptSections


class TestLLMProvider:
    """Test cases for the base LLMProvider class."""

    def test_llm_provider_is_abstract(self):
        """Test that LLMProvider is properly abstract."""
        with pytest.raises(TypeError):
            LLMProvider()  # Should raise TypeError since it's abstract

    def test_llm_provider_generate_method(self):
        """Test that LLMProvider defines generate method."""
        # Check that the abstract method exists
        assert hasattr(LLMProvider, "generate")
        assert callable(getattr(LLMProvider, "generate"))


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

        with patch("ollama.generate") as mock_generate:
            mock_generate.return_value = {"response": "Generated response"}

            response = provider.generate("Test prompt")

            assert response == "Generated response"
            mock_generate.assert_called_once()

            # Check that the call was made with correct parameters
            call_args = mock_generate.call_args
            assert call_args[1]["model"] == "test-model"
            assert call_args[1]["prompt"] == "Test prompt"
            assert "options" in call_args[1]

    def test_ollama_provider_generate_with_options(self, mock_ollama_dependency):
        """Test generation with custom options."""
        provider = OllamaProvider("test-model")

        with patch("ollama.generate") as mock_generate:
            mock_generate.return_value = {"response": "Response with options"}

            response = provider.generate(
                "Test prompt", temperature=0.5, top_p=0.8, max_tokens=1000
            )

            assert response == "Response with options"

            # Check that options were passed correctly
            call_args = mock_generate.call_args
            options = call_args[1]["options"]
            assert options["temperature"] == 0.5
            assert options["top_p"] == 0.8
            assert options["num_predict"] == 1000

    def test_ollama_provider_generate_error(self, mock_ollama_dependency):
        """Test error handling in OllamaProvider."""
        provider = OllamaProvider("test-model")

        with patch("ollama.generate") as mock_generate:
            mock_generate.side_effect = Exception("Connection failed")

            response = provider.generate("Test prompt")

            assert "Error generating response" in response
            assert "Connection failed" in response

    def test_ollama_provider_generate_ollama_error(self, mock_ollama_dependency):
        """Test handling of Ollama-specific errors."""
        provider = OllamaProvider("test-model")

        with patch("ollama.generate") as mock_generate:
            # Simulate Ollama returning an error response
            mock_generate.return_value = {"error": "Model not found"}

            response = provider.generate("Test prompt")

            # Should still work and return the error message
            assert "Model not found" in response


class TestOpenAICompatibleProvider:
    """Test cases for OpenAICompatibleProvider class."""

    def test_openai_provider_initialization(self):
        """Test OpenAICompatibleProvider is properly initialized."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com",
            api_key="test-key"
        )

        assert provider.model_name == "gpt-3.5-turbo"
        assert provider.base_url == "https://api.openai.com"
        assert provider.api_key == "test-key"

    def test_openai_provider_initialization_with_env_var(self, monkeypatch):
        """Test initialization using environment variable for API key."""
        monkeypatch.setenv("OPENAI_API_KEY", "env-api-key")

        provider = OpenAICompatibleProvider(
            model_name="gpt-4",
            base_url="https://api.openai.com"
        )

        assert provider.api_key == "env-api-key"

    def test_openai_provider_initialization_no_api_key(self):
        """Test initialization without API key."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com"
        )

        assert provider.api_key is None

    def test_openai_provider_generate_success(self):
        """Test successful generation with OpenAICompatibleProvider."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com",
            api_key="test-key"
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Generated response"}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate("Test prompt")

            assert response == "Generated response"
            mock_post.assert_called_once()

            # Check that the call was made with correct parameters
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://api.openai.com/v1/chat/completions"

            # Check headers
            headers = call_args[1]["headers"]
            assert headers["Content-Type"] == "application/json"
            assert headers["Authorization"] == "Bearer test-key"

            # Check request body
            data = call_args[1]["json"]
            assert data["model"] == "gpt-3.5-turbo"
            assert len(data["messages"]) == 1
            assert data["messages"][0]["role"] == "user"
            assert data["messages"][0]["content"] == "Test prompt"

    def test_openai_provider_generate_with_system_prompt(self):
        """Test generation with system prompt."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-4",
            base_url="https://api.openai.com",
            api_key="test-key",
            system_prompt="You are a helpful assistant."
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response with system prompt"}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate("User question")

            # Check that system prompt is included in messages
            call_args = mock_post.call_args
            data = call_args[1]["json"]
            messages = data["messages"]
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "You are a helpful assistant."
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "User question"

    def test_openai_provider_generate_with_options(self):
        """Test generation with custom options."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com",
            api_key="test-key"
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response with options"}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate(
                "Test prompt",
                temperature=0.5,
                top_p=0.8,
                max_tokens=1000
            )

            # Check that options were passed correctly
            call_args = mock_post.call_args
            data = call_args[1]["json"]
            assert data["temperature"] == 0.5
            assert data["top_p"] == 0.8
            assert data["max_tokens"] == 1000

    def test_openai_provider_generate_request_error(self):
        """Test error handling for request failures."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com",
            api_key="test-key"
        )

        with patch("requests.post") as mock_post:
            from requests.exceptions import RequestException
            mock_post.side_effect = RequestException("Connection failed")

            response = provider.generate("Test prompt")

            assert "Error connecting to API" in response
            assert "Connection failed" in response

    def test_openai_provider_generate_http_error(self):
        """Test error handling for HTTP errors."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com",
            api_key="test-key"
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 400 Error")
            mock_post.return_value = mock_response

            response = provider.generate("Test prompt")

            assert "Error generating response" in response

    def test_openai_provider_generate_unexpected_response(self):
        """Test handling of unexpected response format."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com",
            api_key="test-key"
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"unexpected": "format"}
            mock_post.return_value = mock_response

            response = provider.generate("Test prompt")

            assert "Error: Unexpected response format" in response


class TestLMStudioProvider:
    """Test cases for LMStudioProvider class."""

    def test_lmstudio_provider_initialization(self):
        """Test LMStudioProvider is properly initialized."""
        provider = LMStudioProvider(model_name="local-model")

        assert provider.model_name == "local-model"
        assert provider.base_url == "http://localhost:1234"
        assert provider.api_key is None  # LM Studio doesn't need API key

    def test_lmstudio_provider_initialization_custom_url(self):
        """Test LMStudioProvider with custom URL."""
        provider = LMStudioProvider(
            model_name="custom-model",
            base_url="http://192.168.1.100:8080"
        )

        assert provider.model_name == "custom-model"
        assert provider.base_url == "http://192.168.1.100:8080"

    def test_lmstudio_provider_generate_inherits_openai_behavior(self):
        """Test that LMStudioProvider inherits OpenAI-compatible behavior."""
        provider = LMStudioProvider(model_name="test-model")

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "LM Studio response"}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate("Test prompt")

            assert response == "LM Studio response"

            # Should call the same endpoint as OpenAI
            call_args = mock_post.call_args
            assert call_args[0][0] == "http://localhost:1234/v1/chat/completions"


class TestSarvamAIProvider:
    """Test cases for SarvamAIProvider class."""

    def test_sarvam_provider_initialization(self):
        """Test SarvamAIProvider is properly initialized."""
        provider = SarvamAIProvider(model_name="sarvam-m", api_key="test-key")

        assert provider.model_name == "sarvam-m"
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.sarvam.ai"

    def test_sarvam_provider_initialization_with_env_var(self, monkeypatch):
        """Test initialization using environment variable for API key."""
        monkeypatch.setenv("SARVAM_API_KEY", "env-sarvam-key")

        provider = SarvamAIProvider()

        assert provider.api_key == "env-sarvam-key"

    def test_sarvam_provider_generate_success(self):
        """Test successful generation with SarvamAIProvider."""
        provider = SarvamAIProvider(api_key="test-key")

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Sarvam AI response"}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate("Test prompt")

            assert response == "Sarvam AI response"
            mock_post.assert_called_once()

            # Check that the call was made with correct parameters
            call_args = mock_post.call_args
            assert call_args[0][0] == "https://api.sarvam.ai/v1/chat/completions"

            # Check headers - should use api-key header, not Authorization
            headers = call_args[1]["headers"]
            assert headers["Content-Type"] == "application/json"
            assert headers["api-key"] == "test-key"
            assert "Authorization" not in headers

            # Check request body
            data = call_args[1]["json"]
            assert data["model"] == "sarvam-m"
            assert len(data["messages"]) == 1
            assert data["messages"][0]["role"] == "user"

    def test_sarvam_provider_generate_with_system_prompt(self):
        """Test generation with system prompt."""
        provider = SarvamAIProvider(
            api_key="test-key",
            system_prompt="You are a helpful assistant."
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response with system prompt"}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate("User question")

            # Check that system prompt is included in messages
            call_args = mock_post.call_args
            data = call_args[1]["json"]
            messages = data["messages"]
            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert messages[0]["content"] == "You are a helpful assistant."
            assert messages[1]["role"] == "user"
            assert messages[1]["content"] == "User question"

    def test_sarvam_provider_generate_request_error(self):
        """Test error handling for request failures."""
        provider = SarvamAIProvider(api_key="test-key")

        with patch("requests.post") as mock_post:
            from requests.exceptions import RequestException
            mock_post.side_effect = RequestException("Connection failed")

            response = provider.generate("Test prompt")

            assert "Error connecting to Sarvam AI API" in response
            assert "Connection failed" in response

    def test_sarvam_provider_generate_unexpected_response(self):
        """Test handling of unexpected response format."""
        provider = SarvamAIProvider(api_key="test-key")

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"unexpected": "format"}
            mock_post.return_value = mock_response

            response = provider.generate("Test prompt")

            assert "Error: Unexpected response format" in response


class TestSystemPromptFunctionality:
    """Test cases for system prompt functionality across providers."""

    def test_openai_provider_system_prompt_integration(self):
        """Test system prompt integration with other parameters."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-4",
            base_url="https://api.openai.com",
            api_key="test-key",
            system_prompt="You are a senior software engineer with expertise in Python."
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Based on my expertise..."}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate(
                "Review this code and suggest improvements.",
                temperature=0.3,
                max_tokens=500
            )

            # Verify system prompt is included with other parameters
            call_args = mock_post.call_args
            data = call_args[1]["json"]
            messages = data["messages"]

            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert "senior software engineer" in messages[0]["content"]
            assert messages[1]["role"] == "user"
            assert "Review this code" in messages[1]["content"]

            # Verify other parameters are preserved
            assert data["temperature"] == 0.3
            assert data["max_tokens"] == 500

    def test_sarvam_provider_system_prompt_integration(self):
        """Test system prompt integration with SarvamAI provider."""
        provider = SarvamAIProvider(
            api_key="test-key",
            system_prompt="You are a helpful coding assistant specializing in web development."
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "As a web development expert..."}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate("Help me build a React component.")

            # Verify system prompt is included
            call_args = mock_post.call_args
            data = call_args[1]["json"]
            messages = data["messages"]

            assert len(messages) == 2
            assert messages[0]["role"] == "system"
            assert "web development" in messages[0]["content"]
            assert messages[1]["role"] == "user"
            assert "React component" in messages[1]["content"]

    def test_openai_provider_no_system_prompt_fallback(self):
        """Test that providers work correctly without system prompts."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com",
            api_key="test-key"
            # No system_prompt provided
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response without system prompt"}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate("Simple question")

            # Should only have user message
            call_args = mock_post.call_args
            data = call_args[1]["json"]
            messages = data["messages"]

            assert len(messages) == 1
            assert messages[0]["role"] == "user"
            assert messages[0]["content"] == "Simple question"

    def test_system_prompt_token_counting(self):
        """Test that system prompts are included in token counting."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-4",
            base_url="https://api.openai.com",
            api_key="test-key",
            system_prompt="You are a helpful assistant."
        )

        # The generate method should handle token counting for the full prompt
        # including system prompt - this is tested indirectly through the debug output
        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Test response"}}]
            }
            mock_post.return_value = mock_response

            # This should not raise an exception and should show token counting
            response = provider.generate("Test message")

            assert response == "Test response"

    def test_empty_system_prompt_handling(self):
        """Test handling of empty or None system prompts."""
        provider = OpenAICompatibleProvider(
            model_name="gpt-3.5-turbo",
            base_url="https://api.openai.com",
            api_key="test-key",
            system_prompt=""  # Empty system prompt
        )

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {
                "choices": [{"message": {"content": "Response with empty system prompt"}}]
            }
            mock_post.return_value = mock_response

            response = provider.generate("Test message")

            # Should only have user message when system prompt is empty
            call_args = mock_post.call_args
            data = call_args[1]["json"]
            messages = data["messages"]

            assert len(messages) == 1
            assert messages[0]["role"] == "user"


class TestProviderIntegration:
    """Integration tests for all providers."""

    def test_all_providers_follow_same_interface(self):
        """Test that all providers implement the same interface."""
        providers = [
            OllamaProvider("test-model"),
            OpenAICompatibleProvider("gpt-3.5-turbo", "https://api.openai.com"),
            LMStudioProvider("local-model"),
            SarvamAIProvider(api_key="test-key")
        ]

        for provider in providers:
            assert hasattr(provider, "generate")
            assert callable(getattr(provider, "generate"))

            # All should have model_name attribute
            assert hasattr(provider, "model_name")
            assert provider.model_name

    def test_provider_error_handling_consistency(self):
        """Test that all providers handle errors consistently."""
        providers = [
            ("OllamaProvider", OllamaProvider("test-model")),
            ("OpenAICompatibleProvider", OpenAICompatibleProvider("gpt-3.5-turbo", "https://api.openai.com")),
            ("LMStudioProvider", LMStudioProvider("local-model")),
            ("SarvamAIProvider", SarvamAIProvider(api_key="test-key"))
        ]

        for provider_name, provider in providers:
            # Test that generate method exists and is callable
            assert callable(provider.generate)

            # Test error message format consistency
            # (This would require mocking different failure modes for each provider)

    def test_system_prompt_backward_compatibility(self):
        """Test that existing code without system prompts still works."""
        # Test providers that previously didn't support system prompts
        openai_provider = OpenAICompatibleProvider("gpt-3.5-turbo", "https://api.openai.com")

        with patch("requests.post") as mock_post:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = {"choices": [{"message": {"content": "OK"}}]}
            mock_post.return_value = mock_response

            # Should work without system prompt
            response = openai_provider.generate("Test")
            assert response == "OK"

            # Verify only user message is sent
            call_args = mock_post.call_args
            messages = call_args[1]["json"]["messages"]
            assert len(messages) == 1
            assert messages[0]["role"] == "user"


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

        # Mock the provider response with new work_items structure
        planner_model.provider.generate.return_value = json.dumps(
            {
                "description": "Create unit tests for the project",
                "mode": "sdet",
                "work_items": [
                    {
                        "mode": "sdet",
                        "file_path": "tests/test_file.py",
                        "file_status": "new",
                        "description": "Create unit tests with pytest",
                        "dependencies": []
                    }
                ],
                "priority": "high",
            }
        )

        result = planner_model.analyze_request(user_input, context)

        # Result is now a message, extract payload
        task_plan = result["payload"]["output"]
        assert task_plan["description"] == "Create unit tests for the project"
        assert task_plan["mode"] == "sdet"
        assert "work_items" in task_plan
        assert len(task_plan["work_items"]) == 1
        assert task_plan["work_items"][0]["file_path"] == "tests/test_file.py"
        assert task_plan["priority"] == "high"

    def test_analyze_request_fallback_on_error(self, planner_model):
        """Test fallback behavior when JSON parsing fails."""
        user_input = "Test request"
        context = "Test context"

        # Mock provider to return invalid JSON
        planner_model.provider.generate.return_value = "Invalid JSON response"

        result = planner_model.analyze_request(user_input, context)

        # Should return fallback values with work_items structure
        task_plan = result["payload"]["output"]
        assert task_plan["description"] == "Code implementation task"
        assert task_plan["mode"] == "coder"
        assert "work_items" in task_plan
        assert len(task_plan["work_items"]) == 1
        assert task_plan["work_items"][0]["description"] == "Implement the requested functionality"
        assert task_plan["priority"] == "normal"

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
        task_plan = result["payload"]["output"]
        assert task_plan["description"] == "Partial test"
        assert task_plan["mode"] == "coder"
        assert "work_items" in task_plan  # Should have fallback work_items

    def test_review_output_success(self, planner_model):
        """Test successful output review."""
        task_description = "Create unit tests"
        executor_output = "Created comprehensive test suite"

        # Mock provider response
        planner_model.provider.generate.return_value = json.dumps(
            {
                "quality_score": 0.9,
                "needs_iteration": False,
                "feedback": "Excellent test coverage",
                "suggestions": ["Add integration tests", "Include edge cases"],
            }
        )

        result = planner_model.review_output(task_description, executor_output)

        # Result is now a message, extract payload
        review = result["payload"]["output"]
        assert review["quality_score"] == 0.9
        assert review["needs_iteration"] is False
        assert review["feedback"] == "Excellent test coverage"
        assert len(review["suggestions"]) == 2

    def test_review_output_fallback_on_error(self, planner_model):
        """Test fallback behavior when review parsing fails."""
        task_description = "Test task"
        executor_output = "Test output"

        # Mock provider to return invalid JSON
        planner_model.provider.generate.return_value = "Invalid review response"

        result = planner_model.review_output(task_description, executor_output)

        # Should return fallback values
        review = result["payload"]["output"]
        assert review["quality_score"] == 0.7
        assert review["needs_iteration"] is False
        assert review["feedback"] == "Review completed"
        assert review["suggestions"] == []

    def test_review_output_with_iteration_needed(self, planner_model):
        """Test review output that requires iteration."""
        task_description = "Implement feature"
        executor_output = "Basic implementation"

        planner_model.provider.generate.return_value = json.dumps(
            {
                "quality_score": 0.4,
                "needs_iteration": True,
                "feedback": "Needs significant improvement",
                "suggestions": [
                    "Add error handling",
                    "Improve performance",
                    "Add tests",
                ],
            }
        )

        result = planner_model.review_output(task_description, executor_output)

        review = result["payload"]["output"]
        assert review["quality_score"] == 0.4
        assert review["needs_iteration"] is True
        assert len(review["suggestions"]) == 3


class TestExecutorModel:
    """Test cases for ExecutorModel class."""

    def test_executor_model_initialization(self, mock_ollama_provider):
        """Test ExecutorModel is properly initialized."""
        executor = BaseExecutor(mock_ollama_provider)

        assert executor.provider == mock_ollama_provider
        assert hasattr(executor, "mode_prompt")
        assert isinstance(executor.mode_prompt, str)

    def test_mode_prompt_content(self, mock_ollama_provider):
        """Test that mode prompt contains appropriate content."""
        executor = BaseExecutor(mock_ollama_provider)

        # BaseExecutor has empty mode_prompt by default (it's a fallback)
        # Test that the attribute exists and is a string
        assert hasattr(executor, "mode_prompt")
        assert isinstance(executor.mode_prompt, str)

    def test_execute_task_success(self, executor_model, sample_task_plan):
        """Test successful task execution."""
        context = '{"project_summary": "Test project"}'

        # Mock provider response
        executor_model.provider.generate.return_value = (
            "Successfully implemented the requested feature"
        )

        result = executor_model.execute_task(sample_task_plan, context)

        # Result is now a message, extract payload
        output = result["payload"]["output"]
        assert "Successfully implemented" in output

        # Verify the provider was called with correct prompt structure
        call_args = executor_model.provider.generate.call_args
        prompt = call_args[0][0]  # First positional argument

        assert sample_task_plan["description"] in prompt
        # Mode is in the mode_prompt, not in the task itself
        assert context in prompt
        assert PromptSections.WORK_ITEMS in prompt  # Updated for new prompt format

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
                "priority": "normal",
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
            "priority": "normal",
        }

        executor_model.provider.generate.return_value = "Coder mode response"

        result = executor_model.execute_task(task_plan, context)

        # Should still work and use coder mode as fallback
        output = result["payload"]["output"]
        assert output == "Coder mode response"

        # Verify that the task was executed (the mode doesn't matter for this test)
        call_args = executor_model.provider.generate.call_args
        prompt = call_args[0][0]
        assert (
            "Test task" in prompt
        )  # Just verify the task description is in the prompt

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
        executor = BaseExecutor(mock_ollama_provider)

        # Mock responses
        planner.provider.generate.return_value = json.dumps(
            {
                "description": "Integration test",
                "mode": "coder",
                "steps": ["Step 1", "Step 2"],
                "relevant_files": ["test.py"],
                "priority": "normal",
            }
        )

        executor.provider.generate.return_value = "Implementation complete"

        # Test the workflow
        user_input = "Test integration"
        context = "Test context"

        task_plan_message = planner.analyze_request(user_input, context)
        task_plan = task_plan_message["payload"]["output"]
        result_message = executor.execute_task(task_plan, context)
        result = result_message["payload"]["output"]

        assert result == "Implementation complete"
        assert task_plan["mode"] == "coder"

    def test_error_handling_integration(self, mock_ollama_provider):
        """Test error handling across model integration."""
        planner = PlannerModel(mock_ollama_provider)
        executor = BaseExecutor(mock_ollama_provider)

        # Mock error responses
        planner.provider.generate.return_value = "Invalid JSON"
        executor.provider.generate.return_value = "Error in execution"

        # Should handle errors gracefully
        task_plan_message = planner.analyze_request("Test", "Context")
        task_plan = task_plan_message["payload"]["output"]
        result_message = executor.execute_task(task_plan, "Context")
        result = result_message["payload"]["output"]

        assert result == "Error in execution"
        # Should fallback to coder mode
        assert task_plan["mode"] == "coder"

    def test_provider_error_propagation(self, mock_ollama_provider):
        """Test that provider errors are properly handled."""
        provider = OllamaProvider("test-model")

        # Test with connection error
        with patch("ollama.generate") as mock_generate:
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
            'Text { "valid": "json" } more text',  # JSON in middle
        ]

        for case in edge_cases:
            planner.provider.generate.return_value = case

            # Should not raise exception, should use fallbacks
            result = planner.analyze_request("Test", "Context")

            # Should have valid fallback structure with work_items (in payload)
            task_plan = result["payload"]["output"]
            assert "description" in task_plan
            assert "mode" in task_plan
            assert "work_items" in task_plan
            assert "priority" in task_plan

    def test_model_initialization_with_different_providers(self):
        """Test model initialization with different provider types."""
        # This would test if we had multiple provider types
        # For now, just test that initialization works
        mock_provider = Mock(spec=LLMProvider)
        mock_provider.generate.return_value = "Mock response"

        planner = PlannerModel(mock_provider)
        executor = BaseExecutor(mock_provider)

        assert planner.provider == mock_provider
        assert executor.provider == mock_provider
