import json
from openai import OpenAI
from config import CHAT_MODEL, API_INFO
from testerx.agent.logger import ModelLogger
from testerx.tools import ToolManager, CurlTool, SystemCommandTool, MemoryStorageTool, StepCompletionTool
from datetime import datetime
from typing import List


class ChatModel:
    def __init__(self):
        provider = CHAT_MODEL["provider"]
        self.model = CHAT_MODEL["model"]
        self.format = CHAT_MODEL["format"]
        self.client = OpenAI(
            base_url=API_INFO[provider]["BASE_URL"],
            api_key=API_INFO[provider]["KEY"]
        )
        self.tool_manager = ToolManager()
        self.logger = ModelLogger(log_file="model_operations.log")

        # 初始化默认工具
        self._init_default_tools()

    def _init_default_tools(self):
        """初始化默认工具"""
        # 注册curl工具
        self.tool_manager.register_tool(CurlTool())
        self.tool_manager.register_tool(MemoryStorageTool())
        self.tool_manager.register_tool(StepCompletionTool())

        # 注册系统命令工具(限制只能执行ls, cat, echo)
        self.tool_manager.register_tool(
            SystemCommandTool(allowed_commands=["ls", "cat", "echo"])
        )

        # 注册获取当前时间的工具
        @self.tool_manager.register_function
        def get_current_time():
            """获取当前系统时间"""
            return {"time": datetime.now().isoformat()}

    def register_tool(self, tool):
        """注册新工具"""
        self.tool_manager.register_tool(tool)

    def register_function(self, func=None, *, name=None, description=None):
        """将函数注册为工具"""
        return self.tool_manager.register_function(func, name=name, description=description)

    def handle_tool_calls(self, tool_calls):
        """处理工具调用"""
        results = []
        for tool_call in tool_calls:
            # 记录工具调用
            self.logger.log(
                "tool_call", {
                    "tool_name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            )

            result = self.tool_manager.execute_tool(
                tool_call.function.name,
                tool_call.function.arguments
            )

            # 记录工具执行结果
            self.logger.log(
                "tool_result", {
                    "tool_name": tool_call.function.name,
                    "result": result
                }
            )

            results.append(
                {
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result) if not isinstance(result, str) else result
                }
            )
        return results

    def chat(self, messages: list[dict], tools_to_use: List[str] = None,
             stream=False, temperature=0, max_tokens=None):
        """
        使用聊天模型生成响应
        :param messages: 对话历史消息列表
        :param tools_to_use: 要启用的工具名称列表,None表示不启用工具
        :param stream: 是否使用流式响应
        :param temperature: 温度参数，控制随机性
        :param max_tokens: 最大生成的token数
        :return: 聊天模型的响应
        """
        # 记录请求
        self.logger.log(
            "request", {
                "messages": messages,
                "tools_to_use": tools_to_use,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )

        # 构建请求参数
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }

        # 添加工具
        if tools_to_use is not None:
            tool_definitions = self.tool_manager.get_tool_definitions(tools_to_use)
            if tool_definitions:
                request_params["tools"] = tool_definitions

        if max_tokens:
            request_params["max_tokens"] = max_tokens

        # 处理流式响应
        if stream:
            response_stream = self.client.chat.completions.create(**request_params)
            return response_stream
        else:
            # 非流式响应
            response = self.client.chat.completions.create(**request_params)

            # 将 ChatCompletion 对象转换为可序列化的字典
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

            # 记录响应
            self.logger.log(
                "response", {
                    "response": response_dict
                }
            )

            # 处理工具调用
            if response.choices[0].message.tool_calls:
                tool_calls = response.choices[0].message.tool_calls

                # 执行工具调用并将结果添加到消息历史
                tool_results = self.handle_tool_calls(tool_calls)

                # 将工具调用和结果添加到消息历史
                updated_messages = messages.copy()
                updated_messages.append(
                    {
                        "role": "assistant",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": tc.type,
                                "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                            } for tc in tool_calls
                        ]
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

                # 使用更新后的消息历史再次调用API获取最终响应
                final_response = self.client.chat.completions.create(
                    model=self.model,
                    messages=updated_messages,
                    temperature=temperature,
                    max_tokens=max_tokens
                )

                # 将最终的 ChatCompletion 对象转换为可序列化的字典
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

                # 记录最终响应
                self.logger.log(
                    "final_response", {
                        "response": final_response_dict
                    }
                )

                return final_response.choices[0].message.content

            return response.choices[0].message.content


# 使用示例
def example_usage():
    # 创建聊天模型
    chat_model = ChatModel()

    # 准备对话历史
    messages = [
        {"role": "system",
         "content": "你是一个专业的 API 测试工程师，请根据提供的文档完成用户任务,你可以利用curl来请求接口,保证接口能正常调通,你拥有两层记忆系统,分别为基于整个项目的长期记忆,以及每个步骤完成后你可以为下个步骤传递所需的关键信息"},
        {"role": "user", "content": """
### 当前任务目标
1. 接口分析
   - 分析接口的基本信息(路径、方法、参数等)
   - 确定接口的业务场景
   - 识别接口的权限要求
   - 分析与其他接口的依赖关系

2. 接口验证
   - 验证必填参数
   - 验证参数格式
   - 验证权限要求
   - 验证基本响应

3. 文档生成
   - 接口基本信息
   - 参数详细说明
   - 依赖接口列表
   - 调用示例(curl)
   - 可能的错误响应
   
### 下一步任务目标
调试该接口,测试边界情况
   
### 输入上下文
1. 系统信息
   - 环境: 测试环境
   - Base URL: http://10.1.1.252:18221
   - API版本: v1

2. 通用参数说明
   - uuid: 设备唯一标识
   - timestamp: 请求时间戳
   - sign: 签名
   - Authorization: 认证token

#### 以下是所有接口的简要说明,你可以根据该文档判断需要测试的接口业务逻辑

```
path,method,summary,description,operationId,tags,parameters,requestBody,responses
/api/v1/account/user_devices,get,获取当前用户下的设备信息,,,设备端用户相关,uuid(query);timestamp(query);sign(query);Authorization(header),,200()
/api/v1/account/user_devices/{device_id},delete,登出指定设备(也可以登出本机),,,设备端用户相关,device_id(path);uuid(query);timestamp(query);sign(query);Authorization(header),,200()
/api/v1/account/user_features,get,获取用户当前会员等级及功能,,,设备端用户相关/会员,uuid(query);timestamp(query);sign(query);Authorization(header),,200()
/api/v1/account/user_info,get,获取当前用户信息,,,设备端用户相关,uuid(query);timestamp(query);sign(query);Authorization(header),,200()
/api/v1/admin/devices,get,获取在线设备,,,管理设备,Authorization(header),,200()
/api/v1/admin/devices/message,post,给设备发送消息,,,管理设备,Authorization(header),application/json(object),200()
/api/v1/admin/devices/{device_id},delete,删除在线设备,,,管理设备,device_id(path);Authorization(header),,200()
/api/v1/admin/users,get,获取用户设备,,,管理设备,Authorization(header),,200()
/api/v1/admin/users/{user_id}/stats,get,获取用户下设备详情,,,管理设备,user_id(path);Authorization(header),,200()
/api/v1/device-clipboard/download,post,指定剪切板数据下载,,,设备端/剪切板,uuid(query);timestamp(query);sign(query);Authorization(header),application/json(object),200()
/api/v1/device-clipboard/labels,get,获取当前设备的标签,,,设备端/剪切板标签,uuid(query);timestamp(query);sign(query);Authorization(header),,200()
/api/v1/device-clipboard/labels,post,设置当前设备的标签,,,设备端/剪切板标签,uuid(query);timestamp(query);sign(query);Authorization(header),application/json(object),200()
/api/v1/device-clipboard/labels/changes,get,获取标签变更数据,,,设备端/剪切板标签,uuid(query);timestamp(query);sign(query);last_sync_time(query);Authorization(header),,200()
/api/v1/device-clipboard/labels/changes,post,上传标签变更数据,,,设备端/剪切板标签,uuid(query);timestamp(query);sign(query);Authorization(header),application/json(object),200()
/api/v1/device-clipboard/merge,post,合并云端剪切板变更,"提供上次同步数据的时间,在提供大于上次同步时间的数据hash,返回所有再次期间的数据",,设备端/剪切板,uuid(query);timestamp(query);sign(query);Authorization(header),application/json(object),200()
/api/v1/device-clipboard/record,post,上传变更日志,,,设备端/剪切板,uuid(query);timestamp(query);sign(query);Authorization(header),application/json(object),200()
/api/v1/device-clipboard/stream,get,剪贴板变更事件,,,设备端/剪切板,uuid(query);timestamp(query);sign(query);Authorization(header),,200()
/api/v1/device-clipboard/upload,post,数据上传,,,设备端/剪切板,uuid(query);timestamp(query);sign(query);Authorization(header),application/json(object),200()
/api/v1/device/bind_user,post,绑定设备到用户,,,设备端/鉴权,uuid(query);timestamp(query);sign(query);Authorization(header),application/json(object),200()
/api/v1/device/check_auth,get,鉴权检查,,,设备端/鉴权,uuid(query);timestamp(query);sign(query);Authorization(header),,200()
/api/v1/device/register,post,注册设备,,,设备端/鉴权,Authorization(header),application/json(object),200()
/api/v1/device/run_record,post,启动记录,,,设备端,uuid(query);timestamp(query);sign(query);Authorization(header),application/json(object),200()
/api/v1/gen_204,get,连通性检测,,,设备端,Authorization(header),,200()
/api/v1/message/send-code,post,发送验证码,,,用户账号/注册,Authorization(header),application/json(object),200()
/api/v1/storage/callback,post,七牛云上传文件回调,,,对象存储,Authorization(header),,200()
/api/v1/timestamp,get,获取服务器时间,,,设备端,Authorization(header),,200()
/api/v1/user/2fa-send-code,post,发送二步验证码,,,用户账号/登录,Authorization(header),application/json(object),200()
/api/v1/user/2fa-verify-code,post,二步验证,,,用户账号/登录,Authorization(header),application/json(object),200()
/api/v1/user/login,post,登录,,,用户账号/登录,Authorization(header),application/json(object),200()
/api/v1/user/register,post,注册,,,用户账号/注册,Authorization(header),application/json(object),200()
```



### warning
- 请保证接口调试没问题的情况下在输出文档,如果有任何疑问,你可以先询问用户

### 验证步骤
1. 参数验证
   - 必填参数缺失测试
   - 参数格式错误测试
   - 参数边界值测试

2. 权限验证
   - 无token测试
   - token过期测试
   - 错误token测试

3. 功能验证
   - 正常请求测试
   - 响应格式验证
   - 响应字段验证

### 错误处理
- 如遇到接口调用失败,请详细记录:
  1. 请求参数
  2. 错误响应
  3. 错误码
  4. 可能的原因

### BASE_URL
- http://10.1.1.252:18221

请帮我完成/api/v1/admin/devices接口的文档,每条信息使用store_memory存储,这个note文档用于后面进行嵌入搜索用于后续的步骤,每条note对项目来说都是一个长期记忆,所以这个note应该与该接口高度相关,以便后续搜索时能为模型提供更精确的信息
在完成该接口相关的文档编写后,使用complete_step命令结束当前步骤,并传递下一步骤所需的关键信息,除此之外,不需要任何其他输出,最后结束时总结该步骤所做事项,最后的总结会原样提供给下个步骤
        """}
    ]

    # 指定要使用的工具
    response = chat_model.chat(
        messages,
        tools_to_use=["store_memory", "execute_curl", "complete_step"],
        temperature=0,
    )
    print(response)


if __name__ == '__main__':
    example_usage()
