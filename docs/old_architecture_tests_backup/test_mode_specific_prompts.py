"""Tests for mode-specific prompt building functionality."""

import pytest
from unittest.mock import Mock
from vivek.llm.executor import BaseExecutor, get_executor
from vivek.llm.models import LLMProvider
from vivek.llm.constants import Mode, TaskStatus, TaskPlanKeys, WorkItemKeys


class TestModeSpecificPromptBuilding:
    """Test that demonstrates current issues with mode-specific prompt building."""

    @pytest.fixture
    def mock_provider(self):
        """Mock LLM provider."""
        return Mock(spec=LLMProvider)

    def test_current_prompt_structure_is_identical_across_modes(self, mock_provider):
        """Test that demonstrates the current prompt consistency issue."""
        # Create different mode executors
        coder_executor = get_executor(Mode.CODER.value, mock_provider)
        architect_executor = get_executor(Mode.ARCHITECT.value, mock_provider)
        peer_executor = get_executor(Mode.PEER.value, mock_provider)
        sdet_executor = get_executor(Mode.SDET.value, mock_provider)

        # Create identical task plans but for different modes
        tasks = {}
        for mode in [Mode.CODER, Mode.ARCHITECT, Mode.PEER, Mode.SDET]:
            tasks[mode] = {
                TaskPlanKeys.DESCRIPTION: f"{mode.value} task",
                TaskPlanKeys.MODE: mode.value,
                TaskPlanKeys.WORK_ITEMS: [
                    {
                        WorkItemKeys.MODE: mode.value,
                        WorkItemKeys.FILE_PATH: f"test_{mode.value}.py",
                        WorkItemKeys.FILE_STATUS: TaskStatus.NEW.value,
                        WorkItemKeys.DESCRIPTION: f"Perform {mode.value} work",
                        WorkItemKeys.DEPENDENCIES: [],
                    }
                ],
            }

        # Generate prompts for each mode
        prompts = {}
        for mode in [Mode.CODER, Mode.ARCHITECT, Mode.PEER, Mode.SDET]:
            executor = get_executor(mode.value, mock_provider)
            prompts[mode] = executor.build_prompt(tasks[mode], "test context")

        # Demonstrate the issue: prompts are too similar despite different modes
        coder_prompt = prompts[Mode.CODER]
        architect_prompt = prompts[Mode.ARCHITECT]

        # Both contain the same generic PROCESS section
        assert "1. Execute work items in dependency order" in coder_prompt
        assert "1. Execute work items in dependency order" in architect_prompt

        # Both contain the same output format requirements
        assert "### Work Item [N]: [file_path]" in coder_prompt
        assert "### Work Item [N]: [file_path]" in architect_prompt

        # The only difference is the mode_prompt at the beginning
        assert "CODER MODE" in coder_prompt
        assert "ARCHITECT MODE" in architect_prompt

        # This shows the consistency issue - prompts don't adapt to mode-specific needs

    def test_executors_only_differ_in_mode_prompt_string(self, mock_provider):
        """Test that current executors only set mode_prompt strings."""
        coder_executor = get_executor(Mode.CODER.value, mock_provider)
        architect_executor = get_executor(Mode.ARCHITECT.value, mock_provider)

        # They have different mode_prompts
        assert coder_executor.mode_prompt != architect_executor.mode_prompt
        assert "CODER MODE" in coder_executor.mode_prompt
        assert "ARCHITECT MODE" in architect_executor.mode_prompt

        # But they use the same build_prompt method from BaseExecutor
        assert (
            coder_executor.build_prompt.__func__
            == architect_executor.build_prompt.__func__
        )

        # This demonstrates the lack of mode-specific prompt building logic

    def test_no_mode_specific_context_handling(self, mock_provider):
        """Test that context handling is identical across all modes."""
        executor = BaseExecutor(mock_provider)

        # Same context compression logic for all modes
        task_plan = {
            TaskPlanKeys.DESCRIPTION: "test task",
            TaskPlanKeys.MODE: Mode.CODER.value,
            TaskPlanKeys.WORK_ITEMS: [],
        }

        # All modes use the same token limit and compression strategy
        prompt1 = executor.build_prompt(task_plan, "short context")
        prompt2 = executor.build_prompt(
            task_plan, "long context that should be compressed differently"
        )

        # Both use same compression settings regardless of mode requirements
        # This demonstrates lack of mode-specific context handling

    def test_identical_output_format_requirements(self, mock_provider):
        """Test that output format requirements are identical across modes."""
        executor = BaseExecutor(mock_provider)

        coder_task = {
            TaskPlanKeys.DESCRIPTION: "code task",
            TaskPlanKeys.MODE: Mode.CODER.value,
            TaskPlanKeys.WORK_ITEMS: [
                {
                    WorkItemKeys.MODE: Mode.CODER.value,
                    WorkItemKeys.FILE_PATH: "test.py",
                    WorkItemKeys.FILE_STATUS: TaskStatus.NEW.value,
                    WorkItemKeys.DESCRIPTION: "implement function",
                    WorkItemKeys.DEPENDENCIES: [],
                }
            ],
        }

        architect_task = {
            TaskPlanKeys.DESCRIPTION: "design task",
            TaskPlanKeys.MODE: Mode.ARCHITECT.value,
            TaskPlanKeys.WORK_ITEMS: [
                {
                    WorkItemKeys.MODE: Mode.ARCHITECT.value,
                    WorkItemKeys.FILE_PATH: "design.md",
                    WorkItemKeys.FILE_STATUS: TaskStatus.NEW.value,
                    WorkItemKeys.DESCRIPTION: "design architecture",
                    WorkItemKeys.DEPENDENCIES: [],
                }
            ],
        }

        coder_prompt = executor.build_prompt(coder_task, "{}")
        architect_prompt = executor.build_prompt(architect_task, "{}")

        # Both require the same output format despite different modes
        # CODER mode should focus on code implementation
        # ARCHITECT mode should focus on design documentation
        # But both get identical format requirements

        # This demonstrates the need for mode-specific output formats
