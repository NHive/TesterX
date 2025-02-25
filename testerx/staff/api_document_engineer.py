from testerx.agent.chat import ChatModel as BaseChatModel
from testerx.utils.parsing_yaml_config import AgentTemplateManager
from typing import List, Dict, Any, Optional


class TemplatedChatModel:
    """
    结合 ChatModel 和 AgentTemplateManager，实现基于模板的聊天模型。
    """

    def __init__(self, config_path: str):
        """
        初始化 TemplatedChatModel。

        参数:
            config_path: YAML 配置文件路径，用于 AgentTemplateManager。
        """
        self.template_manager = AgentTemplateManager(config_path=config_path)
        self.chat_model = BaseChatModel()

    def run_step(self, step_number: int, instance_kwargs: Optional[Dict] = None, user_input: Optional[str] = None,
                 stream=False, temperature=0, max_tokens=None) -> Any:
        """
        运行指定步骤的聊天流程。

        参数:
            step_number: 要运行的步骤编号，对应于 YAML 配置文件中的步骤。
            instance_kwargs: 实例模板的参数，用于格式化 instance_template。
            user_input: 用户输入内容，如果步骤模板需要用户输入，则传入。
            stream: 是否使用流模式。
            temperature: 模型温度参数。
            max_tokens: 模型最大 token 限制。

        返回:
            模型的响应内容。
        """
        system_template = self.template_manager.get_system_template(step_number)
        instance_template = self.template_manager.get_instance_template(step_number, **(instance_kwargs or {}))
        tools_to_use = self.template_manager.get_tools(step_number)

        messages = []
        if system_template:
            messages.append({"role": "system", "content": system_template})
        if instance_template:
            messages.append({"role": "user", "content": instance_template})
        if user_input:
            messages.append({"role": "user", "content": user_input})

        if not messages:
            raise ValueError(f"步骤 {step_number} 没有可用的消息模板。")

        response = self.chat_model.chat(
            messages,
            tools_to_use=tools_to_use,
            stream=stream,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response

    def register_tool(self, tool):
        """注册新工具到 ChatModel"""
        self.chat_model.register_tool(tool)

    def register_function(self, func=None, *, name=None, description=None):
        """注册函数工具到 ChatModel"""
        return self.chat_model.register_function(func, name=name, description=description)


def example_templated_usage():
    # 创建 TemplatedChatModel 实例，指定配置文件路径
    templated_model = TemplatedChatModel(config_path="config/default.yaml")  # 替换成你的yaml文件名

    # 准备步骤 1 的模板参数
    step1_kwargs = {
        "api_path": "/api/v1/admin/devices",
        "base_url": "http://10.1.1.252:18221",
        "api_doc": "请参考之前的接口文档"
    }

    # 运行步骤 1
    response_step1 = templated_model.run_step(
        step_number=1,
        instance_kwargs=step1_kwargs,
        temperature=0
    )
    print(f"步骤 1 响应:\n{response_step1}")


if __name__ == '__main__':
    example_templated_usage()
