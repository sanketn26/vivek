"""Architect executor."""

from vivek.llm.executor import BaseExecutor
from vivek.llm.constants import (
    Mode,
    TokenLimits,
    CompressionStrategy,
    OutputFormatMarkers,
    PromptSections,
)


class ArchitectExecutor(BaseExecutor):
    mode = Mode.ARCHITECT.value
    mode_prompt = """# ARCHITECT MODE - Structured Design Process

Design system architecture:
1. List functional/non-functional requirements
2. Identify constraints (performance, scale, resources)
3. Present 2-3 architecture options with pros/cons
4. Recommend best option with justification
5. Define: components, data flow, interfaces, dependencies
6. Identify applicable design patterns
7. List potential issues and mitigations"""

    def get_mode_specific_instructions(self) -> str:
        """Get architect-specific instructions for design."""
        return """Focus on system design and architecture quality:
- Consider scalability, performance, and maintainability
- Evaluate multiple architectural approaches
- Define clear component responsibilities
- Identify appropriate design patterns
- Consider technology choices and their trade-offs
- Plan for future extensibility and evolution
- Address cross-cutting concerns (security, logging, monitoring)"""

    def get_mode_specific_process_steps(self) -> str:
        """Get architect-specific process steps."""
        return """1. Execute work items in dependency order (check dependencies array - items with [] go first)
2. For each work item, break into 3-5 sub-tasks (analyze, design, validate, document)
3. Analyze requirements and constraints thoroughly
4. Create multiple design options with pros/cons analysis
5. Recommend optimal architecture with clear justification
6. Document components, interfaces, and integration patterns
7. Validate design addresses all requirements and considerations"""

    def get_mode_specific_output_format(self) -> str:
        """Get architect-specific output format requirements."""
        return f"""{OutputFormatMarkers.OUTPUT_FORMAT} (for each work item):
```
{OutputFormatMarkers.WORK_ITEM_HEADER}

**Architecture Analysis:**
- Functional and non-functional requirements
- Constraints and limitations
- Multiple architecture options with trade-off analysis

**Recommended Design:**
- Component structure and responsibilities
- Data flow and integration patterns
- Design patterns and architectural styles
- Technology recommendations with rationale

**Design Documentation:**
```
┌─────────────┐      ┌──────────────┐
│   Component │─────→│   Interface  │
│     A       │      │     Layer    │
└─────────────┘      └──────────────┘
        ↑                       ↓
        │              ┌──────────────┐
        └─────────────→│   Component  │
                       │      B       │
                       └──────────────┘
```

**Validation Checklist:**
- Requirements are fully addressed
- Architecture is scalable and maintainable
- Clear separation of concerns
- Technology choices are justified
- Potential issues are identified with mitigations
```"""

    def get_context_compression_strategy(self) -> str:
        """Architect mode needs comprehensive context for system analysis."""
        return CompressionStrategy.SUMMARY

    def get_max_context_tokens(self) -> int:
        """Architect mode needs more context for comprehensive system analysis."""
        return TokenLimits.PLANNER_CONTEXT_TOKENS  # Use planner's context size for comprehensive analysis
