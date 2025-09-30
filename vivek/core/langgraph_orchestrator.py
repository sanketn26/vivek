"""
LangGraph-based orchestrator for Vivek AI assistant.

This replaces the manual orchestration with a graph-based approach providing:
- Automatic iteration with conditional edges
- Persistent state with SqliteSaver
- Event streaming for progress indicators
- Human-in-the-loop capabilities
"""

import asyncio
from pathlib import Path
from typing import Optional, Dict, Any, AsyncIterator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from .graph_state import VivekState, initialize_state, should_iterate
from .graph_nodes import (
    create_planner_node,
    create_executor_node,
    create_reviewer_node,
    format_response_node,
)
from ..llm.models import PlannerModel, ExecutorModel, OllamaProvider


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
        planner_provider = OllamaProvider(planner_model)
        executor_provider = OllamaProvider(executor_model)

        self.planner = PlannerModel(planner_provider)
        self.executor = ExecutorModel(executor_provider)

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
        Build the LangGraph workflow.

        Returns:
            Configured StateGraph
        """
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
        workflow.add_node("formatter", format_response_node)

        # Set entry point
        workflow.set_entry_point("planner")

        # Add edges
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "reviewer")

        # Conditional edge for iteration
        workflow.add_conditional_edges(
            "reviewer",
            should_iterate,
            {
                "iterate": "executor",  # Go back to executor with feedback
                "finish": "formatter",  # Move to formatting
            },
        )

        # Final edge
        workflow.add_edge("formatter", END)

        return workflow

    async def process_request(
        self, user_input: str, thread_id: str = "default"
    ) -> str:
        """
        Process a user request through the graph.

        Args:
            user_input: The user's request
            thread_id: Thread ID for session persistence

        Returns:
            Final response string
        """
        # Update context with current mode
        self.context["current_mode"] = self.current_mode

        # Initialize state
        initial_state = initialize_state(user_input, self.context)

        # Use checkpointing with async context manager
        async with AsyncSqliteSaver.from_conn_string(str(self.checkpoint_db)) as checkpointer:
            # Compile with checkpointer
            app = self.graph.compile(checkpointer=checkpointer)

            # Configuration for checkpointing
            config = {"configurable": {"thread_id": thread_id}}

            # Invoke graph
            final_state = await app.ainvoke(initial_state, config=config)

        # Update context from final state (for next iteration)
        if "task_plan" in final_state:
            task_plan = final_state["task_plan"]
            self.context["working_files"] = task_plan.get("relevant_files", [])

        return final_state.get("final_response", "No response generated")

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
        # Update context with current mode
        self.context["current_mode"] = self.current_mode

        # Initialize state
        initial_state = initialize_state(user_input, self.context)

        # Use checkpointing with async context manager
        async with AsyncSqliteSaver.from_conn_string(str(self.checkpoint_db)) as checkpointer:
            # Compile with checkpointer
            app = self.graph.compile(checkpointer=checkpointer)

            # Configuration for checkpointing
            config = {"configurable": {"thread_id": thread_id}}

            # Stream events
            async for event in app.astream_events(initial_state, config=config, version="v2"):
                yield event

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

    async def get_session_history(self, thread_id: str = "default") -> list:
        """
        Get the history of a session from checkpoints.

        Args:
            thread_id: Thread ID to query

        Returns:
            List of state checkpoints
        """
        config = {"configurable": {"thread_id": thread_id}}
        history = []

        # Get checkpoint history
        checkpoints = self.checkpointer.list(config)
        for checkpoint in checkpoints:
            history.append(checkpoint)

        return history