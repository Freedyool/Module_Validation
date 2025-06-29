"""
模块验证框架 - 框架核心模块

提供框架的基础功能和工具函数
"""

from .interfaces import AdapterInterface, ModuleInterface, TaskInterface

__version__ = "1.0.0"
__author__ = "Module Validation Framework"

__all__ = [
    "AdapterInterface",
    "ModuleInterface", 
    "TaskInterface"
]
