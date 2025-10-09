"""
Logging utilities for testing and debugging the orchestrator.

Provides wrappers to capture all LLM interactions for analysis.
"""

import time
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional


class OrchestrationLogger:
    """Logs orchestration flow with detailed prompts and responses."""

    def __init__(self, log_file: str):
        self.log_file = log_file
        self.start_time = datetime.now()

        # Create log directory if needed
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    def log(self, section: str, content: str):
        """Log a section with timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed = (datetime.now() - self.start_time).total_seconds()

        with open(self.log_file, "a") as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"[{timestamp}] [{elapsed:.2f}s] {section}\n")
            f.write(f"{'='*80}\n")
            f.write(f"{content}\n")

    def log_separator(self):
        """Log a visual separator."""
        with open(self.log_file, "a") as f:
            f.write(f"\n{'#'*80}\n")
            f.write(f"{'#'*80}\n\n")


class LoggingProviderWrapper:
    """Wraps a provider to log all prompts and responses."""

    def __init__(self, provider, logger: OrchestrationLogger, name: str):
        self.provider = provider
        self.logger = logger
        self.name = name
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate with logging."""
        self.call_count += 1
        call_num = self.call_count

        # Log the prompt
        self.logger.log(
            f"{self.name} CALL #{call_num} - PROMPT",
            f"Length: {len(prompt)} characters\n"
            f"Temperature: {kwargs.get('temperature', 0.1)}\n"
            f"{'─'*80}\n"
            f"{prompt}"
        )

        # Call the actual provider
        start_time = time.time()
        response = self.provider.generate(prompt, **kwargs)
        elapsed = time.time() - start_time

        # Log the response
        self.logger.log(
            f"{self.name} CALL #{call_num} - RESPONSE",
            f"Length: {len(response)} characters\n"
            f"Time: {elapsed:.2f}s\n"
            f"{'─'*80}\n"
            f"{response}"
        )

        return response

    def __getattr__(self, name):
        """Forward all other attributes to wrapped provider."""
        return getattr(self.provider, name)
