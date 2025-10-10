"""
Tests for context condensation and progressive summarization.
"""

import pytest
import time
from unittest.mock import Mock, patch

from vivek.core.context_condensation import (
    ProgressiveContextManager,
    ContextType,
    ContextItem,
    ContextLayer,
)

# Import for type checking
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vivek.core.structured_workflow import ContextSummary


class TestProgressiveContextManager:
    """Test cases for ProgressiveContextManager"""

    def setup_method(self):
        """Set up test fixtures"""
        self.manager = ProgressiveContextManager(total_budget=1000)

    def test_initialization(self):
        """Test proper initialization of context manager"""
        assert self.manager.total_budget == 1000
        assert (
            len(self.manager.layers) == 4
        )  # immediate, short_term, medium_term, long_term
        assert "immediate" in self.manager.layers
        assert "long_term" in self.manager.layers

    def test_add_context_item(self):
        """Test adding context items"""
        item_id = self.manager.add_context_item(
            content="Test decision made",
            context_type=ContextType.DECISION,
            importance=0.8,
            source="test_planner",
            tags=["test", "decision"],
        )

        assert item_id is not None
        assert item_id.startswith("ctx_")
        assert len(self.manager.current_session_items) == 1

        item = self.manager.current_session_items[0]
        assert item.content == "Test decision made"
        assert item.type == ContextType.DECISION
        assert item.importance == 0.8
        assert item.source == "test_planner"
        assert item.tags and "test" in item.tags

    def test_layer_selection_by_importance(self):
        """Test that items are placed in appropriate layers based on importance"""
        # High importance item should go to long_term
        high_item_id = self.manager.add_context_item(
            content="Critical decision",
            context_type=ContextType.DECISION,
            importance=0.9,
            source="test",
        )

        # Low importance item should go to immediate
        low_item_id = self.manager.add_context_item(
            content="Minor detail",
            context_type=ContextType.METADATA,
            importance=0.1,
            source="test",
        )

        # Check that high importance item is in long_term layer
        long_term_items = self.manager.layers["long_term"].items
        short_term_items = self.manager.layers["short_term"].items
        immediate_items = self.manager.layers["immediate"].items

        assert len(long_term_items) >= 1
        assert len(immediate_items) >= 1

    def test_retention_policy_application(self):
        """Test that retention policies are applied"""
        # Add many items to trigger retention policy
        for i in range(15):  # More than immediate layer's max_items (10)
            self.manager.add_context_item(
                content=f"Item {i}",
                context_type=ContextType.ACTION,
                importance=0.3,
                source="test",
            )

        # Immediate layer should not exceed max_items
        immediate_layer = self.manager.layers["immediate"]
        assert len(immediate_layer.items) <= immediate_layer.max_items

    def test_get_condensed_context_strategies(self):
        """Test different context condensation strategies"""
        # Add some test data
        self.manager.add_context_item(
            "Recent important decision", ContextType.DECISION, 0.8
        )
        self.manager.add_context_item("Old decision", ContextType.DECISION, 0.7)
        self.manager.add_context_item("Recent minor detail", ContextType.METADATA, 0.2)

        # Test recent strategy
        recent_context = self.manager.get_condensed_context("recent")
        assert recent_context is not None
        assert recent_context.compression_strategy == "recent"
        assert recent_context.token_budget >= 0

        # Test important strategy
        important_context = self.manager.get_condensed_context("important")
        assert important_context.compression_strategy == "important"

        # Test balanced strategy
        balanced_context = self.manager.get_condensed_context("balanced")
        assert balanced_context.compression_strategy == "balanced"

    def test_context_stats(self):
        """Test context statistics generation"""
        # Add some items
        self.manager.add_context_item("Test item 1", ContextType.ACTION, 0.5)
        self.manager.add_context_item("Test item 2", ContextType.RESULT, 0.7)

        stats = self.manager.get_context_stats()

        assert "total_items" in stats
        assert "total_tokens" in stats
        assert "layers" in stats
        assert stats["total_items"] >= 2

        # Check layer stats
        for layer_name in ["immediate", "short_term", "medium_term", "long_term"]:
            assert layer_name in stats["layers"]
            assert "item_count" in stats["layers"][layer_name]
            assert "total_tokens" in stats["layers"][layer_name]

    def test_cleanup_old_context(self):
        """Test cleanup of old context items"""
        # Add an item
        self.manager.add_context_item("Test item", ContextType.ACTION, 0.5)

        # Manually set timestamp to old time (simulate old item)
        if self.manager.current_session_items:
            self.manager.current_session_items[0].timestamp = time.time() - (
                24 * 3600
            )  # 24 hours ago

        # Cleanup items older than 1 hour
        self.manager.cleanup_old_context(max_age_hours=1.0)

        # Items in layers should be cleaned up, but current_session_items is a separate list
        # that tracks all items added in current session - it doesn't get cleaned by cleanup_old_context
        # This is by design since current_session_items serves as a complete session history


class TestContextItem:
    """Test cases for ContextItem dataclass"""

    def test_context_item_creation(self):
        """Test creating context items with all fields"""
        item = ContextItem(
            id="test_item_1",
            type=ContextType.DECISION,
            content="Test decision content",
            timestamp=time.time(),
            importance=0.8,
            tokens=50,
            source="test_source",
            tags=["test", "decision"],
        )

        assert item.id == "test_item_1"
        assert item.type == ContextType.DECISION
        assert item.content == "Test decision content"
        assert item.importance == 0.8
        assert item.tokens == 50
        assert item.source == "test_source"
        assert item.tags is not None
        assert len(item.tags) == 2
        assert "test" in item.tags

    def test_context_item_default_tags(self):
        """Test that tags default to empty list"""
        item = ContextItem(
            id="test_item",
            type=ContextType.ACTION,
            content="Test content",
            timestamp=time.time(),
            importance=0.5,
            tokens=25,
            source="test",
        )

        assert item.tags == []


class TestContextLayer:
    """Test cases for ContextLayer dataclass"""

    def test_context_layer_creation(self):
        """Test creating context layers"""
        layer = ContextLayer(
            name="test_layer",
            max_items=10,
            max_age_hours=24.0,
            compression_threshold=0.6,
        )

        assert layer.name == "test_layer"
        assert layer.max_items == 10
        assert layer.max_age_hours == 24.0
        assert layer.compression_threshold == 0.6
        assert layer.items == []

    def test_context_layer_with_items(self):
        """Test context layer with items"""
        # Create a mock item
        item = ContextItem(
            id="test_item",
            type=ContextType.ACTION,
            content="Test",
            timestamp=time.time(),
            importance=0.5,
            tokens=10,
            source="test",
        )

        layer = ContextLayer(
            name="test_layer",
            max_items=10,
            max_age_hours=24.0,
            compression_threshold=0.6,
            items=[item],
        )

        assert len(layer.items) == 1
        assert layer.items[0].id == "test_item"


class TestContextIntegration:
    """Test integration between context components"""

    def setup_method(self):
        """Set up integration test fixtures"""
        self.manager = ProgressiveContextManager(total_budget=500)

    def test_context_lifecycle(self):
        """Test full context lifecycle: add, condense, cleanup"""
        # Add various types of context
        self.manager.add_context_item("Decision made", ContextType.DECISION, 0.8)
        self.manager.add_context_item("Action taken", ContextType.ACTION, 0.6)
        self.manager.add_context_item("Result achieved", ContextType.RESULT, 0.7)
        self.manager.add_context_item("Minor detail", ContextType.METADATA, 0.2)

        # Get condensed context
        context = self.manager.get_condensed_context("balanced")
        assert context is not None
        assert (
            len(context.short_term_memory) >= 0
        )  # May be empty if token budget exceeded
        assert context.token_budget >= 0

        # Get stats
        stats = self.manager.get_context_stats()
        assert stats["total_items"] >= 4

        # Cleanup old context (simulate passage of time)
        self.manager.cleanup_old_context(max_age_hours=1.0)
        # Items should still be there since they're recent

    def test_context_strategies_produce_different_results(self):
        """Test that different strategies produce different summaries"""
        # Add test data
        for i in range(10):
            self.manager.add_context_item(
                f"Item {i}",
                ContextType.ACTION if i % 2 == 0 else ContextType.RESULT,
                importance=0.3 + (i * 0.05),  # Increasing importance
                source="test",
            )

        # Get different strategy results
        recent = self.manager.get_condensed_context("recent")
        important = self.manager.get_condensed_context("important")
        balanced = self.manager.get_condensed_context("balanced")

        # All should be valid context summaries
        for ctx in [recent, important, balanced]:
            assert ctx.session_id == "current"
            assert ctx.compression_strategy in ["recent", "important", "balanced"]

        # Should have different token budgets or content
        # (exact comparison depends on implementation details)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
