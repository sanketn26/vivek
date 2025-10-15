"""
Tests for CLI functionality in Vivek project (New Simplified Architecture).
"""

import pytest
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

# Add src to path for testing
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from vivek.cli import cli, init, chat


# Helper to check if Ollama is running (for tests that might need it)
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
    not is_ollama_running(), reason="Ollama service not running"
)


class TestCLI:
    """Test cases for the main CLI interface."""

    def test_cli_group_creation(self):
        """Test that the CLI group is properly created."""
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Vivek - Your AI Coding Assistant" in result.output or "Vivek 2.0" in result.output

    def test_init_command_without_args(self, runner):
        """Test the init command with default arguments."""
        result = runner.invoke(init)
        assert result.exit_code == 0
        assert "Vivek 2.0 initialized successfully" in result.output
        assert ".vivek/config.yml" in result.output

    def test_init_command_with_custom_args(self, runner):
        """Test the init command with custom arguments."""
        result = runner.invoke(
            init,
            [
                "--model",
                "deepseek-coder:6.7b",
            ],
        )
        assert result.exit_code == 0
        assert "deepseek-coder:6.7b" in result.output

    def test_init_creates_config_files(self, tmp_path, runner):
        """Test that init command creates necessary config files."""
        import os

        # Change to tmp directory for the test
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(init)
            assert result.exit_code == 0

            # Check if .vivek/config.yml was created (new CLI uses simplified config)
            config_yml = tmp_path / ".vivek" / "config.yml"
            assert config_yml.exists(), f"config.yml not found at {config_yml}"

            # Check if config.yml was created (new CLI uses simplified config)
            config_yml = tmp_path / ".vivek" / "config.yml"
            assert config_yml.exists(), f"config.yml not found at {config_yml}"

            # Check that config contains expected model
            import yaml
            with open(config_yml, "r") as f:
                config = yaml.safe_load(f)
                assert "model" in config
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
            assert (
                "No vivek configuration found" in result.output or result.exit_code != 0
            )
        finally:
            os.chdir(original_dir)

    @pytest.mark.skip(
        reason="Chat command requires async event loop and can hang in tests"
    )
    def test_chat_command_with_config(self, temp_config_file, runner):
        """Test chat command with existing config."""
        with patch("pathlib.Path.cwd", return_value=temp_config_file.parent.parent):
            result = runner.invoke(chat, ["--help"])
            assert result.exit_code == 0
            assert "Start chat session" in result.output


class TestChatCommand:
    """Test cases for the chat command in simplified architecture."""

    def test_chat_command_without_config(self, runner, tmp_path):
        """Test chat command when no config exists."""
        import os

        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(chat)
            # Command may exit with error or show message
            assert (
                "No vivek configuration found" in result.output or result.exit_code != 0
            )
        finally:
            os.chdir(original_dir)

    def test_chat_command_with_test_input(self, temp_config_file, runner):
        """Test chat command with test input in simplified architecture."""
        with patch("pathlib.Path.cwd", return_value=temp_config_file.parent.parent):
            # Test with test input (should work with mocked dependencies)
            result = runner.invoke(chat, ["--test-input", "Hello, Vivek!"])
            assert result.exit_code == 0
            # Should show processing or result output
            assert len(result.output) > 50 or "processing" in result.output.lower()


class TestCLIIntegration:
    """Integration tests for simplified CLI functionality."""

    def test_init_and_chat_workflow(self, tmp_path, runner):
        """Test the complete init -> chat workflow."""
        # Change to temp directory
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            # Initialize Vivek
            init_result = runner.invoke(init)
            assert init_result.exit_code == 0

            # Try to start chat (should work now that config exists)
            chat_result = runner.invoke(chat, ["--help"])
            assert chat_result.exit_code == 0

    def test_cli_error_handling(self, runner, tmp_path):
        """Test CLI error handling for various scenarios."""
        import os

        # Test with invalid arguments
        result = runner.invoke(init, ["--invalid-arg"])
        assert result.exit_code != 0

        # Test chat without initialization in isolated directory
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Chat should detect missing config and show error
            chat_result = runner.invoke(chat)
            assert (
                "No vivek configuration found" in chat_result.output or
                chat_result.exit_code != 0
            )
        finally:
            os.chdir(original_dir)

    def test_cli_help_output(self, runner):
        """Test that all commands show proper help output."""
        # Test main CLI help
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output

        # Test individual command helps (only init and chat exist in new CLI)
        commands = ["init", "chat"]
        for cmd_name in commands:
            result = runner.invoke(cli, [cmd_name, "--help"])
            assert result.exit_code == 0
            # Check for command name in output
            assert cmd_name in result.output
