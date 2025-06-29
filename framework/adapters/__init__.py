"""
模块验证框架 - 适配器模块

包含所有支持的I2C适配器实现
"""

from .ch341_adapter import CH341Adapter
from .cp2112_adapter import CP2112Adapter

# 注册可用的适配器
AVAILABLE_ADAPTERS = {
    "ch341": {
        "name": "CH341 USB-I2C Adapter",
        "class": CH341Adapter,
        "description": "基于WCH CH341芯片的USB转I2C适配器"
    },
    "cp2112": {
        "name": "CP2112 USB-I2C/SMBus Adapter", 
        "class": CP2112Adapter,
        "description": "基于Silicon Labs CP2112芯片的USB转I2C/SMBus适配器 (开发中)"
    }
}

def get_adapter_list():
    """获取可用适配器列表"""
    return list(AVAILABLE_ADAPTERS.keys())

def create_adapter(adapter_type: str, device_index: int = 0):
    """创建适配器实例
    
    Args:
        adapter_type: 适配器类型
        device_index: 设备索引
        
    Returns:
        适配器实例或None
    """
    if adapter_type not in AVAILABLE_ADAPTERS:
        return None
        
    adapter_info = AVAILABLE_ADAPTERS[adapter_type]
    return adapter_info["class"](device_index)

def get_adapter_info(adapter_type: str):
    """获取适配器信息
    
    Args:
        adapter_type: 适配器类型
        
    Returns:
        适配器信息或None
    """
    return AVAILABLE_ADAPTERS.get(adapter_type)

__all__ = [
    "CH341Adapter",
    "CP2112Adapter",
    "AVAILABLE_ADAPTERS",
    "get_adapter_list",
    "create_adapter", 
    "get_adapter_info"
]
