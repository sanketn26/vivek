import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import ollama

class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        pass

class OllamaProvider(LLMProvider):
    def __init__(self, model_name: str):
        self.model_name = model_name
        
    def generate(self, prompt: str, **kwargs) -> str:
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    "temperature": kwargs.get("temperature", 0.1),
                    "top_p": kwargs.get("top_p", 0.9),
                    "num_predict": kwargs.get("max_tokens", 2048)
                }
            )
            # Check if Ollama returned an error response
            if "error" in response:
                return f"Model error: {response['error']}"
            return response["response"]
        except Exception as e:
            return f"Error generating response: {str(e)}"

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

class ExecutorModel:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.mode_prompts = {
            "peer": """You are in Peer Programming mode. Be collaborative, explain your thinking, 
                     and engage in discussion. Focus on helping understand and solve problems together.""",
            "architect": """You are in Software Architect mode. Focus on design patterns, system structure,
                          scalability, and high-level architectural decisions. Think strategically.""",
            "sdet": """You are in SDET (Software Engineer in Test) mode. Focus on testing strategies,
                     test automation, quality assurance, and identifying potential issues.""",
            "coder": """You are in Coder mode. Focus on clean, efficient implementation. Write production-ready
                      code with proper error handling and documentation."""
        }

    def execute_task(self, task_plan: Dict[str, Any], context: str) -> str:
        mode_instruction = self.mode_prompts.get(task_plan["mode"], self.mode_prompts["coder"])

        prompt = f"""{mode_instruction}

Context: {context}
Task: {task_plan["description"]}
Mode: {task_plan["mode"]}
Priority: {task_plan["priority"]}

Steps to complete:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(task_plan["steps"]))}

Relevant files: {', '.join(task_plan["relevant_files"])}

Execute this task step by step. Provide clear, actionable output suitable for the {task_plan["mode"]} mode."""

        return self.provider.generate(prompt, temperature=0.2)