# Architecture Overview

## Clean Architecture

Vivek follows Clean Architecture principles with clear layer separation.

```
┌─────────────────────────────────────┐
│  CLI / User Interface               │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Infrastructure Layer                │
│  - DI Container                      │
│  - LLM Providers (Ollama, Mock)     │
│  - State Repositories (File, Memory)│
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Application Layer                   │
│  - Use Cases & Orchestration         │
│  - Application Services              │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Domain Layer (Pure Business Logic) │
│  - Task, Workflow, Plan Models      │
│  - Domain Services                   │
│  - Repository Interfaces             │
└─────────────────────────────────────┘
```

## SOLID Principles

- **Single Responsibility**: Each class has one reason to change
- **Open/Closed**: Extensible via interfaces, not modification
- **Liskov Substitution**: All implementations substitute abstractions
- **Interface Segregation**: Small, focused interfaces
- **Dependency Inversion**: Depend on abstractions via DI

## Key Components

### Domain Layer

**Task Model** - Rich domain model with business logic:
- State management (start, complete, fail, block)
- Dependency tracking
- Complexity estimation
- Validation

**Workflow & Planning** - Orchestrate task execution

### Application Layer

**ServiceContainer** - Dependency injection
**SimpleOrchestrator** - Main workflow coordinator
**VivekApplicationService** - Task execution service

### Infrastructure Layer

**LLM Providers**: OllamaProvider, MockLLMProvider
**State Repositories**: FileStateRepository, MemoryStateRepository

## Testing

- **183+ tests** with 94% pass rate
- Mock-based testing via centralized mocks
- Fast test suite (< 2 seconds)

## Design Decisions

1. **Poetry over setuptools** - Better dependency management
2. **DI Container** - Testable, flexible architecture
3. **Rich domain models** - Business logic in domain layer
4. **Repository pattern** - Clean data access abstraction
