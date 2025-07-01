"""
模块验证框架 - 模组模块

包含所有支持的I2C模组实现
"""

from .ina3221_module import INA3221Module
from .ina219_module import INA219Module

# 注册可用的模组
AVAILABLE_MODULES = {
    "ina3221": {
        "name": "INA3221 Triple Current Monitor",
        "class": INA3221Module,
        "description": "德州仪器INA3221三通道电流/电压监测芯片",
        "default_address": 0x40,
        "channels": 3,
        "measurements": ["current", "voltage", "power"]
    },
    "ina219": {
        "name": "INA219 Single Current Monitor",
        "class": INA219Module,
        "description": "德州仪器INA219单通道电流/电压/功率监测芯片",
        "default_address": 0x40,
        "channels": 1,
        "measurements": ["current", "voltage", "power"]
    }
}

def get_module_list():
    """获取可用模组列表"""
    return list(AVAILABLE_MODULES.keys())

def create_module(module_type: str, adapter, device_addr: int = None):
    """创建模组实例
    
    Args:
        module_type: 模组类型
        adapter: I2C适配器实例
        device_addr: 设备地址，None则使用默认地址
        
    Returns:
        模组实例或None
    """
    if module_type not in AVAILABLE_MODULES:
        return None
        
    module_info = AVAILABLE_MODULES[module_type]
    
    if device_addr is None:
        device_addr = module_info["default_address"]
        
    return module_info["class"](adapter, device_addr)

def get_module_info(module_type: str):
    """获取模组信息
    
    Args:
        module_type: 模组类型
        
    Returns:
        模组信息或None
    """
    return AVAILABLE_MODULES.get(module_type)

__all__ = [
    "INA3221Module",
    "INA219Module",
    "AVAILABLE_MODULES",
    "get_module_list",
    "create_module",
    "get_module_info"
]
