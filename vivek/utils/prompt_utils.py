"""Prompt utilities for token management and optimization."""
import re
from typing import Dict, List, Any, Optional

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class TokenCounter:
    """Token counting utility for LLM prompts.

    Uses tiktoken for accurate counting when available, falls back to
    character-based approximation.
    """

    # Rough approximation: 1 token ≈ 4 characters for most LLMs
    CHARS_PER_TOKEN = 4

    # Common context window sizes for popular models
    CONTEXT_WINDOWS = {
        "qwen2.5-coder:7b": 32768,
        "qwen2.5-coder:14b": 32768,
        "deepseek-coder:6.7b": 32768,
        "deepseek-coder:33b": 32768,
        "codellama:7b": 16384,
        "codellama:13b": 16384,
        "codellama:34b": 16384,
        "llama2:7b": 4096,
        "llama2:13b": 4096,
        "llama2:70b": 4096,
        "mistral:7b": 8192,
        "mixtral:8x7b": 32768,
    }

    # Tiktoken encoding mappings for different models
    TIKTOKEN_ENCODINGS = {
        "gpt": "cl100k_base",  # GPT-3.5/4
        "llama": "cl100k_base",  # Approximation for Llama models
        "qwen": "cl100k_base",   # Approximation for Qwen models
        "deepseek": "cl100k_base",  # Approximation for DeepSeek models
        "codellama": "cl100k_base",  # Approximation for CodeLlama
        "mistral": "cl100k_base",  # Approximation for Mistral
    }

    @classmethod
    def _get_encoding_for_model(cls, model_name: str) -> Optional[str]:
        """Get tiktoken encoding for a model."""
        if not TIKTOKEN_AVAILABLE:
            return None

        model_lower = model_name.lower()
        for model_type, encoding in cls.TIKTOKEN_ENCODINGS.items():
            if model_type in model_lower:
                return encoding
        return "cl100k_base"  # Default fallback

    @classmethod
    def count_tokens(cls, text: str, model_name: Optional[str] = None) -> int:
        """Count tokens in text using tiktoken if available."""
        if not text:
            return 0

        if TIKTOKEN_AVAILABLE and model_name:
            try:
                encoding_name = cls._get_encoding_for_model(model_name)
                if encoding_name:
                    encoding = tiktoken.get_encoding(encoding_name)
                    return len(encoding.encode(text))
            except Exception:
                pass  # Fall back to approximation

        # Fallback to character-based approximation
        return len(text) // cls.CHARS_PER_TOKEN

    @classmethod
    def get_context_window(cls, model_name: str) -> int:
        """Get context window size for a model."""
        # Extract base model name (remove size suffix if present)
        base_name = model_name.split(":")[0] if ":" in model_name else model_name
        return cls.CONTEXT_WINDOWS.get(model_name, 4096)  # Default fallback

    @classmethod
    def is_within_limit(cls, text: str, model_name: str, buffer: int = 1000) -> bool:
        """Check if text fits within model's context window with buffer."""
        context_window = cls.get_context_window(model_name)
        token_count = cls.count_tokens(text, model_name)
        return token_count < (context_window - buffer)


class PromptCompressor:
    """Utilities for compressing and optimizing prompts."""

    @staticmethod
    def truncate_context(context: str, max_tokens: int, strategy: str = "recent") -> str:
        """Truncate context to fit within token limit.

        Args:
            context: The context string to truncate
            max_tokens: Maximum tokens to keep
            strategy: Truncation strategy ("recent", "summary", "selective")
        """
        if TokenCounter.count_tokens(context) <= max_tokens:
            return context

        if strategy == "recent":
            # Keep most recent content (last part)
            chars_to_keep = max_tokens * TokenCounter.CHARS_PER_TOKEN
            return context[-chars_to_keep:] if len(context) > chars_to_keep else context

        elif strategy == "summary":
            # Simple summarization by keeping important sections
            lines = context.split('\n')
            # Keep recent lines and any lines that look like summaries or decisions
            important_lines = []
            for line in reversed(lines):
                if any(keyword in line.lower() for keyword in
                      ['decision:', 'summary:', 'key:', 'important:', 'conclusion:']):
                    important_lines.insert(0, line)
                elif len(important_lines) < max_tokens // 10:  # Keep some recent lines
                    important_lines.insert(0, line)

            return '\n'.join(important_lines)

        else:  # selective
            # Keep code blocks and recent content
            lines = context.split('\n')
            code_blocks = []
            recent_lines = []

            in_code_block = False
            for i, line in enumerate(reversed(lines)):
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    code_blocks.insert(0, line)
                elif in_code_block:
                    code_blocks.insert(0, line)
                elif i < 20:  # Keep last 20 lines
                    recent_lines.insert(0, line)

            return '\n'.join(code_blocks + recent_lines)

    @staticmethod
    def compress_prompt_template(system_prompt: str, task_info: Dict[str, Any]) -> str:
        """Compress verbose prompts into more efficient templates."""
        # Remove redundant instructions
        compressed = re.sub(r'\s+', ' ', system_prompt.strip())

        # Build compact task description
        task_parts = []
        if 'description' in task_info:
            task_parts.append(f"Task: {task_info['description']}")
        if 'mode' in task_info:
            task_parts.append(f"Mode: {task_info['mode']}")
        if 'steps' in task_info and task_info['steps']:
            steps_str = ' | '.join(task_info['steps'][:3])  # Limit to 3 steps
            task_parts.append(f"Steps: {steps_str}")
        if 'relevant_files' in task_info and task_info['relevant_files']:
            files_str = ', '.join(task_info['relevant_files'][:5])  # Limit to 5 files
            task_parts.append(f"Files: {files_str}")

        task_summary = ' | '.join(task_parts)

        return f"{compressed}\n\n{task_summary}"


class PromptValidator:
    """Validate prompts before sending to LLM."""

    @staticmethod
    def validate_and_truncate(
        prompt: str,
        model_name: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """Validate prompt length and truncate if necessary."""
        if max_tokens is None:
            context_window = TokenCounter.get_context_window(model_name)
            max_tokens = context_window - 1000  # Leave buffer

        # Check if prompt exceeds max_tokens (not using is_within_limit which has its own buffer)
        prompt_tokens = TokenCounter.count_tokens(prompt, model_name)
        if prompt_tokens > max_tokens:
            # Truncate context portion while keeping system prompt
            lines = prompt.split('\n')
            system_lines = []
            context_lines = []

            in_context = False
            for line in lines:
                if line.startswith('Context:') or line.startswith('Current Context:'):
                    in_context = True
                if not in_context:
                    system_lines.append(line)
                else:
                    context_lines.append(line)

            system_prompt = '\n'.join(system_lines)
            context = '\n'.join(context_lines)

            # Compress context
            compressed_context = PromptCompressor.truncate_context(
                context, max_tokens - TokenCounter.count_tokens(system_prompt)
            )

            # Validate that system_prompt + compressed_context actually fit within max_tokens
            system_tokens = TokenCounter.count_tokens(system_prompt)
            compressed_tokens = TokenCounter.count_tokens(compressed_context)

            if system_tokens > max_tokens:
                raise ValueError(
                    f"System prompt alone ({system_tokens} tokens) exceeds maximum allowed tokens ({max_tokens}). "
                    "Consider using a smaller system prompt or larger context window."
                )

            allowed_for_context = max_tokens - system_tokens
            if compressed_tokens > allowed_for_context:
                # Re-run truncation with correct limit
                compressed_context = PromptCompressor.truncate_context(
                    context, allowed_for_context
                )
                compressed_tokens = TokenCounter.count_tokens(compressed_context)

            # Final validation that combined prompt fits
            final_combined_tokens = system_tokens + compressed_tokens
            if final_combined_tokens > max_tokens:
                raise ValueError(
                    f"Final combined prompt ({final_combined_tokens} tokens) still exceeds maximum allowed tokens ({max_tokens}). "
                    "Context compression was insufficient."
                )

            return f"{system_prompt}\n{compressed_context}"

        return prompt