"""
模块验证框架 - 抽象接口定义

定义了适配器和模组的抽象接口，确保所有实现都遵循统一的规范。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional, Any
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdapterInterface(ABC):
    """I2C适配器抽象接口
    
    定义了所有I2C适配器必须实现的基本功能
    """
    
    def __init__(self, device_index: int = 0):
        """初始化适配器
        
        Args:
            device_index: 设备索引号
        """
        self.device_index = device_index
        self.is_opened = False
        self.name = "Unknown Adapter"
        
    @abstractmethod
    def open(self) -> bool:
        """打开I2C适配器
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        pass
        
    @abstractmethod
    def close(self) -> None:
        """关闭I2C适配器"""
        pass
        
    @abstractmethod
    def i2c_scan(self, start_addr: int = 0x08, end_addr: int = 0x77) -> List[int]:
        """扫描I2C总线上的设备
        
        Args:
            start_addr: 扫描起始地址
            end_addr: 扫描结束地址
            
        Returns:
            List[int]: 发现的设备地址列表
        """
        pass
        
    @abstractmethod
    def i2c_read_byte(self, device_addr: int, reg_addr: int) -> Optional[int]:
        """从I2C设备读取一个字节
        
        Args:
            device_addr: 设备地址
            reg_addr: 寄存器地址
            
        Returns:
            Optional[int]: 读取的数据，失败返回None
        """
        pass
        
    @abstractmethod
    def i2c_write_byte(self, device_addr: int, reg_addr: int, data: int) -> bool:
        """向I2C设备写入一个字节
        
        Args:
            device_addr: 设备地址
            reg_addr: 寄存器地址
            data: 要写入的数据
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        pass
        
    @abstractmethod
    def i2c_read_block(self, device_addr: int, reg_addr: int, length: int) -> Optional[bytes]:
        """从I2C设备读取多个字节
        
        Args:
            device_addr: 设备地址
            reg_addr: 寄存器地址
            length: 读取长度
            
        Returns:
            Optional[bytes]: 读取的数据，失败返回None
        """
        pass
        
    @abstractmethod
    def i2c_write_block(self, device_addr: int, reg_addr: int, data: bytes) -> bool:
        """向I2C设备写入多个字节
        
        Args:
            device_addr: 设备地址
            reg_addr: 寄存器地址
            data: 要写入的数据
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        pass
        
    def get_info(self) -> Dict[str, Any]:
        """获取适配器信息
        
        Returns:
            Dict[str, Any]: 适配器信息
        """
        return {
            "name": self.name,
            "device_index": self.device_index,
            "is_opened": self.is_opened
        }


class ModuleInterface(ABC):
    """I2C模组抽象接口
    
    定义了所有I2C模组必须实现的基本功能
    """
    
    def __init__(self, adapter: AdapterInterface, device_addr: int):
        """初始化模组
        
        Args:
            adapter: I2C适配器实例
            device_addr: 模组的I2C地址
        """
        self.adapter = adapter
        self.device_addr = device_addr
        self.is_initialized = False
        self.name = "Unknown Module"
        
    @abstractmethod
    def initialize(self) -> bool:
        """初始化模组
        
        Returns:
            bool: 成功返回True，失败返回False
        """
        pass
        
    @abstractmethod
    def read_current(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取电流值
        
        Args:
            channel: 通道号，None表示读取所有通道
            
        Returns:
            Union[float, List[float], None]: 单通道返回float，多通道返回List[float]，失败返回None
        """
        pass
        
    @abstractmethod
    def read_voltage(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取电压值
        
        Args:
            channel: 通道号，None表示读取所有通道
            
        Returns:
            Union[float, List[float], None]: 单通道返回float，多通道返回List[float]，失败返回None
        """
        pass
        
    @abstractmethod
    def read_power(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取功率值
        
        Args:
            channel: 通道号，None表示读取所有通道
            
        Returns:
            Union[float, List[float], None]: 单通道返回float，多通道返回List[float]，失败返回None
        """
        pass
        
    @abstractmethod
    def configure(self, **kwargs) -> bool:
        """配置模组参数
        
        Args:
            **kwargs: 配置参数
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        pass
        
    def get_info(self) -> Dict[str, Any]:
        """获取模组信息
        
        Returns:
            Dict[str, Any]: 模组信息
        """
        return {
            "name": self.name,
            "device_addr": f"0x{self.device_addr:02X}",
            "is_initialized": self.is_initialized,
            "adapter": self.adapter.name
        }


class TaskInterface(ABC):
    """任务抽象接口
    
    定义了所有任务必须实现的基本功能
    """
    
    def __init__(self, adapter: AdapterInterface, module: ModuleInterface):
        """初始化任务
        
        Args:
            adapter: I2C适配器实例
            module: I2C模组实例
        """
        self.adapter = adapter
        self.module = module
        self.name = "Unknown Task"
        
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行任务
        
        Args:
            **kwargs: 任务参数
            
        Returns:
            Dict[str, Any]: 任务执行结果
        """
        pass
        
    def get_info(self) -> Dict[str, Any]:
        """获取任务信息
        
        Returns:
            Dict[str, Any]: 任务信息
        """
        return {
            "name": self.name,
            "adapter": self.adapter.name,
            "module": self.module.name
        }
