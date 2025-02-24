from typing import Any
from .base import Tool


class StepCompletionTool(Tool):
    """用于标记当前步骤完成，并开始下一步任务的工具，可以传递关键记忆"""

    def __init__(self):
        """
        初始化步骤完成工具
        """
        super().__init__(
            name="complete_step",
            description="标记当前步骤已完成，并触发下一步任务。可以传递关键记忆给下一步任务。",
            param_schema={
                "type": "object",
                "properties": {
                    "key_memories": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "传递给下一步任务的关键记忆列表"
                    }
                },
                "required": []
            }
        )

    def execute(self, arguments: dict) -> dict:
        """
        执行步骤完成操作，并传递关键记忆

        Args:
            arguments: 包含可选的 key_memories 列表的字典

        Returns:
            dict: 步骤完成的结果，包含关键记忆
        """
        try:
            key_memories = arguments.get("key_memories", [])

            # 在这里可以添加一些逻辑，例如通知下一步任务开始等
            print("当前步骤已完成，正在触发下一步任务...")
            print(f"传递的关键记忆：{key_memories}")

            return {
                "status": "success",
                "message": "当前步骤已成功完成，下一步任务已触发。",
                "key_memories": key_memories
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"步骤完成操作失败: {str(e)}"
            }
