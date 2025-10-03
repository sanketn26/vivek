"""Tests for executors returning structured messages to orchestrator."""

import pytest
from unittest.mock import Mock

from vivek.llm.executor import BaseExecutor, get_executor
from vivek.llm.provider import OllamaProvider
from vivek.core.message_protocol import MessageType


class TestExecutorMessages:
    """Test executors return structured messages for orchestrator."""

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider."""
        provider = Mock(spec=OllamaProvider)
        return provider

    @pytest.fixture
    def executor(self, mock_provider):
        """Create executor with mock provider."""
        return BaseExecutor(mock_provider)

    @pytest.fixture
    def sample_task_plan(self):
        """Sample task plan."""
        return {
            "description": "implement authentication",
            "mode": "coder",
            "work_items": [
                {
                    "mode": "coder",
                    "file_path": "src/auth.py",
                    "file_status": "new",
                    "description": "implement JWT authentication",
                    "dependencies": []
                }
            ],
            "priority": "normal"
        }

    def test_executor_returns_execution_complete_message(self, executor, mock_provider, sample_task_plan):
        """Test executor returns execution_complete message on success."""
        # Mock successful execution
        mock_provider.generate.return_value = """
### Work Item 1: src/auth.py

**Sub-tasks:**
1. Create auth module structure
2. Implement JWT token generation
3. Add error handling

**Implementation:**
```python
def generate_token(user_id):
    return jwt.encode({"user_id": user_id})
```

**Status:**
☑ Sub-task 1: Complete
☑ Sub-task 2: Complete
☑ Sub-task 3: Complete
"""

        result = executor.execute_task(sample_task_plan, "{}")

        # Should return execution_complete message
        assert result["type"] == MessageType.EXECUTION_COMPLETE.value
        assert result["from_node"] == "executor_coder"
        assert "output" in result["payload"]
        assert "src/auth.py" in result["payload"]["output"]

    @pytest.mark.skip(reason="Phase 2: Requires internal ambiguity detection workflow")
    def test_executor_returns_clarification_needed_message(self, executor, mock_provider, sample_task_plan):
        """Test executor returns clarification_needed when ambiguous."""
        # Mock executor finding ambiguity
        mock_provider.generate.return_value = """
CLARIFICATION NEEDED:
1. Found 2 auth.py files - which to modify?
   - src/api/auth.py
   - src/utils/auth.py

2. JWT library not specified - use PyJWT or python-jose?
"""

        result = executor.execute_task(sample_task_plan, "{}")

        # Should return clarification_needed message
        assert result["type"] == MessageType.CLARIFICATION_NEEDED.value
        assert result["from_node"] == "executor_coder"
        assert "questions" in result["payload"]
        assert len(result["payload"]["questions"]) >= 1

    def test_executor_returns_error_message_on_exception(self, executor, mock_provider, sample_task_plan):
        """Test executor returns error message on exception."""
        # Mock provider raising exception
        mock_provider.generate.side_effect = Exception("Network error")

        result = executor.execute_task(sample_task_plan, "{}")

        # Should return error message
        assert result["type"] == MessageType.ERROR.value
        assert result["from_node"] == "executor_coder"
        assert "error" in result["payload"]
        assert "Network error" in result["payload"]["error"]

    def test_executor_includes_metadata_in_messages(self, executor, mock_provider, sample_task_plan):
        """Test executor includes useful metadata."""
        mock_provider.generate.return_value = """
### Work Item 1: src/auth.py
**Implementation:**
```python
def login(): pass
```
**Status:**
☑ Complete
"""

        result = executor.execute_task(sample_task_plan, "{}")

        # Check metadata contains useful info
        assert result["type"] == MessageType.EXECUTION_COMPLETE.value
        assert "metadata" in result
        # Should include work items completed, files modified, etc.

    def test_coder_executor_returns_structured_message(self, mock_provider, sample_task_plan):
        """Test CoderExecutor returns structured messages."""
        from vivek.llm.coder_executor import CoderExecutor
        executor = CoderExecutor(mock_provider)

        mock_provider.generate.return_value = """
### Work Item 1: src/auth.py
**Implementation:**
def authenticate(): return True
**Status:**
☑ Complete
"""

        result = executor.execute_task(sample_task_plan, "{}")

        assert result["type"] == MessageType.EXECUTION_COMPLETE.value
        assert result["from_node"] == "executor_coder"

    def test_executor_factory_creates_executors_returning_messages(self, mock_provider, sample_task_plan):
        """Test get_executor creates executors that return messages."""
        modes = ["peer", "architect", "sdet", "coder"]

        for mode in modes:
            executor = get_executor(mode, mock_provider)
            mock_provider.generate.return_value = "Task complete"

            result = executor.execute_task(sample_task_plan, "{}")

            # All executors should return structured messages
            assert "type" in result
            assert "from_node" in result
            assert "payload" in result

    @pytest.mark.skip(reason="Phase 2: Requires internal ambiguity detection workflow")
    def test_executor_detects_ambiguity_before_execution(self, executor, mock_provider):
        """Test executor checks for ambiguities before executing."""
        # Task with multiple file possibilities
        ambiguous_task = {
            "description": "modify auth",
            "mode": "coder",
            "work_items": [{
                "mode": "coder",
                "file_path": "auth.py",  # No path specified
                "file_status": "existing",
                "description": "add logging",
                "dependencies": []
            }]
        }

        # Context has multiple auth.py files
        context = """
        {
            "files": ["src/auth.py", "tests/auth.py", "utils/auth.py"]
        }
        """

        # Mock executor detecting ambiguity
        mock_provider.generate.return_value = """
CLARIFICATION NEEDED:
Found 3 files matching 'auth.py' - which one to modify?
"""

        result = executor.execute_task(ambiguous_task, context)

        # Should ask for clarification before attempting modification
        assert result["type"] == MessageType.CLARIFICATION_NEEDED.value
