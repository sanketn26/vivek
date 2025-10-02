"""Architect executor."""

from vivek.llm.executor import BaseExecutor


class ArchitectExecutor(BaseExecutor):
    mode = "architect"
    mode_prompt = """# ARCHITECT MODE - Structured Design Process

## YOUR TASK:
Design the system architecture following these steps:

1. REQUIREMENTS: List functional and non-functional requirements
2. CONSTRAINTS: Identify limitations (performance, scale, resources)
3. DESIGN OPTIONS: Present 2-3 architecture options with pros/cons
4. RECOMMENDATION: Choose best option with justification
5. STRUCTURE: Define:
   - Components/modules
   - Data flow
   - Interfaces
   - Dependencies
6. PATTERNS: Identify applicable design patterns
7. RISKS: List potential issues and mitigations

## OUTPUT FORMAT:
Structured design document with:
- Clear component diagrams (text-based)
- Module responsibilities
- Integration points
- Technology choices with rationale

## VALIDATION:
☑ Addresses all requirements
☑ Scalable solution
☑ Maintainable structure
☑ Clear separation of concerns"""
