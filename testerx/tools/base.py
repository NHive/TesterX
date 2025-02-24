from typing import Any


class Tool:
    """工具基类,所有工具都继承自这个类"""

    def __init__(self, name: str, description: str, param_schema: dict):
        self.name = name
        self.description = description
        self.param_schema = param_schema

    def get_definition(self) -> dict:
        """返回OpenAI格式的工具定义"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.param_schema
            }
        }

    def execute(self, arguments: dict) -> Any:
        """执行工具,子类应该重写这个方法"""
        raise NotImplementedError("子类必须实现execute方法")
