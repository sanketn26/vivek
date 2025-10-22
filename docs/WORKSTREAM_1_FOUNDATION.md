# Workstream 1: Foundation & Contracts

**Timeline**: Week 1-2
**Goal**: Set up core architecture, data models, and interfaces

---

## Overview

This workstream establishes the foundation for all other work. You **must** complete this before moving to Workstream 2.

### Deliverables
- ✅ Folder structure created
- ✅ Data models defined (WorkItem, ExecutionResult, QualityScore, Plan)
- ✅ Service interfaces (IPlannerService, IExecutorService, IQualityService)
- ✅ Exception hierarchy
- ✅ Configuration system
- ✅ Basic file operations
- ✅ 15+ unit tests

---

## Part 1: Folder Structure

Create these folders:

```bash
mkdir -p src/vivek/domain/{models,interfaces,exceptions}
mkdir -p src/vivek/domain/planning/{models,services}
mkdir -p src/vivek/domain/execution/{models,services,modes}
mkdir -p src/vivek/domain/quality/{models,services}
mkdir -p src/vivek/application/orchestrators
mkdir -p src/vivek/infrastructure/{file_operations,config,validation}
mkdir -p src/vivek/prompts
mkdir -p tests/{unit,integration,fixtures}
mkdir -p .vivek
```

---

## Part 2: Data Models

### File: `src/vivek/domain/models/work_item.py`

```python
"""Work item data model."""

from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum


class ExecutionMode(str, Enum):
    """Execution mode for work item."""
    CODER = "coder"      # Generate implementation code
    SDET = "sdet"        # Generate tests


@dataclass
class WorkItem:
    """Unit of work to be executed.

    Attributes:
        id: Unique identifier (UUID)
        file_path: Relative path from project root
        description: What to implement
        mode: Execution mode (coder or sdet)
        language: Programming language
        file_status: "new" or "existing"
        dependencies: IDs of work items this depends on
        context: Additional context for execution
    """
    id: str
    file_path: str
    description: str
    mode: ExecutionMode
    language: str = "python"
    file_status: str = "new"  # "new" or "existing"
    dependencies: List[str] = field(default_factory=list)
    context: Optional[str] = None

    def __post_init__(self):
        """Validate work item."""
        if not self.id:
            raise ValueError("Work item ID cannot be empty")
        if not self.file_path:
            raise ValueError("File path cannot be empty")
        if not self.description:
            raise ValueError("Description cannot be empty")
        if self.file_status not in ("new", "existing"):
            raise ValueError(f"Invalid file_status: {self.file_status}")
```

### File: `src/vivek/domain/models/execution_result.py`

```python
"""Execution result data model."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class ExecutionResult:
    """Result of executing a work item.

    Attributes:
        work_item_id: ID of work item executed
        success: Whether execution succeeded
        code: Generated code (if successful)
        file_path: Where code was written
        errors: List of error messages
        warnings: List of warning messages
        metadata: Additional metadata (tokens used, time taken, etc.)
    """
    work_item_id: str
    success: bool
    code: Optional[str] = None
    file_path: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
```

### File: `src/vivek/domain/models/quality_score.py`

```python
"""Quality score data model."""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class QualityScore:
    """Quality evaluation score.

    Attributes:
        overall: Overall score (0.0-1.0)
        completeness: Completeness score (0.0-1.0)
        correctness: Correctness score (0.0-1.0)
        feedback: Detailed feedback for improvement
        passed: Whether quality threshold was met
    """
    overall: float
    completeness: float
    correctness: float
    feedback: List[str] = field(default_factory=list)
    passed: bool = False

    def __post_init__(self):
        """Validate scores."""
        for score_name in ["overall", "completeness", "correctness"]:
            score = getattr(self, score_name)
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"{score_name} must be between 0.0 and 1.0")
```

### File: `src/vivek/domain/planning/models/plan.py`

```python
"""Plan data model."""

from dataclasses import dataclass, field
from typing import List
from datetime import datetime

from vivek.domain.models.work_item import WorkItem


@dataclass
class Plan:
    """Execution plan containing work items.

    Attributes:
        work_items: List of work items to execute
        created_at: When plan was created
        metadata: Additional plan metadata
    """
    work_items: List[WorkItem]
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def get_item_by_id(self, item_id: str) -> WorkItem:
        """Get work item by ID."""
        for item in self.work_items:
            if item.id == item_id:
                return item
        raise ValueError(f"Work item not found: {item_id}")

    def get_items_without_dependencies(self) -> List[WorkItem]:
        """Get work items with no dependencies."""
        return [item for item in self.work_items if not item.dependencies]
```

---

## Part 3: Service Interfaces

### File: `src/vivek/domain/interfaces/__init__.py`

```python
"""Service interfaces."""

from .i_planner_service import IPlannerService
from .i_executor_service import IExecutorService
from .i_quality_service import IQualityService
from .i_file_service import IFileService

__all__ = [
    "IPlannerService",
    "IExecutorService",
    "IQualityService",
    "IFileService",
]
```

### File: `src/vivek/domain/interfaces/i_planner_service.py`

```python
"""Planner service interface."""

from abc import ABC, abstractmethod
from typing import Protocol

from vivek.domain.planning.models.plan import Plan


class IPlannerService(Protocol):
    """Interface for planning service."""

    @abstractmethod
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
        """
        ...
```

### File: `src/vivek/domain/interfaces/i_executor_service.py`

```python
"""Executor service interface."""

from abc import ABC, abstractmethod
from typing import Protocol

from vivek.domain.models.work_item import WorkItem
from vivek.domain.models.execution_result import ExecutionResult


class IExecutorService(Protocol):
    """Interface for execution service."""

    @abstractmethod
    async def execute(self, work_item: WorkItem) -> ExecutionResult:
        """Execute a work item.

        Args:
            work_item: Work item to execute

        Returns:
            Execution result
        """
        ...
```

### File: `src/vivek/domain/interfaces/i_quality_service.py`

```python
"""Quality service interface."""

from abc import ABC, abstractmethod
from typing import Protocol, List

from vivek.domain.models.execution_result import ExecutionResult
from vivek.domain.models.quality_score import QualityScore


class IQualityService(Protocol):
    """Interface for quality evaluation service."""

    @abstractmethod
    async def evaluate(
        self,
        results: List[ExecutionResult]
    ) -> QualityScore:
        """Evaluate quality of execution results.

        Args:
            results: List of execution results to evaluate

        Returns:
            Quality score
        """
        ...
```

### File: `src/vivek/domain/interfaces/i_file_service.py`

```python
"""File service interface."""

from abc import ABC, abstractmethod
from typing import Protocol
from pathlib import Path


class IFileService(Protocol):
    """Interface for file operations."""

    @abstractmethod
    def read_file(self, file_path: str) -> str:
        """Read file content."""
        ...

    @abstractmethod
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to file."""
        ...

    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        ...
```

---

## Part 4: Exception Hierarchy

### File: `src/vivek/domain/exceptions/vivek_exceptions.py`

```python
"""Exception hierarchy for Vivek."""

from typing import Optional


class VivekException(Exception):
    """Base exception for all Vivek errors."""
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


class ValidationException(VivekException):
    """Validation failed."""
    pass


class LLMException(VivekException):
    """LLM provider error."""

    def __init__(
        self,
        message: str,
        provider: str,
        retry_after: Optional[int] = None
    ):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(message)


class ConfigurationException(VivekException):
    """Configuration error."""
    pass
```

---

## Part 5: File Operations

### File: `src/vivek/infrastructure/file_operations/file_service.py`

```python
"""File operations service."""

from pathlib import Path
from typing import Optional

from vivek.domain.interfaces.i_file_service import IFileService
from vivek.domain.exceptions.vivek_exceptions import ExecutionException


class FileService(IFileService):
    """Handle file operations using pathlib."""

    def read_file(self, file_path: str) -> str:
        """Read file content."""
        try:
            path = Path(file_path)
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            return path.read_text()
        except Exception as e:
            raise ExecutionException(f"Failed to read file: {e}")

    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to file."""
        try:
            path = Path(file_path)
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            return True
        except Exception as e:
            raise ExecutionException(f"Failed to write file: {e}")

    def file_exists(self, file_path: str) -> bool:
        """Check if file exists."""
        return Path(file_path).exists()

    def create_directory(self, dir_path: str) -> bool:
        """Create directory."""
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            raise ExecutionException(f"Failed to create directory: {e}")
```

### File: `src/vivek/infrastructure/file_operations/command_executor.py`

```python
"""Command execution service."""

import subprocess
from typing import Dict, Optional


class CommandExecutor:
    """Execute shell commands."""

    @staticmethod
    def run_command(
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, any]:
        """Execute shell command.

        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Timeout in seconds

        Returns:
            Dict with stdout, stderr, exit_code, success
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1
            }
```

---

## Part 6: Configuration

### File: `src/vivek/infrastructure/config/settings.py`

```python
"""Configuration settings."""

from pydantic import BaseSettings, Field
from typing import Optional


class LLMConfig(BaseSettings):
    """LLM provider configuration."""
    provider: str = "ollama"
    model: str = "qwen2.5-coder:7b"
    temperature: float = Field(default=0.1, ge=0.0, le=1.0)
    max_tokens: int = Field(default=4096, gt=0)


class QualityConfig(BaseSettings):
    """Quality configuration."""
    threshold: float = Field(default=0.75, ge=0.0, le=1.0)
    max_iterations: int = Field(default=1, ge=0, le=3)


class Settings(BaseSettings):
    """Application settings."""
    planner_llm: LLMConfig = LLMConfig()
    executor_llm: LLMConfig = LLMConfig()
    quality: QualityConfig = QualityConfig()

    class Config:
        env_file = ".vivek/config.yml"
```

### File: `.vivek/config.yml`

```yaml
# Vivek v4.0.0 Configuration

planner_llm:
  provider: "ollama"
  model: "qwen2.5-coder:7b"
  temperature: 0.3
  max_tokens: 2048

executor_llm:
  provider: "ollama"
  model: "qwen2.5-coder:7b"
  temperature: 0.1
  max_tokens: 4096

quality:
  threshold: 0.75
  max_iterations: 1
```

---

## Part 7: Tests

### File: `tests/unit/domain/models/test_work_item.py`

```python
"""Tests for WorkItem model."""

import pytest
from vivek.domain.models.work_item import WorkItem, ExecutionMode


class TestWorkItem:
    """Test WorkItem model."""

    def test_create_valid_work_item(self):
        """Test creating valid work item."""
        item = WorkItem(
            id="item_1",
            file_path="src/module.py",
            description="Create module",
            mode=ExecutionMode.CODER
        )

        assert item.id == "item_1"
        assert item.mode == ExecutionMode.CODER
        assert item.file_status == "new"
        assert item.dependencies == []

    def test_empty_id_raises_error(self):
        """Test empty ID raises ValueError."""
        with pytest.raises(ValueError, match="ID cannot be empty"):
            WorkItem(
                id="",
                file_path="src/module.py",
                description="Create module",
                mode=ExecutionMode.CODER
            )

    def test_invalid_file_status_raises_error(self):
        """Test invalid file_status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid file_status"):
            WorkItem(
                id="item_1",
                file_path="src/module.py",
                description="Create module",
                mode=ExecutionMode.CODER,
                file_status="invalid"
            )
```

### File: `tests/unit/infrastructure/test_file_service.py`

```python
"""Tests for FileService."""

import pytest
from pathlib import Path
from vivek.infrastructure.file_operations.file_service import FileService


class TestFileService:
    """Test FileService."""

    def test_write_and_read_file(self, tmp_path):
        """Test writing and reading file."""
        service = FileService()
        file_path = tmp_path / "test.txt"
        content = "Hello, World!"

        # Write
        result = service.write_file(str(file_path), content)
        assert result is True

        # Read
        read_content = service.read_file(str(file_path))
        assert read_content == content

    def test_file_exists(self, tmp_path):
        """Test file_exists check."""
        service = FileService()
        file_path = tmp_path / "test.txt"

        # Initially doesn't exist
        assert service.file_exists(str(file_path)) is False

        # Write file
        service.write_file(str(file_path), "content")

        # Now exists
        assert service.file_exists(str(file_path)) is True
```

---

## Summary Checklist

### Week 1-2 Deliverables

- [ ] Folder structure created
- [ ] Data models implemented:
  - [ ] WorkItem
  - [ ] ExecutionResult
  - [ ] QualityScore
  - [ ] Plan
- [ ] Interfaces defined:
  - [ ] IPlannerService
  - [ ] IExecutorService
  - [ ] IQualityService
  - [ ] IFileService
- [ ] Exceptions implemented
- [ ] FileService implemented
- [ ] CommandExecutor implemented
- [ ] Configuration system
- [ ] 15+ unit tests passing

### Ready for Workstream 2?

✅ All models defined and tested
✅ All interfaces defined
✅ File operations working
✅ Tests passing (85%+ coverage)

**Next**: [Workstream 2: Core Services](WORKSTREAM_2_CORE_SERVICES.md)
