"""Simple token counter utility for prompt optimization."""

import logging

logger = logging.getLogger(__name__)


def count_tokens_simple(text: str) -> int:
    """Count tokens using a simple word-based approximation.

    This is a lightweight approximation that's good enough for
    monitoring and optimization purposes. For production use with
    actual token limits, consider using tiktoken.

    Args:
        text: The text to count tokens for

    Returns:
        Approximate token count (words * 1.3)
    """
    if not text:
        return 0
    words = len(text.split())
    # English text averages ~1.3 tokens per word
    return int(words * 1.3)


def log_token_count(prompt: str, context: str = "prompt", threshold: int = 800) -> int:
    """Log token count and warn if exceeding threshold.

    Args:
        prompt: The prompt text to count
        context: Description of what's being counted (for logging)
        threshold: Token count threshold for warnings (default 800)

    Returns:
        Token count
    """
    token_count = count_tokens_simple(prompt)

    logger.info(f"{context} token count: {token_count} tokens")

    if token_count > threshold:
        logger.warning(
            f"{context} exceeds recommended token limit: {token_count} > {threshold} tokens. "
            f"Consider simplifying the prompt for better model performance."
        )

    return token_count
