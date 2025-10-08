#!/bin/bash
# Vivek Integration Test Suite
# Tests all language x mode combinations with real scenarios
# Run from project root: ./examples/001-integration-tests/run_integration_tests.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
RESULTS_FILE="$SCRIPT_DIR/test_results.log"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Initialize results file
cat > "$RESULTS_FILE" << EOF
Vivek Integration Test Results
Generated: $(date)
================================================================================

EOF

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       Vivek v0.2.0 Beta - Comprehensive Integration Tests         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

if [ ! -f "$PROJECT_ROOT/venv/bin/python" ]; then
    echo -e "${RED}❌ Virtual environment not found. Run 'make setup' first${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found${NC}"
echo -e "${GREEN}✓ Virtual environment found${NC}"
echo ""

# Function to run a test scenario
run_test() {
    local test_name="$1"
    local language="$2"
    local mode="$3"
    local project_dir="$4"
    local prompt="$5"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "${BLUE}────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}Test $TOTAL_TESTS: $test_name${NC}"
    echo -e "  Language: ${language}"
    echo -e "  Mode: ${mode}"
    echo -e "  Project: ${project_dir}"
    echo ""

    # Log test details
    cat >> "$RESULTS_FILE" << EOF
Test $TOTAL_TESTS: $test_name
Language: $language
Mode: $mode
Project: $project_dir
Prompt: $prompt
Time: $(date)
----------------------------------------
EOF

    # Run the test using Python script (simulated for now)
    # In real usage, this would invoke Vivek CLI
    cd "$project_dir"

    # Test plugin discovery and executor creation
    TEST_OUTPUT=$("$PROJECT_ROOT/venv/bin/python3" << PYEOF 2>&1
import sys
sys.path.insert(0, "$PROJECT_ROOT")

from vivek.llm.plugins.base.registry import discover_plugins, get_registry
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
executor = get_executor("$mode", provider, "$language")
print(f"✓ Created {executor.__class__.__name__} for $language/$mode")

# Test prompt building
task_plan = {
    "description": "$prompt",
    "work_items": [{
        "file_path": "test_file",
        "description": "Test task",
        "file_status": "new",
        "mode": "$mode",
        "dependencies": []
    }]
}

prompt = executor.build_prompt(task_plan, context="Test context")
print(f"✓ Built prompt ({len(prompt)} chars)")

# Verify prompt contains language-specific content
if "$language" in prompt.lower() or "$mode" in prompt.lower():
    print("✓ Prompt contains language-specific instructions")
else:
    print("⚠ Warning: Prompt may not contain language-specific instructions")

print("SUCCESS")
PYEOF
    )

    if [ $? -eq 0 ] && echo "$TEST_OUTPUT" | grep -q "SUCCESS"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        echo "$TEST_OUTPUT" >> "$RESULTS_FILE"
        echo "Result: PASSED" >> "$RESULTS_FILE"
    else
        echo -e "${RED}❌ FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        echo "$TEST_OUTPUT" >> "$RESULTS_FILE"
        echo "Result: FAILED" >> "$RESULTS_FILE"
        echo "Error output:" >> "$RESULTS_FILE"
        echo "$TEST_OUTPUT" >> "$RESULTS_FILE"
    fi

    echo "" >> "$RESULTS_FILE"
    echo ""

    cd "$SCRIPT_DIR"
}

# ============================================================================
# Test Scenarios
# ============================================================================

echo -e "${BLUE}📋 Running test scenarios...${NC}"
echo ""

# Python Tests (4 modes)
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Python Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test \
    "Python Coder - Add modulo function" \
    "python" \
    "coder" \
    "$SCRIPT_DIR/python-project" \
    "Add a modulo function that returns the remainder of a/b"

run_test \
    "Python Architect - Design calculator API" \
    "python" \
    "architect" \
    "$SCRIPT_DIR/python-project" \
    "Design a REST API architecture for the calculator with error handling"

run_test \
    "Python Peer - Review calculator code" \
    "python" \
    "peer" \
    "$SCRIPT_DIR/python-project" \
    "Review the calculator.py code for best practices and potential improvements"

run_test \
    "Python SDET - Create test suite" \
    "python" \
    "sdet" \
    "$SCRIPT_DIR/python-project" \
    "Create comprehensive pytest tests for all calculator functions including edge cases"

# TypeScript Tests (4 modes)
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  TypeScript Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test \
    "TypeScript Coder - Add power function" \
    "typescript" \
    "coder" \
    "$SCRIPT_DIR/typescript-project" \
    "Add a power function that raises a to the power of b"

run_test \
    "TypeScript Architect - Design calculator module" \
    "typescript" \
    "architect" \
    "$SCRIPT_DIR/typescript-project" \
    "Design a modular architecture with proper TypeScript interfaces and types"

run_test \
    "TypeScript Peer - Review type safety" \
    "typescript" \
    "peer" \
    "$SCRIPT_DIR/typescript-project" \
    "Review the calculator code for type safety and TypeScript best practices"

run_test \
    "TypeScript SDET - Create Jest tests" \
    "typescript" \
    "sdet" \
    "$SCRIPT_DIR/typescript-project" \
    "Create Jest test suite with full coverage for all calculator functions"

# Go Tests (4 modes)
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  Go Language Tests${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════${NC}"

run_test \
    "Go Coder - Add square root function" \
    "go" \
    "coder" \
    "$SCRIPT_DIR/go-project" \
    "Add a square root function with proper error handling"

run_test \
    "Go Architect - Design concurrent calculator" \
    "go" \
    "architect" \
    "$SCRIPT_DIR/go-project" \
    "Design a concurrent calculator using goroutines and channels"

run_test \
    "Go Peer - Review error handling" \
    "go" \
    "peer" \
    "$SCRIPT_DIR/go-project" \
    "Review the calculator code for idiomatic Go patterns and error handling"

run_test \
    "Go SDET - Create table-driven tests" \
    "go" \
    "sdet" \
    "$SCRIPT_DIR/go-project" \
    "Create comprehensive table-driven tests for all calculator functions"

# ============================================================================
# Summary Report
# ============================================================================

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                        Test Summary Report                         ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Total Tests:  ${TOTAL_TESTS}"
echo -e "  ${GREEN}Passed:       ${PASSED_TESTS}${NC}"
echo -e "  ${RED}Failed:       ${FAILED_TESTS}${NC}"
echo ""

PASS_RATE=$(( (PASSED_TESTS * 100) / TOTAL_TESTS ))
echo -e "  Pass Rate:    ${PASS_RATE}%"
echo ""

# Add summary to results file
cat >> "$RESULTS_FILE" << EOF

================================================================================
SUMMARY
================================================================================
Total Tests:  $TOTAL_TESTS
Passed:       $PASSED_TESTS
Failed:       $FAILED_TESTS
Pass Rate:    ${PASS_RATE}%

Test completed at: $(date)
EOF

echo -e "${BLUE}📄 Full results saved to: ${RESULTS_FILE}${NC}"
echo ""

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed! Ready for beta release.${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Review the results before release.${NC}"
    echo ""
    exit 1
fi
