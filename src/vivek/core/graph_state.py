"""
LangGraph state definitions for Vivek orchestration.

This module defines the shared state structure used across all graph nodes.
"""

from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import NotRequired


class WorkItem(TypedDict):
    """Individual work item with detailed breakdown"""

    mode: str  # peer, architect, sdet, coder
    file_path: str  # Exact file path
    file_status: str  # "new" or "existing"
    description: str  # Detailed description/prompt for this work item
    dependencies: NotRequired[List[str]]  # Other work items this depends on


class TaskPlan(TypedDict):
    """Task plan created by planner node"""

    description: str
    mode: str  # Overall mode - peer, architect, sdet, coder
    work_items: List[WorkItem]  # Detailed work items to execute
    priority: str  # low, normal, high


class ReviewResult(TypedDict):
    """Review result from planner node"""

    quality_score: float  # 0.0 to 1.0
    needs_iteration: bool
    feedback: str
    suggestions: List[str]


class VivekState(TypedDict):
    """
    Shared state across all nodes in the Vivek graph.

    This state is automatically managed by LangGraph and persisted via SqliteSaver.
    Each field can be updated by any node and is available to subsequent nodes.
    """

    # Input
    user_input: str

    # Planner outputs
    task_plan: NotRequired[TaskPlan]
    mode: NotRequired[str]

    # Executor outputs
    executor_output: NotRequired[str]

    # Reviewer outputs
    review_result: NotRequired[ReviewResult]

    # Iteration tracking
    iteration_count: NotRequired[int]

    # Context (condensed history, project info)
    context: NotRequired[Dict[str, Any]]

    # Final output
    final_response: NotRequired[str]

    # Error tracking
    error: NotRequired[str]
    last_error: NotRequired[str]

    # Clarification flow
    needs_clarification: NotRequired[bool]
    clarification_from: NotRequired[str]  # Which node needs clarification
    clarification_questions: NotRequired[List[Dict[str, Any]]]
    clarification_answers: NotRequired[Dict[str, str]]
    clarification_output: NotRequired[str]  # Formatted output for user
    partial_task_plan: NotRequired[Dict[str, Any]]  # Partial plan before clarification
    status: NotRequired[str]  # "paused", "running", etc.


def initialize_state(
    user_input: str, context: Optional[Dict[str, Any]] = None
) -> VivekState:
    """
    Initialize a new state for processing a user request.

    Args:
        user_input: The user's request
        context: Optional context from previous interactions

    Returns:
        Initialized VivekState
    """
    return VivekState(user_input=user_input, context=context or {}, iteration_count=0)


def get_iteration_count(state: VivekState) -> int:
    """Get current iteration count, defaulting to 0"""
    return state.get("iteration_count", 0)


def increment_iteration(state: VivekState) -> Dict[str, int]:
    """Increment iteration count"""
    current = get_iteration_count(state)
    return {"iteration_count": current + 1}


def should_iterate(state: VivekState) -> str:
    """
    Conditional edge function to determine if iteration is needed.

    Returns:
        "iterate" if quality is poor and under max iterations
        "finish" otherwise
    """
    review = state.get("review_result")
    if not review:
        return "finish"

    # Check quality threshold
    if review.get("needs_iteration", False) and review.get("quality_score", 1.0) < 0.6:
        # Check iteration limit
        if get_iteration_count(state) < 3:  # Max 3 iterations
            return "iterate"

    return "finish"
