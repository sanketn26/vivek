"""Coder executor."""
from vivek.llm.executor import BaseExecutor

class CoderExecutor(BaseExecutor):
    mode = "coder"
    mode_prompt = (
        "You are in Coder mode. Focus on clean, efficient implementation. "
        "Write production-ready code with proper error handling and documentation."
    )