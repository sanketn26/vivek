# Changelog

## [Unreleased]

### Added - Agentic Context Refactoring
- Comprehensive test suite for refactored agentic_context (117 passing tests)
- 8 new test modules covering all refactored components:
  - `test_agentic_context_config.py` - Config dataclass tests
  - `test_agentic_context_storage.py` - Context storage CRUD operations
  - `test_agentic_context_retrieval_strategies.py` - Retriever functionality
  - `test_agentic_context_semantic_retrieval.py` - Embedding model tests
  - `test_agentic_context_tag_normalization.py` - Tag normalization
  - `test_agentic_context_workflow.py` - Workflow context managers
  - `test_agentic_context_manager.py` - ContextManager integration
  - `test_agentic_context_integration.py` - End-to-end workflow tests
- Documentation organization into `docs/` structure:
  - `docs/refactoring/` - Technical refactoring documentation
  - `docs/guides/` - User guides and examples
  - `docs/reference/` - API reference (coming soon)

### Changed - Agentic Context Refactoring
**Code Reduction & Simplification (73% overall reduction)**
- `config.py`: 279 → 36 lines (87% reduction)
  - Replaced 5 presets with simple dataclass defaults
  - Removed nested configuration structures
  - Added class methods: `default()`, `semantic()`, `from_dict()`
- `context_storage.py`: 327 → 188 lines (43% reduction)
  - Flat model using parent_id references instead of nested hierarchies
  - Simple CRUD operations with clear responsibility
  - Removed thread locks and complex state management
- `context_manager.py`: 327 → 133 lines (59% reduction)
  - Simple interface coordinating storage + retrieval
  - Clear delegation of responsibilities
  - Removed factory patterns and unnecessary abstraction
- `workflow.py`: 1,224 → 121 lines (90% reduction!)
  - Context managers (SessionContext, ActivityContext, TaskContext)
  - Replaced complex state tracking with Python context manager protocol
  - Removed nested class hierarchies and callbacks
- `retrieval_strategies.py`: 633 → 105 lines (83% reduction)
  - Single Retriever class replacing 5 specialized retrievers
  - Optional semantic search via parameter
  - Tag-based scoring with simple interface
- `semantic_retrieval.py`: 310 → 40 lines (87% reduction)
  - Simple wrapper over SentenceTransformer
  - Removed caching and batch processing (let caller manage)
  - Clean encode() and similarity() methods
- `tag_normalization.py`: 310 → 30 lines (90% reduction)
  - SYNONYMS dict instead of complex tag management
  - Simple functions for tag normalization
  - Direct lookup without abstraction layers

**Architecture Improvements**
- Removed all thread locking (simplified for agentic use)
- Eliminated factory patterns where not needed
- Flat data structures instead of hierarchies
- Single responsibility per class
- Optional features via parameters instead of subclasses

### Removed - Agentic Context Refactoring
- 5 specialized Retriever classes (AutoRetriever, SemanticRetriever, TagRetriever, etc.)
- Complex nested context classes
- Tag presets and preset management
- Caching layer in semantic retrieval
- Thread-based concurrency primitives
- Complex state persistence mechanisms
- Multiple configuration factories
- 1,617+ lines of unnecessary code

### Migration Guide
**Breaking Changes:**
- `get_config()` → `Config.default()` or `Config.from_dict()`
- `Config.get_preset("semantic")` → `Config.semantic()`
- `AutoRetriever` → `Retriever(use_semantic=True)`
- `ActivityContext` no longer a separate import; use `SessionContext.activity()`
- `retrieve()` now takes `query_tags: List[str]` instead of single string

**API Improvements:**
- All dataclasses now use standard Python `@dataclass` decorator
- Simple methods instead of complex inheritance
- Optional semantic features via `use_semantic` parameter
- Direct access to context storage without layers

---

## [3.0.0] - 2024-10-16

### Major Refactoring

Complete architecture overhaul following SOLID principles.

### Added
- Clean Architecture with clear layer separation
- Dependency Injection container
- Rich Task domain model with business logic
- Repository pattern for data access
- Concrete LLM providers (Ollama, Mock)
- State repositories (File, Memory)
- Centralized test mocks

### Changed
- Converted from setuptools to Poetry
- Simplified orchestrator (410 → 193 lines)
- Unified Task and WorkItem models
- Updated all services to use repositories
- Dynamic task generation instead of hard-coded

### Removed
- Legacy LangGraph orchestrator (3,000+ lines)
- Old LLM provider implementations
- Duplicate code and DRY violations
- Anemic domain models

### Fixed
- All SOLID principle violations
- Poetry dependency version constraints
- Test suite (183/194 passing)
- Pre-commit configuration

## [2.0.0] - Previous Version

- Initial refactoring attempt
- Mixed Poetry/setuptools setup
- Some architecture improvements

## [1.0.0] - Original Version

- LangGraph-based orchestration
- Complex multi-node workflow
- Mixed responsibilities
