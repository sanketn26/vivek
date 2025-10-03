"""
LangGraph node functions for Vivek orchestration.

Each node is a function that takes the current state and returns state updates.
"""

import json
from typing import Dict, Any

from ..llm.planner import PlannerModel
from .graph_state import (
    VivekState,
    TaskPlan,
    ReviewResult,
    increment_iteration,
    get_iteration_count,
)
from ..llm.executor import BaseExecutor
from ..utils.prompt_utils import TokenCounter


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

        # Check context size and warn if approaching limits
        model_name = getattr(planner.provider, 'model_name', 'qwen2.5-coder:7b')
        context_tokens = TokenCounter.count_tokens(context_str, model_name)
        if context_tokens > 15000:  # Warning threshold
            print(
                f"Warning: Large context ({context_tokens} tokens) may impact performance"
            )

        # Get feedback from previous iteration if exists
        if get_iteration_count(state) > 0:
            review = state.get("review_result")
            if review:
                context_str += f"\n\n**Previous Iteration Feedback:**\n{review.get('feedback', '')}"

        # Analyze request - planner now returns a message
        message = planner.analyze_request(user_input, context_str)

        # Check message type
        from ..core.message_protocol import MessageType

        if message["type"] == MessageType.CLARIFICATION_NEEDED.value:
            # Planner needs clarification
            return {
                "needs_clarification": True,
                "clarification_from": message["from_node"],
                "clarification_questions": message["payload"]["questions"],
                "partial_task_plan": message.get("metadata", {}).get("partial_plan")
            }

        # Extract task plan from execution_complete message
        task_plan_data = message["payload"]["output"]

        return {
            "task_plan": task_plan_data,
            "mode": task_plan_data.get("mode", "coder"),
            "needs_clarification": False
        }

    return planner_node


def create_executor_node(executor: BaseExecutor):
    """
    Factory function to create an executor node with the given executor model.

    Args:
        executor: BaseExecutor instance

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

        # Execute task - executor now returns a message
        message = executor.execute_task(dict(task_plan), context_str)

        # Check message type
        from ..core.message_protocol import MessageType

        if message["type"] == MessageType.CLARIFICATION_NEEDED.value:
            # Executor needs clarification
            return {
                "needs_clarification": True,
                "clarification_from": message["from_node"],
                "clarification_questions": message["payload"]["questions"]
            }

        if message["type"] == MessageType.ERROR.value:
            # Executor encountered error
            error_msg = message["payload"]["error"]
            return {
                "executor_output": f"Error: {error_msg}",
                "needs_clarification": False
            }

        # Extract output from execution_complete message
        output = message["payload"]["output"]

        return {
            "executor_output": output,
            "needs_clarification": False
        }

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

        # Review output - planner.review_output now returns a message
        message = planner.review_output(
            task_plan.get("description", ""), executor_output
        )

        # Check message type
        from ..core.message_protocol import MessageType

        if message["type"] == MessageType.CLARIFICATION_NEEDED.value:
            # Reviewer needs clarification
            return {
                "needs_clarification": True,
                "clarification_from": message["from_node"],
                "clarification_questions": message["payload"]["questions"]
            }

        # Extract review data from execution_complete message
        review_data = message["payload"]["output"]

        # Increment iteration counter
        iteration_update = increment_iteration(state)

        return {
            "review_result": review_data,
            "needs_clarification": False,
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


# Routing Functions for Conditional Edges

def route_planner(state: VivekState) -> str:
    """Route after planner based on clarification need.

    Returns:
        "clarification" if clarification needed, else "executor"
    """
    if state.get("needs_clarification"):
        return "clarification"
    return "executor"


def route_executor(state: VivekState) -> str:
    """Route after executor based on clarification need.

    Returns:
        "clarification" if clarification needed, else "reviewer"
    """
    if state.get("needs_clarification"):
        return "clarification"
    return "reviewer"


def route_reviewer(state: VivekState) -> str:
    """Route after reviewer based on clarification, iteration, or completion.

    Returns:
        "clarification" if clarification needed
        "executor" if needs iteration and under max iterations
        "format_response" if done or max iterations reached
    """
    # Check clarification first
    if state.get("needs_clarification"):
        return "clarification"

    # Check if iteration needed
    review_result = state.get("review_result", {})
    needs_iteration = review_result.get("needs_iteration", False)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = 3

    if needs_iteration and iteration_count < max_iterations:
        return "executor"

    # Done - format response
    return "format_response"


def clarification_node(state: VivekState) -> Dict[str, Any]:
    """Format clarification questions for user display.

    Args:
        state: Current graph state with clarification info

    Returns:
        State updates with formatted clarification output
    """
    from_node = state.get("clarification_from", "unknown")
    questions = state.get("clarification_questions", [])

    # Format questions for display
    formatted_questions = []
    for i, q in enumerate(questions, 1):
        q_text = f"{i}. {q['question']}"

        # Add options if it's a choice question
        if q.get("type") == "choice" and q.get("options"):
            options_str = ", ".join(q["options"])
            q_text += f"\n   Options: {options_str}"

        # Add context if provided
        if q.get("context"):
            q_text += f"\n   Context: {q['context']}"

        formatted_questions.append(q_text)

    # Build output message
    output_lines = [
        f"🤔 Clarification needed from {from_node}:",
        "",
        *formatted_questions,
        "",
        "Please provide your answers to continue."
    ]

    clarification_output = "\n".join(output_lines)

    return {
        "needs_clarification": True,
        "status": "paused",
        "clarification_output": clarification_output,
        "clarification_from": from_node
    }
