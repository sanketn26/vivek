"""
Structured Planner for Vivek

This module implements a new planner that follows the structured workflow
architecture, providing clear separation between understanding, decomposition,
detailing, and task creation phases.
"""

import json
import time
from typing import Dict, Any, List, Optional

from vivek.llm.models import LLMProvider
from vivek.core.message_protocol import (
    execution_complete,
    clarification_needed,
)
from vivek.core.structured_workflow import (
    StructuredWorkflow,
    WorkflowPhase,
    ActivityBreakdown,
    TaskDefinition,
    ContextSummary,
)
from vivek.core.prompt_templates import StructuredPromptBuilder
from vivek.core.context_condensation import ProgressiveContextManager, ContextType


class StructuredPlannerModel:
    """Planner that follows structured engineering workflow"""

    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.workflow = StructuredWorkflow()
        self.prompt_builder = StructuredPromptBuilder()
        self.context_manager = ProgressiveContextManager()
        self.system_prompt = (
            "You are a senior software engineer and technical lead guiding a development project. "
            "Follow structured engineering practices: understand requirements, decompose into activities, "
            "detail each activity from multiple perspectives, and create atomic tasks following TDD. "
            "Always respond in JSON format."
        )

    def analyze_request(self, user_input: str, context: str) -> Dict[str, Any]:
        """Analyze request using structured workflow approach"""
        # Phase 1: Understand the task
        understanding = self._phase_understand(user_input, context)

        # Check if clarification needed
        if understanding.get("needs_clarification"):
            return clarification_needed(
                questions=understanding.get("clarification_questions", []),
                from_node="structured_planner",
                understanding=understanding,
            )

        # Phase 2: Decompose into activities
        activities = self._phase_decompose(understanding, context)

        # Phase 3: Detail activities with multiple perspectives
        detailed_activities = self._phase_detail(activities, context)

        # Phase 4: Create atomic tasks
        tasks = self._phase_taskify(detailed_activities, context)

        # Create structured task plan
        task_plan = self._create_task_plan(understanding, detailed_activities, tasks)

        # Add to context history
        self._update_context_history(understanding, activities, tasks)

        return execution_complete(
            output=task_plan,
            from_node="structured_planner",
            mode=task_plan.get("primary_mode", "coder"),
            work_items_count=len(tasks),
            understanding=understanding,
            activities_count=len(activities),
        )

    def _phase_understand(self, user_input: str, context: str) -> Dict[str, Any]:
        """Phase 1: Understand task and clarify scope"""
        # Build context summary
        context_summary = self.prompt_builder.build_context_summary(
            self.context_manager.context_history
        )

        # Build understanding prompt
        prompt = self.prompt_builder.build_phase_prompt(
            WorkflowPhase.UNDERSTAND,
            context_summary=context_summary,
            user_input=user_input,
        )

        response = self.provider.generate(prompt, temperature=0.1)
        return self._parse_understanding_response(response)

    def _phase_decompose(
        self, understanding: Dict[str, Any], context: str
    ) -> List[ActivityBreakdown]:
        """Phase 2: Decompose into high-level activities"""
        # Use workflow to generate activities
        activities = self.workflow.decompose_activities(understanding)

        # Enhance with LLM if needed for complex decomposition
        if self._requires_llm_decomposition(understanding):
            activities = self._enhance_decomposition_with_llm(
                activities, understanding, context
            )

        return activities

    def _phase_detail(
        self, activities: List[ActivityBreakdown], context: str
    ) -> List[ActivityBreakdown]:
        """Phase 3: Detail activities with multiple perspectives"""
        detailed_activities = []

        for activity in activities:
            # Use workflow to detail activity
            detailed_activity = self.workflow.detail_activities([activity])[0]

            # Enhance with LLM for complex perspective analysis
            if self._requires_deep_perspective_analysis(activity):
                detailed_activity = self._enhance_perspective_analysis(
                    detailed_activity, context
                )

            detailed_activities.append(detailed_activity)

        return detailed_activities

    def _phase_taskify(
        self, activities: List[ActivityBreakdown], context: str
    ) -> List[TaskDefinition]:
        """Phase 4: Convert activities into atomic tasks"""
        # Use workflow to create tasks
        all_tasks = []
        for activity in activities:
            tasks = self.workflow.create_tasks([activity])
            all_tasks.extend(tasks)

        # Enhance tasks with LLM if needed
        if self._requires_llm_task_refinement(all_tasks):
            all_tasks = self._enhance_tasks_with_llm(all_tasks, context)

        return all_tasks

    def _parse_understanding_response(self, response: str) -> Dict[str, Any]:
        """Parse understanding phase response"""
        try:
            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            # Validate structure
            if not isinstance(data, dict):
                raise ValueError("Response is not a valid object")

            return {
                "understanding_complete": data.get("understanding_complete", False),
                "needs_clarification": data.get("needs_clarification", False),
                "core_intent": data.get("core_intent", ""),
                "scope_definition": data.get("scope_definition", {}),
                "assumptions": data.get("assumptions", []),
                "success_criteria": data.get("success_criteria", []),
                "clarification_questions": data.get("clarification_questions", []),
            }

        except Exception as e:
            # Fallback understanding
            return {
                "understanding_complete": False,
                "needs_clarification": True,
                "core_intent": "Unable to determine intent from request",
                "scope_definition": {"in_scope": [], "out_of_scope": []},
                "assumptions": ["Request needs clarification"],
                "success_criteria": ["Requirements are clarified"],
                "clarification_questions": [
                    {
                        "question": "Could you provide more details about what you'd like to accomplish?",
                        "type": "open_ended",
                    }
                ],
            }

    def _requires_llm_decomposition(self, understanding: Dict[str, Any]) -> bool:
        """Check if LLM enhancement needed for decomposition"""
        # Simple heuristic: complex requests need LLM enhancement
        intent = understanding.get("core_intent", "")
        return len(intent) > 100 or len(understanding.get("success_criteria", [])) > 3

    def _enhance_decomposition_with_llm(
        self,
        activities: List[ActivityBreakdown],
        understanding: Dict[str, Any],
        context: str,
    ) -> List[ActivityBreakdown]:
        """Enhance activity decomposition with LLM"""
        # Build decomposition prompt
        activity_names = [a.name for a in activities]
        understanding_summary = json.dumps(
            {
                "core_intent": understanding.get("core_intent", ""),
                "scope": understanding.get("scope_definition", {}),
                "success_criteria": understanding.get("success_criteria", []),
            },
            indent=2,
        )

        prompt = self.prompt_builder.build_phase_prompt(
            WorkflowPhase.DECOMPOSE,
            understanding_summary=understanding_summary,
            current_activities=activity_names,
        )

        response = self.provider.generate(prompt, temperature=0.2)

        # Parse and merge with existing activities
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > 0:
                json_str = response[start:end]
                data = json.loads(json_str)

                if "activities" in data:
                    # Create enhanced activities from LLM response
                    enhanced_activities = []
                    for activity_data in data["activities"]:
                        # Find matching existing activity or create new
                        existing = next(
                            (
                                a
                                for a in activities
                                if a.name == activity_data.get("name", "")
                            ),
                            None,
                        )

                        if existing:
                            # Enhance existing activity
                            enhanced = ActivityBreakdown(
                                activity_id=existing.activity_id,
                                name=activity_data.get("name", existing.name),
                                description=activity_data.get(
                                    "description", existing.description
                                ),
                                expected_outcomes=activity_data.get(
                                    "expected_outcomes", existing.expected_outcomes
                                ),
                                boundaries=activity_data.get(
                                    "boundaries", existing.boundaries
                                ),
                                dependencies=activity_data.get(
                                    "dependencies", existing.dependencies
                                ),
                                perspectives=activity_data.get(
                                    "perspectives", existing.perspectives
                                ),
                            )
                            enhanced_activities.append(enhanced)
                        else:
                            # Create new activity
                            new_activity = ActivityBreakdown(
                                activity_id=f"activity_{len(enhanced_activities)+1}",
                                name=activity_data["name"],
                                description=activity_data.get("description", ""),
                                expected_outcomes=activity_data.get(
                                    "expected_outcomes", []
                                ),
                                boundaries=activity_data.get("boundaries", []),
                                dependencies=activity_data.get("dependencies", []),
                            )
                            enhanced_activities.append(new_activity)

                    return enhanced_activities

        except Exception as e:
            print(f"Error enhancing decomposition: {e}")

        return activities  # Return original if enhancement fails

    def _requires_deep_perspective_analysis(self, activity: ActivityBreakdown) -> bool:
        """Check if activity needs deep perspective analysis"""
        # Activities with high complexity or broad impact need deeper analysis
        complexity_indicators = [
            "system",
            "architecture",
            "platform",
            "integration",
            "security",
            "performance",
        ]

        description_lower = activity.description.lower()
        return any(
            indicator in description_lower for indicator in complexity_indicators
        )

    def _enhance_perspective_analysis(
        self, activity: ActivityBreakdown, context: str
    ) -> ActivityBreakdown:
        """Enhance activity with deep perspective analysis"""
        # Build perspective analysis prompt
        prompt = self.prompt_builder.build_perspective_analysis_prompt(activity)

        response = self.provider.generate(prompt, temperature=0.2)

        try:
            # Extract perspective analysis from response
            # This would parse the LLM response for perspective insights
            # For now, return original activity
            return activity

        except Exception as e:
            print(f"Error enhancing perspective analysis: {e}")
            return activity

    def _requires_llm_task_refinement(self, tasks: List[TaskDefinition]) -> bool:
        """Check if tasks need LLM refinement"""
        # Complex projects or interdependent tasks benefit from LLM refinement
        return len(tasks) > 5 or self._has_complex_dependencies(tasks)

    def _has_complex_dependencies(self, tasks: List[TaskDefinition]) -> bool:
        """Check if tasks have complex dependency patterns"""
        for task in tasks:
            if len(task.dependencies) > 2:
                return True
        return False

    def _enhance_tasks_with_llm(
        self, tasks: List[TaskDefinition], context: str
    ) -> List[TaskDefinition]:
        """Enhance tasks with LLM refinement"""
        # For now, return original tasks
        # In full implementation, this would use LLM to refine task structure
        return tasks

    def _create_task_plan(
        self,
        understanding: Dict[str, Any],
        activities: List[ActivityBreakdown],
        tasks: List[TaskDefinition],
    ) -> Dict[str, Any]:
        """Create structured task plan from workflow results"""
        # Determine primary mode based on activities and tasks
        primary_mode = self._determine_primary_mode(tasks)

        # Convert tasks to work items format expected by existing system
        work_items = []
        for task in tasks:
            work_item = {
                "mode": task.mode,
                "file_path": task.file_path,
                "file_status": task.file_status,
                "description": task.description,
                "dependencies": task.dependencies,
                "task_id": task.task_id,
                "phase": getattr(task, "phase", "implement"),
                "test_criteria": task.test_criteria,
                "current_state": task.current_state,
                "target_state": task.target_state,
            }
            work_items.append(work_item)

        return {
            "description": understanding.get("core_intent", ""),
            "mode": primary_mode,
            "work_items": work_items,
            "priority": "normal",
            "structured_workflow": {
                "understanding": understanding,
                "activities_count": len(activities),
                "tasks_count": len(tasks),
                "phases": [
                    phase.value
                    for phase in [
                        WorkflowPhase.UNDERSTAND,
                        WorkflowPhase.DECOMPOSE,
                        WorkflowPhase.DETAIL,
                        WorkflowPhase.TASKIFY,
                    ]
                ],
            },
        }

    def _determine_primary_mode(self, tasks: List[TaskDefinition]) -> str:
        """Determine primary mode based on task types"""
        mode_counts = {}
        for task in tasks:
            mode = task.mode
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

        # Return most common mode
        return (
            max(mode_counts.items(), key=lambda x: x[1])[0] if mode_counts else "coder"
        )

    def _update_context_history(
        self,
        understanding: Dict[str, Any],
        activities: List[ActivityBreakdown],
        tasks: List[TaskDefinition],
    ):
        """Update context history with current work"""
        # Add understanding to context
        self.context_manager.add_context_item(
            content=f"Understanding: {understanding.get('core_intent', '')}",
            context_type=ContextType.DECISION,
            importance=0.8,
            source="structured_planner",
            tags=["understanding", "planning"],
        )

        # Add activities to context
        for activity in activities:
            self.context_manager.add_context_item(
                content=f"Activity: {activity.name}",
                context_type=ContextType.ACTION,
                importance=0.7,
                source="structured_planner",
                tags=["activity", activity.activity_id],
            )

        # Add high-level tasks to context
        for task in tasks[:3]:  # Limit to first 3 tasks to avoid overflow
            self.context_manager.add_context_item(
                content=f"Task: {task.description}",
                context_type=ContextType.ACTION,
                importance=0.6,
                source="structured_planner",
                tags=["task", task.task_id],
            )

    def review_output(
        self, task_description: str, executor_output: str
    ) -> Dict[str, Any]:
        """Review executor output using structured approach"""
        # Use context manager to get relevant context
        context_summary = self.context_manager.get_condensed_context(strategy="recent")

        # Build review prompt with structured approach
        review_prompt = self._build_structured_review_prompt(
            task_description, executor_output, context_summary
        )

        response = self.provider.generate(review_prompt, temperature=0.1)

        return self._parse_review_response(response)

    def _build_structured_review_prompt(
        self,
        task_description: str,
        executor_output: str,
        context_summary: ContextSummary,
    ) -> str:
        """Build structured review prompt"""
        return f"""# 🔍 STRUCTURED OUTPUT REVIEW

## Context Summary
**Recent Memory:** {' | '.join(context_summary.short_term_memory)}
**Key Outcomes:** {' | '.join(context_summary.medium_term_memory)}

## Task Description
{task_description}

## Executor Output
{executor_output}

## Review Framework

### 1. Completion Check
- Does the output address all requirements in the task description?
- Are all specified features implemented?
- Are all dependencies satisfied?

### 2. Quality Assessment
- Code quality: Follows best practices, readable, maintainable?
- Error handling: Comprehensive and appropriate?
- Documentation: Adequate comments and docstrings?
- Testing: Test criteria met?

### 3. Multiple Perspectives Review
**👤 USER:** Does this provide good user experience?
**🧭 CRITIC:** Are there issues, bugs, or weaknesses?
**🧰 OPS:** Is this deployable and maintainable?
**🐞 DEBUGGER:** Will this be easy to troubleshoot?
**🚀 FUTURE:** Does this support future needs?
**🤝 SDET:** Is this testable and reliable?

### 4. Success Criteria Validation
Check against original success criteria:
- Functional requirements met?
- Quality standards achieved?
- Performance expectations satisfied?

## Output Format (JSON)
{{
  "quality_score": 0.85,
  "needs_iteration": false,
  "completion_check": {{
    "requirements_addressed": true,
    "features_implemented": true,
    "dependencies_satisfied": true
  }},
  "quality_assessment": {{
    "code_quality": "Good",
    "error_handling": "Comprehensive",
    "documentation": "Adequate",
    "testing": "Test criteria met"
  }},
  "perspectives_review": {{
    "user": "Good UX provided",
    "critic": "No major issues found",
    "ops": "Deployable and maintainable",
    "debugger": "Easy to troubleshoot",
    "future": "Supports future needs",
    "sdet": "Testable and reliable"
  }},
  "success_criteria_met": true,
  "feedback": "Implementation looks solid with good quality",
  "suggestions": ["Minor improvements", "Consider edge cases"]
}}"""

    def _parse_review_response(self, response: str) -> Dict[str, Any]:
        """Parse structured review response"""
        try:
            start = response.find("{")
            end = response.rfind("}") + 1

            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            # Extract review components
            quality_score = data.get("quality_score", 0.7)
            needs_iteration = data.get("needs_iteration", False)
            feedback = data.get("feedback", "Review completed")
            suggestions = data.get("suggestions", [])

            return execution_complete(
                output={
                    "quality_score": quality_score,
                    "needs_iteration": needs_iteration,
                    "feedback": feedback,
                    "suggestions": suggestions,
                    "structured_review": data,  # Include full structured review
                },
                from_node="structured_planner",
                quality_score=quality_score,
                needs_iteration=needs_iteration,
            )

        except Exception as e:
            print(f"Error parsing review: {e}")
            # Fallback review
            return execution_complete(
                output={
                    "quality_score": 0.7,
                    "needs_iteration": False,
                    "feedback": "Review completed with fallback scoring",
                    "suggestions": [],
                },
                from_node="structured_planner",
                quality_score=0.7,
                needs_iteration=False,
                parse_error=str(e),
            )
