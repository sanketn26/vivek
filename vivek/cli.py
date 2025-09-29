# vivek/cli.py
import asyncio
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
from pathlib import Path
from typing import Optional
import yaml
import os

from .core.orchestrator import VivekOrchestrator

console = Console()

@click.group()
def cli():
    """🤖 Vivek - Your AI Coding Assistant with Dual-Brain Architecture"""
    pass

@cli.command()
@click.option('--mode', default='hybrid', help='Default mode: local, cloud, or hybrid')
@click.option('--local-model', default='qwen2.5-coder:7b', help='Local model name')
@click.option('--executor-model', default='qwen2.5-coder:7b', help='Executor model (can be different)')
def init(mode, local_model, executor_model):
    """Initialize Vivek in current project"""
    config = {
        'project_settings': {
            'language': ['Python', 'TypeScript', 'React', 'Go'],
            'framework': ['FastAPI', 'Next.js'],
            'test_framework': ['pytest', 'jest'],
            'package_manager': ['pip', 'npm']
        },
        'llm_configuration': {
            'mode': mode,
            'planner_model': local_model,
            'executor_model': executor_model,
            'fallback_enabled': True,
            'auto_switch': True
        },
        'preferences': {
            'default_mode': 'peer',
            'search_enabled': True,
            'auto_index': True,
            'privacy_mode': False
        },
        'ignored_paths': [
            'node_modules/',
            '.git/',
            '__pycache__/',
            '.env',
            '*.pyc',
            'dist/',
            'build/'
        ],
        'custom_instructions': [
            'Focus on clean, maintainable code with good test coverage.',
            'Prefer explicit imports and clear variable names.',
            'Always include error handling for external API calls.'
        ]
    }

    config_path = Path('./vivek.md')

    # Generate vivek.md file
    config_content = f"""# Vivek Configuration

## Project Settings
- **Languages**: {', '.join(config['project_settings']['language'])}
- **Frameworks**: {', '.join(config['project_settings']['framework'])}
- **Test Frameworks**: {', '.join(config['project_settings']['test_framework'])}
- **Package Managers**: {', '.join(config['project_settings']['package_manager'])}

## LLM Configuration
- **Mode**: {config['llm_configuration']['mode']}
- **Planner Model**: {config['llm_configuration']['planner_model']}
- **Executor Model**: {config['llm_configuration']['executor_model']}
- **Fallback Enabled**: {config['llm_configuration']['fallback_enabled']}
- **Auto Switch**: {config['llm_configuration']['auto_switch']}

## Preferences
- **Default Mode**: {config['preferences']['default_mode']}
- **Search Enabled**: {config['preferences']['search_enabled']}
- **Auto Index**: {config['preferences']['auto_index']}
- **Privacy Mode**: {config['preferences']['privacy_mode']}

## Ignored Paths
{chr(10).join(f'- {path}' for path in config['ignored_paths'])}

## Custom Instructions
{chr(10).join(f'- {instruction}' for instruction in config['custom_instructions'])}
"""

    with open(config_path, 'w') as f:
        f.write(config_content)

    # Also save as YAML for easy parsing
    yaml_path = Path('./.vivek/config.yml')
    yaml_path.parent.mkdir(exist_ok=True)

    with open(yaml_path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)

    console.print(Panel(
        f"✅ Vivek initialized successfully!\n\n"
        f"📁 Config saved to: {config_path}\n"
        f"🎯 Mode: {mode}\n"
        f"🧠 Planner: {local_model}\n"
        f"⚙️ Executor: {executor_model}\n\n"
        f"Run 'vivek chat' to start coding!",
        title="🤖 Vivek Setup Complete",
        style="green"
    ))

@cli.command()
@click.option('--planner-model', help='Override planner model')
@click.option('--executor-model', help='Override executor model')
def chat(planner_model, executor_model):
    """Start interactive chat session"""

    # Load config
    config_path = Path('./.vivek/config.yml')
    if not config_path.exists():
        console.print("❌ No vivek configuration found. Run 'vivek init' first.", style="red")
        return

    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Override models if provided
    planner = planner_model or config['llm_configuration']['planner_model']
    executor = executor_model or config['llm_configuration']['executor_model']

    console.print(Panel(
        f"🤖 **Vivek Dual-Brain AI Assistant**\n\n"
        f"🧠 Planner: {planner}\n"
        f"⚙️ Executor: {executor}\n"
        f"📁 Project: {Path.cwd().name}\n\n"
        f"**Available Commands:**\n"
        f"• `/peer` - Collaborative programming mode\n"
        f"• `/architect` - System design and architecture\n"
        f"• `/sdet` - Testing and quality assurance\n"
        f"• `/coder` - Direct implementation mode\n"
        f"• `/status` - Show current session status\n"
        f"• `/exit` - Exit Vivek\n\n"
        f"Type your request to begin!",
        title="🚀 Vivek Chat Session",
        style="blue"
    ))

    # Initialize orchestrator
    vivek = VivekOrchestrator(
        project_root=str(Path.cwd()),
        planner_model=planner,
        executor_model=executor
    )

    asyncio.run(chat_loop(vivek))

async def chat_loop(vivek: VivekOrchestrator):
    """Main interactive chat loop"""

    while True:
        try:
            # Get user input with rich prompt
            user_input = Prompt.ask("\n[bold blue]You[/bold blue]")

            if not user_input.strip():
                continue

            # Handle commands
            if user_input.startswith('/'):
                result = handle_command(user_input, vivek)
                if result == "EXIT":
                    break
                elif result:
                    console.print(f"✅ {result}", style="green")
                continue

            # Show thinking indicator
            with console.status("[bold green]🤖 Vivek is thinking...", spinner="dots"):
                response = await vivek.process_request(user_input)

            # Display response with nice formatting
            console.print(Panel(
                Markdown(response),
                title="🤖 Vivek",
                style="cyan"
            ))

        except KeyboardInterrupt:
            console.print("\n👋 Goodbye!", style="yellow")
            break
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="red")

def handle_command(command: str, vivek: VivekOrchestrator) -> Optional[str]:
    """Handle special commands"""
    cmd = command.lower().strip()

    if cmd == '/exit':
        console.print("👋 Thanks for using Vivek!", style="yellow")
        return "EXIT"

    elif cmd in ['/peer', '/architect', '/sdet', '/coder']:
        mode = cmd[1:]  # Remove the '/'
        return vivek.switch_mode(mode)

    elif cmd == '/status':
        status = vivek.get_status()
        console.print(Panel(status, title="📊 Session Status", style="yellow"))
        return None

    elif cmd == '/help':
        help_text = """
**Available Commands:**
• `/peer` - Switch to collaborative programming mode
• `/architect` - Switch to system design mode
• `/sdet` - Switch to testing and QA mode
• `/coder` - Switch to direct implementation mode
• `/status` - Show current session information
• `/help` - Show this help message
• `/exit` - Exit the chat session

**Tips:**
• Vivek uses two AI models working together for better results
• Context is automatically condensed to maintain focus
• Each mode has specialized prompts for different types of work
        """
        console.print(Panel(Markdown(help_text), title="🆘 Vivek Help", style="yellow"))
        return None

    elif cmd.startswith('/'):
        # Check if it's a mode command (valid or invalid)
        potential_mode = cmd[1:]  # Remove the '/'
        valid_modes = ['peer', 'architect', 'sdet', 'coder']
        if potential_mode in valid_modes:
            # Valid mode - this shouldn't happen since we check above, but just in case
            return vivek.switch_mode(potential_mode)
        else:
            # Invalid mode command
            return f"Invalid mode: {potential_mode}"
    else:
        return f"Unknown command: {command}. Type '/help' for available commands."

@cli.command()
@click.argument('models', nargs=-1)
def models(models):
    """Manage local models"""
    import ollama

    if not models:
        # List available models
        try:
            model_list = ollama.list()
            console.print("📋 Available Local Models:", style="bold")
            for model in model_list.get('models', []):
                name = model.get('name', 'Unknown')
                size = model.get('size', 0)
                size_gb = size / (1024**3) if size else 0
                console.print(f"  • {name} ({size_gb:.1f}GB)")
        except Exception as e:
            console.print(f"❌ Error listing models: {e}", style="red")

    elif models[0] == 'pull':
        if len(models) < 2:
            console.print("❌ Please specify a model to pull", style="red")
            return

        model_name = models[1]
        console.print(f"📥 Downloading {model_name}...", style="blue")

        try:
            # This will show download progress
            ollama.pull(model_name)
            console.print(f"✅ Successfully downloaded {model_name}", style="green")
        except Exception as e:
            console.print(f"❌ Error downloading model: {e}", style="red")

@cli.command()
def setup():
    """Quick setup for first-time users"""

    console.print(Panel(
        "🚀 **Welcome to Vivek Setup!**\n\n"
        "This will help you get started with your AI coding assistant.",
        title="Vivek Setup",
        style="blue"
    ))

    # Check if Ollama is installed
    try:
        import ollama
        ollama.list()
        console.print("✅ Ollama is installed and running", style="green")
    except Exception:
        console.print("❌ Ollama not found. Please install it first:", style="red")
        console.print("   curl -fsSL https://ollama.com/install.sh | sh")
        return

    # Recommend models to download
    recommended_models = [
        ("qwen2.5-coder:7b", "Best for general coding tasks"),
        ("deepseek-coder:6.7b", "Excellent for code generation"),
        ("codellama:7b-instruct", "Good fallback option")
    ]

    console.print("\n📚 Recommended models for Vivek:", style="bold")
    for model, description in recommended_models:
        console.print(f"  • {model} - {description}")

    # Ask user which model to download
    if Prompt.ask("\nDownload qwen2.5-coder:7b now?", choices=["y", "n"], default="y") == "y":
        console.print("📥 Downloading qwen2.5-coder:7b...", style="blue")
        try:
            import ollama
            ollama.pull("qwen2.5-coder:7b")
            console.print("✅ Model downloaded successfully!", style="green")

            # Auto-initialize project
            if Prompt.ask("\nInitialize Vivek in current directory?", choices=["y", "n"], default="y") == "y":
                from click.testing import CliRunner
                runner = CliRunner()
                runner.invoke(init)

        except Exception as e:
            console.print(f"❌ Error downloading model: {e}", style="red")

if __name__ == "__main__":
    cli()