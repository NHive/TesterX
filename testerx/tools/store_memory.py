from typing import Any
from .base import Tool
import time
from datetime import datetime


class MemoryStorageTool(Tool):
    """用于存储长期记忆的工具"""

    def __init__(self):
        """
        初始化记忆存储工具
        """
        super().__init__(
            name="store_memory",
            description="将知识存储到长期记忆中,用于后续检索。输入的内容会被保存并在未来的对话中可被检索",
            param_schema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "要存储的知识内容"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "与内容相关的元数据",
                        "properties": {
                            "source": {
                                "type": "string",
                                "description": "知识的来源"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "知识的标签列表"
                            }
                        }
                    }
                },
                "required": ["content"]
            }
        )

    def execute(self, arguments: dict) -> dict:
        """
        执行记忆存储

        Args:
            arguments: 包含content和可选metadata的字典

        Returns:
            dict: 存储操作的结果
        """
        try:
            content = arguments.get("content")
            metadata = arguments.get("metadata", {})

            # 添加时间戳
            metadata["timestamp"] = datetime.now().isoformat()

            print(arguments)

            return {
                "status": "success",
                "message": "成功存储到长期记忆",
                "doc_id": 1,
                "metadata": metadata
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"存储失败: {str(e)}"
            }
