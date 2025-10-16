"""
Tests for structured workflow architecture.
"""

import pytest
from unittest.mock import Mock, patch
from dataclasses import asdict

from vivek.core.structured_workflow import (
    StructuredWorkflow,
    WorkflowPhase,
    PerspectiveHat,
    ActivityBreakdown,
    TaskDefinition,
    ContextSummary,
)


class TestStructuredWorkflow:
    """Test cases for StructuredWorkflow class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.workflow = StructuredWorkflow()

    def test_understand_task_basic(self):
        """Test basic task understanding"""
        user_input = "Add user authentication to my app"
        context = "Python FastAPI project"

        result = self.workflow.understand_task(user_input, context)

        assert "phase" in result
        assert result["phase"] == WorkflowPhase.UNDERSTAND.value
        assert "analysis" in result
        assert "user_intent" in result["analysis"]

    def test_decompose_activities_creates_activities(self):
        """Test activity decomposition"""
        understanding = {
            "core_intent": "Implement user authentication",
            "scope_definition": {"in_scope": ["JWT auth"], "out_of_scope": ["OAuth"]},
            "success_criteria": ["Users can login"],
        }

        activities = self.workflow.decompose_activities(understanding)

        assert isinstance(activities, list)
        assert len(activities) > 0

        # Check first activity structure
        activity = activities[0]
        assert hasattr(activity, "activity_id")
        assert hasattr(activity, "name")
        assert hasattr(activity, "description")
        assert hasattr(activity, "expected_outcomes")
        assert hasattr(activity, "perspectives")

    def test_detail_activities_enhances_activities(self):
        """Test activity detailing with perspectives"""
        # Create mock activity
        activity = ActivityBreakdown(
            activity_id="test_activity",
            name="Test Activity",
            description="Test description",
            expected_outcomes=["Test outcome"],
            boundaries=["Test boundary"],
            dependencies=[],
        )

        detailed_activities = self.workflow.detail_activities([activity])

        assert len(detailed_activities) == 1
        detailed = detailed_activities[0]

        # Should have enhanced description and perspectives
        assert (
            "enhanced" in detailed.description.lower()
            or len(detailed.expected_outcomes) > 1
        )

    def test_create_tasks_generates_tdd_tasks(self):
        """Test task creation follows TDD pattern"""
        # Create mock activities
        activities = [
            ActivityBreakdown(
                activity_id="activity_1",
                name="User Authentication",
                description="Implement user login",
                expected_outcomes=["Users can authenticate"],
                boundaries=["Basic auth only"],
                dependencies=[],
            )
        ]

        tasks = self.workflow.create_tasks(activities)

        assert isinstance(tasks, list)
        assert len(tasks) > 0

        # Should create multiple tasks per activity (TDD pattern)
        activity_tasks = [t for t in tasks if t.activity_id == "activity_1"]
        assert len(activity_tasks) >= 2  # At least RED and GREEN phases

        # Check task structure
        task = tasks[0]
        assert hasattr(task, "task_id")
        assert hasattr(task, "description")
        assert hasattr(task, "file_path")
        assert hasattr(task, "mode")
        assert hasattr(task, "test_criteria")
        assert hasattr(task, "implementation_steps")

    def test_perspective_analysis_covers_all_hats(self):
        """Test that all six perspectives are analyzed"""
        activity = ActivityBreakdown(
            activity_id="test_activity",
            name="Test Activity",
            description="Test description",
            expected_outcomes=["Test outcome"],
            boundaries=["Test boundary"],
            dependencies=[],
        )

        # Mock the perspective analysis method
        perspectives = self.workflow._analyze_multiple_perspectives(activity)

        # Should have all six perspectives
        expected_hats = {hat for hat in PerspectiveHat}
        actual_hats = set(perspectives.keys())

        assert actual_hats == expected_hats

        # Each perspective should have content
        for hat in PerspectiveHat:
            assert hat in perspectives
            assert len(perspectives[hat]) > 0


class TestActivityBreakdown:
    """Test cases for ActivityBreakdown dataclass"""

    def test_activity_creation(self):
        """Test creating activity with all fields"""
        activity = ActivityBreakdown(
            activity_id="activity_1",
            name="Test Activity",
            description="Test description",
            expected_outcomes=["Outcome 1", "Outcome 2"],
            boundaries=["Boundary 1", "Boundary 2"],
            dependencies=["activity_0"],
        )

        assert activity.activity_id == "activity_1"
        assert activity.name == "Test Activity"
        assert len(activity.expected_outcomes) == 2
        assert len(activity.boundaries) == 2
        assert len(activity.dependencies) == 1

    def test_perspectives_integration(self):
        """Test perspectives are properly integrated"""
        perspectives = {
            PerspectiveHat.USER: "User perspective analysis",
            PerspectiveHat.CRITIC: "Critic perspective analysis",
            PerspectiveHat.OPS: "Ops perspective analysis",
            PerspectiveHat.DEBUGGER: "Debugger perspective analysis",
            PerspectiveHat.FUTURE: "Future perspective analysis",
            PerspectiveHat.SDET: "SDET perspective analysis",
        }

        activity = ActivityBreakdown(
            activity_id="test_activity",
            name="Test Activity",
            description="Test description",
            expected_outcomes=["Test outcome"],
            boundaries=["Test boundary"],
            dependencies=[],
            perspectives=perspectives,
        )

        assert activity.perspectives == perspectives
        assert len(activity.perspectives) == 6


class TestTaskDefinition:
    """Test cases for TaskDefinition dataclass"""

    def test_task_creation_follows_tdd(self):
        """Test that tasks follow TDD pattern"""
        task = TaskDefinition(
            task_id="task_1",
            activity_id="activity_1",
            description="Write failing test for authentication",
            file_path="tests/test_auth.py",
            file_status="new",
            mode="sdet",
            dependencies=[],
            current_state="No tests exist",
            target_state="Failing test exists",
            test_criteria=["Test file created", "Test fails appropriately"],
            implementation_steps=["Create test file", "Write failing test"],
        )

        assert task.task_id == "task_1"
        assert task.mode == "sdet"
        assert task.file_status == "new"
        assert "test" in task.description.lower()
        assert len(task.test_criteria) > 0
        assert len(task.implementation_steps) > 0

    def test_task_dependencies_tracking(self):
        """Test that task dependencies are properly tracked"""
        task = TaskDefinition(
            task_id="task_2",
            activity_id="activity_1",
            description="Implement authentication",
            file_path="src/auth.py",
            file_status="new",
            mode="coder",
            dependencies=["task_1"],
            current_state="Failing test exists",
            target_state="Test passes",
            test_criteria=["Implementation complete"],
            implementation_steps=["Write auth code"],
        )

        assert len(task.dependencies) == 1
        assert task.dependencies[0] == "task_1"
        assert task.mode == "coder"


class TestWorkflowIntegration:
    """Test integration of workflow phases"""

    def setup_method(self):
        """Set up workflow for integration testing"""
        self.workflow = StructuredWorkflow()

    def test_full_workflow_execution(self):
        """Test executing full workflow from understanding to tasks"""
        user_input = "Add JWT authentication to my FastAPI app"
        context = "Python project with FastAPI"

        # Phase 1: Understand
        understanding = self.workflow.understand_task(user_input, context)
        assert understanding["phase"] == WorkflowPhase.UNDERSTAND.value

        # Phase 2: Decompose
        activities = self.workflow.decompose_activities(understanding["analysis"])
        assert len(activities) > 0

        # Phase 3: Detail
        detailed_activities = self.workflow.detail_activities(activities)
        assert len(detailed_activities) == len(activities)

        # Phase 4: Taskify
        tasks = self.workflow.create_tasks(detailed_activities)
        assert len(tasks) > 0

        # Validate task quality
        for task in tasks:
            assert task.task_id
            assert task.description
            assert task.mode in ["coder", "architect", "peer", "sdet"]
            assert task.file_path

    def test_workflow_phase_progression(self):
        """Test that workflow progresses through phases correctly"""
        # This would test the phase progression logic
        # For now, just verify the phases exist
        expected_phases = [
            WorkflowPhase.UNDERSTAND,
            WorkflowPhase.DECOMPOSE,
            WorkflowPhase.DETAIL,
            WorkflowPhase.TASKIFY,
        ]

        for phase in expected_phases:
            assert phase.value in [p.value for p in WorkflowPhase]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
