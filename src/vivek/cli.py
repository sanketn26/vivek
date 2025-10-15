# vivek/new_cli.py - Simplified CLI using new architecture
import asyncio
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path
from typing import Optional
import yaml

# Import new simplified architecture components
import sys
from pathlib import Path

# Add the src directory to Python path for direct execution
src_path = Path(__file__).parent.parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from application.orchestrators.simple_orchestrator import SimpleOrchestrator
from application.services.vivek_application_service import VivekApplicationService
from domain.workflow.services.workflow_service import WorkflowService
from domain.planning.services.planning_service import PlanningService
from infrastructure.llm.llm_provider import LLMProvider
from infrastructure.persistence.state_repository import StateRepository

console = Console()


@click.group()
def cli():
    """🤖 Vivek - Your AI Coding Assistant (Simplified Architecture)"""
    pass


@cli.command()
@click.option("--model", default="qwen2.5-coder:7b", help="LLM model name")
def init(model):
    """Initialize Vivek in current project"""

    config = {"model": model, "version": "2.0-simplified"}

    config_path = Path("./.vivek/config.yml")
    config_path.parent.mkdir(exist_ok=True)

    import yaml

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    console.print(
        Panel(
            f"✅ Vivek 2.0 initialized successfully!\n\n"
            f"📁 Config saved to: {config_path}\n"
            f"🧠 Model: {model}\n\n"
            f"Run 'python -m src.vivek.cli chat' to start coding!",
            title="🤖 Vivek Setup Complete",
            style="green",
        )
    )


@cli.command()
@click.option("--model", help="Override model")
@click.option("--test-input", help="Test input for non-interactive mode")
def chat(model, test_input):
    """Start chat session"""

    # Load config
    config_path = Path("./.vivek/config.yml")
    if not config_path.exists():
        console.print(
            "❌ No vivek configuration found. Run 'python -m src.vivek.cli init' first.",
            style="red",
        )
        return

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Use provided model or config default
    selected_model = model or config.get("model", "qwen2.5-coder:7b")

    # Create simplified architecture components
    workflow_service = WorkflowService()
    planning_service = PlanningService()
    llm_provider = MockLLMProvider()  # We'll create this
    state_repository = MockStateRepository()  # We'll create this

    app_service = VivekApplicationService(
        workflow_service=workflow_service,
        planning_service=planning_service,
        llm_provider=llm_provider,
        state_repository=state_repository,
    )

    orchestrator = SimpleOrchestrator(app_service)

    console.print(
        Panel(
            f"🤖 **Vivek 2.0 - Simplified Architecture**\n\n"
            f"🧠 Model: {selected_model}\n"
            f"📁 Project: {Path.cwd().name}\n"
            f"🔧 Architecture: Domain-Driven Design\n\n"
            f"Type your request to begin!",
            title="🚀 Vivek Chat Session",
            style="blue",
        )
    )

    # Test mode or interactive mode
    if test_input:
        result = orchestrator.process_user_request(test_input)
        console.print(
            Panel(
                Markdown(result.get("output", "No output")),
                title="✅ Result",
                style="green",
            )
        )
    else:
        asyncio.run(chat_loop(orchestrator))


async def chat_loop(orchestrator: SimpleOrchestrator):
    """Main interactive chat loop"""
    while True:
        try:
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")

            if not user_input.strip():
                continue

            if user_input.lower() in ["/exit", "/quit"]:
                console.print("👋 Thanks for using Vivek!", style="yellow")
                break

            with console.status("[bold green]🤖 Vivek is thinking...", spinner="dots"):
                result = orchestrator.process_user_request(user_input)

            if result["status"] == "completed":
                console.print(
                    Panel(
                        Markdown(result.get("output", "No output")),
                        title="🤖 Vivek",
                        style="cyan",
                    )
                )
            else:
                console.print(
                    f"❌ Error: {result.get('error', 'Unknown error')}", style="red"
                )

        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!", style="yellow")
            break
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="red")


# Mock classes for demonstration - in real implementation these would be proper implementations
class MockLLMProvider(LLMProvider):
    def __init__(self):
        super().__init__("mock-model")

    def generate(self, prompt: str, temperature: float = 0.7) -> str:
        return f"Mock response to: {prompt[:50]}..."

    def is_available(self) -> bool:
        return True


class MockStateRepository(StateRepository):
    def __init__(self):
        self.storage = {}

    def save_state(self, thread_id: str, state: dict) -> None:
        self.storage[thread_id] = state

    def load_state(self, thread_id: str) -> dict | None:
        return self.storage.get(thread_id)

    def delete_state(self, thread_id: str) -> bool:
        if thread_id in self.storage:
            del self.storage[thread_id]
            return True
        return False

    def list_threads(self) -> list[str]:
        return list(self.storage.keys())


if __name__ == "__main__":
    cli()
