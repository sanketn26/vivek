"""
Task domain model - represents a single unit of work.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Task:
    """A simple task that needs to be completed."""

    id: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    def mark_completed(self):
        """Mark task as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()

    def mark_failed(self):
        """Mark task as failed."""
        self.status = "failed"
        self.completed_at = datetime.now()
