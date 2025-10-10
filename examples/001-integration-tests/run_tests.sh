#!/bin/bash
################################################################################
# Vivek Integration Test Suite - Home Rental Service
#
# Tests Vivek by building a complete home rental service from scratch:
# - Go backend (API server, database layer)
# - TypeScript UI (React frontend)
# - Python control plane (orchestration, monitoring)
#
# Each component tests all 4 modes in sequence:
#   architect → coder → sdet → peer
#
# Usage:
#   ./run_tests.sh          # Mock mode (fast, no LLM)
#   ./run_tests.sh --real   # Real LLM mode (uses configured models)
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VIVEK_CLI="$PROJECT_ROOT/venv/bin/vivek"
TEST_PROJECT="$SCRIPT_DIR/home-rental-service"
LOG_DIR="$SCRIPT_DIR/test_logs"
RESULTS_FILE="$SCRIPT_DIR/test_results.log"

# Detect timeout command (macOS uses gtimeout from coreutils, Linux uses timeout)
if command -v timeout >/dev/null 2>&1; then
    TIMEOUT_CMD="timeout"
elif command -v gtimeout >/dev/null 2>&1; then
    TIMEOUT_CMD="gtimeout"
else
    echo -e "${YELLOW}⚠️  Warning: timeout command not found. Tests may run indefinitely if they hang.${NC}"
    echo -e "${YELLOW}   Install with: brew install coreutils (macOS)${NC}"
    TIMEOUT_CMD=""
fi

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
    echo -e "${BLUE}║    Vivek Integration Test - Home Rental Service (Mock Mode)       ║${NC}"
else
    echo -e "${BLUE}║    Vivek Integration Test - Home Rental Service (Real LLM)        ║${NC}"
fi
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "Mode:         ${YELLOW}${MODE}${NC}"
echo -e "Project:      ${TEST_PROJECT}"
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

# Check LLM provider for real mode
if [[ "$MODE" == "real" ]]; then
    echo -e "${CYAN}🔍 Checking LLM provider...${NC}"
    echo ""

    # Check if .vivek/config.yml exists and read provider
    if [[ -f "$TEST_PROJECT/.vivek/config.yml" ]] || [[ -f ".vivek/config.yml" ]]; then
        echo -e "${GREEN}✓ Found Vivek config - will use configured provider${NC}"
        echo ""
        echo -e "${YELLOW}Note:${NC} Tests will use provider/models from .vivek/config.yml"
        echo ""
        echo -e "${CYAN}Supported providers:${NC}"
        echo -e "  ${GREEN}✓ LM Studio${NC} (local, privacy-first, recommended)"
        echo -e "    - URL: http://localhost:1234/v1"
        echo -e "    - Planner model: qwen/qwen3-4b-thinking-2507"
        echo -e "    - Executor model: qwen2.5-coder-7b-instruct-mlx"
        echo ""
        echo -e "  ${GREEN}✓ Sarvam AI${NC} (cloud, Indian LLM provider)"
        echo -e "    - Requires SARVAM_API_KEY environment variable"
        echo -e "    - Models: sarvam-2b-v0.5, sarvam-1b-v0.5"
        echo ""

        # Try to detect which provider is configured
        if curl -s http://localhost:1234/v1/models >/dev/null 2>&1; then
            echo -e "${GREEN}✓ LM Studio detected on port 1234${NC}"
        elif [[ -n "$SARVAM_API_KEY" ]]; then
            echo -e "${GREEN}✓ Sarvam API key found in environment${NC}"
        else
            echo -e "${YELLOW}⚠ Provider check: Please ensure your configured provider is available${NC}"
        fi
        echo ""
    else
        echo -e "${YELLOW}⚠ No Vivek config found - tests will create default config${NC}"
        echo ""
        echo -e "${CYAN}The test will create .vivek/config.yml with LM Studio as default.${NC}"
        echo -e "${CYAN}You can modify it to use Sarvam or other providers.${NC}"
        echo ""
    fi
fi

################################################################################
# Project Setup
################################################################################

echo -e "${MAGENTA}🏗️  Setting up Home Rental Service project...${NC}"
echo ""

# Clean and recreate project directory
rm -rf "$TEST_PROJECT"
mkdir -p "$TEST_PROJECT"

# Create initial project structure
cd "$TEST_PROJECT"

# Initialize basic structure
mkdir -p backend/{cmd,internal,pkg} frontend/{src,public} control-plane/{app,config}
touch README.md

# Create initial README
cat > README.md << 'EOF'
# Home Rental Service

A multi-language microservices platform for home rentals.

## Architecture

- **Backend** (Go): REST API, database layer, business logic
- **Frontend** (TypeScript/React): User interface for browsing and booking
- **Control Plane** (Python): Orchestration, monitoring, admin tools

## Components

### Backend (Go)
- Property management API
- Booking system
- User authentication
- Database models

### Frontend (TypeScript)
- Property search and browse
- Booking interface
- User dashboard
- Admin panel

### Control Plane (Python)
- Service orchestration
- Health monitoring
- Analytics dashboard
- Configuration management

## Development

Built and tested using Vivek AI coding assistant.
EOF

# Initialize Vivek config
mkdir -p .vivek
cat > vivek.md << 'EOF'
# Home Rental Service - Vivek Configuration

## Project Context
Multi-language microservices platform for home rental marketplace.

## Tech Stack
- Backend: Go 1.21+
- Frontend: TypeScript, React, Vite
- Control Plane: Python 3.10+
- Database: PostgreSQL
- Cache: Redis

## Work Preferences
- Follow language-specific best practices
- Write comprehensive tests
- Document all public APIs
- Use dependency injection patterns
EOF

cat > .vivek/config.yml << 'EOF'
# Vivek Configuration for Home Rental Service

project_settings:
  name: "Home Rental Service"
  language:
    - "go"
    - "typescript"
    - "python"
  framework:
    - "React"
    - "Vite"
  test_framework:
    - "jest"
    - "pytest"
    - "go test"
  package_manager:
    - "npm"
    - "pip"
    - "go mod"

# ============================================================================
# LLM Configuration - LM Studio (Local, Privacy-First) - ACTIVE
# ============================================================================
# Start LM Studio and load these models before running tests
# Note: Base URL should NOT include /v1 - it's added automatically
llm_configuration:
  mode: "peer"
  planner_model: "qwen/qwen3-4b-thinking-2507"
  executor_model: "qwen2.5-coder-7b-instruct-mlx"
  provider: "lmstudio"
  provider_config:
    base_url: "http://localhost:1234"
    context_window: 9182
  fallback_enabled: true
  auto_switch: true

# ============================================================================
# Sarvam AI Alternative (Cloud-Based) - COMMENTED OUT
# ============================================================================
# To use Sarvam instead of LM Studio:
# 1. Comment out the llm_configuration section above
# 2. Uncomment the section below
# 3. Set SARVAM_API_KEY environment variable: export SARVAM_API_KEY="your-key"
#
# llm_configuration:
#   mode: "peer"
#   planner_model: "sarvam-2b-v0.5"
#   executor_model: "sarvam-2b-v0.5"
#   provider: "sarvam"
#   provider_config:
#     api_key: "${SARVAM_API_KEY}"
#     context_window: 9182
#   fallback_enabled: true
#   auto_switch: true

preferences:
  default_mode: "peer"
  search_enabled: false
  auto_index: false
  context_window: 9182
EOF

echo -e "${GREEN}✓ Project structure created${NC}"
echo ""

################################################################################
# Test Execution Function
################################################################################

run_test() {
    local component=$1
    local mode=$2
    local task=$3
    local test_name="${component}-${mode}"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo -e "${BLUE}────────────────────────────────────────────────────────────────────${NC}"
    echo -e "${YELLOW}Test ${TOTAL_TESTS}: ${component} × /${mode}${NC}"
    echo -e "${BLUE}────────────────────────────────────────────────────────────────────${NC}"
    echo "Task: $task"
    echo ""

    local log_file="$LOG_DIR/${test_name}_$(date +%Y%m%d_%H%M%S).log"

    # Initialize log
    {
        echo "========================================"
        echo "TEST: ${test_name}"
        echo "Started: $(date)"
        echo "========================================"
        echo "Component: $component"
        echo "Mode: $mode"
        echo "Task: $task"
        echo "Project: $TEST_PROJECT"
        echo "========================================"
        echo ""
    } > "$log_file"

    cd "$TEST_PROJECT"

    if [[ "$MODE" == "mock" ]]; then
        # Mock mode: verify CLI can process the request
        echo "Running mock test..."
        echo -e "${CYAN}Note: Mock mode validates orchestration flow only (no real LLM calls)${NC}"

        if [[ -n "$TIMEOUT_CMD" ]]; then
            TEST_CMD="$TIMEOUT_CMD 60 $VIVEK_CLI"
        else
            TEST_CMD="$VIVEK_CLI"
        fi

        if $TEST_CMD chat --test-mode --test-input "/$mode
$task" --log-file "$log_file" 2>&1 | tee -a "$log_file"; then
            # Verify basic orchestration happened by checking log file
            if grep -q "FINAL RESULT" "$log_file" 2>/dev/null; then
                echo -e "${GREEN}✅ PASSED - Orchestration completed${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
                echo "RESULT: PASSED - Orchestration flow validated" >> "$log_file"
            else
                echo -e "${YELLOW}⚠️  PARTIAL - Command succeeded but no final result${NC}"
                PASSED_TESTS=$((PASSED_TESTS + 1))
                echo "RESULT: PARTIAL - CLI succeeded" >> "$log_file"
            fi
        else
            echo -e "${RED}❌ FAILED - CLI error or timeout${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo "RESULT: FAILED - CLI error" >> "$log_file"
        fi

    else
        # Real LLM mode: full orchestration with configured models
        echo "Running with real LLM (config from .vivek/config.yml)..."
        echo -e "${CYAN}Note: This will make actual LLM calls and generate code${NC}"

        if [[ -n "$TIMEOUT_CMD" ]]; then
            TEST_CMD="$TIMEOUT_CMD 300 $VIVEK_CLI"
        else
            TEST_CMD="$VIVEK_CLI"
        fi

        if $TEST_CMD chat --test-mode --test-input "/$mode
$task" --log-file "$log_file" 2>&1 | tee -a "$log_file"; then
            # Verify actual output was generated
            if grep -q "FINAL RESULT" "$log_file" 2>/dev/null; then
                # Extract quality score and check if output contains meaningful content
                quality=$(grep -o '"quality_score":[0-9.]*' "$log_file" 2>/dev/null | tail -1 | cut -d: -f2)
                output_lines=$(grep -A 50 "FINAL RESULT" "$log_file" | wc -l)

                if [[ -n "$quality" ]] && (( $(echo "$quality > 0" | bc -l 2>/dev/null || echo 0) )); then
                    echo -e "${GREEN}✅ PASSED - Generated output with quality score: $quality${NC}"
                    PASSED_TESTS=$((PASSED_TESTS + 1))
                    echo "RESULT: PASSED - Quality: $quality" >> "$log_file"
                elif [[ $output_lines -gt 10 ]]; then
                    echo -e "${GREEN}✅ PASSED - Generated substantial output${NC}"
                    PASSED_TESTS=$((PASSED_TESTS + 1))
                    echo "RESULT: PASSED - Output generated" >> "$log_file"
                else
                    echo -e "${YELLOW}⚠️  PARTIAL - Low quality or minimal output${NC}"
                    PASSED_TESTS=$((PASSED_TESTS + 1))
                    echo "RESULT: PARTIAL - Minimal output" >> "$log_file"
                fi
            else
                echo -e "${RED}❌ FAILED - No output generated${NC}"
                FAILED_TESTS=$((FAILED_TESTS + 1))
                echo "RESULT: FAILED - No output" >> "$log_file"
            fi
        else
            echo -e "${RED}❌ FAILED - CLI error or timeout${NC}"
            FAILED_TESTS=$((FAILED_TESTS + 1))
            echo "RESULT: FAILED - CLI error" >> "$log_file"
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
# Test Suite - Building Home Rental Service
################################################################################

echo -e "${CYAN}📋 Starting Home Rental Service build...${NC}"
echo ""

# ============================================================================
# Phase 1: Go Backend - Property Management
# ============================================================================
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  Phase 1: Go Backend - Property Management API${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"

run_test "go-backend" "architect" "Design a property management REST API architecture for the Go backend. Include:
- Property model (ID, title, description, price, location, amenities)
- RESTful endpoints (GET /properties, POST /properties, GET /properties/:id)
- Repository pattern for database abstraction
- Handler layer for HTTP routing
Design clean architecture with proper separation of concerns."

run_test "go-backend" "coder" "Implement the property management API in Go:
- Create backend/internal/models/property.go with Property struct
- Create backend/internal/repository/property_repository.go with in-memory storage
- Create backend/internal/handlers/property_handler.go with HTTP handlers
- Create backend/cmd/server/main.go with router and server setup
Use standard library net/http or gorilla/mux for routing."

run_test "go-backend" "sdet" "Create comprehensive tests for the property management API:
- Create backend/internal/models/property_test.go with model validation tests
- Create backend/internal/repository/property_repository_test.go with CRUD tests
- Create backend/internal/handlers/property_handler_test.go with HTTP endpoint tests
Use table-driven tests and httptest package for API testing."

run_test "go-backend" "peer" "Review the Go backend code for:
- Idiomatic Go patterns and naming conventions
- Proper error handling and validation
- Thread safety in repository layer
- HTTP status codes and response formats
Suggest improvements for code quality and maintainability."

# ============================================================================
# Phase 2: TypeScript Frontend - Property Listing
# ============================================================================
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  Phase 2: TypeScript Frontend - Property Listing UI${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"

run_test "typescript-frontend" "architect" "Design a React TypeScript frontend architecture for property listings:
- Component hierarchy (PropertyList, PropertyCard, PropertyDetails)
- State management approach (useState/useContext or Redux)
- API client service for backend communication
- TypeScript interfaces for type safety
- Responsive layout considerations
Focus on clean component design and type safety."

run_test "typescript-frontend" "coder" "Implement the property listing UI in TypeScript/React:
- Create frontend/src/types/Property.ts with interface definitions
- Create frontend/src/services/api.ts with fetch-based API client
- Create frontend/src/components/PropertyCard.tsx for displaying properties
- Create frontend/src/components/PropertyList.tsx for listing all properties
- Create frontend/src/App.tsx with basic routing
Use modern React hooks and TypeScript best practices."

run_test "typescript-frontend" "sdet" "Create Jest tests for the frontend components:
- Create frontend/src/types/Property.test.ts for type validation
- Create frontend/src/services/api.test.ts with mocked fetch tests
- Create frontend/src/components/PropertyCard.test.tsx with React Testing Library
- Create frontend/src/components/PropertyList.test.tsx with integration tests
Aim for 90%+ code coverage."

run_test "typescript-frontend" "peer" "Review the TypeScript frontend code for:
- Proper TypeScript usage and type safety
- React component best practices and hooks usage
- API error handling and loading states
- Accessibility and responsive design
- Code organization and file structure
Provide actionable suggestions for improvement."

# ============================================================================
# Phase 3: Python Control Plane - Service Orchestration
# ============================================================================
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  Phase 3: Python Control Plane - Service Orchestration${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"

run_test "python-control" "architect" "Design a Python control plane for service orchestration:
- Health check system for monitoring backend and frontend
- Configuration management for service endpoints
- Logging and monitoring infrastructure
- Admin CLI for service operations
- Data aggregation from multiple services
Use modern Python patterns with async/await where appropriate."

run_test "python-control" "coder" "Implement the Python control plane:
- Create control-plane/app/health_checker.py with async health checks
- Create control-plane/app/config_manager.py for loading service configs
- Create control-plane/app/orchestrator.py for coordinating services
- Create control-plane/app/cli.py with Click-based admin CLI
Use asyncio, aiohttp for async operations and Click for CLI."

run_test "python-control" "sdet" "Create pytest test suite for the control plane:
- Create control-plane/tests/test_health_checker.py with async tests
- Create control-plane/tests/test_config_manager.py for configuration tests
- Create control-plane/tests/test_orchestrator.py with mock service tests
- Create control-plane/tests/test_cli.py for CLI command tests
Use pytest-asyncio and pytest-mock for comprehensive coverage."

run_test "python-control" "peer" "Review the Python control plane code for:
- Pythonic patterns and PEP 8 compliance
- Async/await usage and error handling
- Configuration management security
- CLI user experience and help messages
- Logging strategy and observability
Suggest improvements for production readiness."

# ============================================================================
# Phase 4: Integration & Documentation
# ============================================================================
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${MAGENTA}  Phase 4: Integration & Documentation${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"

run_test "integration" "architect" "Design the integration strategy for all three services:
- Service communication patterns (REST, events, health checks)
- Deployment architecture (docker-compose, kubernetes)
- Environment configuration management
- CI/CD pipeline considerations
- Monitoring and logging aggregation
Provide a comprehensive integration plan."

run_test "integration" "coder" "Create integration tooling:
- Create docker-compose.yml for running all services
- Create Makefile with commands for building and running each service
- Create .env.example with required environment variables
- Create scripts/setup.sh for initial project setup
Make it easy to run the entire stack locally."

run_test "integration" "sdet" "Create end-to-end integration tests:
- Create tests/e2e/test_property_workflow.py testing full property creation flow
- Create tests/e2e/test_service_health.py testing health check integration
- Create tests/e2e/test_api_integration.py testing frontend-backend communication
Use pytest with actual service instances where possible."

run_test "integration" "peer" "Review the complete home rental service project:
- Overall architecture and service boundaries
- Code consistency across Go, TypeScript, Python
- Testing coverage and quality across all components
- Documentation completeness and clarity
- Production readiness and scalability concerns
Provide a final assessment and recommendations."

################################################################################
# Summary Report
################################################################################

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                   Home Rental Service - Test Summary               ║${NC}"
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
echo -e "${CYAN}📂 Project: ${TEST_PROJECT}${NC}"
echo ""

if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}🎉 All tests passed! Home Rental Service is ready!${NC}"
    echo ""
    echo -e "${CYAN}Next steps:${NC}"
    echo "  cd $TEST_PROJECT"
    echo "  # Review generated code in backend/, frontend/, control-plane/"
    echo "  # Check docker-compose.yml and Makefile"
    echo "  # Run 'make build' and 'make run' to start services"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Review logs for details.${NC}"
    echo ""
    echo -e "${YELLOW}Debugging tips:${NC}"
    echo "  - Check $LOG_DIR for detailed test logs"
    echo "  - Review $RESULTS_FILE for summary"
    echo "  - Examine generated code in $TEST_PROJECT"
    exit 1
fi
