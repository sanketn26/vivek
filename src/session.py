import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class TaskPlan:
    description: str
    mode: str  # peer, architect, sdet, coder
    steps: List[str]
    relevant_files: List[str]
    priority: str = "normal"

@dataclass
class ReviewResult:
    quality_score: float  # 0-1
    needs_iteration: bool
    feedback: str
    suggestions: List[str]

class SessionContext:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.current_mode = "peer"
        self.search_enabled = True
        self.condensed_history: List[Dict] = []
        self.project_summary = ""
        self.working_files: Dict[str, str] = {}
        self.key_decisions: List[str] = []
        
    def add_interaction(self, user_input: str, task_plan: TaskPlan, 
                       executor_output: str, review: ReviewResult):
        """Add and immediately condense an interaction"""
        condensed = {
            "timestamp": time.time(),
            "intent": self._extract_intent(user_input),
            "mode": task_plan.mode,
            "key_changes": self._extract_changes(executor_output),
            "decisions": self._extract_decisions(task_plan.description),
            "quality": review.quality_score,
            "files_touched": task_plan.relevant_files
        }
        
        self.condensed_history.append(condensed)
        
        # Keep only last 10 condensed interactions
        if len(self.condensed_history) > 10:
            self.condensed_history.pop(0)
            
        self._update_project_summary()
    
    def get_relevant_context(self, max_tokens: int = 1000) -> str:
        """Get condensed context for the current interaction"""
        context = {
            "project_summary": self.project_summary,
            "current_mode": self.current_mode,
            "recent_decisions": self.key_decisions[-5:],
            "working_files": list(self.working_files.keys()),
            "recent_history": self.condensed_history[-3:]  # Last 3 interactions
        }
        
        context_str = json.dumps(context, indent=2)
        
        # Truncate if too long (simple approximation)
        if len(context_str) > max_tokens * 4:  # ~4 chars per token
            context["recent_history"] = self.condensed_history[-1:]
            context_str = json.dumps(context, indent=2)
            
        return context_str
    
    def _extract_intent(self, user_input: str) -> str:
        """Extract the core intent from user input"""
        # Simple keyword-based intent extraction
        if any(word in user_input.lower() for word in ["test", "testing"]):
            return "testing"
        elif any(word in user_input.lower() for word in ["architecture", "design", "structure"]):
            return "architecture"
        elif any(word in user_input.lower() for word in ["implement", "code", "write"]):
            return "implementation"
        elif any(word in user_input.lower() for word in ["review", "check", "analyze"]):
            return "review"
        else:
            return "general"
    
    def _extract_changes(self, output: str) -> List[str]:
        """Extract key changes from executor output"""
        changes = []
        lines = output.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ["added", "created", "modified", "updated"]):
                changes.append(line.strip())
        return changes[:3]  # Keep top 3 changes
    
    def _extract_decisions(self, description: str) -> str:
        """Extract key architectural decisions"""
        # Simple pattern matching for decisions
        if "pattern" in description.lower():
            return "architectural_pattern"
        elif "framework" in description.lower():
            return "framework_choice"
        elif "structure" in description.lower():
            return "code_structure"
        else:
            return "implementation_detail"
    
    def _update_project_summary(self):
        """Update high-level project understanding"""
        if len(self.condensed_history) < 3:
            return
            
        # Simple aggregation of recent activity
        recent_modes = [h["mode"] for h in self.condensed_history[-5:]]
        dominant_mode = max(set(recent_modes), key=recent_modes.count)
        
        recent_intents = [h["intent"] for h in self.condensed_history[-5:]]
        main_focus = max(set(recent_intents), key=recent_intents.count)
        
        all_files = set()
        for h in self.condensed_history:
            all_files.update(h.get("files_touched", []))
        
        self.project_summary = f"Working on {main_focus} tasks in {dominant_mode} mode. Active files: {', '.join(list(all_files)[:5])}"

# buttler/llm/models.py
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
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
            return response["response"]
        except Exception as e:
            return f"Error generating response: {str(e)}"

class PlannerModel:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.system_prompt = """You are the Planning Brain of Buttler AI coding assistant.

Your responsibilities:
1. Understand user requests and break them into actionable steps
2. Choose the right mode (peer/architect/sdet/coder) for each task
3. Review outputs from the Executor Brain
4. Provide strategic guidance and context management

Respond in JSON format for structured communication."""

    def analyze_request(self, user_input: str, context: str) -> TaskPlan:
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
    
    def review_output(self, task_description: str, executor_output: str) -> ReviewResult:
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
    
    def _parse_task_plan(self, response: str) -> TaskPlan:
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                return TaskPlan(
                    description=data.get("description", ""),
                    mode=data.get("mode", "coder"),
                    steps=data.get("steps", []),
                    relevant_files=data.get("relevant_files", []),
                    priority=data.get("priority", "normal")
                )
        except Exception as e:
            print(f"Error parsing task plan: {e}")
        
        # Fallback
        return TaskPlan(
            description="Code implementation task",
            mode="coder",
            steps=["Implement the requested functionality"],
            relevant_files=[],
            priority="normal"
        )
    
    def _parse_review(self, response: str) -> ReviewResult:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                data = json.loads(json_str)
                return ReviewResult(
                    quality_score=data.get("quality_score", 0.7),
                    needs_iteration=data.get("needs_iteration", False),
                    feedback=data.get("feedback", "Output looks good"),
                    suggestions=data.get("suggestions", [])
                )
        except Exception as e:
            print(f"Error parsing review: {e}")
        
        # Fallback
        return ReviewResult(
            quality_score=0.7,
            needs_iteration=False,
            feedback="Review completed",
            suggestions=[]
        )

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

    def execute_task(self, task_plan: TaskPlan, context: str) -> str:
        mode_instruction = self.mode_prompts.get(task_plan.mode, self.mode_prompts["coder"])
        
        prompt = f"""{mode_instruction}

Context: {context}
Task: {task_plan.description}
Mode: {task_plan.mode}
Priority: {task_plan.priority}

Steps to complete:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(task_plan.steps))}

Relevant files: {', '.join(task_plan.relevant_files)}

Execute this task step by step. Provide clear, actionable output suitable for the {task_plan.mode} mode."""

        return self.provider.generate(prompt, temperature=0.2)

# buttler/core/orchestrator.py
from .session import SessionContext, TaskPlan, ReviewResult
from ..llm.models import PlannerModel, ExecutorModel, OllamaProvider

class ButtlerOrchestrator:
    def __init__(self, project_root: str = ".", 
                 planner_model: str = "qwen2.5-coder:7b",
                 executor_model: str = "qwen2.5-coder:7b"):
        self.session_context = SessionContext(project_root)
        
        # Initialize models
        planner_provider = OllamaProvider(planner_model)
        executor_provider = OllamaProvider(executor_model)
        
        self.planner = PlannerModel(planner_provider)
        self.executor = ExecutorModel(executor_provider)
        
    async def process_request(self, user_input: str) -> str:
        """Main processing pipeline"""
        try:
            # Step 1: Planner analyzes request
            context = self.session_context.get_relevant_context()
            task_plan = self.planner.analyze_request(user_input, context)
            
            # Update session mode
            self.session_context.current_mode = task_plan.mode
            
            print(f"🧠 Planner: Breaking down task in {task_plan.mode} mode...")
            
            # Step 2: Executor implements task
            executor_output = self.executor.execute_task(task_plan, context)
            
            print(f"⚙️ Executor: Completed implementation...")
            
            # Step 3: Planner reviews output
            review = self.planner.review_output(task_plan.description, executor_output)
            
            print(f"🔍 Planner: Quality score {review.quality_score:.1f}/1.0")
            
            # Step 4: Iterate if needed (simplified for now)
            final_output = executor_output
            if review.needs_iteration and review.quality_score < 0.6:
                print("🔄 Iterating for improvement...")
                # Could implement iteration here
            
            # Step 5: Condense interaction and update context
            self.session_context.add_interaction(user_input, task_plan, final_output, review)
            
            # Format response
            response = self._format_response(final_output, review, task_plan.mode)
            return response
            
        except Exception as e:
            return f"❌ Error processing request: {str(e)}"
    
    def _format_response(self, output: str, review: ReviewResult, mode: str) -> str:
        """Format the final response for the user"""
        header = f"[{mode.upper()} MODE] "
        
        formatted = f"{header}{output}"
        
        if review.suggestions:
            formatted += f"\n\n💡 Suggestions:\n" + "\n".join(f"• {s}" for s in review.suggestions[:3])
        
        return formatted
    
    def switch_mode(self, mode: str):
        """Switch current mode"""
        valid_modes = ["peer", "architect", "sdet", "coder"]
        if mode in valid_modes:
            self.session_context.current_mode = mode
            return f"Switched to {mode} mode"
        else:
            return f"Invalid mode. Valid modes: {', '.join(valid_modes)}"
    
    def get_status(self) -> str:
        """Get current session status"""
        ctx = self.session_context
        return f"""Current Status:
• Mode: {ctx.current_mode}
• Project: {ctx.project_root}
• Interactions: {len(ctx.condensed_history)}
• Active files: {len(ctx.working_files)}
• Summary: {ctx.project_summary or 'New session'}"""