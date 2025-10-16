"""
Dependency Injection Container - centralized component wiring.

Simple, explicit DI container following SOLID principles.
All dependencies are configured in one place for easy testing and modification.
"""

from typing import Dict, Any, Optional
from vivek.domain.workflow.services.workflow_service import WorkflowService
from vivek.domain.planning.services.planning_service import PlanningService
from vivek.domain.workflow.repositories.workflow_repository import (
    WorkflowRepository,
    InMemoryWorkflowRepository,
)
from vivek.domain.planning.repositories.plan_repository import (
    PlanRepository,
    InMemoryPlanRepository,
)
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.infrastructure.llm.ollama_provider import OllamaProvider
from vivek.infrastructure.llm.mock_provider import MockLLMProvider
from vivek.infrastructure.persistence.state_repository import StateRepository
from vivek.infrastructure.persistence.memory_repository import MemoryStateRepository
from vivek.infrastructure.persistence.file_repository import FileStateRepository


class ServiceContainer:
    """
    Simple dependency injection container.

    Manages the creation and wiring of all application services.
    Makes testing easy by allowing mock injection.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize container with configuration.

        Args:
            config: Optional configuration dict with keys:
                - llm_provider: 'ollama' or 'mock'
                - llm_model: Model name
                - state_storage: 'memory' or 'file'
                - state_dir: Directory for file storage
        """
        self.config = config or {}
        self._instances: Dict[str, Any] = {}

    def get_llm_provider(self) -> LLMProvider:
        """
        Get or create LLM provider instance.

        Returns:
            Configured LLM provider
        """
        if "llm_provider" not in self._instances:
            provider_type = self.config.get("llm_provider", "ollama")
            model_name = self.config.get("llm_model", "qwen2.5-coder:7b")

            if provider_type == "ollama":
                base_url = self.config.get("ollama_base_url", "http://localhost:11434")
                self._instances["llm_provider"] = OllamaProvider(
                    model_name=model_name, base_url=base_url
                )
            elif provider_type == "mock":
                self._instances["llm_provider"] = MockLLMProvider(model_name=model_name)
            else:
                raise ValueError(f"Unknown LLM provider type: {provider_type}")

        return self._instances["llm_provider"]

    def get_state_repository(self) -> StateRepository:
        """
        Get or create state repository instance.

        Returns:
            Configured state repository
        """
        if "state_repository" not in self._instances:
            storage_type = self.config.get("state_storage", "file")

            if storage_type == "memory":
                self._instances["state_repository"] = MemoryStateRepository()
            elif storage_type == "file":
                storage_dir = self.config.get("state_dir", ".vivek/state")
                self._instances["state_repository"] = FileStateRepository(storage_dir)
            else:
                raise ValueError(f"Unknown state storage type: {storage_type}")

        return self._instances["state_repository"]

    def get_workflow_repository(self) -> WorkflowRepository:
        """
        Get or create workflow repository instance.

        Returns:
            Workflow repository
        """
        if "workflow_repository" not in self._instances:
            # For now, always use in-memory
            # Can be extended to support file/database storage
            self._instances["workflow_repository"] = InMemoryWorkflowRepository()

        return self._instances["workflow_repository"]

    def get_plan_repository(self) -> PlanRepository:
        """
        Get or create plan repository instance.

        Returns:
            Plan repository
        """
        if "plan_repository" not in self._instances:
            # For now, always use in-memory
            # Can be extended to support file/database storage
            self._instances["plan_repository"] = InMemoryPlanRepository()

        return self._instances["plan_repository"]

    def get_workflow_service(self) -> WorkflowService:
        """
        Get or create workflow service instance.

        Returns:
            Configured workflow service
        """
        if "workflow_service" not in self._instances:
            repository = self.get_workflow_repository()
            self._instances["workflow_service"] = WorkflowService(repository)

        return self._instances["workflow_service"]

    def get_planning_service(self) -> PlanningService:
        """
        Get or create planning service instance.

        Returns:
            Configured planning service
        """
        if "planning_service" not in self._instances:
            repository = self.get_plan_repository()
            self._instances["planning_service"] = PlanningService(repository)

        return self._instances["planning_service"]

    def clear(self) -> None:
        """Clear all cached instances (useful for testing)."""
        self._instances.clear()

    def set_instance(self, key: str, instance: Any) -> None:
        """
        Override an instance (useful for testing with mocks).

        Args:
            key: Instance key (e.g., 'llm_provider')
            instance: Instance to use
        """
        self._instances[key] = instance
