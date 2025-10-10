"""
Context Condensation and Progressive Summarization for Vivek

This module implements intelligent context management that allows LLMs with
limited context windows to remain effective over extended conversations.
"""

import json
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

from .structured_workflow import ContextSummary, ActivityBreakdown, TaskDefinition


class CompressionLevel(Enum):
    """Levels of context compression"""

    NONE = "none"  # No compression
    LIGHT = "light"  # Remove redundant information
    MEDIUM = "medium"  # Summarize similar content
    HEAVY = "heavy"  # Keep only essential information
    ARCHIVE = "archive"  # Store in long-term memory


class ContextType(Enum):
    """Types of context information"""

    DECISION = "decision"  # Important decisions made
    ACTION = "action"  # Actions taken
    RESULT = "result"  # Results achieved
    LEARNING = "learning"  # Lessons learned
    DEPENDENCY = "dependency"  # Dependencies identified
    METADATA = "metadata"  # System metadata


@dataclass
class ContextItem:
    """Individual context item with metadata"""

    id: str
    type: ContextType
    content: str
    timestamp: float
    importance: float  # 0.0 to 1.0
    tokens: int
    source: str  # Which node/component created this
    tags: Optional[List[str]] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class ContextLayer:
    """Layer of context with specific retention policy"""

    name: str
    max_items: int
    max_age_hours: float
    compression_threshold: float
    items: List[ContextItem] = field(default_factory=list)


class ProgressiveContextManager:
    """Manages progressive context condensation across conversation"""

    def __init__(self, total_budget: int = 4000):
        self.total_budget = total_budget
        self.layers = self._initialize_layers()
        self.context_history: List[ContextSummary] = []
        self.current_session_items: List[ContextItem] = []

    def _initialize_layers(self) -> Dict[str, ContextLayer]:
        """Initialize context layers with different retention policies"""
        return {
            "immediate": ContextLayer(
                name="immediate",
                max_items=10,
                max_age_hours=1.0,  # 1 hour
                compression_threshold=0.8,
            ),
            "short_term": ContextLayer(
                name="short_term",
                max_items=20,
                max_age_hours=24.0,  # 24 hours
                compression_threshold=0.6,
            ),
            "medium_term": ContextLayer(
                name="medium_term",
                max_items=50,
                max_age_hours=168.0,  # 1 week
                compression_threshold=0.4,
            ),
            "long_term": ContextLayer(
                name="long_term",
                max_items=100,
                max_age_hours=720.0,  # 30 days
                compression_threshold=0.2,
            ),
        }

    def add_context_item(
        self,
        content: str,
        context_type: ContextType,
        importance: float = 0.5,
        source: str = "unknown",
        tags: Optional[List[str]] = None,
    ) -> str:
        """Add a new context item to appropriate layer"""
        item_id = f"ctx_{int(time.time())}_{len(self.current_session_items)}"

        # Estimate tokens (rough approximation)
        estimated_tokens = len(content) // 4

        item = ContextItem(
            id=item_id,
            type=context_type,
            content=content,
            timestamp=time.time(),
            importance=importance,
            tokens=estimated_tokens,
            source=source,
            tags=tags or [],
        )

        # Determine appropriate layer based on importance and type
        layer_name = self._select_layer_for_item(item)
        self.layers[layer_name].items.append(item)
        self.current_session_items.append(item)

        # Apply retention policy for the layer
        self._apply_retention_policy(layer_name)

        return item_id

    def _select_layer_for_item(self, item: ContextItem) -> str:
        """Select appropriate layer for context item"""
        # Critical decisions and results go to longer-term storage
        if item.importance > 0.8 or item.type in [
            ContextType.DECISION,
            ContextType.LEARNING,
        ]:
            return "long_term"
        elif item.importance > 0.6 or item.type in [
            ContextType.RESULT,
            ContextType.DEPENDENCY,
        ]:
            return "medium_term"
        elif item.importance > 0.4 or item.type in [ContextType.ACTION]:
            return "short_term"
        else:
            return "immediate"

    def _apply_retention_policy(self, layer_name: str):
        """Apply retention policy for a layer"""
        layer = self.layers[layer_name]

        # Remove items exceeding max age
        current_time = time.time()
        max_age_seconds = layer.max_age_hours * 3600

        layer.items = [
            item
            for item in layer.items
            if (current_time - item.timestamp) < max_age_seconds
        ]

        # If still too many items, remove least important
        while len(layer.items) > layer.max_items:
            # Sort by importance and recency
            layer.items.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
            layer.items.pop()  # Remove least important/oldest

    def get_condensed_context(self, strategy: str = "balanced") -> ContextSummary:
        """Get condensed context based on strategy"""
        if strategy == "recent":
            return self._get_recent_context()
        elif strategy == "important":
            return self._get_important_context()
        elif strategy == "balanced":
            return self._get_balanced_context()
        else:
            return self._get_comprehensive_context()

    def _get_recent_context(self) -> ContextSummary:
        """Get context focused on recent items"""
        recent_items = []
        total_tokens = 0

        # Get items from most recent first
        all_items = []
        for layer in self.layers.values():
            all_items.extend(layer.items)

        all_items.sort(key=lambda x: x.timestamp, reverse=True)

        for item in all_items:
            if total_tokens + item.tokens > self.total_budget:
                break
            recent_items.append(item.content)
            total_tokens += item.tokens

        return ContextSummary(
            session_id="current",
            timestamp=str(int(time.time())),
            short_term_memory=recent_items[:5],
            medium_term_memory=recent_items[5:10],
            long_term_memory={"recent_focus": recent_items[10:15]},
            token_budget=self.total_budget - total_tokens,
            compression_strategy="recent",
        )

    def _get_important_context(self) -> ContextSummary:
        """Get context focused on important items"""
        important_items = []
        total_tokens = 0

        # Get items sorted by importance
        all_items = []
        for layer in self.layers.values():
            all_items.extend(layer.items)

        all_items.sort(key=lambda x: x.importance, reverse=True)

        for item in all_items:
            if total_tokens + item.tokens > self.total_budget:
                break
            important_items.append(item.content)
            total_tokens += item.tokens

        return ContextSummary(
            session_id="current",
            timestamp=str(int(time.time())),
            short_term_memory=important_items[:3],
            medium_term_memory=important_items[3:8],
            long_term_memory={"important_focus": important_items[8:13]},
            token_budget=self.total_budget - total_tokens,
            compression_strategy="important",
        )

    def _get_balanced_context(self) -> ContextSummary:
        """Get balanced context across all layers"""
        short_term = []
        medium_term = []
        long_term = {}

        total_tokens = 0
        budget_per_layer = self.total_budget // 3

        # Allocate tokens across layers
        for layer_name, layer in self.layers.items():
            layer_items = []
            layer_tokens = 0

            # Sort by importance within layer
            sorted_items = sorted(layer.items, key=lambda x: x.importance, reverse=True)

            for item in sorted_items:
                if layer_tokens + item.tokens > budget_per_layer:
                    break
                layer_items.append(item.content)
                layer_tokens += item.tokens

            total_tokens += layer_tokens

            if layer_name == "immediate":
                short_term.extend(layer_items[:2])
            elif layer_name == "short_term":
                short_term.extend(layer_items[:3])
            elif layer_name == "medium_term":
                medium_term.extend(layer_items[:4])
            else:  # long_term
                long_term[layer_name] = layer_items[:5]

        return ContextSummary(
            session_id="current",
            timestamp=str(int(time.time())),
            short_term_memory=short_term,
            medium_term_memory=medium_term,
            long_term_memory=long_term,
            token_budget=self.total_budget - total_tokens,
            compression_strategy="balanced",
        )

    def _get_comprehensive_context(self) -> ContextSummary:
        """Get comprehensive context with full detail"""
        all_items = []
        total_tokens = 0

        for layer in self.layers.values():
            for item in layer.items:
                if total_tokens + item.tokens > self.total_budget:
                    break
                all_items.append(item.content)
                total_tokens += item.tokens

        return ContextSummary(
            session_id="current",
            timestamp=str(int(time.time())),
            short_term_memory=all_items[:10],
            medium_term_memory=all_items[10:20],
            long_term_memory={"comprehensive": all_items[20:30]},
            token_budget=self.total_budget - total_tokens,
            compression_strategy="comprehensive",
        )

    def archive_completed_work(
        self, activities: List[ActivityBreakdown], tasks: List[TaskDefinition]
    ):
        """Archive completed work to long-term memory"""
        # Archive completed activities
        for activity in activities:
            if self._is_activity_complete(activity):
                self.add_context_item(
                    content=f"Completed activity: {activity.name} - {activity.description}",
                    context_type=ContextType.RESULT,
                    importance=0.7,
                    source="activity_completion",
                    tags=["activity", "completed", activity.activity_id],
                )

        # Archive completed tasks
        for task in tasks:
            if self._is_task_complete(task):
                self.add_context_item(
                    content=f"Completed task: {task.description}",
                    context_type=ContextType.ACTION,
                    importance=0.6,
                    source="task_completion",
                    tags=["task", "completed", task.task_id],
                )

    def _is_activity_complete(self, activity: ActivityBreakdown) -> bool:
        """Check if activity appears complete (heuristic)"""
        # This would need to be implemented based on actual completion tracking
        return False

    def _is_task_complete(self, task: TaskDefinition) -> bool:
        """Check if task appears complete (heuristic)"""
        # This would need to be implemented based on actual completion tracking
        return False

    def get_context_stats(self) -> Dict[str, Any]:
        """Get statistics about current context state"""
        total_items = sum(len(layer.items) for layer in self.layers.values())
        total_tokens = sum(
            sum(item.tokens for item in layer.items) for layer in self.layers.values()
        )

        return {
            "total_items": total_items,
            "total_tokens": total_tokens,
            "layers": {
                name: {
                    "item_count": len(layer.items),
                    "total_tokens": sum(item.tokens for item in layer.items),
                    "oldest_item_age": (
                        time.time()
                        - min(
                            (item.timestamp for item in layer.items),
                            default=time.time(),
                        )
                    )
                    / 3600,  # hours
                }
                for name, layer in self.layers.items()
            },
            "compression_ratio": (
                total_tokens / self.total_budget if self.total_budget > 0 else 0
            ),
        }

    def cleanup_old_context(self, max_age_hours: float = 720.0):
        """Clean up context items older than max_age_hours"""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for layer in self.layers.values():
            layer.items = [
                item
                for item in layer.items
                if (current_time - item.timestamp) < max_age_seconds
            ]
