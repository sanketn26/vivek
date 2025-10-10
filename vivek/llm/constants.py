"""Constants for LLM executor system to eliminate magic strings."""

from enum import Enum


class TaskStatus(Enum):
    """File status values for work items."""

    NEW = "new"
    EXISTING = "existing"
    MODIFIED = "modified"


class Priority(Enum):
    """Priority levels for tasks."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class Mode(Enum):
    """Execution modes for different types of work."""

    CODER = "coder"
    ARCHITECT = "architect"
    PEER = "peer"
    SDET = "sdet"


class TokenLimits:
    """Token limits for different contexts."""

    MAX_CONTEXT_TOKENS = 3000
    MAX_OUTPUT_TOKENS = 1500
    PLANNER_CONTEXT_TOKENS = 2000


class CompressionStrategy:
    """Context compression strategies."""

    SELECTIVE = "selective"
    SUMMARY = "summary"
    RECENT = "recent"


class WorkItemKeys:
    """Standard keys used in work item dictionaries."""

    MODE = "mode"
    FILE_PATH = "file_path"
    FILE_STATUS = "file_status"
    DESCRIPTION = "description"
    DEPENDENCIES = "dependencies"


class TaskPlanKeys:
    """Standard keys used in task plan dictionaries."""

    DESCRIPTION = "description"
    MODE = "mode"
    WORK_ITEMS = "work_items"
    PRIORITY = "priority"


class MessageTypes:
    """Message type constants for consistency."""

    EXECUTION_COMPLETE = "execution_complete"
    CLARIFICATION_NEEDED = "clarification_needed"
    ERROR = "error"


class OutputFormatMarkers:
    """Markers used in prompt output formatting."""

    OUTPUT_FORMAT = "OUTPUT FORMAT"
    WORK_ITEM_HEADER = "### Work Item [N]: [file_path]"
    SUB_TASKS_HEADER = "**Sub-tasks:**"
    IMPLEMENTATION_HEADER = "**Implementation:**"
    STATUS_HEADER = "**Status:**"
    COMPLETE_MARKER = "☑"
    NEW_MARKER = "[NEW]"
    MODIFY_MARKER = "[MODIFY]"


class PromptSections:
    """Standard sections used in prompts."""

    MODE_INSTRUCTION = "MODE_INSTRUCTION"
    CONTEXT = "CONTEXT"
    TASK = "TASK"
    WORK_ITEMS = "WORK_ITEMS"
    PROCESS = "PROCESS"
    OUTPUT_FORMAT = "OUTPUT_FORMAT"


# Backwards compatibility - provide string values for existing code
# These can be gradually removed as code is refactored
FILE_STATUS_NEW = TaskStatus.NEW.value
FILE_STATUS_EXISTING = TaskStatus.EXISTING.value
FILE_STATUS_MODIFIED = TaskStatus.MODIFIED.value

PRIORITY_LOW = Priority.LOW.value
PRIORITY_NORMAL = Priority.NORMAL.value
PRIORITY_HIGH = Priority.HIGH.value
PRIORITY_URGENT = Priority.URGENT.value

MODE_CODER = Mode.CODER.value
MODE_ARCHITECT = Mode.ARCHITECT.value
MODE_PEER = Mode.PEER.value
MODE_SDET = Mode.SDET.value
