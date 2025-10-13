"""
Structured Workflow Architecture for Vivek

This module implements a layered prompt architecture that aligns with natural
engineering workflow patterns, providing clear separation between understanding,
decomposition, activity detailing, task creation, and execution phases.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum


class WorkflowPhase(Enum):
    """Engineering workflow phases"""

    UNDERSTAND = "understand"
    DECOMPOSE = "decompose"
    DETAIL = "detail"
    TASKIFY = "taskify"
    EXECUTE = "execute"
    TEST = "test"
    REFACTOR = "refactor"


class PerspectiveHat(Enum):
    """Multiple perspectives for analysis (inspired by Six Thinking Hats)"""

    USER = "user"  # Usability and user experience
    CRITIC = "critic"  # Weaknesses, risks, and issues
    OPS = "ops"  # Deployability, observability, maintainability
    DEBUGGER = "debugger"  # Debugging, tracing, troubleshooting
    FUTURE = "future"  # Scalability, adaptability, evolution
    SDET = "sdet"  # Testing, quality, reliability


@dataclass
class ActivityBreakdown:
    """Structured breakdown of high-level activities"""

    activity_id: str
    name: str
    description: str
    expected_outcomes: List[str]
    boundaries: List[str]
    dependencies: List[str]
    perspectives: Dict[PerspectiveHat, str] = field(default_factory=dict)


@dataclass
class TaskDefinition:
    """Atomic, executable task definition"""

    task_id: str
    activity_id: str
    description: str
    file_path: str
    file_status: str  # "new" or "existing"
    mode: str  # coder, architect, peer, sdet
    dependencies: List[str]
    current_state: str
    target_state: str
    test_criteria: List[str]
    implementation_steps: List[str]


@dataclass
class ContextSummary:
    """Context summary with metadata for agentic context management"""

    session_id: str
    timestamp: str
    short_term_memory: List[str]  # Recent decisions and actions
    medium_term_memory: List[str]  # Activity summaries and key outcomes
    long_term_memory: Dict[str, Any]  # Archived context with metadata
    token_budget: int
    compression_strategy: str


class StructuredWorkflow:
    """Main workflow orchestrator for structured prompt architecture"""

    def __init__(self):
        self.current_phase = WorkflowPhase.UNDERSTAND
        self.activities: Dict[str, ActivityBreakdown] = {}
        self.tasks: Dict[str, TaskDefinition] = {}
        self.context_history: List[ContextSummary] = []

    def understand_task(self, user_input: str, context: str) -> Dict[str, Any]:
        """Phase 1: Understand the task and clarify scope"""
        return {
            "phase": WorkflowPhase.UNDERSTAND.value,
            "analysis": {
                "user_intent": self._extract_user_intent(user_input),
                "scope_clarification": self._clarify_scope(user_input, context),
                "success_criteria": self._define_success_criteria(user_input),
                "assumptions": self._identify_assumptions(user_input, context),
            },
        }

    def decompose_activities(
        self, understanding: Dict[str, Any]
    ) -> List[ActivityBreakdown]:
        """Phase 2: Break down into high-level activities"""
        activities = []

        # Generate activities based on understanding
        for i, activity_name in enumerate(self._generate_activity_names(understanding)):
            activity = ActivityBreakdown(
                activity_id=f"activity_{i+1}",
                name=activity_name,
                description=self._generate_activity_description(
                    activity_name, understanding
                ),
                expected_outcomes=self._define_expected_outcomes(activity_name),
                boundaries=self._define_boundaries(activity_name),
                dependencies=self._identify_dependencies(activity_name, activities),
            )

            # Add multiple perspective analysis
            activity.perspectives = self._analyze_multiple_perspectives(activity)
            activities.append(activity)

        return activities

    def detail_activities(
        self, activities: List[ActivityBreakdown]
    ) -> List[ActivityBreakdown]:
        """Phase 3: Detail each activity with outcomes and boundaries"""
        detailed_activities = []

        for activity in activities:
            # Enhance activity with detailed analysis
            detailed_activity = ActivityBreakdown(
                activity_id=activity.activity_id,
                name=activity.name,
                description=self._enhance_activity_description(activity),
                expected_outcomes=self._detail_expected_outcomes(activity),
                boundaries=self._detail_boundaries(activity),
                dependencies=activity.dependencies,
                perspectives=self._deepen_perspective_analysis(activity),
            )
            detailed_activities.append(detailed_activity)

        return detailed_activities

    def create_tasks(self, activities: List[ActivityBreakdown]) -> List[TaskDefinition]:
        """Phase 4: Convert activities into atomic tasks"""
        tasks = []

        for activity in activities:
            activity_tasks = self._break_activity_into_tasks(activity)
            tasks.extend(activity_tasks)

        return tasks

    def _extract_user_intent(self, user_input: str) -> str:
        """Extract core user intent from input"""
        # Implementation would analyze user input for key requirements
        return "Extracted user intent based on input analysis"

    def _clarify_scope(self, user_input: str, context: str) -> List[str]:
        """Identify what is and isn't included in scope"""
        return ["In scope: core functionality", "Out of scope: advanced features"]

    def _define_success_criteria(self, user_input: str) -> List[str]:
        """Define measurable success criteria"""
        return ["Functionality works as expected", "Code follows best practices"]

    def _identify_assumptions(self, user_input: str, context: str) -> List[str]:
        """Identify assumptions and prerequisites"""
        return ["Python environment available", "Dependencies installed"]

    def _generate_activity_names(self, understanding: Dict[str, Any]) -> List[str]:
        """Generate high-level activity names"""
        return ["Set up project structure", "Implement core functionality", "Add tests"]

    def _generate_activity_description(
        self, activity_name: str, understanding: Dict[str, Any]
    ) -> str:
        """Generate detailed activity description"""
        return f"Detailed description for {activity_name}"

    def _define_expected_outcomes(self, activity_name: str) -> List[str]:
        """Define expected outcomes for activity"""
        return [f"{activity_name} completed successfully", "All requirements met"]

    def _define_boundaries(self, activity_name: str) -> List[str]:
        """Define activity boundaries and constraints"""
        return [f"{activity_name} should not affect other components"]

    def _identify_dependencies(
        self, activity_name: str, existing_activities: List[ActivityBreakdown]
    ) -> List[str]:
        """Identify activity dependencies"""
        return [
            dep.activity_id
            for dep in existing_activities
            if self._depends_on(activity_name, dep.name)
        ]

    def _depends_on(self, activity_name: str, dependency_name: str) -> bool:
        """Check if one activity depends on another"""
        # Implementation would analyze dependency relationships
        return False

    def _analyze_multiple_perspectives(
        self, activity: ActivityBreakdown
    ) -> Dict[PerspectiveHat, str]:
        """Analyze activity from multiple perspectives"""
        perspectives = {}

        for hat in PerspectiveHat:
            perspectives[hat] = self._analyze_from_perspective(activity, hat)

        return perspectives

    def _analyze_from_perspective(
        self, activity: ActivityBreakdown, hat: PerspectiveHat
    ) -> str:
        """Analyze activity from specific perspective"""
        perspective_prompts = {
            PerspectiveHat.USER: "How does this activity impact user experience and usability?",
            PerspectiveHat.CRITIC: "What are the weaknesses, risks, and potential issues?",
            PerspectiveHat.OPS: "How deployable, observable, and maintainable is this?",
            PerspectiveHat.DEBUGGER: "How easy will this be to debug and troubleshoot?",
            PerspectiveHat.FUTURE: "How scalable and adaptable is this for future needs?",
            PerspectiveHat.SDET: "How testable and reliable is this approach?",
        }

        # Return analysis based on perspective
        return f"Analysis from {hat.value} perspective for {activity.name}"

    def _enhance_activity_description(self, activity: ActivityBreakdown) -> str:
        """Enhance activity description with more detail"""
        return f"Enhanced: {activity.description}"

    def _detail_expected_outcomes(self, activity: ActivityBreakdown) -> List[str]:
        """Add more detailed expected outcomes"""
        return activity.expected_outcomes + ["Performance meets requirements"]

    def _detail_boundaries(self, activity: ActivityBreakdown) -> List[str]:
        """Add more detailed boundaries"""
        return activity.boundaries + ["Must follow coding standards"]

    def _deepen_perspective_analysis(
        self, activity: ActivityBreakdown
    ) -> Dict[PerspectiveHat, str]:
        """Deepen the multiple perspective analysis"""
        return self._analyze_multiple_perspectives(activity)

    def _break_activity_into_tasks(
        self, activity: ActivityBreakdown
    ) -> List[TaskDefinition]:
        """Break activity into atomic tasks following TDD pattern"""
        tasks = []

        # For each activity, create tasks following: Red-Green-Refactor pattern
        base_task = TaskDefinition(
            task_id=f"{activity.activity_id}_1",
            activity_id=activity.activity_id,
            description=f"Set up test structure for {activity.name}",
            file_path=self._suggest_file_path(activity.name, "test"),
            file_status="new",
            mode="sdet",
            dependencies=[],
            current_state="No tests exist",
            target_state="Failing test exists",
            test_criteria=["Test structure created", "Test fails as expected"],
            implementation_steps=["Create test file", "Write failing test case"],
        )
        tasks.append(base_task)

        implementation_task = TaskDefinition(
            task_id=f"{activity.activity_id}_2",
            activity_id=activity.activity_id,
            description=f"Implement {activity.name}",
            file_path=self._suggest_file_path(activity.name, "implementation"),
            file_status="new",
            mode="coder",
            dependencies=[base_task.task_id],
            current_state="Failing test exists",
            target_state="Test passes",
            test_criteria=["Implementation complete", "Test passes"],
            implementation_steps=["Write implementation code", "Run tests"],
        )
        tasks.append(implementation_task)

        refactor_task = TaskDefinition(
            task_id=f"{activity.activity_id}_3",
            activity_id=activity.activity_id,
            description=f"Refactor {activity.name} for quality",
            file_path=self._suggest_file_path(activity.name, "implementation"),
            file_status="existing",
            mode="coder",
            dependencies=[implementation_task.task_id],
            current_state="Test passes",
            target_state="Clean, maintainable code",
            test_criteria=["Code quality improved", "All tests still pass"],
            implementation_steps=["Improve code structure", "Add documentation"],
        )
        tasks.append(refactor_task)

        return tasks

    def _suggest_file_path(self, activity_name: str, task_type: str) -> str:
        """Suggest appropriate file path for task"""
        # Implementation would suggest appropriate file paths
        return f"suggested_path_for_{activity_name}_{task_type}.py"

    def condense_context(
        self, current_context: str, strategy: str = "agentic"
    ) -> ContextSummary:
        """Create context summary for agentic context management"""
        # Implementation would condense context based on strategy
        return ContextSummary(
            session_id="current_session",
            timestamp="now",
            short_term_memory=["Recent decisions"],
            medium_term_memory=["Activity summaries"],
            long_term_memory={"archived": "context"},
            token_budget=4000,
            compression_strategy=strategy,
        )
