"""
Tests for retrieval_strategies module
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from vivek.agentic_context.core.context_storage import (
    ContextCategory,
    ContextItem,
    ContextStorage,
)
from vivek.agentic_context.retrieval.retrieval_strategies import (
    AutoRetriever,
    BaseRetriever,
    EmbeddingBasedRetriever,
    HybridRetriever,
    RetrievalCache,
    RetrievalConfig,
    RetrievalStrategy,
    RetrieverFactory,
    TagBasedRetriever,
)


class TestRetrievalConfig:
    """Test RetrievalConfig class"""

    def test_default_config(self):
        """Test default configuration values"""
        config = RetrievalConfig()

        assert config.strategy == "hybrid"
        assert config.max_results == 5
        assert config.cache_enabled is True
        assert config.tag_normalization is not None
        assert config.tag_normalization["include_related_tags"] is False
        assert config.semantic is not None
        assert config.semantic["model"] == "microsoft/codebert-base"

    def test_custom_config(self):
        """Test custom configuration values"""
        config = RetrievalConfig(
            strategy="tags_only", max_results=10, cache_enabled=False
        )

        assert config.strategy == "tags_only"
        assert config.max_results == 10
        assert config.cache_enabled is False


class TestRetrievalCache:
    """Test RetrievalCache class"""

    def test_cache_operations(self):
        """Test basic cache operations"""
        cache = RetrievalCache(max_size=2, ttl=300)

        # Test put and get
        results = [{"item": {"content": "test"}, "score": 0.9}]
        cache.put("test_strategy", ["tag1"], "test query", 5, results)

        cached = cache.get("test_strategy", ["tag1"], "test query", 5)
        assert cached == results

    def test_cache_expiration(self):
        """Test cache TTL expiration"""
        cache = RetrievalCache(max_size=10, ttl=1)  # 1 second TTL

        results = [{"item": {"content": "test"}, "score": 0.9}]
        cache.put("test_strategy", ["tag1"], "test query", 5, results)

        # Should be available immediately
        cached = cache.get("test_strategy", ["tag1"], "test query", 5)
        assert cached == results

        # Mock time to simulate expiration
        import time

        original_time = time.time
        time.time = lambda: original_time() + 2  # 2 seconds later

        try:
            # Should be expired now
            cached = cache.get("test_strategy", ["tag1"], "test query", 5)
            assert cached is None
        finally:
            time.time = original_time

    def test_cache_lru_eviction(self):
        """Test LRU eviction when cache is full"""
        cache = RetrievalCache(max_size=2, ttl=300)

        # Fill cache
        cache.put("s1", ["t1"], "q1", 5, [{"score": 0.9}])
        cache.put("s2", ["t2"], "q2", 5, [{"score": 0.8}])

        # Add third item (should evict first)
        cache.put("s3", ["t3"], "q3", 5, [{"score": 0.7}])

        # First item should be evicted
        assert cache.get("s1", ["t1"], "q1", 5) is None
        assert cache.get("s2", ["t2"], "q2", 5) is not None


class TestTagBasedRetriever:
    """Test TagBasedRetriever class"""

    def test_retrieval_with_matching_tags(self):
        """Test tag-based retrieval with matching tags"""
        # Setup mock context storage
        context_storage = Mock(spec=ContextStorage)

        # Create test context items
        items = [
            ContextItem(
                content="Test content 1",
                tags=["api", "authentication"],
                category=ContextCategory.SESSION,
                timestamp=datetime.now(),
            ),
            ContextItem(
                content="Test content 2",
                tags=["database", "query"],
                category=ContextCategory.TASK,
                timestamp=datetime.now(),
            ),
        ]
        context_storage.get_all_context_items.return_value = items

        # Create retriever
        config = {"tag_normalization": {"include_related_tags": False}}
        retriever = TagBasedRetriever(context_storage, config)

        # Test retrieval
        results = retriever.retrieve(["api"], "test query", 5)

        assert len(results) == 1
        # Tag normalizer expands "api" to include its synonyms
        # Check that "api" is in the matched tags
        assert "api" in results[0]["matched_tags"]
        assert results[0]["score"] > 0

    def test_retrieval_no_matches(self):
        """Test tag-based retrieval with no matches"""
        context_storage = Mock(spec=ContextStorage)
        context_storage.get_all_context_items.return_value = []

        config = {"tag_normalization": {"include_related_tags": False}}
        retriever = TagBasedRetriever(context_storage, config)

        results = retriever.retrieve(["nonexistent"], "test query", 5)

        assert len(results) == 0


class TestRetrieverFactory:
    """Test RetrieverFactory class"""

    def test_create_tag_based_retriever(self):
        """Test creating tag-based retriever"""
        context_storage = Mock(spec=ContextStorage)

        retriever = RetrieverFactory.create_retriever(
            context_storage, {"strategy": "tags_only"}
        )

        assert isinstance(retriever, TagBasedRetriever)

    def test_create_hybrid_retriever(self):
        """Test creating hybrid retriever"""
        context_storage = Mock(spec=ContextStorage)

        retriever = RetrieverFactory.create_retriever(
            context_storage, {"strategy": "hybrid"}
        )

        assert isinstance(retriever, HybridRetriever)

    def test_create_with_config_object(self):
        """Test creating retriever with RetrievalConfig"""
        context_storage = Mock(spec=ContextStorage)
        config = RetrievalConfig(strategy="auto")

        retriever = RetrieverFactory.create_retriever_with_config(
            context_storage, config
        )

        assert isinstance(retriever, AutoRetriever)

    def test_unknown_strategy(self):
        """Test error handling for unknown strategy"""
        context_storage = Mock(spec=ContextStorage)

        with pytest.raises(ValueError, match="Unknown retrieval strategy"):
            RetrieverFactory.create_retriever(
                context_storage, {"strategy": "unknown_strategy"}
            )

    def test_get_available_strategies(self):
        """Test getting available strategies"""
        strategies = RetrieverFactory.get_available_strategies()

        expected = ["tags_only", "embeddings_only", "hybrid", "auto"]
        assert strategies == expected


class TestErrorHandling:
    """Test error handling across retrievers"""

    def test_missing_dependencies_handling(self):
        """Test graceful handling of missing dependencies"""
        context_storage = Mock(spec=ContextStorage)

        # Mock ImportError in EmbeddingModel
        with patch(
            "vivek.agentic_context.retrieval.retrieval_strategies.EmbeddingModel"
        ) as mock_model:
            mock_model.side_effect = ImportError("sentence-transformers not installed")

            with pytest.raises(
                ImportError, match="Failed to initialize EmbeddingBasedRetriever"
            ):
                EmbeddingBasedRetriever(context_storage, {})

    def test_retrieval_error_handling(self):
        """Test that retrieval errors are handled gracefully"""
        context_storage = Mock(spec=ContextStorage)
        context_storage.get_all_context_items.side_effect = Exception("Database error")

        config = {"tag_normalization": {"include_related_tags": False}}
        retriever = TagBasedRetriever(context_storage, config)

        # Should return empty list instead of raising exception
        results = retriever.retrieve(["test"], "test query", 5)
        assert results == []


if __name__ == "__main__":
    # Run basic functionality test
    print("Running basic retrieval strategies tests...")

    # Test configuration
    config = RetrievalConfig()
    print(f"✓ Default config created: {config.strategy}")

    # Test cache
    cache = RetrievalCache()
    cache.put("test", ["tag"], "query", 5, [{"test": "result"}])
    result = cache.get("test", ["tag"], "query", 5)
    print(f"✓ Cache operations working: {len(result) if result else 0} items")

    # Test factory
    strategies = RetrieverFactory.get_available_strategies()
    print(f"✓ Available strategies: {strategies}")

    print("All basic tests passed! ✓")
