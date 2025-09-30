from vivek.llm.models import LLMProvider


import json
from typing import Any, Dict


class PlannerModel:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.system_prompt = """You are the Planning Brain of Vivek AI coding assistant.

Your responsibilities:
1. Understand user requests and break them into actionable steps
2. Choose the right mode (peer|architect|sdet|coder) for each task
3. Review outputs from the Executor Brain
4. Provide strategic guidance and context management

Respond in JSON format for structured communication."""

    def analyze_request(self, user_input: str, context: str) -> Dict[str, Any]:
        prompt = f"""{self.system_prompt}

Current Context: {context}
User Request: {user_input}

Analyze this request and respond with a JSON object containing:
{{
    "description": "Brief description of what needs to be done",
    "mode": "peer|architect|sdet|coder",
    "steps": ["step1", "step2", "step3"],
    "relevant_files": ["file1.py", "file2.py"],
    "priority": "low|normal|high"
}}

Focus on breaking down the task into specific, actionable steps."""

        response = self.provider.generate(prompt, temperature=0.1)
        return self._parse_task_plan(response)

    def review_output(self, task_description: str, executor_output: str) -> Dict[str, Any]:
        prompt = f"""{self.system_prompt}

Task: {task_description}
Executor Output:
{executor_output}

Review this output and respond with JSON:
{{
    "quality_score": 0.8,
    "needs_iteration": false,
    "feedback": "Specific feedback about the output",
    "suggestions": ["suggestion1", "suggestion2"]
}}

Evaluate code quality, completeness, and adherence to the task."""

        response = self.provider.generate(prompt, temperature=0.1)
        return self._parse_review(response)

    def _parse_task_plan(self, response: str) -> Dict[str, Any]:
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                return {
                    "description": data.get("description", ""),
                    "mode": data.get("mode", "coder"),
                    "steps": data.get("steps", ["Implement the requested functionality"]),
                    "relevant_files": data.get("relevant_files", []),
                    "priority": data.get("priority", "normal")
                }
        except Exception as e:
            print(f"Error parsing task plan: {e}")

        # Fallback
        return {
            "description": "Code implementation task",
            "mode": "coder",
            "steps": ["Implement the requested functionality"],
            "relevant_files": [],
            "priority": "normal"
        }

    def _parse_review(self, response: str) -> Dict[str, Any]:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                return {
                    "quality_score": data.get("quality_score", 0.7),
                    "needs_iteration": data.get("needs_iteration", False),
                    "feedback": data.get("feedback", "Output looks good"),
                    "suggestions": data.get("suggestions", [])
                }
        except Exception as e:
            print(f"Error parsing review: {e}")

        # Fallback
        return {
            "quality_score": 0.7,
            "needs_iteration": False,
            "feedback": "Review completed",
            "suggestions": []
        }