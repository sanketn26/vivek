"""SDET executor."""

from vivek.llm.executor import BaseExecutor


class SDETExecutor(BaseExecutor):
    mode = "sdet"
    mode_prompt = "SDET Mode: Focus on testing strategies, automation, quality assurance, and identifying potential issues."
