from vivek.llm.models import LLMProvider
from vivek.utils.prompt_utils import PromptCompressor
from vivek.core.message_protocol import (
    execution_complete,
    clarification_needed,
)

import json
from typing import Any, Dict


class PlannerModel:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        # Compressed system prompt for token efficiency
        self.system_prompt = (
            "Planning Brain: Analyze requests, break into steps, choose modes "
            "(peer|architect|sdet|coder), review outputs. Respond in JSON format."
        )

    def analyze_request(self, user_input: str, context: str) -> Dict[str, Any]:
        """Analyze user request and return structured message to orchestrator.

        Returns:
            execution_complete message with task plan, OR
            clarification_needed message if requirements unclear
        """
        # Compress context if needed
        max_context_tokens = 2000  # Reserve tokens for system prompt and response
        compressed_context = PromptCompressor.truncate_context(
            context, max_context_tokens, strategy="summary"
        )

        prompt = f"""Task planning assistant: Analyze request and create work items.

Request: {user_input}
Context: {compressed_context}

Choose primary mode:
- peer: discussions, explanations, brainstorming
- architect: design patterns, system structure
- sdet: testing strategies, quality assurance
- coder: writing or modifying code

Break task into 1-5 work items with:
- mode: peer|architect|sdet|coder
- file_path: REAL existing path from context OR specific new path (use "console" for peer mode,
  don't invent paths)
- file_status: "new" or "existing"
- description: detailed, actionable prompt (e.g., "Implement function X with error handling",
  "Design component Y", "Test scenario Z")
- dependencies: array of 1-based work item numbers that must complete first
  (e.g., [1, 2] means item depends on items 1 and 2)

IMPORTANT:
- Use real file paths from context or logical new paths
- Dependencies are 1-based indices (first item is 1, not 0)
- Create appropriate number of items: simple tasks=1-2, complex=3-5

If requirements are unclear or ambiguous, output:
{{
  "needs_clarification": true,
  "questions": [{{"question": "...", "type": "choice", "options": [...]}}],
  "partial_plan": {{"description": "...", "mode": "..."}}
}}

Otherwise output (JSON only):
{{
  "description": "implement user authentication",
  "mode": "coder",
  "work_items": [
    {{
      "mode": "coder",
      "file_path": "src/auth.py",
      "file_status": "new",
      "description": "implement login with JWT tokens and error handling",
      "dependencies": []
    }}
  ],
  "priority": "normal"
}}"""

        response = self.provider.generate(prompt, temperature=0.1)
        return self._parse_task_plan(response)

    def review_output(
        self, task_description: str, executor_output: str
    ) -> Dict[str, Any]:
        """Review executor output and return structured message to orchestrator.

        Returns:
            execution_complete message with review result, OR
            clarification_needed message if requirements unclear
        """
        # Compress executor output if too long
        max_output_tokens = 1500
        compressed_output = PromptCompressor.truncate_context(
            executor_output, max_output_tokens, strategy="recent"
        )

        prompt = f"""Code reviewer: Evaluate output against task requirements.

TASK: {task_description}

OUTPUT: {compressed_output}

Evaluate:
- Completeness: All requirements addressed?
- Quality: Correct syntax, logic, error handling, documentation?
- Issues: Missing functionality, bugs, errors?

Decision: If score >= 0.7 AND complete → needs_iteration=false, else true

If requirements are UNCLEAR (task ambiguous, conflicting info), output:
{{"requirements_unclear": true, "unclear_points": [{{"question": "...", "type": "confirmation", "context": "..."}}],
  "quality_score": 0.6}}

Otherwise output (JSON only):
{{"quality_score": 0.85, "needs_iteration": false, "feedback": "implementation complete with error handling",
  "suggestions": ["add logging", "consider edge case X"]}}"""

        response = self.provider.generate(prompt, temperature=0.1)
        return self._parse_review(response)

    def _parse_task_plan(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and return structured message to orchestrator."""
        try:
            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1

            if start == -1 or end == 0:
                # No JSON found - return fallback
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            # Check if clarification needed
            if data.get("needs_clarification"):
                return clarification_needed(
                    questions=data.get("questions", []),
                    from_node="planner",
                    partial_plan=data.get("partial_plan", {})
                )

            # Parse work items
            work_items = []
            for item in data.get("work_items", []):
                work_items.append({
                    "mode": item.get("mode", "coder"),
                    "file_path": item.get("file_path", ""),
                    "file_status": item.get("file_status", "existing"),
                    "description": item.get("description", ""),
                    "dependencies": item.get("dependencies", [])
                })

            task_plan = {
                "description": data.get("description", ""),
                "mode": data.get("mode", "coder"),
                "work_items": work_items,
                "priority": data.get("priority", "normal"),
            }

            # Return execution_complete message
            return execution_complete(
                output=task_plan,
                from_node="planner",
                mode=task_plan["mode"],
                work_items_count=len(work_items),
                priority=task_plan["priority"]
            )

        except Exception as e:
            print(f"Error parsing task plan: {e}")
            # Return fallback as execution_complete for backward compatibility
            fallback_plan = {
                "description": "Code implementation task",
                "mode": "coder",
                "work_items": [{
                    "mode": "coder",
                    "file_path": "",
                    "file_status": "existing",
                    "description": "Implement the requested functionality",
                    "dependencies": []
                }],
                "priority": "normal",
            }
            return execution_complete(
                output=fallback_plan,
                from_node="planner",
                mode="coder",
                work_items_count=1,
                priority="normal",
                parse_error=str(e)
            )

    def _parse_review(self, response: str) -> Dict[str, Any]:
        """Parse review response and return structured message to orchestrator."""
        error_msg = None
        try:
            start = response.find("{")
            end = response.rfind("}") + 1

            if start == -1 or end == 0:
                # No JSON found
                raise ValueError("No JSON found in response")

            json_str = response[start:end]
            data = json.loads(json_str)

            # Check if requirements unclear (needs clarification)
            if data.get("requirements_unclear"):
                return clarification_needed(
                    questions=data.get("unclear_points", []),
                    from_node="reviewer",
                    current_quality=data.get("quality_score", 0.6)
                )

            # Normal review result
            review = {
                "quality_score": data.get("quality_score", 0.7),
                "needs_iteration": data.get("needs_iteration", False),
                "feedback": data.get("feedback", "Output looks good"),
                "suggestions": data.get("suggestions", []),
            }

            return execution_complete(
                output=review,
                from_node="reviewer",
                quality_score=review["quality_score"],
                needs_iteration=review["needs_iteration"]
            )

        except Exception as e:
            error_msg = str(e)
            print(f"Error parsing review: {error_msg}")

        # Fallback
        fallback_review = {
            "quality_score": 0.7,
            "needs_iteration": False,
            "feedback": "Review completed",
            "suggestions": [],
        }
        return execution_complete(
            output=fallback_review,
            from_node="reviewer",
            quality_score=0.7,
            needs_iteration=False,
            parse_error=error_msg
        )
