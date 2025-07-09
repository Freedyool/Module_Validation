"""
CH341 I2C适配器实现

基于CH341 USB转I2C芯片的适配器实现
"""

import os
import sys
import time
from ctypes import *
from typing import List, Optional, Dict, Any

# 相对导入父级模块
from ..interfaces import AdapterInterface, PinID, PinDirection, PinLevel, PinCapability
import logging

logger = logging.getLogger(__name__)

class CH341Adapter(AdapterInterface):
    """CH341 USB转I2C适配器"""
    
    def __init__(self, device_index: int = 0):
        super().__init__(device_index)
        self.name = "CH341 USB-I2C Adapter"
        self.ch341 = None
        self.dll_loaded = False
        
        # 初始化CH341支持的引脚
        self._init_pin_capabilities()
        
        # 尝试加载DLL
        self._load_dll()
    
    def _init_pin_capabilities(self):
        """初始化CH341支持的引脚定义"""
        self._pin_capabilities = {
            # 数据引脚 D0-D7
            PinID.DATA_0: PinCapability(PinID.DATA_0, PinDirection.BIDIRECTIONAL, "数据引脚D0"),
            PinID.DATA_1: PinCapability(PinID.DATA_1, PinDirection.BIDIRECTIONAL, "数据引脚D1"),
            PinID.DATA_2: PinCapability(PinID.DATA_2, PinDirection.BIDIRECTIONAL, "数据引脚D2"),
            PinID.DATA_3: PinCapability(PinID.DATA_3, PinDirection.BIDIRECTIONAL, "数据引脚D3"),
            PinID.DATA_4: PinCapability(PinID.DATA_4, PinDirection.BIDIRECTIONAL, "数据引脚D4"),
            PinID.DATA_5: PinCapability(PinID.DATA_5, PinDirection.BIDIRECTIONAL, "数据引脚D5"),
            PinID.DATA_6: PinCapability(PinID.DATA_6, PinDirection.BIDIRECTIONAL, "数据引脚D6"),
            PinID.DATA_7: PinCapability(PinID.DATA_7, PinDirection.BIDIRECTIONAL, "数据引脚D7"),
            
            # I2C引脚
            PinID.I2C_SCL: PinCapability(PinID.I2C_SCL, PinDirection.OUTPUT, "I2C时钟引脚"),
            PinID.I2C_SDA: PinCapability(PinID.I2C_SDA, PinDirection.BIDIRECTIONAL, "I2C数据引脚"),
            
            # 控制引脚
            PinID.RESET: PinCapability(PinID.RESET, PinDirection.OUTPUT, "复位引脚"),
            PinID.WRITE: PinCapability(PinID.WRITE, PinDirection.OUTPUT, "写信号引脚"),
            PinID.READ: PinCapability(PinID.READ, PinDirection.OUTPUT, "读信号引脚"),
            PinID.ADDR_STROBE: PinCapability(PinID.ADDR_STROBE, PinDirection.OUTPUT, "地址选通引脚"),
            PinID.DATA_STROBE: PinCapability(PinID.DATA_STROBE, PinDirection.OUTPUT, "数据选通引脚"),
            
            # 状态引脚
            PinID.ERROR: PinCapability(PinID.ERROR, PinDirection.INPUT, "错误信号引脚"),
            PinID.BUSY: PinCapability(PinID.BUSY, PinDirection.INPUT, "忙信号引脚"),
            PinID.SELECT: PinCapability(PinID.SELECT, PinDirection.INPUT, "选择信号引脚"),
            PinID.WAIT: PinCapability(PinID.WAIT, PinDirection.INPUT, "等待信号引脚"),
            
            # 兼容模式 使用 P8/P9 作为 GPIO 输出引脚
            PinID.GPIO_0: PinCapability(PinID.GPIO_0, PinDirection.BIDIRECTIONAL, "GPIO引脚0"),
            PinID.GPIO_1: PinCapability(PinID.GPIO_1, PinDirection.BIDIRECTIONAL, "GPIO引脚1"),
        }

        self.enable_mask = 0x1F
        '''
        If bit 0 is 1, bits 15 to 8 of iSetDataOut are valid. Otherwise, it is ignored
        If bit 1 is 1, bits 15 to 8 of iSetDirOut are valid. Otherwise, the value is ignored
        If bit 2 is 1, the 7-bit 0 of iSetDataOut is valid. Otherwise, it is ignored
        If bit 3 is 1, the iSetDirOut bit 7 to bit 0 is valid. Otherwise, the iSetDirOut bit is ignored
        If bit 4 is 1, bits 23 to 16 of iSetDataOut are valid. Otherwise, it is ignored
        '''
        self.dir_mask = 0x000FC000 # default direction mask
        self.data_mask = 0x0080EFFF # default data mask
    
    def _load_dll(self):
        """加载CH341 DLL库"""
        try:
            # 获取DLL路径
            current_dir = os.path.dirname(os.path.abspath(__file__))
            dll_path = os.path.join(current_dir, "..", "..", "device", "ch341", "Release")
            
            # 检测系统架构并选择合适的DLL
            if sys.maxsize > 2**32:
                dll_file = "CH341DLLA64.DLL"
            else:
                dll_file = "CH341DLL.DLL"
            
            dll_full_path = os.path.join(dll_path, dll_file)
            
            if os.path.exists(dll_full_path):
                self.ch341 = windll.LoadLibrary(dll_full_path)
                self.dll_loaded = True
                logger.info(f"成功加载: {dll_file}")
            else:
                logger.error(f"找不到DLL文件: {dll_full_path}")
                self.dll_loaded = False
                
        except Exception as e:
            logger.error(f"加载DLL失败: {e}")
            self.dll_loaded = False
    
    def _pin_id_to_bit(self, pin_id: PinID) -> Optional[int]:
        """将引脚ID转换为位位置"""
        pin_map = {
            PinID.DATA_0: 0,
            PinID.DATA_1: 1,
            PinID.DATA_2: 2,
            PinID.DATA_3: 3,
            PinID.DATA_4: 4,
            PinID.DATA_5: 5,
            PinID.DATA_6: 6,
            PinID.DATA_7: 7,
        }
        return pin_map.get(pin_id)
    
    def _gpio_pin_to_bit(self, pin_id: PinID) -> Optional[int]:
        """将GPIO引脚ID转换为位位置"""
        gpio_map = {
            PinID.GPIO_0: 8,  # P8
            PinID.GPIO_1: 9,  # P9
        }
        return gpio_map.get(pin_id)
    
    def _pin_id_to_status_bit(self, pin_id: PinID) -> Optional[int]:
        """将引脚ID转换为状态位位置"""
        # 根据CH341的状态寄存器定义
        status_map = {
            PinID.ERROR: 8,      # ERR#
            PinID.BUSY: 9,       # PEMP
            PinID.INTERRUPT: 10,  # INT#
            PinID.SELECT: 11,     # SLCT
            PinID.WAIT: 13,       # WAIT#
            PinID.DATA_STROBE: 14,  # DATAS#/READ#
            PinID.ADDR_STROBE: 15,  # ADDRS#/ADDR/ALE
            PinID.RESET: 16,    # RESET
            # PinID.READ: 14,    # READ# (已包含在DATA_STROBE中)
            PinID.WRITE: 17,    # WRITE#
            PinID.I2C_SCL: 18,    # SCL
            PinID.I2C_SDA: 29,    # SDA
        }
        return status_map.get(pin_id)
    
    def get_supported_pins(self) -> List[PinCapability]:
        """获取支持的引脚列表"""
        return list(self._pin_capabilities.values())
    
    def set_pin_direction(self, pin_id: PinID, direction: PinDirection) -> bool:
        """设置引脚方向"""
        if not self.dll_loaded or not self.is_opened:
            logger.error("设备未打开或DLL未加载")
            return False
        
        if not self.is_pin_supported(pin_id):
            logger.error(f"不支持的引脚: {pin_id}")
            return False
        
        # 对于数据引脚，使用CH341SetOutput来设置方向
        bit_pos = self._pin_id_to_bit(pin_id)
        if bit_pos is not None:
            try:
                if direction == PinDirection.OUTPUT:
                    # 设置为输出模式，需要同时设置方向和初始值
                    enable_mask = 0xC # 0xC表示同时设置D7-D0引脚的方向和初始值
                    self.dir_mask |= 1 << bit_pos  # 设置方向掩码
                    self.data_mask &= ~(1 << bit_pos)  # 清除数据掩码中的该位
                    
                    result = self.ch341.CH341SetOutput(
                        self.device_index,
                        enable_mask,
                        self.dir_mask,
                        self.data_mask
                    )
                    return result != 0
                else:
                    # 设置为输入模式
                    enable_mask = 0x8 # 0x8表示仅设置D7-D0引脚的方向
                    self.dir_mask &= ~(1 << bit_pos)  # 设置方向掩码
                    data_mask = 0  # 输入模式不需要设置数据掩码
                    
                    result = self.ch341.CH341SetOutput(
                        self.device_index,
                        enable_mask,
                        self.dir_mask,
                        data_mask
                    )
                    return result != 0
            except Exception as e:
                logger.error(f"设置引脚方向失败: {e}")
                return False
            
        # 兼容模式
        bit_pos = self._gpio_pin_to_bit(pin_id)
        if bit_pos is not None:
            try:
                if direction == PinDirection.OUTPUT:
                    # 设置为输出模式
                    enable_mask = 0x3 # 0x3表示同时设置P8-P15引脚的方向和初始值
                    self.dir_mask |= (1 << bit_pos)  # 设置方向掩码
                    self.data_mask &= ~(1 << bit_pos)  # 清除数据掩码中的该位
                    
                    result = self.ch341.CH341SetOutput(
                        self.device_index,
                        self.enable_mask,
                        self.dir_mask,
                        self.data_mask
                    )
                    return result != 0
                else:
                    # 设置为输入模式
                    enable_mask = 0x2 # 0x2表示仅设置P8-P15引脚的方向
                    self.dir_mask &= ~(1 << bit_pos)  # 设置方向掩码
                    data_mask = 0  # 输入模式不需要设置数据掩码
                    
                    result = self.ch341.CH341SetOutput(
                        self.device_index,
                        self.enable_mask,
                        self.dir_mask,
                        data_mask
                    )
                    return result != 0
            
            except Exception as e:
                logger.error(f"设置GPIO引脚方向失败: {e}")
                return False
        
        logger.warning(f"引脚 {pin_id} 不支持方向设置")
        return False
    
    def set_pin_level(self, pin_id: PinID, level: PinLevel) -> bool:
        """设置引脚电平"""
        if not self.dll_loaded or not self.is_opened:
            logger.error("设备未打开或DLL未加载")
            return False
        
        if not self.is_pin_supported(pin_id):
            logger.error(f"不支持的引脚: {pin_id}")
            return False
        
        # 对于数据引脚，使用CH341SetOutput
        bit_pos = self._pin_id_to_bit(pin_id)
        if bit_pos is not None:
            try:
                enable_mask = 0x4 # 0x4表示仅设置D7-D0引脚的电平
                dir_mask = 0 # 无需配置方向
                if level == PinLevel.HIGH:
                    self.data_mask |= (1 << bit_pos)
                else:
                    self.data_mask &= ~(1 << bit_pos)
                
                result = self.ch341.CH341SetOutput(
                    self.device_index,
                    enable_mask,
                    dir_mask,
                    self.data_mask
                )
                
                if result != 0:
                    self._pin_capabilities[pin_id].current_level = level
                    return True
                else:
                    return False
            except Exception as e:
                logger.error(f"设置引脚电平失败: {e}")
                return False
        
        # 兼容模式
        bit_pos = self._gpio_pin_to_bit(pin_id)
        if bit_pos is not None:
            try:
                enable_mask = 0x1 # 0x1表示同时设置P8-P15引脚的电平
                dir_mask = 0 # 无需配置方向
                if level == PinLevel.HIGH:
                    self.data_mask |= (1 << bit_pos)
                else:
                    self.data_mask &= ~(1 << bit_pos)
                
                result = self.ch341.CH341SetOutput(
                    self.device_index,
                    enable_mask,
                    dir_mask,
                    self.data_mask
                )
                
                if result != 0:
                    self._pin_capabilities[pin_id].current_level = level
                    return True
                else:
                    return False
            
            except Exception as e:
                logger.error(f"设置GPIO引脚电平失败: {e}")
                return False
        
        logger.warning(f"引脚 {pin_id} 不支持电平设置")
        return False
    
    def get_pin_level(self, pin_id: PinID) -> Optional[PinLevel]:
        """读取引脚电平"""
        if not self.dll_loaded or not self.is_opened:
            logger.error("设备未打开或DLL未加载")
            return None
        
        if not self.is_pin_supported(pin_id):
            logger.error(f"不支持的引脚: {pin_id}")
            return None

        try:
            # 对于数据引脚/兼容引脚，使用CH341GetInput
            bit_pos = self._gpio_pin_to_bit(pin_id) if self._gpio_pin_to_bit(pin_id) is not None else self._pin_id_to_bit(pin_id)
            if bit_pos is not None:
                status = c_ulong()
                self.ch341.CH341GetInput(self.device_index, byref(status))
                if status.value != 0xFFFFFFFF:  # 有效状态
                    level = PinLevel.HIGH if (status.value & (1 << bit_pos)) != 0 else PinLevel.LOW
                    self._pin_capabilities[pin_id].current_level = level
                    return level
                else:
                    return None

            # 对于状态引脚，使用CH341GetStatus
            status_bit = self._pin_id_to_status_bit(pin_id)
            if status_bit is not None:
                status = c_ulong()
                self.ch341.CH341GetStatus(self.device_index, byref(status))
                if status.value != 0xFFFFFFFF:  # 有效状态
                    level = PinLevel.HIGH if (status.value & (1 << status_bit)) != 0 else PinLevel.LOW
                    self._pin_capabilities[pin_id].current_level = level
                    return level
                else:
                    return None
            
        except Exception as e:
            logger.error(f"读取引脚电平失败: {e}")
            return None
        
        logger.warning(f"引脚 {pin_id} 不支持电平读取")
        return None
    
    def set_multiple_pins(self, pin_levels: Dict[PinID, PinLevel]) -> bool:
        """同时设置多个引脚电平"""
        if not self.dll_loaded or not self.is_opened:
            logger.error("设备未打开或DLL未加载")
            return False
        
        try:
            flag = 0
            
            for pin_id, level in pin_levels.items():
                bit_pos = self._pin_id_to_bit(pin_id)
                if bit_pos is not None:
                    flag = 1
                    self.dir_mask |= (1 << bit_pos)  # 设为输出
                    if level == PinLevel.HIGH:
                        self.data_mask |= (1 << bit_pos)
            
            if flag != 0:
                result = self.ch341.CH341SetOutput(
                    self.device_index,
                    self.enable_mask,
                    self.dir_mask,
                    self.data_mask
                )
                
                if result != 0:
                    # 更新缓存的电平状态
                    for pin_id, level in pin_levels.items():
                        if pin_id in self._pin_capabilities:
                            self._pin_capabilities[pin_id].current_level = level
                    return True
                else:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"设置多个引脚失败: {e}")
            return False
    
    def get_multiple_pins(self, pin_ids: List[PinID]) -> Dict[PinID, PinLevel]:
        """同时读取多个引脚电平"""
        result = {}
        
        if not self.dll_loaded or not self.is_opened:
            logger.error("设备未打开或DLL未加载")
            return result
        
        try:
            # 读取输入状态
            status = c_ulong()
            self.ch341.CH341GetInput(self.device_index, byref(status))
            input_status = status.value
            self.ch341.CH341GetStatus(self.device_index, byref(status))
            status_register = status.value
            
            for pin_id in pin_ids:
                if not self.is_pin_supported(pin_id):
                    continue
                
                # 检查是否为数据引脚/兼容引脚
                bit_pos = self._gpio_pin_to_bit(pin_id) if self._gpio_pin_to_bit(pin_id) is not None else self._pin_id_to_bit(pin_id)
                if bit_pos is not None and input_status != 0xFFFFFFFF:
                    level = PinLevel.HIGH if (input_status & (1 << bit_pos)) != 0 else PinLevel.LOW
                    result[pin_id] = level
                    self._pin_capabilities[pin_id].current_level = level
                    continue
                
                # 检查是否为状态引脚
                status_bit = self._pin_id_to_status_bit(pin_id)
                if status_bit is not None and status_register != 0xFFFFFFFF:
                    level = PinLevel.HIGH if (status_register & (1 << status_bit)) != 0 else PinLevel.LOW
                    result[pin_id] = level
                    self._pin_capabilities[pin_id].current_level = level
            
        except Exception as e:
            logger.error(f"读取多个引脚失败: {e}")
        
        return result
    
    
    def _find_device(self) -> bool:
        """查找CH341设备"""
        try:
            # 尝试通过设备名称检测
            device_name = self.ch341.CH341GetDeviceName(self.device_index)
            if device_name:
                device_name_str = string_at(device_name).decode('utf-8', errors='ignore')
                logger.info(f"找到设备 {self.device_index}: {device_name_str}")
                return True
            else:
                logger.warning(f"设备 {self.device_index} 不存在")
                return False
        except Exception as e:
            logger.error(f"查找设备时出错: {e}")
            return False
    
    def open(self) -> bool:
        """打开CH341设备"""
        if not self.dll_loaded:
            logger.error("DLL未加载")
            return False
        
        try:
            # 尝试打开设备
            result = self.ch341.CH341OpenDevice(self.device_index)
            if result != 0:
                self.is_opened = True
                logger.info(f"成功打开设备 {self.device_index}")
                return True
            else:
                logger.error(f"无法打开设备 {self.device_index}")
                return False
        except Exception as e:
            logger.error(f"打开设备时出错: {e}")
            return False
    
    def close(self) -> None:
        """关闭CH341设备"""
        if self.dll_loaded and self.is_opened:
            try:
                self.ch341.CH341CloseDevice(self.device_index)
                self.is_opened = False
                logger.info(f"设备 {self.device_index} 已关闭")
            except Exception as e:
                logger.error(f"关闭设备时出错: {e}")

    def i2c_scan(self, start_addr: int = 0x08, end_addr: int = 0x77) -> List[int]:
        """扫描I2C总线"""
        if not self.is_opened:
            logger.error("设备未打开")
            return []
            
        found_devices = []
        
        try:
            logger.info(f"扫描I2C总线 (0x{start_addr:02X} - 0x{end_addr:02X})")
            
            for addr in range(start_addr, end_addr + 1):
                try:
                    # 尝试读取一个字节
                    data_byte = c_ubyte()
                    if self.ch341.CH341ReadI2C(self.device_index, addr, 0, byref(data_byte)):
                        found_devices.append(addr)
                        logger.debug(f"发现设备: 0x{addr:02X}")
                    
                    # 添加小延时避免总线过于繁忙
                    time.sleep(0.01)
                    
                except Exception:
                    pass
                    
            logger.info(f"扫描完成，发现 {len(found_devices)} 个设备")
            return found_devices
            
        except Exception as e:
            logger.error(f"扫描I2C总线时出错: {e}")
            return []
    
    def i2c_read_byte(self, device_addr: int, reg_addr: int) -> Optional[int]:
        """读取一个字节"""
        if not self.is_opened:
            logger.error("设备未打开")
            return None
            
        try:
            data_byte = c_ubyte()
            if self.ch341.CH341ReadI2C(self.device_index, device_addr, reg_addr, byref(data_byte)):
                return data_byte.value
            else:
                logger.warning(f"读取失败: 设备0x{device_addr:02X}, 寄存器0x{reg_addr:02X}")
                return None
        except Exception as e:
            logger.error(f"读取字节时出错: {e}")
            return None
    
    def i2c_write_byte(self, device_addr: int, reg_addr: int, data: int) -> bool:
        """写入一个字节"""
        if not self.is_opened:
            logger.error("设备未打开")
            return False
            
        try:
            result = self.ch341.CH341WriteI2C(self.device_index, device_addr, reg_addr, data)
            if not result:
                logger.warning(f"写入失败: 设备0x{device_addr:02X}, 寄存器0x{reg_addr:02X}, 数据0x{data:02X}")
            return bool(result)
        except Exception as e:
            logger.error(f"写入字节时出错: {e}")
            return False
    
    def i2c_read_block(self, device_addr: int, reg_addr: int, length: int) -> Optional[bytes]:
        """读取多个字节 - 使用CH341StreamI2C"""
        if not self.is_opened:
            logger.error("设备未打开")
            return None
            
        try:
            # 构造写缓冲区 (设备地址和寄存器地址)
            write_buf = (c_ubyte * 2)()
            write_buf[0] = (device_addr << 1) | 0  # 写地址
            write_buf[1] = reg_addr  # 寄存器地址
            
            # 构造读缓冲区
            read_buf = (c_ubyte * length)()
            
            # 执行I2C流传输
            if self.ch341.CH341StreamI2C(self.device_index, 2, write_buf, length, read_buf):
                return bytes([read_buf[i] for i in range(length)])
            else:
                logger.warning(f"读取块失败: 设备0x{device_addr:02X}, 寄存器0x{reg_addr:02X}, 长度{length}")
                return None
                
        except Exception as e:
            logger.error(f"读取块时出错: {e}")
            return None
    
    def i2c_write_block(self, device_addr: int, reg_addr: int, data: bytes) -> bool:
        """写入多个字节 - 使用CH341StreamI2C"""
        if not self.is_opened:
            logger.error("设备未打开")
            return False
            
        try:
            # 构造写缓冲区 (设备地址 + 寄存器地址 + 数据)
            write_len = 2 + len(data)
            write_buf = (c_ubyte * write_len)()
            
            write_buf[0] = (device_addr << 1) | 0  # 写地址
            write_buf[1] = reg_addr  # 寄存器地址
            
            for i, byte_val in enumerate(data):
                write_buf[2 + i] = byte_val
            
            # 执行I2C流传输
            result = self.ch341.CH341StreamI2C(self.device_index, write_len, write_buf, 0, None)
            if not result:
                logger.warning(f"写入块失败: 设备0x{device_addr:02X}, 寄存器0x{reg_addr:02X}")
            return bool(result)
            
        except Exception as e:
            logger.error(f"写入块时出错: {e}")
            return False
    
    def set_speed(self, speed_mode: int) -> bool:
        """设置I2C速度
        
        Args:
            speed_mode: 0=20KHz, 1=100KHz, 2=400KHz, 3=750KHz
        """
        if not self.is_opened:
            logger.error("设备未打开")
            return False
            
        try:
            speed_names = {
                0: "20KHz (慢速)",
                1: "100KHz (标准)", 
                2: "400KHz (快速)",
                3: "750KHz (高速)"
            }
            
            if self.ch341.CH341SetStream(self.device_index, speed_mode):
                logger.info(f"I2C速度设置成功: {speed_names.get(speed_mode, f'模式{speed_mode}')}")
                return True
            else:
                logger.error(f"I2C速度设置失败: {speed_names.get(speed_mode, f'模式{speed_mode}')}")
                return False
        except Exception as e:
            logger.error(f"设置I2C速度时出错: {e}")
            return False
