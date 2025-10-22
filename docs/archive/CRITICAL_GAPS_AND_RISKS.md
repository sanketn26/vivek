# Critical Gaps & Risks Analysis for v4.0.0

> ⚠️ **ARCHIVED**: This document has been superseded by the workstream documents.
> All gaps identified here have been addressed in the workstreams.
> See [V4_IMPLEMENTATION_INDEX.md](../V4_IMPLEMENTATION_INDEX.md) for current documentation.

**Document Type**: Risk Assessment & Gap Analysis
**Version**: 1.0
**Last Updated**: October 22, 2025
**Status**: ARCHIVED
**Priority**: HIGH - Address before Week 1 implementation

---

## Executive Summary

After reviewing the three planning documents (Migration Roadmap, Tools Integration, Folder Organization), I've identified **15 critical gaps** that could derail the v4.0.0 implementation if not addressed.

### Severity Levels
- 🔴 **CRITICAL**: Will block implementation or cause major failures
- 🟡 **HIGH**: Significant risk, needs planning before implementation
- 🟢 **MEDIUM**: Should be addressed but not blocking

---

## Part 1: Architecture & Design Gaps

### 🔴 GAP 1: Missing API Contracts Between Services

**Problem**: No interface definitions between planner, executor, and quality services.

**What's Missing**:
```python
# Where are these defined?
class IPlannerService(Protocol):
    """Interface for planner service."""
    def create_plan(self, request: str, context: ProjectContext) -> Plan:
        ...

class IExecutorService(Protocol):
    """Interface for executor service."""
    def execute(self, work_item: WorkItem) -> ExecutionResult:
        ...

class IQualityService(Protocol):
    """Interface for quality service."""
    def evaluate(self, results: List[ExecutionResult]) -> QualityScore:
        ...
```

**Impact**: Without clear interfaces, components won't integrate smoothly.

**Solution**: Create `src/vivek/domain/interfaces/` with:
- `i_planner_service.py`
- `i_executor_service.py`
- `i_quality_service.py`
- `i_file_operations.py`
- `i_llm_provider.py` (already exists but needs update)

**Add to Week 1 Deliverables**.

---

### 🔴 GAP 2: Missing Error Handling Strategy

**Problem**: No unified error handling approach across services.

**What's Missing**:
- Custom exception hierarchy
- Error propagation strategy
- Retry logic specification
- User-facing error messages

**Example Issues**:
```python
# What happens when LLM times out?
# What happens when file write fails?
# What happens when quality check fails after max iterations?
# How do we report these to user?
```

**Solution**: Create `src/vivek/domain/exceptions/`:
```python
# vivek_exceptions.py
class VivekException(Exception):
    """Base exception."""
    pass

class PlanningException(VivekException):
    """Planning failed."""
    pass

class ExecutionException(VivekException):
    """Execution failed."""
    pass

class QualityException(VivekException):
    """Quality check failed."""
    pass

class LLMException(VivekException):
    """LLM provider error."""
    def __init__(self, message: str, provider: str, retry_after: Optional[int] = None):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(message)
```

**Add to Week 1 Deliverables**.

---

### 🟡 GAP 3: Missing Data Models Specification

**Problem**: Documents mention models but don't define their attributes.

**What's Missing**: Detailed field definitions for:

```python
@dataclass
class WorkItem:
    """Work item for execution."""
    id: str                           # UUID
    file_path: str                    # Relative to project root
    description: str                  # What to implement
    mode: ExecutionMode               # coder, sdet, architect, peer
    language: str                     # python, typescript, etc.
    file_status: str                  # "new" or "existing"
    dependencies: List[str]           # List of work_item IDs
    context: Optional[str] = None     # Additional context
    priority: int = 0                 # Execution priority

    # Missing: How do we know what to generate?
    # Missing: Reference to related files?
    # Missing: Expected output type?

@dataclass
class ExecutionResult:
    """Result of executing a work item."""
    work_item_id: str
    success: bool
    code: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Missing: Token count?
    # Missing: Execution time?
    # Missing: File path where written?

@dataclass
class QualityScore:
    """Quality evaluation score."""
    overall: float                    # 0.0-1.0
    completeness: float               # 0.0-1.0
    correctness: float                # 0.0-1.0

    # Missing: Detailed feedback?
    # Missing: Which criteria failed?
    # Missing: Suggestions for improvement?

@dataclass
class Plan:
    """Execution plan."""
    work_items: List[WorkItem]

    # Missing: Plan metadata (creation time, model used, tokens)?
    # Missing: Dependency graph representation?
    # Missing: Estimated completion time?
```

**Solution**: Create detailed model specs in Week 1.

---

### 🔴 GAP 4: Missing Prompt Engineering Strategy

**Problem**: No concrete prompt templates or versioning strategy.

**What's Missing**:
- Actual prompt text for planner
- Actual prompt text for executor (coder mode)
- Actual prompt text for executor (sdet mode)
- Actual prompt text for quality evaluator
- Prompt versioning (what if we change prompts?)
- A/B testing strategy

**Example Needed**:
```python
# planner_prompts.py
PLANNER_SYSTEM_PROMPT_V1 = """
You are an expert software architect. Your task is to decompose user requests into actionable work items.

Rules:
1. Create 3-5 work items maximum
2. Each work item must have a clear description
3. Identify dependencies between work items
4. Specify the execution mode (coder or sdet)
5. Output in JSON format

Output format:
{
  "work_items": [
    {
      "id": "item_1",
      "file_path": "src/module.py",
      "description": "...",
      "mode": "coder",
      "dependencies": []
    }
  ]
}
"""

PLANNER_USER_PROMPT_TEMPLATE = """
Project Context:
{project_context}

User Request:
{user_request}

Generate a plan with 3-5 work items.
"""
```

**Solution**:
- Create `src/vivek/prompts/` with **actual prompt text**
- Include version numbers in prompts
- Add prompt testing strategy

**Add to Week 1 Deliverables**.

---

## Part 2: Implementation Gaps

### 🔴 GAP 5: Missing Logging & Observability

**Problem**: No logging strategy defined.

**What's Missing**:
- What to log at each stage?
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Structured logging format
- Performance metrics logging

**Example Needed**:
```python
import logging
from typing import Any

logger = logging.getLogger("vivek")

# What should we log?
# - Planner input/output?
# - Executor progress (each file)?
# - Quality scores?
# - LLM API calls (tokens, latency)?
# - File operations?
# - Errors?

# Structured logging
logger.info(
    "planner_completed",
    extra={
        "work_items_count": 5,
        "dependencies_count": 3,
        "tokens_used": 1500,
        "latency_ms": 2300
    }
)
```

**Solution**: Create `src/vivek/infrastructure/logging/`:
- `logger_config.py` - Logging configuration
- `structured_logger.py` - Structured logging wrapper
- `performance_tracker.py` - Track metrics

**Add to Week 2 Deliverables**.

---

### 🟡 GAP 6: Missing Dependency Injection Container Details

**Problem**: DI container exists but no specification for v4.0.0 services.

**What's Missing**:
```python
# di_container.py - How does this look for v4.0.0?

class DIContainer:
    """Dependency injection container."""

    def __init__(self, config: Settings):
        self.config = config

        # LLM providers
        self._llm_provider = None

        # NEW: How do we register these?
        self._planner_service = None
        self._executor_service = None
        self._quality_service = None
        self._file_service = None

        # How do we handle different modes?
        # How do we inject dependencies?

    def get_orchestrator(self) -> DualBrainOrchestrator:
        """Get orchestrator with all dependencies."""
        return DualBrainOrchestrator(
            planner=self.get_planner_service(),
            executor=self.get_executor_service(),
            quality=self.get_quality_service(),
            iteration_manager=self.get_iteration_manager()
        )
```

**Solution**: Update DI container specification in Week 1.

---

### 🔴 GAP 7: Missing Project Context Detection Logic

**Problem**: "Project context" mentioned but not defined.

**What's Missing**:
```python
# How do we detect?
# - Language (Python, TypeScript, Go)?
# - Framework (FastAPI, Flask, Django, Express)?
# - Project structure (where are src files, tests)?
# - Dependencies (requirements.txt, package.json)?
# - Coding conventions (linting rules)?
# - Existing patterns (how are tests written)?

class ProjectContextBuilder:
    """Build project context."""

    def build(self, project_root: Path) -> ProjectContext:
        """Build context from project."""
        # How do we do this?

        # 1. Detect language
        language = self._detect_language(project_root)

        # 2. Detect framework
        framework = self._detect_framework(project_root, language)

        # 3. Extract file structure
        structure = self._extract_structure(project_root)

        # 4. Parse dependencies
        dependencies = self._parse_dependencies(project_root, language)

        # 5. Detect conventions
        conventions = self._detect_conventions(project_root)

        return ProjectContext(
            language=language,
            framework=framework,
            structure=structure,
            dependencies=dependencies,
            conventions=conventions
        )

    def _detect_language(self, root: Path) -> str:
        """Detect primary language."""
        # Count file extensions?
        # Check for specific files (setup.py, package.json)?
        pass
```

**Solution**:
- Specify detection heuristics
- Create `src/vivek/application/services/project_context_builder.py` with detailed logic

**Add to Week 5 Deliverables** (but design in Week 1).

---

### 🟡 GAP 8: Missing Concurrency & State Management

**Problem**: No strategy for handling concurrent requests or state.

**What's Missing**:
- Can multiple requests run simultaneously?
- How do we manage state during execution?
- What if user cancels mid-execution?
- How do we handle long-running requests?

**Example Questions**:
```python
# User runs: vivek chat "Create feature A"
# While that's running, user runs: vivek chat "Create feature B"
# What happens?

# Should we:
# 1. Queue requests (sequential)?
# 2. Block second request?
# 3. Allow concurrent execution?

# State management:
# - Where do we store in-progress plans?
# - Where do we store partial results?
# - How do we recover from crashes?
```

**Solution**:
- For v4.0.0: **Sequential execution only** (simplest)
- Add to config: `max_concurrent_requests: 1`
- For v4.1.0+: Add job queue

**Document in Week 1, implement in Week 2**.

---

## Part 3: Testing Gaps

### 🟡 GAP 9: Missing Test Data & Fixtures

**Problem**: No test fixtures or sample projects defined.

**What's Missing**:
```
tests/fixtures/
├── sample_projects/
│   ├── empty_python_project/
│   │   ├── src/
│   │   └── tests/
│   │
│   ├── fastapi_simple/          # What does this contain?
│   │   ├── src/
│   │   │   ├── main.py          # What's in here?
│   │   │   └── models/
│   │   ├── tests/
│   │   └── requirements.txt
│   │
│   └── existing_project/         # For testing existing file edits
│
└── expected_outputs/
    ├── coder_mode_output.py      # Expected output for coder mode
    └── sdet_mode_output.py       # Expected output for sdet mode
```

**Solution**: Create test fixtures in Week 1-2 before writing integration tests.

---

### 🟡 GAP 10: Missing Performance Benchmarks

**Problem**: Target times mentioned but no benchmark suite.

**What's Missing**:
```python
# How do we measure?
# - End-to-end latency?
# - LLM API call time?
# - File I/O time?
# - Quality evaluation time?

# Example benchmark suite:
class TestPerformance:
    """Performance benchmarks."""

    def test_simple_request_under_20s(self):
        """Simple request completes in <20s."""
        start = time.time()
        result = orchestrator.execute("Create simple function")
        duration = time.time() - start

        assert duration < 20
        assert result.success

    def test_medium_request_under_35s(self):
        """Medium request (3-4 files) completes in <35s."""
        # ...

    def test_token_usage_under_4k(self):
        """Simple request uses <4k tokens."""
        # ...
```

**Solution**: Create `tests/performance/test_benchmarks.py` in Week 7.

---

### 🔴 GAP 11: Missing Mocking Strategy for LLM Calls

**Problem**: Can't test without real LLM calls (slow, costly, non-deterministic).

**What's Missing**:
```python
# How do we mock LLM responses for testing?

class MockLLMProvider(LLMProvider):
    """Mock LLM for testing."""

    def __init__(self, responses: Dict[str, str]):
        """Initialize with pre-defined responses."""
        self.responses = responses

    async def generate(self, prompt: str, **kwargs) -> str:
        """Return mock response based on prompt."""
        # How do we match prompt to response?
        # Use prompt hash?
        # Use keyword matching?
        # Use fixtures?

        if "create plan" in prompt:
            return self.responses["planner_response"]
        elif "generate code" in prompt:
            return self.responses["coder_response"]
        else:
            raise ValueError(f"No mock response for prompt: {prompt[:50]}")

# Test fixtures
MOCK_PLANNER_RESPONSE = """
{
  "work_items": [
    {
      "id": "item_1",
      "file_path": "src/module.py",
      "description": "Create module",
      "mode": "coder",
      "dependencies": []
    }
  ]
}
"""

MOCK_CODER_RESPONSE = """
def hello():
    return "world"
"""
```

**Solution**:
- Enhance `MockProvider` with fixture-based responses
- Create `tests/fixtures/llm_responses/` with sample responses

**Add to Week 1 Deliverables**.

---

## Part 4: Configuration & Deployment Gaps

### 🟡 GAP 12: Missing Configuration Validation

**Problem**: No validation for config.yml.

**What's Missing**:
```python
# config.yml can have invalid values
llm_configuration:
  planner:
    temperature: 5.0     # Invalid! (should be 0.0-1.0)
    max_tokens: -100     # Invalid!
    provider: "fake"     # Invalid provider

# Need Pydantic validation
from pydantic import BaseSettings, Field, validator

class LLMConfig(BaseSettings):
    """LLM configuration."""
    provider: str = Field(..., regex="^(ollama|openai|anthropic)$")
    model: str
    temperature: float = Field(..., ge=0.0, le=1.0)
    max_tokens: int = Field(..., gt=0, le=100000)

    @validator('model')
    def validate_model(cls, v, values):
        """Validate model exists for provider."""
        provider = values.get('provider')
        valid_models = {
            'ollama': ['qwen2.5-coder:7b', ...],
            'openai': ['gpt-4', 'gpt-3.5-turbo', ...],
        }
        if v not in valid_models.get(provider, []):
            raise ValueError(f"Invalid model {v} for provider {provider}")
        return v
```

**Solution**: Use Pydantic for all config validation in Week 2.

---

### 🟡 GAP 13: Missing Installation & Setup Documentation

**Problem**: How does user install and configure Vivek v4.0.0?

**What's Missing**:
```bash
# Installation
pip install vivek

# First-time setup
vivek init

# What does init do?
# - Create .vivek/ directory?
# - Create config.yml with defaults?
# - Detect project type?
# - Download LLM models (if needed)?

# Configuration
vivek config set llm.provider ollama
vivek config set llm.model qwen2.5-coder:7b

# Usage
vivek chat "Create FastAPI endpoint"
```

**Solution**:
- Create `init_command.py` in Week 7
- Write user guide in Week 8

---

### 🔴 GAP 14: Missing Rollback & Undo Strategy

**Problem**: What if generated code is wrong? Can user undo?

**What's Missing**:
```python
# User runs: vivek chat "Create feature"
# Vivek creates 5 files
# User realizes output is wrong
# How to undo?

# Options:
# 1. Git integration (create branch, commit)?
# 2. Backup files before writing?
# 3. Transaction log?
# 4. No undo (user must use git manually)?

# For v4.0.0: Recommend git workflow
# 1. User creates feature branch
# 2. User runs vivek
# 3. If wrong, user does: git checkout -- .

# For v4.1.0+: Add vivek undo command
```

**Solution**:
- v4.0.0: Document git workflow (no undo command)
- v4.1.0+: Add `vivek undo` or transaction log

**Document in Week 1, implement in v4.1.0**.

---

## Part 5: Documentation Gaps

### 🟡 GAP 15: Missing API Reference Documentation

**Problem**: No detailed API documentation for developers who want to extend Vivek.

**What's Missing**:
```markdown
# API Reference

## Core Classes

### WorkItem
Represents a single unit of work to be executed.

**Attributes**:
- `id` (str): Unique identifier
- `file_path` (str): Relative path to target file
- `description` (str): What to implement
- ...

**Example**:
```python
from vivek.domain.models.work_item import WorkItem

item = WorkItem(
    id="item_1",
    file_path="src/module.py",
    description="Create hello function"
)
```

## Extending Vivek

### Adding a New Execution Mode

1. Create new mode class
2. Implement base mode interface
3. Register in executor service
4. Add prompt template

Example: ...
```

**Solution**: Generate API docs from docstrings using Sphinx in Week 8.

---

## Part 6: Priority Actions

### Immediate (Week 1 - Before Coding)

1. 🔴 **Define API Contracts** (interfaces for all services)
2. 🔴 **Create Exception Hierarchy** (error handling strategy)
3. 🔴 **Write Actual Prompt Templates** (planner, executor, quality)
4. 🔴 **Specify Data Models** (all attributes for WorkItem, ExecutionResult, etc.)
5. 🔴 **Create Mock LLM Strategy** (for testing without real API calls)

### Short-term (Week 1-2)

6. 🟡 **Define Project Context Detection** (heuristics for language, framework)
7. 🟡 **Add Logging Strategy** (what to log, structured format)
8. 🟡 **Update DI Container** (register v4.0.0 services)
9. 🟡 **Create Test Fixtures** (sample projects, expected outputs)
10. 🟡 **Define Concurrency Model** (sequential only for v4.0.0)

### Medium-term (Week 3-7)

11. 🟡 **Config Validation** (Pydantic models)
12. 🟡 **Performance Benchmarks** (measure latency, tokens)
13. 🟡 **Installation & Setup** (init command)
14. 🟡 **Test Data & Fixtures** (complete set)

### Long-term (Week 8 or v4.1.0+)

15. 🟡 **API Documentation** (Sphinx or similar)
16. 🟡 **Rollback Strategy** (undo command)

---

## Part 7: New Documents Needed

Based on gaps identified, create these documents:

### 1. `API_CONTRACTS.md` (CRITICAL - Week 1)
```markdown
# Vivek v4.0.0 API Contracts

## Service Interfaces

### IPlannerService
...

### IExecutorService
...

### IQualityService
...

## Data Models

### WorkItem
Full specification with all attributes, types, validation rules.

### ExecutionResult
...

### QualityScore
...
```

### 2. `ERROR_HANDLING_GUIDE.md` (CRITICAL - Week 1)
```markdown
# Error Handling in Vivek v4.0.0

## Exception Hierarchy
...

## Retry Strategy
...

## User-Facing Messages
...
```

### 3. `PROMPT_LIBRARY.md` (CRITICAL - Week 1)
```markdown
# Vivek Prompt Library

## Planner Prompts
Full text of system and user prompts.

## Executor Prompts (Coder Mode)
...

## Executor Prompts (SDET Mode)
...

## Quality Evaluation Prompts
...
```

### 4. `TESTING_STRATEGY.md` (HIGH - Week 2)
```markdown
# Testing Strategy for v4.0.0

## Unit Testing
...

## Integration Testing
...

## Mocking LLM Calls
...

## Performance Benchmarks
...
```

### 5. `OPERATIONAL_GUIDE.md` (MEDIUM - Week 7)
```markdown
# Operating Vivek v4.0.0

## Installation
...

## Configuration
...

## Logging & Debugging
...

## Troubleshooting
...
```

---

## Summary

### Critical Gaps (Must Address Week 1)
1. ✅ API Contracts (interfaces)
2. ✅ Exception hierarchy
3. ✅ Prompt templates (actual text)
4. ✅ Data model specifications
5. ✅ Mock LLM strategy

### High Priority (Week 1-2)
6. ✅ Project context detection
7. ✅ Logging strategy
8. ✅ DI container update
9. ✅ Test fixtures
10. ✅ Concurrency model

### Recommended Actions
1. **Don't start coding Week 1 until gaps 1-5 are addressed**
2. Create the 5 new documents listed above
3. Review with team before implementation
4. Update roadmap with new deliverables

---

**This analysis should be reviewed before Week 1 implementation starts!**

**Document Status**: Complete - Critical Review Required
**Version**: 1.0
**Last Updated**: October 22, 2025
