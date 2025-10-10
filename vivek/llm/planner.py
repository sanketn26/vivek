from vivek.llm.models import LLMProvider
from vivek.utils.prompt_utils import PromptCompressor
from vivek.core.message_protocol import (
    execution_complete,
    clarification_needed,
)

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


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

        prompt = f"""You are a task planner. Your response MUST be ONLY valid JSON, nothing else.

Request: {user_input}
Context: {compressed_context}

Modes: peer (discussion), architect (design), sdet (testing), coder (code)

If unclear, output THIS EXACT JSON structure:
{{"needs_clarification": true, "questions": [{{"question": "your question", "type": "choice", "options": ["option1", "option2"]}}], "partial_plan": {{"description": "summary", "mode": "coder"}}}}

Otherwise, output THIS EXACT JSON structure (replace placeholders with actual values):
{{"description": "task summary", "mode": "coder", "work_items": [{{"mode": "coder", "file_path": "path/to/file.ext", "file_status": "new", "description": "detailed task", "dependencies": []}}], "priority": "normal"}}

Rules:
- MUST output valid JSON only
- NO explanations, NO markdown, NO text before or after JSON
- Use 1-5 work items
- file_status: "new" or "existing"
- dependencies: array of integers (1-based indices)

Output ONLY the JSON now:"""

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

        prompt = f"""You are a code reviewer. Your response MUST be ONLY valid JSON, nothing else.

TASK: {task_description}
OUTPUT: {compressed_output}

Evaluate: completeness, quality, correctness. Score 0.0-1.0.

If requirements unclear, output THIS EXACT JSON:
{{"requirements_unclear": true, "unclear_points": [{{"question": "clarifying question", "type": "confirmation", "context": "context"}}], "quality_score": 0.6}}

Otherwise output THIS EXACT JSON (replace values):
{{"quality_score": 0.85, "needs_iteration": false, "feedback": "brief summary", "suggestions": ["suggestion 1", "suggestion 2"]}}

Rules:
- MUST output valid JSON only
- NO explanations, NO markdown, NO text
- quality_score: 0.0 to 1.0
- needs_iteration: true if score < 0.7 or incomplete

Output ONLY the JSON now:"""

        response = self.provider.generate(prompt, temperature=0.1)
        return self._parse_review(response)

    def _parse_task_plan(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and return structured message to orchestrator."""
        try:
            # Debug: Print response info
            print(f"DEBUG: Response type: {type(response)}")
            print(f"DEBUG: Response length: {len(response) if response else 0}")
            print(f"DEBUG: Response preview: {response[:200] if response else 'EMPTY'}")

            # Check if response is empty
            if not response or not response.strip():
                print("ERROR: Received empty response from LLM")
                raise ValueError("Empty response from LLM")

            # Strip <think> tags if present (for thinking models like qwen3-4b-thinking)
            if "<think>" in response:
                # Find the end of the thinking section
                think_end = response.find("</think>")
                if think_end != -1:
                    # Get content after </think>
                    response = response[think_end + len("</think>"):].strip()
                    print(f"DEBUG: Stripped <think> tags, remaining length: {len(response)}")
                    print(f"DEBUG: Content after think: {response[:200]}")

            # First, try to parse the entire response as JSON (for test mocks)
            try:
                data = json.loads(response.strip())
            except json.JSONDecodeError as e1:
                print(f"DEBUG: Direct JSON parse failed: {e1}")
                # If that fails, extract JSON from response (for real LLM responses)
                start = response.find("{")
                end = response.rfind("}") + 1

                if start == -1 or end == 0:
                    # No JSON found - return fallback
                    print(f"ERROR: No JSON found in response")
                    print(f"Full response: {response}")
                    raise ValueError("No JSON found in response")

                json_str = response[start:end]
                print(f"DEBUG: Extracted JSON string length: {len(json_str)}")
                print(f"DEBUG: Extracted JSON (first 500 chars): {json_str[:500]}")
                try:
                    data = json.loads(json_str)
                except json.JSONDecodeError as e2:
                    print(f"ERROR: Failed to parse extracted JSON: {e2}")
                    print(f"Problematic JSON: {json_str}")
                    raise

            # Check if clarification needed
            if data.get("needs_clarification"):
                return clarification_needed(
                    questions=data.get("questions", []),
                    from_node="planner",
                    partial_plan=data.get("partial_plan", {}),
                )

            # Parse work items
            work_items = []
            for item in data.get("work_items", []):
                work_items.append(
                    {
                        "mode": item.get("mode", "coder"),
                        "file_path": item.get("file_path", ""),
                        "file_status": item.get("file_status", "existing"),
                        "description": item.get("description", ""),
                        "dependencies": item.get("dependencies", []),
                    }
                )

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
                priority=task_plan["priority"],
            )

        except Exception as e:
            logger.error(f"Error parsing task plan: {e}", exc_info=True)
            # Return fallback as execution_complete for backward compatibility
            fallback_plan = {
                "description": "Code implementation task",
                "mode": "coder",
                "work_items": [
                    {
                        "mode": "coder",
                        "file_path": "",
                        "file_status": "existing",
                        "description": "Implement the requested functionality",
                        "dependencies": [],
                    }
                ],
                "priority": "normal",
            }
            return execution_complete(
                output=fallback_plan,
                from_node="planner",
                mode="coder",
                work_items_count=1,
                priority="normal",
                parse_error=str(e),
            )

    def _parse_review(self, response: str) -> Dict[str, Any]:
        """Parse review response and return structured message to orchestrator."""
        error_msg = None
        try:
            # Debug: Print response info
            print(f"DEBUG REVIEW: Response type: {type(response)}")
            print(f"DEBUG REVIEW: Response length: {len(response) if response else 0}")
            print(f"DEBUG REVIEW: Response preview: {response[:200] if response else 'EMPTY'}")

            # Check if response is empty
            if not response or not response.strip():
                print("ERROR: Received empty response from LLM in review")
                raise ValueError("Empty response from LLM")

            # Strip <think> tags if present (for thinking models like qwen3-4b-thinking)
            if "<think>" in response:
                # Find the end of the thinking section
                think_end = response.find("</think>")
                if think_end != -1:
                    # Get content after </think>
                    response = response[think_end + len("</think>"):].strip()
                    print(f"DEBUG REVIEW: Stripped <think> tags, remaining length: {len(response)}")
                    print(f"DEBUG REVIEW: Content after think: {response[:200]}")

            # First, try to parse the entire response as JSON (for test mocks)
            try:
                data = json.loads(response.strip())
            except json.JSONDecodeError:
                # If that fails, extract JSON from response (for real LLM responses)
                start = response.find("{")
                end = response.rfind("}") + 1

                if start == -1 or end == 0:
                    # No JSON found
                    print(f"ERROR: No JSON found in review response: {response[:500]}")
                    raise ValueError("No JSON found in response")

                json_str = response[start:end]
                data = json.loads(json_str)

            # Check if requirements unclear (needs clarification)
            if data.get("requirements_unclear"):
                return clarification_needed(
                    questions=data.get("unclear_points", []),
                    from_node="reviewer",
                    current_quality=data.get("quality_score", 0.6),
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
                needs_iteration=review["needs_iteration"],
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error parsing review: {error_msg}", exc_info=True)

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
            parse_error=error_msg,
        )
