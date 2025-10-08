# Vivek Integration Test Suite

Comprehensive integration tests for Vivek v0.2.0 Beta covering all language × mode combinations.

## Overview

This test suite validates that Vivek correctly handles all supported languages (Python, TypeScript, Go) across all execution modes (Coder, Architect, Peer, SDET).

### Test Coverage

- **3 Languages**: Python, TypeScript, Go
- **4 Modes per Language**: coder, architect, peer, sdet
- **Total Scenarios**: 12 comprehensive integration tests
- **Real Projects**: Sample calculator implementations in each language

## Quick Start

### Prerequisites

1. **Install Vivek dependencies**:
   ```bash
   cd ../../  # Go to project root
   make setup
   ```

2. **Verify installation**:
   ```bash
   make test
   ```

### Running Integration Tests

From the project root:

```bash
./examples/001-integration-tests/run_integration_tests.sh
```

Or from the examples directory:

```bash
cd examples/001-integration-tests
./run_integration_tests.sh
```

## Test Structure

```
001-integration-tests/
├── README.md                      # This file
├── run_integration_tests.sh       # Main test runner
├── test_results.log               # Generated test results
├── python-project/
│   └── calculator.py              # Sample Python code
├── typescript-project/
│   ├── calculator.ts              # Sample TypeScript code
│   └── package.json
└── go-project/
    ├── calculator.go              # Sample Go code
    └── go.mod
```

## Test Scenarios

### Python Tests

1. **Coder Mode**: Add modulo function to calculator
2. **Architect Mode**: Design REST API architecture
3. **Peer Mode**: Review code for best practices
4. **SDET Mode**: Create comprehensive pytest suite

### TypeScript Tests

5. **Coder Mode**: Add power function to calculator
6. **Architect Mode**: Design modular architecture with interfaces
7. **Peer Mode**: Review type safety and best practices
8. **SDET Mode**: Create Jest test suite with full coverage

### Go Tests

9. **Coder Mode**: Add square root function with error handling
10. **Architect Mode**: Design concurrent calculator with goroutines
11. **Peer Mode**: Review idiomatic Go patterns
12. **SDET Mode**: Create table-driven tests

## What Gets Tested

Each test validates:

✅ **Plugin Discovery**: All language plugins are found and loaded
✅ **Executor Creation**: Correct executor is created for language/mode
✅ **Prompt Building**: Prompts are generated with language-specific instructions
✅ **Language Context**: Prompts contain appropriate language conventions
✅ **Token Counting**: Prompts are logged with token counts
✅ **No Errors**: No exceptions or failures during execution

## Understanding Results

### Success Output

```
✅ PASSED - Test completed successfully
✓ Discovered 3 language plugins
✓ Created executor for python/coder
✓ Built prompt (477 chars)
✓ Prompt contains language-specific instructions
```

### Failure Output

```
❌ FAILED - Test encountered an error
Error: Plugin not found for language=python
```

### Summary Report

```
╔════════════════════════════════════════╗
║      Test Summary Report               ║
╚════════════════════════════════════════╝

  Total Tests:  12
  Passed:       12
  Failed:       0
  Pass Rate:    100%

🎉 All tests passed! Ready for beta release.
```

## Detailed Results

Full test results including:
- Test execution timestamps
- Detailed output for each test
- Plugin discovery logs
- Token counts for generated prompts
- Pass/fail status for each scenario

Results are saved to: `test_results.log`

## Troubleshooting

### Tests Fail with "Plugin not found"

**Solution**: Run plugin discovery manually:
```bash
cd ../..
./venv/bin/python3 -c "
from vivek.llm.plugins.base.registry import discover_plugins
count = discover_plugins()
print(f'Discovered {count} plugins')
"
```

### Tests Fail with "Module not found"

**Solution**: Ensure virtual environment is activated:
```bash
cd ../..
source venv/bin/activate  # or ./venv/bin/activate on some systems
```

### Slow Test Execution

**Expected**: Each test takes ~0.5-1 second. Total suite runs in ~10-15 seconds.

If tests are slower, check:
- System resources
- Virtual environment activation
- Python version (3.10+ recommended)

## Beta Release Criteria

Before tagging v0.2.0-beta, ensure:

- [ ] All 12 integration tests pass (100%)
- [ ] Unit tests pass (111 tests)
- [ ] No Python errors or warnings
- [ ] Plugin discovery works for all languages
- [ ] Token counting logs appear
- [ ] Prompts contain language-specific instructions

## Next Steps

After running integration tests:

1. **Review Results**: Check `test_results.log` for details
2. **Fix Issues**: Address any failed tests
3. **Run Unit Tests**: `cd ../.. && make test`
4. **Tag Release**: If all tests pass, tag v0.2.0-beta

## Version History

### v0.2.0-beta (Current)
- Comprehensive integration test suite
- 12 scenarios covering all language × mode combinations
- Automated test runner with detailed reporting
- Sample projects in Python, TypeScript, and Go

### v0.1.0
- Initial plugin-based architecture
- Manual testing only

## Contributing

To add new test scenarios:

1. Add sample project files to appropriate language directory
2. Add `run_test` call to `run_integration_tests.sh`
3. Update this README with new test description
4. Run full suite to verify

## License

MIT - See project root LICENSE file
