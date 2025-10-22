# Workstream 3: Orchestration & Integration

**Timeline**: Week 5-6
**Goal**: Tie all services together with orchestration logic

**Prerequisites**: Workstreams 1 & 2 complete

---

## Overview

This workstream connects planner, executor, and quality services into a cohesive dual-brain orchestrator.

### Deliverables
- ✅ Dual-brain orchestrator
- ✅ Iteration manager (quality-driven retry logic)
- ✅ Project context builder
- ✅ 20+ integration tests (end-to-end)

---

## Part 1: Dual-Brain Orchestrator

### File: `src/vivek/application/orchestrators/dual_brain_orchestrator.py`

```python
"""Dual-brain orchestrator - coordinates planning and execution."""

from typing import List

from vivek.domain.interfaces.i_planner_service import IPlannerService
from vivek.domain.interfaces.i_executor_service import IExecutorService
from vivek.domain.interfaces.i_quality_service import IQualityService
from vivek.domain.interfaces.i_file_service import IFileService
from vivek.domain.planning.models.plan import Plan
from vivek.domain.models.execution_result import ExecutionResult
from vivek.domain.models.quality_score import QualityScore
from vivek.domain.planning.services.dependency_resolver import DependencyResolver


class DualBrainOrchestrator:
    """Orchestrate dual-brain architecture: planning + execution."""

    def __init__(
        self,
        planner: IPlannerService,
        executor: IExecutorService,
        quality: IQualityService,
        file_service: IFileService,
        max_iterations: int = 1
    ):
        self.planner = planner
        self.executor = executor
        self.quality = quality
        self.file_service = file_service
        self.max_iterations = max_iterations
        self.dependency_resolver = DependencyResolver()

    async def execute_request(
        self,
        user_request: str,
        project_context: str = ""
    ) -> dict:
        """Execute user request end-to-end.

        Args:
            user_request: What user wants to implement
            project_context: Project information

        Returns:
            Dict with results, quality score, files created
        """
        iteration = 0
        quality_score = None

        while iteration < self.max_iterations:
            # Step 1: Planning (Reasoning Brain)
            print(f"🧠 Planning... (iteration {iteration + 1})")
            plan = await self.planner.create_plan(user_request, project_context)
            print(f"📋 Plan created: {len(plan.work_items)} work items")

            # Step 2: Resolve dependencies
            ordered_items = self.dependency_resolver.resolve(plan.work_items)
            print(f"🔗 Dependencies resolved")

            # Step 3: Execution (Code Generation Brain)
            print(f"⚙️  Executing {len(ordered_items)} work items...")
            results = []

            for work_item in ordered_items:
                print(f"  → {work_item.file_path} ({work_item.mode.value})")
                result = await self.executor.execute(work_item)
                results.append(result)

                # Write to file if successful
                if result.success and result.code:
                    self.file_service.write_file(
                        result.file_path,
                        result.code
                    )
                    print(f"    ✅ {result.file_path}")
                else:
                    print(f"    ❌ Failed: {', '.join(result.errors)}")

            # Step 4: Quality Evaluation
            print(f"🔍 Evaluating quality...")
            quality_score = await self.quality.evaluate(results)
            print(f"📊 Quality score: {quality_score.overall:.2f}")

            # Step 5: Decision
            if quality_score.passed:
                print(f"✅ Quality threshold met!")
                break
            else:
                iteration += 1
                if iteration < self.max_iterations:
                    print(f"⚠️  Quality below threshold, retrying...")
                    # TODO: Add feedback to context for retry
                else:
                    print(f"❌ Max iterations reached")

        return {
            "success": quality_score.passed if quality_score else False,
            "results": results,
            "quality_score": quality_score,
            "iterations": iteration + 1,
            "files_created": [r.file_path for r in results if r.success]
        }
```

---

## Part 2: Iteration Manager

### File: `src/vivek/application/orchestrators/iteration_manager.py`

```python
"""Iteration manager - handles quality-driven retries."""

from typing import List, Optional

from vivek.domain.models.execution_result import ExecutionResult
from vivek.domain.models.quality_score import QualityScore


class IterationManager:
    """Manage iteration and feedback loop."""

    def __init__(self, max_iterations: int = 1):
        self.max_iterations = max_iterations
        self.iteration_history = []

    def should_iterate(
        self,
        quality_score: QualityScore,
        current_iteration: int
    ) -> bool:
        """Determine if another iteration is needed.

        Args:
            quality_score: Current quality score
            current_iteration: Current iteration number (0-indexed)

        Returns:
            True if should iterate, False otherwise
        """
        # Don't iterate if passed
        if quality_score.passed:
            return False

        # Don't iterate if max reached
        if current_iteration >= self.max_iterations - 1:
            return False

        return True

    def build_feedback_context(
        self,
        quality_score: QualityScore,
        previous_results: List[ExecutionResult]
    ) -> str:
        """Build context from previous iteration for retry.

        Args:
            quality_score: Quality score from previous iteration
            previous_results: Results from previous iteration

        Returns:
            Feedback context string
        """
        feedback_parts = [
            "Previous attempt did not meet quality standards.",
            "",
            "Issues identified:"
        ]

        for feedback_item in quality_score.feedback:
            feedback_parts.append(f"- {feedback_item}")

        feedback_parts.append("")
        feedback_parts.append("Please address these issues in the next attempt.")

        return "\n".join(feedback_parts)

    def record_iteration(
        self,
        iteration: int,
        results: List[ExecutionResult],
        quality_score: QualityScore
    ):
        """Record iteration for history/debugging."""
        self.iteration_history.append({
            "iteration": iteration,
            "quality_score": quality_score.overall,
            "passed": quality_score.passed,
            "num_results": len(results)
        })
```

---

## Part 3: Project Context Builder

### File: `src/vivek/application/services/project_context_builder.py`

```python
"""Build project context for LLM prompts."""

from pathlib import Path
from typing import Dict, List


class ProjectContextBuilder:
    """Build context about project for planner."""

    def build_context(self, project_root: Path) -> str:
        """Build project context.

        Args:
            project_root: Project root directory

        Returns:
            Context string
        """
        context_parts = []

        # 1. Detect language
        language = self._detect_language(project_root)
        context_parts.append(f"Primary Language: {language}")

        # 2. Detect framework
        framework = self._detect_framework(project_root, language)
        if framework:
            context_parts.append(f"Framework: {framework}")

        # 3. File structure (1 level)
        structure = self._get_structure(project_root)
        context_parts.append(f"\nProject Structure:\n{structure}")

        # 4. Existing patterns
        patterns = self._detect_patterns(project_root, language)
        if patterns:
            context_parts.append(f"\nExisting Patterns:\n{patterns}")

        return "\n".join(context_parts)

    def _detect_language(self, project_root: Path) -> str:
        """Detect primary language."""
        # Count file extensions
        extensions = {}
        for file in project_root.rglob("*.py"):
            extensions["python"] = extensions.get("python", 0) + 1
        for file in project_root.rglob("*.ts"):
            extensions["typescript"] = extensions.get("typescript", 0) + 1
        for file in project_root.rglob("*.go"):
            extensions["go"] = extensions.get("go", 0) + 1

        if not extensions:
            return "unknown"

        # Return most common
        return max(extensions, key=extensions.get)

    def _detect_framework(self, project_root: Path, language: str) -> str:
        """Detect framework."""
        if language == "python":
            # Check for framework files
            if (project_root / "requirements.txt").exists():
                requirements = (project_root / "requirements.txt").read_text()
                if "fastapi" in requirements.lower():
                    return "FastAPI"
                elif "flask" in requirements.lower():
                    return "Flask"
                elif "django" in requirements.lower():
                    return "Django"
        elif language == "typescript":
            if (project_root / "package.json").exists():
                package = (project_root / "package.json").read_text()
                if "next" in package:
                    return "Next.js"
                elif "react" in package:
                    return "React"

        return "unknown"

    def _get_structure(self, project_root: Path) -> str:
        """Get project structure (1 level)."""
        lines = []
        for item in sorted(project_root.iterdir()):
            if item.name.startswith("."):
                continue
            if item.name in ("node_modules", "venv", "__pycache__"):
                continue

            if item.is_dir():
                lines.append(f"├── {item.name}/")
            else:
                lines.append(f"├── {item.name}")

        return "\n".join(lines[:20])  # Limit to 20 items

    def _detect_patterns(self, project_root: Path, language: str) -> str:
        """Detect coding patterns."""
        patterns = []

        if language == "python":
            # Check for common patterns
            src_dir = project_root / "src"
            tests_dir = project_root / "tests"

            if src_dir.exists():
                patterns.append("- Source code in src/")
            if tests_dir.exists():
                patterns.append("- Tests in tests/")

            # Check for type hints
            sample_files = list(project_root.rglob("*.py"))[:5]
            if sample_files:
                has_type_hints = any(
                    "->" in f.read_text() for f in sample_files
                )
                if has_type_hints:
                    patterns.append("- Uses type hints")

        return "\n".join(patterns) if patterns else "None detected"
```

---

## Part 4: Integration Tests

### File: `tests/integration/test_end_to_end_simple.py`

```python
"""End-to-end integration test."""

import pytest
from pathlib import Path

from vivek.application.orchestrators.dual_brain_orchestrator import DualBrainOrchestrator
from vivek.domain.planning.services.planner_service import PlannerService
from vivek.domain.execution.services.executor_service import ExecutorService
from vivek.domain.execution.modes.coder_mode import CoderMode
from vivek.domain.execution.modes.sdet_mode import SDETMode
from vivek.domain.quality.services.quality_service import QualityService
from vivek.infrastructure.file_operations.file_service import FileService
from vivek.infrastructure.llm.mock_provider import MockProvider


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator with mock LLM."""

    # Mock LLM responses
    mock_llm = MockProvider(responses={
        "planner": """
        {
          "work_items": [
            {
              "id": "item_1",
              "file_path": "src/hello.py",
              "description": "Create hello function",
              "mode": "coder",
              "language": "python",
              "file_status": "new",
              "dependencies": []
            }
          ]
        }
        """,
        "coder": """
def hello(name: str) -> str:
    \"\"\"Say hello.\"\"\"
    return f"Hello, {name}!"
        """,
        "quality": """
        {
          "completeness": 1.0,
          "correctness": 1.0,
          "feedback": ["Code looks good"]
        }
        """
    })

    # Create services
    planner = PlannerService(mock_llm)
    coder_mode = CoderMode(mock_llm)
    sdet_mode = SDETMode(mock_llm, FileService())
    executor = ExecutorService(coder_mode, sdet_mode)
    quality = QualityService(mock_llm, threshold=0.75)
    file_service = FileService()

    # Create orchestrator
    orchestrator = DualBrainOrchestrator(
        planner=planner,
        executor=executor,
        quality=quality,
        file_service=file_service,
        max_iterations=1
    )

    return orchestrator


@pytest.mark.asyncio
async def test_end_to_end_simple_request(orchestrator, tmp_path):
    """Test simple end-to-end request."""

    # Change to temp directory
    import os
    os.chdir(tmp_path)

    # Execute request
    result = await orchestrator.execute_request(
        user_request="Create a hello function",
        project_context="Python project"
    )

    # Assertions
    assert result["success"] is True
    assert len(result["files_created"]) == 1
    assert result["files_created"][0] == "src/hello.py"
    assert result["iterations"] == 1
    assert result["quality_score"].overall >= 0.75

    # Check file was created
    hello_file = tmp_path / "src" / "hello.py"
    assert hello_file.exists()
    content = hello_file.read_text()
    assert "def hello" in content
```

---

## Summary Checklist

### Week 5-6 Deliverables

- [ ] Orchestrator implemented:
  - [ ] DualBrainOrchestrator
  - [ ] IterationManager
  - [ ] ProjectContextBuilder
- [ ] Integration tests:
  - [ ] End-to-end simple request
  - [ ] End-to-end with dependencies
  - [ ] End-to-end with quality iteration
  - [ ] 20+ integration tests total
- [ ] All services working together
- [ ] Real project tested

### Ready for Workstream 4?

✅ Orchestrator working end-to-end
✅ Integration tests passing
✅ Can generate 3-5 files with tests
✅ Quality gate working

**Next**: [Workstream 4: CLI & Polish](WORKSTREAM_4_CLI_POLISH.md)
