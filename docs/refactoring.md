# Vivek AI Assistant - Architecture Refactoring Plan

## Executive Summary

The current Vivek codebase suffers from significant architectural issues including mixed responsibilities, unclear boundaries between layers, and tight coupling between business logic and infrastructure concerns. This document outlines a comprehensive refactoring plan to restructure the codebase using Domain-Driven Design (DDD) principles.

## Current State Analysis

### Architectural Problems Identified

#### 1. Mixed Responsibilities in Core Layer
- **`langgraph_orchestrator.py`**: Orchestration logic mixed with graph construction and state management
- **`workflow_integration.py`**: Integration concerns mixed with component lifecycle management
- **`enhanced_graph_nodes.py`**: Graph infrastructure mixed with business logic (planning, execution, review)
- **`performance_validator.py`**: Validation logic mixed with optimization algorithms
- **`structured_workflow.py`**: Data models mixed with workflow orchestration logic
- **`prompt_templates.py`**: Template rendering mixed with business rules

#### 2. Mixed Responsibilities in LLM Layer
- **`executor.py`**: Base execution logic mixed with prompt building and token management
- **`structured_executor.py`**: Execution logic mixed with TDD workflow implementation
- **`structured_planner.py`**: Planning logic mixed with multi-phase workflow management
- **`models.py`**: Provider abstractions mixed with configuration management
- **`constants.py`**: Constants mixed with enums and business configuration

#### 3. Infrastructure Concerns in Utils Layer
- **`prompt_utils.py`**: Token counting mixed with business-specific compression strategies
- **`language_detector.py`**: Detection logic mixed with file system operations
- **`token_counter.py`**: Pure utility mixed with model-specific configurations

#### 4. State Management Issues
- Graph state defined in `core/graph_state.py` but accessed across all layers
- Message protocol spans core and LLM layers without clear boundaries
- Business logic dependencies leak into utility functions

### Code Quality Impact

1. **Testability**: Mixed concerns make unit testing difficult
2. **Maintainability**: Changes in one area affect multiple unrelated components
3. **Extensibility**: Adding new features requires touching multiple layers
4. **Debugging**: Issues can originate from any mixed responsibility area

## Proposed Architecture

### Domain-Driven Design Structure

```
vivek/
├── domain/                    # Business logic & domain models
│   ├── workflow/             # Workflow orchestration (DDD bounded context)
│   │   ├── models/           # Domain entities and value objects
│   │   ├── services/         # Domain services
│   │   └── repositories/     # Domain repositories (interfaces)
│   ├── planning/             # Task planning domain
│   │   ├── models/
│   │   ├── services/
│   │   └── repositories/
│   ├── execution/            # Task execution domain
│   │   ├── models/
│   │   ├── services/
│   │   └── repositories/
│   └── review/               # Code review domain
│       ├── models/
│       ├── services/
│       └── repositories/
├── infrastructure/           # External concerns & adapters
│   ├── llm/                  # LLM provider implementations
│   │   ├── providers/        # Concrete provider implementations
│   │   ├── clients/          # LLM client abstractions
│   │   └── config/           # Provider configurations
│   ├── persistence/          # State persistence layer
│   │   ├── graph/            # Graph state persistence
│   │   ├── checkpoints/      # Checkpoint management
│   │   └── storage/          # Storage abstractions
│   ├── messaging/            # Inter-component communication
│   │   ├── protocols/        # Message protocols
│   │   ├── events/           # Event definitions
│   │   └── handlers/         # Message handlers
│   └── external/             # External service integrations
├── application/              # Use case orchestration
│   ├── services/             # Application services (use cases)
│   │   ├── workflow_service.py
│   │   ├── planning_service.py
│   │   ├── execution_service.py
│   │   └── review_service.py
│   ├── orchestrators/        # High-level orchestration
│   │   ├── graph_orchestrator.py
│   │   └── workflow_orchestrator.py
│   └── dtos/                 # Data transfer objects
├── shared/                   # Pure utilities & framework code
│   ├── kernel/               # Core utilities
│   │   ├── text/             # Text processing utilities
│   │   ├── tokens/           # Token counting utilities
│   │   ├── compression/      # Generic compression algorithms
│   │   └── validation/       # Generic validation utilities
│   ├── adapters/             # Protocol adapters
│   │   ├── langgraph/        # LangGraph adapters
│   │   └── filesystem/       # File system adapters
│   └── interfaces/           # Common interfaces
└── presentation/             # Entry points & CLI
    ├── cli/                  # Command line interface
    ├── api/                  # API endpoints (future)
    └── config/               # Configuration management
```

### Layer Responsibilities

#### Domain Layer
- **Pure business logic** with no external dependencies
- **Domain entities** and value objects
- **Domain services** implementing business rules
- **Repository interfaces** defining data access contracts
- **Domain events** for cross-bounded context communication

#### Infrastructure Layer
- **External service implementations** (LLM providers, databases, etc.)
- **Data persistence** adapters
- **Message queuing** implementations
- **External API** clients
- **Framework-specific** code (LangGraph, etc.)

#### Application Layer
- **Use case orchestration** coordinating domain services
- **Application services** implementing user-facing features
- **DTOs** for data transfer between layers
- **Transaction management** and cross-cutting concerns

#### Shared Layer
- **Framework-agnostic utilities**
- **Pure functions** with no side effects
- **Common interfaces** and abstractions
- **Cross-cutting concerns** (logging, validation, etc.)

## Implementation Phases

### Phase 1: Foundation (2-3 weeks)
**Goal**: Establish new architecture foundation without breaking existing functionality

#### 1.1 Create Domain Layer Structure
```bash
# Create new directory structure
mkdir -p domain/{workflow,planning,execution,review}/{models,services,repositories}
mkdir -p infrastructure/{llm,persistence,messaging}
mkdir -p application/{services,orchestrators,dtos}
mkdir -p shared/{kernel,adapters,interfaces}
mkdir -p presentation/{cli,config}
```

#### 1.2 Extract Domain Models
- Move `WorkflowPhase`, `PerspectiveHat`, `ActivityBreakdown`, `TaskDefinition`, `ContextSummary` to `domain/workflow/models/`
- Create domain entities for `Task`, `WorkItem`, `TaskPlan`, `ReviewResult`
- Define repository interfaces in `domain/*/repositories/`

#### 1.3 Create Infrastructure Abstractions
- Extract LLM provider interfaces to `infrastructure/llm/`
- Create persistence abstractions in `infrastructure/persistence/`
- Define message protocols in `infrastructure/messaging/`

#### 1.4 Move Pure Utilities
- Move `TokenCounter` to `shared/kernel/tokens/`
- Move text processing utilities to `shared/kernel/text/`
- Create generic compression algorithms in `shared/kernel/compression/`

### Phase 2: Domain Services (3-4 weeks)
**Goal**: Implement domain logic in isolation

#### 2.1 Planning Domain Service
- Extract planning logic from `structured_planner.py` and `enhanced_graph_nodes.py`
- Implement `PlanningService` with pure business logic
- Create planning repository interface

#### 2.2 Execution Domain Service
- Extract execution logic from `structured_executor.py` and `executor.py`
- Implement `ExecutionService` with TDD workflow logic
- Create execution repository interface

#### 2.3 Review Domain Service
- Extract review logic from graph nodes
- Implement `ReviewService` with quality assessment logic
- Create review repository interface

#### 2.4 Workflow Domain Service
- Extract workflow orchestration from `structured_workflow.py`
- Implement `WorkflowService` coordinating planning/execution/review
- Create workflow repository interface

### Phase 3: Infrastructure Implementation (2-3 weeks)
**Goal**: Implement infrastructure adapters

#### 3.1 LLM Infrastructure
- Implement provider abstractions in `infrastructure/llm/providers/`
- Create LLM client interfaces in `infrastructure/llm/clients/`
- Move provider configurations to `infrastructure/llm/config/`

#### 3.2 Persistence Infrastructure
- Implement graph state persistence in `infrastructure/persistence/graph/`
- Create checkpoint management in `infrastructure/persistence/checkpoints/`
- Implement storage abstractions in `infrastructure/persistence/storage/`

#### 3.3 Messaging Infrastructure
- Implement message protocols in `infrastructure/messaging/protocols/`
- Create event definitions in `infrastructure/messaging/events/`
- Implement message handlers in `infrastructure/messaging/handlers/`

### Phase 4: Application Services (2-3 weeks)
**Goal**: Implement use case orchestration

#### 4.1 Application Services
- Implement `WorkflowApplicationService` coordinating domain services
- Create `PlanningApplicationService` for task planning use cases
- Implement `ExecutionApplicationService` for task execution use cases
- Create `ReviewApplicationService` for code review use cases

#### 4.2 Orchestrators
- Implement `GraphOrchestrator` using application services
- Create `WorkflowOrchestrator` for high-level workflow management
- Implement DTOs for data transfer between layers

#### 4.3 Cross-cutting Concerns
- Implement transaction management
- Add logging and monitoring
- Create error handling abstractions

### Phase 5: Migration & Integration (3-4 weeks)
**Goal**: Migrate existing code and integrate new architecture

#### 5.1 Parallel Implementation
- Keep existing code working while building new architecture
- Create feature flags for gradual migration
- Implement adapter patterns for legacy integration

#### 5.2 Graph Node Migration
- Replace `enhanced_graph_nodes.py` with thin application service calls
- Update `langgraph_orchestrator.py` to use new orchestrators
- Migrate state management to infrastructure layer

#### 5.3 Testing & Validation
- Implement comprehensive test suite for new architecture
- Create integration tests for layer interactions
- Validate performance and functionality parity

#### 5.4 Legacy Code Removal
- Remove old implementation files
- Update imports and dependencies
- Clean up deprecated code

## Migration Strategy

### Incremental Migration Approach

1. **Strangler Fig Pattern**: Build new architecture alongside existing code
2. **Feature Flags**: Use feature toggles to switch between old/new implementations
3. **Adapter Pattern**: Create adapters to make new components work with old interfaces
4. **Parallel Testing**: Run both implementations and compare results

### Risk Mitigation

#### Technical Risks
- **Breaking Changes**: Use semantic versioning and deprecation warnings
- **Performance Impact**: Profile and optimize new architecture
- **Integration Issues**: Create comprehensive integration tests

#### Operational Risks
- **Downtime**: Implement zero-downtime deployment strategy
- **Rollback Plan**: Maintain ability to rollback to previous version
- **Data Migration**: Plan for state and configuration migration

### Success Metrics

#### Code Quality Metrics
- **Cyclomatic Complexity**: Reduce average complexity per file
- **Test Coverage**: Maintain >80% coverage during migration
- **Dependency Injection**: Achieve proper DI across all layers

#### Architecture Metrics
- **Layer Isolation**: No cross-layer dependencies except through defined interfaces
- **Single Responsibility**: Each class/module has one clear responsibility
- **Testability**: All business logic easily unit testable

## Benefits of Refactoring

### Maintainability
- **Clear Boundaries**: Each layer has well-defined responsibilities
- **Reduced Coupling**: Changes in one layer don't affect others
- **Easier Debugging**: Issues isolated to specific layers

### Testability
- **Unit Testing**: Pure domain logic easily testable
- **Mocking**: Infrastructure dependencies easily mockable
- **Integration Testing**: Clear interfaces between layers

### Extensibility
- **New Features**: Easy to add without touching existing code
- **Technology Changes**: Infrastructure layer isolates external dependencies
- **Scalability**: Clear separation allows independent scaling of layers

### Developer Experience
- **Onboarding**: New developers understand layer responsibilities quickly
- **Code Navigation**: Clear structure makes finding code intuitive
- **Refactoring Safety**: Changes have predictable impact scope

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-3)
- [ ] Create directory structure
- [ ] Extract domain models
- [ ] Create infrastructure abstractions
- [ ] Move pure utilities

### Phase 2: Domain Services (Weeks 4-7)
- [ ] Implement Planning domain service
- [ ] Implement Execution domain service
- [ ] Implement Review domain service
- [ ] Implement Workflow domain service

### Phase 3: Infrastructure (Weeks 8-10)
- [ ] Implement LLM infrastructure
- [ ] Implement persistence infrastructure
- [ ] Implement messaging infrastructure

### Phase 4: Application Services (Weeks 11-13)
- [ ] Implement application services
- [ ] Implement orchestrators
- [ ] Add cross-cutting concerns

### Phase 5: Migration (Weeks 14-17)
- [ ] Parallel implementation
- [ ] Graph node migration
- [ ] Testing and validation
- [ ] Legacy code removal

## Conclusion

This refactoring plan addresses the core architectural issues identified in the current codebase. By implementing a Domain-Driven Design approach with clear layer separation, we will achieve:

1. **Better Maintainability**: Clear boundaries and single responsibilities
2. **Improved Testability**: Isolated business logic and mockable dependencies
3. **Enhanced Extensibility**: Easy addition of new features and technologies
4. **Reduced Coupling**: Changes have predictable and limited impact

The phased approach ensures minimal disruption to existing functionality while building a solid foundation for future development.

## Next Steps

1. **Review and Approval**: Get stakeholder buy-in for the refactoring plan
2. **Team Alignment**: Ensure all developers understand the new architecture
3. **Kickoff Phase 1**: Begin with foundation work
4. **Regular Checkpoints**: Review progress at the end of each phase
5. **Continuous Integration**: Ensure CI/CD pipeline supports new structure

---

*Document Version: 1.0*
*Last Updated: October 13, 2025*
*Authors: Vivek AI Assistant*</content>
<parameter name="filePath">/home/sanket/workspaces/vivek/refactoring.md