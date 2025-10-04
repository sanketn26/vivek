"""
LangGraph-based orchestrator for Vivek AI assistant.

This replaces the manual orchestration with a graph-based approach providing:
- Automatic iteration with conditional edges
- Persistent state with SqliteSaver
- Event streaming for progress indicators
- Human-in-the-loop capabilities
"""

from pathlib import Path
from typing import Dict, Any, AsyncIterator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.runnables import RunnableConfig

from ..llm.planner import PlannerModel

from ..llm.provider import OllamaProvider

from .graph_state import VivekState, initialize_state, should_iterate
from .graph_nodes import (
    create_planner_node,
    create_executor_node,
    create_reviewer_node,
    format_response_node,
)
from ..llm.executor import get_executor


class LangGraphVivekOrchestrator:
    """
    LangGraph-based orchestrator for multi-agent Vivek system.

    Replaces the manual orchestration in orchestrator.py with a graph-based
    approach that provides automatic iteration, state persistence, and better
    observability.
    """

    def __init__(
        self,
        project_root: str = ".",
        planner_model: str = "qwen2.5-coder:7b",
        executor_model: str = "qwen2.5-coder:7b",
    ):
        """
        Initialize the LangGraph orchestrator.

        Args:
            project_root: Root directory of the project
            planner_model: Model name for planner
            executor_model: Model name for executor
        """
        self.project_root = Path(project_root)
        self.project_root.mkdir(parents=True, exist_ok=True)

        # Initialize models
        self.planner_provider = OllamaProvider(planner_model)
        self.executor_provider = OllamaProvider(executor_model)

        self.planner = PlannerModel(self.planner_provider)

        # Set initial mode before creating executor
        self.current_mode = "peer"
        # instantiate executor for the initial mode
        self.executor = get_executor(self.current_mode, self.executor_provider)

        # Build graph
        self.graph = self._build_graph()

        # Setup checkpointing for persistence
        checkpoint_dir = self.project_root / ".vivek"
        checkpoint_dir.mkdir(exist_ok=True)
        self.checkpoint_db = checkpoint_dir / "checkpoints.db"

        # Store the checkpoint connection (will be managed in async context)
        self._checkpointer_context = None

        # For now, compile without checkpointer (will add in async setup)
        # This allows synchronous initialization
        self.app = self.graph.compile()

        # Track current mode and context
        self.current_mode = "peer"
        self.context: Dict[str, Any] = {
            "project_root": str(self.project_root),
            "current_mode": self.current_mode,
            "project_summary": "",
            "recent_decisions": [],
            "working_files": [],
        }

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow with conditional routing for clarifications.

        Returns:
            Configured StateGraph
        """
        # Import routing functions
        from .graph_nodes import (
            route_planner,
            route_executor,
            route_reviewer,
            clarification_node,
        )

        # Create workflow
        workflow = StateGraph(VivekState)

        # Create nodes with factory functions
        planner_node = create_planner_node(self.planner)
        executor_node = create_executor_node(self.executor)
        reviewer_node = create_reviewer_node(self.planner)

        # Add nodes to graph
        workflow.add_node("planner", planner_node)
        workflow.add_node("executor", executor_node)
        workflow.add_node("reviewer", reviewer_node)
        workflow.add_node("clarification", clarification_node)
        workflow.add_node("formatter", format_response_node)

        # Set entry point
        workflow.set_entry_point("planner")

        # Conditional edges with clarification routing
        workflow.add_conditional_edges(
            "planner",
            route_planner,
            {
                "executor": "executor",
                "clarification": "clarification",
            },
        )

        workflow.add_conditional_edges(
            "executor",
            route_executor,
            {
                "reviewer": "reviewer",
                "clarification": "clarification",
            },
        )

        workflow.add_conditional_edges(
            "reviewer",
            route_reviewer,
            {
                "executor": "executor",  # Iteration
                "clarification": "clarification",
                "format_response": "formatter",
            },
        )

        # Clarification ends the flow (pause for user input)
        workflow.add_edge("clarification", END)

        # Final edge
        workflow.add_edge("formatter", END)

        return workflow

    async def process_request(self, user_input: str, thread_id: str = "default") -> Dict[str, Any]:
        """
        Process a user request through the graph.

        Args:
            user_input: The user's request
            thread_id: Thread ID for session persistence

        Returns:
            Dict with status and response/questions
        """
        try:
            # Update context with current mode
            self.context["current_mode"] = self.current_mode

            # Initialize state
            initial_state = initialize_state(user_input, self.context)

            # Use checkpointing with async context manager
            async with AsyncSqliteSaver.from_conn_string(
                str(self.checkpoint_db)
            ) as checkpointer:
                # Compile with checkpointer and interrupt before clarification
                app = self.graph.compile(
                    checkpointer=checkpointer,
                    interrupt_before=["clarification"]
                )

                # Configuration for checkpointing
                config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

                # Invoke graph
                final_state = await app.ainvoke(initial_state, config=config)

        except Exception as e:
            # Log the error and return error response
            import logging
            logging.error(f"Error processing request in thread {thread_id}: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to process request: {str(e)}",
                "thread_id": thread_id
            }

        # Check if paused for clarification
        if final_state.get("needs_clarification"):
            return {
                "status": "awaiting_clarification",
                "questions": final_state.get("clarification_questions", []),
                "from_node": final_state.get("clarification_from", "unknown"),
                "clarification_output": final_state.get("clarification_output", ""),
                "thread_id": thread_id
            }

        # Update context from final state (for next iteration)
        if "task_plan" in final_state:
            task_plan = final_state["task_plan"]
            self.context["working_files"] = task_plan.get("relevant_files", [])

        return {
            "status": "complete",
            "output": final_state.get("final_response", "No response generated")
        }

    async def resume_with_answers(self, thread_id: str, answers: Dict[str, str]) -> Dict[str, Any]:
        """
        Resume execution after user provides clarification answers.

        Args:
            thread_id: Thread ID to resume
            answers: User's answers to clarification questions

        Returns:
            Dict with status and response/questions (might pause again)
        """
        try:
            async with AsyncSqliteSaver.from_conn_string(
                str(self.checkpoint_db)
            ) as checkpointer:
                # Compile with checkpointer
                app = self.graph.compile(
                    checkpointer=checkpointer,
                    interrupt_before=["clarification"]
                )

                # Configuration
                config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

                # Get current state
                state_snapshot = await app.aget_state(config)
                current_state = state_snapshot.values

                # Update state with answers
                current_state["clarification_answers"] = answers
                current_state["needs_clarification"] = False

                # Add answers to context for planner/executor to use
                if "context" not in current_state:
                    current_state["context"] = {}
                current_state["context"]["user_clarifications"] = answers

                # Resume execution
                final_state = await app.ainvoke(current_state, config=config)

        except Exception as e:
            # Log the error and return error response
            import logging
            logging.error(f"Error resuming request in thread {thread_id}: {e}", exc_info=True)
            return {
                "status": "error",
                "error": f"Failed to resume request: {str(e)}",
                "thread_id": thread_id
            }

        # Check if paused again
        if final_state.get("needs_clarification"):
            return {
                "status": "awaiting_clarification",
                "questions": final_state.get("clarification_questions", []),
                "from_node": final_state.get("clarification_from", "unknown"),
                "clarification_output": final_state.get("clarification_output", ""),
                "thread_id": thread_id
            }

        return {
            "status": "complete",
            "output": final_state.get("final_response", "No response generated")
        }

    async def stream_process_request(
        self, user_input: str, thread_id: str = "default"
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Process a user request with event streaming for progress indicators.

        Args:
            user_input: The user's request
            thread_id: Thread ID for session persistence

        Yields:
            Event dictionaries with progress information
        """
        try:
            # Update context with current mode
            self.context["current_mode"] = self.current_mode

            # Initialize state
            initial_state = initialize_state(user_input, self.context)

            # Use checkpointing with async context manager
            async with AsyncSqliteSaver.from_conn_string(
                str(self.checkpoint_db)
            ) as checkpointer:
                # Compile with checkpointer
                app = self.graph.compile(checkpointer=checkpointer)

                # Configuration for checkpointing
                config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

                # Stream events
                async for event in app.astream_events(
                    initial_state, config=config, version="v2"
                ):
                    # Convert event to dict format for compatibility
                    yield {
                        "event": event["event"],
                        "data": event["data"],
                        "metadata": event.get("metadata", {})
                    }

        except Exception as e:
            # Log the error and yield error event
            import logging
            logging.error(f"Error in streaming request for thread {thread_id}: {e}", exc_info=True)
            yield {
                "event": "error",
                "data": {"error": str(e)},
                "metadata": {"thread_id": thread_id}
            }

    def switch_mode(self, mode: str) -> str:
        """
        Switch the current working mode.

        Args:
            mode: New mode (peer, architect, sdet, coder)

        Returns:
            Status message
        """
        valid_modes = ["peer", "architect", "sdet", "coder"]
        if mode in valid_modes:
            self.current_mode = mode
            self.context["current_mode"] = mode
            # update executor instance for the new mode
            self.executor = get_executor(mode, self.executor_provider)
            return f"Switched to {mode} mode"
        else:
            return f"Invalid mode. Valid modes: {', '.join(valid_modes)}"

    def get_status(self) -> str:
        """
        Get current orchestrator status.

        Returns:
            Status string
        """
        return f"""**Vivek LangGraph Status:**
• Mode: {self.current_mode}
• Project: {self.project_root}
• Working Files: {len(self.context.get('working_files', []))}
• Checkpoint DB: {self.project_root / '.vivek' / 'checkpoints.db'}"""
