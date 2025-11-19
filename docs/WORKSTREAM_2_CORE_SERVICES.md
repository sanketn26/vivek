# Workstream 2: Core Services & Interactive Planning

**Timeline**: Week 3-5
**Goal**: Implement planning, execution, and quality services with multi-phase interactive workflow

**Prerequisites**: Workstream 1 complete

---

## Overview

This workstream implements the core services with a **multi-phase interactive planning system** that progressively refines requirements before decomposition. The system now uses a three-phase approach:

1. **Clarification Phase**: Ask clarifying questions for missing requirements
2. **Confirmation Phase**: Validate understanding of requirements
3. **Decomposition Phase**: Break down into actionable work items using TDD

### Deliverables
- ✅ Multi-phase planner service (clarify → confirm → decompose)
- ✅ Executor service with multiple modes (Coder, SDET with 5-phase TDD, Architect, Peer)
- ✅ Quality service (evaluate outputs)
- ✅ Dependency resolution with topological sort
- ✅ Prompt architecture with factory pattern and interfaces
- ✅ TDD workflow orchestrator (struct → tests → implementation → verification)
- ✅ Granular SDET workflow (5-phase test development)
- ✅ 40+ unit tests

### Context Window Strategy

**Problem**: LLMs have limited context windows (typically 8K-32K tokens). Each work item execution needs:
- System prompt (~500 tokens)
- User prompt with context (~2K tokens)
- Output buffer (~2K tokens)
- **Available for code generation: ~4K tokens** (≈200 lines of code)

**Solution**: The planner creates **small, focused work items** with language-specific TDD patterns:
- ✅ Each work item = ONE file
- ✅ Each file = <200 lines (coder) or <100 lines per test phase (SDET)
- ✅ Large features = Multiple work items with explicit dependencies
- ✅ TDD workflow = Structs/Interfaces → Tests (5 phases) → Implementation → Verification
- ✅ Context includes only relevant dependencies (not entire codebase)

**Example Breakdown (Python User Authentication)**:
```
User request: "Create user authentication system"

Phase 1 - CLARIFICATION (User Input Required):
Question: "Do you need OAuth or JWT? Single user service or multi-tenant?"
User Response: "JWT-based, single-tenant, email/password login"

Phase 2 - CONFIRMATION (User Input Required):
Understanding Summary:
  • What we're building: JWT token-based authentication
  • Scope: User creation, login, token validation
  • Key constraints: Single tenant, in-memory for now
  • Assumptions: User emails are unique
  • Success criteria: Can create users, login, validate tokens

User Confirmation: ✅ Confirmed

Phase 3 - DECOMPOSITION (Generated Plan):
- item_1: coder - "Create User dataclass with id, email, password_hash, created_at"
- item_2: sdet phase_1_fixtures - "Define UserFactory, mock DB, test data builders"
- item_3: sdet phase_2b_happy_path - "Test successful user creation and retrieval"
- item_4: sdet phase_2c_edge_cases - "Test empty email, null password, boundary values"
- item_5: sdet phase_2d_error_handling - "Test duplicate users, invalid input, DB failures"
- item_6: coder - "Implement UserService with create_user, get_user methods"
- item_7: sdet phase_2e_coverage_analysis - "Analyze test coverage, identify gaps"
- item_8: coder - "Create JWT token generation service"
- item_9: sdet phase_1_fixtures - "Define TokenFactory, mock crypto, test tokens"
- item_10: sdet phase_2b_happy_path - "Test token generation and validation"
```

This approach ensures:
- Each LLM call stays within context limits
- Users have intermediate control over requirements
- Comprehensive test coverage through TDD
- Language-specific best practices applied

---

## Part 1: Prompt Architecture (Refactored)

The prompt system has been completely refactored to use a **factory pattern with abstract base classes** for type safety and extensibility.

### New Prompt Architecture Files

#### File: `src/vivek/prompts/prompt_architecture.py`

Complete architecture with:
- **Enums**: `ExecutorMode` (coder, sdet, architect, peer), `SDETPhase` (5 phases), `PlannerPhase` (3 phases)
- **Data Classes**: `PromptPair` (system + user prompts), `WorkItem`
- **Abstract Base Classes**: `BasePrompt`, `BasePlannerPrompt`, `BaseExecutorPrompt`
- **Concrete Implementations**:
  - Planner: `ClarificationPrompt`, `ConfirmationPrompt`, `DecompositionPrompt`
  - Executor: `StructInterfacePrompt`, `TestFixturesPrompt`, `HappyPathTestsPrompt`, `ImplementationPrompt`
- **Factory**: `PromptFactory` for centralized creation
- **Backward Compatibility**: Helper functions for existing code

**Key Benefits**:
- Type-safe prompt creation
- Easy to extend with new prompt types (e.g., architect, peer modes)
- Backward compatible through helper functions
- Language-agnostic architecture supports Go, Python, TypeScript

#### File: `src/vivek/prompts/multi_phase_planner_prompts.py`

**Three-Phase Interactive Planning System** (replaces single-phase planner):

**Phase 1 - CLARIFICATION**:
- System Prompt: "Skilled requirement analyst"
- Task: Ask 2-4 critical clarifying questions if needed
- Output: `{needs_clarification: bool, questions: [], reason: ""}`
- Flow: If unclear, user answers questions → continue to Phase 2
- Flow: If clear, skip questions → continue to Phase 2

**Phase 2 - CONFIRMATION**:
- System Prompt: "Requirements validation expert"
- Task: Validate understanding based on user request + clarifications
- Output: `{understanding: [5-7 bullet points], confirmed: bool, concerns: ""}`
- Flow: If confirmed=true → proceed to Phase 3
- Flow: If confirmed=false → return to Phase 1 for more clarifications

**Phase 3 - DECOMPOSITION**:
- System Prompt: "Expert software architect with TDD expertise"
- Task: Decompose requirements into 5-10 work items using TDD pattern
- Output: `{work_items: [...], rationale: ""}`
- Each work item includes: id, file_path, description, mode, language, file_status, dependencies, sdet_phase (if applicable), context_hints

**TDD Decomposition Rules**:

For each component (User model, Auth service, etc.):
```
1. coder - Define structs/dataclasses/interfaces (no implementation, <100 lines)
2. sdet phase_1_fixtures - Create test fixtures, mocks, factories (<80 lines)
3. sdet phase_2b_happy_path - Write success scenario tests (<60 lines)
4. sdet phase_2c_edge_cases - Write boundary condition tests (<60 lines)
5. sdet phase_2d_error_handling - Write exception handling tests (<60 lines)
6. coder - Implement functions to pass tests (<50 lines per method)
7. sdet phase_2e_coverage_analysis - Analyze coverage and identify gaps
```

**Language-Specific Patterns**:

Go:
- Structs: Separate item (models/user.go)
- Interfaces: Separate item if >1 method (services/user_service.go)
- Implementation: Separate items per major function

Python:
- Dataclasses/Models: Separate item (models/user.py)
- Service Classes: Separate item (services/user_service.py)
- Utilities: Separate items by functional group

TypeScript:
- Types/Interfaces: Separate item (types/user.ts)
- Classes/Implementations: Separate item (services/user.service.ts)
- Utilities: Separate items by functional group

#### File: `src/vivek/prompts/granular_sdet_prompts.py`

**5-Phase Test Development (SDET Workflow)**:

**Phase 1 - Test Fixtures**:
- Task: Define test data builders, mocks, setup utilities
- Output: Reusable test infrastructure code
- Focus: Mocks, factories, fixtures (no test cases)

**Phase 2b - Happy Path Tests**:
- Task: Write 3-5 success scenario tests
- Output: Happy path test cases
- Focus: Main functionality, correct outputs, state changes

**Phase 2c - Edge Case Tests**:
- Task: Write boundary condition tests
- Output: Edge case test cases
- Focus: Empty inputs, null values, limits, special cases

**Phase 2d - Error Handling Tests**:
- Task: Write exception and failure scenario tests
- Output: Error handling test cases
- Focus: Invalid inputs, dependency failures, exceptions

**Phase 2e - Coverage Analysis**:
- Task: Analyze test coverage and identify gaps
- Output: Coverage report with recommendations
- Focus: Coverage metrics, untested paths, improvement suggestions

**Helper Functions**:
- `build_test_fixtures_prompt(work_item, language, signatures)`
- `build_happy_path_tests_prompt(work_item, language, fixtures_code)`
- `build_edge_case_tests_prompt(work_item, language, fixtures_code)`
- `build_error_handling_tests_prompt(work_item, language, fixtures_code)`
- `build_test_coverage_prompt(test_output, coverage_report, implementation_files)`

#### File: `src/vivek/prompts/tdd_workflow_orchestrator.py`

**TDD Workflow Orchestration** across languages (Go, Python, TypeScript):

**Execution Phases**:
1. `STRUCT_INTERFACE` - Define types/structs/interfaces
2. `TEST_FIXTURES` - Create test fixtures
3. `HAPPY_PATH_TESTS` - Write success tests
4. `EDGE_CASE_TESTS` - Write boundary tests
5. `ERROR_HANDLING_TESTS` - Write error tests
6. `TEST_COVERAGE_ANALYSIS` - Verify coverage
7. `IMPLEMENTATION` - Implement functions
8. `TEST_EXECUTION` - Run tests and verify

**TDDWorkflowOrchestrator Class**:
- `__init__(language, work_item)` - Initialize for language
- `phase_1_define_structures()` - Generate struct/interface definitions
- `phase_2a_test_fixtures(signatures)` - Generate test fixtures
- `phase_2b_happy_path_tests(fixtures_code)` - Generate happy path tests
- `phase_2c_edge_case_tests(fixtures_code)` - Generate edge case tests
- `phase_2d_error_handling_tests(fixtures_code)` - Generate error tests
- `phase_2e_test_coverage_analysis(...)` - Analyze coverage
- `phase_3_implement(signatures, test_code)` - Implement to pass tests
- `phase_4_run_tests(...)` - Run and verify tests
- `get_execution_plan()` - Return ordered execution steps

**Workflow Examples** (included in file):
- Go workflow with structs, table-driven tests
- Python workflow with dataclasses, pytest fixtures
- TypeScript workflow with interfaces, Jest mocks

---

## Part 2: Planner Service (Updated)

### File: `src/vivek/domain/planning/services/planning_service.py`

```python
"""Planner service with multi-phase interactive workflow."""

import json
from typing import Optional

from vivek.domain.interfaces.planner import IPlannerService
from vivek.domain.planning.models.plan import Plan
from vivek.domain.models.work_item import WorkItem, ExecutionMode
from vivek.domain.exceptions.exception import PlanningException
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.prompts.multi_phase_planner_prompts import (
    build_clarification_prompt,
    build_confirmation_prompt,
    build_decomposition_prompt,
)

class PlannerService(IPlannerService):
    """Service for multi-phase planning and decomposition."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def create_plan(
        self,
        user_request: str,
        project_context: str
    ) -> Plan:
        """Create execution plan through three interactive phases.

        Args:
            user_request: What user wants to implement
            project_context: Project information

        Returns:
            Plan with 5-10 work items

        Raises:
            PlanningException: If planning fails

        Flow:
            Phase 1: Clarification - Ask missing requirement questions
            Phase 2: Confirmation - Validate understanding (may loop back to Phase 1)
            Phase 3: Decomposition - Generate work items using TDD pattern
        """
        try:
            # PHASE 1: CLARIFICATION
            clarification = await self._clarify_requirements(
                user_request, project_context
            )

            # PHASE 2: CONFIRMATION
            confirmation = await self._confirm_understanding(
                user_request, project_context, clarification
            )

            # Loop back if not confirmed
            max_loops = 3
            loop_count = 0
            while not confirmation.get("confirmed", True) and loop_count < max_loops:
                clarification = await self._clarify_requirements(
                    user_request, project_context
                )
                confirmation = await self._confirm_understanding(
                    user_request, project_context, clarification
                )
                loop_count += 1

            # PHASE 3: DECOMPOSITION
            plan_data = await self._decompose_into_items(
                project_context, confirmation
            )

            # Convert to WorkItem objects
            work_items = self._parse_work_items(plan_data)

            # Validate plan
            self._validate_plan(work_items)

            return Plan(work_items=work_items)

        except json.JSONDecodeError as e:
            raise PlanningException(f"Failed to parse LLM response: {e}")
        except Exception as e:
            raise PlanningException(f"Planning failed: {e}")

    async def _clarify_requirements(
        self, user_request: str, project_context: str
    ) -> dict:
        """Phase 1: Ask clarifying questions if needed."""
        prompts = build_clarification_prompt(user_request, project_context)
        response = self.llm.generate(
            system_prompt=prompts["system"],
            prompt=prompts["user"]
        )
        return json.loads(response)

    async def _confirm_understanding(
        self, user_request: str, project_context: str, clarifications: str
    ) -> dict:
        """Phase 2: Validate understanding of requirements."""
        clarifications_str = json.dumps(clarifications)
        prompts = build_confirmation_prompt(
            user_request, project_context, clarifications_str
        )
        response = self.llm.generate(
            system_prompt=prompts["system"],
            prompt=prompts["user"]
        )
        return json.loads(response)

    async def _decompose_into_items(
        self, project_context: str, confirmed_understanding: dict
    ) -> dict:
        """Phase 3: Decompose into work items using TDD pattern."""
        confirmed_str = json.dumps(confirmed_understanding)
        prompts = build_decomposition_prompt(project_context, confirmed_str)
        response = self.llm.generate(
            system_prompt=prompts["system"],
            prompt=prompts["user"]
        )
        return json.loads(response)

    def _parse_work_items(self, plan_data: dict) -> list:
        """Convert plan data to WorkItem objects."""
        work_items = []
        for item_data in plan_data.get("work_items", []):
            work_item = WorkItem(
                id=item_data["id"],
                file_path=item_data["file_path"],
                description=item_data["description"],
                mode=ExecutionMode(item_data["mode"]),
                language=item_data.get("language", "python"),
                file_status=item_data.get("file_status", "new"),
                dependencies=item_data.get("dependencies", []),
            )
            work_items.append(work_item)
        return work_items

    def _validate_plan(self, work_items: list) -> None:
        """Validate plan."""
        if not work_items:
            raise PlanningException("Plan must have at least one work item")

        if len(work_items) > 20:
            raise PlanningException("Plan cannot have more than 20 work items")

        # Check for circular dependencies
        self._check_circular_dependencies(work_items)

    def _check_circular_dependencies(self, work_items: list) -> None:
        """Check for circular dependencies."""
        item_ids = {item.id for item in work_items}

        for item in work_items:
            if item.id in item.dependencies:
                raise PlanningException(f"Circular dependency detected: {item.id}")

            # Check dependencies exist
            for dep_id in item.dependencies:
                if dep_id not in item_ids:
                    raise PlanningException(f"Unknown dependency: {dep_id} in {item.id}")
```

**Key Changes**:
- Three-phase interactive workflow (clarify → confirm → decompose)
- Loop back to clarification if confirmation fails (max 3 loops)
- Increased work items limit from 5 to 20 (due to 5-phase SDET)
- Clear separation of concerns with phase-specific methods
- Imports from refactored `multi_phase_planner_prompts`

---

## Part 3: Executor Service (Updated for TDD Phases)

The executor service now needs to handle granular SDET phases. Each SDET work item has a `sdet_phase` field.

### File: `src/vivek/domain/execution/services/executor_service.py`

**Updated to handle SDET phases**:

```python
"""Executor service with support for TDD phases."""

from typing import Dict
from enum import Enum

from vivek.domain.models.work_item import WorkItem, ExecutionMode
from vivek.domain.models.execution_result import ExecutionResult
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.prompts.tdd_workflow_orchestrator import TDDWorkflowOrchestrator

class ExecutorService:
    """Service for executing work items with TDD workflow."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def execute(self, work_item: WorkItem) -> ExecutionResult:
        """Execute a work item based on its mode and SDET phase.

        Args:
            work_item: Work item to execute

        Returns:
            Execution result with generated code

        Raises:
            ExecutionException: If execution fails
        """
        orchestrator = TDDWorkflowOrchestrator(work_item.language, work_item)

        if work_item.mode == ExecutionMode.CODER:
            return await self._execute_coder(work_item, orchestrator)
        elif work_item.mode == ExecutionMode.SDET:
            return await self._execute_sdet(work_item, orchestrator)
        else:
            raise ValueError(f"Unsupported execution mode: {work_item.mode}")

    async def _execute_coder(
        self, work_item: WorkItem, orchestrator: TDDWorkflowOrchestrator
    ) -> ExecutionResult:
        """Execute coder mode (struct definition or implementation)."""
        # TODO: Call appropriate phase method from orchestrator
        # For now, placeholder
        return ExecutionResult(
            work_item_id=work_item.id,
            success=False,
            errors=["Coder execution not yet implemented"]
        )

    async def _execute_sdet(
        self, work_item: WorkItem, orchestrator: TDDWorkflowOrchestrator
    ) -> ExecutionResult:
        """Execute SDET mode (one of 5 test phases)."""
        # TODO: Route to appropriate SDET phase method
        # sdet_phase: phase_1_fixtures, phase_2b_happy_path, phase_2c_edge_cases,
        #            phase_2d_error_handling, phase_2e_coverage_analysis

        return ExecutionResult(
            work_item_id=work_item.id,
            success=False,
            errors=["SDET execution not yet implemented"]
        )
```

**Implementation Notes**:
- Uses `TDDWorkflowOrchestrator` to generate prompts
- Routes to appropriate phase method based on work item mode/SDET phase
- Needs integration with LLMProvider for actual code generation

---

## Part 4: Quality Service

Quality evaluation remains largely the same, evaluating complete generated code:

### File: `src/vivek/domain/quality/services/quality_service.py`

The quality service evaluates:
1. **Completeness** (0.0-1.0): Are all requirements met?
2. **Correctness** (0.0-1.0): Is the code syntactically correct?
3. **Feedback**: Specific improvement suggestions

Output format (JSON):
```json
{
  "completeness": 0.85,
  "correctness": 1.0,
  "feedback": [
    "Missing error handling for network requests",
    "All type hints present"
  ],
  "passed": true  // if (completeness + correctness) / 2 >= threshold
}
```

---

## Part 5: Dependency Resolution

Using topological sort (Kahn's algorithm) to determine execution order:

### File: `src/vivek/domain/planning/services/dependency_resolver.py`

```python
"""Dependency resolution using topological sort."""

from typing import List
from collections import defaultdict, deque

from vivek.domain.models.work_item import WorkItem
from vivek.domain.exceptions.exception import PlanningException

class DependencyResolver:
    """Resolve work item dependencies and determine execution order."""

    @staticmethod
    def resolve(work_items: List[WorkItem]) -> List[WorkItem]:
        """Resolve dependencies using topological sort (Kahn's algorithm).

        Args:
            work_items: List of work items with dependencies

        Returns:
            List of work items in execution order

        Raises:
            PlanningException: If circular dependency detected
        """
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        item_map = {item.id: item for item in work_items}

        for item in work_items:
            if item.id not in in_degree:
                in_degree[item.id] = 0

        for item in work_items:
            for dep_id in item.dependencies:
                graph[dep_id].append(item.id)
                in_degree[item.id] += 1

        queue = deque([
            item_id for item_id in in_degree if in_degree[item_id] == 0
        ])
        sorted_items = []

        while queue:
            current_id = queue.popleft()
            sorted_items.append(item_map[current_id])

            for neighbor_id in graph[current_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        if len(sorted_items) != len(work_items):
            raise PlanningException("Circular dependency detected")

        return sorted_items
```

---

## Implementation Strategy

### Phase 1: Core Prompt Architecture
- [x] Create `prompt_architecture.py` with factory pattern
- [x] Create `multi_phase_planner_prompts.py` with 3-phase workflow
- [x] Create `granular_sdet_prompts.py` with 5-phase test workflow
- [x] Create `tdd_workflow_orchestrator.py` for orchestration

### Phase 2: Service Implementation
- [ ] Update `planning_service.py` to use multi-phase approach
- [ ] Update `executor_service.py` to handle SDET phases
- [ ] Update quality service for comprehensive evaluation
- [ ] Implement dependency resolver with topological sort

### Phase 3: Integration & Testing
- [ ] Test clarification phase with user mocks
- [ ] Test confirmation phase with loopback scenarios
- [ ] Test decomposition with real work item generation
- [ ] Test TDD workflow orchestration
- [ ] Test dependency resolution
- [ ] 40+ unit tests (mock LLM responses)

---

## Summary Checklist

### Week 3-5 Deliverables

Prompt Architecture:
- [x] PromptFactory and ABC pattern
- [x] Three-phase planner prompts
- [x] Five-phase SDET prompts
- [x] TDD workflow orchestrator

Services:
- [ ] Updated PlannerService (3 phases with loopback)
- [ ] Updated ExecutorService (SDET phase routing)
- [ ] Quality service (completeness + correctness)
- [ ] DependencyResolver (topological sort)

Testing:
- [ ] 40+ unit tests with mock LLM
- [ ] Clarification phase tests
- [ ] Confirmation phase tests
- [ ] Decomposition phase tests
- [ ] SDET workflow tests
- [ ] Dependency resolution tests

---

## User Interaction Points

Unlike the original single-phase approach, the new system requires user input at two critical points:

### 1. Clarification Feedback (Phase 1 Output)
```json
{
  "needs_clarification": true,
  "questions": [
    "Do you need JWT or OAuth?",
    "Single-tenant or multi-tenant?"
  ],
  "reason": "Authentication strategy and scale affect architecture"
}
```

**User Action**: Answer clarifying questions or confirm if all clear.

### 2. Confirmation Feedback (Phase 2 Output)
```json
{
  "understanding": [
    "• Building JWT-based auth system",
    "• Single-tenant architecture",
    "• Support email/password login"
  ],
  "confirmed": false,
  "concerns": "No database specified - using in-memory?"
}
```

**User Action**: Confirm understanding or provide corrections (loops back to Phase 1).

### 3. Final Plan (Phase 3 Output)
Once confirmed, the system generates the complete work plan with all dependencies and TDD phases ready for execution.

---

## Next Steps

**Workstream 3: Orchestration** will implement:
- Execution orchestration across work items
- Dependency resolution and parallel execution
- Inter-work-item context passing
- Test execution and verification
- Plan monitoring and error handling

**Next**: [Workstream 3: Orchestration](WORKSTREAM_3_ORCHESTRATION.md)
