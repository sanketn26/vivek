"""
Vivek CLI - Clean, simple command-line interface.

No path hacks. Uses proper package imports and DI container.
"""

import asyncio
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path
from typing import Optional
import yaml

from vivek.infrastructure.di_container import ServiceContainer
from vivek.application.orchestrators.simple_orchestrator import SimpleOrchestrator
from vivek.application.services.vivek_application_service import VivekApplicationService

console = Console()


@click.group()
def cli():
    """Vivek - Your AI Coding Assistant (Clean Architecture)"""
    pass


@cli.command()
@click.option("--model", default="qwen2.5-coder:7b", help="LLM model name")
@click.option("--provider", default="ollama", help="LLM provider (ollama/mock)")
def init(model: str, provider: str):
    """Initialize Vivek in current project"""

    config = {
        "llm_model": model,
        "llm_provider": provider,
        "state_storage": "file",
        "state_dir": ".vivek/state",
        "version": "3.0-clean",
    }

    config_path = Path("./.vivek/config.yml")
    config_path.parent.mkdir(exist_ok=True, parents=True)

    with open(config_path, "w") as f:
        yaml.dump(config, f, default_flow_style=False)

    console.print(
        Panel(
            f"✅ Vivek initialized successfully!\n\n"
            f"📁 Config saved to: {config_path}\n"
            f"🧠 Model: {model}\n"
            f"🔌 Provider: {provider}\n\n"
            f"Run 'vivek chat' to start coding!",
            title="🤖 Vivek Setup Complete",
            style="green",
        )
    )


@cli.command()
@click.option("--model", help="Override model from config")
@click.option("--test-input", help="Test input for non-interactive mode")
def chat(model: Optional[str], test_input: Optional[str]):
    """Start chat session"""

    # Load config
    config_path = Path("./.vivek/config.yml")
    if not config_path.exists():
        console.print(
            "❌ No vivek configuration found. Run 'vivek init' first.", style="red"
        )
        return

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Override model if provided
    if model:
        config["llm_model"] = model

    # Create service container with config
    container = ServiceContainer(config)

    # Build application service
    app_service = VivekApplicationService(
        workflow_service=container.get_workflow_service(),
        planning_service=container.get_planning_service(),
        llm_provider=container.get_llm_provider(),
        state_repository=container.get_state_repository(),
    )

    # Create orchestrator
    orchestrator = SimpleOrchestrator(app_service)

    console.print(
        Panel(
            f"🤖 **Vivek - Clean Architecture**\n\n"
            f"🧠 Model: {config.get('llm_model', 'unknown')}\n"
            f"🔌 Provider: {config.get('llm_provider', 'unknown')}\n"
            f"📁 Project: {Path.cwd().name}\n\n"
            f"Type your request to begin!",
            title="🚀 Vivek Chat Session",
            style="blue",
        )
    )

    # Test mode or interactive mode
    if test_input:
        try:
            result = orchestrator.process_user_request(test_input)
            console.print(
                Panel(
                    f"Status: {result['status']}\n"
                    f"Tasks executed: {result['tasks_executed']}\n"
                    f"Workflow: {result['workflow_id']}",
                    title="✅ Result",
                    style="green",
                )
            )
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="red")
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

            with console.status(
                "[bold green]🤖 Vivek is thinking...", spinner="dots"
            ):
                result = orchestrator.process_user_request(user_input)

            if result["status"] == "completed":
                # Format results
                output_lines = [
                    f"**Workflow**: {result['workflow_id']}",
                    f"**Tasks Executed**: {result['tasks_executed']}",
                    "",
                    "**Results**:",
                ]

                for i, task_result in enumerate(result["results"], 1):
                    status_emoji = "✅" if task_result["status"] == "completed" else "❌"
                    output_lines.append(
                        f"{i}. {status_emoji} {task_result.get('task_id', 'unknown')}: {task_result.get('status', 'unknown')}"
                    )
                    if "result" in task_result:
                        output_lines.append(f"   {task_result['result'][:100]}...")

                console.print(
                    Panel(
                        "\n".join(output_lines), title="🤖 Vivek", style="cyan"
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


@cli.command()
def status():
    """Show Vivek status and configuration"""
    config_path = Path("./.vivek/config.yml")

    if not config_path.exists():
        console.print("❌ Vivek not initialized in this project", style="red")
        return

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    console.print(
        Panel(
            f"**Model**: {config.get('llm_model', 'unknown')}\n"
            f"**Provider**: {config.get('llm_provider', 'unknown')}\n"
            f"**Version**: {config.get('version', 'unknown')}\n"
            f"**State Storage**: {config.get('state_storage', 'unknown')}\n"
            f"**Config**: {config_path}",
            title="📊 Vivek Status",
            style="blue",
        )
    )


if __name__ == "__main__":
    cli()
