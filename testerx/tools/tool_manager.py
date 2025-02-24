import json
from typing import Dict, List, Any, Callable, Optional
from .base import Tool
from .python_function_tool import PythonFunctionTool


class ToolManager:
    """工具管理器,负责管理和提供工具"""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        """注册一个新工具"""
        self.tools[tool.name] = tool

    def register_function(self, func=None, *, name=None, description=None):
        """将Python函数注册为工具的装饰器"""

        def decorator(f):
            tool = PythonFunctionTool(f, name=name, description=description)
            self.register_tool(tool)
            return f

        if func is None:
            return decorator
        return decorator(func)

    def get_tool_definitions(self, tool_names: List[str] = None) -> List[dict]:
        """获取指定工具的定义"""
        if tool_names is None:
            return [tool.get_definition() for tool in self.tools.values()]

        definitions = []
        for name in tool_names:
            if name in self.tools:
                definitions.append(self.tools[name].get_definition())
        return definitions

    def execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """执行指定的工具"""
        if tool_name not in self.tools:
            return {"error": f"未知工具: {tool_name}"}

        try:
            parsed_args = json.loads(arguments) if isinstance(arguments, str) else arguments
            return self.tools[tool_name].execute(parsed_args)
        except json.JSONDecodeError:
            return {"error": "参数解析失败"}
        except Exception as e:
            return {"error": f"工具执行失败: {str(e)}"}
