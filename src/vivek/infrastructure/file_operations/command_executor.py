"""Command execution service."""

import subprocess
from typing import Any, Dict, Optional


class CommandExecutor:
    """Execute shell commands."""

    @staticmethod
    def run_command(
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 60
    ) -> Dict[str, Any]:
        """Execute shell command.

        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Timeout in seconds

        Returns:
            Dict with stdout, stderr, exit_code, success
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "exit_code": -1
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1
            }