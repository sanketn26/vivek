from vivek.llm.models import LLMProvider
from vivek.utils.prompt_utils import TokenCounter, PromptCompressor

import json
from typing import Any, Dict


class PlannerModel:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        # Compressed system prompt for token efficiency
        self.system_prompt = (
            "Planning Brain: Analyze requests, break into steps, choose modes (peer|architect|sdet|coder), "
            "review outputs. Respond in JSON format."
        )

    def analyze_request(self, user_input: str, context: str) -> Dict[str, Any]:
        # Compress context if needed
        max_context_tokens = 2000  # Reserve tokens for system prompt and response
        compressed_context = PromptCompressor.truncate_context(
            context, max_context_tokens, strategy="summary"
        )

        prompt = f"""{self.system_prompt}

Context: {compressed_context}
Request: {user_input}

JSON: {{"description": "Brief task description", "mode": "peer|architect|sdet|coder", "steps": ["step1", "step2"], "relevant_files": ["file1.py"], "priority": "low|normal|high"}}"""

        response = self.provider.generate(prompt, temperature=0.1)
        return self._parse_task_plan(response)

    def review_output(
        self, task_description: str, executor_output: str
    ) -> Dict[str, Any]:
        # Compress executor output if too long
        max_output_tokens = 1500
        compressed_output = PromptCompressor.truncate_context(
            executor_output, max_output_tokens, strategy="recent"
        )

        prompt = f"""{self.system_prompt}

Task: {task_description}
Output: {compressed_output}

JSON: {{"quality_score": 0.8, "needs_iteration": false, "feedback": "Specific feedback", "suggestions": ["suggestion1"]}}"""

        response = self.provider.generate(prompt, temperature=0.1)
        return self._parse_review(response)

    def _parse_task_plan(self, response: str) -> Dict[str, Any]:
        try:
            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                return {
                    "description": data.get("description", ""),
                    "mode": data.get("mode", "coder"),
                    "steps": data.get(
                        "steps", ["Implement the requested functionality"]
                    ),
                    "relevant_files": data.get("relevant_files", []),
                    "priority": data.get("priority", "normal"),
                }
        except Exception as e:
            print(f"Error parsing task plan: {e}")

        # Fallback
        return {
            "description": "Code implementation task",
            "mode": "coder",
            "steps": ["Implement the requested functionality"],
            "relevant_files": [],
            "priority": "normal",
        }

    def _parse_review(self, response: str) -> Dict[str, Any]:
        try:
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                return {
                    "quality_score": data.get("quality_score", 0.7),
                    "needs_iteration": data.get("needs_iteration", False),
                    "feedback": data.get("feedback", "Output looks good"),
                    "suggestions": data.get("suggestions", []),
                }
        except Exception as e:
            print(f"Error parsing review: {e}")

        # Fallback
        return {
            "quality_score": 0.7,
            "needs_iteration": False,
            "feedback": "Review completed",
            "suggestions": [],
        }
