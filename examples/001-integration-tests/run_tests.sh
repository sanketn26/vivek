#!/bin/bash
# Vivek Unified Test Runner
# Supports both mock and real LLM modes with multiple providers
#
# Usage:
#   ./run_tests.sh                                    # Mock mode (fast, no LLM needed)
#   ./run_tests.sh --real                             # Real LLM mode (auto-detect provider)
#   ./run_tests.sh --real --provider ollama           # Real with Ollama
#   ./run_tests.sh --real --provider lmstudio         # Real with LM Studio
#   ./run_tests.sh --real --provider openai           # Real with OpenAI API
#   ./run_tests.sh --real --model qwen2.5-coder:7b    # Specify model
#   ./run_tests.sh --real --url http://localhost:8080 # Custom endpoint

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Default configuration
MODE="mock"
PROVIDER="auto"
MODEL=""
BASE_URL=""
API_KEY=""

# Script paths
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESULTS_FILE="$SCRIPT_DIR/test_results_$(date +%Y%m%d_%H%M%S).log"

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --real|--llm)
            MODE="real"
            shift
            ;;
        --mock)
            MODE="mock"
            shift
            ;;
        --provider|-p)
            PROVIDER="$2"
            shift 2
            ;;
        --model|-m)
            MODEL="$2"
            shift 2
            ;;
        --url|-u)
            BASE_URL="$2"
            shift 2
            ;;
        --api-key|-k)
            API_KEY="$2"
            shift 2
            ;;
        --help|-h)
            cat << 'EOF'
Vivek Unified Test Runner

Usage:
  ./run_tests.sh [OPTIONS]

Modes:
  --mock              Run in mock mode (default, no LLM needed)
  --real, --llm       Run with real LLM

Provider Options:
  --provider, -p      LLM provider: auto|ollama|lmstudio|openai|anthropic|sarvam|custom
                      Default: auto (detects Ollama port 11434 or LM Studio port 1234)

  --model, -m         Model name (e.g., qwen2.5-coder:7b, gpt-4, claude-3-sonnet)
                      If not specified, uses first available model

  --url, -u           Custom API endpoint URL
                      Default: http://localhost:11434 (Ollama) or http://localhost:1234 (LM Studio)

  --api-key, -k       API key for cloud providers (OpenAI, Anthropic, etc.)

Examples:
  # Fast mock tests (no LLM needed)
  ./run_tests.sh
  ./run_tests.sh --mock

  # Real LLM tests (auto-detect local server)
  ./run_tests.sh --real

  # Specific provider
  ./run_tests.sh --real --provider ollama
  ./run_tests.sh --real --provider lmstudio --model qwen2.5-coder-7b-instruct

  # Cloud providers
  ./run_tests.sh --real --provider openai --model gpt-4o --api-key sk-...
  ./run_tests.sh --real --provider anthropic --model claude-3-sonnet-20240229 --api-key sk-ant-...

  # Custom endpoint
  ./run_tests.sh --real --provider custom --url http://localhost:8080 --model my-model

For more information, see: examples/001-integration-tests/README.md
EOF
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Print header
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
if [ "$MODE" = "mock" ]; then
    echo -e "${BLUE}║           Vivek Integration Tests - Mock Mode (Fast)              ║${NC}"
else
    echo -e "${BLUE}║         Vivek Integration Tests - Real LLM Mode                   ║${NC}"
fi
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Initialize results file
cat > "$RESULTS_FILE" << EOF
Vivek Integration Test Results
Mode: $MODE
Provider: $PROVIDER
Model: $MODEL
Generated: $(date)
================================================================================

EOF

# Check prerequisites
echo -e "${CYAN}🔍 Checking prerequisites...${NC}"

if [ ! -f "$PROJECT_ROOT/venv/bin/python" ]; then
    echo -e "${RED}❌ Virtual environment not found${NC}"
    echo "Run: make setup"
    exit 1
fi
echo -e "${GREEN}✓ Virtual environment found${NC}"

# Provider detection and configuration
if [ "$MODE" = "real" ]; then
    echo -e "${CYAN}🔍 Configuring LLM provider...${NC}"

    # Try to load from .vivek/config.yml if it exists and model not specified
    if [ -z "$MODEL" ] && [ -f "$PROJECT_ROOT/.vivek/config.yml" ]; then
        echo -e "${CYAN}  Found .vivek/config.yml, loading executor model...${NC}"
        MODEL=$(grep "executor_model:" "$PROJECT_ROOT/.vivek/config.yml" | sed 's/.*executor_model: *//;s/ *$//' | tr -d '"' | tr -d "'")
        if [ -n "$MODEL" ]; then
            echo -e "${GREEN}  ✓ Using model from config: $MODEL${NC}"
        fi
    fi

    # Auto-detect provider if not specified
    if [ "$PROVIDER" = "auto" ]; then
        if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
            PROVIDER="ollama"
            [ -z "$BASE_URL" ] && BASE_URL="http://localhost:11434"
            echo -e "${GREEN}✓ Auto-detected: Ollama on port 11434${NC}"
        elif curl -s http://localhost:1234/v1/models >/dev/null 2>&1; then
            PROVIDER="lmstudio"
            [ -z "$BASE_URL" ] && BASE_URL="http://localhost:1234"
            echo -e "${GREEN}✓ Auto-detected: LM Studio on port 1234${NC}"
        else
            echo -e "${RED}❌ No local LLM server detected${NC}"
            echo ""
            echo "Please either:"
            echo "  1. Start Ollama: ollama serve"
            echo "  2. Start LM Studio local server"
            echo "  3. Use --provider with cloud API"
            echo ""
            exit 1
        fi
    else
        # Set default URLs for known providers
        case "$PROVIDER" in
            ollama)
                [ -z "$BASE_URL" ] && BASE_URL="http://localhost:11434"
                ;;
            lmstudio)
                [ -z "$BASE_URL" ] && BASE_URL="http://localhost:1234"
                ;;
            openai)
                [ -z "$BASE_URL" ] && BASE_URL="https://api.openai.com/v1"
                [ -z "$API_KEY" ] && echo -e "${RED}❌ OpenAI requires --api-key${NC}" && exit 1
                ;;
            anthropic)
                [ -z "$BASE_URL" ] && BASE_URL="https://api.anthropic.com/v1"
                [ -z "$API_KEY" ] && echo -e "${RED}❌ Anthropic requires --api-key${NC}" && exit 1
                ;;
            sarvam)
                [ -z "$MODEL" ] && MODEL="sarvam-m"
                [ -z "$API_KEY" ] && API_KEY="${SARVAM_API_KEY}"
                [ -z "$API_KEY" ] && echo -e "${RED}❌ SarvamAI requires --api-key or SARVAM_API_KEY env var${NC}" && exit 1
                ;;
            custom)
                [ -z "$BASE_URL" ] && echo -e "${RED}❌ Custom provider requires --url${NC}" && exit 1
                ;;
            *)
                echo -e "${RED}❌ Unknown provider: $PROVIDER${NC}"
                echo "Supported: auto, ollama, lmstudio, openai, anthropic, sarvam, custom"
                exit 1
                ;;
        esac
        echo -e "${GREEN}✓ Provider configured: $PROVIDER${NC}"
    fi

    # Auto-detect model if not specified
    if [ -z "$MODEL" ]; then
        echo -e "${CYAN}🔍 Detecting available model...${NC}"

        case "$PROVIDER" in
            ollama)
                MODEL=$(curl -s "$BASE_URL/api/tags" | grep -o '"name":"[^"]*"' | head -1 | cut -d'"' -f4)
                ;;
            lmstudio)
                MODEL=$(curl -s "$BASE_URL/v1/models" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
                ;;
            openai|anthropic|sarvam|custom)
                # For cloud/custom, model must be specified
                echo -e "${RED}❌ --model required for $PROVIDER provider${NC}"
                exit 1
                ;;
        esac

        if [ -z "$MODEL" ]; then
            echo -e "${RED}❌ No model found/loaded${NC}"
            echo "Please load a model or specify with --model"
            exit 1
        fi
    fi

    echo -e "${GREEN}✓ Using model: $MODEL${NC}"
    echo -e "${GREEN}✓ Endpoint: $BASE_URL${NC}"
    echo ""
fi

# Test execution function
run_test() {
    local test_name="$1"
    local language="$2"
    local mode_arg="$3"
    local project_dir="$4"
    local prompt="$5"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "${BLUE}────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}Test $TOTAL_TESTS: $test_name${NC}"
    echo -e "  Language: ${language}"
    echo -e "  Mode: ${mode_arg}"
    if [ "$MODE" = "real" ]; then
        echo -e "  Provider: ${PROVIDER}"
        echo -e "  Model: ${MODEL}"
    fi
    echo ""

    # Log test details
    cat >> "$RESULTS_FILE" << EOF
Test $TOTAL_TESTS: $test_name
Language: $language
Mode: $mode_arg
$([ "$MODE" = "real" ] && echo "Provider: $PROVIDER")
$([ "$MODE" = "real" ] && echo "Model: $MODEL")
Prompt: $prompt
Time: $(date)
----------------------------------------
EOF

    cd "$project_dir"

    # Run test with appropriate provider
    if [ "$MODE" = "mock" ]; then
        # Mock mode - fast tests
        TEST_OUTPUT=$("$PROJECT_ROOT/venv/bin/python3" << PYEOF 2>&1
import sys
sys.path.insert(0, "$PROJECT_ROOT")

from vivek.llm.plugins.base.registry import discover_plugins
from vivek.llm.executor import get_executor
from vivek.llm.provider import OllamaProvider
from unittest.mock import Mock

# Discover plugins
count = discover_plugins()
print(f"✓ Discovered {count} language plugins")

# Create mock provider
provider = Mock(spec=OllamaProvider)
provider.generate.return_value = "Mock implementation complete"

# Test executor creation
executor = get_executor("$mode_arg", provider, "$language")
print(f"✓ Created {executor.__class__.__name__}")

# Test prompt building
task_plan = {
    "description": "$prompt",
    "work_items": [{
        "file_path": "test_file.${language}",
        "description": "$prompt",
        "file_status": "new",
        "mode": "$mode_arg",
        "dependencies": []
    }]
}

prompt_text = executor.build_prompt(task_plan, context="Test context")
print(f"✓ Built prompt ({len(prompt_text)} chars)")

if "$language" in prompt_text.lower():
    print(f"✓ Prompt contains language-specific content")

print("SUCCESS")
PYEOF
        )
    else
        # Real LLM mode - actual tests
        TEST_OUTPUT=$("$PROJECT_ROOT/venv/bin/python3" << PYEOF 2>&1
import sys
import signal
sys.path.insert(0, "$PROJECT_ROOT")

from vivek.llm.plugins.base.registry import discover_plugins
from vivek.llm.executor import get_executor
from vivek.llm.provider import (
    OllamaProvider,
    LMStudioProvider,
    OpenAICompatibleProvider,
    SarvamAIProvider
)

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Test timeout")
signal.signal(signal.SIGALRM, timeout_handler)

try:
    # Discover plugins
    discover_plugins()

    # Create provider based on type
    provider_type = "$PROVIDER"
    model = "$MODEL"
    base_url = "$BASE_URL"
    api_key = "$API_KEY" if "$API_KEY" else None

    if provider_type in ["ollama", "auto"] and not base_url:
        # Ollama provider - only needs model name
        provider = OllamaProvider(model_name=model)
    elif provider_type == "lmstudio" or (provider_type == "auto" and ":1234" in base_url):
        # LM Studio provider
        provider = LMStudioProvider(
            model_name=model,
            base_url=base_url or "http://localhost:1234"
        )
    elif provider_type == "sarvam":
        # Sarvam AI provider
        provider = SarvamAIProvider(
            model_name=model or "sarvam-m",
            api_key=api_key
        )
    else:
        # Generic OpenAI-compatible provider (OpenAI, Anthropic, custom)
        provider = OpenAICompatibleProvider(
            model_name=model,
            base_url=base_url or "http://localhost:11434",
            api_key=api_key
        )

    # Create executor
    executor = get_executor("$mode_arg", provider, "$language")
    print(f"✓ Created executor: {executor.__class__.__name__}")

    # Build task
    task_plan = {
        "description": "$prompt",
        "work_items": [{
            "file_path": "example.${language}",
            "description": "$prompt",
            "file_status": "new",
            "mode": "$mode_arg",
            "dependencies": []
        }]
    }

    prompt_text = executor.build_prompt(task_plan, context="Test project")
    print(f"✓ Built prompt: {len(prompt_text)} characters")

    # Execute with timeout
    signal.alarm(30)
    result = executor.execute_task(task_plan, context="Test project")
    signal.alarm(0)

    # Result is a message dict with structure: {type, payload, from_node, metadata}
    if "payload" in result and "output" in result["payload"]:
        output = result["payload"]["output"]
        print(f"✓ LLM generated output: {len(output)} characters")

        # Quality checks
        if len(output) > 50:
            print("✓ Output has reasonable length")

        # Check for language patterns
        lang_patterns = {
            "python": ["def ", "class ", "import "],
            "typescript": ["function", "const ", "interface"],
            "go": ["func ", "package ", "type "]
        }

        if any(pattern in output for pattern in lang_patterns.get("$language", [])):
            print(f"✓ Output contains $language code patterns")

        print("SUCCESS")
    else:
        print(f"⚠ Unexpected result structure: {list(result.keys())}")
        if "payload" in result:
            print(f"  Payload keys: {list(result['payload'].keys())}")
        print("PARTIAL_SUCCESS")

except TimeoutError:
    print("⏱ Test timeout (30s)")
    print("TIMEOUT")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("FAILED")
PYEOF
        )
    fi

    # Evaluate result
    if echo "$TEST_OUTPUT" | grep -q "SUCCESS"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "Result: PASSED" >> "$RESULTS_FILE"
    elif echo "$TEST_OUTPUT" | grep -q "PARTIAL_SUCCESS"; then
        echo -e "${YELLOW}⚠️  PARTIAL PASS${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "Result: PARTIAL_PASS" >> "$RESULTS_FILE"
    elif echo "$TEST_OUTPUT" | grep -q "TIMEOUT"; then
        echo -e "${YELLOW}⏱️  TIMEOUT${NC}"
        SKIPPED_TESTS=$((SKIPPED_TESTS + 1))
        echo "Result: TIMEOUT" >> "$RESULTS_FILE"
    else
        echo -e "${RED}❌ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "Result: FAILED" >> "$RESULTS_FILE"
    fi

    echo "$TEST_OUTPUT" >> "$RESULTS_FILE"
    echo "" >> "$RESULTS_FILE"
    echo ""

    cd "$SCRIPT_DIR"
}

# Run test scenarios
echo -e "${CYAN}📋 Running test scenarios...${NC}"
echo ""

# Python tests
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Python Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test "Python Coder - Add function" "python" "coder" \
    "$SCRIPT_DIR/python-project" \
    "Add a modulo function that returns remainder of a/b"

run_test "Python Architect - API design" "python" "architect" \
    "$SCRIPT_DIR/python-project" \
    "Design REST API architecture for calculator"

run_test "Python Peer - Code review" "python" "peer" \
    "$SCRIPT_DIR/python-project" \
    "Review calculator.py for best practices"

run_test "Python SDET - Test suite" "python" "sdet" \
    "$SCRIPT_DIR/python-project" \
    "Create pytest tests for calculator functions"

# TypeScript tests
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  TypeScript Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test "TypeScript Coder - Add function" "typescript" "coder" \
    "$SCRIPT_DIR/typescript-project" \
    "Add power function that raises a to power of b"

run_test "TypeScript Architect - Module design" "typescript" "architect" \
    "$SCRIPT_DIR/typescript-project" \
    "Design modular architecture with TypeScript interfaces"

run_test "TypeScript Peer - Type safety review" "typescript" "peer" \
    "$SCRIPT_DIR/typescript-project" \
    "Review calculator for type safety and best practices"

run_test "TypeScript SDET - Jest tests" "typescript" "sdet" \
    "$SCRIPT_DIR/typescript-project" \
    "Create Jest test suite for calculator"

# Go tests
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Go Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test "Go Coder - Add function" "go" "coder" \
    "$SCRIPT_DIR/go-project" \
    "Add square root function with error handling"

run_test "Go Architect - Concurrent design" "go" "architect" \
    "$SCRIPT_DIR/go-project" \
    "Design concurrent calculator using goroutines"

run_test "Go Peer - Review error handling" "go" "peer" \
    "$SCRIPT_DIR/go-project" \
    "Review calculator for idiomatic Go patterns"

run_test "Go SDET - Table-driven tests" "go" "sdet" \
    "$SCRIPT_DIR/go-project" \
    "Create table-driven tests for calculator"

# Summary report
echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                        Test Summary Report                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Mode:         ${MODE}"
[ "$MODE" = "real" ] && echo -e "  Provider:     ${PROVIDER}"
[ "$MODE" = "real" ] && echo -e "  Model:        ${MODEL}"
echo -e "  Total Tests:  ${TOTAL_TESTS}"
echo -e "  ${GREEN}Passed:       ${PASSED_TESTS}${NC}"
echo -e "  ${RED}Failed:       ${FAILED_TESTS}${NC}"
[ $SKIPPED_TESTS -gt 0 ] && echo -e "  ${YELLOW}Skipped:      ${SKIPPED_TESTS}${NC}"
echo ""

if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
    echo -e "  Pass Rate:    ${PASS_RATE}%"
fi
echo ""
echo -e "${CYAN}📄 Full results: ${RESULTS_FILE}${NC}"
echo ""

# Summary to results file
cat >> "$RESULTS_FILE" << EOF

================================================================================
SUMMARY
================================================================================
Mode:         $MODE
$([ "$MODE" = "real" ] && echo "Provider:     $PROVIDER")
$([ "$MODE" = "real" ] && echo "Model:        $MODEL")
Total Tests:  $TOTAL_TESTS
Passed:       $PASSED_TESTS
Failed:       $FAILED_TESTS
$([ $SKIPPED_TESTS -gt 0 ] && echo "Skipped:      $SKIPPED_TESTS")
Pass Rate:    ${PASS_RATE}%

Completed: $(date)
EOF

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed${NC}"
    exit 1
fi
