"""Exception hierarchy for Vivek."""

from typing import Optional


class VivekException(Exception):
    """Base exception for all Vivek errors."""

    pass


class PlanningException(VivekException):
    """Planning failed."""

    pass


class ExecutionException(VivekException):
    """Execution failed."""

    pass


class QualityException(VivekException):
    """Quality check failed."""

    pass


class ValidationException(VivekException):
    """Validation failed."""

    pass


class LLMException(VivekException):
    """LLM provider error."""

    def __init__(self, message: str, provider: str, retry_after: Optional[int] = None):
        self.provider = provider
        self.retry_after = retry_after
        super().__init__(message)


class ConfigurationException(VivekException):
    """Configuration error."""

    pass
