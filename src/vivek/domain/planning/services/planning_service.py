"""Planner service implementation."""

import json
from typing import Optional

from vivek.domain.interfaces.planner import IPlannerService
from vivek.domain.planning.models.plan import Plan
from vivek.domain.models.work_item import WorkItem, ExecutionMode
from vivek.domain.exceptions.exception import PlanningException
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.prompts.multi_phase_planner_prompts import (
    build_clarification_prompt,
    build_confirmation_prompt,
    build_decomposition_prompt,
)


class PlannerService(IPlannerService):
    """Service for planning and decomposition."""

    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def create_plan(self, user_request: str, project_context: str) -> Plan:
        """Create execution plan from user request.

        Args:
            user_request: What user wants to implement
            project_context: Project information

        Returns:
            Plan with 3-5 work items

        Raises:
            PlanningException: If planning fails
        """
        try:
            # Build prompt
            clarification_prompt = build_clarification_prompt(user_request, project_context)

            # Call LLM
            response = self.llm.generate(
                system_prompt=clarification_prompt["system"], prompt=clarification_prompt["user"]
            )

            # Parse response
            plan_data = json.loads(response)

            # Convert to WorkItem objects
            work_items = []
            for item_data in plan_data["work_items"]:
                work_item = WorkItem(
                    id=item_data["id"],
                    file_path=item_data["file_path"],
                    description=item_data["description"],
                    mode=ExecutionMode(item_data["mode"]),
                    language=item_data.get("language", "python"),
                    file_status=item_data.get("file_status", "new"),
                    dependencies=item_data.get("dependencies", []),
                )
                work_items.append(work_item)

            # Validate plan
            self._validate_plan(work_items)

            return Plan(work_items=work_items)

        except json.JSONDecodeError as e:
            raise PlanningException(f"Failed to parse LLM response: {e}")
        except Exception as e:
            raise PlanningException(f"Planning failed: {e}")

    def _validate_plan(self, work_items: list) -> None:
        """Validate plan."""
        if not work_items:
            raise PlanningException("Plan must have at least one work item")

        if len(work_items) > 5:
            raise PlanningException("Plan cannot have more than 5 work items")

        # Check for circular dependencies
        self._check_circular_dependencies(work_items)

    def _check_circular_dependencies(self, work_items: list) -> None:
        """Check for circular dependencies."""
        # Simple implementation: check each item doesn't depend on itself
        item_ids = {item.id for item in work_items}

        for item in work_items:
            if item.id in item.dependencies:
                raise PlanningException(f"Circular dependency detected: {item.id}")

            # Check dependencies exist
            for dep_id in item.dependencies:
                if dep_id not in item_ids:
                    raise PlanningException(f"Unknown dependency: {dep_id} in {item.id}")
