# Workstream 2: Core Services

**Timeline**: Week 3-5
**Goal**: Implement planning, execution, and quality services

**Prerequisites**: Workstream 1 complete

---

## Overview

This workstream implements the three core services that power Vivek's dual-brain architecture.

### Deliverables
- ✅ Planner service (decompose requests into work items)
- ✅ Executor service with 2 modes (Coder, SDET)
- ✅ Quality service (evaluate outputs)
- ✅ Dependency resolution
- ✅ Prompt templates
- ✅ 40+ unit tests

### Context Window Strategy

**Problem**: LLMs have limited context windows (typically 8K-32K tokens). Each work item execution needs:
- System prompt (~500 tokens)
- User prompt with context (~2K tokens)
- Output buffer (~2K tokens)
- **Available for code generation: ~4K tokens** (≈200 lines of code)

**Solution**: The planner is designed to create **small, focused work items**:
- ✅ Each work item = ONE file
- ✅ Each file = <200 lines
- ✅ Large features = Multiple work items with dependencies
- ✅ Context includes only relevant dependencies (not entire codebase)

**Example Breakdown**:
```
User request: "Create user authentication system"

❌ BAD (too large):
- item_1: "Create complete auth system" (would generate 1000+ lines)

✅ GOOD (properly scoped):
- item_1: "Create User model (30 lines)"
- item_2: "Create AuthService with login/logout (80 lines)"
- item_3: "Create auth middleware (50 lines)"
- item_4: "Create /login endpoint (40 lines)"
- item_5: "Create tests for AuthService (100 lines)"
```

This approach ensures each LLM call stays within context limits.

---

## Part 1: Prompt Templates

### File: `src/vivek/prompts/planner_prompts.py`

```python
"""Prompts for planner service."""

PLANNER_SYSTEM_PROMPT = """You are an expert software architect. Your task is to decompose user requests into actionable work items.

Rules:
1. Create 3-5 work items maximum
2. Each work item must be specific and actionable
3. Each work item should target ONE FILE ONLY (keep scope small)
4. Keep each file under 200 lines to fit in LLM context window
5. Break large features into multiple small files instead of one large file
6. Identify dependencies between work items (use work item IDs)
7. Specify execution mode: "coder" for implementation, "sdet" for tests
8. Output ONLY valid JSON, no additional text

Context Window Considerations:
- Each work item will be executed with ~4K tokens of context
- Generated code should be <200 lines per file
- If a feature needs >200 lines, split into multiple files with clear interfaces

Output format:
{
  "work_items": [
    {
      "id": "item_1",
      "file_path": "src/models/user.py",
      "description": "Create User Pydantic model with email and password fields only",
      "mode": "coder",
      "language": "python",
      "file_status": "new",
      "dependencies": []
    },
    {
      "id": "item_2",
      "file_path": "src/services/auth_service.py",
      "description": "Create AuthService with login method using User model",
      "mode": "coder",
      "language": "python",
      "file_status": "new",
      "dependencies": ["item_1"]
    },
    {
      "id": "item_3",
      "file_path": "tests/test_auth_service.py",
      "description": "Write tests for AuthService login method (3-5 test cases)",
      "mode": "sdet",
      "language": "python",
      "file_status": "new",
      "dependencies": ["item_2"]
    }
  ]
}

Good Example (Small Scoped Work Items):
✅ "Create User model with 3 fields: email, password, full_name"
✅ "Create AuthService with single login() method"
✅ "Write 5 tests for login success and failure cases"

Bad Example (Too Large for Context Window):
❌ "Create complete user authentication system with models, services, routes, middleware, and tests"
❌ "Build entire REST API with 10 endpoints"
"""

PLANNER_USER_PROMPT_TEMPLATE = """Project Context:
{project_context}

User Request:
{user_request}

Generate a plan with 3-5 work items. Include at least one test file (sdet mode).
Output ONLY the JSON plan, nothing else."""


def build_planner_prompt(user_request: str, project_context: str) -> dict:
    """Build planner prompt.

    Args:
        user_request: What user wants to implement
        project_context: Project information

    Returns:
        Dict with system and user prompts
    """
    return {
        "system": PLANNER_SYSTEM_PROMPT,
        "user": PLANNER_USER_PROMPT_TEMPLATE.format(
            project_context=project_context,
            user_request=user_request
        )
    }
```

### File: `src/vivek/prompts/executor_prompts.py`

```python
"""Prompts for executor service."""

CODER_SYSTEM_PROMPT = """You are an expert software engineer. Generate production-quality code.

Requirements:
1. Follow best practices for the language
2. Include proper error handling
3. Add type hints (Python) or types (TypeScript)
4. Write clear docstrings/comments
5. Follow DRY principle
6. Output ONLY code, no explanations

Code style:
- Python: Follow PEP 8, use type hints
- TypeScript: Use strict types
- All: Keep functions small (<50 lines)
"""

CODER_USER_PROMPT_TEMPLATE = """File: {file_path}
Language: {language}
Task: {description}

Context from related files:
{context}

Generate the complete file content. Output ONLY the code."""


SDET_SYSTEM_PROMPT = """You are an expert SDET (Software Development Engineer in Test). Generate comprehensive tests.

Requirements:
1. Use pytest for Python, Jest for TypeScript
2. Test happy paths and edge cases
3. Aim for 80%+ coverage
4. Use descriptive test names
5. Include fixtures where appropriate
6. Output ONLY test code, no explanations

Test structure:
- Group related tests in classes
- One assertion per test (prefer)
- Test error cases with pytest.raises or expect().toThrow()
"""

SDET_USER_PROMPT_TEMPLATE = """Test file: {file_path}
Language: {language}
Task: {description}

Code to test:
{code_to_test}

Generate comprehensive tests. Output ONLY the test code."""


def build_coder_prompt(work_item, context: str = "") -> dict:
    """Build coder mode prompt."""
    return {
        "system": CODER_SYSTEM_PROMPT,
        "user": CODER_USER_PROMPT_TEMPLATE.format(
            file_path=work_item.file_path,
            language=work_item.language,
            description=work_item.description,
            context=context or "No additional context"
        )
    }


def build_sdet_prompt(work_item, code_to_test: str) -> dict:
    """Build SDET mode prompt."""
    return {
        "system": SDET_SYSTEM_PROMPT,
        "user": SDET_USER_PROMPT_TEMPLATE.format(
            file_path=work_item.file_path,
            language=work_item.language,
            description=work_item.description,
            code_to_test=code_to_test
        )
    }
```

### File: `src/vivek/prompts/quality_prompts.py`

```python
"""Prompts for quality evaluation."""

QUALITY_SYSTEM_PROMPT = """You are a code quality evaluator. Assess code quality objectively.

Evaluation criteria:
1. Completeness (0.0-1.0): Are all requirements met?
2. Correctness (0.0-1.0): Is the code syntactically correct?

Output format (JSON only):
{
  "completeness": 0.85,
  "correctness": 1.0,
  "feedback": [
    "Missing error handling for network requests",
    "All type hints present"
  ]
}
"""

QUALITY_USER_PROMPT_TEMPLATE = """Requirements:
{requirements}

Generated code:
{code}

Evaluate completeness and correctness. Output ONLY JSON."""


def build_quality_prompt(requirements: str, code: str) -> dict:
    """Build quality evaluation prompt."""
    return {
        "system": QUALITY_SYSTEM_PROMPT,
        "user": QUALITY_USER_PROMPT_TEMPLATE.format(
            requirements=requirements,
            code=code
        )
    }
```

---

## Part 2: Planner Service

### File: `src/vivek/domain/planning/services/planner_service.py`

```python
"""Planner service implementation."""

import json
from typing import Optional

from vivek.domain.interfaces.i_planner_service import IPlannerService
from vivek.domain.planning.models.plan import Plan
from vivek.domain.models.work_item import WorkItem, ExecutionMode
from vivek.domain.exceptions.vivek_exceptions import PlanningException
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.prompts.planner_prompts import build_planner_prompt


class PlannerService(IPlannerService):
    """Service for planning and decomposition."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def create_plan(
        self,
        user_request: str,
        project_context: str
    ) -> Plan:
        """Create execution plan from user request.

        Args:
            user_request: What user wants to implement
            project_context: Project information

        Returns:
            Plan with 3-5 work items

        Raises:
            PlanningException: If planning fails
        """
        try:
            # Build prompt
            prompts = build_planner_prompt(user_request, project_context)

            # Call LLM
            response = await self.llm.generate(
                system_prompt=prompts["system"],
                user_prompt=prompts["user"]
            )

            # Parse response
            plan_data = json.loads(response)

            # Convert to WorkItem objects
            work_items = []
            for item_data in plan_data["work_items"]:
                work_item = WorkItem(
                    id=item_data["id"],
                    file_path=item_data["file_path"],
                    description=item_data["description"],
                    mode=ExecutionMode(item_data["mode"]),
                    language=item_data.get("language", "python"),
                    file_status=item_data.get("file_status", "new"),
                    dependencies=item_data.get("dependencies", [])
                )
                work_items.append(work_item)

            # Validate plan
            self._validate_plan(work_items)

            return Plan(work_items=work_items)

        except json.JSONDecodeError as e:
            raise PlanningException(f"Failed to parse LLM response: {e}")
        except Exception as e:
            raise PlanningException(f"Planning failed: {e}")

    def _validate_plan(self, work_items: list) -> None:
        """Validate plan."""
        if not work_items:
            raise PlanningException("Plan must have at least one work item")

        if len(work_items) > 5:
            raise PlanningException("Plan cannot have more than 5 work items")

        # Check for circular dependencies
        self._check_circular_dependencies(work_items)

    def _check_circular_dependencies(self, work_items: list) -> None:
        """Check for circular dependencies."""
        # Simple implementation: check each item doesn't depend on itself
        item_ids = {item.id for item in work_items}

        for item in work_items:
            if item.id in item.dependencies:
                raise PlanningException(
                    f"Circular dependency detected: {item.id}"
                )

            # Check dependencies exist
            for dep_id in item.dependencies:
                if dep_id not in item_ids:
                    raise PlanningException(
                        f"Unknown dependency: {dep_id} in {item.id}"
                    )
```

---

## Part 3: Executor Service

### File: `src/vivek/domain/execution/modes/base_mode.py`

```python
"""Base execution mode."""

from abc import ABC, abstractmethod

from vivek.domain.models.work_item import WorkItem
from vivek.domain.models.execution_result import ExecutionResult


class BaseMode(ABC):
    """Base class for execution modes."""

    @abstractmethod
    async def execute(
        self,
        work_item: WorkItem,
        context: dict
    ) -> ExecutionResult:
        """Execute work item.

        Args:
            work_item: Work item to execute
            context: Execution context

        Returns:
            Execution result
        """
        pass

    @abstractmethod
    def validate_output(self, code: str, language: str) -> list:
        """Validate generated code.

        Args:
            code: Generated code
            language: Programming language

        Returns:
            List of validation errors (empty if valid)
        """
        pass
```

### File: `src/vivek/domain/execution/modes/coder_mode.py`

```python
"""Coder mode implementation."""

import ast

from vivek.domain.execution.modes.base_mode import BaseMode
from vivek.domain.models.work_item import WorkItem
from vivek.domain.models.execution_result import ExecutionResult
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.prompts.executor_prompts import build_coder_prompt


class CoderMode(BaseMode):
    """Coder mode - generates implementation code."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def execute(
        self,
        work_item: WorkItem,
        context: dict
    ) -> ExecutionResult:
        """Execute work item in coder mode."""

        # Build prompt
        prompts = build_coder_prompt(
            work_item,
            context=context.get("related_files", "")
        )

        # Generate code
        code = await self.llm.generate(
            system_prompt=prompts["system"],
            user_prompt=prompts["user"]
        )

        # Validate
        errors = self.validate_output(code, work_item.language)

        # Create result
        result = ExecutionResult(
            work_item_id=work_item.id,
            success=len(errors) == 0,
            code=code,
            file_path=work_item.file_path,
            errors=errors
        )

        return result

    def validate_output(self, code: str, language: str) -> list:
        """Validate generated code."""
        errors = []

        if language == "python":
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append(f"Syntax error at line {e.lineno}: {e.msg}")

        return errors
```

### File: `src/vivek/domain/execution/modes/sdet_mode.py`

```python
"""SDET mode implementation."""

import ast

from vivek.domain.execution.modes.base_mode import BaseMode
from vivek.domain.models.work_item import WorkItem
from vivek.domain.models.execution_result import ExecutionResult
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.infrastructure.file_operations.file_service import FileService
from vivek.prompts.executor_prompts import build_sdet_prompt


class SDETMode(BaseMode):
    """SDET mode - generates tests."""

    def __init__(self, llm_provider: LLMProvider, file_service: FileService):
        self.llm = llm_provider
        self.file_service = file_service

    async def execute(
        self,
        work_item: WorkItem,
        context: dict
    ) -> ExecutionResult:
        """Execute work item in SDET mode."""

        # Get code to test from dependencies
        code_to_test = context.get("code_to_test", "")

        if not code_to_test:
            # Try to read from file if it exists
            if work_item.dependencies:
                # Get file path from first dependency
                dep_file = context.get("dependency_files", {}).get(
                    work_item.dependencies[0]
                )
                if dep_file and self.file_service.file_exists(dep_file):
                    code_to_test = self.file_service.read_file(dep_file)

        # Build prompt
        prompts = build_sdet_prompt(work_item, code_to_test)

        # Generate tests
        test_code = await self.llm.generate(
            system_prompt=prompts["system"],
            user_prompt=prompts["user"]
        )

        # Validate
        errors = self.validate_output(test_code, work_item.language)

        # Create result
        result = ExecutionResult(
            work_item_id=work_item.id,
            success=len(errors) == 0,
            code=test_code,
            file_path=work_item.file_path,
            errors=errors
        )

        return result

    def validate_output(self, code: str, language: str) -> list:
        """Validate generated test code."""
        errors = []

        if language == "python":
            try:
                ast.parse(code)
                # Check for pytest
                if "import pytest" not in code and "from pytest" not in code:
                    errors.append("Warning: No pytest import found")
            except SyntaxError as e:
                errors.append(f"Syntax error at line {e.lineno}: {e.msg}")

        return errors
```

### File: `src/vivek/domain/execution/services/executor_service.py`

```python
"""Executor service implementation."""

from typing import Dict

from vivek.domain.interfaces.i_executor_service import IExecutorService
from vivek.domain.models.work_item import WorkItem, ExecutionMode
from vivek.domain.models.execution_result import ExecutionResult
from vivek.domain.execution.modes.base_mode import BaseMode
from vivek.domain.execution.modes.coder_mode import CoderMode
from vivek.domain.execution.modes.sdet_mode import SDETMode
from vivek.domain.exceptions.vivek_exceptions import ExecutionException


class ExecutorService(IExecutorService):
    """Service for executing work items."""

    def __init__(
        self,
        coder_mode: CoderMode,
        sdet_mode: SDETMode
    ):
        self.modes: Dict[ExecutionMode, BaseMode] = {
            ExecutionMode.CODER: coder_mode,
            ExecutionMode.SDET: sdet_mode
        }

    async def execute(self, work_item: WorkItem) -> ExecutionResult:
        """Execute a work item.

        Args:
            work_item: Work item to execute

        Returns:
            Execution result

        Raises:
            ExecutionException: If execution fails
        """
        try:
            # Get appropriate mode
            mode = self.modes.get(work_item.mode)
            if not mode:
                raise ExecutionException(
                    f"Unknown execution mode: {work_item.mode}"
                )

            # Build context (simplified for now)
            context = {}

            # Execute
            result = await mode.execute(work_item, context)

            return result

        except Exception as e:
            # Return failed result
            return ExecutionResult(
                work_item_id=work_item.id,
                success=False,
                errors=[str(e)]
            )
```

---

## Part 4: Quality Service

### File: `src/vivek/domain/quality/services/quality_service.py`

```python
"""Quality evaluation service."""

import json
from typing import List

from vivek.domain.interfaces.i_quality_service import IQualityService
from vivek.domain.models.execution_result import ExecutionResult
from vivek.domain.models.quality_score import QualityScore
from vivek.domain.exceptions.vivek_exceptions import QualityException
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.prompts.quality_prompts import build_quality_prompt


class QualityService(IQualityService):
    """Service for evaluating output quality."""

    def __init__(self, llm_provider: LLMProvider, threshold: float = 0.75):
        self.llm = llm_provider
        self.threshold = threshold

    async def evaluate(
        self,
        results: List[ExecutionResult]
    ) -> QualityScore:
        """Evaluate quality of execution results.

        Args:
            results: List of execution results

        Returns:
            Quality score
        """
        try:
            # Check for execution errors first
            if any(not r.success for r in results):
                return QualityScore(
                    overall=0.0,
                    completeness=0.0,
                    correctness=0.0,
                    feedback=["Execution failed for some work items"],
                    passed=False
                )

            # Aggregate all code
            all_code = "\n\n".join(
                f"# {r.file_path}\n{r.code}"
                for r in results if r.code
            )

            # Build requirements from work items
            requirements = "\n".join(
                f"- {r.work_item_id}: Generated code for {r.file_path}"
                for r in results
            )

            # Build prompt
            prompts = build_quality_prompt(requirements, all_code)

            # Call LLM
            response = await self.llm.generate(
                system_prompt=prompts["system"],
                user_prompt=prompts["user"]
            )

            # Parse response
            quality_data = json.loads(response)

            # Calculate overall score
            completeness = quality_data["completeness"]
            correctness = quality_data["correctness"]
            overall = (completeness + correctness) / 2

            # Create score
            score = QualityScore(
                overall=overall,
                completeness=completeness,
                correctness=correctness,
                feedback=quality_data.get("feedback", []),
                passed=overall >= self.threshold
            )

            return score

        except Exception as e:
            raise QualityException(f"Quality evaluation failed: {e}")
```

---

## Part 5: Dependency Resolution

### File: `src/vivek/domain/planning/services/dependency_resolver.py`

```python
"""Dependency resolution service."""

from typing import List, Dict, Set
from collections import defaultdict, deque

from vivek.domain.models.work_item import WorkItem
from vivek.domain.exceptions.vivek_exceptions import PlanningException


class DependencyResolver:
    """Resolve work item dependencies and determine execution order."""

    @staticmethod
    def resolve(work_items: List[WorkItem]) -> List[WorkItem]:
        """Resolve dependencies using topological sort.

        Args:
            work_items: List of work items with dependencies

        Returns:
            List of work items in execution order

        Raises:
            PlanningException: If circular dependency detected
        """
        # Build dependency graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        item_map = {item.id: item for item in work_items}

        # Initialize
        for item in work_items:
            if item.id not in in_degree:
                in_degree[item.id] = 0

        # Build graph
        for item in work_items:
            for dep_id in item.dependencies:
                graph[dep_id].append(item.id)
                in_degree[item.id] += 1

        # Topological sort (Kahn's algorithm)
        queue = deque([
            item_id for item_id in in_degree if in_degree[item_id] == 0
        ])
        sorted_items = []

        while queue:
            current_id = queue.popleft()
            sorted_items.append(item_map[current_id])

            # Reduce in-degree for neighbors
            for neighbor_id in graph[current_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        # Check for cycles
        if len(sorted_items) != len(work_items):
            raise PlanningException("Circular dependency detected")

        return sorted_items
```

---

## Summary Checklist

### Week 3-5 Deliverables

- [ ] Prompts implemented:
  - [ ] Planner prompts
  - [ ] Coder mode prompts
  - [ ] SDET mode prompts
  - [ ] Quality prompts
- [ ] Services implemented:
  - [ ] PlannerService
  - [ ] ExecutorService
  - [ ] CoderMode
  - [ ] SDETMode
  - [ ] QualityService
  - [ ] DependencyResolver
- [ ] 40+ unit tests passing
- [ ] Mock LLM provider for tests

### Ready for Workstream 3?

✅ All services implemented
✅ Prompts tested with real LLM
✅ Dependency resolution working
✅ Tests passing (85%+ coverage)

**Next**: [Workstream 3: Orchestration](WORKSTREAM_3_ORCHESTRATION.md)
