"""
INA3221 电流监测模组实现

基于Texas Instruments INA3221三通道电流/电压监测芯片的模组实现
"""

import os
import sys
import time
from typing import List, Optional, Union, Dict, Any

# 相对导入父级模块
from ..interfaces import ModuleInterface, AdapterInterface
import logging

logger = logging.getLogger(__name__)

# INA3221寄存器地址定义
_DEFAULT_ADDRESS = 0x40

# 寄存器定义
C_REG_CONFIG = 0x00
C_REG_CH1_SHUNT_VOLTAGE = 0x01
C_REG_CH1_BUS_VOLTAGE = 0x02
C_REG_CH2_SHUNT_VOLTAGE = 0x03
C_REG_CH2_BUS_VOLTAGE = 0x04
C_REG_CH3_SHUNT_VOLTAGE = 0x05
C_REG_CH3_BUS_VOLTAGE = 0x06
C_REG_CH1_CRITICAL_ALERT_LIMIT = 0x07
C_REG_CH1_WARNING_ALERT_LIMIT = 0x08
C_REG_CH2_CRITICAL_ALERT_LIMIT = 0x09
C_REG_CH2_WARNING_ALERT_LIMIT = 0x0A
C_REG_CH3_CRITICAL_ALERT_LIMIT = 0x0B
C_REG_CH3_WARNING_ALERT_LIMIT = 0x0C
C_REG_SHUNT_VOLTAGE_SUM = 0x0D
C_REG_SHUNT_VOLTAGE_SUM_LIMIT = 0x0E
C_REG_MASK_ENABLE = 0x0F
C_REG_POWER_VALID_UPPER_LIMIT = 0x10
C_REG_POWER_VALID_LOWER_LIMIT = 0x11
C_REG_MANUFACTURER_ID = 0xFE
C_REG_DIE_ID = 0xFF

# 配置位定义
C_RESET = 0x8000
C_ENABLE_CH1 = 0x4000
C_ENABLE_CH2 = 0x2000
C_ENABLE_CH3 = 0x1000
C_AVG_1 = 0x0000
C_AVG_4 = 0x0200
C_AVG_16 = 0x0400
C_AVG_64 = 0x0600
C_AVG_128 = 0x0800
C_AVG_256 = 0x0A00
C_AVG_512 = 0x0C00
C_AVG_1024 = 0x0E00
C_VBUS_CT_140_us = 0x0000
C_VBUS_CT_204_us = 0x0040
C_VBUS_CT_332_us = 0x0080
C_VBUS_CT_588_us = 0x00C0
C_VBUS_CT_1100_us = 0x0100
C_VBUS_CT_2116_us = 0x0140
C_VBUS_CT_4156_us = 0x0180
C_VBUS_CT_8244_us = 0x01C0
C_VSH_CT_140_us = 0x0000
C_VSH_CT_204_us = 0x0008
C_VSH_CT_332_us = 0x0010
C_VSH_CT_588_us = 0x0018
C_VSH_CT_1100_us = 0x0020
C_VSH_CT_2116_us = 0x0028
C_VSH_CT_4156_us = 0x0030
C_VSH_CT_8244_us = 0x0038
C_MODE_POWER_DOWN = 0x0000
C_MODE_SHUNT_VOLTAGE_TRIGGERED = 0x0001
C_MODE_BUS_VOLTAGE_TRIGGERED = 0x0002
C_MODE_SHUNT_AND_BUS_TRIGGERED = 0x0003
C_MODE_POWER_DOWN2 = 0x0004
C_MODE_SHUNT_VOLTAGE_CONTINUOUS = 0x0005
C_MODE_BUS_VOLTAGE_CONTINUOUS = 0x0006
C_MODE_SHUNT_AND_BUS_CONTINUOUS = 0x0007


class INA3221Module(ModuleInterface):
    """INA3221三通道电流监测模组"""
    
    def __init__(self, adapter: AdapterInterface, device_addr: int = _DEFAULT_ADDRESS):
        super().__init__(adapter, device_addr)
        self.name = "INA3221 Triple Current Monitor"
        
        # 默认分流电阻值 (欧姆)
        self.shunt_resistors = [0.1, 0.1, 0.1]  # 每通道100mΩ
        
        # 默认配置
        self.default_config = (
            C_ENABLE_CH1 | C_ENABLE_CH2 | C_ENABLE_CH3 |  # 启用所有通道
            C_AVG_1 |  # 平均1次采样
            C_VBUS_CT_1100_us |  # 总线电压转换时间
            C_VSH_CT_1100_us |  # 分流电压转换时间
            C_MODE_SHUNT_AND_BUS_CONTINUOUS  # 连续模式
        )
        
    def _read_register(self, reg_addr: int) -> Optional[int]:
        """读取16位寄存器"""
        try:
            data = self.adapter.i2c_read_block(self.device_addr, reg_addr, 2)
            if data:
                # 大端序转换
                return (data[0] << 8) | data[1]
            return None
        except Exception as e:
            logger.error(f"读取寄存器0x{reg_addr:02X}时出错: {e}")
            return None
    
    def _write_register(self, reg_addr: int, value: int) -> bool:
        """写入16位寄存器"""
        try:
            # 大端序转换
            data = bytes([(value >> 8) & 0xFF, value & 0xFF])
            return self.adapter.i2c_write_block(self.device_addr, reg_addr, data)
        except Exception as e:
            logger.error(f"写入寄存器0x{reg_addr:02X}时出错: {e}")
            return False
    
    def initialize(self) -> bool:
        """初始化INA3221模组"""
        try:
            logger.info("初始化INA3221模组...")
            
            # 检查制造商ID
            manufacturer_id = self._read_register(C_REG_MANUFACTURER_ID)
            if manufacturer_id != 0x5449:  # "TI"的ASCII码
                logger.error(f"制造商ID不匹配: 期望0x5449, 实际0x{manufacturer_id:04X}")
                return False
            
            # 检查器件ID
            die_id = self._read_register(C_REG_DIE_ID)
            if die_id != 0x3220:
                logger.warning(f"器件ID可能不匹配: 期望0x3220, 实际0x{die_id:04X}")
            
            # 复位设备
            if not self._write_register(C_REG_CONFIG, C_RESET):
                logger.error("复位设备失败")
                return False
            
            # 等待复位完成
            time.sleep(0.1)
            
            # 写入配置
            if not self._write_register(C_REG_CONFIG, self.default_config):
                logger.error("写入配置失败")
                return False
            
            # 验证配置
            config_read = self._read_register(C_REG_CONFIG)
            if config_read != self.default_config:
                logger.warning(f"配置验证不匹配: 期望0x{self.default_config:04X}, 实际0x{config_read:04X}")
            
            self.is_initialized = True
            logger.info("INA3221模组初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"初始化INA3221时出错: {e}")
            return False
    
    def _read_shunt_voltage(self, channel: int) -> Optional[float]:
        """读取分流电压 (mV)"""
        if channel < 1 or channel > 3:
            logger.error(f"无效通道号: {channel}")
            return None
            
        reg_map = {
            1: C_REG_CH1_SHUNT_VOLTAGE,
            2: C_REG_CH2_SHUNT_VOLTAGE,
            3: C_REG_CH3_SHUNT_VOLTAGE
        }
        
        raw_value = self._read_register(reg_map[channel])
        if raw_value is None:
            return None
        
        # 转换为有符号整数
        if raw_value & 0x8000:
            raw_value -= 0x10000
        
        # 分流电压精度为40µV/LSB，最低3位为0
        shunt_voltage_mv = (raw_value >> 3) * 0.04
        return shunt_voltage_mv
    
    def _read_bus_voltage(self, channel: int) -> Optional[float]:
        """读取总线电压 (V)"""
        if channel < 1 or channel > 3:
            logger.error(f"无效通道号: {channel}")
            return None
            
        reg_map = {
            1: C_REG_CH1_BUS_VOLTAGE,
            2: C_REG_CH2_BUS_VOLTAGE,
            3: C_REG_CH3_BUS_VOLTAGE
        }
        
        raw_value = self._read_register(reg_map[channel])
        if raw_value is None:
            return None
        
        # 总线电压精度为8mV/LSB，最低3位为标志位
        bus_voltage_v = (raw_value >> 3) * 0.008
        return bus_voltage_v
    
    def read_current(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取电流值 (A)"""
        if not self.is_initialized:
            logger.error("模组未初始化")
            return None
        
        if channel is not None:
            # 读取单通道
            shunt_voltage = self._read_shunt_voltage(channel)
            if shunt_voltage is None:
                return None
            
            # 计算电流: I = V_shunt / R_shunt
            current_a = (shunt_voltage / 1000.0) / self.shunt_resistors[channel - 1]
            return current_a
        else:
            # 读取所有通道
            currents = []
            for ch in range(1, 4):
                current = self.read_current(ch)
                currents.append(current if current is not None else 0.0)
            return currents
    
    def read_voltage(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取电压值 (V)"""
        if not self.is_initialized:
            logger.error("模组未初始化")
            return None
        
        if channel is not None:
            # 读取单通道
            return self._read_bus_voltage(channel)
        else:
            # 读取所有通道
            voltages = []
            for ch in range(1, 4):
                voltage = self.read_voltage(ch)
                voltages.append(voltage if voltage is not None else 0.0)
            return voltages
    
    def read_power(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取功率值 (W)"""
        if not self.is_initialized:
            logger.error("模组未初始化")
            return None
        
        if channel is not None:
            # 读取单通道
            current = self.read_current(channel)
            voltage = self.read_voltage(channel)
            
            if current is None or voltage is None:
                return None
            
            # 计算功率: P = V * I
            power_w = voltage * current
            return power_w
        else:
            # 读取所有通道
            powers = []
            for ch in range(1, 4):
                power = self.read_power(ch)
                powers.append(power if power is not None else 0.0)
            return powers
    
    def configure(self, **kwargs) -> bool:
        """配置模组参数"""
        try:
            # 设置分流电阻
            if "shunt_resistors" in kwargs:
                resistors = kwargs["shunt_resistors"]
                if isinstance(resistors, (list, tuple)) and len(resistors) == 3:
                    self.shunt_resistors = list(resistors)
                    logger.info(f"设置分流电阻: {self.shunt_resistors}")
                else:
                    logger.error("分流电阻参数格式错误")
                    return False
            
            # 设置配置寄存器
            if "config" in kwargs:
                config = kwargs["config"]
                if not self._write_register(C_REG_CONFIG, config):
                    logger.error("写入配置失败")
                    return False
                logger.info(f"设置配置寄存器: 0x{config:04X}")
            
            return True
            
        except Exception as e:
            logger.error(f"配置模组时出错: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """获取模组详细信息"""
        base_info = super().get_info()
        
        # 添加INA3221特有信息
        extra_info = {
            "channels": 3,
            "shunt_resistors": self.shunt_resistors,
            "measurement_range": {
                "shunt_voltage": "±163.8 mV",
                "bus_voltage": "0-26 V",
                "current": f"±{163.8 / (min(self.shunt_resistors) * 1000):.2f} A (per channel)"
            }
        }
        
        if self.is_initialized:
            try:
                # 读取器件信息
                manufacturer_id = self._read_register(C_REG_MANUFACTURER_ID)
                die_id = self._read_register(C_REG_DIE_ID)
                config = self._read_register(C_REG_CONFIG)
                
                extra_info.update({
                    "manufacturer_id": f"0x{manufacturer_id:04X}" if manufacturer_id else "Unknown",
                    "die_id": f"0x{die_id:04X}" if die_id else "Unknown",
                    "current_config": f"0x{config:04X}" if config else "Unknown"
                })
            except Exception:
                pass
        
        base_info.update(extra_info)
        return base_info
