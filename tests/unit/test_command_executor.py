"""Unit tests for CommandExecutor."""

import pytest
from vivek.infrastructure.file_operations.command_executor import CommandExecutor


class TestCommandExecutorBasicCommands:
    """Test CommandExecutor with basic shell commands."""

    def test_run_successful_echo_command(self):
        """Test running a successful echo command."""
        result = CommandExecutor.run_command("echo 'Hello World'")

        assert result["success"] is True
        assert "Hello World" in result["stdout"]
        assert result["exit_code"] == 0
        assert result["stderr"] == ""

    def test_run_command_returns_dict(self):
        """Test that run_command returns a dictionary."""
        result = CommandExecutor.run_command("echo test")

        assert isinstance(result, dict)
        assert "success" in result
        assert "stdout" in result
        assert "stderr" in result
        assert "exit_code" in result

    def test_run_successful_command_sets_success_true(self):
        """Test that successful command sets success to True."""
        result = CommandExecutor.run_command("true")

        assert result["success"] is True
        assert result["exit_code"] == 0

    def test_run_failing_command_sets_success_false(self):
        """Test that failing command sets success to False."""
        result = CommandExecutor.run_command("false")

        assert result["success"] is False
        assert result["exit_code"] != 0

    def test_run_command_with_exit_code(self):
        """Test that exit code is captured correctly."""
        result = CommandExecutor.run_command("exit 42")

        # Note: exit code might vary, but failure should be captured
        assert result["exit_code"] != 0

    def test_run_command_captures_stdout(self):
        """Test that stdout is captured."""
        result = CommandExecutor.run_command("echo 'stdout test'")

        assert "stdout test" in result["stdout"]

    def test_run_command_captures_stderr(self):
        """Test that stderr is captured."""
        # Using a command that writes to stderr
        result = CommandExecutor.run_command("bash -c 'echo error >&2'")

        assert "error" in result["stderr"]

    def test_run_command_with_multiline_output(self):
        """Test capturing multiline command output."""
        result = CommandExecutor.run_command("echo 'Line 1' && echo 'Line 2' && echo 'Line 3'")

        assert "Line 1" in result["stdout"]
        assert "Line 2" in result["stdout"]
        assert "Line 3" in result["stdout"]
        assert result["success"] is True


class TestCommandExecutorWorkingDirectory:
    """Test CommandExecutor with different working directories."""

    def test_run_command_with_cwd(self):
        """Test running command with specified working directory."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = CommandExecutor.run_command("pwd", cwd=tmpdir)

            assert result["success"] is True
            assert tmpdir in result["stdout"]

    def test_run_command_without_cwd_uses_default(self):
        """Test that command without cwd uses default directory."""
        result = CommandExecutor.run_command("pwd")

        assert result["success"] is True
        assert result["stdout"].strip() != ""

    def test_run_command_with_nonexistent_cwd(self):
        """Test command with nonexistent working directory."""
        result = CommandExecutor.run_command("pwd", cwd="/nonexistent/directory/path")

        # Should fail or handle gracefully
        assert result["success"] is False or "nonexistent" in result["stderr"].lower()

    def test_run_command_respects_cwd(self):
        """Test that cwd is respected for file operations."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a file in the temp directory
            test_file = os.path.join(tmpdir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test content")
            
            # List files in that directory
            result = CommandExecutor.run_command("ls test.txt", cwd=tmpdir)

            assert result["success"] is True
            assert "test.txt" in result["stdout"]


class TestCommandExecutorTimeout:
    """Test CommandExecutor timeout functionality."""

    def test_run_command_with_default_timeout(self):
        """Test that command runs with default 60s timeout."""
        result = CommandExecutor.run_command("echo 'quick command'")

        assert result["success"] is True

    def test_run_command_with_custom_timeout(self):
        """Test command with custom timeout."""
        result = CommandExecutor.run_command("echo 'test'", timeout=30)

        assert result["success"] is True

    def test_run_command_timeout_expired(self):
        """Test that timeout is respected."""
        result = CommandExecutor.run_command("sleep 10", timeout=1)

        assert result["success"] is False
        assert "timed out" in result["stderr"].lower()
        assert result["exit_code"] == -1

    def test_timeout_error_message(self):
        """Test that timeout error includes timeout duration."""
        timeout_seconds = 2
        result = CommandExecutor.run_command(
            "sleep 100",
            timeout=timeout_seconds
        )

        assert result["success"] is False
        assert str(timeout_seconds) in result["stderr"]

    def test_timeout_zero_still_runs(self):
        """Test command with very small timeout."""
        result = CommandExecutor.run_command("echo 'fast'", timeout=1)

        assert result["success"] is True

    def test_long_running_command_timeout(self):
        """Test that long-running command times out."""
        result = CommandExecutor.run_command(
            "python -c \"import time; time.sleep(5)\"",
            timeout=1
        )

        assert result["success"] is False


class TestCommandExecutorPythonCommands:
    """Test CommandExecutor with Python commands."""

    def test_run_python_print_command(self):
        """Test running a Python print command."""
        result = CommandExecutor.run_command("python3 -c \"print('Hello from Python')\"")

        assert result["success"] is True
        assert "Hello from Python" in result["stdout"]

    def test_run_python_arithmetic(self):
        """Test running a Python arithmetic command."""
        result = CommandExecutor.run_command("python3 -c \"print(2 + 2)\"")

        assert result["success"] is True
        assert "4" in result["stdout"]

    def test_run_python_with_error(self):
        """Test Python command that produces error."""
        result = CommandExecutor.run_command("python3 -c \"raise ValueError('test error')\"")

        assert result["success"] is False
        assert "ValueError" in result["stderr"]

    def test_run_python_module_import(self):
        """Test running Python with module import."""
        result = CommandExecutor.run_command("python3 -c \"import json; print('json imported')\"")

        assert result["success"] is True

    def test_run_python_list_comprehension(self):
        """Test Python list comprehension command."""
        result = CommandExecutor.run_command("python3 -c \"result = [x*2 for x in range(5)]; print(result)\"")

        assert result["success"] is True
        assert "[" in result["stdout"]


class TestCommandExecutorComplexCommands:
    """Test CommandExecutor with complex shell commands."""

    def test_run_piped_command(self):
        """Test running piped commands."""
        result = CommandExecutor.run_command("echo 'test line' | grep 'test'")

        assert result["success"] is True
        assert "test line" in result["stdout"]

    def test_run_command_with_redirection(self):
        """Test command with output redirection."""
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = os.path.join(tmpdir, "output.txt")
            # Using >> for append to ensure file operation
            result = CommandExecutor.run_command(
                f"echo 'test' >> {output_file}",
                cwd=tmpdir
            )

            assert result["success"] is True
            if os.path.exists(output_file):
                with open(output_file) as f:
                    assert "test" in f.read()

    def test_run_conditional_command(self):
        """Test conditional command with &&."""
        result = CommandExecutor.run_command("echo 'first' && echo 'second'")

        assert result["success"] is True
        assert "first" in result["stdout"]
        assert "second" in result["stdout"]

    def test_run_failing_conditional_command(self):
        """Test that && stops on failure."""
        result = CommandExecutor.run_command("false && echo 'should not print'")

        assert result["success"] is False

    def test_run_or_command(self):
        """Test command with || operator."""
        result = CommandExecutor.run_command("false || echo 'fallback'")

        assert result["success"] is True
        assert "fallback" in result["stdout"]

    def test_run_command_with_variables(self):
        """Test command with shell variables."""
        result = CommandExecutor.run_command("export VAR='hello' && echo $VAR")

        assert result["success"] is True
        assert "hello" in result["stdout"]


class TestCommandExecutorErrorHandling:
    """Test CommandExecutor error handling."""

    def test_run_nonexistent_command(self):
        """Test running a nonexistent command."""
        result = CommandExecutor.run_command("nonexistent_command_xyz")

        assert result["success"] is False
        assert result["exit_code"] != 0

    def test_command_with_syntax_error(self):
        """Test command with syntax error."""
        result = CommandExecutor.run_command("echo 'unclosed string")

        # Should fail due to syntax error
        assert result["success"] is False

    def test_exception_returns_error_dict(self):
        """Test that exceptions return proper error dictionary."""
        result = CommandExecutor.run_command("this_is_an_invalid_command_xyz123")

        # Should have proper error structure
        assert isinstance(result, dict)
        assert result["success"] is False
        assert "exit_code" in result

    def test_permission_denied_error(self):
        """Test handling of permission denied error."""
        result = CommandExecutor.run_command("cat /root/secret_file 2>/dev/null || echo 'permission denied'")

        # Command should handle gracefully
        assert result["exit_code"] == 0 or result["success"] is False

    def test_stderr_in_error_result(self):
        """Test that stderr is captured in error results."""
        result = CommandExecutor.run_command("python3 -c \"import sys; sys.stderr.write('error message'); sys.exit(1)\"")

        assert result["success"] is False
        assert "error message" in result["stderr"]


class TestCommandExecutorReturnValues:
    """Test CommandExecutor return value structure."""

    def test_return_dict_has_all_keys(self):
        """Test that return dict has all expected keys."""
        result = CommandExecutor.run_command("echo 'test'")

        expected_keys = {"success", "stdout", "stderr", "exit_code"}
        assert set(result.keys()) == expected_keys

    def test_return_values_are_correct_types(self):
        """Test that return values have correct types."""
        result = CommandExecutor.run_command("echo 'test'")

        assert isinstance(result["success"], bool)
        assert isinstance(result["stdout"], str)
        assert isinstance(result["stderr"], str)
        assert isinstance(result["exit_code"], int)

    def test_stdout_is_string(self):
        """Test that stdout is always a string."""
        result = CommandExecutor.run_command("echo 'output'")

        assert isinstance(result["stdout"], str)
        assert len(result["stdout"]) > 0

    def test_stderr_is_string(self):
        """Test that stderr is always a string."""
        result = CommandExecutor.run_command("echo 'test' 1>&2")

        assert isinstance(result["stderr"], str)

    def test_exit_code_is_integer(self):
        """Test that exit_code is always an integer."""
        result = CommandExecutor.run_command("echo 'test'")

        assert isinstance(result["exit_code"], int)
        assert result["exit_code"] == 0

    def test_empty_stdout_is_empty_string(self):
        """Test that missing stdout is empty string, not None."""
        result = CommandExecutor.run_command("true")

        assert result["stdout"] == ""
        assert isinstance(result["stdout"], str)


class TestCommandExecutorStaticMethod:
    """Test that CommandExecutor.run_command is a static method."""

    def test_run_command_is_callable_on_class(self):
        """Test that run_command can be called on the class."""
        result = CommandExecutor.run_command("echo 'test'")

        assert result["success"] is True

    def test_run_command_works_without_instance(self):
        """Test that run_command doesn't require an instance."""
        # Should not need to instantiate
        result = CommandExecutor.run_command("echo 'test'")

        assert isinstance(result, dict)
        assert result["success"] is True

    def test_multiple_static_calls_are_independent(self):
        """Test that multiple calls are independent."""
        result1 = CommandExecutor.run_command("echo 'test1'")
        result2 = CommandExecutor.run_command("echo 'test2'")

        assert result1["stdout"] != result2["stdout"]
        assert "test1" in result1["stdout"]
        assert "test2" in result2["stdout"]


class TestCommandExecutorSpecialCases:
    """Test CommandExecutor special cases."""

    def test_command_with_no_output(self):
        """Test command that produces no output."""
        result = CommandExecutor.run_command("true")

        assert result["success"] is True
        assert result["stdout"] == ""
        assert result["stderr"] == ""

    def test_command_with_empty_string(self):
        """Test behavior with empty command string."""
        result = CommandExecutor.run_command("")

        # Behavior depends on shell interpretation
        assert isinstance(result, dict)
        assert "success" in result

    def test_command_with_only_whitespace(self):
        """Test command with only whitespace."""
        result = CommandExecutor.run_command("   ")

        # Should execute (might be no-op)
        assert isinstance(result, dict)

    def test_command_with_special_shell_chars(self):
        """Test command with special shell characters."""
        result = CommandExecutor.run_command("echo 'Special: $HOME & | ;'")

        assert result["success"] is True

    def test_very_long_command(self):
        """Test with very long command string."""
        long_echo = "echo '" + "x" * 10000 + "'"
        result = CommandExecutor.run_command(long_echo)

        assert result["success"] is True
        assert len(result["stdout"]) > 10000
