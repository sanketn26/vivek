from enum import Enum
from typing import Any, Dict, List


class MessageType(Enum):
    """Standard message types from nodes to orchestrator."""

    EXECUTION_COMPLETE = "execution_complete"
    CLARIFICATION_NEEDED = "clarification_needed"
    ERROR = "error"
    PARTIAL_RESULT = "partial_result"


def execution_complete(output: Any, from_node: str, **metadata) -> Dict[str, Any]:
    """Create execution complete message.

    Args:
        output: The result/output from the node
        from_node: Identifier of the node sending message
        **metadata: Additional context (files_modified, tests_run, etc.)

    Returns:
        Structured message dict
    """
    return {
        "type": MessageType.EXECUTION_COMPLETE.value,
        "payload": {"output": output},
        "from_node": from_node,
        "metadata": metadata,
    }


def clarification_needed(
    questions: List[Dict[str, Any]], from_node: str, **context
) -> Dict[str, Any]:
    """Create clarification needed message.

    Args:
        questions: List of question dicts with 'question', 'type', 'options', etc.
        from_node: Identifier of the node requesting clarification
        **context: Additional context (partial_work, analysis, etc.)

    Returns:
        Structured message dict
    """
    return {
        "type": MessageType.CLARIFICATION_NEEDED.value,
        "payload": {"questions": questions},
        "from_node": from_node,
        "metadata": context,
    }


def error_occurred(error: str, from_node: str, **context) -> Dict[str, Any]:
    """Create error message.

    Args:
        error: Error description
        from_node: Identifier of the node where error occurred
        **context: Additional context (stack_trace, task_plan, etc.)

    Returns:
        Structured message dict
    """
    return {
        "type": MessageType.ERROR.value,
        "payload": {"error": error},
        "from_node": from_node,
        "metadata": context,
    }


def partial_result(
    output: Any, from_node: str, progress: float = 0.0, **context
) -> Dict[str, Any]:
    """Create partial result message (for streaming/progress updates).

    Args:
        output: Partial output/result
        from_node: Identifier of the node sending message
        progress: Progress percentage (0.0 to 1.0)
        **context: Additional context

    Returns:
        Structured message dict
    """
    return {
        "type": MessageType.PARTIAL_RESULT.value,
        "payload": {"output": output, "progress": progress},
        "from_node": from_node,
        "metadata": context,
    }
