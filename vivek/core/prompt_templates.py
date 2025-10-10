"""
Structured Prompt Templates for Vivek

This module provides structured prompt templates that align with the natural
engineering workflow and support multiple perspectives analysis.
"""

from typing import Dict, Any, List
from .structured_workflow import (
    WorkflowPhase,
    PerspectiveHat,
    ActivityBreakdown,
    TaskDefinition,
    ContextSummary,
)


class StructuredPromptBuilder:
    """Builds structured prompts aligned with engineering workflow"""

    def __init__(self):
        self.context_budget = 4000  # tokens
        self.phase_templates = self._initialize_phase_templates()

    def _initialize_phase_templates(self) -> Dict[str, str]:
        """Initialize prompt templates for each workflow phase"""
        return {
            WorkflowPhase.UNDERSTAND.value: self._build_understand_template(),
            WorkflowPhase.DECOMPOSE.value: self._build_decompose_template(),
            WorkflowPhase.DETAIL.value: self._build_detail_template(),
            WorkflowPhase.TASKIFY.value: self._build_taskify_template(),
            WorkflowPhase.EXECUTE.value: self._build_execute_template(),
        }

    def _build_understand_template(self) -> str:
        """Build template for understanding phase"""
        return """# 🎯 UNDERSTANDING PHASE - Clarify Intent & Scope

## Context Summary
{context_summary}

## User Request
{user_input}

## Understanding Framework

### 1. Core Intent Analysis
What is the user fundamentally trying to achieve?
- Primary goal:
- Key requirements:
- Success criteria:

### 2. Scope Definition
What boundaries should we establish?
**In Scope:**
- Core functionality requested
- Essential supporting features
- Basic error handling and validation

**Out of Scope:**
- Advanced features not mentioned
- Future enhancements
- Non-essential optimizations

### 3. Assumptions & Prerequisites
What must be true for this to work?
- Technical assumptions:
- Required dependencies:
- Existing constraints:

### 4. Success Metrics
How will we know this is complete?
- Functional requirements:
- Quality standards:
- Performance expectations:

## Critical Thinking Questions
1. Is the request clear and unambiguous?
2. Are there implicit requirements not stated?
3. What could go wrong with this approach?
4. How might this evolve in the future?

## Output Format (JSON)
{{
  "understanding_complete": true/false,
  "needs_clarification": false/true,
  "core_intent": "clear statement of what user wants",
  "scope_definition": {{
    "in_scope": ["item1", "item2"],
    "out_of_scope": ["item1", "item2"]
  }},
  "assumptions": ["assumption1", "assumption2"],
  "success_criteria": ["criterion1", "criterion2"],
  "clarification_questions": ["question1", "question2"]  // if needs_clarification=true
}}"""

    def _build_decompose_template(self) -> str:
        """Build template for decomposition phase"""
        return """# 🔄 DECOMPOSITION PHASE - Break Into Activities

## Understanding Summary
{understanding_summary}

## Decomposition Framework

### Activity Identification Strategy
Break down the request into 3-5 high-level activities that:
- Represent logical units of work
- Can be completed independently (when possible)
- Follow natural development workflow
- Have clear start/end points

### Activity Structure
For each activity, define:
- **Name**: Clear, actionable title
- **Description**: What work needs to be done
- **Expected Outcomes**: Measurable results
- **Dependencies**: What must come first
- **Boundaries**: What is/isn't included

## Multiple Perspectives Analysis
Analyze each activity from six critical perspectives:

### 👤 USER Perspective
- How does this activity impact user experience?
- Is the user flow intuitive and efficient?
- What usability considerations exist?

### 🧭 CRITIC Perspective
- What are the weaknesses or risks?
- What could go wrong?
- What are the trade-offs?

### 🧰 OPS/DevOps Perspective
- How deployable and maintainable is this?
- What monitoring/logging is needed?
- How will this scale?

### 🐞 DEBUGGER Perspective
- How easy will this be to troubleshoot?
- What debugging information should be included?
- How will errors be surfaced and diagnosed?

### 🚀 FUTURE Perspective
- How will this adapt to future needs?
- What extension points are needed?
- How will this scale?

### 🤝 SDET (Testing) Perspective
- How testable is this approach?
- What edge cases need coverage?
- How will quality be validated?

## Output Format (JSON)
{{
  "activities": [
    {{
      "activity_id": "activity_1",
      "name": "Set up authentication system",
      "description": "Implement user authentication with JWT tokens",
      "expected_outcomes": ["Users can login/logout", "JWT tokens work"],
      "dependencies": [],
      "boundaries": ["Focus on core auth only", "No advanced features"],
      "perspectives": {{
        "user": "Simple login flow for good UX",
        "critic": "Security vulnerabilities in token handling",
        "ops": "Easy to deploy and monitor",
        "debugger": "Clear error messages for auth failures",
        "future": "Extensible for OAuth, MFA later",
        "sdet": "Comprehensive test coverage for auth flows"
      }}
    }}
  ],
  "decomposition_rationale": "Explanation of how activities were derived"
}}"""

    def _build_detail_template(self) -> str:
        """Build template for detailing phase"""
        return """# 📋 DETAILING PHASE - Elaborate Activities

## Activity Overview
{activity_overview}

## Detailing Framework

### Expected Outcomes Refinement
For each activity, detail what "done" means:
- **Functional outcomes**: What works when complete?
- **Quality outcomes**: What standards must be met?
- **Documentation outcomes**: What must be documented?
- **Testing outcomes**: What must be validated?

### Boundary Clarification
For each activity, clarify:
- **What's definitely included**: Core deliverables
- **What's definitely excluded**: Out of scope items
- **What's negotiable**: Nice-to-have items
- **What's dependent**: External factors

### Risk Assessment
For each activity, identify:
- **Technical risks**: Implementation challenges
- **Quality risks**: Potential defects or issues
- **Timeline risks**: Schedule impacts
- **Dependency risks**: External dependencies

## Enhanced Multiple Perspectives
Deep dive into each perspective:

### 👤 USER Perspective - Enhanced
- User journey mapping
- Accessibility considerations
- Error handling UX
- Performance expectations

### 🧭 CRITIC Perspective - Enhanced
- Failure mode analysis
- Edge case identification
- Security considerations
- Performance bottlenecks

### 🧰 OPS/DevOps Perspective - Enhanced
- Deployment strategy
- Monitoring requirements
- Maintenance procedures
- Rollback procedures

### 🐞 DEBUGGER Perspective - Enhanced
- Logging strategy
- Error tracking
- Debugging workflows
- Diagnostic capabilities

### 🚀 FUTURE Perspective - Enhanced
- Scalability planning
- Extension points
- Technology evolution
- Maintenance strategy

### 🤝 SDET Perspective - Enhanced
- Test strategy design
- Quality metrics
- Automation opportunities
- Validation approach

## Output Format (JSON)
{{
  "detailed_activities": [
    {{
      "activity_id": "activity_1",
      "enhanced_description": "More detailed description with specifics",
      "detailed_outcomes": {{
        "functional": ["User can authenticate", "JWT tokens issued"],
        "quality": ["Follows security best practices", "Code is maintainable"],
        "documentation": ["API docs updated", "Setup instructions"],
        "testing": ["Unit tests pass", "Integration tests pass"]
      }},
      "clarified_boundaries": {{
        "included": ["Core authentication", "Basic error handling"],
        "excluded": ["Advanced auth features", "Third-party integrations"],
        "negotiable": ["Additional validation", "Enhanced logging"],
        "dependencies": ["Database setup", "Configuration management"]
      }},
      "risk_assessment": {{
        "technical_risks": ["JWT library compatibility", "Database performance"],
        "quality_risks": ["Security vulnerabilities", "Edge case handling"],
        "timeline_risks": ["Testing complexity", "Debugging challenges"],
        "dependency_risks": ["External service availability"]
      }},
      "enhanced_perspectives": {{
        "user": "Enhanced user experience analysis...",
        "critic": "Detailed risk analysis...",
        "ops": "Operational considerations...",
        "debugger": "Debugging strategy...",
        "future": "Future-proofing approach...",
        "sdet": "Testing strategy..."
      }}
    }}
  ]
}}"""

    def _build_taskify_template(self) -> str:
        """Build template for task creation phase"""
        return """# ⚙️ TASK CREATION PHASE - Atomic Tasks with TDD

## Activity to Taskify
{activity_to_taskify}

## Task Creation Framework

### Test-Driven Development Pattern
For each activity, create tasks following Red-Green-Refactor:

1. **RED**: Write failing test
   - Define expected behavior
   - Create test structure
   - Verify test fails appropriately

2. **GREEN**: Implement minimal solution
   - Write just enough code to pass test
   - Focus on functionality first
   - Verify test passes

3. **REFACTOR**: Improve implementation
   - Enhance code quality
   - Add documentation
   - Optimize performance
   - Verify all tests still pass

### Task Structure
Each task should be:
- **Atomic**: Single responsibility
- **Testable**: Clear success criteria
- **Independent**: Minimal dependencies
- **Estimable**: Clear scope

### File Organization Strategy
- **Test files**: `tests/test_[feature].py`
- **Implementation files**: `src/[feature].py`
- **Configuration files**: `config/[feature].yml`
- **Documentation files**: `docs/[feature].md`

## Output Format (JSON)
{{
  "tasks": [
    {{
      "task_id": "task_1_1",
      "activity_id": "activity_1",
      "phase": "red",
      "description": "Write failing test for user authentication",
      "file_path": "tests/test_auth.py",
      "file_status": "new",
      "mode": "sdet",
      "dependencies": [],
      "current_state": "No authentication tests exist",
      "target_state": "Failing test exists that validates auth requirements",
      "test_criteria": [
        "Test file created",
        "Test fails with clear error message",
        "Test validates expected behavior"
      ],
      "implementation_steps": [
        "Create test file structure",
        "Write test for login functionality",
        "Run test to verify it fails appropriately"
      ]
    }},
    {{
      "task_id": "task_1_2",
      "activity_id": "activity_1",
      "phase": "green",
      "description": "Implement basic authentication functionality",
      "file_path": "src/auth.py",
      "file_status": "new",
      "mode": "coder",
      "dependencies": ["task_1_1"],
      "current_state": "Failing test exists",
      "target_state": "Authentication works and test passes",
      "test_criteria": [
        "Login functionality implemented",
        "JWT token generation works",
        "Test passes successfully"
      ],
      "implementation_steps": [
        "Implement login function",
        "Add JWT token creation",
        "Run test to verify it passes"
      ]
    }},
    {{
      "task_id": "task_1_3",
      "activity_id": "activity_1",
      "phase": "refactor",
      "description": "Improve authentication code quality",
      "file_path": "src/auth.py",
      "file_status": "existing",
      "mode": "coder",
      "dependencies": ["task_1_2"],
      "current_state": "Basic implementation works",
      "target_state": "Clean, maintainable, well-documented code",
      "test_criteria": [
        "Code follows best practices",
        "Documentation is complete",
        "Error handling is comprehensive",
        "All tests still pass"
      ],
      "implementation_steps": [
        "Add comprehensive error handling",
        "Improve code structure and naming",
        "Add detailed documentation",
        "Run all tests to ensure nothing broken"
      ]
    }}
  ]
}}"""

    def _build_execute_template(self) -> str:
        """Build template for execution phase"""
        return """# 🚀 EXECUTION PHASE - Implement Tasks

## Task to Execute
{task_to_execute}

## Execution Context
{execution_context}

## Implementation Framework

### Current State Analysis
- What exists now?
- What needs to be created/modified?
- What dependencies are needed?

### Target State Definition
- What should exist when done?
- What criteria define success?
- What quality standards must be met?

### Step-by-Step Implementation
Follow the detailed steps provided in the task definition while:
- Maintaining code quality standards
- Including proper error handling
- Adding appropriate documentation
- Following project conventions

### Validation Checklist
- [ ] Implementation matches requirements
- [ ] Code follows style guidelines
- [ ] Error handling is comprehensive
- [ ] Documentation is adequate
- [ ] Tests pass (if applicable)
- [ ] No regressions introduced

## Output Format
Provide the implementation following this structure:

```
## Implementation Summary
Brief description of what was implemented

## Files Modified/Created
- file1.py: Description of changes
- file2.py: Description of changes

## Code Changes
```python
# Actual code implementation
# Include all necessary imports, functions, classes
```

## Verification
- Tests run: [x] Pass | [ ] Fail
- Code quality: [x] Good | [ ] Needs improvement
- Documentation: [x] Complete | [ ] Incomplete

## Notes
Any additional considerations or follow-up items
```"""

    def build_phase_prompt(self, phase: WorkflowPhase, **kwargs) -> str:
        """Build prompt for specific workflow phase"""
        template = self.phase_templates[phase.value]

        # Format template with provided arguments
        try:
            return template.format(**kwargs)
        except KeyError as e:
            # Handle missing template variables gracefully
            missing_var = str(e).strip("'")
            return f"Template error: Missing required variable '{missing_var}'"

    def build_context_summary(self, context_history: List[ContextSummary]) -> str:
        """Build condensed context summary for prompts"""
        if not context_history:
            return "No previous context available."

        latest = context_history[-1]

        summary_parts = [
            "## Context Summary",
            f"**Token Budget:** {latest.token_budget} tokens",
            f"**Strategy:** {latest.compression_strategy}",
            "",
            "### Recent Activity",
            *latest.short_term_memory[-3:],  # Last 3 items
            "",
            "### Key Outcomes",
            *latest.medium_term_memory[-2:],  # Last 2 items
        ]

        return "\n".join(summary_parts)

    def build_perspective_analysis_prompt(self, activity: ActivityBreakdown) -> str:
        """Build prompt for multiple perspectives analysis"""
        perspectives_section = []

        for hat in PerspectiveHat:
            analysis = activity.perspectives.get(hat, "No analysis available")
            perspectives_section.extend(
                [f"### {hat.value.upper()} Perspective", analysis, ""]
            )

        return "\n".join(
            [
                "# 🎭 MULTIPLE PERSPECTIVES ANALYSIS",
                f"## Activity: {activity.name}",
                "",
                *perspectives_section,
                "## Synthesis",
                "How do these perspectives align or conflict?",
                "What trade-offs need to be considered?",
                "What is the recommended approach given all perspectives?",
            ]
        )
