"""Tests for magic strings and constants used throughout the system."""

import pytest
from unittest.mock import Mock
from vivek.llm.executor import BaseExecutor, get_executor
from vivek.llm.planner import PlannerModel
from vivek.llm.models import LLMProvider
from vivek.core.message_protocol import MessageType


class TestMagicStringsAndConstants:
    """Test that magic strings are properly defined as constants."""

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider."""
        return Mock(spec=LLMProvider)

    def test_file_status_uses_magic_strings(self, mock_provider):
        """Test that file_status values are currently magic strings."""
        # This test demonstrates the current magic string problem
        task_plan = {
            "description": "test task",
            "mode": "coder",
            "work_items": [
                {
                    "mode": "coder",
                    "file_path": "test.py",
                    "file_status": "new",  # This is a magic string!
                    "description": "test work item",
                    "dependencies": []
                }
            ]
        }

        # Currently this works but uses magic strings
        executor = BaseExecutor(mock_provider)
        prompt = executor.build_prompt(task_plan, "{}")

        # Should contain the processed magic string
        assert "[NEW]" in prompt
        # The original magic string "new" is processed into "[NEW]"
        # This demonstrates the magic string issue - "new" is hardcoded

    def test_mode_uses_magic_strings(self, mock_provider):
        """Test that mode values are currently magic strings."""
        modes = ["coder", "architect", "peer", "sdet"]

        for mode in modes:
            # This should work but uses magic strings
            executor = get_executor(mode, mock_provider)
            assert executor is not None

    def test_priority_uses_magic_strings(self):
        """Test that priority values are magic strings."""
        task_plan = {
            "description": "test task",
            "mode": "coder",
            "priority": "normal",  # Magic string!
            "work_items": []
        }

        # Currently works but with magic strings
        assert task_plan["priority"] == "normal"

    def test_executor_prompt_consistency_issue(self):
        """Test that demonstrates the prompt consistency problem."""
        from unittest.mock import Mock

        mock_provider = Mock()
        executor = BaseExecutor(mock_provider)

        # Different types of tasks
        coder_task = {
            "description": "implement feature",
            "mode": "coder",
            "work_items": [
                {
                    "mode": "coder",
                    "file_path": "src/feature.py",
                    "file_status": "new",
                    "description": "implement core logic",
                    "dependencies": []
                }
            ]
        }

        architect_task = {
            "description": "design system",
            "mode": "architect",
            "work_items": [
                {
                    "mode": "architect",
                    "file_path": "docs/architecture.md",
                    "file_status": "new",
                    "description": "design system architecture",
                    "dependencies": []
                }
            ]
        }

        # Both tasks get the same generic prompt structure
        # This demonstrates the consistency issue
        coder_prompt = executor.build_prompt(coder_task, "{}")
        architect_prompt = executor.build_prompt(architect_task, "{}")

        # Both contain generic PROCESS section that doesn't adapt to mode
        assert "1. Execute work items in dependency order" in coder_prompt
        assert "1. Execute work items in dependency order" in architect_prompt

        # Both contain the same output format requirements
        assert "### Work Item [N]: [file_path]" in coder_prompt
        assert "### Work Item [N]: [file_path]" in architect_prompt

    def test_mode_specific_executors_only_set_prompt_string(self):
        """Test that demonstrates mode executors only set prompt strings."""
        from unittest.mock import Mock
        from vivek.llm.coder_executor import CoderExecutor
        from vivek.llm.architect_executor import ArchitectExecutor

        mock_provider = Mock()

        coder_executor = CoderExecutor(mock_provider)
        architect_executor = ArchitectExecutor(mock_provider)

        # Both only differ in mode_prompt string
        assert coder_executor.mode == "coder"
        assert architect_executor.mode == "architect"
        assert coder_executor.mode_prompt != architect_executor.mode_prompt

        # But they use the same build_prompt method from BaseExecutor
        # This demonstrates the lack of mode-specific prompt building

        coder_task = {
            "description": "code task",
            "mode": "coder",
            "work_items": [{"mode": "coder", "file_path": "test.py", "file_status": "new", "description": "code", "dependencies": []}]
        }

        architect_task = {
            "description": "design task",
            "mode": "architect",
            "work_items": [{"mode": "architect", "file_path": "design.md", "file_status": "new", "description": "design", "dependencies": []}]
        }

        coder_prompt = coder_executor.build_prompt(coder_task, "{}")
        architect_prompt = architect_executor.build_prompt(architect_task, "{}")

        # The prompts are very similar despite different modes
        # Only difference is the mode_prompt at the beginning
        assert "CODER MODE" in coder_prompt
        assert "ARCHITECT MODE" in architect_prompt

        # But the rest of the prompt structure is identical
        # This shows the consistency issue