"""Plan data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from vivek.domain.models.work_item import WorkItem


@dataclass
class Plan:
    """Execution plan containing work items.

    Attributes:
        work_items: List of work items to execute
        created_at: When plan was created
        metadata: Additional plan metadata
    """

    work_items: List[WorkItem]
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

    def get_item_by_id(self, item_id: str) -> WorkItem:
        """Get work item by ID."""
        for item in self.work_items:
            if item.id == item_id:
                return item
        raise ValueError(f"Work item not found: {item_id}")

    def get_items_without_dependencies(self) -> List[WorkItem]:
        """Get work items with no dependencies."""
        return [item for item in self.work_items if not item.dependencies]
