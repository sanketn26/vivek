# Vivek Integration Test Suite - Home Rental Service

Comprehensive end-to-end integration test that builds a complete multi-language microservices application from scratch using Vivek.

## Overview

This integration test validates Vivek's capabilities by building a real-world **Home Rental Service** with three distinct components:

- **Go Backend**: Property management REST API with database layer
- **TypeScript Frontend**: React-based user interface for browsing and booking
- **Python Control Plane**: Service orchestration, health monitoring, and admin tools

Each component is developed using all four Vivek modes in sequence: **architect → coder → sdet → peer**

### Why This Approach?

Instead of testing isolated features in separate projects, this test:

✅ **Validates Real-World Usage**: Tests Vivek as developers would actually use it
✅ **Tests Cross-Language Coordination**: Ensures consistency across Go, TypeScript, and Python
✅ **Validates Mode Transitions**: Tests switching between architect, coder, sdet, and peer modes
✅ **Builds Production-Ready Code**: Creates a deployable microservices application
✅ **Tests Incremental Development**: Each phase builds on previous work

## Quick Start

### Prerequisites

1. **Install Vivek**:
   ```bash
   cd ../../  # Go to project root
   make setup
   ```

2. **Verify installation**:
   ```bash
   make test
   ```

3. **(macOS only) Install timeout command**:
   ```bash
   brew install coreutils
   ```

   This provides `gtimeout` which prevents tests from hanging indefinitely.

4. **For Real LLM Testing** - Choose one of these providers:

   **Option A: LM Studio (Recommended for Privacy)**
   - Start LM Studio and load these models:
     - **Planner**: `qwen/qwen3-4b-thinking-2507`
     - **Executor**: `qwen2.5-coder-7b-instruct-mlx`
   - Benefits: Fully local, private, no API costs

   **Option B: Sarvam AI (Cloud Alternative)**
   - Sign up at [sarvam.ai](https://sarvam.ai) and get API key
   - Set environment variable: `export SARVAM_API_KEY="your-key"`
   - Benefits: No local setup, cloud-based

### Running Tests

#### Mock Mode (Fast - No LLM Required)

Tests the orchestration flow **without making actual LLM calls**:

```bash
./examples/001-integration-tests/run_tests.sh
```

**Duration**: ~2-3 minutes
**What it validates**:
- ✅ LangGraph orchestration completes without errors
- ✅ Planner and executor nodes execute successfully
- ✅ State transitions work correctly
- ✅ CLI processes all 16 test cases
- ❌ Does NOT validate actual code generation quality
- ❌ Does NOT test real LLM integration

**Use Case**: Quick validation during development, CI/CD pipelines

#### Real LLM Mode (Full End-to-End)

Tests with **actual LLM models generating real code**. Uses your configured provider from `.vivek/config.yml`:

```bash
./examples/001-integration-tests/run_tests.sh --real
```

**Duration**: ~30-60 minutes (depending on models)
**What it validates**:
- ✅ Complete LangGraph orchestration with real LLMs
- ✅ Actual code generation in Go, TypeScript, Python
- ✅ Architecture designs from architect mode
- ✅ Test suites from sdet mode
- ✅ Code reviews from peer mode
- ✅ Quality scores and iteration logic
- ✅ Multi-turn context preservation

**Use Case**: Beta testing, release validation, model quality assessment

> **Important**: Real mode requires a running LLM provider (LM Studio or Sarvam) and will generate actual code files in the test project.

### Provider Configuration

The test reads provider settings from `.vivek/config.yml`. You can configure it to use:

#### LM Studio (Local, Privacy-First)

Edit `.vivek/config.yml`:
```yaml
planner:
  provider: lmstudio
  model: qwen/qwen3-4b-thinking-2507
  base_url: http://localhost:1234
  temperature: 0.1

executor:
  provider: lmstudio
  model: qwen2.5-coder-7b-instruct-mlx
  base_url: http://localhost:1234
  temperature: 0.2
```

> **Note**: Do NOT include `/v1` in `base_url` - it's automatically appended by the provider code.

Then start LM Studio and load the models above.

#### Sarvam AI (Cloud-Based)

Edit `.vivek/config.yml`:
```yaml
planner:
  provider: sarvam
  model: sarvam-2b-v0.5
  api_key: ${SARVAM_API_KEY}
  temperature: 0.1

executor:
  provider: sarvam
  model: sarvam-2b-v0.5
  api_key: ${SARVAM_API_KEY}
  temperature: 0.2
```

Set your API key:
```bash
export SARVAM_API_KEY="your-sarvam-api-key"
./examples/001-integration-tests/run_tests.sh --real
```

## Test Structure

The test builds a complete home rental service through **4 development phases**:

### Phase 1: Go Backend - Property Management API

| Mode | Task |
|------|------|
| **architect** | Design property management REST API architecture |
| **coder** | Implement Go API with models, repository, handlers |
| **sdet** | Create comprehensive Go tests (table-driven, httptest) |
| **peer** | Review Go code for idiomatic patterns and best practices |

**Deliverables**:
- `backend/internal/models/property.go`
- `backend/internal/repository/property_repository.go`
- `backend/internal/handlers/property_handler.go`
- `backend/cmd/server/main.go`
- Comprehensive test suite

### Phase 2: TypeScript Frontend - Property Listing UI

| Mode | Task |
|------|------|
| **architect** | Design React TypeScript component architecture |
| **coder** | Implement property listing UI with React hooks |
| **sdet** | Create Jest tests with React Testing Library |
| **peer** | Review TypeScript code for type safety and best practices |

**Deliverables**:
- `frontend/src/types/Property.ts`
- `frontend/src/services/api.ts`
- `frontend/src/components/PropertyCard.tsx`
- `frontend/src/components/PropertyList.tsx`
- `frontend/src/App.tsx`
- Full test coverage

### Phase 3: Python Control Plane - Service Orchestration

| Mode | Task |
|------|------|
| **architect** | Design async health check and orchestration system |
| **coder** | Implement Python control plane with asyncio |
| **sdet** | Create pytest suite with async tests |
| **peer** | Review Python code for Pythonic patterns and PEP 8 |

**Deliverables**:
- `control-plane/app/health_checker.py`
- `control-plane/app/config_manager.py`
- `control-plane/app/orchestrator.py`
- `control-plane/app/cli.py`
- Comprehensive pytest tests

### Phase 4: Integration & Documentation

| Mode | Task |
|------|------|
| **architect** | Design deployment and integration strategy |
| **coder** | Create docker-compose, Makefile, setup scripts |
| **sdet** | Create end-to-end integration tests |
| **peer** | Final review of entire codebase and architecture |

**Deliverables**:
- `docker-compose.yml`
- `Makefile`
- `.env.example`
- `scripts/setup.sh`
- End-to-end tests
- Final architecture assessment

## Project Structure Created

```
home-rental-service/
├── README.md                           # Project documentation
├── vivek.md                            # Vivek project configuration
├── .vivek/
│   └── config.yml                      # LLM provider configuration
│
├── backend/                            # Go Backend
│   ├── cmd/
│   │   └── server/
│   │       └── main.go                 # HTTP server entrypoint
│   ├── internal/
│   │   ├── models/
│   │   │   ├── property.go
│   │   │   └── property_test.go
│   │   ├── repository/
│   │   │   ├── property_repository.go
│   │   │   └── property_repository_test.go
│   │   └── handlers/
│   │       ├── property_handler.go
│   │       └── property_handler_test.go
│   └── go.mod
│
├── frontend/                           # TypeScript Frontend
│   ├── src/
│   │   ├── types/
│   │   │   ├── Property.ts
│   │   │   └── Property.test.ts
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── api.test.ts
│   │   ├── components/
│   │   │   ├── PropertyCard.tsx
│   │   │   ├── PropertyCard.test.tsx
│   │   │   ├── PropertyList.tsx
│   │   │   └── PropertyList.test.tsx
│   │   └── App.tsx
│   ├── public/
│   └── package.json
│
├── control-plane/                      # Python Control Plane
│   ├── app/
│   │   ├── health_checker.py
│   │   ├── config_manager.py
│   │   ├── orchestrator.py
│   │   └── cli.py
│   ├── tests/
│   │   ├── test_health_checker.py
│   │   ├── test_config_manager.py
│   │   ├── test_orchestrator.py
│   │   └── test_cli.py
│   └── requirements.txt
│
├── tests/                              # Integration Tests
│   └── e2e/
│       ├── test_property_workflow.py
│       ├── test_service_health.py
│       └── test_api_integration.py
│
├── docker-compose.yml                  # Multi-service orchestration
├── Makefile                            # Build and run commands
├── .env.example                        # Environment configuration
└── scripts/
    └── setup.sh                        # Initial setup script
```

## What Gets Tested

### Mock Mode Validation

Each test validates **orchestration flow only** (no real LLM calls):

✅ **LangGraph Orchestration**: Proper state transitions through graph nodes
✅ **Planner Analysis**: Task breakdown and quality review logic (with mock responses)
✅ **Executor Routing**: Correct mode-specific prompt generation
✅ **State Management**: Context preservation across iterations
✅ **Quality Loop**: Review and iteration mechanism
✅ **CLI Integration**: Test mode input processing
✅ **Error Handling**: No Python exceptions during orchestration

**Pass Criteria (Mock Mode)**:
- CLI exits successfully (exit code 0)
- Log file contains "FINAL RESULT" (orchestration completed)
- No Python tracebacks or exceptions

**What Mock Mode Does NOT Test**:
- ❌ Actual LLM API connectivity
- ❌ Real code generation quality
- ❌ Model-specific behavior
- ❌ Token usage or performance

### Real LLM Mode Validation

Tests **end-to-end with real LLM calls**:

✅ **LLM Connectivity**: Successful connection to LM Studio or Sarvam
✅ **Code Generation Quality**: Syntactically correct Go, TypeScript, Python
✅ **Architecture Decisions**: Reasonable design choices in architect mode
✅ **Test Coverage**: Comprehensive test suites in sdet mode
✅ **Code Reviews**: Actionable feedback in peer mode
✅ **Multi-Turn Coherence**: Context maintained across 16 sequential requests
✅ **Cross-Language Consistency**: Unified patterns across all three languages
✅ **Quality Scores**: Planner assigns reasonable quality scores (>0.6 target)

**Pass Criteria (Real Mode)**:
- CLI exits successfully
- Log file contains "FINAL RESULT" with actual generated content
- Quality score > 0 (extracted from logs)
- Output contains substantial content (>10 lines)
- No connection errors to LLM provider

**Expected Artifacts (Real Mode)**:
After running real mode tests, you should see actual files created in `home-rental-service/`:
- `backend/internal/models/property.go` (Go code from coder mode)
- `frontend/src/types/Property.ts` (TypeScript interfaces)
- `control-plane/app/health_checker.py` (Python code)
- Test files, docker-compose.yml, Makefiles, etc.

## Understanding Results

### Success Output

```
╔════════════════════════════════════════════════════════════════════╗
║         Vivek Integration Test - Home Rental Service (Mock Mode)  ║
╚════════════════════════════════════════════════════════════════════╝

Mode:         mock
Project:      /path/to/home-rental-service
Log Dir:      /path/to/test_logs
Results:      /path/to/test_results.log

✓ Vivek CLI found

🏗️  Setting up Home Rental Service project...
✓ Project structure created

═══════════════════════════════════════════════════════════════════
  Phase 1: Go Backend - Property Management API
═══════════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────────────
Test 1: go-backend × /architect
────────────────────────────────────────────────────────────────────
Task: Design a property management REST API architecture...
✅ PASSED

[... 15 more tests ...]

╔════════════════════════════════════════════════════════════════════╗
║                   Home Rental Service - Test Summary               ║
╚════════════════════════════════════════════════════════════════════╝

  Mode:         mock
  Total Tests:  16
  Passed:       16
  Failed:       0
  Pass Rate:    100%

🎉 All tests passed! Home Rental Service is ready!

Next steps:
  cd /path/to/home-rental-service
  # Review generated code in backend/, frontend/, control-plane/
  # Check docker-compose.yml and Makefile
  # Run 'make build' and 'make run' to start services
```

### Failure Example

```
────────────────────────────────────────────────────────────────────
Test 5: typescript-frontend × /coder
────────────────────────────────────────────────────────────────────
Task: Implement the property listing UI...
❌ FAILED

⚠️  Some tests failed. Review logs for details.

Debugging tips:
  - Check /path/to/test_logs for detailed test logs
  - Review /path/to/test_results.log for summary
  - Examine generated code in /path/to/home-rental-service
```

## Detailed Logs

All test outputs are saved to:

- **Summary**: `test_results.log` - Pass/fail status for each test
- **Detailed Logs**: `test_logs/` - Full CLI output for each test including:
  - LangGraph state transitions
  - Planner analysis results
  - Executor generated output
  - Review scores and feedback
  - Iteration counts

Example log file: `test_logs/go-backend-architect_20251010_165500.log`

## Troubleshooting

### Mock Mode Fails

**Symptom**: Tests fail with Python exceptions

**Solution**: Check Vivek installation:
```bash
cd ../..
make test  # Should pass all 111+ unit tests
```

### Real LLM Mode Connection Error

**Symptom**: Tests fail to connect to LLM provider

**Solution A - Using LM Studio**:
1. Open LM Studio
2. Load `qwen/qwen3-4b-thinking-2507` for Planner
3. Load `qwen2.5-coder-7b-instruct-mlx` for Executor
4. Verify: `curl http://localhost:1234/v1/models`
5. Ensure `.vivek/config.yml` has `provider: lmstudio` and `base_url: http://localhost:1234/v1`

**Solution B - Using Sarvam AI**:
1. Get API key from [sarvam.ai](https://sarvam.ai)
2. Set environment variable: `export SARVAM_API_KEY="your-key"`
3. Ensure `.vivek/config.yml` has `provider: sarvam` and `api_key: ${SARVAM_API_KEY}`
4. Verify: API key is set with `echo $SARVAM_API_KEY`

### Tests Timeout

**Symptom**: Tests hang or timeout

**Solution**:
- **Mock mode**: Should complete in 2-3 minutes, check for Python errors
- **Real mode**: May take 30-60 minutes depending on model speed
- Increase timeout values in [run_tests.sh](run_tests.sh:286) if needed

### Generated Code Quality Issues

**Symptom**: Real LLM mode passes but generated code is poor quality

**Solution**: Try different models:
- **Faster/Smaller**: `qwen2.5-coder:3b` (less accurate)
- **Balanced**: `qwen2.5-coder:7b` (recommended)
- **Best Quality**: `deepseek-coder:6.7b` or cloud models (GPT-4, Claude)

## Beta Release Criteria

Before tagging v0.2.0-beta, ensure:

- [ ] All 16 integration tests pass in mock mode
- [ ] At least 12/16 tests pass in real LLM mode (75%+)
- [ ] Generated code compiles/runs without errors
- [ ] Unit tests pass (111+ tests)
- [ ] LangGraph orchestration completes without exceptions
- [ ] Quality scores > 0.6 for most iterations

## Next Steps

After running integration tests:

1. **Review Generated Project**: `cd home-rental-service && tree`
2. **Inspect Logs**: Check `test_logs/` for any issues
3. **Validate Code**: Try running generated services locally
4. **Run Unit Tests**: `cd ../.. && make test`
5. **Tag Release**: If all criteria met, tag v0.2.0-beta

## Version History

### Current (v0.2.0-beta)
- Complete home rental service integration test
- 16 tests across 4 phases
- Tests architect, coder, sdet, peer modes
- Multi-language coordination (Go, TypeScript, Python)

### v0.1.0
- Initial plugin-based architecture
- Manual testing only

## Contributing

To modify the integration test:

1. Edit [run_tests.sh](run_tests.sh)
2. Update test cases in respective phase sections
3. Adjust timeouts if needed (mock: 60s, real: 300s)
4. Update this README with new test descriptions
5. Run full suite to verify changes

## Quick Reference - Provider Setup

### LM Studio Setup (Local)

```bash
# 1. Start LM Studio and load models
# 2. Create/edit .vivek/config.yml in the test project:
cat > .vivek/config.yml << 'EOF'
planner:
  provider: lmstudio
  model: qwen/qwen3-4b-thinking-2507
  base_url: http://localhost:1234
  temperature: 0.1

executor:
  provider: lmstudio
  model: qwen2.5-coder-7b-instruct-mlx
  base_url: http://localhost:1234
  temperature: 0.2
EOF

# 3. Run tests
./examples/001-integration-tests/run_tests.sh --real
```

**Important**: Use `http://localhost:1234` NOT `http://localhost:1234/v1` - the `/v1` path is added automatically.

### Sarvam AI Setup (Cloud)

```bash
# 1. Get API key from https://sarvam.ai
# 2. Set environment variable
export SARVAM_API_KEY="your-sarvam-api-key-here"

# 3. Create/edit .vivek/config.yml in the test project:
cat > .vivek/config.yml << 'EOF'
planner:
  provider: sarvam
  model: sarvam-2b-v0.5
  api_key: ${SARVAM_API_KEY}
  temperature: 0.1

executor:
  provider: sarvam
  model: sarvam-2b-v0.5
  api_key: ${SARVAM_API_KEY}
  temperature: 0.2
EOF

# 4. Run tests
./examples/001-integration-tests/run_tests.sh --real
```

### Switching Providers

You can switch providers by simply editing `.vivek/config.yml` and rerunning the tests. No code changes needed!

## License

MIT - See project root LICENSE file
