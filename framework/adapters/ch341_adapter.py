"""
CH341 I2C适配器实现

基于CH341 USB转I2C芯片的适配器实现
"""

import os
import sys
import time
from ctypes import *
from typing import List, Optional

# 相对导入父级模块
from ..interfaces import AdapterInterface
import logging

logger = logging.getLogger(__name__)


class CH341Adapter(AdapterInterface):
    """CH341 I2C适配器"""
    
    def __init__(self, device_index: int = 0):
        super().__init__(device_index)
        self.name = "CH341 USB-I2C Adapter"
        self.ch341 = None
        self.device_handle = None
        
    def _load_dll(self) -> bool:
        """加载CH341 DLL库"""
        try:
            # 获取DLL路径 - 调整为新的目录结构
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            dll_path = os.path.join(script_dir, "device", "ch341", "Release")
            
            # 尝试加载64位DLL
            try:
                dll_file = os.path.join(dll_path, "CH341DLLA64.DLL")
                if os.path.exists(dll_file):
                    self.ch341 = windll.LoadLibrary(dll_file)
                    logger.info(f"成功加载64位DLL: {dll_file}")
                    return True
            except Exception as e:
                logger.warning(f"加载64位DLL失败: {e}")
            
            # 尝试加载32位DLL
            try:
                dll_file = os.path.join(dll_path, "CH341DLL.DLL")
                if os.path.exists(dll_file):
                    self.ch341 = windll.LoadLibrary(dll_file)
                    logger.info(f"成功加载32位DLL: {dll_file}")
                    return True
            except Exception as e:
                logger.warning(f"加载32位DLL失败: {e}")
                
            logger.error("无法加载CH341 DLL库")
            return False
            
        except Exception as e:
            logger.error(f"加载DLL时出错: {e}")
            return False
    
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
        if self.is_opened:
            logger.warning("设备已经打开")
            return True
            
        try:
            # 加载DLL
            if not self._load_dll():
                return False
                
            # 查找设备
            if not self._find_device():
                return False
                
            # 打开设备
            self.device_handle = self.ch341.CH341OpenDevice(self.device_index)
            if not self.device_handle:
                logger.error("无法打开CH341设备")
                return False
                
            # 设置I2C模式 (100KHz标准模式)
            if not self.ch341.CH341SetStream(self.device_index, 1):
                logger.error("无法设置I2C模式")
                self.ch341.CH341CloseDevice(self.device_index)
                return False
                
            self.is_opened = True
            logger.info(f"成功打开CH341设备 {self.device_index}")
            return True
            
        except Exception as e:
            logger.error(f"打开设备时出错: {e}")
            return False
    
    def close(self) -> None:
        """关闭CH341设备"""
        if not self.is_opened:
            return
            
        try:
            if self.ch341 and self.device_handle:
                self.ch341.CH341CloseDevice(self.device_index)
                logger.info(f"CH341设备 {self.device_index} 已关闭")
        except Exception as e:
            logger.error(f"关闭设备时出错: {e}")
        finally:
            self.is_opened = False
            self.device_handle = None
    
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
