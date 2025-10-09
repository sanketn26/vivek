#!/bin/bash
################################################################################
# Vivek Integration Test Suite Runner
#
# Tests all language × mode combinations using Vivek CLI
# Reads config from each project's .vivek/config.yml
#
# Usage:
#   ./run_tests.sh          # Mock mode (fast, no LLM)
#   ./run_tests.sh --real   # Real LLM mode (uses LM Studio with configured models)
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VIVEK_CLI="$PROJECT_ROOT/venv/bin/vivek"
LOG_DIR="$SCRIPT_DIR/test_logs"
RESULTS_FILE="$SCRIPT_DIR/test_results.log"

# Test mode
MODE="mock"
if [[ "$1" == "--real" ]]; then
    MODE="real"
fi

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Create log directory
mkdir -p "$LOG_DIR"
> "$RESULTS_FILE"

################################################################################
# Header
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
if [[ "$MODE" == "mock" ]]; then
    echo -e "${BLUE}║         Vivek Integration Tests - Mock Mode (Fast)                ║${NC}"
else
    echo -e "${BLUE}║         Vivek Integration Tests - Real LLM Mode                   ║${NC}"
fi
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Mode:         ${YELLOW}${MODE}${NC}"
echo -e "Log Dir:      ${LOG_DIR}"
echo -e "Results:      ${RESULTS_FILE}"
echo ""

# Check Vivek CLI
if [[ ! -f "$VIVEK_CLI" ]]; then
    echo -e "${RED}❌ Vivek CLI not found at $VIVEK_CLI${NC}"
    echo "Run: make setup"
    exit 1
fi
echo -e "${GREEN}✓ Vivek CLI found${NC}"

# Check LM Studio for real mode
if [[ "$MODE" == "real" ]]; then
    echo -e "${CYAN}🔍 Checking LM Studio...${NC}"
    if curl -s http://localhost:1234/v1/models >/dev/null 2>&1; then
        echo -e "${GREEN}✓ LM Studio detected${NC}"
        echo ""
        echo -e "${CYAN}Expected models:${NC}"
        echo -e "  Planner:  qwen/qwen3-4b-thinking-2507"
        echo -e "  Executor: qwen2.5-coder-7b-instruct-mlx"
        echo ""
    else
        echo -e "${RED}❌ LM Studio not running on port 1234${NC}"
        echo "Please start LM Studio and load the models above."
        exit 1
    fi
fi

################################################################################
# Test Execution Function
################################################################################

run_test() {
    local language=$1
    local mode=$2
    local task=$3
    local test_name="${language}-${mode}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "${BLUE}────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}Test ${TOTAL_TESTS}: ${language} × ${mode}${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────${NC}"
    echo "Task: $task"
    echo ""

    local project_dir="$SCRIPT_DIR/${language}-project"
    local log_file="$LOG_DIR/${test_name}_$(date +%Y%m%d_%H%M%S).log"

    # Initialize log
    {
        echo "========================================"
        echo "TEST: ${test_name}"
        echo "Started: $(date)"
        echo "========================================"
        echo "Language: $language"
        echo "Mode: $mode"
        echo "Task: $task"
        echo "Project: $project_dir"
        echo "========================================"
        echo ""
    } > "$log_file"

    cd "$project_dir"

    if [[ "$MODE" == "mock" ]]; then
        # Mock mode: just verify CLI can load config and run
        echo "Running mock test..."

        if "$VIVEK_CLI" chat --test-mode --test-input "/$mode
$task" --log-file "$log_file" 2>&1 | tee -a "$log_file"; then
            echo -e "${GREEN}✅ PASSED${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            echo "RESULT: PASSED" >> "$log_file"
        else
            echo -e "${RED}❌ FAILED${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo "RESULT: FAILED" >> "$log_file"
        fi

    else
        # Real LLM mode: full orchestration with configured models
        echo "Running with real LLM (config from .vivek/config.yml)..."

        # CLI will:
        # 1. Load config from .vivek/config.yml
        # 2. Use qwen3-4b-thinking for planner
        # 3. Use qwen2.5-coder-mlx for executor
        # 4. Run full orchestration flow

        if "$VIVEK_CLI" chat --test-mode --test-input "/$mode
$task" --log-file "$log_file" 2>&1 | tee -a "$log_file"; then
            echo -e "${GREEN}✅ PASSED${NC}"
            PASSED_TESTS=$((PASSED_TESTS + 1))
            echo "RESULT: PASSED" >> "$log_file"
        else
            echo -e "${RED}❌ FAILED${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo "RESULT: FAILED" >> "$log_file"
        fi
    fi

    # Log result
    {
        echo ""
        echo "Test: ${test_name}"
        echo "Status: $(grep "RESULT:" "$log_file" | tail -1)"
        echo "Log: $log_file"
        echo "---"
    } >> "$RESULTS_FILE"

    echo ""
    cd "$SCRIPT_DIR"
}

################################################################################
# Test Cases
################################################################################

echo -e "${CYAN}📋 Running test suite...${NC}"
echo ""

# Python Tests
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Python Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test "python" "coder" "Add a modulo function to calculate remainder of a/b with zero division handling"
run_test "python" "architect" "Design a REST API architecture for this calculator service"
run_test "python" "peer" "Review the calculator code for best practices and suggest improvements"
run_test "python" "sdet" "Create comprehensive pytest test suite for all calculator functions"

# TypeScript Tests
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  TypeScript Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test "typescript" "coder" "Add a power function to calculate base to the power of exponent"
run_test "typescript" "architect" "Design modular calculator architecture with proper TypeScript interfaces"
run_test "typescript" "peer" "Review TypeScript code for type safety and best practices"
run_test "typescript" "sdet" "Create Jest test suite with 100% code coverage for calculator"

# Go Tests
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Go Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test "go" "coder" "Add square root function with proper error handling for negative numbers"
run_test "go" "architect" "Design concurrent calculator service using goroutines and channels"
run_test "go" "peer" "Review Go code for idiomatic patterns and error handling"
run_test "go" "sdet" "Create table-driven tests for all calculator operations"

################################################################################
# Summary Report
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                        Test Summary Report                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo "  Mode:         ${MODE}"
echo "  Total Tests:  ${TOTAL_TESTS}"
echo -e "  ${GREEN}Passed:       ${PASSED_TESTS}${NC}"
echo -e "  ${RED}Failed:       ${FAILED_TESTS}${NC}"

if [[ $TOTAL_TESTS -gt 0 ]]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "  Pass Rate:    ${PASS_RATE}%"
fi

echo ""
echo -e "${CYAN}📄 Full results: ${RESULTS_FILE}${NC}"
echo -e "${CYAN}📁 Test logs: ${LOG_DIR}${NC}"
echo ""

if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}🎉 All tests passed! Ready for beta release.${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Review logs for details.${NC}"
    exit 1
fi
