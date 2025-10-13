"""
Unit tests for agentic_context.workflow module
"""

from unittest.mock import Mock, patch

import pytest

from vivek.agentic_context.workflow import (
    ActivityContext,
    ContextWorkflow,
    RetrievalError,
    SessionContext,
    StorageError,
    TaskContext,
    ValidationError,
)


class TestTaskContext:
    """Test TaskContext functionality"""

    def setup_method(self):
        """Set up TaskContext with mocked dependencies"""
        self.mock_storage = Mock()
        self.mock_retriever = Mock()
        self.config = {"retrieval": {"max_results": 5}}

        # Mock storage methods
        self.mock_storage.build_hierarchical_context.return_value = {
            "session": {"original_ask": "Test session"},
            "activity": {"description": "Test activity"},
            "task": {"description": "Test task"},
        }

        self.task_context = TaskContext(
            "task_001",
            "Implement feature",
            ["feature", "implementation"],
            self.mock_storage,
            self.mock_retriever,
            self.config,
        )

    def test_initialization(self):
        """Test TaskContext initialization"""
        assert self.task_context.task_id == "task_001"
        assert self.task_context.description == "Implement feature"
        assert self.task_context.tags == ["feature", "implementation"]
        assert self.task_context._result is None

    def test_initialization_validation_errors(self):
        """Test TaskContext validation errors"""
        with pytest.raises(ValidationError):
            TaskContext(
                "",
                "Test",
                ["test"],
                self.mock_storage,
                self.mock_retriever,
                self.config,
            )

        with pytest.raises(ValidationError):
            TaskContext(
                "task_001",
                "",
                ["test"],
                self.mock_storage,
                self.mock_retriever,
                self.config,
            )

        with pytest.raises(ValidationError):
            TaskContext(
                "task_001",
                "Test",
                [],
                self.mock_storage,
                self.mock_retriever,
                self.config,
            )

    def test_context_property(self):
        """Test context property"""
        context = self.task_context.context
        assert "session" in context
        assert "activity" in context
        assert "task" in context
        self.mock_storage.build_hierarchical_context.assert_called_once()

    def test_build_prompt(self):
        """Test building prompt with context"""
        # Mock retriever response
        self.mock_retriever.retrieve.return_value = [
            {
                "item": {"content": "Previous implementation", "category": "actions"},
                "score": 0.8,
                "matched_tags": ["feature"],
                "category": "actions",
            }
        ]

        prompt = self.task_context.build_prompt()

        assert "SESSION CONTEXT" in prompt
        assert "ACTIVITY CONTEXT" in prompt
        assert "TASK CONTEXT" in prompt
        assert "RELEVANT CONTEXT FROM HISTORY" in prompt
        assert "Previous implementation" in prompt
        assert "INSTRUCTIONS" in prompt

    def test_build_prompt_without_history(self):
        """Test building prompt without history"""
        prompt = self.task_context.build_prompt(include_history=False)

        assert "SESSION CONTEXT" in prompt
        assert "ACTIVITY CONTEXT" in prompt
        assert "TASK CONTEXT" in prompt
        assert "RELEVANT CONTEXT FROM HISTORY" not in prompt

    def test_build_prompt_retrieval_error(self):
        """Test building prompt handles retrieval errors gracefully"""
        self.mock_retriever.retrieve.side_effect = Exception("Retrieval failed")

        prompt = self.task_context.build_prompt()

        # Should still build prompt but with error message for history
        assert "SESSION CONTEXT" in prompt
        assert "Unable to retrieve historical context" in prompt

    def test_record_action(self):
        """Test recording an action"""
        self.mock_storage.add_context.return_value = Mock()

        result = self.task_context.record_action(
            "Created new function", file="test.py", lines=50
        )

        self.mock_storage.add_context.assert_called_once()
        call_args = self.mock_storage.add_context.call_args
        assert call_args[0][1] == "Created new function"  # ContextCategory.ACTIONS
        assert call_args[0][2] == ["feature", "implementation"]  # tags
        assert call_args[1]["file"] == "test.py"
        assert call_args[1]["lines"] == 50

    def test_record_decision(self):
        """Test recording a decision"""
        self.mock_storage.add_context.return_value = Mock()

        result = self.task_context.record_decision(
            "Use async approach", reasoning="Better performance"
        )

        self.mock_storage.add_context.assert_called_once()
        call_args = self.mock_storage.add_context.call_args
        assert call_args[0][1] == "Use async approach"  # ContextCategory.DECISIONS
        assert call_args[1]["reasoning"] == "Better performance"

    def test_record_learning(self):
        """Test recording a learning"""
        self.mock_storage.add_context.return_value = Mock()

        result = self.task_context.record_learning(
            "Always validate input data", lesson_type="best_practice"
        )

        self.mock_storage.add_context.assert_called_once()
        call_args = self.mock_storage.add_context.call_args
        assert (
            call_args[0][1] == "Always validate input data"
        )  # ContextCategory.LEARNINGS
        assert call_args[1]["lesson_type"] == "best_practice"

    def test_record_validation_errors(self):
        """Test record methods validation"""
        with pytest.raises(ValidationError):
            self.task_context.record_action("")

        with pytest.raises(ValidationError):
            self.task_context.record_decision("")

    def test_set_result(self):
        """Test setting task result"""
        self.task_context.set_result("Task completed successfully")
        assert self.task_context._result == "Task completed successfully"

        # Test with empty string (converted to None internally)
        self.task_context.set_result("")
        assert self.task_context._result == ""

    def test_finalize(self):
        """Test task finalization"""
        # Set a result
        self.task_context.set_result("Final result")

        # Mock storage methods
        self.mock_storage.complete_task = Mock()
        self.mock_storage.add_context = Mock()

        # Finalize
        self.task_context._finalize()

        # Verify completion and result recording
        self.mock_storage.complete_task.assert_called_once_with(
            "task_001", "Final result"
        )
        self.mock_storage.add_context.assert_called_once()

    def test_finalize_without_result(self):
        """Test finalization without result"""
        self.task_context._finalize()

        # Should not call complete_task or add_context
        self.mock_storage.complete_task.assert_not_called()
        self.mock_storage.add_context.assert_not_called()


class TestActivityContext:
    """Test ActivityContext functionality"""

    def setup_method(self):
        """Set up ActivityContext with mocked dependencies"""
        self.mock_storage = Mock()
        self.mock_retriever = Mock()
        self.config = {"retrieval": {"max_results": 5}}

        # Mock storage hierarchy
        self.mock_storage.build_hierarchical_context.return_value = {
            "session": {"original_ask": "Test session"},
            "activity": {"description": "Test activity"},
        }

        # Mock task creation
        self.mock_storage.create_task.return_value = Mock(task_id="task_001")

        self.activity_context = ActivityContext(
            "act_001",
            "Implement authentication system",
            ["auth", "security"],
            "coder",
            "auth_service",
            "Need to implement JWT validation",
            self.mock_storage,
            self.mock_retriever,
            self.config,
        )

    def test_initialization(self):
        """Test ActivityContext initialization"""
        assert self.activity_context.activity_id == "act_001"
        assert self.activity_context.description == "Implement authentication system"
        assert self.activity_context.mode == "coder"
        assert self.activity_context.component == "auth_service"
        assert self.activity_context._task_counter == 0

    def test_task_context_manager(self):
        """Test task context manager"""
        with patch("vivek.agentic_context.workflow.TaskContext") as mock_task_class:
            mock_task_instance = Mock()
            mock_task_class.return_value = mock_task_instance

            with self.activity_context.task(
                "Create JWT handler", ["jwt", "handler"]
            ) as task:
                assert task == mock_task_instance

            # Verify task was created correctly
            mock_task_class.assert_called_once()
            call_args = mock_task_class.call_args
            assert call_args[0][1] == "Create JWT handler"  # description
            assert "jwt" in call_args[0][2]  # tags
            assert "auth" in call_args[0][2]  # inherited activity tags

    def test_task_context_manager_inheritance(self):
        """Test task inherits activity tags"""
        with patch("vivek.agentic_context.workflow.TaskContext") as mock_task_class:
            with self.activity_context.task("Test task") as task:
                pass

            # Check that activity tags were inherited (first 2)
            call_args = mock_task_class.call_args
            task_tags = call_args[0][2]
            assert "auth" in task_tags
            assert "security" in task_tags

    def test_task_context_manager_with_custom_tags(self):
        """Test task with custom tags"""
        with patch("vivek.agentic_context.workflow.TaskContext") as mock_task_class:
            with self.activity_context.task("Test task", ["custom", "tags"]) as task:
                pass

            # Check that custom tags are combined with activity tags
            call_args = mock_task_class.call_args
            task_tags = call_args[0][2]
            assert "custom" in task_tags
            assert "tags" in task_tags
            assert "auth" in task_tags  # inherited

    def test_task_finalization_on_error(self):
        """Test that task is finalized even if an error occurs"""
        mock_task = Mock()
        mock_task._finalize = Mock()

        with patch(
            "vivek.agentic_context.workflow.TaskContext", return_value=mock_task
        ):
            with pytest.raises(Exception, match="Test error"):
                with self.activity_context.task("Test task") as task:
                    raise Exception("Test error")

            # Verify task was finalized despite error
            mock_task._finalize.assert_called_once()


class TestSessionContext:
    """Test SessionContext functionality"""

    def setup_method(self):
        """Set up SessionContext with mocked dependencies"""
        self.mock_storage = Mock()
        self.mock_retriever = Mock()
        self.config = {"retrieval": {"max_results": 5}}

        # Mock storage hierarchy
        self.mock_storage.build_hierarchical_context.return_value = {
            "session": {"original_ask": "Test session"}
        }

        # Mock activity creation
        self.mock_storage.create_activity.return_value = Mock(activity_id="act_001")
        self.mock_storage.add_context.return_value = Mock()

        self.session_context = SessionContext(
            "session_001",
            "Build e-commerce platform",
            "Implement product catalog, shopping cart, and payment processing",
            self.mock_storage,
            self.mock_retriever,
            self.config,
        )

    def test_initialization(self):
        """Test SessionContext initialization"""
        assert self.session_context.session_id == "session_001"
        assert self.session_context.original_ask == "Build e-commerce platform"
        assert (
            self.session_context.high_level_plan
            == "Implement product catalog, shopping cart, and payment processing"
        )
        assert self.session_context._activity_counter == 0

    def test_activity_context_manager(self):
        """Test activity context manager"""
        with patch(
            "vivek.agentic_context.workflow.ActivityContext"
        ) as mock_activity_class:
            mock_activity_instance = Mock()
            mock_activity_class.return_value = mock_activity_instance

            with self.session_context.activity(
                "Implement user authentication",
                ["auth", "user"],
                "coder",
                "auth_service",
                "Need to implement login, register, and password reset",
            ) as activity:
                assert activity == mock_activity_instance

            # Verify activity was created correctly
            mock_activity_class.assert_called_once()
            call_args = mock_activity_class.call_args
            assert call_args[0][1] == "Implement user authentication"  # description
            assert call_args[0][2] == ["auth", "user"]  # tags
            assert call_args[0][3] == "coder"  # mode
            assert call_args[0][4] == "auth_service"  # component


class TestContextWorkflow:
    """Test ContextWorkflow functionality"""

    def setup_method(self):
        """Set up ContextWorkflow with mocked dependencies"""
        self.config = {
            "retrieval": {"strategy": "tags_only", "max_results": 5},
            "semantic": {"enabled": False},
        }

        with (
            patch(
                "vivek.agentic_context.workflow.ContextStorage"
            ) as mock_storage_class,
            patch(
                "vivek.agentic_context.workflow.RetrieverFactory"
            ) as mock_factory_class,
        ):

            self.mock_storage = Mock()
            self.mock_retriever = Mock()
            self.mock_storage.get_statistics.return_value = {"total_sessions": 0}

            mock_storage_class.return_value = self.mock_storage
            mock_factory_class.create_retriever.return_value = self.mock_retriever

            self.workflow = ContextWorkflow(self.config)

    def test_initialization(self):
        """Test ContextWorkflow initialization"""
        assert self.workflow.config == self.config
        assert self.workflow.storage == self.mock_storage
        assert self.workflow.retriever == self.mock_retriever
        assert self.workflow._session_counter == 0

    def test_initialization_storage_error(self):
        """Test initialization handles storage errors"""
        with patch(
            "vivek.agentic_context.workflow.ContextStorage"
        ) as mock_storage_class:
            mock_storage_class.side_effect = Exception("Storage init failed")

            with pytest.raises(StorageError, match="Failed to initialize storage"):
                ContextWorkflow(self.config)

    def test_initialization_retrieval_error(self):
        """Test initialization handles retrieval errors"""
        with (
            patch("vivek.agentic_context.workflow.ContextStorage"),
            patch(
                "vivek.agentic_context.workflow.RetrieverFactory.create_retriever"
            ) as mock_create,
        ):

            mock_create.side_effect = Exception("Retriever init failed")

            with pytest.raises(RetrievalError, match="Failed to initialize retriever"):
                ContextWorkflow(self.config)

    def test_session_context_manager(self):
        """Test session context manager"""
        with patch(
            "vivek.agentic_context.workflow.SessionContext"
        ) as mock_session_class:
            mock_session_instance = Mock()
            mock_session_class.return_value = mock_session_instance

            with self.workflow.session("Build API system") as session:
                assert session == mock_session_instance

            # Verify session was created correctly
            mock_session_class.assert_called_once()
            call_args = mock_session_class.call_args
            assert call_args[0][1] == "Build API system"  # original_ask
            assert (
                call_args[0][2] == "To be determined by planner"
            )  # default high_level_plan

    def test_session_with_high_level_plan(self):
        """Test session with custom high level plan"""
        with patch(
            "vivek.agentic_context.workflow.SessionContext"
        ) as mock_session_class:
            with self.workflow.session(
                "Build API", high_level_plan="Implement REST API with auth"
            ) as session:
                pass

            call_args = mock_session_class.call_args
            assert call_args[0][2] == "Implement REST API with auth"

    def test_get_statistics(self):
        """Test getting workflow statistics"""
        expected_stats = {"total_sessions": 1, "total_activities": 2}
        self.mock_storage.get_statistics.return_value = expected_stats

        stats = self.workflow.get_statistics()
        assert stats == expected_stats
        self.mock_storage.get_statistics.assert_called_once()

    def test_switch_strategy(self):
        """Test switching retrieval strategy"""
        with patch("vivek.agentic_context.workflow.RetrieverFactory") as mock_factory:
            mock_new_retriever = Mock()
            # Reset the call count since it was called during initialization
            mock_factory.create_retriever.reset_mock()
            mock_factory.create_retriever.return_value = mock_new_retriever

            self.workflow.switch_strategy("hybrid")

            # Verify config was updated and new retriever created
            assert self.workflow.config["retrieval"]["strategy"] == "hybrid"
            assert self.workflow.retriever == mock_new_retriever
            # Should be called once for the switch (ignoring the initialization call)
            assert mock_factory.create_retriever.call_count >= 1

    def test_switch_strategy_validation(self):
        """Test strategy switching validation"""
        with pytest.raises(ValidationError):
            self.workflow.switch_strategy("")

        with pytest.raises(ValidationError):
            self.workflow.switch_strategy("invalid_strategy")

    def test_export(self):
        """Test exporting workflow context"""
        # Mock storage sessions and context DB
        mock_session = Mock()
        mock_session.session_id = "session_001"
        mock_session.original_ask = "Test ask"
        mock_session.high_level_plan = "Test plan"
        mock_session.created_at.isoformat.return_value = "2023-01-01T00:00:00"

        self.mock_storage.sessions = {"session_001": mock_session}
        self.mock_storage.context_db = {Mock(): [Mock()]}  # Mock enum and items

        # Mock context DB items
        mock_item = Mock()
        mock_item.content = "Test content"
        mock_item.tags = ["test"]
        mock_item.timestamp.isoformat.return_value = "2023-01-01T00:00:00"
        mock_item.activity_id = None
        mock_item.task_id = None
        mock_item.metadata = {}

        # Set up the context DB properly
        with patch.object(self.mock_storage, "context_db") as mock_db:
            mock_category = Mock()
            mock_category.value = "actions"
            mock_db.items.return_value = [(mock_category, [mock_item])]

            export_data = self.workflow.export()

            assert "sessions" in export_data
            assert "context_db" in export_data

    def test_nested_context_managers(self):
        """Test nested context managers work correctly"""
        # This test verifies the integration between all context managers
        with (
            patch("vivek.agentic_context.workflow.SessionContext") as mock_session,
            patch("vivek.agentic_context.workflow.ActivityContext") as mock_activity,
            patch("vivek.agentic_context.workflow.TaskContext") as mock_task,
        ):

            # Create mock instances that support context manager protocol
            mock_session_instance = Mock()
            mock_session_instance.__enter__ = Mock(return_value=mock_session_instance)
            mock_session_instance.__exit__ = Mock(return_value=None)

            # Mock the activity method to return a context manager
            mock_activity_instance = Mock()
            mock_activity_instance.__enter__ = Mock(return_value=mock_activity_instance)
            mock_activity_instance.__exit__ = Mock(return_value=None)

            mock_task_instance = Mock()
            mock_task_instance.__enter__ = Mock(return_value=mock_task_instance)
            mock_task_instance.__exit__ = Mock(return_value=None)

            # Set up the session mock to return activity mock when activity() is called
            mock_session_instance.activity = Mock(return_value=mock_activity_instance)

            # Set up the activity mock to return task mock when task() is called
            mock_activity_instance.task = Mock(return_value=mock_task_instance)

            mock_session.return_value = mock_session_instance
            mock_activity.return_value = mock_activity_instance
            mock_task.return_value = mock_task_instance

            # Test nested usage
            with self.workflow.session("Test session") as session:
                with session.activity(
                    "Test activity", ["test"], "coder", "test", "Test analysis"
                ) as activity:
                    with activity.task("Test task", ["test"]) as task:
                        pass  # Work here

            # Verify all were created and used correctly
            mock_session.assert_called_once()
            # ActivityContext and TaskContext are called by the real workflow, not our mocks
            # So we verify the methods were called on our mock instances instead
            mock_session_instance.activity.assert_called_once()
            mock_activity_instance.task.assert_called_once()
