"""Workflow context managers - simple context hierarchy."""

from contextlib import contextmanager
from typing import Optional, List
from vivek.agentic_context.core.context_manager import ContextManager
from vivek.agentic_context.config import Config


class ContextWorkflow:
    """Entry point for context tracking in workflows."""

    def __init__(self, config: Optional[Config] = None):
        """Initialize workflow with optional config."""
        self.manager = ContextManager(config or Config.default())

    @contextmanager
    def session(self, session_id: str, original_ask: str, high_level_plan: str):
        """Create session context."""
        self.manager.create_session(session_id, original_ask, high_level_plan)
        try:
            yield SessionContext(self.manager)
        finally:
            pass

    def clear(self):
        """Clear all context."""
        self.manager.clear()


class SessionContext:
    """Session-level context manager."""

    def __init__(self, manager: ContextManager):
        """Initialize with manager."""
        self.manager = manager

    @contextmanager
    def activity(
        self,
        activity_id: str,
        description: str,
        mode: str,
        component: str,
        planner_analysis: str,
        tags: Optional[List[str]] = None,
    ):
        """Create activity context."""
        session = self.manager.storage.get_current_session()
        if not session:
            raise ValueError("No active session")

        tags = tags or []
        self.manager.create_activity(
            activity_id, session.session_id, description, tags, mode, component, planner_analysis
        )

        try:
            yield ActivityContext(self.manager)
        finally:
            pass


class ActivityContext:
    """Activity-level context manager."""

    def __init__(self, manager: ContextManager):
        """Initialize with manager."""
        self.manager = manager

    @contextmanager
    def task(self, description: str, tags: Optional[List[str]] = None):
        """Create task context."""
        activity = self.manager.storage.get_current_activity()
        if not activity:
            raise ValueError("No active activity")

        tags = tags or []
        task_id = f"task_{len(self.manager.storage.tasks) + 1:03d}"
        self.manager.create_task(task_id, activity.activity_id, description, tags)

        try:
            yield TaskContext(self.manager)
        finally:
            pass


class TaskContext:
    """Task-level context manager."""

    def __init__(self, manager: ContextManager):
        """Initialize with manager."""
        self.manager = manager

    def build_prompt(self, include_history: bool = True) -> str:
        """Build prompt for current task."""
        return self.manager.build_prompt(include_history)

    def record_action(self, content: str):
        """Record action taken."""
        task = self.manager.get_current_task()
        if task:
            self.manager.record_action(content, task.tags)

    def record_decision(self, content: str):
        """Record decision made."""
        task = self.manager.get_current_task()
        if task:
            self.manager.record_decision(content, task.tags)

    def record_learning(self, content: str):
        """Record learning."""
        task = self.manager.get_current_task()
        if task:
            self.manager.record_learning(content, task.tags)

    def set_result(self, result: str):
        """Set task result."""
        task = self.manager.get_current_task()
        if task:
            self.manager.complete_task(task.task_id, result)
            self.manager.record_result(result, task.tags)
