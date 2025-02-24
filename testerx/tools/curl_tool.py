import subprocess
import shlex
from .base import Tool


class CurlTool(Tool):
    """curl命令行工具"""

    def __init__(self):
        super().__init__(
            name="execute_curl",
            description="执行curl命令获取HTTP请求结果",
            param_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的curl命令，例如 'curl -X GET https://example.com'"
                    }
                },
                "required": ["command"]
            }
        )

    def execute(self, arguments: dict) -> dict:
        command = arguments.get("command", "")
        try:
            if not command.strip().startswith('curl'):
                return {"error": "命令必须以curl开头"}

            args = shlex.split(command)
            result = subprocess.run(args, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return {
                    "status": "success",
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                return {
                    "status": "error",
                    "code": result.returncode,
                    "stderr": result.stderr
                }
        except Exception as e:
            return {"error": str(e)}
