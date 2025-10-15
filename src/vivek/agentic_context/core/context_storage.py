"""
Context Storage System with 3-layer hierarchy and 7-category storage
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import threading


class ContextCategory(Enum):
    """7 categories for context storage"""

    SESSION = "session"
    ACTIVITY = "activity"
    TASK = "task"
    ACTIONS = "actions"
    DECISIONS = "decisions"
    LEARNINGS = "learnings"
    RESULTS = "results"


@dataclass
class ContextItem:
    """Base context item with metadata"""

    content: str
    tags: List[str]
    category: ContextCategory
    timestamp: datetime = field(default_factory=datetime.now)
    activity_id: Optional[str] = None
    task_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[Any] = None  # For semantic retrieval


@dataclass
class TaskContext:
    """Task-level context (most specific)"""

    task_id: str
    description: str
    tags: List[str]
    previous_result: Optional[str] = None
    files_involved: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActivityContext:
    """Activity-level context (mid-level)"""

    activity_id: str
    description: str
    tags: List[str]
    mode: str  # coder, architect, sdet, peer
    component: str
    planner_analysis: str
    tasks: List[TaskContext] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SessionContext:
    """Session-level context (highest level)"""

    session_id: str
    original_ask: str
    high_level_plan: str
    activities: List[ActivityContext] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextStorage:
    """
    Manages 3-layer hierarchical context and 7-category historical storage with thread-safe operations
    """

    def __init__(self):
        # Thread safety
        self._lock = threading.RLock()

        # 3-layer hierarchy
        self.sessions: Dict[str, SessionContext] = {}
        self.current_session: Optional[SessionContext] = None
        self.current_activity: Optional[ActivityContext] = None
        self.current_task: Optional[TaskContext] = None

        # 7-category historical storage
        self.context_db: Dict[ContextCategory, List[ContextItem]] = {
            ContextCategory.SESSION: [],
            ContextCategory.ACTIVITY: [],
            ContextCategory.TASK: [],
            ContextCategory.ACTIONS: [],
            ContextCategory.DECISIONS: [],
            ContextCategory.LEARNINGS: [],
            ContextCategory.RESULTS: [],
        }

    # ==================== Session Management ====================

    def create_session(
        self, session_id: str, original_ask: str, high_level_plan: str, **metadata
    ) -> SessionContext:
        """Create new session context"""
        with self._lock:
            session = SessionContext(
                session_id=session_id,
                original_ask=original_ask,
                high_level_plan=high_level_plan,
                metadata=metadata,
            )
            self.sessions[session_id] = session
            self.current_session = session
            return session

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        """Retrieve session by ID"""
        return self.sessions.get(session_id)

    # ==================== Activity Management ====================

    def create_activity(
        self,
        activity_id: str,
        description: str,
        tags: List[str],
        mode: str,
        component: str,
        planner_analysis: str,
        **metadata,
    ) -> ActivityContext:
        """Create new activity under current session"""
        with self._lock:
            if not self.current_session:
                raise ValueError("No active session. Create session first.")

            activity = ActivityContext(
                activity_id=activity_id,
                description=description,
                tags=tags,
                mode=mode,
                component=component,
                planner_analysis=planner_analysis,
                metadata=metadata,
            )
            self.current_session.activities.append(activity)
            self.current_activity = activity
            return activity

    def get_activity(self, activity_id: str) -> Optional[ActivityContext]:
        """Find activity across all sessions"""
        for session in self.sessions.values():
            for activity in session.activities:
                if activity.activity_id == activity_id:
                    return activity
        return None

    # ==================== Task Management ====================

    def create_task(
        self, task_id: str, description: str, tags: List[str], **metadata
    ) -> TaskContext:
        """Create new task under current activity"""
        with self._lock:
            if not self.current_activity:
                raise ValueError("No active activity. Create activity first.")

            task = TaskContext(
                task_id=task_id, description=description, tags=tags, metadata=metadata
            )
            self.current_activity.tasks.append(task)
            self.current_task = task
            return task

    def complete_task(self, task_id: str, result: str):
        """Mark task as complete with result"""
        with self._lock:
            task = self.current_task
            if task and task.task_id == task_id:
                task.previous_result = result
            else:
                # Find task in current activity
                if self.current_activity:
                    for t in self.current_activity.tasks:
                        if t.task_id == task_id:
                            t.previous_result = result
                            break

    # ==================== Context DB Management ====================

    def add_context(
        self,
        category: ContextCategory,
        content: str,
        tags: List[str],
        embedding: Optional[Any] = None,
        **metadata,
    ) -> ContextItem:
        """Add item to historical context DB"""
        with self._lock:
            item = ContextItem(
                content=content,
                tags=tags,
                category=category,
                activity_id=(
                    self.current_activity.activity_id if self.current_activity else None
                ),
                task_id=self.current_task.task_id if self.current_task else None,
                metadata=metadata,
                embedding=embedding,
            )
            self.context_db[category].append(item)
            return item

    def get_all_context_items(
        self, category: Optional[ContextCategory] = None
    ) -> List[ContextItem]:
        """Get all context items, optionally filtered by category"""
        if category:
            return self.context_db[category]

        # Return all items from all categories
        all_items = []
        for items in self.context_db.values():
            all_items.extend(items)
        return all_items

    def get_context_by_category(self, category: ContextCategory) -> List[ContextItem]:
        """Get all context items for a specific category"""
        return self.context_db[category].copy()

    def get_context_by_tags(self, tags: List[str]) -> List[ContextItem]:
        """Get all context items that match any of the provided tags"""
        if not tags:
            return []

        matching_items = []
        for items in self.context_db.values():
            for item in items:
                if any(tag in item.tags for tag in tags):
                    matching_items.append(item)
        return matching_items

    def get_context_by_activity(self, activity_id: str) -> List[ContextItem]:
        """Get all context items related to specific activity"""
        result = []
        for items in self.context_db.values():
            for item in items:
                if item.activity_id == activity_id:
                    result.append(item)
        return result

    # ==================== Context Retrieval for Prompt ====================

    def get_session_context(self) -> Optional[SessionContext]:
        """Get current session context"""
        return self.current_session

    def get_activity_context(self) -> Optional[ActivityContext]:
        """Get current activity context"""
        return self.current_activity

    def get_task_context(self) -> Optional[TaskContext]:
        """Get current task context"""
        return self.current_task

    def build_hierarchical_context(self) -> Dict[str, Any]:
        """Build complete hierarchical context for current state"""
        return {
            "session": {
                "original_ask": (
                    self.current_session.original_ask if self.current_session else None
                ),
                "high_level_plan": (
                    self.current_session.high_level_plan
                    if self.current_session
                    else None
                ),
            },
            "activity": {
                "description": (
                    self.current_activity.description if self.current_activity else None
                ),
                "mode": self.current_activity.mode if self.current_activity else None,
                "component": (
                    self.current_activity.component if self.current_activity else None
                ),
                "planner_analysis": (
                    self.current_activity.planner_analysis
                    if self.current_activity
                    else None
                ),
                "tags": self.current_activity.tags if self.current_activity else [],
            },
            "task": {
                "description": (
                    self.current_task.description if self.current_task else None
                ),
                "previous_result": (
                    self.current_task.previous_result if self.current_task else None
                ),
                "tags": self.current_task.tags if self.current_task else [],
            },
        }

    # ==================== Utility Methods ====================

    def clear_all(self):
        """Clear all stored context (use with caution)"""
        with self._lock:
            self.sessions.clear()
            self.current_session = None
            self.current_activity = None
            self.current_task = None
            for category in self.context_db:
                self.context_db[category].clear()

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics about stored context"""
        return {
            "total_sessions": len(self.sessions),
            "total_activities": sum(len(s.activities) for s in self.sessions.values()),
            "total_tasks": sum(
                len(a.tasks) for s in self.sessions.values() for a in s.activities
            ),
            "session_contexts": len(self.context_db[ContextCategory.SESSION]),
            "activity_contexts": len(self.context_db[ContextCategory.ACTIVITY]),
            "task_contexts": len(self.context_db[ContextCategory.TASK]),
            "decisions": len(self.context_db[ContextCategory.DECISIONS]),
            "actions": len(self.context_db[ContextCategory.ACTIONS]),
            "results": len(self.context_db[ContextCategory.RESULTS]),
            "learnings": len(self.context_db[ContextCategory.LEARNINGS]),
        }
