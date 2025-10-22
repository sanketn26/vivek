# Vivek v4.0.0: Quick Reference - Folder Structure

**For quick lookup during implementation**

---

## Where to Put New Code

### Domain Layer (Business Logic)

| What | Where | Example |
|------|-------|---------|
| **Domain Models** | `src/vivek/domain/models/` | `work_item.py`, `execution_result.py` |
| **Planning Logic** | `src/vivek/domain/planning/services/` | `planner_service.py`, `dependency_resolver.py` |
| **Execution Logic** | `src/vivek/domain/execution/services/` | `executor_service.py` |
| **Execution Modes** | `src/vivek/domain/execution/modes/` | `coder_mode.py`, `sdet_mode.py` |
| **Quality Logic** | `src/vivek/domain/quality/services/` | `quality_service.py`, `completeness_checker.py` |

### Application Layer (Use Cases)

| What | Where | Example |
|------|-------|---------|
| **Orchestrators** | `src/vivek/application/orchestrators/` | `dual_brain_orchestrator.py`, `iteration_manager.py` |
| **App Services** | `src/vivek/application/services/` | `project_context_builder.py` |
| **Use Cases** | `src/vivek/application/use_cases/` | `generate_code_use_case.py` |

### Infrastructure Layer (External Integrations)

| What | Where | Example |
|------|-------|---------|
| **LLM Providers** | `src/vivek/infrastructure/llm/` | `ollama_provider.py`, `openai_provider.py` |
| **File Operations** | `src/vivek/infrastructure/file_operations/` | `file_service.py`, `command_executor.py` |
| **Code Tools** | `src/vivek/infrastructure/code_tools/` | `ast_transformer.py`, `template_engine.py` (v4.1.0+) |
| **Validation** | `src/vivek/infrastructure/validation/` | `syntax_validator.py`, `linter_service.py` |
| **Configuration** | `src/vivek/infrastructure/config/` | `config_loader.py`, `settings.py` |

### Presentation Layer (User Interface)

| What | Where | Example |
|------|-------|---------|
| **CLI Entry** | `src/vivek/presentation/cli/` | `main.py` |
| **CLI Commands** | `src/vivek/presentation/cli/commands/` | `chat_command.py`, `init_command.py` |
| **Formatters** | `src/vivek/presentation/cli/formatters/` | `progress_formatter.py` |

### Supporting Files

| What | Where | Example |
|------|-------|---------|
| **Prompts** | `src/vivek/prompts/` | `planner_prompts.py`, `executor_prompts.py` |
| **Templates** | `src/vivek/templates/` | `fastapi_endpoint.py.jinja2` (v4.1.0+) |
| **Utils** | `src/vivek/utils/` | `token_counter.py`, `context_window_manager.py` |

### Tests

| What | Where | Example |
|------|-------|---------|
| **Unit Tests** | `tests/unit/{layer}/{module}/` | `tests/unit/domain/planning/test_planner_service.py` |
| **Integration Tests** | `tests/integration/` | `test_end_to_end_simple.py` |
| **Fixtures** | `tests/fixtures/` | Sample projects, expected outputs |

---

## Quick Decision Tree: Where Does My Code Go?

```
Is it business logic (rules, algorithms)?
├─ YES → domain/
│   ├─ Planning? → domain/planning/
│   ├─ Execution? → domain/execution/
│   └─ Quality? → domain/quality/
│
├─ NO → Is it orchestration/coordination?
    ├─ YES → application/orchestrators/
    │
    ├─ NO → Is it external integration?
        ├─ YES → infrastructure/
        │   ├─ LLM? → infrastructure/llm/
        │   ├─ Files? → infrastructure/file_operations/
        │   ├─ Validation? → infrastructure/validation/
        │   └─ Config? → infrastructure/config/
        │
        └─ NO → Is it user interface?
            ├─ YES → presentation/cli/
            └─ NO → utils/ or prompts/
```

---

## Common Tasks

### Task 1: Add a New Execution Mode

1. Create: `src/vivek/domain/execution/modes/new_mode.py`
2. Inherit from: `base_mode.py`
3. Create prompt: `src/vivek/prompts/mode_prompts/new_mode_prompt.py`
4. Test: `tests/unit/domain/execution/test_new_mode.py`
5. Register in: `ExecutorService`

### Task 2: Add a New LLM Provider

1. Create: `src/vivek/infrastructure/llm/new_provider.py`
2. Implement: `LLMProvider` interface
3. Add to: `provider_factory.py`
4. Test: `tests/unit/infrastructure/test_new_provider.py`
5. Update config: `config.yml`

### Task 3: Add a New Quality Criterion

1. Create: `src/vivek/domain/quality/services/new_checker.py`
2. Add to: `quality_service.py`
3. Update: `quality_prompts.py`
4. Test: `tests/unit/domain/quality/test_new_checker.py`

### Task 4: Add File Operation

1. Add method to: `src/vivek/infrastructure/file_operations/file_service.py`
2. Test: `tests/unit/infrastructure/test_file_service.py`
3. Use in: Executor or other services

---

## Import Cheat Sheet

```python
# Domain Models
from vivek.domain.models.work_item import WorkItem
from vivek.domain.models.execution_result import ExecutionResult

# Services
from vivek.domain.planning.services.planner_service import PlannerService
from vivek.domain.execution.services.executor_service import ExecutorService
from vivek.domain.quality.services.quality_service import QualityService

# Orchestrator
from vivek.application.orchestrators.dual_brain_orchestrator import DualBrainOrchestrator

# Infrastructure
from vivek.infrastructure.llm.ollama_provider import OllamaProvider
from vivek.infrastructure.file_operations.file_service import FileService
from vivek.infrastructure.validation.syntax_validator import SyntaxValidator
from vivek.infrastructure.config.config_loader import ConfigLoader

# Utils
from vivek.utils.token_counter import TokenCounter
from vivek.utils.context_window_manager import ContextWindowManager
```

---

## Week-by-Week Focus

### Week 1-2: Minimal End-to-End
**Focus on**: `domain/`, `application/orchestrators/`, `infrastructure/file_operations/`

### Week 3-4: Quality Gate
**Focus on**: `domain/quality/`, `application/orchestrators/iteration_manager.py`, `infrastructure/validation/`

### Week 5-6: Dependencies & SDET
**Focus on**: `domain/planning/dependency_resolver.py`, `domain/execution/modes/sdet_mode.py`, `application/services/project_context_builder.py`

### Week 7-8: Production Ready
**Focus on**: `presentation/cli/`, `tests/`, `examples/`, `docs/`

---

## File Naming Patterns

```
# Services (business logic)
{noun}_service.py           # planner_service.py, executor_service.py

# Models (data structures)
{noun}.py                   # work_item.py, execution_result.py

# Modes (execution strategies)
{adjective}_mode.py         # coder_mode.py, sdet_mode.py

# Providers (external integrations)
{provider}_provider.py      # ollama_provider.py, openai_provider.py

# Utilities (helpers)
{purpose}_{type}.py         # token_counter.py, context_window_manager.py

# Tests (mirror source)
test_{source_file}.py       # test_planner_service.py
```

---

## Architecture Layers (Dependency Direction)

```
Presentation (CLI)
    ↓ depends on
Application (Orchestrators, Use Cases)
    ↓ depends on
Domain (Business Logic)
    ↓ depends on (interfaces only)
Infrastructure (External Integrations)
```

**Rule**: Arrows point **down** only. Domain never imports from Infrastructure directly.

---

## Configuration Files

```
vivek/
├── pyproject.toml          # Python project metadata
├── setup.py                # Package installation
├── pytest.ini              # Test configuration
├── .flake8                 # Linting rules
├── .mypy.ini               # Type checking
└── .vivek/
    └── config.yml          # Vivek configuration
```

---

## Common File Templates

### Domain Service

```python
"""Service for handling X logic."""

from typing import List
from vivek.domain.models.y import Y

class XService:
    """Handle X operations."""

    def __init__(self, dependency: Dependency):
        self.dependency = dependency

    def do_something(self, input: str) -> Y:
        """Do something with input."""
        # Implementation
        pass
```

### Infrastructure Service

```python
"""External integration for X."""

from pathlib import Path
from typing import Optional

class XService:
    """Wrapper for X external tool."""

    @staticmethod
    def operation(param: str) -> bool:
        """Perform operation."""
        # Implementation
        pass
```

### Test File

```python
"""Tests for x_service."""

import pytest
from vivek.domain.services.x_service import XService

@pytest.fixture
def x_service():
    """Create XService instance."""
    return XService()

class TestXService:
    """Test XService functionality."""

    def test_basic_operation(self, x_service):
        """Test basic operation works."""
        result = x_service.do_something("input")
        assert result is not None
```

---

**Quick Tip**: When in doubt, look at existing files in the same folder for patterns!
