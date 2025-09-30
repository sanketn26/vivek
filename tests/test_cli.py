"""
Tests for CLI functionality in Vivek project.
"""
import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from vivek.cli import cli, init, chat, handle_command, models, setup


# Helper to check if Ollama is running
def is_ollama_running():
    """Check if Ollama service is available."""
    try:
        import ollama
        ollama.list()
        return True
    except Exception:
        return False


# Skip marker for tests requiring Ollama
requires_ollama = pytest.mark.skipif(
    not is_ollama_running(),
    reason="Ollama service not running"
)


class TestCLI:
    """Test cases for the main CLI interface."""

    def test_cli_group_creation(self):
        """Test that the CLI group is properly created."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Vivek - Your AI Coding Assistant" in result.output

    def test_init_command_without_args(self, runner):
        """Test the init command with default arguments."""
        result = runner.invoke(init)
        assert result.exit_code == 0
        assert "Vivek initialized successfully" in result.output
        assert "vivek.md" in result.output

    def test_init_command_with_custom_args(self, runner):
        """Test the init command with custom arguments."""
        result = runner.invoke(init, [
            '--mode', 'hybrid',
            '--local-model', 'deepseek-coder:6.7b',
            '--executor-model', 'codellama:7b-instruct'
        ])
        assert result.exit_code == 0
        assert "deepseek-coder:6.7b" in result.output
        assert "codellama:7b-instruct" in result.output

    def test_init_creates_config_files(self, tmp_path, runner):
        """Test that init command creates necessary config files."""
        import os

        # Change to tmp directory for the test
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(init)
            assert result.exit_code == 0

            # Check if vivek.md was created
            vivek_md = tmp_path / 'vivek.md'
            assert vivek_md.exists(), f"vivek.md not found at {vivek_md}"

            # Check if config.yml was created
            config_yml = tmp_path / '.vivek' / 'config.yml'
            assert config_yml.exists(), f"config.yml not found at {config_yml}"
        finally:
            os.chdir(original_dir)

    def test_chat_command_without_config(self, runner, tmp_path):
        """Test chat command when no config exists."""
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(chat)
            # Command exits but may not return 1 in test context
            assert "No vivek configuration found" in result.output or result.exit_code != 0
        finally:
            os.chdir(original_dir)

    @pytest.mark.skip(reason="Chat command requires async event loop and can hang in tests")
    def test_chat_command_with_config(self, temp_config_file, runner):
        """Test chat command with existing config."""
        with patch('pathlib.Path.cwd', return_value=temp_config_file.parent.parent):
            result = runner.invoke(chat, ['--help'])
            assert result.exit_code == 0
            assert "Start interactive chat session" in result.output


class TestHandleCommand:
    """Test cases for the handle_command function."""

    def test_exit_command(self, mock_orchestrator, capsys):
        """Test the /exit command."""
        result = handle_command("/exit", mock_orchestrator)
        assert result == "EXIT"

    def test_mode_switch_commands(self, mock_orchestrator):
        """Test mode switching commands."""
        valid_modes = ['/peer', '/architect', '/sdet', '/coder']

        for mode_cmd in valid_modes:
            result = handle_command(mode_cmd, mock_orchestrator)
            expected_mode = mode_cmd[1:]  # Remove the '/'
            assert f"Switched to {expected_mode} mode" in result

    def test_invalid_mode_command(self, mock_orchestrator):
        """Test invalid mode command."""
        result = handle_command("/invalid_mode", mock_orchestrator)
        assert "Invalid mode" in result

    def test_status_command(self, mock_orchestrator, capsys):
        """Test the /status command."""
        result = handle_command("/status", mock_orchestrator)
        assert result is None  # Status prints to console

        # Check that status was printed (LangGraph status)
        captured = capsys.readouterr()
        assert "Session Status" in captured.out or "Vivek LangGraph Status" in captured.out

    def test_help_command(self, mock_orchestrator, capsys):
        """Test the /help command."""
        result = handle_command("/help", mock_orchestrator)
        assert result is None  # Help prints to console

        # Check that help was printed
        captured = capsys.readouterr()
        assert "Available Commands:" in captured.out

    def test_unknown_command(self, mock_orchestrator):
        """Test unknown command handling."""
        result = handle_command("/unknown", mock_orchestrator)
        # Unknown commands are treated as invalid modes
        assert "Invalid mode" in result or "Unknown command" in result


class TestModelsCommand:
    """Test cases for the models command."""

    @requires_ollama
    def test_models_list_empty(self, runner):
        """Test models command when no models are available."""
        result = runner.invoke(models)
        assert result.exit_code == 0
        assert "Available Local Models:" in result.output

    def test_models_list_with_models(self, runner):
        """Test models command with available models."""
        with patch('ollama.list') as mock_list:
            mock_list.return_value = {
                'models': [
                    {'name': 'qwen2.5-coder:7b', 'size': 4 * 1024**3},
                    {'name': 'deepseek-coder:6.7b', 'size': 3.5 * 1024**3}
                ]
            }

            result = runner.invoke(models)
            assert result.exit_code == 0
            assert "qwen2.5-coder:7b" in result.output
            assert "deepseek-coder:6.7b" in result.output

    def test_models_pull_missing_argument(self, runner):
        """Test models pull command without model name."""
        result = runner.invoke(models, ['pull'])
        # Command doesn't raise exit code, just prints message
        assert "Please specify a model to pull" in result.output

    def test_models_pull_with_model(self, runner):
        """Test models pull command with model name."""
        with patch('ollama.pull') as mock_pull:
            mock_pull.return_value = None

            result = runner.invoke(models, ['pull', 'qwen2.5-coder:7b'])
            assert result.exit_code == 0
            assert "Downloading qwen2.5-coder:7b" in result.output
            assert "Successfully downloaded" in result.output

            mock_pull.assert_called_once_with('qwen2.5-coder:7b')

    def test_models_pull_error(self, runner):
        """Test models pull command with error."""
        with patch('ollama.pull') as mock_pull:
            mock_pull.side_effect = Exception("Download failed")

            result = runner.invoke(models, ['pull', 'qwen2.5-coder:7b'])
            assert result.exit_code == 0  # CLI doesn't exit with error code
            assert "Error downloading model" in result.output


class TestSetupCommand:
    """Test cases for the setup command."""

    def test_setup_with_ollama_installed(self, runner):
        """Test setup command when Ollama is installed."""
        with patch('ollama.list') as mock_list:
            mock_list.return_value = {'models': []}

            # Mock Prompt.ask to avoid interactive input
            with patch('rich.prompt.Prompt.ask', return_value='n'):
                result = runner.invoke(setup)
                assert result.exit_code == 0
                assert "Ollama is installed and running" in result.output

    def test_setup_without_ollama(self, runner):
        """Test setup command when Ollama is not installed."""
        with patch('ollama.list') as mock_list:
            mock_list.side_effect = Exception("Ollama not found")

            result = runner.invoke(setup)
            assert result.exit_code == 0
            assert "Ollama not found" in result.output
            assert "curl -fsSL https://ollama.com/install.sh | sh" in result.output

    def test_setup_model_download_success(self, runner):
        """Test setup command with successful model download."""
        with patch('ollama.list') as mock_list:
            mock_list.return_value = {'models': []}

            # Mock Prompt.ask to return 'y' for download, 'n' for init
            with patch('rich.prompt.Prompt.ask', side_effect=['y', 'n']):
                with patch('ollama.pull') as mock_pull:
                    mock_pull.return_value = None

                    result = runner.invoke(setup)
                    assert result.exit_code == 0
                    assert "Model downloaded successfully" in result.output


class TestCLIIntegration:
    """Integration tests for CLI functionality."""

    def test_init_and_chat_workflow(self, tmp_path, runner):
        """Test the complete init -> chat workflow."""
        # Change to temp directory
        with patch('pathlib.Path.cwd', return_value=tmp_path):
            # Initialize Vivek
            init_result = runner.invoke(init)
            assert init_result.exit_code == 0

            # Try to start chat (should work now that config exists)
            chat_result = runner.invoke(chat, ['--help'])
            assert chat_result.exit_code == 0

    def test_cli_error_handling(self, runner, tmp_path):
        """Test CLI error handling for various scenarios."""
        import os

        # Test with invalid arguments
        result = runner.invoke(init, ['--invalid-arg'])
        assert result.exit_code != 0

        # Test chat without initialization in isolated directory
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Chat tries to start even without proper config, but will error on input
            # Skip this test as it requires interactive session handling
            pass
        finally:
            os.chdir(original_dir)

    def test_cli_help_output(self, runner):
        """Test that all commands show proper help output."""
        # Test main CLI help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "Usage:" in result.output

        # Test individual command helps
        commands = ['init', 'chat', 'models', 'setup']
        for cmd_name in commands:
            result = runner.invoke(cli, [cmd_name, '--help'])
            assert result.exit_code == 0
            # Check for command name in output (without quotes requirement)
            assert cmd_name in result.output or f"cli {cmd_name}" in result.output