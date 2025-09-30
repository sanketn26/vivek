from typing import Any, Dict
import importlib

from vivek.llm.models import LLMProvider


class BaseExecutor:
    """Base executor that builds a prompt and delegates generation to an LLM provider.

    Mode-specific executors should inherit from this and set `mode` and `mode_prompt`.
    """

    mode: str = "coder"
    mode_prompt: str = ""

    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def build_prompt(self, task_plan: Dict[str, Any], context: str) -> str:
        mode_instruction = self.mode_prompt or ""
        steps = chr(10).join(
            f"{i+1}. {step}" for i, step in enumerate(task_plan.get("steps", []))
        )
        relevant = ", ".join(task_plan.get("relevant_files", []))
        prompt = f"""{mode_instruction}

Context: {context}
Task: {task_plan.get('description', '')}
Mode: {task_plan.get('mode', self.mode)}
Priority: {task_plan.get('priority', '')}

Steps to complete:
{steps}

Relevant files: {relevant}

Execute this task step by step. Provide clear, actionable output suitable for the {task_plan.get('mode', self.mode)} mode."""
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
