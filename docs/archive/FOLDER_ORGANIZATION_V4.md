# Vivek v4.0.0: Folder Organization & Architecture

> ⚠️ **ARCHIVED**: This document has been superseded by the workstream documents.
> All folder structure details are now in Workstream 1.
> See [V4_IMPLEMENTATION_INDEX.md](../V4_IMPLEMENTATION_INDEX.md) for current documentation.

**Document Type**: Architecture Guide
**Version**: 1.0
**Last Updated**: October 22, 2025
**Status**: ARCHIVED

---

## Executive Summary

This document defines the **folder structure** and **code organization** for Vivek v4.0.0 based on the migration roadmap and tools integration strategy. The structure follows **Clean Architecture** principles with clear separation of concerns.

### Design Principles

1. **Domain-Driven Design (DDD)**: Business logic separated from infrastructure
2. **Clean Architecture**: Dependency inversion (domain → application → infrastructure)
3. **Testability**: Each layer independently testable
4. **Gradual Migration**: v3.0.0 components coexist during transition

---

## Part 1: Current State (v3.0.0)

### Existing Structure

```
vivek/
├── src/vivek/
│   ├── application/
│   │   ├── orchestrators/
│   │   │   └── simple_orchestrator.py      # v3.0.0 orchestrator
│   │   └── services/
│   │       └── vivek_application_service.py
│   │
│   ├── domain/
│   │   ├── planning/
│   │   │   ├── models/
│   │   │   ├── repositories/
│   │   │   └── services/
│   │   └── workflow/
│   │       ├── models/
│   │       ├── repositories/
│   │       └── services/
│   │
│   ├── infrastructure/
│   │   ├── llm/
│   │   │   ├── llm_provider.py
│   │   │   ├── ollama_provider.py
│   │   │   └── mock_provider.py
│   │   └── persistence/
│   │       ├── state_repository.py
│   │       ├── memory_repository.py
│   │       └── file_repository.py
│   │
│   ├── agentic_context/              # Context management
│   ├── utils/                        # Utilities
│   └── cli.py                        # CLI entry point
│
└── tests/                            # Currently minimal
```

### Assessment

**Strengths**:
- ✅ Clean separation (domain, application, infrastructure)
- ✅ DDD structure in place
- ✅ LLM providers abstracted

**Gaps for v4.0.0**:
- ❌ No planner service
- ❌ No executor service
- ❌ No quality service
- ❌ No file operations module
- ❌ Minimal tests
- ❌ No mode-specific implementations

---

## Part 2: Recommended Structure (v4.0.0)

### Complete Folder Organization

```
vivek/
├── src/vivek/
│   │
│   ├── domain/                       # Business Logic (Core)
│   │   │
│   │   ├── models/                   # Domain Models
│   │   │   ├── __init__.py
│   │   │   ├── work_item.py         # WorkItem, WorkItemStatus
│   │   │   ├── execution_result.py  # ExecutionResult
│   │   │   ├── quality_score.py     # QualityScore, QualityCriteria
│   │   │   ├── project_context.py   # ProjectContext
│   │   │   └── execution_mode.py    # ExecutionMode enum
│   │   │
│   │   ├── planning/                 # Planning Domain
│   │   │   ├── __init__.py
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── plan.py          # Plan, PlanItem
│   │   │   │   └── dependency.py    # DependencyGraph
│   │   │   │
│   │   │   ├── services/             # Domain Services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── planner_service.py        # NEW: v4.0.0 planner
│   │   │   │   └── dependency_resolver.py    # NEW: Topological sort
│   │   │   │
│   │   │   └── repositories/         # Interfaces (abstractions)
│   │   │       ├── __init__.py
│   │   │       └── plan_repository.py
│   │   │
│   │   ├── execution/                # NEW: Execution Domain
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   └── execution_context.py
│   │   │   │
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── executor_service.py      # NEW: Base executor
│   │   │   │   └── mode_executor.py         # NEW: Mode-specific logic
│   │   │   │
│   │   │   └── modes/                # NEW: Execution modes
│   │   │       ├── __init__.py
│   │   │       ├── base_mode.py             # Abstract base
│   │   │       ├── coder_mode.py            # NEW: Coder mode
│   │   │       ├── sdet_mode.py             # NEW: SDET mode
│   │   │       ├── architect_mode.py        # v4.1.0+
│   │   │       └── peer_mode.py             # v4.1.0+
│   │   │
│   │   ├── quality/                  # NEW: Quality Domain
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── quality_criteria.py
│   │   │   │   └── quality_feedback.py
│   │   │   │
│   │   │   └── services/
│   │   │       ├── __init__.py
│   │   │       ├── quality_service.py       # NEW: Quality evaluation
│   │   │       ├── completeness_checker.py  # NEW: Completeness
│   │   │       └── correctness_checker.py   # NEW: Correctness
│   │   │
│   │   └── workflow/                 # Existing (may be refactored)
│   │       ├── models/
│   │       ├── repositories/
│   │       └── services/
│   │
│   ├── application/                  # Application Layer (Use Cases)
│   │   │
│   │   ├── orchestrators/
│   │   │   ├── __init__.py
│   │   │   ├── simple_orchestrator.py       # v3.0.0 (keep for now)
│   │   │   ├── dual_brain_orchestrator.py   # NEW: v4.0.0 orchestrator
│   │   │   └── iteration_manager.py         # NEW: Iteration logic
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── vivek_application_service.py # Existing
│   │   │   └── project_context_builder.py   # NEW: Build context
│   │   │
│   │   └── use_cases/                # NEW: Use case handlers
│   │       ├── __init__.py
│   │       ├── generate_code_use_case.py    # Main use case
│   │       └── validate_output_use_case.py
│   │
│   ├── infrastructure/               # Infrastructure Layer (External)
│   │   │
│   │   ├── llm/                      # LLM Providers
│   │   │   ├── __init__.py
│   │   │   ├── llm_provider.py      # Base interface
│   │   │   ├── ollama_provider.py   # Existing
│   │   │   ├── mock_provider.py     # Existing
│   │   │   ├── openai_provider.py   # v4.1.0+
│   │   │   ├── anthropic_provider.py # v4.1.0+
│   │   │   └── provider_factory.py  # NEW: Factory pattern
│   │   │
│   │   ├── file_operations/          # NEW: File I/O
│   │   │   ├── __init__.py
│   │   │   ├── file_service.py      # NEW: Core file ops (pathlib)
│   │   │   ├── directory_service.py # NEW: Directory ops
│   │   │   └── command_executor.py  # NEW: Subprocess wrapper
│   │   │
│   │   ├── code_tools/               # NEW: Code manipulation (v4.1.0+)
│   │   │   ├── __init__.py
│   │   │   ├── ast_transformer.py   # libcst wrapper
│   │   │   ├── template_engine.py   # Jinja2 wrapper
│   │   │   └── tree_sitter_parser.py # tree-sitter wrapper
│   │   │
│   │   ├── validation/               # NEW: Code validation
│   │   │   ├── __init__.py
│   │   │   ├── syntax_validator.py  # ast.parse wrapper
│   │   │   ├── linter_service.py    # flake8/pylint
│   │   │   └── formatter_service.py # black/autopep8
│   │   │
│   │   ├── persistence/              # Existing
│   │   │   ├── __init__.py
│   │   │   ├── state_repository.py
│   │   │   ├── memory_repository.py
│   │   │   └── file_repository.py
│   │   │
│   │   ├── config/                   # NEW: Configuration
│   │   │   ├── __init__.py
│   │   │   ├── config_loader.py     # YAML config loader
│   │   │   ├── settings.py          # Settings model
│   │   │   └── defaults.py          # Default values
│   │   │
│   │   └── di_container.py           # Existing (update for v4)
│   │
│   ├── presentation/                 # NEW: User Interface Layer
│   │   ├── __init__.py
│   │   ├── cli/
│   │   │   ├── __init__.py
│   │   │   ├── main.py              # CLI entry point
│   │   │   ├── commands/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── chat_command.py  # chat command
│   │   │   │   ├── init_command.py  # init command
│   │   │   │   └── config_command.py # config command
│   │   │   │
│   │   │   └── formatters/
│   │   │       ├── __init__.py
│   │   │       ├── progress_formatter.py  # Progress display
│   │   │       └── result_formatter.py    # Result display
│   │   │
│   │   └── api/                      # Future: REST API (v4.2.0+)
│   │       └── __init__.py
│   │
│   ├── agentic_context/              # Existing (refactor for v4)
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── workflow.py
│   │   ├── core/
│   │   │   ├── context_manager.py
│   │   │   └── context_storage.py
│   │   └── retrieval/
│   │       ├── retrieval_strategies.py
│   │       ├── semantic_retrieval.py
│   │       └── tag_normalization.py
│   │
│   ├── utils/                        # Shared Utilities
│   │   ├── __init__.py
│   │   ├── prompt_utils.py          # Existing
│   │   ├── token_counter.py         # Existing
│   │   ├── language_detector.py     # Existing
│   │   ├── path_setup.py            # Existing
│   │   └── context_window_manager.py # NEW: Token budget
│   │
│   ├── templates/                    # NEW: Code templates (v4.1.0+)
│   │   ├── python/
│   │   │   ├── fastapi_endpoint.py.jinja2
│   │   │   ├── pydantic_model.py.jinja2
│   │   │   └── pytest_test.py.jinja2
│   │   └── typescript/
│   │       └── react_component.tsx.jinja2
│   │
│   ├── prompts/                      # NEW: LLM Prompts
│   │   ├── __init__.py
│   │   ├── planner_prompts.py       # Planner prompts
│   │   ├── executor_prompts.py      # Executor prompts
│   │   ├── quality_prompts.py       # Quality prompts
│   │   └── mode_prompts/
│   │       ├── coder_prompt.py
│   │       ├── sdet_prompt.py
│   │       ├── architect_prompt.py  # v4.1.0+
│   │       └── peer_prompt.py       # v4.1.0+
│   │
│   ├── cli.py                        # DEPRECATED: Move to presentation/cli/main.py
│   └── __init__.py
│
├── tests/                            # Test Suite
│   │
│   ├── unit/                         # NEW: Unit tests
│   │   ├── __init__.py
│   │   │
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── planning/
│   │   │   │   ├── test_planner_service.py
│   │   │   │   └── test_dependency_resolver.py
│   │   │   │
│   │   │   ├── execution/
│   │   │   │   ├── test_executor_service.py
│   │   │   │   ├── test_coder_mode.py
│   │   │   │   └── test_sdet_mode.py
│   │   │   │
│   │   │   └── quality/
│   │   │       ├── test_quality_service.py
│   │   │       ├── test_completeness_checker.py
│   │   │       └── test_correctness_checker.py
│   │   │
│   │   ├── application/
│   │   │   ├── test_dual_brain_orchestrator.py
│   │   │   ├── test_iteration_manager.py
│   │   │   └── test_project_context_builder.py
│   │   │
│   │   └── infrastructure/
│   │       ├── test_file_service.py
│   │       ├── test_command_executor.py
│   │       ├── test_syntax_validator.py
│   │       └── test_config_loader.py
│   │
│   ├── integration/                  # NEW: Integration tests
│   │   ├── __init__.py
│   │   ├── test_end_to_end_simple.py
│   │   ├── test_end_to_end_with_tests.py
│   │   ├── test_quality_gate.py
│   │   ├── test_dependency_resolution.py
│   │   └── test_iteration_loop.py
│   │
│   ├── fixtures/                     # NEW: Test fixtures
│   │   ├── __init__.py
│   │   ├── sample_projects/
│   │   │   ├── fastapi_simple/
│   │   │   └── multi_file_project/
│   │   └── expected_outputs/
│   │
│   └── conftest.py                   # pytest configuration
│
├── .vivek/                           # NEW: Default config location
│   └── config.yml                    # Default configuration
│
├── docs/                             # Documentation
│   ├── MIGRATION_ROADMAP_V3_TO_V4.md
│   ├── TOOLS_AND_FILE_INTEGRATION.md
│   ├── FOLDER_ORGANIZATION_V4.md     # This file
│   ├── API_REFERENCE.md              # Future
│   └── ARCHITECTURE.md               # Future
│
├── examples/                         # NEW: Example projects
│   ├── simple_fastapi/
│   ├── database_crud/
│   └── multi_file_feature/
│
├── scripts/                          # Development scripts
│   ├── run_tests.sh
│   ├── format_code.sh
│   └── build.sh
│
├── pyproject.toml                    # Project config
├── setup.py
├── README.md
└── .gitignore
```

---

## Part 3: Week-by-Week Implementation

### Week 1-2: Foundation

**Create these folders/files**:

```
src/vivek/domain/
├── models/
│   ├── work_item.py              ✅ Create
│   ├── execution_result.py       ✅ Create
│   └── execution_mode.py         ✅ Create
│
├── planning/services/
│   └── planner_service.py        ✅ Create (basic)
│
└── execution/
    ├── services/
    │   └── executor_service.py   ✅ Create (basic)
    └── modes/
        ├── base_mode.py          ✅ Create
        └── coder_mode.py         ✅ Create

src/vivek/application/orchestrators/
└── dual_brain_orchestrator.py    ✅ Create (minimal)

src/vivek/infrastructure/
├── file_operations/
│   ├── file_service.py           ✅ Create
│   └── command_executor.py       ✅ Create
│
└── config/
    ├── config_loader.py          ✅ Create
    └── settings.py               ✅ Create

tests/unit/
├── domain/planning/
│   └── test_planner_service.py   ✅ Create (15 tests)
└── domain/execution/
    └── test_executor_service.py  ✅ Create (10 tests)

tests/integration/
└── test_end_to_end_simple.py     ✅ Create (1 test)
```

### Week 3-4: Quality Gate

**Add these folders/files**:

```
src/vivek/domain/quality/
├── models/
│   ├── quality_score.py          ✅ Create
│   └── quality_feedback.py       ✅ Create
│
└── services/
    ├── quality_service.py        ✅ Create
    ├── completeness_checker.py   ✅ Create
    └── correctness_checker.py    ✅ Create

src/vivek/application/orchestrators/
└── iteration_manager.py          ✅ Create

src/vivek/infrastructure/validation/
├── syntax_validator.py           ✅ Create
└── linter_service.py             ✅ Create

src/vivek/prompts/
├── planner_prompts.py            ✅ Create
├── executor_prompts.py           ✅ Create
└── quality_prompts.py            ✅ Create

tests/unit/domain/quality/
├── test_quality_service.py       ✅ Create (20 tests)
├── test_completeness_checker.py  ✅ Create
└── test_correctness_checker.py   ✅ Create

tests/integration/
├── test_quality_gate.py          ✅ Create (5 tests)
└── test_iteration_loop.py        ✅ Create
```

### Week 5-6: Dependencies & SDET Mode

**Add these folders/files**:

```
src/vivek/domain/planning/services/
└── dependency_resolver.py        ✅ Create

src/vivek/domain/execution/modes/
└── sdet_mode.py                  ✅ Create

src/vivek/application/services/
└── project_context_builder.py    ✅ Create

src/vivek/utils/
└── context_window_manager.py     ✅ Create

src/vivek/prompts/mode_prompts/
├── coder_prompt.py               ✅ Create
└── sdet_prompt.py                ✅ Create

.vivek/
└── config.yml                    ✅ Create

tests/unit/domain/planning/
└── test_dependency_resolver.py   ✅ Create (15 tests)

tests/unit/domain/execution/
└── test_sdet_mode.py             ✅ Create (10 tests)

tests/integration/
├── test_dependency_resolution.py ✅ Create (5 tests)
└── test_end_to_end_with_tests.py ✅ Create
```

### Week 7-8: Production Ready

**Add these folders/files**:

```
src/vivek/presentation/cli/
├── main.py                       ✅ Create (migrate from cli.py)
├── commands/
│   ├── chat_command.py           ✅ Create
│   ├── init_command.py           ✅ Create
│   └── config_command.py         ✅ Create
│
└── formatters/
    ├── progress_formatter.py     ✅ Create
    └── result_formatter.py       ✅ Create

examples/
├── simple_fastapi/               ✅ Create
├── database_crud/                ✅ Create
└── multi_file_feature/           ✅ Create

docs/
├── USER_GUIDE.md                 ✅ Create
├── CONFIGURATION.md              ✅ Create
└── MODE_GUIDE.md                 ✅ Create

tests/                            ✅ 100+ total tests
├── unit/                         ✅ 70+ tests
└── integration/                  ✅ 20+ tests
```

---

## Part 4: File Naming Conventions

### Python Files

```
# Models (domain objects)
work_item.py              # Single responsibility
execution_result.py
quality_score.py

# Services (business logic)
planner_service.py
executor_service.py
quality_service.py

# Infrastructure (external integrations)
file_service.py
ollama_provider.py
syntax_validator.py

# Tests (mirror source structure)
test_planner_service.py
test_executor_service.py
```

### Test Files

```
# Unit tests
tests/unit/domain/planning/test_planner_service.py
tests/unit/domain/execution/test_executor_service.py

# Integration tests
tests/integration/test_end_to_end_simple.py
tests/integration/test_quality_gate.py

# Test fixtures
tests/fixtures/sample_projects/fastapi_simple/
```

---

## Part 5: Import Paths

### Absolute Imports (Preferred)

```python
# Domain models
from vivek.domain.models.work_item import WorkItem
from vivek.domain.models.execution_result import ExecutionResult

# Domain services
from vivek.domain.planning.services.planner_service import PlannerService
from vivek.domain.execution.services.executor_service import ExecutorService
from vivek.domain.quality.services.quality_service import QualityService

# Application layer
from vivek.application.orchestrators.dual_brain_orchestrator import DualBrainOrchestrator
from vivek.application.services.project_context_builder import ProjectContextBuilder

# Infrastructure
from vivek.infrastructure.llm.ollama_provider import OllamaProvider
from vivek.infrastructure.file_operations.file_service import FileService
from vivek.infrastructure.validation.syntax_validator import SyntaxValidator

# Utils
from vivek.utils.token_counter import TokenCounter
from vivek.utils.context_window_manager import ContextWindowManager
```

### Relative Imports (Within Package)

```python
# Within domain/planning/services/
from .planner_service import PlannerService
from ..models.plan import Plan
from ...models.work_item import WorkItem
```

---

## Part 6: Configuration Files

### Project Root

```
vivek/
├── pyproject.toml          # Python project config
├── setup.py                # Package setup
├── setup.cfg               # Tool configs
├── .gitignore
├── .flake8                 # Linter config
├── .mypy.ini               # Type checker config
├── pytest.ini              # Test config
└── README.md
```

### User Config

```
# User's project
my_project/
├── .vivek/
│   └── config.yml         # Project-specific config
├── src/
└── tests/
```

### pyproject.toml Structure

```toml
[project]
name = "vivek"
version = "4.0.0"
description = "Intelligent code generation assistant"
requires-python = ">=3.11"

dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "httpx>=0.24.0",
    # v4.1.0+
    "libcst>=1.0.0",
    "jinja2>=3.1.0",
    # v4.2.0+
    "tree-sitter>=0.20.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "flake8>=6.0.0",
    "mypy>=1.0.0",
]

[project.scripts]
vivek = "vivek.presentation.cli.main:app"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src/vivek --cov-report=html --cov-report=term-missing"

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

---

## Part 7: Dependency Flow (Clean Architecture)

```
┌─────────────────────────────────────────────┐
│          Presentation Layer                  │
│  (CLI, API, Formatters)                     │
│  • presentation/cli/main.py                 │
│  • presentation/cli/commands/               │
└──────────────────┬──────────────────────────┘
                   │ depends on
                   ▼
┌─────────────────────────────────────────────┐
│          Application Layer                   │
│  (Orchestrators, Use Cases)                 │
│  • application/orchestrators/               │
│  • application/services/                    │
└──────────────────┬──────────────────────────┘
                   │ depends on
                   ▼
┌─────────────────────────────────────────────┐
│          Domain Layer                        │
│  (Business Logic, Models)                   │
│  • domain/models/                           │
│  • domain/planning/services/                │
│  • domain/execution/services/               │
│  • domain/quality/services/                 │
└──────────────────┬──────────────────────────┘
                   │ depends on (interfaces)
                   ▼
┌─────────────────────────────────────────────┐
│          Infrastructure Layer                │
│  (External Integrations)                    │
│  • infrastructure/llm/                      │
│  • infrastructure/file_operations/          │
│  • infrastructure/validation/               │
└─────────────────────────────────────────────┘
```

**Key Principle**: Dependencies point **inward** (domain never depends on infrastructure)

---

## Part 8: Migration Strategy

### Phase 1: Parallel Development (Week 1-6)

- Keep v3.0.0 code intact
- Build v4.0.0 alongside
- No breaking changes to existing code

```python
# Old (v3.0.0) - Still works
from vivek.application.orchestrators.simple_orchestrator import SimpleOrchestrator

# New (v4.0.0) - Add alongside
from vivek.application.orchestrators.dual_brain_orchestrator import DualBrainOrchestrator
```

### Phase 2: Feature Flag (Week 7)

```python
# config.yml
version: "4.0.0"  # Switch between v3 and v4

# In CLI
if config.version == "4.0.0":
    orchestrator = DualBrainOrchestrator()
else:
    orchestrator = SimpleOrchestrator()  # Fallback
```

### Phase 3: Deprecation (Week 8)

```python
# Mark v3 as deprecated
@deprecated("Use DualBrainOrchestrator instead")
class SimpleOrchestrator:
    pass
```

### Phase 4: Removal (v4.1.0)

- Remove deprecated v3 code
- Clean up old files

---

## Part 9: File Creation Checklist

### Every Python File Should Have

```python
"""Module docstring.

Description of what this module does.
"""

from __future__ import annotations  # For forward references

from typing import List, Optional, Dict, Any
from pathlib import Path

# Imports (standard lib, third party, local)

# Constants (if any)
MAX_RETRIES = 3
DEFAULT_TIMEOUT = 60

# Classes/Functions

# Type hints everywhere
def function_name(param: str, optional: Optional[int] = None) -> bool:
    """Function docstring.

    Args:
        param: Description of param
        optional: Description of optional param

    Returns:
        Description of return value

    Raises:
        ValueError: When param is invalid
    """
    pass
```

### Every Test File Should Have

```python
"""Tests for module_name.

Test cases for the ModuleName class/function.
"""

import pytest
from vivek.domain.module_name import ModuleName

@pytest.fixture
def setup_data():
    """Fixture for common test data."""
    return ModuleName()

class TestModuleName:
    """Test suite for ModuleName."""

    def test_basic_functionality(self, setup_data):
        """Test basic functionality works as expected."""
        result = setup_data.method()
        assert result is not None

    def test_error_handling(self):
        """Test error cases are handled correctly."""
        with pytest.raises(ValueError):
            ModuleName().invalid_method()
```

---

## Part 10: Summary

### v4.0.0 Folder Organization Key Points

1. **Clean Architecture**: Domain → Application → Infrastructure → Presentation
2. **Gradual Migration**: v3 and v4 coexist during transition
3. **Testability**: Mirror source structure in tests/
4. **Separation of Concerns**: Each layer has clear responsibility
5. **Extensibility**: Easy to add new modes, providers, validators

### Next Steps

1. ✅ Review this structure with team
2. ✅ Start Week 1-2 implementation
3. ✅ Create skeleton folders
4. ✅ Begin with domain models
5. ✅ Build vertically (one slice at a time)

---

**Document Status**: Complete
**Version**: 1.0
**Last Updated**: October 22, 2025
**Ready for**: Week 1 Implementation
