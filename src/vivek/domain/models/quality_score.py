"""Quality score data model."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class QualityScore:
    """Quality evaluation score.

    Attributes:
        overall: Overall score (0.0-1.0)
        completeness: Completeness score (0.0-1.0)
        correctness: Correctness score (0.0-1.0)
        feedback: Detailed feedback for improvement
        passed: Whether quality threshold was met
    """

    overall: float
    completeness: float
    correctness: float
    feedback: List[str] = field(default_factory=list)
    passed: bool = False

    def __post_init__(self):
        """Validate scores."""
        for score_name in ["overall", "completeness", "correctness"]:
            score = getattr(self, score_name)
            if not 0.0 <= score <= 1.0:
                raise ValueError(f"{score_name} must be between 0.0 and 1.0")
