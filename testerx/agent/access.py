import json
from openai import OpenAI
from config import CHAT_MODEL, API_INFO
from testerx.agent.logger import ModelLogger
from testerx.tools import ToolManager, CurlTool, SystemCommandTool, MemoryStorageTool, StepCompletionTool
from datetime import datetime
from typing import List, Dict, Any, Optional


class OpenAIClient:
    """封装 OpenAI API 调用"""

    def __init__(self, provider, model):
        self.client = OpenAI(
            base_url=API_INFO[provider]["BASE_URL"],
            api_key=API_INFO[provider]["KEY"]
        )
        self.model = model

    def create_chat_completion(self, messages, tools=None, temperature=0, stream=False, max_tokens=None):
        params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        if tools:
            params["tools"] = tools
        if max_tokens:
            params["max_tokens"] = max_tokens
        return self.client.chat.completions.create(**params)


class ToolExecutor:
    """负责工具的执行和日志记录"""

    def __init__(self, tool_manager, logger):
        self.tool_manager = tool_manager
        self.logger = logger

    def execute_tool(self, tool_call):
        self._log_tool_call(tool_call)
        result = self.tool_manager.execute_tool(
            tool_call["function"]["name"],
            tool_call["function"]["arguments"]
        )
        self._log_tool_result(tool_call["function"]["name"], result)
        return {
            "tool_call_id": tool_call["id"],
            "output": json.dumps(result) if not isinstance(result, str) else result
        }

    def _log_tool_call(self, tool_call):
        self.logger.log(
            "tool_call", {
                "tool_name": tool_call["function"]["name"],
                "arguments": tool_call["function"]["arguments"]
            }
        )

    def _log_tool_result(self, tool_name, result):
        self.logger.log(
            "tool_result", {
                "tool_name": tool_name,
                "result": result
            }
        )


class ChatModel:
    def __init__(self):
        self.provider = CHAT_MODEL["provider"]
        self.model = CHAT_MODEL["model"]
        self.format = CHAT_MODEL["format"]
        self.logger = ModelLogger(log_file="res/model_operations.log")
        self.tool_manager = ToolManager()
        self.openai_client = OpenAIClient(self.provider, self.model)
        self.tool_executor = ToolExecutor(self.tool_manager, self.logger)
        self._init_default_tools()

    def _init_default_tools(self):
        """初始化默认工具"""
        self.tool_manager.register_tool(CurlTool())
        self.tool_manager.register_tool(MemoryStorageTool())
        self.tool_manager.register_tool(StepCompletionTool())
        self.tool_manager.register_tool(SystemCommandTool(allowed_commands=["ls", "cat", "echo"]))

        @self.tool_manager.register_function
        def get_current_time() -> Dict[str, str]:
            """获取当前系统时间"""
            return {"time": datetime.now().isoformat()}

    def register_tool(self, tool):
        """注册新工具"""
        self.tool_manager.register_tool(tool)

    def register_function(self, func=None, *, name=None, description=None):
        """将函数注册为工具"""
        return self.tool_manager.register_function(func, name=name, description=description)

    def chat(self, messages: List[Dict[str, str]], tools_to_use: Optional[List[str]] = None,
             stream=False, temperature=0, max_tokens=None) -> Any:
        """使用聊天模型生成响应"""
        self._log_request(messages, tools_to_use, temperature, max_tokens)
        tool_definitions = self.tool_manager.get_tool_definitions(tools_to_use) if tools_to_use else None
        response = self.openai_client.create_chat_completion(
            messages, tool_definitions, temperature, stream, max_tokens
        )
        response_dict = self._log_response(response)

        if response_dict["choices"][0]["message"]["tool_calls"]:
            tool_calls = response_dict["choices"][0]["message"]["tool_calls"]
            tool_results = [self.tool_executor.execute_tool(tool_call) for tool_call in tool_calls]
            final_response = self._handle_tool_results(messages, tool_calls, tool_results, temperature, max_tokens)
            return final_response["choices"][0]["message"]["content"]
        return response_dict["choices"][0]["message"]["content"]

    def _handle_tool_results(self, messages, tool_calls, tool_results, temperature, max_tokens):
        """处理工具结果并生成最终响应"""
        updated_messages = messages.copy()
        updated_messages.append(
            {
                "role": "assistant",
                "tool_calls": tool_calls
            }
        )
        for result in tool_results:
            updated_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": result["tool_call_id"],
                    "content": result["output"]
                }
            )
        final_response = self.openai_client.create_chat_completion(
            updated_messages, temperature=temperature, max_tokens=max_tokens
        )
        return self._log_final_response(final_response)

    def _log_request(self, messages, tools_to_use, temperature, max_tokens):
        """记录请求日志"""
        self.logger.log(
            "request", {
                "messages": messages,
                "tools_to_use": tools_to_use,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )

    def _log_response(self, response):
        """记录响应日志"""
        response_dict = {
            "id": response.id,
            "object": response.object,
            "created": response.created,
            "model": response.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content,
                        "tool_calls": [
                            {
                                "id": tool_call.id,
                                "type": tool_call.type,
                                "function": {
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                }
                            } for tool_call in choice.message.tool_calls
                        ] if choice.message.tool_calls else None
                    },
                    "finish_reason": choice.finish_reason
                } for choice in response.choices
            ]
        }
        self.logger.log("response", {"response": response_dict})
        return response_dict

    def _log_final_response(self, final_response):
        """记录最终响应日志"""
        final_response_dict = {
            "id": final_response.id,
            "object": final_response.object,
            "created": final_response.created,
            "model": final_response.model,
            "choices": [
                {
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content
                    },
                    "finish_reason": choice.finish_reason
                } for choice in final_response.choices
            ]
        }
        self.logger.log("final_response", {"response": final_response_dict})
        return final_response_dict
