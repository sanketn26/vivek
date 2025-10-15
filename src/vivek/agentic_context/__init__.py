"""
Agentic Context - Internal Context Management for Small LLM Agents

Clean API for automatic context tracking in hierarchical workflows.
"""

# Main workflow interface (what most users need)
from .workflow import ContextWorkflow, SessionContext, ActivityContext, TaskContext

# Configuration
from .config import Config, get_config


# Advanced imports (for power users)
from .core.context_storage import ContextStorage, ContextCategory, ContextItem

from .retrieval.retrieval_strategies import (
    BaseRetriever,
    TagBasedRetriever,
    EmbeddingBasedRetriever,
    HybridRetriever,
    AutoRetriever,
    RetrieverFactory,
)

from .retrieval.tag_normalization import TagVocabulary, TagNormalizer

from .retrieval.semantic_retrieval import (
    EmbeddingModel,
    SemanticSimilarity,
    SemanticRetriever,
)


# Public API
__all__ = [
    # Main interface
    "ContextWorkflow",
    "SessionContext",
    "ActivityContext",
    "TaskContext",
    # Configuration
    "Config",
    "get_config",
    # Advanced
    "ContextStorage",
    "ContextCategory",
    "ContextItem",
    "RetrieverFactory",
    "TagVocabulary",
    "TagNormalizer",
    "EmbeddingModel",
]
