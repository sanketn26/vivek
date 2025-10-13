"""
Structured Executor for Vivek

This module implements an enhanced executor that follows the structured workflow
and TDD (Test-Driven Development) patterns for better code quality and reliability.
"""

import json
from typing import Dict, Any, List

from vivek.llm.models import LLMProvider
from vivek.core.message_protocol import (
    execution_complete,
    clarification_needed,
    error_occurred,
)
from vivek.core.structured_workflow import TaskDefinition, ContextSummary, WorkflowPhase
from vivek.core.prompt_templates import StructuredPromptBuilder


class StructuredExecutor:
    """
    Enhanced executor that follows structured workflow and TDD patterns.

    This executor understands the activity-task-test relationship and executes
    tasks with proper consideration of their position in the TDD workflow.
    """

    def __init__(self, provider: LLMProvider, mode: str = "coder"):
        self.provider = provider
        self.mode = mode
        self.prompt_builder = StructuredPromptBuilder()
        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Build system prompt based on executor mode"""
        mode_prompts = {
            "coder": """# STRUCTURED CODER EXECUTOR - TDD Pattern Implementation

You implement tasks following Test-Driven Development (TDD) principles:

## TDD Workflow Pattern
1. **RED Phase**: Execute failing tests (verify current state)
2. **GREEN Phase**: Implement minimal solution to pass tests
3. **REFACTOR Phase**: Improve code quality while maintaining tests

## Code Quality Standards
- Write clean, readable, maintainable code
- Include comprehensive error handling
- Add type hints and docstrings
- Follow language-specific best practices
- Consider edge cases and error conditions

## Task Execution Framework
- Execute tasks in dependency order
- Track current state vs target state
- Validate against test criteria
- Document implementation steps""",
            "architect": """# STRUCTURED ARCHITECT EXECUTOR - Design Pattern Implementation

You implement architectural tasks following structured design principles:

## Design Workflow Pattern
1. **ANALYZE**: Understand requirements and constraints
2. **DESIGN**: Create architectural solution
3. **VALIDATE**: Ensure design meets all criteria
4. **DOCUMENT**: Provide clear design documentation

## Architecture Quality Standards
- Consider multiple design options
- Evaluate trade-offs and make recommendations
- Define clear component responsibilities
- Plan for scalability and maintainability
- Address cross-cutting concerns""",
            "sdet": """# STRUCTURED SDET EXECUTOR - Quality Assurance Implementation

You implement testing tasks following quality assurance principles:

## Testing Workflow Pattern
1. **PLAN**: Define testing strategy and scope
2. **PREPARE**: Set up test environment and data
3. **EXECUTE**: Run tests and capture results
4. **ANALYZE**: Evaluate results and identify issues

## Testing Quality Standards
- Comprehensive test coverage
- Clear test organization and naming
- Proper setup and teardown procedures
- Meaningful assertions and error messages
- Test maintainability and reusability""",
            "peer": """# STRUCTURED PEER EXECUTOR - Collaborative Implementation

You facilitate collaborative development tasks:

## Collaboration Workflow Pattern
1. **UNDERSTAND**: Clarify requirements and context
2. **DISCUSS**: Explore different approaches
3. **RECOMMEND**: Provide balanced recommendations
4. **EXPLAIN**: Document reasoning and alternatives

## Collaboration Quality Standards
- Provide balanced, well-reasoned perspectives
- Consider multiple stakeholder viewpoints
- Explain technical concepts clearly
- Offer concrete next steps and recommendations""",
        }

        return mode_prompts.get(self.mode, mode_prompts["coder"])

    def execute_task(self, task_plan: Dict[str, Any], context: str) -> Dict[str, Any]:
        """
        Execute task with structured workflow awareness.

        Args:
            task_plan: Task plan with work items
            context: Context information

        Returns:
            Execution result with enhanced metadata
        """
        try:
            # Check for ambiguities before execution
            clarification_check = self._check_task_ambiguities(task_plan, context)
            if clarification_check:
                return clarification_needed(
                    questions=clarification_check["questions"],
                    from_node=f"structured_executor_{self.mode}",
                    task_context=task_plan,
                )

            # Execute work items following TDD pattern
            execution_results = self._execute_work_items_structurely(task_plan, context)

            # Extract metadata from execution
            metadata = self._extract_execution_metadata(execution_results, task_plan)

            return execution_complete(
                output=execution_results,
                from_node=f"structured_executor_{self.mode}",
                execution_metadata=metadata,
            )

        except Exception as e:
            return error_occurred(
                error=str(e),
                from_node=f"structured_executor_{self.mode}",
                task_plan=task_plan.get("description", "unknown"),
                mode=self.mode,
            )

    def _check_task_ambiguities(
        self, task_plan: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        """
        Check for ambiguities in task plan that need clarification.

        Returns:
            Dict with questions if clarification needed, None otherwise
        """
        work_items = task_plan.get("work_items", [])

        if not work_items:
            return {
                "questions": [
                    {
                        "question": "No work items found in task plan. Could you clarify what specific work should be done?",
                        "type": "clarification",
                        "context": "Task plan appears to be empty or malformed",
                    }
                ]
            }

        # Check for ambiguous file paths
        for item in work_items:
            file_path = item.get("file_path", "")
            if not file_path or file_path == "console":
                continue

            # If file path doesn't exist in context and isn't clearly new, ask for clarification
            if (
                item.get("file_status") != "new"
                and isinstance(context, dict)
                and "existing_files" in context
            ):

                existing_files = context.get("existing_files", [])
                if isinstance(existing_files, list) and file_path not in existing_files:
                    return {
                        "questions": [
                            {
                                "question": f"Could you clarify the file path '{file_path}'? Should this be a new file or modify an existing one?",
                                "type": "choice",
                                "options": [
                                    "New file",
                                    "Modify existing file",
                                    "Different path",
                                ],
                            }
                        ]
                    }

        return {}

    def _execute_work_items_structurely(
        self, task_plan: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        """
        Execute work items following structured TDD approach.

        Returns:
            Structured execution results with TDD phase tracking
        """
        work_items = task_plan.get("work_items", [])
        execution_results = {
            "task_description": task_plan.get("description", ""),
            "mode": self.mode,
            "work_items_executed": [],
            "tdd_phases": {},
            "overall_status": "completed",
        }

        # Group work items by TDD phase if they have phase information
        for item in work_items:
            item_result = self._execute_single_work_item(item, context)
            execution_results["work_items_executed"].append(item_result)

            # Track TDD phases
            phase = item.get("phase", "implement")
            if phase not in execution_results["tdd_phases"]:
                execution_results["tdd_phases"][phase] = []
            execution_results["tdd_phases"][phase].append(item_result)

        return execution_results

    def _execute_single_work_item(
        self, work_item: Dict[str, Any], context: str
    ) -> Dict[str, Any]:
        """
        Execute a single work item with TDD awareness.

        Args:
            work_item: Individual work item to execute
            context: Context information

        Returns:
            Execution result for the work item
        """
        item_id = work_item.get("task_id", "unknown")
        description = work_item.get("description", "")
        phase = work_item.get("phase", "implement")

        # Build TDD-aware prompt
        prompt = self._build_tdd_aware_prompt(work_item, context)

        # Execute with appropriate temperature based on phase
        temperature = self._get_temperature_for_phase(phase)
        output = self.provider.generate(prompt, temperature=temperature)

        # Parse output and validate against test criteria
        validation_result = self._validate_output_against_criteria(output, work_item)

        return {
            "item_id": item_id,
            "description": description,
            "phase": phase,
            "output": output,
            "validation": validation_result,
            "status": validation_result.get("status", "completed"),
            "implementation_steps": work_item.get("implementation_steps", []),
        }

    def _build_tdd_aware_prompt(self, work_item: Dict[str, Any], context: str) -> str:
        """Build prompt that is aware of TDD phase and requirements"""
        phase = work_item.get("phase", "implement")
        current_state = work_item.get("current_state", "")
        target_state = work_item.get("target_state", "")
        test_criteria = work_item.get("test_criteria", [])

        # Build phase-specific instructions
        phase_instructions = self._get_phase_specific_instructions(phase, work_item)

        # Include TDD context
        tdd_context = f"""
## TDD Context
- **Current State**: {current_state}
- **Target State**: {target_state}
- **Test Criteria**: {json.dumps(test_criteria, indent=2)}
- **Dependencies**: {work_item.get("dependencies", [])}
"""

        # Build the complete prompt
        prompt = f"""{self.system_prompt}

## Task Information
- **Description**: {work_item.get("description", "")}
- **File Path**: {work_item.get("file_path", "")}
- **Mode**: {work_item.get("mode", self.mode)}

## Context
{context}

{tdd_context}

{phase_instructions}

## Output Format
{self._get_output_format_for_phase(phase)}

Begin execution:"""

        return prompt

    def _get_phase_specific_instructions(
        self, phase: str, work_item: Dict[str, Any]
    ) -> str:
        """Get instructions specific to TDD phase"""
        phase_guides = {
            "red": """## RED Phase: Write Failing Test
Focus on creating tests that validate the expected behavior:

1. **Test Structure**: Create proper test file structure
2. **Test Cases**: Write tests that should fail initially
3. **Assertions**: Include clear, meaningful assertions
4. **Coverage**: Test the specific functionality described

Execute the failing test to verify it fails as expected.""",
            "green": """## GREEN Phase: Implement Minimal Solution
Focus on making tests pass with minimal implementation:

1. **Minimal Code**: Write just enough code to pass tests
2. **No Over-engineering**: Avoid unnecessary features or optimizations
3. **Test Validation**: Ensure all test criteria are met
4. **Quick Feedback**: Run tests frequently to validate progress

The goal is working functionality, not perfect code.""",
            "refactor": """## REFACTOR Phase: Improve Code Quality
Focus on improving code while maintaining functionality:

1. **Code Quality**: Improve structure, naming, and organization
2. **Documentation**: Add clear comments and docstrings
3. **Error Handling**: Enhance error handling and edge cases
4. **Performance**: Consider performance implications
5. **Test Preservation**: Ensure all tests still pass

Maintain the same external behavior while improving internal quality.""",
            "implement": """## IMPLEMENT Phase: Standard Implementation
Follow best practices for the specified mode:

1. **Requirements**: Address all requirements in the task
2. **Quality**: Follow language and mode-specific best practices
3. **Testing**: Ensure functionality works as expected
4. **Documentation**: Include necessary documentation

Focus on delivering working, maintainable code.""",
        }

        return phase_guides.get(phase, phase_guides["implement"])

    def _get_temperature_for_phase(self, phase: str) -> float:
        """Get appropriate temperature for TDD phase"""
        temperature_map = {
            "red": 0.1,  # Low temperature for predictable test writing
            "green": 0.2,  # Slightly higher for implementation
            "refactor": 0.3,  # Higher creativity for refactoring
            "implement": 0.2,  # Standard implementation temperature
        }
        return temperature_map.get(phase, 0.2)

    def _get_output_format_for_phase(self, phase: str) -> str:
        """Get output format for TDD phase"""
        base_format = """
## Implementation Result
- **Phase**: {phase}
- **Status**: Complete/Incomplete with issues

## Code Changes
```python
# Implementation goes here
# Include all necessary imports, functions, classes
```

## Validation
- **Test Results**: All tests pass/failures noted
- **Requirements Met**: Yes/No with details
- **Quality Check**: Follows best practices

## Next Steps
- Ready for next phase: Yes/No
- Dependencies resolved: Yes/No
- Additional work needed: Details"""

        return base_format.format(phase=phase)

    def _validate_output_against_criteria(
        self, output: str, work_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate output against test criteria"""
        test_criteria = work_item.get("test_criteria", [])

        validation = {
            "status": "completed",
            "criteria_met": [],
            "criteria_failed": [],
            "overall_score": 1.0,
        }

        # Simple validation - in real implementation, this would run actual tests
        for criterion in test_criteria:
            # This is a simplified validation
            # In practice, would run tests or analyze output more thoroughly
            if any(
                keyword in output.lower()
                for keyword in ["error", "fail", "exception", "not implemented"]
            ):
                validation["criteria_failed"].append(criterion)
                validation["overall_score"] *= 0.8
            else:
                validation["criteria_met"].append(criterion)

        if validation["criteria_failed"]:
            validation["status"] = "needs_review"

        return validation

    def _extract_execution_metadata(
        self, execution_results: Dict[str, Any], task_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract metadata from execution results"""
        work_items = task_plan.get("work_items", [])
        executed_items = execution_results.get("work_items_executed", [])

        # Count successful executions
        successful_items = sum(
            1 for item in executed_items if item.get("status") == "completed"
        )
        failed_items = len(executed_items) - successful_items

        return {
            "total_work_items": len(work_items),
            "executed_items": len(executed_items),
            "successful_items": successful_items,
            "failed_items": failed_items,
            "tdd_phases_used": list(execution_results.get("tdd_phases", {}).keys()),
            "execution_mode": self.mode,
            "structured_execution": True,
        }




def get_structured_executor(mode: str, provider: LLMProvider) -> StructuredExecutor:
    """
    Factory function to create structured executor for specific mode.

    Args:
        mode: Execution mode (coder, architect, peer, sdet)
        provider: LLM provider instance

    Returns:
        StructuredExecutor instance for the specified mode
    """
    return StructuredExecutor(provider, mode)
