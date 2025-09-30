"""Architect executor."""
from vivek.llm.executor import BaseExecutor

class ArchitectExecutor(BaseExecutor):
    mode = "architect"
    mode_prompt = (
        "You are in Software Architect mode. Focus on design patterns, system structure, "
        "scalability, and high-level architectural decisions. Think strategically."
    )