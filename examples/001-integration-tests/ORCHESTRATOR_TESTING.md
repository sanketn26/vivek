# Orchestrator Flow Testing

End-to-end testing of Vivek's dual-brain architecture with LangGraph orchestration using the Vivek CLI.

## Overview

This test suite validates the complete **Planner → Executor → Reviewer** flow with real LLMs through Vivek's CLI interface. Tests are configured to use different models for planning vs execution for optimal performance.

## Dual-Model Architecture

### Configuration

Tests use two specialized models:
- **Planner**: `qwen/qwen3-4b-thinking-2507` - Optimized for reasoning and task breakdown
- **Executor**: `qwen2.5-coder-7b-instruct-mlx` - Optimized for code generation

This configuration is stored in each test project's `.vivek/config.yml`:

```yaml
llm_configuration:
  provider: lmstudio
  planner_model: qwen/qwen3-4b-thinking-2507
  executor_model: qwen2.5-coder-7b-instruct-mlx
  provider_config:
    base_url: http://localhost:1234
```

## What Gets Tested

### Complete Orchestration Flow

```
User Input
    ↓
Planner Brain (analyzes & creates task plan)
    ↓
Executor Brain (implements solution)
    ↓
Reviewer Brain (evaluates quality)
    ↓
Final Output (with iteration if quality < 0.6)
```

### Test Coverage

✅ **All language × mode combinations** (3 languages × 4 modes = 12 tests)
✅ **CLI integration** (config loading, mode switching, orchestration)
✅ **Dual-model coordination** (planner model ≠ executor model)
✅ **Real LLM communication** (with LM Studio backend)
✅ **Test logs** (prompts, responses, timing, errors)

## Running the Tests

### Prerequisites

1. **Start LM Studio** with both models loaded:
   ```bash
   # Check LM Studio is running with models
   curl http://localhost:1234/v1/models
   ```

   Load these models in LM Studio:
   - `qwen/qwen3-4b-thinking-2507`
   - `qwen2.5-coder-7b-instruct-mlx`

2. **Ensure Vivek is installed**:
   ```bash
   cd /path/to/vivek
   make setup
   ```

### Run Test Suite

#### Mock Mode (Fast - No LLM Calls)

```bash
./examples/001-integration-tests/run_tests.sh
# or explicitly:
./examples/001-integration-tests/run_tests.sh --mock
```

Mock mode validates:
- CLI can be invoked
- Config files are readable
- Mode switching works
- No actual LLM calls made

**Expected time**: ~10-15 seconds total

#### Real LLM Mode (Full Orchestration)

```bash
./examples/001-integration-tests/run_tests.sh --real
```

Real mode tests:
- Full planner → executor → reviewer flow
- Actual model inference with configured models
- Quality-based iteration (if score < 0.6)
- Complete output generation

**Expected time**: ~5-30 minutes depending on model performance

### Output

```
╔════════════════════════════════════════════════════════════════════╗
║         Vivek Integration Tests - Real LLM Mode                   ║
╚════════════════════════════════════════════════════════════════════╝

Mode:         real
Log Dir:      examples/001-integration-tests/test_logs
Results:      examples/001-integration-tests/test_results.log

✓ Vivek CLI found
🔍 Checking LM Studio...
✓ LM Studio detected

Expected models:
  Planner:  qwen/qwen3-4b-thinking-2507
  Executor: qwen2.5-coder-7b-instruct-mlx

📋 Running test suite...

═══════════════════════════════════════════════════════════════════
  Python Language Tests
═══════════════════════════════════════════════════════════════════

────────────────────────────────────────────────────────────────────
Test 1: python × coder
────────────────────────────────────────────────────────────────────
Task: Add a modulo function to calculate remainder of a/b with zero division handling

Running with real LLM (config from .vivek/config.yml)...
✅ PASSED

[... 11 more tests ...]

╔════════════════════════════════════════════════════════════════════╗
║                        Test Summary Report                         ║
╚════════════════════════════════════════════════════════════════════╝

  Mode:         real
  Total Tests:  12
  Passed:       12
  Failed:       0
  Pass Rate:    100%

📄 Full results: examples/001-integration-tests/test_results.log
📁 Test logs: examples/001-integration-tests/test_logs

🎉 All tests passed! Ready for beta release.
```

## Log Files

### Location

```
examples/001-integration-tests/test_logs/
```

### Naming Pattern

```
{language}-{mode}_{timestamp}.log
```

**Examples:**
```
python-coder_20251009_114655.log
typescript-architect_20251009_115202.log
go-sdet_20251009_120145.log
```

### Log Structure

Each log contains:

1. **Test Metadata**
   ```
   ========================================
   TEST: python-coder
   Started: Wed Oct  9 11:46:55 PDT 2025
   ========================================
   Language: python
   Mode: coder
   Task: Add a modulo function...
   Project: .../python-project
   ========================================
   ```

2. **CLI Invocation**
   - Command executed
   - Config file loaded
   - Models detected

3. **Orchestrator Output**
   - Planner analysis (from thinking model)
   - Executor implementation (from coding model)
   - Reviewer evaluation
   - Iteration info (if triggered)

4. **Final Result**
   ```
   RESULT: PASSED
   ```

## Test Cases

### Python Tests (4 scenarios)

1. **Coder**: Add modulo function with zero division handling
2. **Architect**: Design REST API architecture for calculator
3. **Peer**: Review calculator code for best practices
4. **SDET**: Create pytest test suite for all functions

### TypeScript Tests (4 scenarios)

5. **Coder**: Add power function (base to exponent)
6. **Architect**: Design modular architecture with interfaces
7. **Peer**: Review TypeScript code for type safety
8. **SDET**: Create Jest test suite with 100% coverage

### Go Tests (4 scenarios)

9. **Coder**: Add square root function with error handling
10. **Architect**: Design concurrent calculator with goroutines
11. **Peer**: Review Go code for idiomatic patterns
12. **SDET**: Create table-driven tests

## Configuration Details

### Project Config Files

Each test project has its own config:

```
python-project/.vivek/config.yml
typescript-project/.vivek/config.yml
go-project/.vivek/config.yml
```

All use the same dual-model configuration:
- **Planner**: Thinking model for analysis
- **Executor**: Coding model for implementation

### Why Dual Models?

- **Thinking model** (Qwen3-4B-Thinking) excels at:
  - Analyzing requirements
  - Breaking down tasks
  - Evaluating quality
  - Reasoning about architecture

- **Coding model** (Qwen2.5-Coder-7B-MLX) excels at:
  - Code generation
  - Language-specific patterns
  - Implementation details
  - Syntax correctness

This separation allows each model to focus on what it does best.

## Customizing Tests

### Change Models

Edit the config files in each test project:

```yaml
llm_configuration:
  planner_model: your-planner-model
  executor_model: your-executor-model
```

### Add New Test Cases

Edit `run_tests.sh` and add a new `run_test` call:

```bash
run_test "python" "coder" "Your task description here"
```

### Adjust Timeouts

For slower models, increase timeout in run_tests.sh:

```bash
# Change from 180s to 300s
if timeout 300 "$VIVEK_CLI" chat --test-mode ...
```

## Analysis

### View Test Results

```bash
cat examples/001-integration-tests/test_results.log
```

### View Specific Test Log

```bash
cat examples/001-integration-tests/test_logs/python-coder_*.log
```

### Check Pass Rate

```bash
grep "Pass Rate:" examples/001-integration-tests/test_results.log
```

### Count Failures

```bash
grep "FAILED" examples/001-integration-tests/test_logs/*.log | wc -l
```

## Troubleshooting

### "Vivek CLI not found"

**Solution**: Install Vivek first
```bash
cd /path/to/vivek
make setup
```

### "LM Studio not running"

**Solution**: Start LM Studio and load models
```bash
# Check if running
curl http://localhost:1234/v1/models

# Should return JSON with both models listed
```

### Tests timeout

**Issue**: Model takes too long

**Solutions**:
1. Use smaller models (3B-4B)
2. Increase timeout in run_tests.sh
3. Check system resources (CPU/RAM)

### Config not loaded

**Issue**: CLI not reading .vivek/config.yml

**Solution**: Verify config exists and is valid YAML
```bash
cat python-project/.vivek/config.yml
# Check for YAML syntax errors
```

### Mode switching fails

**Issue**: CLI doesn't switch to requested mode

**Solution**: Check mode command in test input:
```bash
# Should be: "/<mode>\n<task>"
# Example: "/coder\nAdd a function..."
```

## Performance Benchmarks

**Tested with configured dual-model setup on M1 Mac:**

| Language | Mode | Avg Time | Notes |
|----------|------|----------|-------|
| Python | coder | 45s | Fast code generation |
| Python | architect | 60s | Longer thinking time |
| TypeScript | peer | 50s | Review + suggestions |
| Go | sdet | 55s | Test generation |

**Per-component timing:**
- Planner (thinking model): 10-15s
- Executor (coding model): 25-35s
- Reviewer (thinking model): 8-12s

## CLI Test Mode

### How It Works

The test runner uses CLI's test mode:

```bash
vivek chat --test-mode \
  --test-input "/<mode>
<task>" \
  --log-file test.log
```

This:
1. Loads config from `.vivek/config.yml` in current directory
2. Switches to specified mode
3. Processes task through orchestrator
4. Logs all output to file
5. Exits (non-interactive)

### Benefits

✅ **Uses real CLI** (same code path as users)
✅ **Tests config loading** (validates config system)
✅ **Repeatable** (automated, no manual input)
✅ **Logged** (all output captured for analysis)

## Next Steps

After running tests:

1. **Review logs** - Check for errors or warnings
2. **Analyze quality** - Look for consistent high-quality output
3. **Compare models** - Try different planner/executor combinations
4. **Optimize prompts** - Improve if output quality is low
5. **Benchmark** - Measure performance improvements

## Related Documentation

- [Integration Tests README](README.md) - Overview and usage
- [CLAUDE.md](../../CLAUDE.md) - Full architecture docs
- [TODO.md](../../TODO.md) - Roadmap and future work

## Version

- **Vivek Version**: 0.2.0-beta
- **Test Approach**: CLI-based with dual models
- **Models**: Qwen3-4B-Thinking (planner) + Qwen2.5-Coder-7B-MLX (executor)
- **Last Updated**: 2025-10-09
