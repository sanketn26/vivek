"""Architect executor."""

from vivek.llm.executor import BaseExecutor


class ArchitectExecutor(BaseExecutor):
    mode = "architect"
    mode_prompt = "Architect Mode: Focus on design patterns, system structure, scalability, and high-level architectural decisions."
