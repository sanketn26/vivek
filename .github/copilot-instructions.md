# Vivek AI Assistant - Copilot Instructions

## Architecture Overview

Vivek uses a **dual-brain collaborative AI architecture** with specialized Planner and Executor models working together via LangGraph orchestration. The system breaks complex tasks into file-level work items with dependencies, then executes them through 3-phase workflows.

### Core Components
- **Planner Brain**: Task decomposition, requirement analysis, quality assurance
- **Executor Brain**: Code generation, implementation, technical execution
- **LangGraph Orchestrator**: State management, iteration control, persistence
- **Agentic Context**: Hierarchical context tracking (Session → Activity → Task)
- **Mode-Specific Executors**: peer, architect, sdet, coder with specialized prompts

## Critical Workflows

### Development Setup
```bash
make setup          # Create venv, install deps, setup pre-commit
make install-dev    # Install with dev dependencies
make test          # Run pytest with coverage
make format        # Black + isort formatting
make lint          # Flake8 linting
make type-check    # MyPy type checking
```

### Project Initialization
```bash
vivek init         # Auto-detect languages, create .vivek/config.yml
vivek chat         # Start interactive session
```

## Work Item Breakdown Pattern

Tasks are decomposed into **file-level work items** with explicit dependencies:

```python
work_item = {
    "mode": "coder|sdet|architect|peer",
    "file_path": "exact/file/path.py",
    "file_status": "new|existing",
    "description": "Detailed implementation instructions",
    "dependencies": [0, 1]  # Indices of prerequisite work items
}
```

Each work item breaks into **3-5 atomic sub-tasks** executed sequentially.

## Mode-Specific Patterns

### Coder Mode
- **Focus**: Direct implementation, clean code generation
- **Output**: PEP 8 compliant Python with type hints
- **Pattern**: Implement functions/classes with comprehensive error handling

### SDET Mode
- **Focus**: Test-driven development, comprehensive coverage
- **Output**: pytest fixtures, parameterized tests, edge case coverage
- **Pattern**: Red-Green-Refactor with `test_` prefixed functions

### Architect Mode
- **Focus**: System design, architectural decisions
- **Output**: Service boundaries, data flows, design documents
- **Pattern**: Multi-perspective analysis (user, critic, ops, debugger, future, QA)

### Peer Mode
- **Focus**: Collaborative programming, discussion
- **Output**: Balanced solutions with multiple approaches
- **Pattern**: Six thinking hats analysis for comprehensive evaluation

## Key Conventions

### File Organization
- `vivek/core/`: Orchestration, state management, graph nodes
- `vivek/llm/`: Model providers, executors, planner logic
- `vivek/agentic_context/`: Context tracking and retrieval
- `vivek/utils/`: Language detection, prompt compression, token counting

### Error Handling
```python
from vivek.core.message_protocol import execution_complete, error_occurred

try:
    # Implementation
    return execution_complete(result)
except Exception as e:
    return error_occurred(str(e))
```

### Logging
```python
logger = logging.getLogger(__name__)
logger.info("Operation completed: %s", operation_name)
```

### Testing
```python
@pytest.mark.unit
def test_function_name():
    # Arrange
    # Act
    # Assert
```

## Integration Points

### LLM Providers
- **Ollama**: Local models (qwen2.5-coder:7b default)
- **LM Studio**: Alternative local provider
- **External APIs**: OpenAI, Anthropic, Sarvam support

### Language Plugins
- Auto-detection via `vivek/utils/language_detector.py`
- Language-specific prompts in `vivek/llm/plugins/`
- Supported: Python, TypeScript, Go with language-aware executors

### Context Management
- **Hierarchical**: Session → Activity → Task contexts
- **Retrieval**: Tag-based, embedding-based, hybrid strategies
- **Storage**: SQLite persistence with automatic cleanup

## Quality Gates

### Pre-commit Checks
- Black formatting (88 char line length)
- Flake8 linting (extended ignore: E203,W503)
- MyPy type checking (ignore missing imports)
- Pytest with coverage reporting

### Code Standards
- **Python**: PEP 8, type hints, explicit imports
- **Error Handling**: Comprehensive try/catch with specific exceptions
- **Documentation**: Docstrings for public APIs
- **Testing**: 100% coverage target, integration tests for workflows

## Common Patterns

### Executor Implementation
```python
class CustomExecutor(BaseExecutor):
    mode = "custom"
    mode_prompt = "Custom mode instructions"

    def get_mode_specific_instructions(self) -> str:
        return "Custom implementation guidelines"
```

### Graph Node Creation
```python
def create_custom_node(state: VivekState) -> Dict[str, Any]:
    # Process state
    # Return updated state
    return {"key": "updated_value"}
```

### Context Workflow
```python
with ContextWorkflow() as workflow:
    with workflow.session("Task session"):
        with workflow.activity("Implementation"):
            with workflow.task("Specific work"):
                # Execute work item
                pass
```

## Debugging Tips

- Check `.vivek/checkpoints.db` for persistent state
- Use `LangGraphVivekOrchestrator` for graph visualization
- Monitor token usage with `log_token_count()`
- Enable debug logging for context tracking

## File Examples

**Core Orchestrator**: `vivek/core/langgraph_orchestrator.py`
**Base Executor**: `vivek/llm/executor.py`
**Context Workflow**: `vivek/agentic_context/workflow.py`
**Test Structure**: `tests/conftest.py`