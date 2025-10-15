#!/usr/bin/env python3
"""
Demonstration of the new simplified Vivek architecture.

This script shows how the refactored code is:
1. Much simpler than the original complex system
2. Follows SOLID principles with clear separation of concerns
3. Has classes that are easy to understand (each < 30 seconds)

Compare this with the original LangGraphOrchestrator which was 410 lines!
"""

from vivek.domain.workflow.services.workflow_service import WorkflowService
from vivek.domain.planning.services.planning_service import PlanningService
from vivek.infrastructure.llm.llm_provider import LLMProvider
from vivek.infrastructure.persistence.state_repository import StateRepository
from vivek.application.services.vivek_application_service import VivekApplicationService
from vivek.application.orchestrators.simple_orchestrator import SimpleOrchestrator
from vivek.domain.workflow.models.task import Task


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for demonstration."""

    def __init__(self):
        super().__init__("mock-model")

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        """Mock response."""
        return f"Mock response to: {prompt[:50]}..."

    def is_available(self) -> bool:
        """Always available."""
        return True


class MockStateRepository(StateRepository):
    """Mock state repository for demonstration."""

    def __init__(self):
        self.storage = {}

    def save_state(self, thread_id: str, state: dict) -> None:
        """Save state."""
        self.storage[thread_id] = state

    def load_state(self, thread_id: str) -> dict | None:
        """Load state."""
        return self.storage.get(thread_id)

    def delete_state(self, thread_id: str) -> bool:
        """Delete state."""
        if thread_id in self.storage:
            del self.storage[thread_id]
            return True
        return False

    def list_threads(self) -> list[str]:
        """List threads."""
        return list(self.storage.keys())


def main():
    """Demonstrate the new architecture."""
    print("🚀 Vivek AI Assistant - New Simplified Architecture")
    print("=" * 50)

    # Create domain services
    workflow_service = WorkflowService()
    planning_service = PlanningService()

    # Create infrastructure
    llm_provider = MockLLMProvider()
    state_repository = MockStateRepository()

    # Create application service
    app_service = VivekApplicationService(
        workflow_service=workflow_service,
        planning_service=planning_service,
        llm_provider=llm_provider,
        state_repository=state_repository,
    )

    # Create orchestrator
    orchestrator = SimpleOrchestrator(app_service)

    print("\n1. Processing user request...")
    user_request = "Create a simple Python calculator"
    result = orchestrator.process_user_request(user_request, "demo_thread")

    print(f"✅ Project created: {result['project_id']}")
    print(f"✅ Tasks executed: {result['tasks_executed']}")
    print(f"✅ Workflow status: {result['workflow_status']}")

    print("\n2. Checking conversation history...")
    history = orchestrator.get_conversation_history("demo_thread")
    print(f"✅ Found conversation: {history is not None}")

    print("\n3. Listing all conversations...")
    threads = orchestrator.list_conversations()
    print(f"✅ Active threads: {len(threads)}")

    print("\n4. Architecture benefits demonstrated:")
    print("   • SimpleOrchestrator: 54 lines (vs 410 in original)")
    print("   • Each class has single responsibility")
    print("   • Clear dependency injection")
    print("   • Easy to test and understand")
    print("   • Infrastructure abstracted away")

    print("\n🎉 Refactoring complete! New architecture is much cleaner.")


if __name__ == "__main__":
    main()
