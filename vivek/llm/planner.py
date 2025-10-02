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

        prompt = f"""You are a task planning assistant. Analyze the request and create detailed work items.

## STEP 1: Understand the Request
Request: {user_input}
Context: {compressed_context}

## STEP 2: Determine Overall Mode
Choose primary mode for this task:
- peer: For discussions, explanations, brainstorming, consulting
- architect: For design patterns, system structure, architecture
- sdet: For testing strategies, quality assurance, test automation
- coder: For writing or modifying code

## STEP 3: Create Work Items
Break the task into 1-5 work items. For EACH work item specify:

### Work Item Structure:
- mode: Specific mode for this item (peer|architect|sdet|coder)
- file_path: EXACT file path (e.g., "src/module/file.py" or "docs/design.md")
  * Use "console" for peer/consulting mode (no file output)
  * Use "docs/architecture.md" for architecture diagrams
  * Use "tests/test_feature.py" for tests
- file_status: "new" (create new file) or "existing" (modify existing)
- description: DETAILED prompt describing what to do with this file
  * For coder: "Implement function X in file Y that does Z with error handling"
  * For architect: "Design component diagram for X showing Y and Z"
  * For sdet: "Write tests for function X covering happy path, edge cases A, B"
  * For peer: "Explain concept X with examples and trade-offs"
- dependencies: List of other work item indices this depends on (optional)

## STEP 4: Validate Work Items
Check each work item:
- Has specific, actionable description?
- Has exact file path (or "console")?
- Correct file_status (new/existing)?
- Dependencies in correct order?

## OUTPUT (JSON only, no explanation):
{{
  "description": "one sentence task summary",
  "mode": "peer|architect|sdet|coder",
  "work_items": [
    {{
      "mode": "coder",
      "file_path": "exact/path/file.py",
      "file_status": "new",
      "description": "detailed prompt for this specific work item",
      "dependencies": []
    }}
  ],
  "priority": "low|normal|high"
}}"""

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

        prompt = f"""You are a code reviewer. Evaluate the output against the task requirements.

## TASK DESCRIPTION:
{task_description}

## EXECUTOR OUTPUT:
{compressed_output}

## EVALUATION CRITERIA:

### STEP 1: Completeness Check
- Does output address ALL requirements from task description?
- Are all steps completed?
- YES/NO for each requirement

### STEP 2: Quality Assessment
- Code correctness (syntax, logic)
- Error handling present?
- Documentation/comments present?
- Score: 0.0 to 1.0

### STEP 3: Identify Issues
- List specific problems found
- Missing functionality
- Bugs or errors

### STEP 4: Decision
- If score >= 0.7 AND all requirements met: needs_iteration=false
- Otherwise: needs_iteration=true

## OUTPUT (JSON only):
{{"quality_score": 0.0-1.0, "needs_iteration": true|false, "feedback": "specific issues or confirmation", "suggestions": ["actionable suggestion 1", "actionable suggestion 2"]}}"""

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
                
                return {
                    "description": data.get("description", ""),
                    "mode": data.get("mode", "coder"),
                    "work_items": work_items,
                    "priority": data.get("priority", "normal"),
                }
        except Exception as e:
            print(f"Error parsing task plan: {e}")

        # Fallback - create single work item
        return {
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
