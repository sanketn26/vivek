"""SDET executor."""
from vivek.llm.executor import BaseExecutor

class SDETExecutor(BaseExecutor):
    mode = "sdet"
    mode_prompt = (
        "You are in SDET (Software Engineer in Test) mode. Focus on testing strategies, "
        "test automation, quality assurance, and identifying potential issues."
    )