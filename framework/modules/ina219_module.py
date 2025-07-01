"""
INA219 电流监测模组实现

基于Texas Instruments INA219单通道电流/电压/功率监测芯片的模组实现
"""

import os
import sys
import time
from typing import List, Optional, Union, Dict, Any

# 相对导入父级模块
from ..interfaces import ModuleInterface, AdapterInterface
import logging

logger = logging.getLogger(__name__)

# INA219寄存器地址定义
_DEFAULT_ADDRESS = 0x40

# 寄存器定义
INA219_REG_CONFIG = 0x00
INA219_REG_SHUNT_VOLTAGE = 0x01
INA219_REG_BUS_VOLTAGE = 0x02
INA219_REG_POWER = 0x03
INA219_REG_CURRENT = 0x04
INA219_REG_CALIBRATION = 0x05

# 配置位定义
INA219_CONFIG_RESET = 0x8000
INA219_CONFIG_BVOLTAGERANGE_MASK = 0x2000
INA219_CONFIG_BVOLTAGERANGE_16V = 0x0000
INA219_CONFIG_BVOLTAGERANGE_32V = 0x2000

INA219_CONFIG_GAIN_MASK = 0x1800
INA219_CONFIG_GAIN_1_40MV = 0x0000
INA219_CONFIG_GAIN_2_80MV = 0x0800
INA219_CONFIG_GAIN_4_160MV = 0x1000
INA219_CONFIG_GAIN_8_320MV = 0x1800

INA219_CONFIG_BADCRES_MASK = 0x0780
INA219_CONFIG_BADCRES_9BIT = 0x0000
INA219_CONFIG_BADCRES_10BIT = 0x0080
INA219_CONFIG_BADCRES_11BIT = 0x0100
INA219_CONFIG_BADCRES_12BIT = 0x0180
INA219_CONFIG_BADCRES_12BIT_2S_1060US = 0x0480
INA219_CONFIG_BADCRES_12BIT_4S_2130US = 0x0500
INA219_CONFIG_BADCRES_12BIT_8S_4260US = 0x0580
INA219_CONFIG_BADCRES_12BIT_16S_8510US = 0x0600
INA219_CONFIG_BADCRES_12BIT_32S_17MS = 0x0680
INA219_CONFIG_BADCRES_12BIT_64S_34MS = 0x0700
INA219_CONFIG_BADCRES_12BIT_128S_69MS = 0x0780

INA219_CONFIG_SADCRES_MASK = 0x0078
INA219_CONFIG_SADCRES_9BIT_1S_84US = 0x0000
INA219_CONFIG_SADCRES_10BIT_1S_148US = 0x0008
INA219_CONFIG_SADCRES_11BIT_1S_276US = 0x0010
INA219_CONFIG_SADCRES_12BIT_1S_532US = 0x0018
INA219_CONFIG_SADCRES_12BIT_2S_1060US = 0x0048
INA219_CONFIG_SADCRES_12BIT_4S_2130US = 0x0050
INA219_CONFIG_SADCRES_12BIT_8S_4260US = 0x0058
INA219_CONFIG_SADCRES_12BIT_16S_8510US = 0x0060
INA219_CONFIG_SADCRES_12BIT_32S_17MS = 0x0068
INA219_CONFIG_SADCRES_12BIT_64S_34MS = 0x0070
INA219_CONFIG_SADCRES_12BIT_128S_69MS = 0x0078

INA219_CONFIG_MODE_MASK = 0x0007
INA219_CONFIG_MODE_POWERDOWN = 0x0000
INA219_CONFIG_MODE_SVOLT_TRIGGERED = 0x0001
INA219_CONFIG_MODE_BVOLT_TRIGGERED = 0x0002
INA219_CONFIG_MODE_SANDBVOLT_TRIGGERED = 0x0003
INA219_CONFIG_MODE_ADCOFF = 0x0004
INA219_CONFIG_MODE_SVOLT_CONTINUOUS = 0x0005
INA219_CONFIG_MODE_BVOLT_CONTINUOUS = 0x0006
INA219_CONFIG_MODE_SANDBVOLT_CONTINUOUS = 0x0007


class INA219Module(ModuleInterface):
    """INA219单通道电流监测模组"""
    
    def __init__(self, adapter: AdapterInterface, device_addr: int = _DEFAULT_ADDRESS):
        super().__init__(adapter, device_addr)
        self.name = "INA219 Single Current Monitor"
        
        # 默认配置参数
        self.shunt_resistor = 0.1  # 分流电阻值 (欧姆) - 100mΩ
        self.max_expected_current = 0.1  # 最大期望电流 (A)
        self.bus_voltage_range = 32  # 总线电压范围 (V) - 16V或32V
        
        # 校准参数
        self.current_lsb = None
        self.power_lsb = None
        self.cal_value = None
        
        # 默认配置寄存器
        self.default_config = (
            INA219_CONFIG_BVOLTAGERANGE_32V |  # 32V总线电压范围
            INA219_CONFIG_GAIN_8_320MV |      # ±320mV增益 (适用于0.1Ω分流电阻)
            INA219_CONFIG_BADCRES_12BIT |     # 12位总线ADC分辨率
            INA219_CONFIG_SADCRES_12BIT_1S_532US |  # 12位分流ADC分辨率
            INA219_CONFIG_MODE_SANDBVOLT_CONTINUOUS  # 连续转换模式
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
    
    def _calculate_calibration(self):
        """计算校准值"""
        # 计算电流LSB (每位代表的电流值)
        # 推荐值为最大期望电流的1/32768，但要确保是合理的值
        min_lsb = self.max_expected_current / 32767
        self.current_lsb = min_lsb
        
        # 调整LSB到合理的值 (通常为10的倍数)

        if self.current_lsb < 0.0001:  # 100µA
            self.current_lsb = 0.0001
        elif self.current_lsb < 0.001:  # 1mA
            self.current_lsb = 0.001
        elif self.current_lsb < 0.01:   # 10mA
            self.current_lsb = 0.01
        elif self.current_lsb < 0.1:    # 100mA
            self.current_lsb = 0.1
        
        # 计算校准寄存器值
        # Cal = trunc(0.04096 / (Current_LSB * R_shunt))
        self.cal_value = int(0.04096 / (self.current_lsb * self.shunt_resistor))
        
        # 功率LSB = 20 * 电流LSB
        self.power_lsb = 20 * self.current_lsb
        
        logger.info(f"校准参数计算完成:")
        logger.info(f"  电流LSB: {self.current_lsb*1000:.3f}mA/bit")
        logger.info(f"  功率LSB: {self.power_lsb*1000:.3f}mW/bit")
        logger.info(f"  校准值: {self.cal_value}")
    
    def initialize(self) -> bool:
        """初始化INA219模组"""
        try:
            logger.info("初始化INA219模组...")
            
            # 复位设备
            if not self._write_register(INA219_REG_CONFIG, INA219_CONFIG_RESET):
                logger.error("复位设备失败")
                return False
            
            # 等待复位完成
            time.sleep(0.1)
            
            # 计算校准参数
            self._calculate_calibration()
            
            # 写入校准寄存器
            if not self._write_register(INA219_REG_CALIBRATION, self.cal_value):
                logger.error("写入校准寄存器失败")
                return False
            
            # 写入配置寄存器
            if not self._write_register(INA219_REG_CONFIG, self.default_config):
                logger.error("写入配置寄存器失败")
                return False
            
            # 验证配置
            config_read = self._read_register(INA219_REG_CONFIG)
            if config_read != self.default_config:
                logger.warning(f"配置验证不匹配: 期望0x{self.default_config:04X}, 实际0x{config_read:04X}")
            
            self.is_initialized = True
            logger.info("INA219模组初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"初始化INA219时出错: {e}")
            return False
    
    def _read_shunt_voltage(self) -> Optional[float]:
        """读取分流电压 (mV)"""
        raw_value = self._read_register(INA219_REG_SHUNT_VOLTAGE)
        if raw_value is None:
            return None
        
        # 转换为有符号整数
        if raw_value & 0x8000:
            raw_value -= 0x10000
        
        # 分流电压精度为10µV/LSB
        shunt_voltage_mv = raw_value * 0.01
        return shunt_voltage_mv
    
    def _read_bus_voltage(self) -> Optional[float]:
        """读取总线电压 (V)"""
        raw_value = self._read_register(INA219_REG_BUS_VOLTAGE)
        if raw_value is None:
            return None
        
        # 检查转换准备标志 (CNVR bit)
        if not (raw_value & 0x0002):
            logger.warning("转换未完成")
        
        # 检查溢出标志 (OVF bit)
        if raw_value & 0x0001:
            logger.warning("数学溢出")
        
        # 总线电压精度为4mV/LSB，右移3位丢弃标志位
        bus_voltage_v = (raw_value >> 3) * 0.004
        return bus_voltage_v
    
    def _read_power_raw(self) -> Optional[float]:
        """读取功率寄存器原始值 (W)"""
        if not self.is_initialized or self.power_lsb is None:
            logger.error("模组未初始化或校准参数缺失")
            return None
        
        raw_value = self._read_register(INA219_REG_POWER)
        if raw_value is None:
            return None
        
        # 功率值 = 原始值 * 功率LSB
        power_w = raw_value * self.power_lsb
        return power_w
    
    def _read_current_raw(self) -> Optional[float]:
        """读取电流寄存器原始值 (A)"""
        if not self.is_initialized or self.current_lsb is None:
            logger.error("模组未初始化或校准参数缺失")
            return None
        
        raw_value = self._read_register(INA219_REG_CURRENT)
        if raw_value is None:
            return None
        
        # 转换为有符号整数
        if raw_value & 0x8000:
            raw_value -= 0x10000
        
        # 电流值 = 原始值 * 电流LSB
        current_a = raw_value * self.current_lsb
        return current_a
    
    def read_current(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取电流值 (A)
        
        Args:
            channel: 通道号(INA219只有一个通道，此参数被忽略)
        """
        if not self.is_initialized:
            logger.error("模组未初始化")
            return None
        
        # INA219只有一个通道
        if channel is not None and channel != 1:
            logger.warning(f"INA219只有通道1，忽略通道{channel}请求")
        
        # 可以从电流寄存器直接读取，也可以通过分流电压计算
        current = self._read_current_raw()
        if current is not None:
            return current
        
        # 备选方法：通过分流电压计算
        shunt_voltage = self._read_shunt_voltage()
        if shunt_voltage is None:
            return None
        
        # 计算电流: I = V_shunt / R_shunt
        current_a = (shunt_voltage / 1000.0) / self.shunt_resistor
        return current_a
    
    def read_voltage(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取电压值 (V)
        
        Args:
            channel: 通道号(INA219只有一个通道，此参数被忽略)
        """
        if not self.is_initialized:
            logger.error("模组未初始化")
            return None
        
        # INA219只有一个通道
        if channel is not None and channel != 1:
            logger.warning(f"INA219只有通道1，忽略通道{channel}请求")
        
        return self._read_bus_voltage()
    
    def read_power(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取功率值 (W)
        
        Args:
            channel: 通道号(INA219只有一个通道，此参数被忽略)
        """
        if not self.is_initialized:
            logger.error("模组未初始化")
            return None
        
        # INA219只有一个通道
        if channel is not None and channel != 1:
            logger.warning(f"INA219只有通道1，忽略通道{channel}请求")
        
        # 可以从功率寄存器直接读取，也可以通过电流和电压计算
        power = self._read_power_raw()
        if power is not None:
            return power
        
        # 备选方法：通过电流和电压计算
        current = self.read_current()
        voltage = self.read_voltage()
        
        if current is None or voltage is None:
            return None
        
        # 计算功率: P = V * I
        power_w = voltage * current
        return power_w
    
    def configure(self, **kwargs) -> bool:
        """配置模组参数"""
        try:
            recalibrate = False
            
            # 设置分流电阻
            if "shunt_resistor" in kwargs:
                resistor = kwargs["shunt_resistor"]
                if isinstance(resistor, (int, float)) and resistor > 0:
                    self.shunt_resistor = float(resistor)
                    logger.info(f"设置分流电阻: {self.shunt_resistor}Ω")
                    recalibrate = True
                else:
                    logger.error("分流电阻参数格式错误")
                    return False
            
            # 设置最大期望电流
            if "max_expected_current" in kwargs:
                current = kwargs["max_expected_current"]
                if isinstance(current, (int, float)) and current > 0:
                    self.max_expected_current = float(current)
                    logger.info(f"设置最大期望电流: {self.max_expected_current}A")
                    recalibrate = True
                else:
                    logger.error("最大期望电流参数格式错误")
                    return False
            
            # 设置总线电压范围
            if "bus_voltage_range" in kwargs:
                voltage_range = kwargs["bus_voltage_range"]
                if voltage_range in [16, 32]:
                    self.bus_voltage_range = voltage_range
                    logger.info(f"设置总线电压范围: {self.bus_voltage_range}V")
                    
                    # 更新配置寄存器
                    if voltage_range == 16:
                        self.default_config = (self.default_config & ~INA219_CONFIG_BVOLTAGERANGE_MASK) | INA219_CONFIG_BVOLTAGERANGE_16V
                    else:
                        self.default_config = (self.default_config & ~INA219_CONFIG_BVOLTAGERANGE_MASK) | INA219_CONFIG_BVOLTAGERANGE_32V
                    
                    if self.is_initialized:
                        if not self._write_register(INA219_REG_CONFIG, self.default_config):
                            logger.error("写入配置失败")
                            return False
                else:
                    logger.error("总线电压范围必须是16或32")
                    return False
            
            # 设置配置寄存器
            if "config" in kwargs:
                config = kwargs["config"]
                if isinstance(config, int):
                    self.default_config = config
                    if self.is_initialized:
                        if not self._write_register(INA219_REG_CONFIG, config):
                            logger.error("写入配置失败")
                            return False
                    logger.info(f"设置配置寄存器: 0x{config:04X}")
                else:
                    logger.error("配置寄存器参数格式错误")
                    return False
            
            # 如果需要重新校准
            if recalibrate and self.is_initialized:
                self._calculate_calibration()
                if not self._write_register(INA219_REG_CALIBRATION, self.cal_value):
                    logger.error("重新校准失败")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"配置模组时出错: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """获取模组详细信息"""
        base_info = super().get_info()
        
        # 添加INA219特有信息
        extra_info = {
            "channels": 1,
            "shunt_resistor": self.shunt_resistor,
            "max_expected_current": self.max_expected_current,
            "bus_voltage_range": f"{self.bus_voltage_range}V",
            "measurement_range": {
                "shunt_voltage": "±320 mV",
                "bus_voltage": f"0-{self.bus_voltage_range} V",
                "current": f"±{320 / (self.shunt_resistor * 1000):.2f} A"
            }
        }
        
        if self.is_initialized:
            try:
                # 读取器件信息
                config = self._read_register(INA219_REG_CONFIG)
                cal = self._read_register(INA219_REG_CALIBRATION)
                
                extra_info.update({
                    "current_config": f"0x{config:04X}" if config else "Unknown",
                    "calibration_value": cal if cal else "Unknown",
                    "current_lsb": f"{self.current_lsb*1000:.3f} mA/bit" if self.current_lsb else "Unknown",
                    "power_lsb": f"{self.power_lsb*1000:.3f} mW/bit" if self.power_lsb else "Unknown"
                })
            except Exception:
                pass
        
        base_info.update(extra_info)
        return base_info
