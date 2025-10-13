# Agentic Context Tests

Comprehensive test suite for the `vivek.agentic_context` package.

## Test Structure

### Unit Tests
- `test_agentic_context_config.py` - Configuration management and presets
- `test_agentic_context_storage.py` - Context storage and hierarchy management
- `test_agentic_context_manager.py` - Context manager orchestration
- `test_agentic_context_workflow.py` - Workflow context managers
- `test_agentic_context_tag_normalization.py` - Tag vocabulary and normalization
- `test_agentic_context_semantic_retrieval.py` - Embedding models and similarity
- `test_agentic_context_retrieval_strategies.py` - All retrieval strategies

### Integration Tests
- `test_agentic_context_integration.py` - Complete workflow scenarios and cross-component integration

## Running Tests

### Prerequisites
```bash
pip install -r requirements-test.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Tests that require embedding models (requires additional dependencies)
pytest -m embedding

# Slow tests
pytest -m slow
```

### Run Specific Files
```bash
# Test configuration functionality
pytest tests/test_agentic_context_config.py

# Test storage functionality
pytest tests/test_agentic_context_storage.py

# Test workflow functionality
pytest tests/test_agentic_context_workflow.py
```

### Run with Coverage
```bash
# Generate coverage report
pytest --cov=vivek.agentic_context --cov-report=html --cov-report=term

# View HTML coverage report
open htmlcov/index.html
```

## Test Configuration

The tests use `pytest.ini` for configuration:

- **Test Discovery**: Automatically finds tests in `tests/` directory
- **Markers**: Use markers to categorize tests (`unit`, `integration`, `embedding`, `slow`)
- **Coverage**: Optional coverage reporting (requires `pytest-cov`)

## Test Design Principles

### 1. Comprehensive Coverage
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions and complete workflows
- **Edge Cases**: Cover error conditions and boundary cases

### 2. Mocking Strategy
- **External Dependencies**: Mock embedding models, file I/O, and network calls
- **Internal Components**: Use real implementations where possible for better testing
- **Deterministic Results**: Ensure tests produce consistent results

### 3. Test Organization
- **Setup/Teardown**: Proper test isolation and cleanup
- **Descriptive Names**: Clear test method names indicating what they test
- **Documentation**: Docstrings explaining complex test scenarios

## Key Testing Areas

### Configuration System
- Preset validation and customization
- Configuration file I/O (YAML/JSON)
- Nested configuration overrides

### Context Hierarchy
- 3-layer hierarchy (Session → Activity → Task)
- Context item storage and retrieval
- Thread-safe operations

### Retrieval Strategies
- Tag-based retrieval with normalization
- Semantic retrieval with embeddings
- Hybrid and auto strategy selection
- Performance and caching behavior

### Workflow Management
- Context manager pattern implementation
- Automatic context tracking
- Error handling and cleanup

### Integration Scenarios
- Complete workflow execution
- Strategy switching during execution
- Concurrent workflow handling
- Large-scale context management

## Adding New Tests

When adding new functionality:

1. **Create Test File**: Follow naming convention `test_<module_name>.py`
2. **Add Markers**: Use appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
3. **Mock External Dependencies**: Avoid slow or flaky external dependencies
4. **Test Error Cases**: Include validation and error handling tests
5. **Update Documentation**: Add tests to this README

## Continuous Integration

The test suite is designed to run in CI environments:

- **Fast Execution**: Unit tests complete quickly
- **Reliable**: No flaky tests or external dependencies by default
- **Comprehensive**: High test coverage of critical paths
- **Configurable**: Can enable additional tests (embedding, integration) as needed

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed from `requirements-test.txt`
2. **Mock Issues**: Check that mocks are properly configured for the test scenario
3. **Path Issues**: Verify that import paths work from the project root

### Debug Tips

1. **Verbose Output**: Use `pytest -v` for detailed test output
2. **Debug Individual Tests**: Use `pytest tests/test_file.py::TestClass::test_method -v -s`
3. **Inspect Mock Calls**: Add assertions to verify mock behavior
4. **Check Test Isolation**: Ensure tests don't interfere with each other
