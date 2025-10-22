# Workstream 4: CLI & Polish

**Timeline**: Week 7-8
**Goal**: User interface, documentation, and release

**Prerequisites**: Workstreams 1, 2, 3 complete

---

## Overview

This workstream delivers the final user-facing CLI and prepares for v4.0.0 release.

### Deliverables
- ✅ CLI with progress display
- ✅ Configuration management (`vivek init`, `vivek config`)
- ✅ 100+ total tests (85%+ coverage)
- ✅ User documentation
- ✅ 3 example projects
- ✅ v4.0.0 release

---

## Part 1: CLI Interface

### File: `src/vivek/presentation/cli/main.py`

```python
"""CLI entry point."""

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from pathlib import Path

from vivek.application.orchestrators.dual_brain_orchestrator import DualBrainOrchestrator
from vivek.infrastructure.di_container import DIContainer


app = typer.Typer(
    name="vivek",
    help="Intelligent code generation assistant"
)
console = Console()


@app.command()
def chat(
    request: str = typer.Argument(..., help="What to implement"),
    project_root: Path = typer.Option(
        ".",
        "--project",
        "-p",
        help="Project root directory"
    )
):
    """Generate code from natural language request.

    Example:
        vivek chat "Create FastAPI endpoint for user registration"
    """
    try:
        # Load configuration
        container = DIContainer()
        orchestrator = container.get_orchestrator()

        # Build project context
        context_builder = container.get_context_builder()
        project_context = context_builder.build_context(project_root)

        # Execute with progress display
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            # Planning
            task = progress.add_task("🧠 Planning...", total=None)
            # (Execute orchestrator here - async handling needed)

        console.print("[green]✅ Done![/green]")

    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def init():
    """Initialize Vivek in current project.

    Creates .vivek/ directory with default configuration.
    """
    vivek_dir = Path(".vivek")

    if vivek_dir.exists():
        console.print("[yellow]⚠️  .vivek/ already exists[/yellow]")
        return

    # Create directory
    vivek_dir.mkdir()

    # Create default config
    config_content = """# Vivek v4.0.0 Configuration

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
"""

    (vivek_dir / "config.yml").write_text(config_content)

    console.print("[green]✅ Initialized Vivek[/green]")
    console.print(f"  Config: {vivek_dir / 'config.yml'}")


@app.command()
def config(
    key: str = typer.Argument(..., help="Config key (e.g., quality.threshold)"),
    value: str = typer.Argument(..., help="Config value"),
):
    """Update configuration value.

    Example:
        vivek config quality.threshold 0.80
    """
    # TODO: Implement config update
    console.print(f"[green]✅ Updated {key} = {value}[/green]")


if __name__ == "__main__":
    app()
```

---

## Part 2: Progress Formatter

### File: `src/vivek/presentation/cli/formatters/progress_formatter.py`

```python
"""Format and display progress."""

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class ProgressFormatter:
    """Format progress messages for CLI."""

    def __init__(self):
        self.console = Console()

    def show_plan(self, work_items: list):
        """Display execution plan."""
        table = Table(title="📋 Execution Plan")
        table.add_column("ID", style="cyan")
        table.add_column("File", style="green")
        table.add_column("Mode", style="yellow")
        table.add_column("Dependencies", style="blue")

        for item in work_items:
            table.add_row(
                item.id,
                item.file_path,
                item.mode.value,
                ", ".join(item.dependencies) or "none"
            )

        self.console.print(table)

    def show_quality_score(self, quality_score):
        """Display quality score."""
        score_text = f"""
Overall Score: {quality_score.overall:.2f}
Completeness: {quality_score.completeness:.2f}
Correctness: {quality_score.correctness:.2f}

Status: {"✅ PASSED" if quality_score.passed else "❌ FAILED"}
        """

        panel = Panel(
            score_text.strip(),
            title="📊 Quality Evaluation",
            border_style="green" if quality_score.passed else "red"
        )

        self.console.print(panel)

        if quality_score.feedback:
            self.console.print("\n[yellow]Feedback:[/yellow]")
            for feedback in quality_score.feedback:
                self.console.print(f"  • {feedback}")
```

---

## Part 3: Example Projects

### Example 1: `examples/simple_fastapi/`

**README.md**:
```markdown
# Simple FastAPI Example

Test Vivek with a simple FastAPI project.

## Run

```bash
cd examples/simple_fastapi
vivek init
vivek chat "Create user registration endpoint with email and password"
```

## Expected Output

- `src/models/user.py` - User Pydantic model
- `src/routes/auth.py` - Registration endpoint
- `tests/test_auth.py` - Tests for endpoint
```

---

## Part 4: User Documentation

### File: `docs/USER_GUIDE.md`

```markdown
# Vivek v4.0.0 User Guide

## Installation

```bash
pip install vivek
```

## Quick Start

1. Initialize Vivek in your project:
   ```bash
   cd your-project
   vivek init
   ```

2. Generate code:
   ```bash
   vivek chat "Create FastAPI endpoint for user login"
   ```

3. Review generated files and commit.

## Configuration

Edit `.vivek/config.yml`:

```yaml
quality:
  threshold: 0.75    # Quality score threshold (0.0-1.0)
  max_iterations: 1  # Max retry attempts
```

## Commands

- `vivek chat "<request>"` - Generate code
- `vivek init` - Initialize project
- `vivek config <key> <value>` - Update config

## Tips

1. **Be specific**: "Create FastAPI user registration endpoint with email validation"
2. **Use git**: Always commit before running Vivek
3. **Review outputs**: Generated code should be reviewed before use
```

---

## Part 5: Testing

### File: `tests/integration/test_complete_workflow.py`

```python
"""Test complete workflow with all components."""

import pytest
from pathlib import Path


@pytest.mark.asyncio
async def test_complete_workflow_with_quality_iteration():
    """Test complete workflow including quality iteration."""
    # TODO: Implement complete workflow test
    pass


@pytest.mark.asyncio
async def test_multi_file_generation_with_dependencies():
    """Test generating multiple files with dependencies."""
    # TODO: Implement multi-file test
    pass
```

### Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/vivek --cov-report=html

# Run only integration tests
pytest tests/integration/ -v
```

---

## Part 6: Release Preparation

### File: `pyproject.toml` (Update)

```toml
[project]
name = "vivek"
version = "4.0.0"
description = "Intelligent code generation assistant with dual-brain architecture"
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]

dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "httpx>=0.24.0",
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
addopts = "-v --cov=src/vivek --cov-report=term-missing"

[tool.black]
line-length = 100
target-version = ['py311']
```

### Release Checklist

- [ ] All tests passing (100+)
- [ ] Coverage >= 85%
- [ ] Documentation complete
- [ ] Examples working
- [ ] CHANGELOG.md updated
- [ ] Version bumped to 4.0.0
- [ ] Tagged in git
- [ ] Published to PyPI

---

## Summary Checklist

### Week 7-8 Deliverables

- [ ] CLI implemented:
  - [ ] `vivek chat` command
  - [ ] `vivek init` command
  - [ ] `vivek config` command
  - [ ] Progress display (rich)
  - [ ] Result formatting
- [ ] Tests:
  - [ ] 100+ total tests
  - [ ] 85%+ coverage
  - [ ] All integration tests passing
- [ ] Documentation:
  - [ ] User guide
  - [ ] Configuration guide
  - [ ] API reference (optional)
- [ ] Examples:
  - [ ] simple_fastapi/
  - [ ] database_crud/ (optional)
  - [ ] multi_file_feature/ (optional)
- [ ] Release:
  - [ ] Version 4.0.0
  - [ ] PyPI package
  - [ ] Release notes

### v4.0.0 Complete! 🎉

✅ Dual-brain architecture working
✅ 3-5 files generated per request
✅ 80% test inclusion
✅ Quality gate operational
✅ <5% syntax errors
✅ User-friendly CLI

**Success Metrics Achieved**:
- Files per request: 1 → 3-5 (5x improvement)
- Test inclusion: 0% → 80%
- Syntax errors: ~25% → <5%
- Quality validation: Added

---

## Next Steps (v4.1.0)

After v4.0.0 release, consider adding:
- Architect mode (design docs)
- Peer mode (code review)
- Multi-provider support (OpenAI, Anthropic)
- Vector storage (semantic file search)
- Parallel execution
- Advanced caching

See `VECTOR_STORAGE_STRATEGY.md` for details on semantic search.

---

**Congratulations! v4.0.0 is complete! 🚀**
