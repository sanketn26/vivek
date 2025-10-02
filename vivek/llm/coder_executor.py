"""Coder executor."""

from vivek.llm.executor import BaseExecutor


class CoderExecutor(BaseExecutor):
    mode = "coder"
    mode_prompt = "Coder Mode: Write clean, efficient, production-ready code with error handling and documentation."
