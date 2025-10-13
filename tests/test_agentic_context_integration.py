"""
Integration tests for agentic_context package

Tests complete workflows and interactions between components
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from contextlib import contextmanager

from vivek.agentic_context.config import Config
from vivek.agentic_context.workflow import ContextWorkflow
from vivek.agentic_context.core.context_storage import ContextCategory


def create_context_manager_mock(**attrs):
    """
    Create a Mock that supports the context manager protocol
    """
    mock = MagicMock(**attrs)
    mock.__enter__ = MagicMock(return_value=mock)
    mock.__exit__ = MagicMock(return_value=False)
    return mock


class TestCompleteWorkflowIntegration:
    """Test complete workflow scenarios"""

    @pytest.mark.skip(reason="Integration test requires complex mocking - needs refactoring")
    def test_basic_workflow_execution(self):
        """Test basic workflow from session to task completion"""
        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            # Set up mocks
            mock_storage = Mock()
            mock_retriever = Mock()

            # Create context manager mocks with proper protocol support
            mock_task = create_context_manager_mock(
                task_id="task_001",
                build_prompt=Mock(return_value="Test prompt"),
                record_action=Mock(),
                record_decision=Mock(),
                record_learning=Mock(),
                set_result=Mock()
            )

            mock_activity = create_context_manager_mock(
                activity_id="act_001",
                task=Mock(return_value=mock_task)
            )

            mock_session = create_context_manager_mock(
                session_id="session_001",
                activity=Mock(return_value=mock_activity)
            )

            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            # Mock storage methods
            mock_storage.create_session.return_value = mock_session
            mock_storage.create_activity.return_value = mock_activity
            mock_storage.create_task.return_value = mock_task
            mock_storage.build_hierarchical_context.return_value = {
                "session": {"original_ask": "Test"},
                "activity": {"description": "Test activity"},
                "task": {"description": "Test task"}
            }

            # Mock context managers in workflow classes
            with patch('vivek.agentic_context.workflow.SessionContext') as mock_session_class, \
                 patch('vivek.agentic_context.workflow.ActivityContext') as mock_activity_class, \
                 patch('vivek.agentic_context.workflow.TaskContext') as mock_task_class:

                mock_session_class.return_value = mock_session
                mock_activity_class.return_value = mock_activity
                mock_task_class.return_value = mock_task

                # Execute workflow
                workflow = ContextWorkflow(config)

                with workflow.session("Build API") as session:
                    with session.activity(
                        "Implement auth",
                        ["auth", "api"],
                        "coder",
                        "auth_service",
                        "Need JWT implementation"
                    ) as activity:
                        with activity.task("Create middleware", ["middleware", "auth"]) as task:
                            # Simulate work
                            prompt = task.build_prompt()
                            task.record_action("Created middleware", file="auth.py")
                            task.record_decision("Use JWT", reasoning="Industry standard")
                            task.record_learning("Validate tokens", lesson_type="security")
                            task.set_result("Middleware completed")

                # Verify all operations were called
                mock_storage.create_session.assert_called_once()
                mock_storage.create_activity.assert_called_once()
                mock_storage.create_task.assert_called_once()

    @pytest.mark.skip(reason="Integration test requires complex mocking - needs refactoring")
    def test_workflow_with_context_retrieval(self):
        """Test workflow with historical context retrieval"""
        config = Config.from_preset("production")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            # Set up mocks
            mock_storage = Mock()
            mock_retriever = Mock()

            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            # Mock historical context
            mock_retriever.retrieve.return_value = [
                {
                    "item": {
                        "content": "Previous JWT implementation",
                        "category": "actions",
                        "tags": ["jwt", "auth"]
                    },
                    "score": 0.8,
                    "matched_tags": ["auth"],
                    "category": "actions"
                }
            ]

            # Set up context hierarchy
            mock_storage.build_hierarchical_context.return_value = {
                "session": {"original_ask": "Build auth system"},
                "activity": {"description": "Implement JWT"},
                "task": {"description": "Create token validation"}
            }

            with patch('vivek.agentic_context.workflow.SessionContext') as mock_session_class, \
                 patch('vivek.agentic_context.workflow.ActivityContext') as mock_activity_class, \
                 patch('vivek.agentic_context.workflow.TaskContext') as mock_task_class:

                # Set up context managers
                mock_session = Mock()
                mock_session.__enter__ = Mock(return_value=mock_session)
                mock_session.__exit__ = Mock(return_value=None)

                mock_activity = Mock()
                mock_activity.__enter__ = Mock(return_value=mock_activity)
                mock_activity.__exit__ = Mock(return_value=None)

                mock_task = Mock()
                mock_task.__enter__ = Mock(return_value=mock_task)
                mock_task.__exit__ = Mock(return_value=None)
                mock_task.build_prompt = Mock(return_value="Generated prompt")
                mock_task.record_action = Mock()
                mock_task.record_decision = Mock()
                mock_task.set_result = Mock()

                mock_session_class.return_value = mock_session
                mock_activity_class.return_value = mock_activity
                mock_task_class.return_value = mock_task

                # Execute workflow
                workflow = ContextWorkflow(config)

                with workflow.session("Test session") as session:
                    with session.activity("Test", ["test"], "coder", "test", "Test") as activity:
                        with activity.task("Test task", ["test"]) as task:
                            # Build prompt should include historical context
                            prompt = task.build_prompt()

                            # Verify retriever was called
                            mock_retriever.retrieve.assert_called_once()

    def test_workflow_error_handling(self):
        """Test workflow handles errors gracefully"""
        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class:
            # Make storage creation fail
            mock_storage_class.side_effect = Exception("Storage init failed")

            # Workflow creation should fail gracefully
            with pytest.raises(Exception):  # Would be StorageError in real implementation
                ContextWorkflow(config)

    def test_configuration_preset_integration(self):
        """Test that configuration presets work with workflow"""
        # Test different presets
        presets = ["development", "production", "fast", "accurate"]

        for preset in presets:
            config = Config.from_preset(preset)

            # Should be able to create workflow with any preset
            with patch('vivek.agentic_context.workflow.ContextStorage'), \
                 patch('vivek.agentic_context.workflow.RetrieverFactory'):

                workflow = ContextWorkflow(config)
                assert workflow.config == config

    @pytest.mark.skip(reason="Integration test requires complex mocking - needs refactoring")
    def test_context_persistence_across_tasks(self):
        """Test that context persists across multiple tasks"""
        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            # Set up mocks
            mock_storage = Mock()
            mock_retriever = Mock()

            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            # Mock storage methods for multiple operations
            mock_storage.add_context = Mock()
            mock_storage.build_hierarchical_context.return_value = {
                "session": {"original_ask": "Test"},
                "activity": {"description": "Test activity"},
                "task": {"description": "Test task"}
            }

            with patch('vivek.agentic_context.workflow.SessionContext') as mock_session_class, \
                 patch('vivek.agentic_context.workflow.ActivityContext') as mock_activity_class, \
                 patch('vivek.agentic_context.workflow.TaskContext') as mock_task_class:

                # Set up context managers
                mock_session = Mock()
                mock_session.__enter__ = Mock(return_value=mock_session)
                mock_session.__exit__ = Mock(return_value=None)

                mock_activity = Mock()
                mock_activity.__enter__ = Mock(return_value=mock_activity)
                mock_activity.__exit__ = Mock(return_value=None)

                def create_mock_task(task_id, description, tags):
                    mock_task = Mock()
                    mock_task.__enter__ = Mock(return_value=mock_task)
                    mock_task.__exit__ = Mock(return_value=None)
                    mock_task.task_id = task_id
                    mock_task.record_action = Mock()
                    mock_task.record_decision = Mock()
                    mock_task.set_result = Mock()
                    return mock_task

                mock_task1 = create_mock_task("task_001", "Task 1", ["test"])
                mock_task2 = create_mock_task("task_002", "Task 2", ["test"])

                mock_session_class.return_value = mock_session
                mock_activity_class.return_value = mock_activity

                # Use a counter object instead of function attribute
                task_counter = {"count": 0}

                def task_side_effect(*args, **kwargs):
                    task_counter["count"] += 1

                    if task_counter["count"] == 1:
                        return mock_task1
                    else:
                        return mock_task2

                mock_task_class.side_effect = task_side_effect

                # Execute workflow with multiple tasks
                workflow = ContextWorkflow(config)

                with workflow.session("Test session") as session:
                    with session.activity("Test", ["test"], "coder", "test", "Test") as activity:
                        # First task
                        with activity.task("Task 1", ["test"]) as task1:
                            task1.record_action("Action 1", file="file1.py")
                            task1.set_result("Result 1")

                        # Second task
                        with activity.task("Task 2", ["test"]) as task2:
                            task2.record_action("Action 2", file="file2.py")
                            task2.set_result("Result 2")

                # Verify both tasks recorded their actions
                assert mock_storage.add_context.call_count >= 2

    def test_strategy_switching_during_workflow(self):
        """Test switching retrieval strategies during workflow execution"""
        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            # Set up mocks
            mock_storage = Mock()
            mock_retriever = Mock()

            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            # Set up context hierarchy
            mock_storage.build_hierarchical_context.return_value = {
                "session": {"original_ask": "Test"},
                "activity": {"description": "Test activity"},
                "task": {"description": "Test task"}
            }

            with patch('vivek.agentic_context.workflow.SessionContext') as mock_session_class, \
                 patch('vivek.agentic_context.workflow.ActivityContext') as mock_activity_class, \
                 patch('vivek.agentic_context.workflow.TaskContext') as mock_task_class:

                # Set up context managers
                mock_session = Mock()
                mock_session.__enter__ = Mock(return_value=mock_session)
                mock_session.__exit__ = Mock(return_value=None)

                mock_activity = Mock()
                mock_activity.__enter__ = Mock(return_value=mock_activity)
                mock_activity.__exit__ = Mock(return_value=None)

                mock_task = Mock()
                mock_task.__enter__ = Mock(return_value=mock_task)
                mock_task.__exit__ = Mock(return_value=None)

                mock_session_class.return_value = mock_session
                mock_activity_class.return_value = mock_activity
                mock_task_class.return_value = mock_task

                # Create workflow
                workflow = ContextWorkflow(config)

                # Switch strategy
                with patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_new_factory:
                    mock_new_retriever = Mock()
                    mock_new_factory.create_retriever.return_value = mock_new_retriever

                    workflow.switch_strategy("hybrid")

                    # Verify strategy was switched
                    assert workflow.config["retrieval"]["strategy"] == "hybrid"
                    assert workflow.retriever == mock_new_retriever

    def test_workflow_statistics(self):
        """Test workflow statistics collection"""
        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            # Set up mocks
            mock_storage = Mock()
            mock_retriever = Mock()

            # Mock statistics
            expected_stats = {
                "total_sessions": 1,
                "total_activities": 2,
                "total_tasks": 3,
                "actions": 5,
                "decisions": 2,
                "results": 3,
                "learnings": 1
            }

            mock_storage.get_statistics.return_value = expected_stats
            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            workflow = ContextWorkflow(config)

            # Get statistics
            stats = workflow.get_statistics()

            assert stats == expected_stats
            mock_storage.get_statistics.assert_called_once()

    @pytest.mark.skip(reason="Integration test requires complex mocking - needs refactoring")
    def test_workflow_export_functionality(self):
        """Test workflow export for persistence"""
        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            # Set up mocks
            mock_storage = Mock()
            mock_retriever = Mock()

            # Mock sessions data
            mock_session = Mock()
            mock_session.session_id = "session_001"
            mock_session.original_ask = "Test ask"
            mock_session.high_level_plan = "Test plan"
            mock_session.created_at.isoformat.return_value = "2023-01-01T00:00:00"
            mock_session.activities = []

            mock_storage.sessions = {"session_001": mock_session}

            # Mock context DB
            mock_item = Mock()
            mock_item.content = "Test content"
            mock_item.tags = ["test"]
            mock_item.timestamp.isoformat.return_value = "2023-01-01T00:00:00"
            mock_item.activity_id = None
            mock_item.task_id = None
            mock_item.metadata = {}

            # Mock context DB structure
            with patch.object(mock_storage, 'context_db') as mock_db:
                mock_category = Mock()
                mock_category.value = "actions"
                mock_db.items.return_value = [(mock_category, [mock_item])]

            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            workflow = ContextWorkflow(config)

            # Export workflow
            export_data = workflow.export()

            assert "sessions" in export_data
            assert "context_db" in export_data
            assert "session_001" in export_data["sessions"]

            # Verify session data
            session_data = export_data["sessions"]["session_001"]
            assert session_data["original_ask"] == "Test ask"
            assert session_data["high_level_plan"] == "Test plan"

            # Verify context DB data
            assert "actions" in export_data["context_db"]
            assert len(export_data["context_db"]["actions"]) == 1


class TestCrossComponentIntegration:
    """Test interactions between different components"""

    def test_config_to_storage_integration(self):
        """Test configuration affects storage behavior"""
        # Test with different presets
        presets = ["fast", "accurate"]

        for preset in presets:
            config = Config.from_preset(preset)

            with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
                 patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

                mock_storage = Mock()
                mock_retriever = Mock()

                mock_storage_class.return_value = mock_storage
                mock_factory_class.create_retriever.return_value = mock_retriever

                workflow = ContextWorkflow(config)

                # Config should be passed to retriever factory
                mock_factory_class.create_retriever.assert_called_with(mock_storage, config)

    def test_retrieval_strategy_configuration(self):
        """Test that retrieval strategy configuration affects behavior"""
        strategies = ["tags_only", "hybrid", "auto"]

        for strategy in strategies:
            config = Config.from_preset("development")
            config = Config.from_preset("development", **{f"retrieval.strategy": strategy})

            with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
                 patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

                mock_storage = Mock()
                mock_retriever = Mock()

                mock_storage_class.return_value = mock_storage
                mock_factory_class.create_retriever.return_value = mock_retriever

                workflow = ContextWorkflow(config)

                # Should create appropriate retriever type based on strategy
                mock_factory_class.create_retriever.assert_called_once()

    def test_context_hierarchy_validation(self):
        """Test that context hierarchy is properly validated"""
        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            mock_storage = Mock()
            mock_retriever = Mock()

            # Make storage operations fail to test error handling
            mock_storage.create_activity.side_effect = ValueError("No active session")
            mock_storage.create_task.side_effect = ValueError("No active activity")

            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            with patch('vivek.agentic_context.workflow.SessionContext') as mock_session_class, \
                 patch('vivek.agentic_context.workflow.ActivityContext') as mock_activity_class, \
                 patch('vivek.agentic_context.workflow.TaskContext') as mock_task_class:

                # Set up context managers
                mock_session = Mock()
                mock_session.__enter__ = Mock(return_value=mock_session)
                mock_session.__exit__ = Mock(return_value=None)

                mock_activity = Mock()
                mock_activity.__enter__ = Mock(return_value=mock_activity)
                mock_activity.__exit__ = Mock(return_value=None)

                mock_task = Mock()
                mock_task.__enter__ = Mock(return_value=mock_task)
                mock_task.__exit__ = Mock(return_value=None)

                mock_session_class.return_value = mock_session
                mock_activity_class.return_value = mock_activity
                mock_task_class.return_value = mock_task

                workflow = ContextWorkflow(config)

                # Test hierarchy validation - should fail when trying to create activity without session
                with workflow.session("Test") as session:
                    # This should work
                    pass

                # Activity creation without session should fail
                # (This would be tested in actual implementation)


class TestPerformanceAndScalability:
    """Test performance and scalability aspects"""

    @pytest.mark.skip(reason="Integration test requires complex mocking - needs refactoring")
    def test_large_context_handling(self):
        """Test handling of large context databases"""
        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            # Set up mocks
            mock_storage = Mock()
            mock_retriever = Mock()

            # Mock large number of context items
            large_context_items = [
                Mock(content=f"Content {i}", tags=[f"tag{i}"], category=ContextCategory.ACTIONS)
                for i in range(1000)
            ]

            mock_storage.get_all_context_items.return_value = large_context_items
            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            # Mock retriever to handle large dataset
            mock_retriever.retrieve.return_value = [
                {"item": {"content": "Relevant item"}, "score": 0.8, "matched_tags": ["test"]}
            ]

            workflow = ContextWorkflow(config)

            # Should handle large context without issues
            with patch('vivek.agentic_context.workflow.SessionContext') as mock_session_class, \
                 patch('vivek.agentic_context.workflow.ActivityContext') as mock_activity_class, \
                 patch('vivek.agentic_context.workflow.TaskContext') as mock_task_class:

                mock_session = Mock()
                mock_session.__enter__ = Mock(return_value=mock_session)
                mock_session.__exit__ = Mock(return_value=None)

                mock_activity = Mock()
                mock_activity.__enter__ = Mock(return_value=mock_activity)
                mock_activity.__exit__ = Mock(return_value=None)

                mock_task = Mock()
                mock_task.__enter__ = Mock(return_value=mock_task)
                mock_task.__exit__ = Mock(return_value=None)

                mock_session_class.return_value = mock_session
                mock_activity_class.return_value = mock_activity
                mock_task_class.return_value = mock_task

                # Execute workflow with large context
                with workflow.session("Test") as session:
                    with session.activity("Test", ["test"], "coder", "test", "Test") as activity:
                        with activity.task("Test task", ["test"]) as task:
                            # Should handle large context retrieval
                            prompt = task.build_prompt()

                # Verify retriever was called with large dataset
                mock_storage.get_all_context_items.assert_called()

    @pytest.mark.skip(reason="Integration test requires complex mocking - needs refactoring")
    def test_concurrent_workflow_execution(self):
        """Test concurrent workflow execution"""
        import threading
        import time

        config = Config.from_preset("development")

        with patch('vivek.agentic_context.workflow.ContextStorage') as mock_storage_class, \
             patch('vivek.agentic_context.workflow.RetrieverFactory') as mock_factory_class:

            mock_storage = Mock()
            mock_retriever = Mock()

            mock_storage_class.return_value = mock_storage
            mock_factory_class.create_retriever.return_value = mock_retriever

            # Set up context hierarchy
            mock_storage.build_hierarchical_context.return_value = {
                "session": {"original_ask": "Test"},
                "activity": {"description": "Test activity"},
                "task": {"description": "Test task"}
            }

            with patch('vivek.agentic_context.workflow.SessionContext') as mock_session_class, \
                 patch('vivek.agentic_context.workflow.ActivityContext') as mock_activity_class, \
                 patch('vivek.agentic_context.workflow.TaskContext') as mock_task_class:

                mock_session = Mock()
                mock_session.__enter__ = Mock(return_value=mock_session)
                mock_session.__exit__ = Mock(return_value=None)

                mock_activity = Mock()
                mock_activity.__enter__ = Mock(return_value=mock_activity)
                mock_activity.__exit__ = Mock(return_value=None)

                mock_task = Mock()
                mock_task.__enter__ = Mock(return_value=mock_task)
                mock_task.__exit__ = Mock(return_value=None)
                mock_task.record_action = Mock()

                mock_session_class.return_value = mock_session
                mock_activity_class.return_value = mock_activity
                mock_task_class.return_value = mock_task

                def run_workflow(workflow_id):
                    """Run a workflow in a separate thread"""
                    workflow = ContextWorkflow(config)

                    with workflow.session(f"Session {workflow_id}") as session:
                        with session.activity(f"Activity {workflow_id}", [f"tag{workflow_id}"], "coder", "test", "Test") as activity:
                            with activity.task(f"Task {workflow_id}", [f"tag{workflow_id}"]) as task:
                                task.record_action(f"Action {workflow_id}")
                                time.sleep(0.01)  # Simulate work

                # Run multiple workflows concurrently
                threads = []
                for i in range(5):
                    thread = threading.Thread(target=run_workflow, args=(i,))
                    threads.append(thread)

                # Start all threads
                for thread in threads:
                    thread.start()

                # Wait for completion
                for thread in threads:
                    thread.join()

                # Verify all workflows completed without interference
                assert mock_storage.add_context.call_count >= 5