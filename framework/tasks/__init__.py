"""
模块验证框架 - 任务模块

包含所有预定义的测试任务
"""

from .current_sampling import CurrentSamplingTask
from .continuous_sampling import ContinuousSamplingTask

# 注册可用的任务
AVAILABLE_TASKS = {
    "current_sampling": {
        "name": "Current Sampling Task",
        "class": CurrentSamplingTask,
        "description": "定时电流采样任务，支持高精度定时和多通道采样",
        "parameters": {
            "duration_s": "采样持续时间(秒)",
            "interval_ms": "采样间隔(毫秒)",
            "channels": "采样通道列表"
        }
    },
    "continuous_sampling": {
        "name": "Continuous Sampling Task",
        "class": ContinuousSamplingTask,
        "description": "连续循环采样任务，支持用户交互终止和实时数据显示",
        "parameters": {
            "interval_ms": "采样间隔(毫秒)",
            "channels": "采样通道列表",
            "display_samples": "是否实时显示采样数据"
        }
    }
}

def get_task_list():
    """获取可用任务列表"""
    return list(AVAILABLE_TASKS.keys())

def create_task(task_type: str, adapter, module):
    """创建任务实例
    
    Args:
        task_type: 任务类型
        adapter: I2C适配器实例
        module: 模组实例
        
    Returns:
        任务实例或None
    """
    if task_type not in AVAILABLE_TASKS:
        return None
        
    task_info = AVAILABLE_TASKS[task_type]
    return task_info["class"](adapter, module)

def get_task_info(task_type: str):
    """获取任务信息
    
    Args:
        task_type: 任务类型
        
    Returns:
        任务信息或None
    """
    return AVAILABLE_TASKS.get(task_type)

__all__ = [
    "CurrentSamplingTask",
    "ContinuousSamplingTask",
    "AVAILABLE_TASKS",
    "get_task_list",
    "create_task",
    "get_task_info"
]
