import json
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

from ..llm.models import PlannerModel, ExecutorModel, OllamaProvider

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
        # Order matters - more specific terms first
        user_lower = user_input.lower()

        if any(word in user_lower for word in ["review", "check", "analyze", "examine"]):
            return "review"
        elif any(word in user_lower for word in ["test", "testing", "unit test", "integration test"]):
            return "testing"
        elif any(word in user_lower for word in ["architecture", "design", "structure", "system design"]):
            return "architecture"
        elif any(word in user_lower for word in ["implement", "create", "build", "develop", "add"]):
            return "implementation"
        elif any(word in user_lower for word in ["write", "code", "programming"]):
            return "implementation"
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

class VivekOrchestrator:
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
            task_plan_data = self.planner.analyze_request(user_input, context)
            task_plan = TaskPlan(**task_plan_data)

            # Update session mode
            self.session_context.current_mode = task_plan.mode

            print(f"🧠 Planner: Breaking down task in {task_plan.mode} mode...")

            # Step 2: Executor implements task
            executor_output = self.executor.execute_task(task_plan_data, context)

            print(f"⚙️ Executor: Completed implementation...")

            # Step 3: Planner reviews output
            review_data = self.planner.review_output(task_plan.description, executor_output)
            review = ReviewResult(**review_data)

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