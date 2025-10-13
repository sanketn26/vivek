"""
Semantic Retrieval using Embeddings
"""

import numpy as np
from typing import List, Dict, Any
import hashlib


class EmbeddingModel:
    """
    Wrapper for embedding models with caching
    Supports multiple backends (sentence-transformers, etc.)
    """

    def __init__(
        self,
        model_name: str = "microsoft/codebert-base",
        cache_size: int = 1000,
        device: str = "cpu",
    ):
        """
        Initialize embedding model

        Args:
            model_name: Name of the model to use
                - "microsoft/codebert-base" (best for code)
                - "sentence-transformers/all-mpnet-base-v2" (general purpose)
                - "all-MiniLM-L6-v2" (lightweight)
            cache_size: Size of LRU cache for embeddings
            device: "cpu" or "cuda"
        """
        self.model_name = model_name
        self.cache_size = cache_size
        self.device = device
        self.model = None
        self._embedding_cache: Dict[str, np.ndarray] = {}
        self._load_model()

    def _load_model(self):
        """Lazy load the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name, device=self.device)
            print(f"✓ Loaded embedding model: {self.model_name}")
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load model {self.model_name}: {e}")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        return hashlib.md5(text.encode()).hexdigest()

    def encode(self, text: str, use_cache: bool = True) -> np.ndarray:
        """
        Generate embedding for text

        Args:
            text: Input text to embed
            use_cache: Whether to use cached embeddings

        Returns:
            numpy array of embedding vector
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.get_embedding_dim())

        cache_key = self._get_cache_key(text)

        # Check cache
        if use_cache and cache_key in self._embedding_cache:
            return self._embedding_cache[cache_key]

        # Generate embedding
        embedding = self.model.encode(
            text, convert_to_tensor=False, show_progress_bar=False
        )

        # Cache if enabled
        if use_cache and self.cache_size > 0:
            # Implement simple cache size limit
            if len(self._embedding_cache) >= self.cache_size:
                # Remove oldest entry (simple FIFO)
                first_key = next(iter(self._embedding_cache))
                self._embedding_cache.pop(first_key)
            self._embedding_cache[cache_key] = embedding

        return embedding

    def encode_batch(
        self, texts: List[str], use_cache: bool = True
    ) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts
        More efficient than encoding one by one
        """
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            if not text or not text.strip():
                embeddings.append(np.zeros(self.get_embedding_dim()))
                continue

            cache_key = self._get_cache_key(text)
            if use_cache and cache_key in self._embedding_cache:
                embeddings.append(self._embedding_cache[cache_key])
            else:
                embeddings.append(None)  # Placeholder
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Batch encode uncached texts
        if uncached_texts:
            batch_embeddings = self.model.encode(
                uncached_texts, convert_to_tensor=False, show_progress_bar=False
            )

            # Fill in results and cache
            for idx, emb, text in zip(
                uncached_indices, batch_embeddings, uncached_texts
            ):
                embeddings[idx] = emb
                if use_cache and self.cache_size > 0:
                    cache_key = self._get_cache_key(text)
                    if len(self._embedding_cache) >= self.cache_size:
                        first_key = next(iter(self._embedding_cache))
                        self._embedding_cache.pop(first_key)
                    self._embedding_cache[cache_key] = emb

        return embeddings

    def get_embedding_dim(self) -> int:
        """Get dimensionality of embeddings"""
        if self.model:
            return self.model.get_sentence_embedding_dimension()
        return 768  # Default for most models

    def clear_cache(self):
        """Clear embedding cache"""
        self._embedding_cache.clear()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "cache_size": len(self._embedding_cache),
            "cache_limit": self.cache_size,
        }


class SemanticSimilarity:
    """
    Calculate semantic similarity between texts using embeddings
    """

    @staticmethod
    def cosine_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        Returns value between -1 and 1 (1 = identical, 0 = orthogonal, -1 = opposite)
        """
        # Handle zero vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))

    @staticmethod
    def euclidean_distance(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate Euclidean distance between embeddings
        Lower is more similar
        """
        return float(np.linalg.norm(embedding1 - embedding2))

    @staticmethod
    def batch_cosine_similarity(
        query_embedding: np.ndarray, embeddings: List[np.ndarray]
    ) -> List[float]:
        """
        Calculate cosine similarity between query and multiple embeddings
        Optimized for batch processing
        """
        if not embeddings:
            return []

        # Stack embeddings into matrix
        embedding_matrix = np.vstack(embeddings)

        # Normalize query
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return [0.0] * len(embeddings)

        normalized_query = query_embedding / query_norm

        # Normalize all embeddings
        norms = np.linalg.norm(embedding_matrix, axis=1, keepdims=True)
        norms[norms == 0] = 1  # Avoid division by zero
        normalized_embeddings = embedding_matrix / norms

        # Compute similarities
        similarities = np.dot(normalized_embeddings, normalized_query)

        return similarities.tolist()


class SemanticRetriever:
    """
    Retrieves context items based on semantic similarity
    """

    def __init__(self, embedding_model: EmbeddingModel):
        self.embedding_model = embedding_model
        self.similarity = SemanticSimilarity()

    def retrieve(
        self,
        query: str,
        items: List[Dict[str, Any]],
        top_k: int = 5,
        min_score: float = 0.0,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve top-k most semantically similar items

        Args:
            query: Query text
            items: List of items with 'content' and optionally 'embedding'
            top_k: Number of results to return
            min_score: Minimum similarity score threshold

        Returns:
            List of items with similarity scores
        """
        if not items:
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)

        # Get or generate embeddings for items
        item_embeddings = []
        for item in items:
            if "embedding" in item and item["embedding"] is not None:
                # Use pre-computed embedding
                item_embeddings.append(item["embedding"])
            else:
                # Generate embedding from content
                content = self._format_item_for_embedding(item)
                embedding = self.embedding_model.encode(content)
                item_embeddings.append(embedding)

        # Calculate similarities
        similarities = self.similarity.batch_cosine_similarity(
            query_embedding, item_embeddings
        )

        # Create results with scores
        results = []
        for item, score in zip(items, similarities):
            if score >= min_score:
                results.append({"item": item, "semantic_score": score})

        # Sort by score and return top-k
        results.sort(key=lambda x: x["semantic_score"], reverse=True)
        return results[:top_k]

    def _format_item_for_embedding(self, item: Dict[str, Any]) -> str:
        """
        Format item content for embedding
        Combines content and tags for better representation
        """
        parts = []

        if "content" in item:
            parts.append(item["content"])

        if "tags" in item and item["tags"]:
            parts.append(" ".join(item["tags"]))

        return " ".join(parts)

    def precompute_embeddings(
        self, items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Pre-compute and store embeddings for items
        Useful when storing items in context DB
        """
        texts = [self._format_item_for_embedding(item) for item in items]
        embeddings = self.embedding_model.encode_batch(texts)

        # Add embeddings to items
        for item, embedding in zip(items, embeddings):
            item["embedding"] = embedding

        return items
