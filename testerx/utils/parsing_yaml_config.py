from typing import Dict, List, Optional
import yaml
from pathlib import Path


class AgentTemplateManager:
    """
    A class to manage and parse agent templates from YAML configuration.
    """

    def __init__(self, config_path: Optional[str] = None, config_dict: Optional[dict] = None):
        """
        Initialize the template manager either from a YAML file path or a dictionary.

        Args:
            config_path: Path to the YAML configuration file
            config_dict: Dictionary containing the configuration
        """
        if config_path and config_dict:
            raise ValueError("Please provide either config_path or config_dict, not both")

        if config_path:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        elif config_dict:
            self.config = config_dict
        else:
            raise ValueError("Must provide either config_path or config_dict")

        self.templates = self.config['agent']['templates']
        self.tools = self.config['agent'].get('tools', {})
        self.history_processors = self.config['agent'].get('history_processors', [])

    def get_system_prompt(self) -> str:
        """Get the system template."""
        return self.templates.get('system_template', '')

    def get_instance_prompt(self, problem_statement: str, open_file: str, working_dir: str) -> str:
        """
        Get the formatted instance template.

        Args:
            problem_statement: The issue or problem to be solved
            open_file: Currently open file
            working_dir: Current working directory
        """
        template = self.templates.get('instance_template', '')
        return template.format(
            problem_statement=problem_statement,
            open_file=open_file,
            working_dir=working_dir
        )

    def get_next_step_prompt(self,
                             observation: str,
                             open_file: str,
                             working_dir: str,
                             has_output: bool = True) -> str:
        """
        Get the formatted next step template.

        Args:
            observation: The observation from the previous step
            open_file: Currently open file
            working_dir: Current working directory
            has_output: Whether the previous command produced output
        """
        template = self.templates.get(
            'next_step_template' if has_output else 'next_step_no_output_template',
            ''
        )
        return template.format(
            observation=observation,
            open_file=open_file,
            working_dir=working_dir
        )

    def get_demonstration_prompt(self) -> str:
        """Get the demonstration template."""
        return self.templates.get('demonstration_template', '')

    def get_demonstrations(self) -> List[str]:
        """Get the list of demonstration paths."""
        return self.templates.get('demonstrations', [])

    def should_put_demos_in_history(self) -> bool:
        """Check if demonstrations should be included in history."""
        return self.templates.get('put_demos_in_history', False)

    def get_env_variables(self) -> Dict[str, str]:
        """Get environment variables configuration."""
        return self.tools.get('env_variables', {})

    def get_tool_bundles(self) -> List[Dict]:
        """Get tool bundles configuration."""
        return self.tools.get('bundles', [])

    def get_bash_tool_enabled(self) -> bool:
        """Check if bash tool is enabled."""
        return self.tools.get('enable_bash_tool', False)

    def get_parse_function_config(self) -> Dict:
        """Get parse function configuration."""
        return self.tools.get('parse_function', {})

    def get_history_processors(self) -> List[Dict]:
        """Get history processors configuration."""
        return self.history_processors

    def to_dict(self) -> Dict:
        """Convert the configuration back to a dictionary."""
        return self.config

    def save_config(self, path: str) -> None:
        """
        Save the current configuration to a YAML file.

        Args:
            path: Path where to save the YAML file
        """
        with open(path, 'w') as f:
            yaml.dump(self.config, f)


if __name__ == '__main__':
    cfg = AgentTemplateManager(config_path="./config/default.yaml")

    print(cfg.get_system_prompt())
