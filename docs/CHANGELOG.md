# Changelog

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
