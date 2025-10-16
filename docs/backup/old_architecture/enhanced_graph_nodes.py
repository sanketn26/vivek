"""
Enhanced LangGraph node functions with structured workflow integration.

This module provides enhanced versions of the core graph nodes that can optionally
use the structured prompt architecture for improved workflow alignment.
"""

import json
from typing import Dict, Any, Union

from ..llm.planner import PlannerModel
from ..llm.structured_planner import StructuredPlannerModel
from ..llm.executor import BaseExecutor
from .graph_state import VivekState
from ..utils.prompt_utils import TokenCounter


def create_enhanced_planner_node(
    planner: Union[PlannerModel, StructuredPlannerModel], use_structured: bool = True
):
    """
    Factory function to create an enhanced planner node.

    Args:
        planner: PlannerModel or StructuredPlannerModel instance
        use_structured: Whether to use structured workflow (if StructuredPlannerModel)

    Returns:
        Enhanced node function with structured workflow support
    """

    def enhanced_planner_node(state: VivekState) -> Dict[str, Any]:
        """
        Enhanced planner node with structured workflow support.

        Args:
            state: Current graph state

        Returns:
            State updates with enhanced task planning
        """
        user_input = state["user_input"]
        context = state.get("context", {})

        # Convert context to string for model
        context_str = json.dumps(context, indent=2)

        # Check context size and warn if approaching limits
        model_name = getattr(planner.provider, "model_name", "qwen2.5-coder:7b")
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

        # Analyze request - both planner types return messages
        message = planner.analyze_request(user_input, context_str)

        # Check message type
        from ..core.message_protocol import MessageType

        if message["type"] == MessageType.CLARIFICATION_NEEDED.value:
            # Planner needs clarification (new message protocol format)
            return {
                "needs_clarification": True,
                "clarification_from": message["from_node"],
                "clarification_questions": message["payload"]["questions"],
                "partial_task_plan": message.get("metadata", {}).get("partial_plan"),
            }
        elif isinstance(message, dict) and message.get("needs_clarification"):
            # Planner needs clarification (legacy format - backward compatibility)
            return {
                "needs_clarification": True,
                "clarification_from": "planner",
                "clarification_questions": message.get("questions", []),
                "partial_task_plan": message.get("partial_plan"),
            }
        else:
            # Execution complete or other message type
            return {
                "task_plan": message.get("payload", {}).get("output", message),
                "mode": message.get("mode", "coder"),
                "needs_clarification": False,
            }

        # Extract task plan from execution_complete message
        task_plan_data = message["payload"]["output"]

        # Enhanced metadata for structured workflows
        enhanced_metadata = {}

        # If using structured planner, add workflow metadata
        if use_structured and isinstance(planner, StructuredPlannerModel):
            enhanced_metadata.update(
                {
                    "structured_workflow": task_plan_data.get(
                        "structured_workflow", {}
                    ),
                    "workflow_phases": ["understand", "decompose", "detail", "taskify"],
                    "context_management": {
                        "strategy": "agentic_context",
                        "context_layers": [
                            "immediate",
                            "short_term",
                            "medium_term",
                            "long_term",
                        ],
                    },
                }
            )

        return {
            "task_plan": task_plan_data,
            "mode": task_plan_data.get("mode", "coder"),
            "needs_clarification": False,
            "enhanced_metadata": enhanced_metadata,
        }

    return enhanced_planner_node


def create_enhanced_executor_node(executor: BaseExecutor, context_manager=None):
    """
    Factory function to create an enhanced executor node.

    Args:
        executor: BaseExecutor instance
        context_manager: Optional context manager for enhanced context handling

    Returns:
        Enhanced executor node function
    """

    def enhanced_executor_node(state: VivekState) -> Dict[str, Any]:
        """
        Enhanced executor node with context management.

        Args:
            state: Current graph state

        Returns:
            State updates with enhanced execution tracking
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

        # Add workflow context if available
        enhanced_metadata = state.get("enhanced_metadata", {})
        if enhanced_metadata:
            workflow_context = enhanced_metadata.get("structured_workflow", {})
            if workflow_context:
                context_str += f"\n\n**Workflow Context:** {json.dumps(workflow_context, indent=2)}"

        # Execute task - executor returns a message
        message = executor.execute_task(dict(task_plan), context_str)

        # Check message type
        from ..core.message_protocol import MessageType

        if message["type"] == MessageType.CLARIFICATION_NEEDED.value:
            # Executor needs clarification (new message protocol format)
            return {
                "needs_clarification": True,
                "clarification_from": message["from_node"],
                "clarification_questions": message["payload"]["questions"],
            }

        if message["type"] == MessageType.ERROR.value:
            # Executor encountered error (new message protocol format)
            error_msg = message["payload"]["error"]
            return {
                "executor_output": f"Error: {error_msg}",
                "needs_clarification": False,
            }

        # Handle legacy format for backward compatibility
        if message.get("type") == "clarification_needed":
            return {
                "needs_clarification": True,
                "clarification_from": message.get("from_node", "executor"),
                "clarification_questions": message.get("payload", {}).get(
                    "questions", []
                ),
            }

        # Extract output from execution_complete message (new format)
        if message["type"] == MessageType.EXECUTION_COMPLETE.value:
            output = message["payload"]["output"]
        else:
            # Legacy format fallback
            output = message.get("output", str(message))

        # Enhanced execution metadata
        execution_metadata = {
            "execution_context": {
                "iteration_count": iteration_count,
                "context_tokens": TokenCounter.count_tokens(
                    context_str,
                    model_name=getattr(executor.provider, "model_name", "unknown"),
                ),
                "task_complexity": len(task_plan.get("work_items", [])),
            }
        }

        return {
            "executor_output": output,
            "needs_clarification": False,
            "execution_metadata": execution_metadata,
        }

    return enhanced_executor_node


def create_enhanced_reviewer_node(
    planner: Union[PlannerModel, StructuredPlannerModel], use_structured: bool = True
):
    """
    Factory function to create an enhanced reviewer node.

    Args:
        planner: PlannerModel or StructuredPlannerModel instance
        use_structured: Whether to use structured review process

    Returns:
        Enhanced reviewer node function
    """

    def enhanced_reviewer_node(state: VivekState) -> Dict[str, Any]:
        """
        Enhanced reviewer node with structured review process.

        Args:
            state: Current graph state

        Returns:
            State updates with enhanced review and iteration tracking
        """
        task_plan = state.get("task_plan", {})
        executor_output = state.get("executor_output", "")

        # Get workflow context for enhanced review
        enhanced_metadata = state.get("enhanced_metadata", {})
        workflow_context = enhanced_metadata.get("structured_workflow", {})

        # Review output - both planner types return messages
        message = planner.review_output(
            task_plan.get("description", ""), executor_output
        )

        # Check message type
        from ..core.message_protocol import MessageType

        if message["type"] == MessageType.CLARIFICATION_NEEDED.value:
            # Reviewer needs clarification (new message protocol format)
            return {
                "needs_clarification": True,
                "clarification_from": message["from_node"],
                "clarification_questions": message["payload"]["questions"],
            }

        # Handle legacy format for backward compatibility
        if message.get("requirements_unclear"):
            return {
                "needs_clarification": True,
                "clarification_from": "reviewer",
                "clarification_questions": message.get("unclear_points", []),
            }

        # Extract review data from execution_complete message (new format)
        if message["type"] == MessageType.EXECUTION_COMPLETE.value:
            review_data = message["payload"]["output"]
        else:
            # Legacy format fallback
            review_data = message.get("output", message)

        # Increment iteration counter
        iteration_update = increment_iteration(state)

        # Enhanced review metadata
        enhanced_review_metadata = {
            "review_context": {
                "workflow_phase": workflow_context.get("current_phase", "unknown"),
                "iteration_count": iteration_update.get("iteration_count", 0),
                "structured_review": use_structured,
            }
        }

        return {
            "review_result": review_data,
            "needs_clarification": False,
            "enhanced_review_metadata": enhanced_review_metadata,
            **iteration_update,
        }

    return enhanced_reviewer_node


def create_enhanced_format_response_node():
    """
    Factory function to create an enhanced format response node.

    Returns:
        Enhanced format response node function with structured workflow display
    """

    def enhanced_format_response_node(state: VivekState) -> Dict[str, str]:
        """
        Enhanced format response node with structured workflow information.

        Args:
            state: Current graph state

        Returns:
            State update with enhanced final response
        """
        executor_output = state.get("executor_output", "")
        review_result = state.get("review_result", {})
        mode = state.get("mode", "coder")
        iteration_count = get_iteration_count(state)

        # Get enhanced metadata for structured workflow display
        enhanced_metadata = state.get("enhanced_metadata", {})
        execution_metadata = state.get("execution_metadata", {})
        review_metadata = state.get("enhanced_review_metadata", {})

        # Build enhanced response header
        header = f"[{mode.upper()} MODE]"

        # Add structured workflow info if available
        if enhanced_metadata.get("structured_workflow"):
            workflow_info = enhanced_metadata["structured_workflow"]
            header += (
                f" (Structured Workflow: {workflow_info.get('phases', ['unknown'])})"
            )

        if iteration_count > 1:
            header += f" (Refined after {iteration_count} iterations)"

        formatted = f"{header}\n\n{executor_output}"

        # Add enhanced suggestions with workflow context
        suggestions = review_result.get("suggestions", [])
        if suggestions:
            formatted += "\n\n💡 **Enhanced Suggestions:**\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                formatted += f"{i}. {suggestion}\n"

        # Add workflow insights if available
        if enhanced_metadata or execution_metadata:
            formatted += "\n\n🔧 **Workflow Insights:**\n"

            if enhanced_metadata.get("structured_workflow"):
                workflow = enhanced_metadata["structured_workflow"]
                formatted += f"• Activities: {workflow.get('activities_count', 0)}\n"
                formatted += f"• Tasks: {workflow.get('tasks_count', 0)}\n"

            if execution_metadata.get("execution_context"):
                exec_ctx = execution_metadata["execution_context"]
                formatted += (
                    f"• Context Used: {exec_ctx.get('context_tokens', 0)} tokens\n"
                )
                formatted += f"• Task Complexity: {exec_ctx.get('task_complexity', 0)} work items\n"

        # Add quality score with enhanced context
        quality = review_result.get("quality_score", 0.0)
        if quality > 0:
            quality_context = (
                " (High confidence)"
                if quality > 0.8
                else " (Good quality)" if quality > 0.6 else ""
            )
            formatted += f"\n\n✨ **Quality Score:** {quality:.1f}/1.0{quality_context}"

        return {"final_response": formatted}

    return enhanced_format_response_node


# Import here to avoid circular imports
def get_iteration_count(state: VivekState) -> int:
    """Get current iteration count from state"""
    return state.get("iteration_count", 0)


def increment_iteration(state: VivekState) -> Dict[str, int]:
    """Increment iteration count"""
    current = get_iteration_count(state)
    return {"iteration_count": current + 1}


# Enhanced routing functions that consider structured workflow state


def enhanced_route_planner(state: Dict[str, Any]) -> str:
    """Enhanced routing after planner with structured workflow awareness."""
    if state.get("needs_clarification"):
        return "clarification"
    return "executor"


def enhanced_route_executor(state: Dict[str, Any]) -> str:
    """Enhanced routing after executor with execution metadata awareness."""
    if state.get("needs_clarification"):
        return "clarification"

    # Check execution metadata for potential issues
    exec_metadata = state.get("execution_metadata", {})
    if exec_metadata.get("execution_context", {}).get("failed_tasks", 0) > 0:
        # If tasks failed, might need clarification
        return "clarification"

    return "reviewer"


def enhanced_route_reviewer(state: Dict[str, Any]) -> str:
    """Enhanced routing after reviewer with structured workflow awareness."""
    # Check clarification first
    if state.get("needs_clarification"):
        return "clarification"

    # Check if iteration needed
    review_result = state.get("review_result", {})
    needs_iteration = review_result.get("needs_iteration", False)
    iteration_count = state.get("iteration_count", 0)
    max_iterations = 3

    if needs_iteration and iteration_count < max_iterations:
        # Check if we have structured workflow context for better iteration decisions
        enhanced_metadata = state.get("enhanced_metadata", {})
        if enhanced_metadata.get("structured_workflow"):
            # For structured workflows, be more conservative with iterations
            # since the structured approach typically produces better initial results
            if iteration_count < 2:  # Only allow 1 iteration for structured workflows
                return "executor"

        return "executor"

    # Done - format response
    return "format_response"


def clarification_node(state: Dict[str, Any]) -> Dict[str, Any]:
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
        "Please provide your answers to continue.",
    ]

    clarification_output = "\n".join(output_lines)

    return {
        "needs_clarification": True,
        "status": "paused",
        "clarification_output": clarification_output,
        "clarification_from": from_node,
    }
