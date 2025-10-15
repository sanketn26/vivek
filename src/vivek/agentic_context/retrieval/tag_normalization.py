"""
Tag Normalization and Vocabulary Management
"""

from typing import List, Dict, Set
from dataclasses import dataclass


@dataclass
class TagDefinition:
    """Definition of a tag with its synonyms and related terms"""

    canonical: str  # The main tag name
    synonyms: List[str]  # Alternative names for the same concept
    related: List[str]  # Related but not identical concepts


class TagVocabulary:
    """
    Manages tag vocabulary with synonyms and related terms
    Expandable - start small and grow organically
    """

    def __init__(self):
        self.vocabulary: Dict[str, TagDefinition] = {}
        self._synonym_map: Dict[str, str] = {}  # Maps synonym -> canonical
        self._initialize_default_vocabulary()

    def _initialize_default_vocabulary(self):
        """Initialize with common coding-related tags"""

        # Infrastructure tags
        self.add_tag(
            "kafka",
            synonyms=["kafka-client", "message-queue", "event-streaming", "messaging"],
            related=["consumer", "producer", "broker", "topic", "streaming"],
        )

        self.add_tag(
            "consumer",
            synonyms=["kafka-consumer", "async-consumer", "event-consumer"],
            related=["kafka", "messaging", "deserialization", "offset", "subscription"],
        )

        self.add_tag(
            "producer",
            synonyms=["kafka-producer", "event-producer", "publisher"],
            related=["kafka", "messaging", "serialization", "partition"],
        )

        # Security tags
        self.add_tag(
            "authentication",
            synonyms=["auth", "jwt", "jwt-validation", "bearer-token", "token-auth"],
            related=[
                "security",
                "authorization",
                "middleware",
                "credentials",
                "session",
            ],
        )

        self.add_tag(
            "authorization",
            synonyms=["authz", "permissions", "access-control", "rbac"],
            related=["security", "authentication", "roles", "policies"],
        )

        # Error handling tags
        self.add_tag(
            "error-handling",
            synonyms=["exception-handling", "error-management", "fault-tolerance"],
            related=["logging", "retry", "circuit-breaker", "monitoring", "try-catch"],
        )

        self.add_tag(
            "logging",
            synonyms=["log", "logger", "audit", "tracing"],
            related=["monitoring", "debugging", "observability", "error-handling"],
        )

        # Data processing tags
        self.add_tag(
            "enrichment",
            synonyms=["data-enrichment", "transformation", "augmentation"],
            related=["validation", "mapping", "normalization", "processing"],
        )

        self.add_tag(
            "validation",
            synonyms=["data-validation", "schema-validation", "input-validation"],
            related=["sanitization", "verification", "constraints", "rules"],
        )

        self.add_tag(
            "serialization",
            synonyms=["encode", "marshal", "serialize"],
            related=["deserialization", "json", "protobuf", "format"],
        )

        self.add_tag(
            "deserialization",
            synonyms=["decode", "unmarshal", "deserialize", "parse"],
            related=["serialization", "json", "protobuf", "format"],
        )

        # API tags
        self.add_tag(
            "api",
            synonyms=["rest-api", "endpoint", "route", "http-api"],
            related=["rest", "http", "middleware", "handler"],
        )

        self.add_tag(
            "middleware",
            synonyms=["middleware-layer", "interceptor", "filter"],
            related=["api", "authentication", "request", "response"],
        )

        # Database tags
        self.add_tag(
            "database",
            synonyms=["db", "postgres", "mysql", "sql"],
            related=["query", "orm", "migration", "connection"],
        )

        self.add_tag(
            "query",
            synonyms=["sql-query", "database-query", "select"],
            related=["database", "filter", "join", "aggregate"],
        )

        # Testing tags
        self.add_tag(
            "testing",
            synonyms=["test", "unit-test", "integration-test"],
            related=["assertion", "mock", "fixture", "coverage"],
        )

        # Configuration tags
        self.add_tag(
            "configuration",
            synonyms=["config", "settings", "env", "environment"],
            related=["deployment", "secrets", "parameters"],
        )

        # Async/Performance tags
        self.add_tag(
            "async",
            synonyms=["asynchronous", "non-blocking", "concurrent"],
            related=["await", "promise", "threading", "coroutine"],
        )

        self.add_tag(
            "performance",
            synonyms=["optimization", "speed", "efficiency"],
            related=["caching", "indexing", "profiling", "bottleneck"],
        )

    def add_tag(
        self, canonical: str, synonyms: List[str] = None, related: List[str] = None
    ):
        """Add a new tag definition to vocabulary"""
        synonyms = synonyms or []
        related = related or []

        tag_def = TagDefinition(
            canonical=canonical.lower(),
            synonyms=[s.lower() for s in synonyms],
            related=[r.lower() for r in related],
        )

        self.vocabulary[canonical.lower()] = tag_def

        # Update synonym map
        self._synonym_map[canonical.lower()] = canonical.lower()
        for syn in synonyms:
            self._synonym_map[syn.lower()] = canonical.lower()

    def get_canonical(self, tag: str) -> str:
        """Get canonical form of a tag"""
        tag_lower = tag.lower().strip()
        return self._synonym_map.get(tag_lower, tag_lower)

    def get_synonyms(self, tag: str) -> List[str]:
        """Get all synonyms for a tag"""
        canonical = self.get_canonical(tag)
        if canonical in self.vocabulary:
            return self.vocabulary[canonical].synonyms
        return []

    def get_related(self, tag: str) -> List[str]:
        """Get related tags"""
        canonical = self.get_canonical(tag)
        if canonical in self.vocabulary:
            return self.vocabulary[canonical].related
        return []

    def normalize_tag(self, tag: str) -> str:
        """Normalize a single tag to canonical form"""
        # Remove extra whitespace and convert to lowercase
        tag = tag.strip().lower()

        # Handle multi-word tags by splitting
        if " " in tag:
            # Take first word as the tag (e.g., "kafka consumer" -> "kafka")
            tag = tag.split()[0]

        return self.get_canonical(tag)

    def normalize_tags(self, tags: List[str]) -> List[str]:
        """Normalize a list of tags"""
        normalized = set()
        for tag in tags:
            canonical = self.normalize_tag(tag)
            normalized.add(canonical)
        return list(normalized)


class TagNormalizer:
    """
    Handles tag expansion and normalization for retrieval
    """

    def __init__(self, vocabulary: TagVocabulary = None, include_related: bool = False):
        self.vocabulary = vocabulary or TagVocabulary()
        self.include_related = include_related

    def expand_tags(self, tags: List[str]) -> Set[str]:
        """
        Expand tags to include canonical form + synonyms (+ related if enabled)
        This increases recall in retrieval
        """
        expanded = set()

        for tag in tags:
            # Add canonical form
            canonical = self.vocabulary.normalize_tag(tag)
            expanded.add(canonical)

            # Add all synonyms
            synonyms = self.vocabulary.get_synonyms(canonical)
            expanded.update(synonyms)

            # Optionally add related terms
            if self.include_related:
                related = self.vocabulary.get_related(canonical)
                expanded.update(related)

        return expanded

    def calculate_tag_overlap(
        self, query_tags: List[str], item_tags: List[str]
    ) -> Dict[str, any]:
        """
        Calculate overlap between query tags and item tags
        Returns match info including score
        """
        # Expand both sets
        expanded_query = self.expand_tags(query_tags)
        expanded_item = self.expand_tags(item_tags)

        # Calculate overlap
        overlap = expanded_query & expanded_item

        # Calculate Jaccard similarity
        union = expanded_query | expanded_item
        jaccard_score = len(overlap) / len(union) if union else 0.0

        # Calculate overlap ratio (more intuitive)
        overlap_score = len(overlap) / len(expanded_query) if expanded_query else 0.0

        return {
            "matched_tags": list(overlap),
            "jaccard_score": jaccard_score,
            "overlap_score": overlap_score,
            "match_count": len(overlap),
        }

    def clean_tags(self, tags: List[str]) -> List[str]:
        """
        Clean and normalize tags from LLM output
        - Convert to lowercase
        - Remove whitespace
        - Split multi-word tags
        - Remove duplicates
        - Normalize to canonical form
        """
        cleaned = set()

        for tag in tags:
            # Basic cleaning
            tag = tag.strip().lower()

            # Skip empty
            if not tag:
                continue

            # Split multi-word tags
            if " " in tag:
                parts = tag.split()
                for part in parts:
                    if part:
                        cleaned.add(self.vocabulary.normalize_tag(part))
            else:
                cleaned.add(self.vocabulary.normalize_tag(tag))

        return list(cleaned)
