import inspect
from typing import Callable, Optional, Dict, List, Any
from .base import Tool


class PythonFunctionTool(Tool):
    """将Python函数包装为工具"""

    def __init__(self, func: Callable, name: Optional[str] = None, description: Optional[str] = None):
        self.func = func
        func_name = name or func.__name__
        func_doc = description or (func.__doc__ or f"执行{func_name}函数")
        param_schema = self._generate_param_schema()

        super().__init__(
            name=func_name,
            description=func_doc,
            param_schema=param_schema
        )

    def _generate_param_schema(self) -> dict:
        """从函数签名生成JSON Schema"""
        sig = inspect.signature(self.func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param.default is inspect.Parameter.empty:
                required.append(param_name)

            param_type = param.annotation if param.annotation is not inspect.Parameter.empty else None
            param_info = {"description": f"{param_name}参数"}

            if param_type:
                if param_type == str:
                    param_info["type"] = "string"
                elif param_type == int:
                    param_info["type"] = "integer"
                elif param_type == float:
                    param_info["type"] = "number"
                elif param_type == bool:
                    param_info["type"] = "boolean"
                elif param_type == list or param_type == List:
                    param_info["type"] = "array"
                elif param_type == dict or param_type == Dict:
                    param_info["type"] = "object"

            properties[param_name] = param_info

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    def execute(self, arguments: dict) -> Any:
        """执行包装的Python函数"""
        try:
            return self.func(**arguments)
        except Exception as e:
            return {"error": str(e)}
