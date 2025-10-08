from typing import Any, Dict, Optional
import importlib
import logging

from vivek.llm.models import LLMProvider
from vivek.llm.constants import (
    TaskStatus,
    Mode,
    TokenLimits,
    CompressionStrategy,
    WorkItemKeys,
    TaskPlanKeys,
    OutputFormatMarkers,
    PromptSections,
)
from vivek.utils.prompt_utils import PromptCompressor
from vivek.utils.token_counter import log_token_count
from vivek.core.message_protocol import (
    execution_complete,
    clarification_needed,
    error_occurred,
)

logger = logging.getLogger(__name__)


class BaseExecutor:
    """Base executor that builds a prompt and delegates generation to an LLM provider.

    Mode-specific executors should inherit from this and set `mode` and `mode_prompt`.
    """

    mode: str = "coder"
    mode_prompt: str = ""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def get_mode_specific_instructions(self) -> str:
        """Get mode-specific instructions for prompt building.

        Override in subclasses to provide mode-specific guidance.
        """
        return ""

    def get_mode_specific_process_steps(self) -> str:
        """Get mode-specific process steps.

        Override in subclasses to customize the PROCESS section.
        """
        return """1. Execute work items in dependency order (check dependencies array - items with [] go first)
2. For each work item, break into 3-5 sub-tasks (specific, testable, ordered)
3. Implement each sub-task following mode guidelines
4. Verify completion: mark "Complete" or "Issue: [reason]" if blocked
5. Combine outputs and ensure all dependencies satisfied"""

    def get_mode_specific_output_format(self) -> str:
        """Get mode-specific output format requirements.

        Override in subclasses to customize the OUTPUT FORMAT section.
        """
        return f"""{OutputFormatMarkers.OUTPUT_FORMAT} (for each work item):
```
{OutputFormatMarkers.WORK_ITEM_HEADER}

{OutputFormatMarkers.SUB_TASKS_HEADER}:
1. [description]
2. [description]
3. [description]

{OutputFormatMarkers.IMPLEMENTATION_HEADER}:
[code/design/tests/explanation]

{OutputFormatMarkers.STATUS_HEADER}:
{OutputFormatMarkers.COMPLETE_MARKER} Sub-task 1: Complete
{OutputFormatMarkers.COMPLETE_MARKER} Sub-task 2: Issue: [reason] (if any problem, otherwise Complete)
{OutputFormatMarkers.COMPLETE_MARKER} Sub-task 3: Complete
```"""

    def get_context_compression_strategy(self) -> str:
        """Get mode-specific context compression strategy.

        Override in subclasses to use different compression strategies.
        """
        return CompressionStrategy.SELECTIVE

    def get_max_context_tokens(self) -> int:
        """Get mode-specific maximum context tokens.

        Override in subclasses to use different token limits.
        """
        return TokenLimits.MAX_CONTEXT_TOKENS

    def build_prompt(self, task_plan: Dict[str, Any], context: str) -> str:
        # Compress context using mode-specific strategy
        compressed_context = PromptCompressor.truncate_context(
            context, self.get_max_context_tokens(), strategy=self.get_context_compression_strategy()
        )

        # Get work items from task plan
        work_items = task_plan.get(TaskPlanKeys.WORK_ITEMS, [])

        # Build work items summary
        work_items_summary = []
        for i, item in enumerate(work_items, 1):
            status = OutputFormatMarkers.NEW_MARKER if item.get(WorkItemKeys.FILE_STATUS) == TaskStatus.NEW.value else OutputFormatMarkers.MODIFY_MARKER
            file_path = item.get(WorkItemKeys.FILE_PATH, "")
            desc = item.get(WorkItemKeys.DESCRIPTION, "")
            deps = item.get(WorkItemKeys.DEPENDENCIES, [])
            deps_str = f" (depends on: {', '.join(map(str, deps))})" if deps else ""

            work_items_summary.append(
                f"{i}. {status} {file_path}\n   Mode: {item.get(WorkItemKeys.MODE, Mode.CODER.value)}\n   "
                f"Task: {desc}{deps_str}"
            )

        work_items_str = "\n".join(work_items_summary) if work_items_summary else \
                          "No specific work items defined"

        # Get mode-specific components
        mode_instruction = self.mode_prompt or f"Mode: {self.mode}"
        mode_specific_instructions = self.get_mode_specific_instructions()
        process_steps = self.get_mode_specific_process_steps()
        output_format = self.get_mode_specific_output_format()

        # Combine all components
        instruction_section = f"{mode_instruction}\n\n{mode_specific_instructions}" if mode_specific_instructions else mode_instruction

        prompt = f"""{instruction_section}

{PromptSections.CONTEXT}: {compressed_context}

{PromptSections.TASK}: {task_plan.get(TaskPlanKeys.DESCRIPTION, 'Execute the task')}

{PromptSections.WORK_ITEMS}:
{work_items_str}

{PromptSections.PROCESS}:
{process_steps}

{output_format}

Begin execution:"""

        # Log token count for monitoring and optimization
        log_token_count(prompt, context=f"Executor[{self.mode}] prompt", threshold=800)

        return prompt

    def execute_task(self, task_plan: Dict[str, Any], context: str) -> Dict[str, Any]:
        """Execute task and return structured message to orchestrator.

        Returns:
            execution_complete message with output, OR
            clarification_needed message if ambiguities found, OR
            error message if execution fails
        """
        try:
            # Check for ambiguities before execution
            clarification_check = self._check_for_ambiguities(task_plan, context)
            if clarification_check:
                return clarification_needed(
                    questions=clarification_check["questions"],
                    from_node=f"executor_{self.mode}",
                    **clarification_check.get("metadata", {})
                )

            # Execute implementation
            prompt = self.build_prompt(task_plan, context)
            output = self.provider.generate(prompt, temperature=0.2)

            # Parse output to extract metadata
            metadata = self._extract_metadata(output, task_plan)

            # Return execution_complete message
            return execution_complete(
                output=output,
                from_node=f"executor_{self.mode}",
                **metadata
            )

        except Exception as e:
            # Return error message
            return error_occurred(
                error=str(e),
                from_node=f"executor_{self.mode}",
                task_plan=task_plan.get(TaskPlanKeys.DESCRIPTION, "unknown"),
                mode=self.mode
            )

    def _check_for_ambiguities(self, task_plan: Dict[str, Any], context: str) \
            -> Optional[Dict[str, Any]]:
        """Check if clarification needed before execution.

        Override in subclasses for mode-specific ambiguity detection.

        Returns:
            Dict with 'questions' and 'metadata' if clarification needed, None otherwise
        """
        # Base implementation: no ambiguity check
        # Subclasses can override for specific checks
        return None

    def _extract_metadata(self, output: str, task_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metadata from executor output.

        Returns:
            Dict with metadata fields like files_modified, work_items_completed, etc.
        """
        # Basic metadata extraction
        work_items = task_plan.get(TaskPlanKeys.WORK_ITEMS, [])
        return {
            "work_items_count": len(work_items),
            "mode": self.mode,
        }


def get_executor(mode: str, provider: LLMProvider, language: Optional[str] = None) -> BaseExecutor:
    """Factory to return a mode and language-specific executor.

    Uses plugin system for dynamic language support with fallback to
    legacy hardcoded mapping for backward compatibility.

    Args:
        mode: Execution mode (coder, architect, peer, sdet)
        provider: LLM provider instance
        language: Programming language (python, typescript, go, etc.)

    Returns:
        Appropriate executor instance
    """
    from ..utils.language_detector import LanguageDetector

    # Auto-detect language if not provided
    if language is None:
        language = LanguageDetector.get_primary_language()

    # Normalize language name
    language = language.lower()

    # Try plugin system first for dynamic language support
    try:
        # Import here to avoid circular imports at module level
        from vivek.llm.plugins.base.registry import create_executor as create_plugin_executor

        plugin_executor = create_plugin_executor(language, mode, provider)
        if plugin_executor is not None:
            return plugin_executor
    except ImportError as e:
        # Plugin system not available, continue to fallback
        logger.debug(f"Plugin system not available: {e}")
    except Exception as e:
        # Plugin system failed, log error but continue to fallback
        logger.warning(f"Plugin system error for {language}/{mode}: {e}")

    # Plugin system is now the single source of truth for language-specific executors
    # Legacy language-specific mapping removed - plugins handle this now

    # Fall back to mode-only mapping (original behavior)
    _MODE_EXECUTOR_MAPPING = {
        Mode.CODER.value: ("vivek.llm.coder_executor", "CoderExecutor"),
        Mode.ARCHITECT.value: ("vivek.llm.architect_executor", "ArchitectExecutor"),
        Mode.PEER.value: ("vivek.llm.peer_executor", "PeerExecutor"),
        Mode.SDET.value: ("vivek.llm.sdet_executor", "SDETExecutor"),
    }

    module_name, class_name = _MODE_EXECUTOR_MAPPING.get(mode, ("vivek.llm.coder_executor", "CoderExecutor"))

    try:
        mod = importlib.import_module(module_name)
        executor_cls = getattr(mod, class_name)
        return executor_cls(provider)
    except Exception:
        return BaseExecutor(provider)
