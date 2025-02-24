from datetime import datetime
from typing import Dict, List, Callable, Any, Optional, Union
import json


class ModelLogger:
    """模型操作记录器，用于记录模型的每一步操作"""

    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.logs = []

    def log(self, action: str, data: dict):
        """记录一个操作"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "data": data
        }
        self.logs.append(log_entry)

        # 如果指定了日志文件，则将日志写入文件
        if self.log_file:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def get_logs(self) -> List[dict]:
        """获取所有日志"""
        return self.logs

    def clear_logs(self):
        """清空日志"""
        self.logs = []
