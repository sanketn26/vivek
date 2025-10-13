"""
Retrieval Strategies: Tag-based, Embedding-based, Hybrid, and Auto

Comprehensive retrieval system providing multiple strategies for context retrieval:
- Tag-based: Fast keyword + tag normalization retrieval
- Embedding-based: Pure semantic similarity using embeddings
- Hybrid: Two-stage retrieval combining tag filtering + semantic reranking
- Auto: Intelligent strategy selection based on query characteristics

Features:
- Pluggable architecture for easy strategy extension
- Efficient similarity calculations with caching
- Configurable retrieval parameters
- Error handling for missing dependencies
- Performance optimizations

Example:
    >>> config = {
    ...     "retrieval": {"strategy": "hybrid"},
    ...     "semantic": {"model": "microsoft/codebert-base", "cache_size": 1000},
    ...     "tag_normalization": {"include_related_tags": True}
    ... }
    >>> factory = RetrieverFactory()
    >>> retriever = factory.create_retriever(context_storage, config)
    >>> results = retriever.retrieve(["api", "auth"], "Create JWT middleware", 5)
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import time
import functools
from dataclasses import dataclass

from vivek.agentic_context.retrieval.tag_normalization import TagNormalizer, TagVocabulary
from vivek.agentic_context.retrieval.semantic_retrieval import (
    EmbeddingModel,
    SemanticRetriever,
    SemanticSimilarity
)
from vivek.agentic_context.core.context_storage import ContextStorage, ContextItem


class RetrievalStrategy(Enum):
    """Available retrieval strategies"""

    TAGS_ONLY = "tags_only"
    EMBEDDINGS_ONLY = "embeddings_only"
    HYBRID = "hybrid"
    AUTO = "auto"


@dataclass
class RetrievalConfig:
    """Configuration for retrieval strategies with validation and defaults"""

    strategy: str = "hybrid"
    max_results: int = 5
    min_score: float = 0.0

    # Tag-based configuration
    tag_normalization: Optional[Dict[str, Any]] = None
    max_candidates: int = 20

    # Semantic configuration
    semantic: Optional[Dict[str, Any]] = None

    # Auto strategy configuration
    auto: Optional[Dict[str, Any]] = None

    # Caching configuration
    cache_enabled: bool = True
    cache_ttl: int = 300  # 5 minutes

    def __post_init__(self):
        """Set defaults for nested configurations"""
        if self.tag_normalization is None:
            self.tag_normalization = {
                "include_related_tags": False,
                "max_candidates": self.max_candidates
            }

        if self.semantic is None:
            self.semantic = {
                "model": "microsoft/codebert-base",
                "cache_size": 1000,
                "device": "cpu",
                "min_score": self.min_score,
                "score_weight": 0.6
            }

        if self.auto is None:
            self.auto = {
                "simple_task_threshold": 2,
                "use_semantic_for_complex": True,
                "description_length_threshold": 20
            }


class RetrievalCache:
    """LRU cache for retrieval results to improve performance"""

    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _make_key(self, strategy: str, query_tags: List[str], query_desc: str, max_results: int) -> str:
        """Generate cache key from query parameters"""
        import hashlib
        key_data = f"{strategy}:{sorted(query_tags)}:{query_desc}:{max_results}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get(self, strategy: str, query_tags: List[str], query_desc: str, max_results: int) -> Optional[List[Dict[str, Any]]]:
        """Get cached results if available and not expired"""
        key = self._make_key(strategy, query_tags, query_desc, max_results)

        if key not in self._cache:
            return None

        entry = self._cache[key]
        if time.time() - entry["timestamp"] > self.ttl:
            del self._cache[key]
            return None

        return entry["results"]

    def put(self, strategy: str, query_tags: List[str], query_desc: str, max_results: int, results: List[Dict[str, Any]]):
        """Cache retrieval results"""
        key = self._make_key(strategy, query_tags, query_desc, max_results)

        # Implement simple LRU eviction
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["timestamp"])
            del self._cache[oldest_key]

        self._cache[key] = {
            "results": results,
            "timestamp": time.time()
        }

    def clear(self):
        """Clear all cached entries"""
        self._cache.clear()

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_ratio": "N/A"  # Would need hit/miss tracking for this
        }


class BaseRetriever(ABC):
    """Abstract base class for all retrieval strategies with caching and error handling"""

    def __init__(self, context_storage: ContextStorage, config: Dict[str, Any]):
        self.context_storage = context_storage
        self.config = config

        # Initialize cache if enabled
        cache_enabled = config.get("cache_enabled", True)
        cache_ttl = config.get("cache_ttl", 300)

        if cache_enabled:
            cache_size = config.get("cache_max_size", 100)
            self.cache = RetrievalCache(cache_size, cache_ttl)
        else:
            self.cache = None

        # Strategy name for caching
        self.strategy_name = self.__class__.__name__.lower().replace("retriever", "")

    def retrieve(
        self, query_tags: List[str], query_description: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context items with caching support

        Args:
            query_tags: Tags from current task/activity
            query_description: Description of current task/activity
            max_results: Maximum number of results to return

        Returns:
            List of matched items with scores and metadata
        """
        # Check cache first
        if self.cache:
            cached_results = self.cache.get(
                self.strategy_name, query_tags, query_description, max_results
            )
            if cached_results is not None:
                return cached_results

        # Perform actual retrieval
        try:
            results = self._retrieve_impl(query_tags, query_description, max_results)

            # Cache results
            if self.cache:
                self.cache.put(
                    self.strategy_name, query_tags, query_description, max_results, results
                )

            return results

        except Exception as e:
            # Enhanced error handling
            error_msg = f"Retrieval failed for strategy {self.strategy_name}: {str(e)}"
            print(f"Warning: {error_msg}")

            # Return empty results on error rather than crashing
            return []

    @abstractmethod
    def _retrieve_impl(
        self, query_tags: List[str], query_description: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Internal retrieval implementation to be implemented by subclasses

        Args:
            query_tags: Tags from current task/activity
            query_description: Description of current task/activity
            max_results: Maximum number of results to return

        Returns:
            List of matched items with scores and metadata
        """
        pass


class TagBasedRetriever(BaseRetriever):
    """
    Fast keyword + tag normalization retrieval
    Uses tag expansion and overlap scoring
    """

    def __init__(self, context_storage: ContextStorage, config: Dict[str, Any]):
        super().__init__(context_storage, config)

        # Initialize tag normalizer
        vocabulary = TagVocabulary()
        include_related = config.get("tag_normalization", {}).get(
            "include_related_tags", False
        )
        self.tag_normalizer = TagNormalizer(vocabulary, include_related)

    def _retrieve_impl(
        self, query_tags: List[str], query_description: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Retrieve using tag matching"""

        # Clean and normalize query tags
        cleaned_tags = self.tag_normalizer.clean_tags(query_tags)

        # Get all context items
        all_items = self.context_storage.get_all_context_items()

        if not all_items:
            return []

        # Calculate tag overlap for each item
        matches = []
        for item in all_items:
            overlap_info = self.tag_normalizer.calculate_tag_overlap(
                cleaned_tags, item.tags
            )

            # Only include if there's overlap
            if overlap_info["match_count"] > 0:
                matches.append(
                    {
                        "item": self._item_to_dict(item),
                        "score": overlap_info["overlap_score"],
                        "matched_tags": overlap_info["matched_tags"],
                        "category": item.category.value,
                    }
                )

        # Sort by score
        matches.sort(key=lambda x: x["score"], reverse=True)

        return matches[:max_results]

    def _item_to_dict(self, item: ContextItem) -> Dict[str, Any]:
        """Convert ContextItem to dict for results"""
        return {
            "content": item.content,
            "tags": item.tags,
            "category": item.category.value,
            "timestamp": item.timestamp.isoformat(),
            "activity_id": item.activity_id,
            "task_id": item.task_id,
            "metadata": item.metadata,
            "embedding": item.embedding,
        }


class EmbeddingBasedRetriever(BaseRetriever):
    """
    Pure semantic similarity retrieval using embeddings
    """

    def __init__(self, context_storage: ContextStorage, config: Dict[str, Any]):
        super().__init__(context_storage, config)

        # Get configuration parameters first
        semantic_config = config.get("semantic", {})
        model_name = semantic_config.get("model", "microsoft/codebert-base")
        cache_size = semantic_config.get("cache_size", 1000)
        device = semantic_config.get("device", "cpu")

        # Initialize embedding model with error handling
        try:
            self.embedding_model = EmbeddingModel(model_name, cache_size, device)
            self.semantic_retriever = SemanticRetriever(self.embedding_model)
        except ImportError as e:
            raise ImportError(
                f"Failed to initialize EmbeddingBasedRetriever: {e}. "
                "Install required dependencies: pip install sentence-transformers torch"
            ) from e
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize embedding model '{model_name}': {e}"
            ) from e

    def _retrieve_impl(
        self, query_tags: List[str], query_description: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """Retrieve using semantic similarity"""

        # Use description as query (more semantic than just tags)
        query = query_description if query_description else " ".join(query_tags)

        # Get all context items
        all_items = self.context_storage.get_all_context_items()

        if not all_items:
            return []

        # Convert to format expected by semantic retriever
        items_for_retrieval = [self._item_to_dict(item) for item in all_items]

        # Retrieve semantically similar items
        min_score = self.config.get("semantic", {}).get("min_score", 0.0)
        results = self.semantic_retriever.retrieve(
            query, items_for_retrieval, max_results, min_score
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append(
                {
                    "item": result["item"],
                    "score": result["semantic_score"],
                    "matched_tags": [],  # No tag matching in pure semantic
                    "category": result["item"]["category"],
                }
            )

        return formatted_results

    def _item_to_dict(self, item: ContextItem) -> Dict[str, Any]:
        """Convert ContextItem to dict"""
        return {
            "content": item.content,
            "tags": item.tags,
            "category": item.category.value,
            "timestamp": item.timestamp.isoformat(),
            "activity_id": item.activity_id,
            "task_id": item.task_id,
            "metadata": item.metadata,
            "embedding": item.embedding,
        }


class HybridRetriever(BaseRetriever):
    """
    Two-stage retrieval: tag-based filtering + semantic reranking
    Best of both worlds - fast and accurate
    """

    def __init__(self, context_storage: ContextStorage, config: Dict[str, Any]):
        super().__init__(context_storage, config)

        # Initialize both retrievers
        self.tag_retriever = TagBasedRetriever(context_storage, config)
        self.embedding_retriever = EmbeddingBasedRetriever(context_storage, config)

    def _retrieve_impl(
        self, query_tags: List[str], query_description: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Two-stage retrieval:
        1. Fast tag-based filtering to get candidates
        2. Semantic reranking of candidates
        """

        # Stage 1: Tag-based filtering
        max_candidates = self.config.get("tag_normalization", {}).get(
            "max_candidates", 20
        )
        candidates = self.tag_retriever.retrieve(
            query_tags, query_description, max_candidates
        )

        if not candidates:
            return []

        # If we have few candidates, just return them
        if len(candidates) <= max_results:
            return candidates

        # Stage 2: Semantic reranking
        return self._semantic_rerank(
            query_description, query_tags, candidates, max_results
        )

    def _semantic_rerank(
        self,
        query_description: str,
        query_tags: List[str],
        candidates: List[Dict[str, Any]],
        max_results: int,
    ) -> List[Dict[str, Any]]:
        """Rerank candidates using semantic similarity"""

        # Prepare query
        query = query_description if query_description else " ".join(query_tags)

        # Get embeddings for candidates (use cached if available)
        query_embedding = self.embedding_retriever.embedding_model.encode(query)

        # Calculate semantic scores
        semantic_config = self.config.get("semantic", {})
        semantic_weight = semantic_config.get("score_weight", 0.6)
        tag_weight = 1.0 - semantic_weight

        for candidate in candidates:
            item = candidate["item"]

            # Get or compute embedding
            if item.get("embedding") is not None:
                item_embedding = item["embedding"]
            else:
                item_text = f"{item['content']} {' '.join(item['tags'])}"
                item_embedding = self.embedding_retriever.embedding_model.encode(
                    item_text
                )

            # Calculate semantic similarity
            semantic_score = SemanticSimilarity.cosine_similarity(
                query_embedding, item_embedding
            )

            # Combine scores
            tag_score = candidate["score"]
            candidate["final_score"] = (tag_weight * tag_score) + (
                semantic_weight * semantic_score
            )
            candidate["semantic_score"] = semantic_score
            candidate["tag_score"] = tag_score

        # Re-sort by final score
        candidates.sort(key=lambda x: x["final_score"], reverse=True)

        return candidates[:max_results]


class AutoRetriever(BaseRetriever):
    """
    Automatically choose strategy based on query characteristics
    Simple heuristics to decide between tag-only and hybrid
    """

    def __init__(self, context_storage: ContextStorage, config: Dict[str, Any]):
        super().__init__(context_storage, config)

        # Initialize both strategies
        self.tag_retriever = TagBasedRetriever(context_storage, config)
        self.hybrid_retriever = HybridRetriever(context_storage, config)

    def _retrieve_impl(
        self, query_tags: List[str], query_description: str, max_results: int
    ) -> List[Dict[str, Any]]:
        """
        Automatically choose retrieval strategy based on query
        """

        auto_config = self.config.get("auto", {})
        simple_threshold = auto_config.get("simple_task_threshold", 2)
        use_semantic_for_complex = auto_config.get("use_semantic_for_complex", True)

        # Decision logic
        is_simple = len(query_tags) < simple_threshold
        has_description = bool(query_description and len(query_description) > 20)

        # Simple query with few tags → use tag-only (faster)
        if is_simple and not has_description:
            return self.tag_retriever.retrieve(
                query_tags, query_description, max_results
            )

        # Complex query → use hybrid (more accurate)
        if use_semantic_for_complex:
            return self.hybrid_retriever.retrieve(
                query_tags, query_description, max_results
            )

        # Fallback to tag-based
        return self.tag_retriever.retrieve(query_tags, query_description, max_results)


class RetrieverFactory:
    """
    Factory to create appropriate retriever based on configuration

    Supports both legacy configuration format and new RetrievalConfig format.
    Provides validation and helpful error messages for configuration issues.
    """

    @staticmethod
    def create_retriever(
        context_storage: ContextStorage,
        config: Optional[Dict[str, Any]] = None,
        strategy: Optional[str] = None
    ) -> BaseRetriever:
        """
        Create retriever based on strategy in config

        Args:
            context_storage: ContextStorage instance
            config: Configuration dict with retrieval settings
            strategy: Override strategy (optional)

        Returns:
            Appropriate retriever instance

        Raises:
            ValueError: If strategy is unknown or configuration is invalid
        """
        if config is None:
            config = {}

        # Determine strategy
        if strategy is None:
            # Support both new and legacy config formats
            if "strategy" in config:
                strategy = config["strategy"]
            else:
                strategy = config.get("retrieval", {}).get("strategy", "hybrid")

        # Validate strategy
        valid_strategies = [s.value for s in RetrievalStrategy]
        if strategy not in valid_strategies:
            raise ValueError(
                f"Unknown retrieval strategy: {strategy}. "
                f"Valid options: {valid_strategies}"
            )

        # Create retriever with error handling
        retriever_map = {
            RetrievalStrategy.TAGS_ONLY.value: TagBasedRetriever,
            RetrievalStrategy.EMBEDDINGS_ONLY.value: EmbeddingBasedRetriever,
            RetrievalStrategy.HYBRID.value: HybridRetriever,
            RetrievalStrategy.AUTO.value: AutoRetriever,
        }

        retriever_class = retriever_map.get(strategy)
        if not retriever_class:
            raise ValueError(f"Unsupported strategy: {strategy}")

        try:
            return retriever_class(context_storage, config)
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize {strategy} retriever: {e}"
            ) from e

    @staticmethod
    def create_retriever_with_config(
        context_storage: ContextStorage,
        retrieval_config: RetrievalConfig
    ) -> BaseRetriever:
        """
        Create retriever using RetrievalConfig dataclass

        Args:
            context_storage: ContextStorage instance
            retrieval_config: Validated configuration object

        Returns:
            Appropriate retriever instance
        """
        # Convert config to dict format for retriever
        config_dict = {
            "strategy": retrieval_config.strategy,
            "max_results": retrieval_config.max_results,
            "min_score": retrieval_config.min_score,
            "tag_normalization": retrieval_config.tag_normalization or {},
            "semantic": retrieval_config.semantic or {},
            "auto": retrieval_config.auto or {},
            "cache_enabled": retrieval_config.cache_enabled,
            "cache_ttl": retrieval_config.cache_ttl,
        }

        return RetrieverFactory.create_retriever(context_storage, config_dict)

    @staticmethod
    def get_available_strategies() -> List[str]:
        """Get list of available retrieval strategies"""
        return [s.value for s in RetrievalStrategy]
