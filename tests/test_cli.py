"""
Tests for CLI functionality - Clean Architecture version.
"""

import pytest
from click.testing import CliRunner
import yaml

from vivek.cli import cli, init, chat, status


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project directory."""
    return tmp_path


class TestCLIBasics:
    """Basic CLI functionality tests."""

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Vivek" in result.output

    def test_init_command(self, runner, temp_project, monkeypatch):
        """Test init command creates config."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(init, ["--model", "test-model", "--provider", "mock"])
        assert result.exit_code == 0
        assert "initialized successfully" in result.output

        # Check config file was created
        config_path = temp_project / ".vivek" / "config.yml"
        assert config_path.exists()

        # Verify config content
        with open(config_path) as f:
            config = yaml.safe_load(f)
            assert config["llm_model"] == "test-model"
            assert config["llm_provider"] == "mock"

    def test_status_without_init(self, runner, temp_project, monkeypatch):
        """Test status command without initialization."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(status)
        assert result.exit_code == 0
        assert "not initialized" in result.output.lower()

    def test_status_after_init(self, runner, temp_project, monkeypatch):
        """Test status command after initialization."""
        monkeypatch.chdir(temp_project)

        # Initialize first
        runner.invoke(init, ["--model", "test-model"])

        # Check status
        result = runner.invoke(status)
        assert result.exit_code == 0
        assert "test-model" in result.output

    def test_chat_without_init(self, runner, temp_project, monkeypatch):
        """Test chat command without initialization."""
        monkeypatch.chdir(temp_project)

        result = runner.invoke(chat)
        assert result.exit_code == 0
        assert "No vivek configuration found" in result.output

    def test_chat_with_test_input(self, runner, temp_project, monkeypatch):
        """Test chat command with test input (non-interactive)."""
        monkeypatch.chdir(temp_project)

        # Initialize with mock provider
        runner.invoke(init, ["--provider", "mock"])

        # Run chat with test input
        result = runner.invoke(chat, ["--test-input", "Create a hello world function"])

        # Should not error (though it might not complete successfully without proper setup)
        # Just verify it doesn't crash
        assert "Error" not in result.output or "Mock response" in result.output


class TestCLIIntegration:
    """Integration tests for CLI workflows."""

    def test_complete_workflow(self, runner, temp_project, monkeypatch):
        """Test complete workflow: init -> status -> chat."""
        monkeypatch.chdir(temp_project)

        # Step 1: Initialize
        result = runner.invoke(init, ["--provider", "mock"])
        assert result.exit_code == 0

        # Step 2: Check status
        result = runner.invoke(status)
        assert result.exit_code == 0
        assert "mock" in result.output

        # Step 3: Run chat with test input
        result = runner.invoke(chat, ["--test-input", "Test task"])
        # Should execute without crashing
        assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
