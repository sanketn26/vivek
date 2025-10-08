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

3. **(Optional) Initialize config** for real LLM tests:
   ```bash
   cd ../../  # Go to project root
   vivek init --local-model qwen2.5-coder:7b --executor-model qwen2.5-coder:7b
   ```

   This creates `.vivek/config.yml` which the test runner will use if no `--model` is specified.

### Running Tests

#### Mock Mode (Default - Fast)

Tests all scenarios using mocked LLM providers:

```bash
./examples/001-integration-tests/run_tests.sh
# or explicitly:
./examples/001-integration-tests/run_tests.sh --mock
```

#### Real LLM Mode (Actual Model Testing)

**Auto-detect local LLM** (Ollama or LM Studio):
```bash
./examples/001-integration-tests/run_tests.sh --real
```

**Ollama** (explicit):
```bash
./examples/001-integration-tests/run_tests.sh --real --provider ollama --model qwen2.5-coder:7b
```

**LM Studio**:
```bash
./examples/001-integration-tests/run_tests.sh --real --provider lmstudio --model qwen2.5-coder
```

**OpenAI**:
```bash
./examples/001-integration-tests/run_tests.sh --real --provider openai --model gpt-4o --api-key sk-...
```

**Anthropic**:
```bash
./examples/001-integration-tests/run_tests.sh --real --provider anthropic --model claude-3-5-sonnet-20241022 --api-key sk-ant-...
```

**SarvamAI**:
```bash
# Using command-line API key
./examples/001-integration-tests/run_tests.sh --real --provider sarvam --api-key your-sarvam-key

# Or using environment variable
export SARVAM_API_KEY="your-sarvam-key"
./examples/001-integration-tests/run_tests.sh --real --provider sarvam
```

**Custom Endpoint**:
```bash
./examples/001-integration-tests/run_tests.sh --real --provider custom --url http://your-endpoint:8000 --model your-model
```

### Configuration Priority

The test runner uses this order to determine settings:

1. **Command-line arguments** (highest priority)
   - `--provider`, `--model`, `--url`, `--api-key`
2. **Config file** (`.vivek/config.yml` in project root)
   - Used if CLI args not provided
   - Reads `executor_model` setting
3. **Auto-detection** (lowest priority)
   - Detects Ollama (port 11434) or LM Studio (port 1234)
   - Queries available models from provider API

**Example workflow**:
```bash
# One-time setup: create config
cd /path/to/vivek
vivek init --executor-model qwen2.5-coder:7b

# Run tests using config
./examples/001-integration-tests/run_tests.sh --real

# Override config for specific test
./examples/001-integration-tests/run_tests.sh --real --model deepseek-coder:6.7b
```

## Test Structure

```
001-integration-tests/
├── README.md                      # This file
├── run_tests.sh                   # Unified test runner (mock + real LLM)
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

### Mock Mode Tests

Each test validates:

✅ **Plugin Discovery**: All language plugins are found and loaded
✅ **Executor Creation**: Correct executor is created for language/mode
✅ **Prompt Building**: Prompts are generated with language-specific instructions
✅ **Language Context**: Prompts contain appropriate language conventions
✅ **Token Counting**: Prompts are logged with token counts
✅ **No Errors**: No exceptions or failures during execution

### Real LLM Mode Tests

In addition to mock mode validations, real LLM tests also verify:

✅ **LLM Connectivity**: Connection to local or cloud LLM provider
✅ **Actual Generation**: Real text generation based on prompts
✅ **Response Quality**: Generated responses contain expected elements
✅ **Provider Compatibility**: Works with Ollama, LM Studio, OpenAI, Anthropic
✅ **Language-Specific Output**: Generated code uses correct language conventions
✅ **Mode Behavior**: Different modes produce appropriate responses (code vs design vs tests)

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

### Real LLM Mode Fails with Connection Error

**Solution**: Verify LLM server is running:

**For Ollama**:
```bash
curl http://localhost:11434/api/tags
# Should return list of models
```

**For LM Studio**:
```bash
curl http://localhost:1234/v1/models
# Should return list of loaded models
```

### Slow Test Execution

**Expected Times**:
- **Mock Mode**: 0.5-1 second per test (~10-15 seconds total)
- **Real LLM Mode**: 5-30 seconds per test depending on model size and hardware

If tests are slower than expected, check:
- Model size (3B models faster than 7B models)
- System resources (RAM, CPU)
- GPU availability (for faster inference)
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
