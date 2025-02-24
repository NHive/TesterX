import shlex
import subprocess
from typing import List
from .base import Tool


class SystemCommandTool(Tool):
    """系统命令执行工具"""

    def __init__(self, allowed_commands: List[str] = None):
        self.allowed_commands = allowed_commands or []

        super().__init__(
            name="execute_system_command",
            description="执行系统命令并返回结果",
            param_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的系统命令"
                    }
                },
                "required": ["command"]
            }
        )

    def execute(self, arguments: dict) -> dict:
        command = arguments.get("command", "")
        try:
            command_parts = shlex.split(command)
            if not command_parts:
                return {"error": "空命令"}

            if self.allowed_commands and command_parts[0] not in self.allowed_commands:
                return {"error": f"不允许执行命令: {command_parts[0]}"}

            result = subprocess.run(
                command_parts,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "status": "success" if result.returncode == 0 else "error",
                "code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"error": str(e)}
