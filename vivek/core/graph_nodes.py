"""
LangGraph node functions for Vivek orchestration.

Each node is a function that takes the current state and returns state updates.
"""

import json
from typing import Dict, Any
from .graph_state import VivekState, TaskPlan, ReviewResult, increment_iteration, get_iteration_count
from ..llm.models import PlannerModel, ExecutorModel


def create_planner_node(planner: PlannerModel):
    """
    Factory function to create a planner node with the given planner model.

    Args:
        planner: PlannerModel instance

    Returns:
        Node function that analyzes user requests
    """

    def planner_node(state: VivekState) -> Dict[str, Any]:
        """
        Planner node: Analyzes user input and creates a task plan.

        Args:
            state: Current graph state

        Returns:
            State updates with task_plan and mode
        """
        user_input = state["user_input"]
        context = state.get("context", {})

        # Convert context to string for model
        context_str = json.dumps(context, indent=2)

        # Get feedback from previous iteration if exists
        if get_iteration_count(state) > 0:
            review = state.get("review_result")
            if review:
                context_str += f"\n\n**Previous Iteration Feedback:**\n{review.get('feedback', '')}"

        # Analyze request
        task_plan_data = planner.analyze_request(user_input, context_str)

        return {
            "task_plan": task_plan_data,
            "mode": task_plan_data.get("mode", "coder")
        }

    return planner_node


def create_executor_node(executor: ExecutorModel):
    """
    Factory function to create an executor node with the given executor model.

    Args:
        executor: ExecutorModel instance

    Returns:
        Node function that executes tasks
    """

    def executor_node(state: VivekState) -> Dict[str, Any]:
        """
        Executor node: Implements the solution based on the task plan.

        Args:
            state: Current graph state

        Returns:
            State updates with executor_output
        """
        task_plan = state.get("task_plan", {})
        context = state.get("context", {})

        # Convert context to string for model
        context_str = json.dumps(context, indent=2)

        # Add iteration info to context
        iteration_count = get_iteration_count(state)
        if iteration_count > 0:
            context_str += f"\n\n**Iteration:** {iteration_count + 1}/3"
            review = state.get("review_result")
            if review:
                context_str += f"\n**Feedback:** {review.get('feedback', '')}"

        # Execute task
        output = executor.execute_task(task_plan, context_str)

        return {"executor_output": output}

    return executor_node


def create_reviewer_node(planner: PlannerModel):
    """
    Factory function to create a reviewer node with the given planner model.

    Args:
        planner: PlannerModel instance

    Returns:
        Node function that reviews executor output
    """

    def reviewer_node(state: VivekState) -> Dict[str, Any]:
        """
        Reviewer node: Reviews the executor output for quality.

        Args:
            state: Current graph state

        Returns:
            State updates with review_result and incremented iteration_count
        """
        task_plan = state.get("task_plan", {})
        executor_output = state.get("executor_output", "")

        # Review output
        review_data = planner.review_output(
            task_plan.get("description", ""),
            executor_output
        )

        # Increment iteration counter
        iteration_update = increment_iteration(state)

        return {
            "review_result": review_data,
            **iteration_update
        }

    return reviewer_node


def format_response_node(state: VivekState) -> Dict[str, str]:
    """
    Final node: Formats the response for the user.

    Args:
        state: Current graph state

    Returns:
        State update with final_response
    """
    executor_output = state.get("executor_output", "")
    review_result = state.get("review_result", {})
    mode = state.get("mode", "coder")
    iteration_count = get_iteration_count(state)

    # Build response
    header = f"[{mode.upper()} MODE]"

    if iteration_count > 1:
        header += f" (Refined after {iteration_count} iterations)"

    formatted = f"{header}\n\n{executor_output}"

    # Add suggestions if any
    suggestions = review_result.get("suggestions", [])
    if suggestions:
        formatted += "\n\n💡 **Suggestions:**\n"
        formatted += "\n".join(f"• {s}" for s in suggestions[:3])

    # Add quality score
    quality = review_result.get("quality_score", 0.0)
    if quality > 0:
        formatted += f"\n\n✨ **Quality Score:** {quality:.1f}/1.0"

    return {"final_response": formatted}