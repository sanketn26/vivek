from typing import Any, Dict
import importlib

from vivek.llm.models import LLMProvider
from vivek.utils.prompt_utils import PromptCompressor


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

        # Build compact task summary
        task_parts = []
        if task_plan.get("description"):
            task_parts.append(f"Task: {task_plan['description']}")
        if task_plan.get("mode"):
            task_parts.append(f"Mode: {task_plan['mode']}")
        if task_plan.get("steps"):
            steps_str = " | ".join(task_plan["steps"][:3])  # Limit to 3 main steps
            task_parts.append(f"Steps: {steps_str}")
        if task_plan.get("relevant_files"):
            files_str = ", ".join(task_plan["relevant_files"][:5])  # Limit to 5 files
            task_parts.append(f"Files: {files_str}")

        task_summary = " | ".join(task_parts)

        mode_instruction = self.mode_prompt or f"Mode: {self.mode}"

        prompt = f"""{mode_instruction}

Context: {compressed_context}

{task_summary}

Execute step by step."""
        return prompt

    def execute_task(self, task_plan: Dict[str, Any], context: str) -> str:
        prompt = self.build_prompt(task_plan, context)
        return self.provider.generate(prompt, temperature=0.2)


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
