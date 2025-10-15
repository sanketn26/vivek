# Vivek AI Assistant - Migration Guide

## 🎯 Migration Complete

Successfully migrated from the complex LangGraph-based architecture to a simplified Domain-Driven Design architecture.

## 📋 What Was Removed

### Complex Files Removed (Backed up in `backup/old_architecture/`)

#### Core Files
- `vivek/core/langgraph_orchestrator.py` (410 lines) - Complex orchestration logic
- `vivek/core/enhanced_graph_nodes.py` (503 lines) - Mixed planning/execution/review logic
- `vivek/core/structured_workflow.py` - Complex workflow management
- `vivek/core/workflow_integration.py` - Integration concerns mixed with business logic
- `vivek/core/performance_validator.py` - Validation mixed with optimization
- `vivek/core/prompt_templates.py` - Templates mixed with business rules

#### LLM Files
- `vivek/llm/executor.py` (294 lines) - Complex base executor with mixed concerns
- `vivek/llm/structured_executor.py` - TDD workflow implementation mixed with execution
- `vivek/llm/structured_planner.py` - Multi-phase workflow management
- `vivek/llm/architect_executor.py` - Mode-specific logic mixed with base functionality
- `vivek/llm/coder_executor.py` - Mode-specific logic mixed with base functionality
- `vivek/llm/peer_executor.py` - Mode-specific logic mixed with base functionality
- `vivek/llm/sdet_executor.py` - Mode-specific logic mixed with base functionality
- `vivek/llm/planner.py` - Provider abstractions mixed with configuration

## 🏗️ What Was Added

### New Clean Architecture

#### Domain Layer (`src/vivek/domain/`)
```
src/vivek/domain/
├── workflow/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # 28 lines - Simple task management
│   │   ├── workflow.py      # 50 lines - Workflow state management
│   │   └── work_item.py     # 29 lines - Work items with dependencies
│   └── services/
│       ├── __init__.py
│       └── workflow_service.py  # 49 lines - Pure workflow logic
├── planning/
│   ├── models/
│   │   ├── __init__.py
│   │   └── task_plan.py     # 37 lines - Execution planning
│   └── services/
│       ├── __init__.py
│       └── planning_service.py   # 55 lines - Pure planning logic
└── execution/
    └── review/              # Ready for future domain areas
```

#### Infrastructure Layer (`src/vivek/infrastructure/`)
```
src/vivek/infrastructure/
├── llm/
│   ├── __init__.py
│   └── llm_provider.py      # 29 lines - Simple LLM abstraction
└── persistence/
    ├── __init__.py
    └── state_repository.py   # 30 lines - Simple state persistence
```

#### Application Layer (`src/vivek/application/`)
```
src/vivek/application/
├── services/
│   ├── __init__.py
│   └── vivek_application_service.py  # 91 lines - Use case orchestration
└── orchestrators/
    ├── __init__.py
    └── simple_orchestrator.py         # 54 lines - High-level coordination
```

## 🚀 How to Use the New Architecture

### 1. Basic Usage

```python
from vivek.domain.workflow.services.workflow_service import WorkflowService
from vivek.domain.planning.services.planning_service import PlanningService
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.infrastructure.persistence.state_repository import StateRepository
from vivek.application.services.vivek_application_service import VivekApplicationService
from vivek.application.orchestrators.simple_orchestrator import SimpleOrchestrator

# Create services
workflow_service = WorkflowService()
planning_service = PlanningService()
llm_provider = YourLLMProvider()  # Implement LLMProvider interface
state_repository = YourStateRepository()  # Implement StateRepository interface

# Create application service
app_service = VivekApplicationService(
    workflow_service=workflow_service,
    planning_service=planning_service,
    llm_provider=llm_provider,
    state_repository=state_repository
)

# Create orchestrator
orchestrator = SimpleOrchestrator(app_service)

# Process user request
result = orchestrator.process_user_request("Create a simple calculator")
```

### 2. Custom LLM Provider

```python
from vivek.infrastructure.llm.llm_provider import LLMProvider

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str, base_url: str = "http://localhost:11434"):
        super().__init__(model_name)
        self.base_url = base_url

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        # Your Ollama implementation here
        return ollama_response

    def is_available(self) -> bool:
        # Check if Ollama is running
        return True
```

### 3. Custom State Repository

```python
from vivek.infrastructure.persistence.state_repository import StateRepository

class SqliteStateRepository(StateRepository):
    def __init__(self, db_path: str = ".vivek/states.db"):
        self.db_path = db_path
        # Initialize database connection

    def save_state(self, thread_id: str, state: dict) -> None:
        # Save to SQLite
        pass

    def load_state(self, thread_id: str) -> dict | None:
        # Load from SQLite
        pass

    def delete_state(self, thread_id: str) -> bool:
        # Delete from SQLite
        pass

    def list_threads(self) -> list[str]:
        # List all thread IDs
        pass
```

## 📊 Benefits Achieved

### Code Quality
- **87% reduction** in core complexity (410 → 54 lines for orchestration)
- **Single Responsibility**: Each class has one clear purpose
- **30-second rule**: Every class can be understood quickly
- **SOLID principles**: Proper separation of concerns

### Architecture Benefits
- **Domain-Driven Design**: Business logic isolated from infrastructure
- **Dependency Injection**: Easy to test and mock dependencies
- **Interface Segregation**: Focused abstractions for each concern
- **Clean Layers**: Clear boundaries between domain, infrastructure, and application

### Developer Experience
- **Easy Onboarding**: New developers can understand the system quickly
- **Safe Refactoring**: Changes have predictable, limited impact
- **Better Testing**: Pure functions and mockable dependencies
- **Clear Navigation**: Intuitive structure for finding code

## 🧪 Testing

### Running Tests
```bash
# Run the demo to verify everything works
python demo_new_architecture.py

# Run the new CLI
python -m vivek.new_cli init
python -m vivek.new_cli chat --test-input "Hello, world!"
```

### Writing Tests for New Architecture
```python
import pytest
from vivek.domain.workflow.services.workflow_service import WorkflowService
from vivek.domain.workflow.models.task import Task

def test_workflow_service():
    service = WorkflowService()

    # Create workflow
    workflow = service.create_workflow("test", "Test workflow")

    # Add task
    task = Task(id="task1", description="Test task")
    service.add_task_to_workflow(workflow.id, task)

    # Verify
    tasks = service.get_pending_tasks(workflow.id)
    assert len(tasks) == 1
    assert tasks[0].description == "Test task"
```

## 🔄 Migration Strategy for Production

If you're migrating a production system:

1. **Phase 1**: Deploy new architecture alongside old (Strangler Fig pattern)
2. **Phase 2**: Use feature flags to switch between architectures
3. **Phase 3**: Gradually migrate users to new architecture
4. **Phase 4**: Remove old architecture once migration is complete

## 📁 File Structure After Migration

```
src/vivek/
├── domain/                    # 🏗️ Pure business logic
│   ├── workflow/             # Workflow management domain
│   ├── planning/             # Task planning domain
│   └── execution/            # Ready for execution domain
├── infrastructure/           # 🔌 External dependencies
│   ├── llm/                  # LLM provider abstractions
│   └── persistence/          # State persistence abstractions
├── application/              # 🎯 Use case orchestration
│   ├── services/             # Application services
│   └── orchestrators/        # High-level coordination
├── agentic_context/          # 🤖 Agentic context management (MOVED)
├── utils/                    # 🛠️ Utility functions (MOVED)
├── core/                     # 🔧 Core utilities (MOVED)
├── llm/                      # 🧠 LLM implementations (MOVED)
└── cli.py                   # 💻 Command-line interface

tests/                         # 🧪 Test directory
docs/                         # 📚 Documentation
├── MIGRATION_GUIDE.md        # Migration documentation
├── REFACTORING_SUMMARY.md   # Technical summary
└── backup/                   # 📦 Old files for reference
    └── old_architecture/     # Complex files that were removed

demo_new_architecture.py      # 🚀 Working demonstration
```

## 🎉 Next Steps

1. **Implement Real LLM Providers**: Replace MockLLMProvider with actual implementations
2. **Add State Persistence**: Implement proper database storage
3. **Expand Domain Areas**: Add execution and review domains as needed
4. **Add More Application Services**: Create specialized services for different use cases
5. **Update Tests**: Migrate existing tests to work with new architecture

## 🔗 Key Architectural Principles

- **Domain First**: Business logic drives the architecture
- **Dependency Inversion**: Depend on abstractions, not concretions
- **Single Responsibility**: Each class has one reason to change
- **Interface Segregation**: Focused interfaces for specific needs
- **Clean Boundaries**: Clear separation between layers

The new architecture provides a solid foundation for future development while being much easier to understand, test, and maintain than the previous complex system.