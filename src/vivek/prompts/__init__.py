"""Prompt system for Vivek - Planning and execution prompts with TDD support.

Key Components:
- prompt_architecture: Interface/ABC architecture (main entry point)
- multi_phase_planner_prompts: Raw planner prompt strings
- granular_sdet_prompts: SDET phase-specific prompts
- tdd_workflow_orchestrator: TDD workflow coordination
"""

# Main architecture exports
from vivek.prompts.prompt_architecture import (
    BaseExecutorPrompt,
    BasePlannerPrompt,
    BasePrompt,
    ClarificationPrompt,
    ConfirmationPrompt,
    DecompositionPrompt,
    ExecutorMode,
    HappyPathTestsPrompt,
    ImplementationPrompt,
    PlannerPhase,
    PromptFactory,
    PromptPair,
    SDETPhase,
    StructInterfacePrompt,
    TestFixturesPrompt,
    WorkItem,
    build_clarification_prompt,
    build_confirmation_prompt,
    build_decomposition_prompt,
)

# SDET phase exports
from vivek.prompts.granular_sdet_prompts import (
    SDET_WORKFLOW_PHASES,
    build_edge_case_tests_prompt,
    build_error_handling_tests_prompt,
    build_test_coverage_prompt,
    build_test_fixtures_prompt,
)

# Planner prompt strings (for reference)
from vivek.prompts.multi_phase_planner_prompts import (
    CLARIFICATION_SYSTEM_PROMPT,
    CLARIFICATION_USER_PROMPT_TEMPLATE,
    CONFIRMATION_SYSTEM_PROMPT,
    CONFIRMATION_USER_PROMPT_TEMPLATE,
    DECOMPOSITION_SYSTEM_PROMPT,
    DECOMPOSITION_USER_PROMPT_TEMPLATE,
)

# Orchestrator
from vivek.prompts.tdd_workflow_orchestrator import (
    ExecutionPhase,
    TDDWorkflowOrchestrator,
)

__all__ = [
    # Architecture
    "BasePrompt",
    "BasePlannerPrompt",
    "BaseExecutorPrompt",
    "PromptPair",
    "WorkItem",
    "PromptFactory",
    # Enums
    "PlannerPhase",
    "ExecutorMode",
    "SDETPhase",
    "ExecutionPhase",
    # Planner prompts
    "ClarificationPrompt",
    "ConfirmationPrompt",
    "DecompositionPrompt",
    # Executor prompts
    "StructInterfacePrompt",
    "TestFixturesPrompt",
    "HappyPathTestsPrompt",
    "ImplementationPrompt",
    # Builder functions (legacy compatibility)
    "build_clarification_prompt",
    "build_confirmation_prompt",
    "build_decomposition_prompt",
    "build_test_fixtures_prompt",
    "build_edge_case_tests_prompt",
    "build_error_handling_tests_prompt",
    "build_test_coverage_prompt",
    # Orchestrator
    "TDDWorkflowOrchestrator",
    # Raw prompt strings
    "CLARIFICATION_SYSTEM_PROMPT",
    "CLARIFICATION_USER_PROMPT_TEMPLATE",
    "CONFIRMATION_SYSTEM_PROMPT",
    "CONFIRMATION_USER_PROMPT_TEMPLATE",
    "DECOMPOSITION_SYSTEM_PROMPT",
    "DECOMPOSITION_USER_PROMPT_TEMPLATE",
    # SDET phases
    "SDET_WORKFLOW_PHASES",
]
