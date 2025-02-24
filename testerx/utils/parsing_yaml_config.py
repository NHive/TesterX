from typing import Dict, List, Optional
import yaml


class AgentTemplateManager:
    """
    一个用于管理和解析来自 YAML 配置的代理模板的类。
    """

    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[dict] = None):
        """
        从 YAML 文件路径或字典初始化模板管理器。

        参数:
            config_path: YAML 配置文件的路径
            config_dict: 包含配置的字典
        """
        if config_path and config_dict:
            raise ValueError("请仅提供 config_path 或 config_dict，不要同时提供两者")

        if config_path:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        elif config_dict:
            self.config = config_dict
        else:
            raise ValueError("必须提供 config_path 或 config_dict")

        self.steps = self.config.get('steps', [])
        self.tools = self.config.get('tools', {})
        self.history_processors = self.config.get('history_processors', [])

    def get_step(self, step_number: int) -> Optional[Dict]:
        """从配置中获取特定的步骤。

        参数:
            step_number: 要获取的步骤编号。

        返回:
            步骤字典，如果找到；否则返回 None。
        """
        for step in self.steps:
            if step.get('step') == step_number:
                return step
        return None

    def get_system_template(self, step_number: int) -> Optional[str]:
        """获取特定步骤的系统模板。

        参数:
            step_number: 步骤编号。

        返回:
            系统模板字符串，如果找到；否则返回 None。
        """
        step = self.get_step(step_number)
        if step and step.get('templates'):
            return step['templates'].get('system_template', '')
        return None

    def get_instance_template(self, step_number: int, **kwargs) -> Optional[str]:
        """
        获取特定步骤的格式化实例模板。

        参数:
            step_number: 步骤编号。
            **kwargs: 用于格式化模板的变量。

        返回:
            格式化后的实例模板字符串，如果找到；否则返回 None。
        """
        step = self.get_step(step_number)
        if step and step.get('templates'):
            template = step['templates'].get('instance_template', '')
            try:
                return template.format(**kwargs)
            except KeyError as e:
                print(f"在格式化步骤 {step_number} 的模板时发生 KeyError：{e}")
                return None
        return None

    def get_briefly(self, step_number: int) -> Optional[str]:
        """获取特定步骤的简要描述。

        参数:
            step_number: 步骤编号。

        返回:
            简要描述字符串，如果找到；否则返回 None。
        """
        step = self.get_step(step_number)
        if step and step.get('templates'):
            return step['templates'].get('briefly', '')
        return None

    def get_tools(self, step_number: int) -> Optional[List[str]]:
        """获取特定步骤的工具列表。

        参数:
            step_number: 步骤编号。

        返回:
            工具列表，如果找到；否则返回 None。
        """
        step = self.get_step(step_number)
        if step:
            return step.get('tools', [])
        return None

    def get_env_variables(self) -> Dict[str, str]:
        """获取环境变量配置。"""
        return self.tools.get('env_variables', {})

    def get_tool_bundles(self) -> List[Dict]:
        """获取工具包配置。"""
        return self.tools.get('bundles', [])

    def get_bash_tool_enabled(self) -> bool:
        """检查 bash 工具是否启用。"""
        return self.tools.get('enable_bash_tool', False)

    def get_parse_function_config(self) -> Dict:
        """获取解析函数配置。"""
        return self.tools.get('parse_function', {})

    def get_history_processors(self) -> List[Dict]:
        """获取历史处理器配置。"""
        return self.history_processors

    def to_dict(self) -> Dict:
        """将配置转换回字典。"""
        return self.config

    def save_config(self, path: str) -> None:
        """
        将当前配置保存到 YAML 文件。

        参数:
            path: 要保存 YAML 文件的路径。
        """
        with open(path, 'w') as f:
            yaml.dump(self.config, f)

    def get_all_step_numbers(self) -> List[int]:
        """获取所有步骤编号的列表。"""
        return [step.get('step') for step in self.steps if step.get('step') is not None]


if __name__ == '__main__':
    cfg = AgentTemplateManager(config_path="config/default.yaml")  # 替换成你的yaml文件名

    # 示例用法:
    step_number = 1
    # print(f"步骤 {step_number} 系统模板:")
    # print(cfg.get_system_template(step_number))

    print(f"\n步骤 {step_number} 实例模板:")
    formatted_instance = cfg.get_instance_template(
        step_number, api_path="/users", base_url="http://example.com", api_doc="示例 API 文档"
    )
    print(formatted_instance)

    # print(f"\n步骤 {step_number} 简要描述:")
    # print(cfg.get_briefly(step_number))
    #
    # print(f"\n步骤 {step_number} 工具:")
    # print(cfg.get_tools(step_number))

    print(f"\n所有步骤编号:")
    print(cfg.get_all_step_numbers())
