"""TDD Workflow Orchestrator - Coordinates multi-phase execution.

Execution Flow:
  Plan → Clarify → Confirm → Decompose → [For Each Work Item]:
                                           1. Define Structs/Interfaces
                                           2. Write Unit Tests (RED)
                                           3. Implement Functions (GREEN)
                                           4. Run & Verify Tests (REFACTOR)
"""

from enum import Enum
from typing import Optional


class ExecutionPhase(Enum):
    """Execution phases in TDD workflow."""
    
    STRUCT_INTERFACE = "struct_interface"
    TEST_FIXTURES = "test_fixtures"
    HAPPY_PATH_TESTS = "happy_path_tests"
    EDGE_CASE_TESTS = "edge_case_tests"
    ERROR_HANDLING_TESTS = "error_handling_tests"
    TEST_COVERAGE_ANALYSIS = "test_coverage_analysis"
    IMPLEMENTATION = "implementation"
    TEST_EXECUTION = "test_execution"


class TDDWorkflowOrchestrator:
    """Orchestrates TDD execution workflow across languages.
    
    Pattern:
    1. Define types/structures (input for tests)
    2. Write failing tests (RED)
    3. Implement to pass tests (GREEN)
    4. Verify all tests pass (REFACTOR)
    
    This ensures:
    - Clear contracts before implementation
    - Test coverage from the start
    - Confidence through verification
    - Language-aware patterns
    """
    
    def __init__(self, language: str, work_item):
        """Initialize orchestrator for language-specific workflow.
        
        Args:
            language: "go", "python", or "typescript"
            work_item: Work item with file_path, description, language
        """
        self.language = language.lower()
        self.work_item = work_item
        self.execution_state = {
            "structs_code": None,
            "test_code": None,
            "implementation_code": None,
            "test_results": None,
        }
    
    def phase_1_define_structures(self) -> dict:
        """Phase 1: Define structs/interfaces/types.
        
        Returns:
            Generated struct/interface code
        """
        from vivek.prompts.prompt_architecture import StructInterfacePrompt, WorkItem
        
        work_item = WorkItem(
            file_path=self.work_item.file_path,
            description=self.work_item.description,
            language=self.language
        )
        prompt_builder = StructInterfacePrompt()
        prompt_pair = prompt_builder.build(work_item)
        # LLM execution happens here
        # self.execution_state["structs_code"] = llm_response
        return prompt_pair.to_dict()
    
    def phase_2a_test_fixtures(self, signatures: str) -> dict:
        """Phase 2a: Define test fixtures, setup, and mocks.
        
        Args:
            signatures: Code from phase 1 (structs/interfaces)
        
        Returns:
            Generated test fixtures code
        """
        from vivek.prompts.granular_sdet_prompts import build_test_fixtures_prompt
        
        prompt = build_test_fixtures_prompt(self.work_item, self.language, signatures)
        # LLM execution happens here
        # self.execution_state["test_fixtures_code"] = llm_response
        return prompt
    
    def phase_2b_happy_path_tests(self, fixtures_code: str) -> dict:
        """Phase 2b: Write happy path tests (success scenarios).
        
        Args:
            fixtures_code: Test fixtures from phase 2a
        
        Returns:
            Generated happy path test code
        """
        from vivek.prompts.granular_sdet_prompts import build_happy_path_tests_prompt
        
        prompt = build_happy_path_tests_prompt(self.work_item, self.language, fixtures_code)
        # LLM execution happens here
        # self.execution_state["happy_path_tests_code"] = llm_response
        return prompt
    
    def phase_2c_edge_case_tests(self, fixtures_code: str) -> dict:
        """Phase 2c: Write edge case tests (boundary conditions).
        
        Args:
            fixtures_code: Test fixtures from phase 2a
        
        Returns:
            Generated edge case test code
        """
        from vivek.prompts.granular_sdet_prompts import build_edge_case_tests_prompt
        
        prompt = build_edge_case_tests_prompt(self.work_item, self.language, fixtures_code)
        # LLM execution happens here
        # self.execution_state["edge_case_tests_code"] = llm_response
        return prompt
    
    def phase_2d_error_handling_tests(self, fixtures_code: str) -> dict:
        """Phase 2d: Write error handling tests (exception scenarios).
        
        Args:
            fixtures_code: Test fixtures from phase 2a
        
        Returns:
            Generated error handling test code
        """
        from vivek.prompts.granular_sdet_prompts import build_error_handling_tests_prompt
        
        prompt = build_error_handling_tests_prompt(self.work_item, self.language, fixtures_code)
        # LLM execution happens here
        # self.execution_state["error_handling_tests_code"] = llm_response
        return prompt
    
    def phase_2e_test_coverage_analysis(
        self,
        test_output: str,
        coverage_report: str,
        implementation_files: str
    ) -> dict:
        """Phase 2e: Analyze test coverage and identify gaps.
        
        Args:
            test_output: Output from running all tests
            coverage_report: Code coverage report
            implementation_files: Implementation files being tested
        
        Returns:
            Coverage analysis results
        """
        from vivek.prompts.granular_sdet_prompts import build_test_coverage_prompt
        
        prompt = build_test_coverage_prompt(test_output, coverage_report, implementation_files)
        # LLM execution happens here
        # self.execution_state["coverage_analysis"] = llm_response
        return prompt
    
    def phase_3_implement(self, signatures: str, test_code: str) -> dict:
        """Phase 3: Implement functions/methods (GREEN phase).
        
        Args:
            signatures: Code from phase 1 (structs/interfaces)
            test_code: Code from phase 2 (unit tests)
        
        Returns:
            Generated implementation code
        """
        from vivek.prompts.prompt_architecture import ImplementationPrompt, WorkItem
        
        work_item = WorkItem(
            file_path=self.work_item.file_path,
            description=self.work_item.description,
            language=self.language
        )
        prompt_builder = ImplementationPrompt()
        prompt_pair = prompt_builder.build(work_item, signatures, test_code)
        # LLM execution happens here
        # self.execution_state["implementation_code"] = llm_response
        return prompt_pair.to_dict()
    
    def phase_4_run_tests(
        self,
        test_output: str,
        test_file_path: str,
        implementation_file_path: str
    ) -> dict:
        """Phase 4: Run tests and verify (REFACTOR phase).
        
        Args:
            test_output: Output from test runner
            test_file_path: Path to test file
            implementation_file_path: Path to implementation file
        
        Returns:
            Test execution analysis
        """
        from vivek.prompts.granular_sdet_prompts import build_test_coverage_prompt
        
        # Use coverage analysis prompt for test execution verification
        prompt = build_test_coverage_prompt(
            test_output,
            test_file_path,
            implementation_file_path
        )
        # LLM execution for analysis happens here
        # self.execution_state["test_results"] = llm_response
        return prompt
    
    def get_execution_plan(self) -> list:
        """Get ordered execution steps for this work item.
        
        Returns:
            List of execution phases in order (granular SDET included)
        """
        return [
            ExecutionPhase.STRUCT_INTERFACE,
            ExecutionPhase.TEST_FIXTURES,
            ExecutionPhase.HAPPY_PATH_TESTS,
            ExecutionPhase.EDGE_CASE_TESTS,
            ExecutionPhase.ERROR_HANDLING_TESTS,
            ExecutionPhase.TEST_COVERAGE_ANALYSIS,
            ExecutionPhase.IMPLEMENTATION,
            ExecutionPhase.TEST_EXECUTION,
        ]


# ============================================================================
# WORKFLOW EXAMPLES
# ============================================================================

EXAMPLE_GO_WORKFLOW = """
Go TDD Workflow Example:

1. STRUCT_INTERFACE - Define structs and interfaces
   Input:  Task description "Create a user service"
   Output: 
   ```go
   type User struct {
       ID    string
       Email string
       Name  string
   }
   
   type UserService interface {
       CreateUser(ctx context.Context, email string) (*User, error)
       GetUser(ctx context.Context, id string) (*User, error)
   }
   ```

2. UNIT_TESTS - Write table-driven tests (RED)
   Input:  Above structs
   Output:
   ```go
   func TestUserService_CreateUser(t *testing.T) {
       tests := []struct {
           name    string
           email   string
           wantErr bool
       }{
           {"valid email", "user@example.com", false},
           {"empty email", "", true},
       }
       for _, tt := range tests {
           t.Run(tt.name, func(t *testing.T) {
               // assertions
           })
       }
   }
   ```

3. IMPLEMENTATION - Write functions to pass tests (GREEN)
   Input:  Structs + tests
   Output:
   ```go
   func (s *userService) CreateUser(ctx context.Context, email string) (*User, error) {
       if email == "" {
           return nil, errors.New("email required")
       }
       // implementation
   }
   ```

4. TEST_EXECUTION - Run tests and verify
   Input:  go test output
   Output: Analysis of pass/fail and fixes needed
"""

EXAMPLE_PYTHON_WORKFLOW = """
Python TDD Workflow Example:

1. STRUCT_INTERFACE - Define dataclasses/Pydantic models
   Input:  Task description "Create a user service"
   Output:
   ```python
   from dataclasses import dataclass
   from typing import Protocol
   
   @dataclass
   class User:
       id: str
       email: str
       name: str
   
   class UserService(Protocol):
       def create_user(self, email: str) -> User: ...
   ```

2. UNIT_TESTS - Write pytest tests (RED)
   Input:  Above classes
   Output:
   ```python
   import pytest
   
   @pytest.fixture
   def service():
       return UserServiceImpl()
   
   def test_create_user_success(service):
       user = service.create_user("user@example.com")
       assert user.email == "user@example.com"
   
   def test_create_user_invalid_email(service):
       with pytest.raises(ValueError):
           service.create_user("")
   ```

3. IMPLEMENTATION - Write methods to pass tests (GREEN)
   Input:  Classes + tests
   Output:
   ```python
   class UserServiceImpl:
       def create_user(self, email: str) -> User:
           if not email:
               raise ValueError("Email required")
           return User(id=str(uuid.uuid4()), email=email, name="")
   ```

4. TEST_EXECUTION - Run pytest and verify
   Input:  pytest output
   Output: Analysis of pass/fail and fixes needed
"""

EXAMPLE_TYPESCRIPT_WORKFLOW = """
TypeScript TDD Workflow Example:

1. STRUCT_INTERFACE - Define interfaces and types
   Input:  Task description "Create a user service"
   Output:
   ```typescript
   interface User {
       id: string;
       email: string;
       name: string;
   }
   
   interface IUserService {
       createUser(email: string): Promise<User>;
       getUser(id: string): Promise<User>;
   }
   ```

2. UNIT_TESTS - Write Jest tests (RED)
   Input:  Above interfaces
   Output:
   ```typescript
   describe("UserService", () => {
       it("should create user with valid email", async () => {
           const service = new UserService();
           const user = await service.createUser("user@example.com");
           expect(user.email).toBe("user@example.com");
       });
   
       it("should throw on invalid email", async () => {
           const service = new UserService();
           await expect(service.createUser("")).rejects.toThrow();
       });
   });
   ```

3. IMPLEMENTATION - Write methods to pass tests (GREEN)
   Input:  Interfaces + tests
   Output:
   ```typescript
   class UserService implements IUserService {
       async createUser(email: string): Promise<User> {
           if (!email) throw new Error("Email required");
           return {
               id: crypto.randomUUID(),
               email,
               name: "",
           };
       }
   }
   ```

4. TEST_EXECUTION - Run jest and verify
   Input:  jest output
   Output: Analysis of pass/fail and fixes needed
"""


if __name__ == "__main__":
    print("TDD Workflow Orchestrator Examples")
    print("=" * 50)
    print(EXAMPLE_GO_WORKFLOW)
    print("\n")
    print(EXAMPLE_PYTHON_WORKFLOW)
    print("\n")
    print(EXAMPLE_TYPESCRIPT_WORKFLOW)
