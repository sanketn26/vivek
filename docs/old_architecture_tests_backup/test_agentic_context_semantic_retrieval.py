"""
Unit tests for agentic_context.retrieval.semantic_retrieval module
"""

from unittest.mock import Mock, patch

import numpy as np
import pytest

from vivek.agentic_context.retrieval.semantic_retrieval import (
    EmbeddingModel,
    SemanticRetriever,
    SemanticSimilarity,
)


class TestEmbeddingModel:
    """Test EmbeddingModel functionality"""

    def setup_method(self):
        """Set up EmbeddingModel for each test"""
        # Use a small model for testing
        self.model_name = "all-MiniLM-L6-v2"

    def test_initialization(self):
        """Test EmbeddingModel initialization"""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_model = Mock()
            mock_model.get_sentence_embedding_dimension.return_value = 384
            mock_st.return_value = mock_model

            model = EmbeddingModel(self.model_name, cache_size=100)

            assert model.model_name == self.model_name
            assert model.cache_size == 100
            assert model.model == mock_model
            mock_st.assert_called_once_with(self.model_name, device="cpu")

    def test_initialization_with_custom_device(self):
        """Test initialization with custom device"""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            EmbeddingModel(self.model_name, device="cuda")
            mock_st.assert_called_once_with(self.model_name, device="cuda")

    def test_initialization_missing_dependency(self):
        """Test initialization handles missing sentence-transformers"""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_st.side_effect = ImportError("sentence-transformers not installed")

            with pytest.raises(
                ImportError, match="sentence-transformers not installed"
            ):
                EmbeddingModel(self.model_name)

    def test_initialization_model_load_error(self):
        """Test initialization handles model loading errors"""
        with patch("sentence_transformers.SentenceTransformer") as mock_st:
            mock_st.side_effect = Exception("Model load failed")

            with pytest.raises(RuntimeError, match="Failed to load model"):
                EmbeddingModel(self.model_name)

    def test_encode_empty_text(self):
        """Test encoding empty text"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name)

            # Mock the model to avoid actual computation
            model.model = Mock()
            model.model.encode.return_value = np.array([0.1, 0.2, 0.3])
            model.model.get_sentence_embedding_dimension.return_value = 3

            # Test empty text
            embedding = model.encode("")
            expected_zero = np.zeros(3)
            np.testing.assert_array_equal(embedding, expected_zero)

    def test_encode_whitespace_text(self):
        """Test encoding whitespace-only text"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name)

            model.model = Mock()
            model.model.encode.return_value = np.array([0.1, 0.2, 0.3])
            model.model.get_sentence_embedding_dimension.return_value = 3

            # Test whitespace text
            embedding = model.encode("   \n\t   ")
            expected_zero = np.zeros(3)
            np.testing.assert_array_equal(embedding, expected_zero)

    def test_encode_with_caching(self):
        """Test encoding with caching enabled"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name, cache_size=10)

            model.model = Mock()
            model.model.encode.return_value = np.array([0.1, 0.2, 0.3])
            model.model.get_sentence_embedding_dimension.return_value = 3

            # First encode
            embedding1 = model.encode("test text")

            # Second encode of same text should use cache
            embedding2 = model.encode("test text")

            # Model should only be called once due to caching
            assert model.model.encode.call_count == 1
            np.testing.assert_array_equal(embedding1, embedding2)

    def test_encode_without_caching(self):
        """Test encoding with caching disabled"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name)

            # Disable caching by using cache size 0
            model.cache_size = 0

            model.model = Mock()
            model.model.encode.return_value = np.array([0.1, 0.2, 0.3])
            model.model.get_sentence_embedding_dimension.return_value = 3

            # Encode same text twice
            model.encode("test text")
            model.encode("test text")

            # Model should be called twice since caching is disabled
            assert model.model.encode.call_count == 2

    def test_encode_cache_eviction(self):
        """Test cache eviction when full"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name, cache_size=2)

            model.model = Mock()
            model.model.encode.return_value = np.array([0.1, 0.2, 0.3])
            model.model.get_sentence_embedding_dimension.return_value = 3

            # Fill cache
            model.encode("text1")
            model.encode("text2")

            # Add one more to trigger eviction
            model.encode("text3")

            # Cache should have evicted one entry
            assert len(model._embedding_cache) == 2

    def test_encode_batch_empty(self):
        """Test batch encoding empty list"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name)

            model.model = Mock()
            model.model.get_sentence_embedding_dimension.return_value = 3

            embeddings = model.encode_batch([])
            assert embeddings == []

    def test_encode_batch_with_empty_texts(self):
        """Test batch encoding with empty texts"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name)

            model.model = Mock()
            model.model.encode.return_value = np.array([[0.1, 0.2, 0.3]])
            model.model.get_sentence_embedding_dimension.return_value = 3

            embeddings = model.encode_batch(["", "   ", "valid text"])

            # Empty texts should get zero vectors
            assert len(embeddings) == 3
            np.testing.assert_array_equal(embeddings[0], np.zeros(3))
            np.testing.assert_array_equal(embeddings[1], np.zeros(3))
            # Valid text should get result from model
            np.testing.assert_array_equal(embeddings[2], np.array([0.1, 0.2, 0.3]))

    def test_encode_batch_with_caching(self):
        """Test batch encoding with caching"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name, cache_size=10)

            model.model = Mock()
            # First call encodes 2 texts in batch, returns 2D array
            model.model.encode.return_value = np.array(
                [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]  # text1  # text2
            )
            model.model.get_sentence_embedding_dimension.return_value = 3

            # First batch with new texts
            embeddings1 = model.encode_batch(["text1", "text2"])

            # Second batch with same texts should use cache
            embeddings2 = model.encode_batch(["text1", "text2"])

            # Model should only be called once due to caching
            assert model.model.encode.call_count == 1
            np.testing.assert_array_equal(embeddings1[0], embeddings2[0])
            np.testing.assert_array_equal(embeddings1[1], embeddings2[1])

    def test_get_embedding_dim(self):
        """Test getting embedding dimension"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name)

            model.model = Mock()
            model.model.get_sentence_embedding_dimension.return_value = 768

            assert model.get_embedding_dim() == 768

    def test_get_embedding_dim_no_model(self):
        """Test getting embedding dimension when model not loaded"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name)

            # Don't set model
            model.model = None

            # Should return default dimension
            assert model.get_embedding_dim() == 768

    def test_clear_cache(self):
        """Test clearing embedding cache"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name)

            # Add some cache entries
            model._embedding_cache["key1"] = np.array([0.1, 0.2])
            model._embedding_cache["key2"] = np.array([0.3, 0.4])

            assert len(model._embedding_cache) == 2

            # Clear cache
            model.clear_cache()

            assert len(model._embedding_cache) == 0

    def test_get_cache_stats(self):
        """Test getting cache statistics"""
        with patch("sentence_transformers.SentenceTransformer"):
            model = EmbeddingModel(self.model_name, cache_size=100)

            # Add some cache entries
            model._embedding_cache["key1"] = np.array([0.1, 0.2])
            model._embedding_cache["key2"] = np.array([0.3, 0.4])

            stats = model.get_cache_stats()

            assert stats["cache_size"] == 2
            assert stats["cache_limit"] == 100


class TestSemanticSimilarity:
    """Test SemanticSimilarity functionality"""

    def test_cosine_similarity_identical(self):
        """Test cosine similarity with identical vectors"""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([1.0, 2.0, 3.0])

        similarity = SemanticSimilarity.cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0, abs=1e-6)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity with orthogonal vectors"""
        vec1 = np.array([1.0, 0.0])
        vec2 = np.array([0.0, 1.0])

        similarity = SemanticSimilarity.cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0, abs=1e-6)

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity with opposite vectors"""
        vec1 = np.array([1.0, 2.0])
        vec2 = np.array([-1.0, -2.0])

        similarity = SemanticSimilarity.cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(-1.0, abs=1e-6)

    def test_cosine_similarity_zero_vector(self):
        """Test cosine similarity with zero vector"""
        vec1 = np.array([1.0, 2.0])
        vec2 = np.array([0.0, 0.0])

        similarity = SemanticSimilarity.cosine_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_cosine_similarity_both_zero(self):
        """Test cosine similarity with both vectors zero"""
        vec1 = np.array([0.0, 0.0])
        vec2 = np.array([0.0, 0.0])

        similarity = SemanticSimilarity.cosine_similarity(vec1, vec2)
        assert similarity == 0.0

    def test_euclidean_distance_identical(self):
        """Test Euclidean distance with identical vectors"""
        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([1.0, 2.0, 3.0])

        distance = SemanticSimilarity.euclidean_distance(vec1, vec2)
        assert distance == pytest.approx(0.0, abs=1e-6)

    def test_euclidean_distance_different(self):
        """Test Euclidean distance with different vectors"""
        vec1 = np.array([0.0, 0.0])
        vec2 = np.array([3.0, 4.0])

        distance = SemanticSimilarity.euclidean_distance(vec1, vec2)
        assert distance == pytest.approx(5.0, abs=1e-6)  # sqrt(3^2 + 4^2)

    def test_batch_cosine_similarity(self):
        """Test batch cosine similarity calculation"""
        query = np.array([1.0, 0.0])

        embeddings = [
            np.array([1.0, 0.0]),  # Same as query
            np.array([0.0, 1.0]),  # Orthogonal to query
            np.array([-1.0, 0.0]),  # Opposite to query
        ]

        similarities = SemanticSimilarity.batch_cosine_similarity(query, embeddings)

        assert len(similarities) == 3
        assert similarities[0] == pytest.approx(1.0, abs=1e-6)  # Same
        assert similarities[1] == pytest.approx(0.0, abs=1e-6)  # Orthogonal
        assert similarities[2] == pytest.approx(-1.0, abs=1e-6)  # Opposite

    def test_batch_cosine_similarity_empty(self):
        """Test batch cosine similarity with empty list"""
        query = np.array([1.0, 0.0])
        similarities = SemanticSimilarity.batch_cosine_similarity(query, [])
        assert similarities == []

    def test_batch_cosine_similarity_zero_query(self):
        """Test batch cosine similarity with zero query vector"""
        query = np.array([0.0, 0.0])

        embeddings = [np.array([1.0, 0.0]), np.array([0.0, 1.0])]

        similarities = SemanticSimilarity.batch_cosine_similarity(query, embeddings)

        assert len(similarities) == 2
        assert similarities[0] == 0.0
        assert similarities[1] == 0.0


class TestSemanticRetriever:
    """Test SemanticRetriever functionality"""

    def setup_method(self):
        """Set up SemanticRetriever for each test"""
        with patch(
            "vivek.agentic_context.retrieval.semantic_retrieval.EmbeddingModel"
        ) as mock_model_class:
            self.mock_model = Mock()
            self.mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
            self.mock_model.get_sentence_embedding_dimension.return_value = 3
            mock_model_class.return_value = self.mock_model

            self.retriever = SemanticRetriever(self.mock_model)

    def test_initialization(self):
        """Test SemanticRetriever initialization"""
        assert self.retriever.embedding_model == self.mock_model
        assert self.retriever.similarity is not None

    def test_retrieve_empty_items(self):
        """Test retrieving from empty item list"""
        results = self.retriever.retrieve("test query", [], top_k=5)
        assert results == []

    def test_retrieve_with_embeddings(self):
        """Test retrieving with pre-computed embeddings"""
        # Create items with embeddings
        items = [
            {
                "content": "Authentication middleware",
                "tags": ["auth", "middleware"],
                "embedding": np.array([0.1, 0.2, 0.3]),
            },
            {
                "content": "Database query optimization",
                "tags": ["database", "performance"],
                "embedding": np.array([0.4, 0.5, 0.6]),
            },
        ]

        # Mock similarity calculation
        with patch.object(
            self.retriever.similarity, "batch_cosine_similarity"
        ) as mock_similarity:
            mock_similarity.return_value = [0.8, 0.3]  # First item more similar

            results = self.retriever.retrieve(
                "auth system", items, top_k=5, min_score=0.0
            )

            assert len(results) == 2
            # Should be sorted by similarity score
            assert results[0]["semantic_score"] == 0.8
            assert results[1]["semantic_score"] == 0.3

    def test_retrieve_without_embeddings(self):
        """Test retrieving without pre-computed embeddings"""
        items = [
            {"content": "Authentication middleware", "tags": ["auth"]},
            {"content": "Database query", "tags": ["database"]},
        ]

        # Mock similarity calculation
        with patch.object(
            self.retriever.similarity, "batch_cosine_similarity"
        ) as mock_similarity:
            mock_similarity.return_value = [0.8, 0.3]

            results = self.retriever.retrieve(
                "auth system", items, top_k=5, min_score=0.0
            )

            assert len(results) == 2
            # Should generate embeddings from content
            assert self.mock_model.encode.call_count >= 2  # At least query + items

    def test_retrieve_with_min_score_filtering(self):
        """Test retrieving with minimum score filtering"""
        items = [
            {"content": "High similarity", "tags": ["test"]},
            {"content": "Low similarity", "tags": ["test"]},
        ]

        with patch.object(
            self.retriever.similarity, "batch_cosine_similarity"
        ) as mock_similarity:
            mock_similarity.return_value = [0.8, 0.2]  # One above, one below threshold

            results = self.retriever.retrieve("test", items, top_k=5, min_score=0.5)

            # Should only return high similarity item
            assert len(results) == 1
            assert results[0]["semantic_score"] == 0.8

    def test_retrieve_with_top_k_limiting(self):
        """Test retrieving with top-k limiting"""
        items = [{"content": f"Item {i}", "tags": ["test"]} for i in range(5)]

        with patch.object(
            self.retriever.similarity, "batch_cosine_similarity"
        ) as mock_similarity:
            # Return scores in descending order
            mock_similarity.return_value = [0.9, 0.8, 0.7, 0.6, 0.5]

            results = self.retriever.retrieve("test", items, top_k=3, min_score=0.0)

            # Should only return top 3
            assert len(results) == 3
            assert results[0]["semantic_score"] == 0.9
            assert results[1]["semantic_score"] == 0.8
            assert results[2]["semantic_score"] == 0.7

    def test_format_item_for_embedding(self):
        """Test formatting item for embedding"""
        item = {
            "content": "Authentication middleware",
            "tags": ["auth", "security", "middleware"],
        }

        formatted = self.retriever._format_item_for_embedding(item)

        # Should combine content and tags
        assert "Authentication middleware" in formatted
        assert "auth" in formatted
        assert "security" in formatted
        assert "middleware" in formatted

    def test_format_item_for_embedding_content_only(self):
        """Test formatting item with content only"""
        item = {"content": "Simple content"}

        formatted = self.retriever._format_item_for_embedding(item)
        assert formatted == "Simple content"

    def test_format_item_for_embedding_tags_only(self):
        """Test formatting item with tags only"""
        item = {"tags": ["tag1", "tag2"]}

        formatted = self.retriever._format_item_for_embedding(item)
        assert "tag1 tag2" == formatted

    def test_precompute_embeddings(self):
        """Test pre-computing embeddings for items"""
        items = [
            {"content": "Item 1", "tags": ["tag1"]},
            {"content": "Item 2", "tags": ["tag2"]},
        ]

        # Mock batch encoding
        self.mock_model.encode_batch.return_value = [
            np.array([0.1, 0.2]),
            np.array([0.3, 0.4]),
        ]

        result = self.retriever.precompute_embeddings(items)

        # Should add embeddings to items
        assert "embedding" in result[0]
        assert "embedding" in result[1]
        np.testing.assert_array_equal(result[0]["embedding"], np.array([0.1, 0.2]))
        np.testing.assert_array_equal(result[1]["embedding"], np.array([0.3, 0.4]))

        # Should call batch encoding
        self.mock_model.encode_batch.assert_called_once()
