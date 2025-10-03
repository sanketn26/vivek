from typing import Any, Dict
import importlib

from vivek.llm.models import LLMProvider
from vivek.utils.prompt_utils import PromptCompressor
from vivek.core.message_protocol import (
    execution_complete,
    clarification_needed,
    error_occurred,
)


class BaseExecutor:
    """Base executor that builds a prompt and delegates generation to an LLM provider.

    Mode-specific executors should inherit from this and set `mode` and `mode_prompt`.
    """

    mode: str = "coder"
    mode_prompt: str = ""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def build_prompt(self, task_plan: Dict[str, Any], context: str) -> str:
        # Compress context to fit within token limits
        max_context_tokens = 3000  # Reserve tokens for mode prompt and task info
        compressed_context = PromptCompressor.truncate_context(
            context, max_context_tokens, strategy="selective"
        )

        # Get work items from task plan
        work_items = task_plan.get("work_items", [])
        
        # Build work items summary
        work_items_summary = []
        for i, item in enumerate(work_items, 1):
            status = "[NEW]" if item.get("file_status") == "new" else "[MODIFY]"
            file_path = item.get("file_path", "")
            desc = item.get("description", "")
            deps = item.get("dependencies", [])
            deps_str = f" (depends on: {', '.join(map(str, deps))})" if deps else ""
            
            work_items_summary.append(
                f"{i}. {status} {file_path}\n   Mode: {item.get('mode', 'coder')}\n   Task: {desc}{deps_str}"
            )
        
        work_items_str = "\n".join(work_items_summary) if work_items_summary else "No specific work items defined"

        mode_instruction = self.mode_prompt or f"Mode: {self.mode}"

        prompt = f"""{mode_instruction}

CONTEXT: {compressed_context}

TASK: {task_plan.get('description', 'Execute the task')}

WORK ITEMS:
{work_items_str}

PROCESS:
1. Execute work items in dependency order (check dependencies array - items with [] go first)
2. For each work item, break into 3-5 sub-tasks (specific, testable, ordered)
3. Implement each sub-task following mode guidelines
4. Verify completion: mark "Complete" or "Issue: [reason]" if blocked
5. Combine outputs and ensure all dependencies satisfied

OUTPUT FORMAT (for each work item):
```
### Work Item [N]: [file_path]

**Sub-tasks:**
1. [description]
2. [description]
3. [description]

**Implementation:**
[code/design/tests/explanation]

**Status:**
☑ Sub-task 1: Complete
☑ Sub-task 2: Issue: [reason] (if any problem, otherwise Complete)
☑ Sub-task 3: Complete
```

Begin execution:"""
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
                task_plan=task_plan.get("description", "unknown"),
                mode=self.mode
            )

    def _check_for_ambiguities(self, task_plan: Dict[str, Any], context: str) -> Dict[str, Any]:
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
        work_items = task_plan.get("work_items", [])
        return {
            "work_items_count": len(work_items),
            "mode": self.mode,
        }


def get_executor(mode: str, provider: LLMProvider) -> BaseExecutor:
    """Factory to return a mode-specific executor.

    Tries to import vivek.llm.<mode>_executor and instantiate the expected class.
    Falls back to BaseExecutor when the specific executor is not available.
    """
    mapping = {
        "peer": "PeerExecutor",
        "architect": "ArchitectExecutor",
        "sdet": "SDETExecutor",
        "coder": "CoderExecutor",
    }
    class_name = mapping.get(mode, "CoderExecutor")
    module_name = f"vivek.llm.{mode}_executor"
    try:
        mod = importlib.import_module(module_name)
        executor_cls = getattr(mod, class_name)
        return executor_cls(provider)
    except Exception:
        return BaseExecutor(provider)
