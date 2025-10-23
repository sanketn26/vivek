"""Quality service interface."""

from abc import abstractmethod
from typing import List, Protocol

from vivek.domain.models.execution_result import ExecutionResult
from vivek.domain.models.quality_score import QualityScore


class IQualityService(Protocol):
    """Interface for quality evaluation service."""

    @abstractmethod
    async def evaluate(self, results: List[ExecutionResult]) -> QualityScore:
        """Evaluate quality of execution results.

        Args:
            results: List of execution results to evaluate

        Returns:
            Quality score
        """
        ...
