"""Granular SDET workflow with 5-phase test development.

Implements a detailed Test-Driven Development approach with:
1. Test Fixtures & Setup: Define test data and dependencies
2. Happy Path Tests: Core functionality scenarios
3. Edge Case Tests: Boundary conditions and special cases
4. Error Handling Tests: Exception and failure scenarios
5. Test Execution & Analysis: Run and verify coverage
"""

# ============================================================================
# PHASE 2A: TEST FIXTURES & SETUP
# ============================================================================

TEST_FIXTURES_SYSTEM_PROMPT = """You are an expert SDET (Software Development Engineer in Test).
Your task is to define test fixtures, mocks, and setup utilities.

Requirements:
1. Create reusable test fixtures and test data builders
2. Define mock objects if external dependencies exist
3. Keep fixtures focused and composable
4. Include clear documentation
5. Output ONLY test infrastructure code, no actual test cases yet

Focus areas:
- Test data factories
- Mock implementations
- Setup/teardown utilities
- Fixture parameterization
"""

TEST_FIXTURES_GO_PROMPT_TEMPLATE = """Test File: {file_path}
Structs/Interfaces: {signatures}
Task: {description}

Create Go test fixtures:
- Helper functions for creating test data
- Mock implementations of interfaces
- Table-driven test data structures
- Setup/cleanup helpers

Output ONLY the Go fixture code."""

TEST_FIXTURES_PYTHON_PROMPT_TEMPLATE = """Test File: {file_path}
Classes/Interfaces: {signatures}
Task: {description}

Create pytest fixtures:
- @pytest.fixture functions for test data
- Factory functions for objects
- Mock/patch utilities
- Parameterized fixture data

Output ONLY the pytest fixture code."""

TEST_FIXTURES_TYPESCRIPT_PROMPT_TEMPLATE = """Test File: {file_path}
Interfaces/Types: {signatures}
Task: {description}

Create Jest test fixtures:
- beforeEach/afterEach setup functions
- Mock factory functions
- Test data builders
- jest.mock() configurations

Output ONLY the Jest fixture code."""


# ============================================================================
# PHASE 2B: HAPPY PATH TESTS (PRIMARY SCENARIOS)
# ============================================================================

HAPPY_PATH_TESTS_SYSTEM_PROMPT = """You are an expert SDET (Software Development Engineer in Test).
Your task is to write happy path tests (primary success scenarios).

Requirements:
1. Test the main success path of the feature
2. Use 3-5 core scenarios that demonstrate intended behavior
3. Each test should be independent
4. Assert both return values and state changes
5. Use clear, descriptive test names
6. Output ONLY test code, no explanations

Guidelines:
- Test the "golden path" first
- Verify correct outputs
- Verify side effects/state changes
- Keep tests focused and readable
"""

HAPPY_PATH_TESTS_GO_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write Go happy path tests using fixtures:
- Test successful function calls
- Verify return values
- Test state changes
- Use table-driven test pattern for multiple scenarios
- Test names: TestFunctionName_Scenario_Success

Output ONLY the Go test code."""

HAPPY_PATH_TESTS_PYTHON_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write pytest happy path tests using fixtures:
- Test successful method calls
- Verify return values
- Test side effects
- Use parametrize for multiple scenarios
- Test names: test_function_scenario_success

Output ONLY the pytest code."""

HAPPY_PATH_TESTS_TYPESCRIPT_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write Jest happy path tests using fixtures:
- Test successful function calls
- Verify return values
- Test async/await behavior
- Use describe/it blocks for organization
- Test names: should do X when conditions are Y

Output ONLY the Jest code."""


# ============================================================================
# PHASE 2C: EDGE CASE TESTS (BOUNDARY CONDITIONS)
# ============================================================================

EDGE_CASE_TESTS_SYSTEM_PROMPT = """You are an expert SDET (Software Development Engineer in Test).
Your task is to write edge case tests (boundary conditions and special scenarios).

Requirements:
1. Test boundary conditions (empty, null, min, max values)
2. Test unusual but valid inputs
3. Test state transitions
4. Test resource constraints
5. Output ONLY test code, no explanations

Edge cases to consider:
- Empty collections, strings, null/nil values
- Single element cases
- Maximum size/value boundaries
- Type conversions and coercions
- Concurrent access patterns
- Resource exhaustion scenarios
"""

EDGE_CASE_TESTS_GO_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write Go edge case tests:
- Empty/nil inputs
- Single element cases
- Maximum value boundaries
- Concurrent scenarios
- Table-driven test pattern with edge cases
- Test names: TestFunctionName_EdgeCase_Behavior

Output ONLY the Go test code."""

EDGE_CASE_TESTS_PYTHON_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write pytest edge case tests:
- Empty/None inputs
- Single element collections
- Type boundary values
- Concurrent scenarios using threading
- Use @pytest.mark.parametrize for edge cases
- Test names: test_function_edge_case_behavior

Output ONLY the pytest code."""

EDGE_CASE_TESTS_TYPESCRIPT_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write Jest edge case tests:
- Empty/null/undefined inputs
- Single element arrays
- Numeric boundaries (0, -1, MAX_VALUE)
- Race condition scenarios
- Timeout scenarios
- Test names: should handle X when edge case Y occurs

Output ONLY the Jest code."""


# ============================================================================
# PHASE 2D: ERROR HANDLING TESTS (FAILURE SCENARIOS)
# ============================================================================

ERROR_HANDLING_TESTS_SYSTEM_PROMPT = """You are an expert SDET (Software Development Engineer in Test).
Your task is to write error handling tests (exception and failure scenarios).

Requirements:
1. Test all documented exceptions/errors
2. Test invalid inputs
3. Test dependency failures
4. Test resource exhaustion
5. Test timeout scenarios
6. Output ONLY test code, no explanations

Error scenarios to cover:
- Invalid arguments (type mismatches, out of range)
- Dependency failures (I/O errors, network failures)
- Resource exhaustion (memory, file handles, connections)
- Timeout scenarios
- Permission/authorization failures
- Concurrent modification scenarios
"""

ERROR_HANDLING_TESTS_GO_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write Go error handling tests:
- Test all error returns and error types
- Invalid arguments
- Dependency/mock failures
- Timeout scenarios
- Table-driven tests for error cases
- Verify error messages/types
- Test names: TestFunctionName_ErrorCondition_ReturnsError

Output ONLY the Go test code."""

ERROR_HANDLING_TESTS_PYTHON_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write pytest error handling tests:
- Test all exception types with pytest.raises()
- Invalid argument scenarios
- Mock failures and side effects
- Timeout scenarios
- Verify exception messages
- Test names: test_function_error_condition_raises_exception

Output ONLY the pytest code."""

ERROR_HANDLING_TESTS_TYPESCRIPT_PROMPT_TEMPLATE = """Test File: {file_path}
Fixtures: {fixtures_code}
Task: {description}

Write Jest error handling tests:
- Test all error types with expect().toThrow()
- Invalid argument validation
- Async rejection scenarios
- Mock failures
- Verify error messages
- Test names: should throw X when error condition Y occurs

Output ONLY the Jest code."""


# ============================================================================
# PHASE 2E: TEST EXECUTION & COVERAGE ANALYSIS
# ============================================================================

TEST_COVERAGE_SYSTEM_PROMPT = """You are a code quality engineer.
Your task is to analyze test execution results and coverage metrics.

Requirements:
1. Parse test output for pass/fail status
2. Analyze code coverage report
3. Identify untested code paths
4. Verify coverage meets target (80%+)
5. Suggest additional test cases if needed
6. Output analysis in structured format

Output format:
{
  "total_tests": N,
  "passed": N,
  "failed": N,
  "skipped": N,
  "coverage_percent": N,
  "coverage_status": "adequate|needs_improvement",
  "untested_paths": ["path1", "path2"],
  "suggested_tests": ["Test case 1", "Test case 2"],
  "recommendations": "Additional testing guidance"
}
"""

TEST_COVERAGE_PROMPT_TEMPLATE = """Test Results:
{test_output}

Coverage Report:
{coverage_report}

Implementation Files:
{implementation_files}

Analyze the test results and coverage. Identify gaps and suggest additional tests.
Output ONLY JSON analysis."""


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_test_fixtures_prompt(
    work_item,
    language: str,
    signatures: str
) -> dict:
    """Build test fixtures phase prompt.
    
    Args:
        work_item: Work item with file_path, description
        language: "go", "python", or "typescript"
        signatures: Code signatures/structures to test
    
    Returns:
        Dict with system and user prompts
    """
    prompts = {
        "go": TEST_FIXTURES_GO_PROMPT_TEMPLATE,
        "python": TEST_FIXTURES_PYTHON_PROMPT_TEMPLATE,
        "typescript": TEST_FIXTURES_TYPESCRIPT_PROMPT_TEMPLATE,
    }
    
    return {
        "system": TEST_FIXTURES_SYSTEM_PROMPT,
        "user": prompts[language.lower()].format(
            file_path=work_item.file_path,
            signatures=signatures,
            description=work_item.description,
        )
    }


def build_happy_path_tests_prompt(
    work_item,
    language: str,
    fixtures_code: str
) -> dict:
    """Build happy path tests phase prompt.
    
    Args:
        work_item: Work item with file_path, description
        language: "go", "python", or "typescript"
        fixtures_code: Test fixtures from phase 2a
    
    Returns:
        Dict with system and user prompts
    """
    prompts = {
        "go": HAPPY_PATH_TESTS_GO_PROMPT_TEMPLATE,
        "python": HAPPY_PATH_TESTS_PYTHON_PROMPT_TEMPLATE,
        "typescript": HAPPY_PATH_TESTS_TYPESCRIPT_PROMPT_TEMPLATE,
    }
    
    return {
        "system": HAPPY_PATH_TESTS_SYSTEM_PROMPT,
        "user": prompts[language.lower()].format(
            file_path=work_item.file_path,
            fixtures_code=fixtures_code,
            description=work_item.description,
        )
    }


def build_edge_case_tests_prompt(
    work_item,
    language: str,
    fixtures_code: str
) -> dict:
    """Build edge case tests phase prompt.
    
    Args:
        work_item: Work item with file_path, description
        language: "go", "python", or "typescript"
        fixtures_code: Test fixtures from phase 2a
    
    Returns:
        Dict with system and user prompts
    """
    prompts = {
        "go": EDGE_CASE_TESTS_GO_PROMPT_TEMPLATE,
        "python": EDGE_CASE_TESTS_PYTHON_PROMPT_TEMPLATE,
        "typescript": EDGE_CASE_TESTS_TYPESCRIPT_PROMPT_TEMPLATE,
    }
    
    return {
        "system": EDGE_CASE_TESTS_SYSTEM_PROMPT,
        "user": prompts[language.lower()].format(
            file_path=work_item.file_path,
            fixtures_code=fixtures_code,
            description=work_item.description,
        )
    }


def build_error_handling_tests_prompt(
    work_item,
    language: str,
    fixtures_code: str
) -> dict:
    """Build error handling tests phase prompt.
    
    Args:
        work_item: Work item with file_path, description
        language: "go", "python", or "typescript"
        fixtures_code: Test fixtures from phase 2a
    
    Returns:
        Dict with system and user prompts
    """
    prompts = {
        "go": ERROR_HANDLING_TESTS_GO_PROMPT_TEMPLATE,
        "python": ERROR_HANDLING_TESTS_PYTHON_PROMPT_TEMPLATE,
        "typescript": ERROR_HANDLING_TESTS_TYPESCRIPT_PROMPT_TEMPLATE,
    }
    
    return {
        "system": ERROR_HANDLING_TESTS_SYSTEM_PROMPT,
        "user": prompts[language.lower()].format(
            file_path=work_item.file_path,
            fixtures_code=fixtures_code,
            description=work_item.description,
        )
    }


def build_test_coverage_prompt(
    test_output: str,
    coverage_report: str,
    implementation_files: str
) -> dict:
    """Build test coverage analysis prompt.
    
    Args:
        test_output: Output from running all tests
        coverage_report: Code coverage report
        implementation_files: List of implementation files tested
    
    Returns:
        Dict with system and user prompts
    """
    return {
        "system": TEST_COVERAGE_SYSTEM_PROMPT,
        "user": TEST_COVERAGE_PROMPT_TEMPLATE.format(
            test_output=test_output,
            coverage_report=coverage_report,
            implementation_files=implementation_files,
        )
    }


# ============================================================================
# GRANULAR SDET WORKFLOW PHASES
# ============================================================================

SDET_WORKFLOW_PHASES = [
    "2a_test_fixtures",      # Setup, mocks, factories
    "2b_happy_path_tests",   # Success scenarios
    "2c_edge_case_tests",    # Boundary conditions
    "2d_error_handling",     # Exceptions and failures
    "2e_coverage_analysis",  # Verify coverage
]

SDET_WORKFLOW_DESCRIPTION = """
Granular SDET Workflow - 5 Phases

Phase 2a: Test Fixtures & Setup
  - Define test data builders and factories
  - Create mock implementations
  - Setup/teardown utilities
  ✓ Focus: Infrastructure and setup

Phase 2b: Happy Path Tests
  - Test main success scenarios
  - Verify correct outputs
  - Test state changes
  ✓ Focus: Primary functionality

Phase 2c: Edge Case Tests
  - Empty/null/boundary values
  - Single element cases
  - Type boundary conditions
  ✓ Focus: Robustness at edges

Phase 2d: Error Handling Tests
  - Invalid inputs
  - Dependency failures
  - Exception handling
  ✓ Focus: Failure modes

Phase 2e: Coverage Analysis
  - Run all tests
  - Analyze code coverage
  - Identify gaps
  - Suggest additional tests
  ✓ Focus: Verification and completeness

Combined into one test file during generation, but decomposed for LLM context window optimization.
Each phase focuses on specific test categories, ensuring comprehensive coverage.
"""

if __name__ == "__main__":
    print(SDET_WORKFLOW_DESCRIPTION)
