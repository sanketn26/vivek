"""
Context Manager - Main orchestrator for the context system
"""

from typing import List, Dict, Any, Optional

from vivek.agentic_context.retrieval.retrieval_strategies import RetrieverFactory
from vivek.agentic_context.retrieval.semantic_retrieval import EmbeddingModel
from vivek.agentic_context.core.context_storage import ContextStorage, ContextCategory


class ContextManager:
    """
    Main interface for managing context throughout the workflow
    Handles 3-layer hierarchy, 4-category storage, and intelligent retrieval
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize context manager

        Args:
            config: Configuration dictionary with retrieval and storage settings
        """
        self.config = config
        self.storage = ContextStorage()
        self.retriever = RetrieverFactory.create_retriever(self.storage, config)

        # Initialize embedding model for pre-computing if enabled
        self.embedding_model = None
        if self._should_precompute_embeddings():
            semantic_config = config.get("semantic", {})
            model_name = semantic_config.get("model", "microsoft/codebert-base")
            self.embedding_model = EmbeddingModel(model_name)

    def _should_precompute_embeddings(self) -> bool:
        """Check if embeddings should be pre-computed"""
        strategy = self.config.get("retrieval", {}).get("strategy", "hybrid")
        cache_enabled = self.config.get("semantic", {}).get("cache_embeddings", True)
        return strategy in ["embeddings_only", "hybrid", "auto"] and cache_enabled

    # ==================== Session Management ====================

    def start_session(
        self, session_id: str, original_ask: str, high_level_plan: str, **metadata
    ):
        """Start a new session"""
        return self.storage.create_session(
            session_id, original_ask, high_level_plan, **metadata
        )

    def get_session_context(self):
        """Get current session context"""
        return self.storage.get_session_context()

    # ==================== Activity Management ====================

    def start_activity(
        self,
        activity_id: str,
        description: str,
        tags: List[str],
        mode: str,
        component: str,
        planner_analysis: str,
        **metadata,
    ):
        """Start a new activity under current session"""
        return self.storage.create_activity(
            activity_id,
            description,
            tags,
            mode,
            component,
            planner_analysis,
            **metadata,
        )

    def get_activity_context(self):
        """Get current activity context"""
        return self.storage.get_activity_context()

    # ==================== Task Management ====================

    def start_task(self, task_id: str, description: str, tags: List[str], **metadata):
        """Start a new task under current activity"""
        return self.storage.create_task(task_id, description, tags, **metadata)

    def complete_task(self, task_id: str, result: str):
        """Mark task as complete with result"""
        self.storage.complete_task(task_id, result)

    def get_task_context(self):
        """Get current task context"""
        return self.storage.get_task_context()

    # ==================== Context Recording ====================

    def record_decision(self, content: str, tags: List[str], **metadata):
        """Record an architectural or design decision"""
        embedding = self._compute_embedding_if_needed(content, tags)
        return self.storage.add_context(
            ContextCategory.DECISIONS, content, tags, embedding, **metadata
        )

    def record_action(self, content: str, tags: List[str], **metadata):
        """Record a code change or implementation action"""
        embedding = self._compute_embedding_if_needed(content, tags)
        return self.storage.add_context(
            ContextCategory.ACTIONS, content, tags, embedding, **metadata
        )

    def record_result(self, content: str, tags: List[str], **metadata):
        """Record a completion or outcome"""
        embedding = self._compute_embedding_if_needed(content, tags)
        return self.storage.add_context(
            ContextCategory.RESULTS, content, tags, embedding, **metadata
        )

    def record_learning(self, content: str, tags: List[str], **metadata):
        """Record a lesson learned or issue encountered"""
        embedding = self._compute_embedding_if_needed(content, tags)
        return self.storage.add_context(
            ContextCategory.LEARNINGS, content, tags, embedding, **metadata
        )

    def _compute_embedding_if_needed(self, content: str, tags: List[str]):
        """Compute embedding if pre-computation is enabled"""
        if self.embedding_model:
            text = f"{content} {' '.join(tags)}"
            return self.embedding_model.encode(text)
        return None

    # ==================== Context Retrieval ====================

    def retrieve_relevant_context(
        self,
        query_tags: List[str],
        query_description: str,
        max_results: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant historical context

        Args:
            query_tags: Tags from current task/activity
            query_description: Description of what you're working on
            max_results: Max results to return (uses config default if None)

        Returns:
            List of relevant context items with scores
        """
        if max_results is None:
            max_results = self.config.get("retrieval", {}).get("max_results", 5)

        results = self.retriever.retrieve(query_tags, query_description, max_results)

        # Filter by minimum score threshold
        min_threshold = self.config.get("retrieval", {}).get("min_score_threshold", 0.0)
        filtered = [r for r in results if r.get("score", 0) >= min_threshold]

        return filtered

    # ==================== Prompt Building ====================

    def build_prompt_context(self, include_relevant_history: bool = True) -> str:
        """
        Build complete context for LLM prompt
        Includes 3-layer hierarchy + retrieved relevant history

        Args:
            include_relevant_history: Whether to retrieve and include historical context

        Returns:
            Formatted context string for prompt
        """
        session = self.storage.get_session_context()
        activity = self.storage.get_activity_context()
        task = self.storage.get_task_context()

        # Build hierarchical context
        context_parts = []

        # Session layer
        if session:
            context_parts.append("=== SESSION CONTEXT ===")
            context_parts.append(f"Original Request: {session.original_ask}")
            context_parts.append(f"High-Level Plan: {session.high_level_plan}")
            context_parts.append("")

        # Activity layer
        if activity:
            context_parts.append("=== ACTIVITY CONTEXT ===")
            context_parts.append(f"Current Activity: {activity.description}")
            context_parts.append(f"Mode: {activity.mode}")
            context_parts.append(f"Component: {activity.component}")
            context_parts.append(f"Planner Analysis:\n{activity.planner_analysis}")
            context_parts.append(f"Activity Tags: {', '.join(activity.tags)}")
            context_parts.append("")

        # Task layer
        if task:
            context_parts.append("=== TASK CONTEXT ===")
            context_parts.append(f"Current Task: {task.description}")
            if task.previous_result:
                context_parts.append(f"Previous Task Result: {task.previous_result}")
            context_parts.append(f"Task Tags: {', '.join(task.tags)}")
            context_parts.append("")

        # Relevant history
        if include_relevant_history and task:
            relevant = self.retrieve_relevant_context(
                query_tags=task.tags, query_description=task.description
            )

            if relevant:
                context_parts.append("=== RELEVANT CONTEXT FROM HISTORY ===")
                for i, item in enumerate(relevant, 1):
                    score = item.get("final_score", item.get("score", 0))
                    context_parts.append(
                        f"\n[{i}] {item['category'].upper()} (relevance: {score:.2f})"
                    )
                    context_parts.append(item["item"]["content"])
                    if item.get("matched_tags"):
                        context_parts.append(
                            f"   Matched tags: {', '.join(item['matched_tags'])}"
                        )
                context_parts.append("")

        # Focus instruction
        context_parts.append("=== INSTRUCTIONS ===")
        context_parts.append(
            "Focus on the current task. The planner has already identified integration points."
        )
        context_parts.append(
            "Use the relevant context from history to inform your implementation."
        )

        return "\n".join(context_parts)

    def build_minimal_context(self) -> Dict[str, Any]:
        """
        Build minimal hierarchical context (no retrieval)
        Useful for debugging or when you don't need history
        """
        return self.storage.build_hierarchical_context()

    # ==================== Utilities ====================

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored context"""
        stats = self.storage.get_statistics()

        # Add retrieval info
        if hasattr(self.retriever, "embedding_model"):
            cache_stats = self.retriever.embedding_model.get_cache_stats()
            stats["embedding_cache"] = cache_stats

        return stats

    def clear_all_context(self):
        """Clear all stored context (use with caution)"""
        self.storage.clear_all()

    def switch_retrieval_strategy(self, new_strategy: str):
        """
        Switch retrieval strategy at runtime

        Args:
            new_strategy: One of: tags_only, embeddings_only, hybrid, auto
        """
        self.config["retrieval"]["strategy"] = new_strategy
        self.retriever = RetrieverFactory.create_retriever(self.storage, self.config)
        print(f"✓ Switched to retrieval strategy: {new_strategy}")

    def export_context_db(self) -> Dict[str, Any]:
        """
        Export entire context DB for persistence
        Returns serializable dict
        """
        export = {"sessions": {}, "context_db": {}}

        # Export sessions
        for session_id, session in self.storage.sessions.items():
            export["sessions"][session_id] = {
                "session_id": session.session_id,
                "original_ask": session.original_ask,
                "high_level_plan": session.high_level_plan,
                "created_at": session.created_at.isoformat(),
                "activities": [
                    {
                        "activity_id": a.activity_id,
                        "description": a.description,
                        "tags": a.tags,
                        "mode": a.mode,
                        "component": a.component,
                        "planner_analysis": a.planner_analysis,
                        "tasks": [
                            {
                                "task_id": t.task_id,
                                "description": t.description,
                                "tags": t.tags,
                                "previous_result": t.previous_result,
                            }
                            for t in a.tasks
                        ],
                    }
                    for a in session.activities
                ],
            }

        # Export context DB (excluding embeddings for size)
        for category, items in self.storage.context_db.items():
            export["context_db"][category.value] = [
                {
                    "content": item.content,
                    "tags": item.tags,
                    "timestamp": item.timestamp.isoformat(),
                    "activity_id": item.activity_id,
                    "task_id": item.task_id,
                    "metadata": item.metadata,
                }
                for item in items
            ]

        return export
