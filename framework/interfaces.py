"""
模块验证框架 - 抽象接口定义

定义了适配器和模组的抽象接口，确保所有实现都遵循统一的规范。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Union, Optional, Any
import logging
from enum import Enum

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PinID(Enum):
    """统一的引脚ID定义
    
    定义了所有适配器可能支持的引脚类型，具体适配器可以选择性实现
    """
    # 数据引脚 (通用GPIO)
    GPIO_0 = "GPIO_0"
    GPIO_1 = "GPIO_1"
    GPIO_2 = "GPIO_2"
    GPIO_3 = "GPIO_3"
    GPIO_4 = "GPIO_4"
    GPIO_5 = "GPIO_5"
    GPIO_6 = "GPIO_6"
    GPIO_7 = "GPIO_7"
    
    # 并口数据引脚
    DATA_0 = "DATA_0"
    DATA_1 = "DATA_1"
    DATA_2 = "DATA_2"
    DATA_3 = "DATA_3"
    DATA_4 = "DATA_4"
    DATA_5 = "DATA_5"
    DATA_6 = "DATA_6"
    DATA_7 = "DATA_7"
    
    # I2C引脚
    I2C_SCL = "I2C_SCL"
    I2C_SDA = "I2C_SDA"
    
    # SPI引脚
    SPI_MOSI = "SPI_MOSI"
    SPI_MISO = "SPI_MISO"
    SPI_CLK = "SPI_CLK"
    SPI_CS = "SPI_CS"
    
    # 控制引脚
    RESET = "RESET"
    ENABLE = "ENABLE"
    INTERRUPT = "INTERRUPT"
    READY = "READY"
    
    # 并口控制引脚
    WRITE = "WRITE"
    READ = "READ"
    ADDR_STROBE = "ADDR_STROBE"
    DATA_STROBE = "DATA_STROBE"
    
    # 状态引脚
    ERROR = "ERROR"
    BUSY = "BUSY"
    SELECT = "SELECT"
    WAIT = "WAIT"


class PinDirection(Enum):
    """引脚方向定义"""
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    BIDIRECTIONAL = "BIDIRECTIONAL"


class PinLevel(Enum):
    """引脚电平定义"""
    LOW = 0
    HIGH = 1


class PinCapability:
    """引脚能力描述"""
    
    def __init__(self, pin_id: PinID, direction: PinDirection, description: str = ""):
        self.pin_id = pin_id
        self.direction = direction
        self.description = description
        self.is_available = True
        self.current_level = PinLevel.LOW
        
    def __repr__(self):
        return f"PinCapability({self.pin_id.value}, {self.direction.value}, available={self.is_available})"


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
        self._pin_capabilities: Dict[PinID, PinCapability] = {}
        
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
    
    # ============= 引脚控制功能 =============
    
    @abstractmethod
    def get_supported_pins(self) -> List[PinCapability]:
        """获取支持的引脚列表
        
        Returns:
            List[PinCapability]: 支持的引脚能力列表
        """
        pass
    
    @abstractmethod
    def set_pin_direction(self, pin_id: PinID, direction: PinDirection) -> bool:
        """设置引脚方向
        
        Args:
            pin_id: 引脚ID
            direction: 引脚方向
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        pass
    
    @abstractmethod
    def set_pin_level(self, pin_id: PinID, level: PinLevel) -> bool:
        """设置引脚电平
        
        Args:
            pin_id: 引脚ID
            level: 引脚电平
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        pass
    
    @abstractmethod
    def get_pin_level(self, pin_id: PinID) -> Optional[PinLevel]:
        """读取引脚电平
        
        Args:
            pin_id: 引脚ID
            
        Returns:
            Optional[PinLevel]: 引脚电平，失败返回None
        """
        pass
    
    @abstractmethod
    def set_multiple_pins(self, pin_levels: Dict[PinID, PinLevel]) -> bool:
        """同时设置多个引脚电平
        
        Args:
            pin_levels: 引脚ID到电平的映射
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        pass
    
    @abstractmethod
    def get_multiple_pins(self, pin_ids: List[PinID]) -> Dict[PinID, PinLevel]:
        """同时读取多个引脚电平
        
        Args:
            pin_ids: 要读取的引脚ID列表
            
        Returns:
            Dict[PinID, PinLevel]: 引脚ID到电平的映射
        """
        pass
    
    def is_pin_supported(self, pin_id: PinID) -> bool:
        """检查引脚是否支持
        
        Args:
            pin_id: 引脚ID
            
        Returns:
            bool: 支持返回True，不支持返回False
        """
        return pin_id in self._pin_capabilities
    
    def get_pin_capability(self, pin_id: PinID) -> Optional[PinCapability]:
        """获取引脚能力信息
        
        Args:
            pin_id: 引脚ID
            
        Returns:
            Optional[PinCapability]: 引脚能力，不支持返回None
        """
        return self._pin_capabilities.get(pin_id)
    
    def toggle_pin(self, pin_id: PinID) -> bool:
        """切换引脚电平
        
        Args:
            pin_id: 引脚ID
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        current_level = self.get_pin_level(pin_id)
        if current_level is None:
            return False
        
        new_level = PinLevel.LOW if current_level == PinLevel.HIGH else PinLevel.HIGH
        return self.set_pin_level(pin_id, new_level)
    
    def pulse_pin(self, pin_id: PinID, duration_ms: int = 1) -> bool:
        """产生引脚脉冲
        
        Args:
            pin_id: 引脚ID
            duration_ms: 脉冲持续时间(毫秒)
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        import time
        
        # 获取当前电平
        original_level = self.get_pin_level(pin_id)
        if original_level is None:
            return False
        
        # 切换到相反电平
        pulse_level = PinLevel.LOW if original_level == PinLevel.HIGH else PinLevel.HIGH
        if not self.set_pin_level(pin_id, pulse_level):
            return False
        
        # 等待指定时间
        time.sleep(duration_ms / 1000.0)
        
        # 恢复原始电平
        return self.set_pin_level(pin_id, original_level)
        
    def get_info(self) -> Dict[str, Any]:
        """获取适配器信息
        
        Returns:
            Dict[str, Any]: 适配器信息
        """
        return {
            "name": self.name,
            "device_index": self.device_index,
            "is_opened": self.is_opened,
            "supported_pins": [cap.pin_id.value for cap in self.get_supported_pins()],
            "pin_count": len(self._pin_capabilities)
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
