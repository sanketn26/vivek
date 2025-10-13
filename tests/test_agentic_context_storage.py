"""
Unit tests for agentic_context.core.context_storage module
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from vivek.agentic_context.core.context_storage import (
    ActivityContext,
    ContextCategory,
    ContextItem,
    ContextStorage,
    SessionContext,
    TaskContext,
)


class TestContextItem:
    """Test ContextItem dataclass"""

    def test_context_item_creation(self):
        """Test creating a ContextItem"""
        item = ContextItem(
            content="test content",
            tags=["test", "example"],
            category=ContextCategory.ACTIONS,
            activity_id="act_001",
            task_id="task_001",
            metadata={"key": "value"},
        )

        assert item.content == "test content"
        assert item.tags == ["test", "example"]
        assert item.category == ContextCategory.ACTIONS
        assert item.activity_id == "act_001"
        assert item.task_id == "task_001"
        assert item.metadata == {"key": "value"}
        assert isinstance(item.timestamp, datetime)


class TestContextStorage:
    """Test ContextStorage functionality"""

    def setup_method(self):
        """Set up fresh ContextStorage for each test"""
        self.storage = ContextStorage()

    def test_initialization(self):
        """Test ContextStorage initialization"""
        assert len(self.storage.sessions) == 0
        assert self.storage.current_session is None
        assert self.storage.current_activity is None
        assert self.storage.current_task is None

        # Check all categories are initialized
        for category in ContextCategory:
            assert category in self.storage.context_db
            assert len(self.storage.context_db[category]) == 0

    def test_create_session(self):
        """Test creating a session"""
        session = self.storage.create_session(
            "session_001",
            "Build auth system",
            "Implement JWT authentication with refresh tokens",
        )

        assert session.session_id == "session_001"
        assert session.original_ask == "Build auth system"
        assert (
            session.high_level_plan
            == "Implement JWT authentication with refresh tokens"
        )
        assert self.storage.current_session == session
        assert "session_001" in self.storage.sessions

    def test_get_session(self):
        """Test retrieving a session"""
        # Create session first
        created_session = self.storage.create_session(
            "session_002", "Test ask", "Test plan"
        )

        # Retrieve it
        retrieved_session = self.storage.get_session("session_002")
        assert retrieved_session == created_session

        # Test non-existent session
        assert self.storage.get_session("nonexistent") is None

    def test_create_activity_without_session(self):
        """Test creating activity without active session fails"""
        with pytest.raises(ValueError, match="No active session"):
            self.storage.create_activity(
                "act_001", "Test activity", ["test"], "coder", "auth", "Test analysis"
            )

    def test_create_activity_with_session(self):
        """Test creating activity with active session"""
        # Create session first
        self.storage.create_session("session_003", "Test", "Plan")

        # Create activity
        activity = self.storage.create_activity(
            "act_001",
            "Implement authentication",
            ["auth", "security"],
            "coder",
            "auth_service",
            "Need to implement JWT token validation",
        )

        assert activity.activity_id == "act_001"
        assert activity.description == "Implement authentication"
        assert activity.tags == ["auth", "security"]
        assert activity.mode == "coder"
        assert activity.component == "auth_service"
        assert activity.planner_analysis == "Need to implement JWT token validation"
        assert self.storage.current_activity == activity
        assert self.storage.current_session is not None
        assert activity in self.storage.current_session.activities

    def test_get_activity(self):
        """Test finding activity across sessions"""
        # Create session and activity
        self.storage.create_session("session_004", "Test", "Plan")
        self.storage.create_activity(
            "act_002", "Test activity", ["test"], "coder", "test", "Analysis"
        )

        # Find activity
        found_activity = self.storage.get_activity("act_002")
        assert found_activity is not None
        assert found_activity.activity_id == "act_002"

        # Test non-existent activity
        assert self.storage.get_activity("nonexistent") is None

    def test_create_task_without_activity(self):
        """Test creating task without active activity fails"""
        self.storage.create_session("session_005", "Test", "Plan")

        with pytest.raises(ValueError, match="No active activity"):
            self.storage.create_task("task_001", "Test task", ["test"])

    def test_create_task_with_activity(self):
        """Test creating task with active activity"""
        # Create session and activity first
        self.storage.create_session("session_006", "Test", "Plan")
        self.storage.create_activity(
            "act_003", "Test activity", ["test"], "coder", "test", "Analysis"
        )

        # Create task
        task = self.storage.create_task(
            "task_001", "Implement feature", ["feature", "implementation"]
        )

        assert task.task_id == "task_001"
        assert task.description == "Implement feature"
        assert task.tags == ["feature", "implementation"]
        assert self.storage.current_task == task
        assert self.storage.current_activity is not None
        assert task in self.storage.current_activity.tasks

    def test_complete_task(self):
        """Test completing a task"""
        # Set up session -> activity -> task
        self.storage.create_session("session_007", "Test", "Plan")
        self.storage.create_activity(
            "act_004", "Test activity", ["test"], "coder", "test", "Analysis"
        )
        task = self.storage.create_task("task_002", "Test task", ["test"])

        # Complete the task
        self.storage.complete_task("task_002", "Task completed successfully")

        # Check current task is marked complete
        assert self.storage.current_task is not None
        assert (
            self.storage.current_task.previous_result == "Task completed successfully"
        )

        # Check task in activity is also marked complete
        assert self.storage.current_activity is not None
        activity_task = self.storage.current_activity.tasks[0]
        assert activity_task.previous_result == "Task completed successfully"

    def test_add_context(self):
        """Test adding context items"""
        # Set up context hierarchy
        self.storage.create_session("session_008", "Test", "Plan")
        self.storage.create_activity(
            "act_005", "Test", ["test"], "coder", "test", "Analysis"
        )
        self.storage.create_task("task_003", "Test task", ["test"])

        # Add context item
        item = self.storage.add_context(
            ContextCategory.ACTIONS,
            "Implemented authentication middleware",
            ["auth", "middleware"],
            activity_id="act_005",
            task_id="task_003",
        )

        assert item.content == "Implemented authentication middleware"
        assert item.tags == ["auth", "middleware"]
        assert item.category == ContextCategory.ACTIONS
        assert item.activity_id == "act_005"
        assert item.task_id == "task_003"
        assert len(self.storage.context_db[ContextCategory.ACTIONS]) == 1

    def test_get_all_context_items(self):
        """Test getting all context items"""
        # Add items to different categories
        self.storage.add_context(ContextCategory.ACTIONS, "Action 1", ["test"])
        self.storage.add_context(ContextCategory.DECISIONS, "Decision 1", ["test"])

        # Get all items
        all_items = self.storage.get_all_context_items()
        assert len(all_items) == 2

        # Get items by category
        action_items = self.storage.get_all_context_items(ContextCategory.ACTIONS)
        assert len(action_items) == 1
        assert action_items[0].content == "Action 1"

    def test_get_context_by_category(self):
        """Test getting context by category"""
        # Add items to different categories
        self.storage.add_context(ContextCategory.ACTIONS, "Action 1", ["test"])
        self.storage.add_context(ContextCategory.DECISIONS, "Decision 1", ["test"])

        actions = self.storage.get_context_by_category(ContextCategory.ACTIONS)
        decisions = self.storage.get_context_by_category(ContextCategory.DECISIONS)

        assert len(actions) == 1
        assert len(decisions) == 1
        assert actions[0].content == "Action 1"
        assert decisions[0].content == "Decision 1"

    def test_get_context_by_tags(self):
        """Test getting context by tags"""
        # Add items with different tags
        self.storage.add_context(
            ContextCategory.ACTIONS, "Auth action", ["auth", "security"]
        )
        self.storage.add_context(
            ContextCategory.DECISIONS, "API decision", ["api", "design"]
        )
        self.storage.add_context(
            ContextCategory.LEARNINGS, "Auth learning", ["auth", "lessons"]
        )

        # Get items by tag
        auth_items = self.storage.get_context_by_tags(["auth"])
        api_items = self.storage.get_context_by_tags(["api"])

        assert len(auth_items) == 2  # Both auth action and auth learning
        assert len(api_items) == 1
        assert api_items[0].content == "API decision"

        # Test no matches
        empty_items = self.storage.get_context_by_tags(["nonexistent"])
        assert len(empty_items) == 0

    def test_get_context_by_activity(self):
        """Test getting context by activity"""
        # Set up hierarchy and add context
        self.storage.create_session("session_009", "Test", "Plan")
        self.storage.create_activity(
            "act_006", "Test", ["test"], "coder", "test", "Analysis"
        )
        self.storage.create_task("task_004", "Test task", ["test"])

        self.storage.add_context(
            ContextCategory.ACTIONS, "Activity action", ["test"], activity_id="act_006"
        )

        # Get context for activity
        activity_context = self.storage.get_context_by_activity("act_006")
        assert len(activity_context) == 1
        assert activity_context[0].content == "Activity action"

    def test_build_hierarchical_context(self):
        """Test building hierarchical context"""
        # Set up complete hierarchy
        self.storage.create_session(
            "session_010",
            "Build payment system",
            "Implement payment processing with multiple providers",
        )
        self.storage.create_activity(
            "act_007",
            "Implement Stripe integration",
            ["stripe", "payment"],
            "coder",
            "payment_service",
            "Need to integrate Stripe API for payment processing",
        )
        self.storage.create_task(
            "task_005", "Create payment handler", ["payment", "handler"]
        )

        context = self.storage.build_hierarchical_context()

        assert "session" in context
        assert "activity" in context
        assert "task" in context

        # Check session data
        assert context["session"]["original_ask"] == "Build payment system"
        assert (
            context["session"]["high_level_plan"]
            == "Implement payment processing with multiple providers"
        )

        # Check activity data
        assert context["activity"]["description"] == "Implement Stripe integration"
        assert context["activity"]["mode"] == "coder"
        assert context["activity"]["component"] == "payment_service"
        assert (
            context["activity"]["planner_analysis"]
            == "Need to integrate Stripe API for payment processing"
        )
        assert context["activity"]["tags"] == ["stripe", "payment"]

        # Check task data
        assert context["task"]["description"] == "Create payment handler"
        assert context["task"]["tags"] == ["payment", "handler"]

    def test_get_statistics(self):
        """Test getting storage statistics"""
        # Initially empty
        stats = self.storage.get_statistics()
        assert stats["total_sessions"] == 0
        assert stats["total_activities"] == 0
        assert stats["total_tasks"] == 0
        # Check specific expected keys that are actually returned by get_statistics()
        expected_keys = [
            "total_sessions",
            "total_activities",
            "total_tasks",
            "session_contexts",
            "activity_contexts",
            "task_contexts",
            "decisions",
            "actions",
            "results",
            "learnings",
        ]

        for key in expected_keys:
            assert key in stats
            assert stats[key] == 0

        # Add some data
        self.storage.create_session("session_011", "Test", "Plan")
        self.storage.create_activity(
            "act_008", "Test", ["test"], "coder", "test", "Analysis"
        )
        self.storage.create_task("task_006", "Test task", ["test"])
        self.storage.add_context(ContextCategory.ACTIONS, "Test action", ["test"])
        self.storage.add_context(ContextCategory.DECISIONS, "Test decision", ["test"])

        stats = self.storage.get_statistics()
        assert stats["total_sessions"] == 1
        assert stats["total_activities"] == 1
        assert stats["total_tasks"] == 1
        assert stats["actions"] == 1
        assert stats["decisions"] == 1

    def test_clear_all(self):
        """Test clearing all context"""
        # Add some data
        self.storage.create_session("session_012", "Test", "Plan")
        self.storage.create_activity(
            "act_009", "Test", ["test"], "coder", "test", "Analysis"
        )
        self.storage.add_context(ContextCategory.ACTIONS, "Test action", ["test"])

        # Verify data exists
        assert len(self.storage.sessions) == 1
        assert len(self.storage.context_db[ContextCategory.ACTIONS]) == 1

        # Clear all
        self.storage.clear_all()

        # Verify everything is cleared
        assert len(self.storage.sessions) == 0
        assert self.storage.current_session is None
        assert self.storage.current_activity is None
        assert self.storage.current_task is None
        for category in ContextCategory:
            assert len(self.storage.context_db[category]) == 0

    def test_thread_safety(self):
        """Test that operations are thread-safe"""
        import threading

        results = []

        def create_session_with_id(session_id):
            session = self.storage.create_session(
                session_id, f"Ask {session_id}", f"Plan {session_id}"
            )
            results.append(session_id)

        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(
                target=create_session_with_id, args=(f"session_{i}",)
            )
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all sessions were created
        assert len(results) == 5
        assert len(self.storage.sessions) == 5

    def test_context_persistence_through_hierarchy_changes(self):
        """Test that context items persist when hierarchy changes"""
        # Create session and add context
        self.storage.create_session("session_013", "Test", "Plan")
        self.storage.add_context(
            ContextCategory.DECISIONS, "Session decision", ["test"]
        )

        # Create activity and add more context
        self.storage.create_activity(
            "act_010", "Test", ["test"], "coder", "test", "Analysis"
        )
        self.storage.add_context(ContextCategory.ACTIONS, "Activity action", ["test"])

        # Create task and add more context
        self.storage.create_task("task_007", "Test task", ["test"])
        self.storage.add_context(ContextCategory.LEARNINGS, "Task learning", ["test"])

        # Verify all context items exist
        assert len(self.storage.context_db[ContextCategory.DECISIONS]) == 1
        assert len(self.storage.context_db[ContextCategory.ACTIONS]) == 1
        assert len(self.storage.context_db[ContextCategory.LEARNINGS]) == 1

        # Change current context
        self.storage.create_activity(
            "act_011", "New activity", ["new"], "coder", "new", "New analysis"
        )
        self.storage.create_task("task_008", "New task", ["new"])

        # Verify old context items still exist
        assert len(self.storage.context_db[ContextCategory.DECISIONS]) == 1
        assert len(self.storage.context_db[ContextCategory.ACTIONS]) == 1
        assert len(self.storage.context_db[ContextCategory.LEARNINGS]) == 1
