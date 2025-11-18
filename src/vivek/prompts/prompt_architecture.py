"""Prompt architecture with interfaces and abstract classes.

Defines the contract for all prompt types and their builders using ABCs and protocols.
Enables type-safe, extensible prompt system.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol


# ============================================================================
# ENUMS
# ============================================================================

class ExecutorMode(Enum):
    """Executor modes for work item execution."""
    CODER = "coder"
    SDET = "sdet"
    ARCHITECT = "architect"
    PEER = "peer"


class SDETPhase(Enum):
    """SDET (test) workflow phases."""
    FIXTURES = "phase_1_fixtures"
    HAPPY_PATH = "phase_2b_happy_path"
    EDGE_CASES = "phase_2c_edge_cases"
    ERROR_HANDLING = "phase_2d_error_handling"
    COVERAGE_ANALYSIS = "phase_2e_coverage_analysis"


class PlannerPhase(Enum):
    """Planner workflow phases."""
    CLARIFICATION = "clarification"
    CONFIRMATION = "confirmation"
    DECOMPOSITION = "decomposition"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class PromptPair:
    """A complete prompt with system and user components."""
    system: str
    user: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format."""
        return {"system": self.system, "user": self.user}


@dataclass
class WorkItem:
    """Work item with metadata for execution."""
    file_path: str
    description: str
    language: Optional[str] = None
    mode: Optional[ExecutorMode] = None
    sdet_phase: Optional[SDETPhase] = None


# ============================================================================
# PROTOCOLS (Type Hints)
# ============================================================================

class PromptBuilder(Protocol):
    """Protocol for prompt builder functions."""

    def build(self, *args, **kwargs) -> PromptPair:
        """Build and return a PromptPair."""
        ...


# ============================================================================
# ABSTRACT BASE CLASSES
# ============================================================================

class BasePrompt(ABC):
    """Abstract base class for all prompt types."""

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        """System prompt (instructions for LLM role/behavior)."""
        pass

    @property
    @abstractmethod
    def user_prompt_template(self) -> str:
        """User prompt template with {placeholders} for formatting."""
        pass

    @abstractmethod
    def build(self, *args: Any, **kwargs: Any) -> PromptPair:
        """Build and return a complete PromptPair.
        
        Returns:
            PromptPair with system and formatted user prompt
        """
        pass

    def to_dict(self) -> Dict[str, str]:
        """Convert built prompt to dictionary."""
        # Subclasses should override build() to use this
        raise NotImplementedError


class BasePlannerPrompt(BasePrompt):
    """Abstract base for planner workflow prompts."""

    @property
    @abstractmethod
    def phase(self) -> PlannerPhase:
        """Which phase of planning this represents."""
        pass


class BaseExecutorPrompt(BasePrompt):
    """Abstract base for executor workflow prompts."""

    @property
    @abstractmethod
    def executor_mode(self) -> ExecutorMode:
        """Which executor mode this supports."""
        pass


# ============================================================================
# CONCRETE PROMPT IMPLEMENTATIONS - PLANNER
# ============================================================================

class ClarificationPrompt(BasePlannerPrompt):
    """Prompt for clarification phase (ask questions)."""

    @property
    def phase(self) -> PlannerPhase:
        return PlannerPhase.CLARIFICATION

    @property
    def system_prompt(self) -> str:
        return """You are a skilled requirement analyst.
Your task is to identify gaps in user requirements and ask clarifying questions.

Be SUCCINCT - ask key questions to better comprehend the ask.
Focus on critical unknowns that affect architecture and scope."""

    @property
    def user_prompt_template(self) -> str:
        return """Project Context:
{project_context}

User Request:
{user_request}

Ask 2-4 clarifying questions if critical information is missing.
Output format:
{{
  "needs_clarification": true/false,
  "questions": ["Q1", "Q2"],
  "reason": "Brief explanation"
}}

Be direct. Only ask if information is truly critical."""

    def build(self, project_context: str, user_request: str) -> PromptPair:
        """Build clarification prompt.
        
        Args:
            project_context: Project information
            user_request: User's initial request
        
        Returns:
            PromptPair with formatted prompts
        """
        user = self.user_prompt_template.format(
            project_context=project_context,
            user_request=user_request
        )
        return PromptPair(system=self.system_prompt, user=user)


class ConfirmationPrompt(BasePlannerPrompt):
    """Prompt for confirmation phase (validate understanding)."""

    @property
    def phase(self) -> PlannerPhase:
        return PlannerPhase.CONFIRMATION

    @property
    def system_prompt(self) -> str:
        return """You are a requirements validation expert.
Your task is to confirm understanding of requirements based on provided information.

Validate scope, constraints, and assumptions clearly and concisely."""

    @property
    def user_prompt_template(self) -> str:
        return """Project Context:
{project_context}

User Request:
{user_request}

Clarifications Provided:
{clarifications}

Confirm your understanding in bullet points (5-7 max):
{{
  "understanding": [
    "• What we're building: [brief description]",
    "• Scope: [key boundaries]",
    "• Key constraints: [limitations]",
    "• Assumptions: [critical assumptions]",
    "• Success criteria: [how to know it's done]"
  ],
  "confirmed": true/false,
  "concerns": "Any concerns or red flags (if any)"
}}

Be concise."""

    def build(
        self,
        project_context: str,
        user_request: str,
        clarifications: str
    ) -> PromptPair:
        """Build confirmation prompt.
        
        Args:
            project_context: Project information
            user_request: User's initial request
            clarifications: Q&A from clarification phase
        
        Returns:
            PromptPair with formatted prompts
        """
        user = self.user_prompt_template.format(
            project_context=project_context,
            user_request=user_request,
            clarifications=clarifications
        )
        return PromptPair(system=self.system_prompt, user=user)


class DecompositionPrompt(BasePlannerPrompt):
    """Prompt for decomposition phase (create work items)."""

    @property
    def phase(self) -> PlannerPhase:
        return PlannerPhase.DECOMPOSITION

    @property
    def system_prompt(self) -> str:
        return """You are an expert software architect.
Your task is to decompose confirmed requirements into actionable work items.

[Full decomposition rules from multi_phase_planner_prompts.py...]"""

    @property
    def user_prompt_template(self) -> str:
        return """Project Context:
{project_context}

Confirmed Requirements:
{confirmed_understanding}

Create 5-10 work items using TDD decomposition...
[Full template from multi_phase_planner_prompts.py...]"""

    def build(
        self,
        project_context: str,
        confirmed_understanding: str
    ) -> PromptPair:
        """Build decomposition prompt.
        
        Args:
            project_context: Project information
            confirmed_understanding: Validated requirements from phase 2
        
        Returns:
            PromptPair with formatted prompts
        """
        user = self.user_prompt_template.format(
            project_context=project_context,
            confirmed_understanding=confirmed_understanding
        )
        return PromptPair(system=self.system_prompt, user=user)


# ============================================================================
# CONCRETE PROMPT IMPLEMENTATIONS - EXECUTOR (TDD)
# ============================================================================

class StructInterfacePrompt(BaseExecutorPrompt):
    """Prompt for defining structures and interfaces (Phase 1)."""

    @property
    def executor_mode(self) -> ExecutorMode:
        return ExecutorMode.CODER

    @property
    def system_prompt(self) -> str:
        return """You are an expert software architect.
Your task is to define data structures and interfaces (contracts).

Requirements:
1. Define ONLY types, structs, interfaces, or classes (no implementations)
2. Include comprehensive type hints / type annotations
3. Add docstrings explaining the contract
4. Design for extensibility and clarity
5. Output ONLY code, no explanations"""

    @property
    def user_prompt_template(self) -> str:
        return """File: {file_path}
Language: {language}
Task: {description}

Output ONLY the {language} code (package/imports required)."""

    def build(self, work_item: WorkItem) -> PromptPair:
        """Build struct/interface definition prompt.
        
        Args:
            work_item: Work item with file_path, description, language
        
        Returns:
            PromptPair with formatted prompts
        """
        user = self.user_prompt_template.format(
            file_path=work_item.file_path,
            language=work_item.language,
            description=work_item.description
        )
        return PromptPair(system=self.system_prompt, user=user)


class TestFixturesPrompt(BaseExecutorPrompt):
    """Prompt for test fixtures (SDET Phase 1)."""

    @property
    def executor_mode(self) -> ExecutorMode:
        return ExecutorMode.SDET

    @property
    def system_prompt(self) -> str:
        return """You are an expert SDET (Software Development Engineer in Test).
Your task is to define test fixtures, mocks, and setup utilities.

Requirements:
1. Create reusable test fixtures and test data builders
2. Define mock objects if external dependencies exist
3. Keep fixtures focused and composable
4. Include clear documentation
5. Output ONLY test infrastructure code, no actual test cases yet"""

    @property
    def user_prompt_template(self) -> str:
        return """Test File: {file_path}
Language: {language}
Structures: {signatures}
Task: {description}

Create test fixtures for {language}.
Output ONLY the fixture code (imports required)."""

    def build(self, work_item: WorkItem, signatures: str) -> PromptPair:
        """Build test fixtures prompt.
        
        Args:
            work_item: Work item with file_path, description, language
            signatures: Code signatures/structures to test
        
        Returns:
            PromptPair with formatted prompts
        """
        user = self.user_prompt_template.format(
            file_path=work_item.file_path,
            language=work_item.language,
            signatures=signatures,
            description=work_item.description
        )
        return PromptPair(system=self.system_prompt, user=user)


class HappyPathTestsPrompt(BaseExecutorPrompt):
    """Prompt for happy path tests (SDET Phase 2b)."""

    @property
    def executor_mode(self) -> ExecutorMode:
        return ExecutorMode.SDET

    @property
    def system_prompt(self) -> str:
        return """You are an expert SDET (Software Development Engineer in Test).
Your task is to write happy path tests (primary success scenarios).

Requirements:
1. Test the main success path of the feature
2. Use 3-5 core scenarios that demonstrate intended behavior
3. Each test should be independent
4. Assert both return values and state changes
5. Use clear, descriptive test names
6. Output ONLY test code, no explanations"""

    @property
    def user_prompt_template(self) -> str:
        return """Test File: {file_path}
Language: {language}
Fixtures: {fixtures_code}
Task: {description}

Write happy path tests using fixtures.
Output ONLY the test code (imports required)."""

    def build(self, work_item: WorkItem, fixtures_code: str) -> PromptPair:
        """Build happy path tests prompt.
        
        Args:
            work_item: Work item with file_path, description, language
            fixtures_code: Test fixtures from phase 1
        
        Returns:
            PromptPair with formatted prompts
        """
        user = self.user_prompt_template.format(
            file_path=work_item.file_path,
            language=work_item.language,
            fixtures_code=fixtures_code,
            description=work_item.description
        )
        return PromptPair(system=self.system_prompt, user=user)


class ImplementationPrompt(BaseExecutorPrompt):
    """Prompt for implementation (GREEN phase)."""

    @property
    def executor_mode(self) -> ExecutorMode:
        return ExecutorMode.CODER

    @property
    def system_prompt(self) -> str:
        return """You are an expert software engineer.
Your task is to implement functions/methods to pass the provided unit tests (GREEN phase of TDD).

Requirements:
1. Write code that passes ALL provided unit tests
2. Follow language best practices and conventions
3. Handle all error cases tested
4. Keep functions focused and small (<50 lines)
5. Add clear docstrings/comments
6. Output ONLY code, no explanations"""

    @property
    def user_prompt_template(self) -> str:
        return """File: {file_path}
Language: {language}
Signatures: {signatures}
Tests: {test_code}
Task: {description}

Implement to pass all tests.
Output ONLY the implementation code (imports required)."""

    def build(
        self,
        work_item: WorkItem,
        signatures: str,
        test_code: str
    ) -> PromptPair:
        """Build implementation prompt.
        
        Args:
            work_item: Work item with file_path, description, language
            signatures: Code signatures/structures
            test_code: Unit test code to pass
        
        Returns:
            PromptPair with formatted prompts
        """
        user = self.user_prompt_template.format(
            file_path=work_item.file_path,
            language=work_item.language,
            signatures=signatures,
            test_code=test_code,
            description=work_item.description
        )
        return PromptPair(system=self.system_prompt, user=user)


# ============================================================================
# PROMPT FACTORY
# ============================================================================

class PromptFactory:
    """Factory for creating appropriate prompt instances."""

    _planner_prompts = {
        PlannerPhase.CLARIFICATION: ClarificationPrompt(),
        PlannerPhase.CONFIRMATION: ConfirmationPrompt(),
        PlannerPhase.DECOMPOSITION: DecompositionPrompt(),
    }

    _executor_prompts = {
        (ExecutorMode.CODER, "struct"): StructInterfacePrompt(),
        (ExecutorMode.SDET, SDETPhase.FIXTURES): TestFixturesPrompt(),
        (ExecutorMode.SDET, SDETPhase.HAPPY_PATH): HappyPathTestsPrompt(),
        (ExecutorMode.CODER, "implementation"): ImplementationPrompt(),
    }

    @staticmethod
    def get_planner_prompt(phase: PlannerPhase) -> BasePlannerPrompt:
        """Get planner prompt for given phase.
        
        Args:
            phase: PlannerPhase enum value
        
        Returns:
            Appropriate planner prompt instance
        
        Raises:
            ValueError: If phase not supported
        """
        if phase not in PromptFactory._planner_prompts:
            raise ValueError(f"Unsupported planner phase: {phase}")
        return PromptFactory._planner_prompts[phase]

    @staticmethod
    def get_executor_prompt(
        mode: ExecutorMode,
        stage: Optional[SDETPhase] = None
    ) -> BaseExecutorPrompt:
        """Get executor prompt for given mode and stage.
        
        Args:
            mode: ExecutorMode enum value
            stage: SDETPhase for SDET mode, or string stage for coder mode
        
        Returns:
            Appropriate executor prompt instance
        
        Raises:
            ValueError: If mode/stage not supported
        """
        key = (mode, stage) if stage else (mode, None)
        if key not in PromptFactory._executor_prompts:
            raise ValueError(f"Unsupported executor combination: {key}")
        return PromptFactory._executor_prompts[key]


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ============================================================================

def build_clarification_prompt(
    user_request: str,
    project_context: str
) -> Dict[str, str]:
    """Build clarification phase prompt (legacy interface).
    
    Args:
        user_request: Initial user request
        project_context: Project information
    
    Returns:
        Dict with system and user prompts
    """
    prompt = PromptFactory.get_planner_prompt(PlannerPhase.CLARIFICATION)
    return prompt.build(
        project_context=project_context,
        user_request=user_request
    ).to_dict()


def build_confirmation_prompt(
    user_request: str,
    project_context: str,
    clarifications: str
) -> Dict[str, str]:
    """Build confirmation phase prompt (legacy interface).
    
    Args:
        user_request: Original user request
        project_context: Project information
        clarifications: Clarification Q&A from phase 1
    
    Returns:
        Dict with system and user prompts
    """
    prompt = PromptFactory.get_planner_prompt(PlannerPhase.CONFIRMATION)
    return prompt.build(
        project_context=project_context,
        user_request=user_request,
        clarifications=clarifications
    ).to_dict()


def build_decomposition_prompt(
    project_context: str,
    confirmed_understanding: str
) -> Dict[str, str]:
    """Build decomposition phase prompt (legacy interface).
    
    Args:
        project_context: Project information
        confirmed_understanding: Validated requirements from phase 2
    
    Returns:
        Dict with system and user prompts
    """
    prompt = PromptFactory.get_planner_prompt(PlannerPhase.DECOMPOSITION)
    return prompt.build(
        project_context=project_context,
        confirmed_understanding=confirmed_understanding
    ).to_dict()
