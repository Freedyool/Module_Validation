

"""
INA228 电流监测模组实现

基于Texas Instruments INA228高精度单通道电流/电压/功率/能量监测芯片的模组实现
INA228 支持 20-bit ADC，具有更高的精度和更宽的测量范围
"""

import os
import sys
import time
from typing import List, Optional, Union, Dict, Any

# 相对导入父级模块
from ..interfaces import ModuleInterface, AdapterInterface
import logging

logger = logging.getLogger(__name__)

# INA228默认I2C地址
_DEFAULT_ADDRESS = 0x40

# INA228寄存器地址定义
INA228_REG_CONFIG = 0x00
INA228_REG_ADC_CONFIG = 0x01
INA228_REG_SHUNT_CAL = 0x02
INA228_REG_SHUNT_TEMPCO = 0x03
INA228_REG_VSHUNT = 0x04
INA228_REG_VBUS = 0x05
INA228_REG_DIETEMP = 0x06
INA228_REG_CURRENT = 0x07
INA228_REG_POWER = 0x08
INA228_REG_ENERGY = 0x09
INA228_REG_CHARGE = 0x0A
INA228_REG_DIAG_ALRT = 0x0B
INA228_REG_SOVL = 0x0C
INA228_REG_SUVL = 0x0D
INA228_REG_BOVL = 0x0E
INA228_REG_BUVL = 0x0F
INA228_REG_TEMP_LIMIT = 0x10
INA228_REG_PWR_LIMIT = 0x11
INA228_REG_MANUFACTURER_ID = 0x3E
INA228_REG_DEVICE_ID = 0x3F

# 配置寄存器位定义
INA228_CONFIG_RESET = 0x8000
INA228_CONFIG_RESETACC = 0x4000
INA228_CONFIG_CONVDLY_MASK = 0x3FC0
INA228_CONFIG_CONVDLY_0us = 0x0000
INA228_CONFIG_CONVDLY_2ms = 0x0080
INA228_CONFIG_CONVDLY_510ms = 0x3FC0
INA228_CONFIG_TEMP_COMP_MASK = 0x0020
INA228_CONFIG_TEMP_COMP_DISABLE = 0x0000
INA228_CONFIG_TEMP_COMP_ENABLE = 0x0020
INA228_CONFIG_ADC_RANGE_MASK = 0x0010
INA228_CONFIG_ADC_RANGE_0 = 0x0000  # ±163.84mV
INA228_CONFIG_ADC_RANGE_1 = 0x0010  # ± 40.96mV


# ADC配置寄存器位定义
INA228_ADC_CONFIG_MODE_MASK = 0xF000
INA228_ADC_CONFIG_MODE_SHUTDOWN = 0x0000
INA228_ADC_CONFIG_MODE_TRIG_BUS = 0x1000
INA228_ADC_CONFIG_MODE_TRIG_SHUNT = 0x2000
INA228_ADC_CONFIG_MODE_TRIG_BUS_SHUNT = 0x3000
INA228_ADC_CONFIG_MODE_TRIG_TEMP = 0x4000
INA228_ADC_CONFIG_MODE_TRIG_TEMP_BUS = 0x5000
INA228_ADC_CONFIG_MODE_TRIG_TEMP_SHUNT = 0x6000
INA228_ADC_CONFIG_MODE_TRIG_TEMP_BUS_SHUNT = 0x7000
INA228_ADC_CONFIG_MODE_SHUTDOWN2 = 0x8000
INA228_ADC_CONFIG_MODE_CONT_BUS = 0x9000
INA228_ADC_CONFIG_MODE_CONT_SHUNT = 0xA000
INA228_ADC_CONFIG_MODE_CONT_BUS_SHUNT = 0xB000
INA228_ADC_CONFIG_MODE_CONT_TEMP = 0xC000
INA228_ADC_CONFIG_MODE_CONT_TEMP_BUS = 0xD000
INA228_ADC_CONFIG_MODE_CONT_TEMP_SHUNT = 0xE000
INA228_ADC_CONFIG_MODE_CONT_ALL = 0xF000

# 总线电压转换时间
INA228_ADC_CONFIG_VBUSCT_MASK = 0x0E00
INA228_ADC_CONFIG_VBUSCT_50us = 0x0000
INA228_ADC_CONFIG_VBUSCT_84us = 0x0200
INA228_ADC_CONFIG_VBUSCT_150us = 0x0400
INA228_ADC_CONFIG_VBUSCT_280us = 0x0600
INA228_ADC_CONFIG_VBUSCT_540us = 0x0800
INA228_ADC_CONFIG_VBUSCT_1052us = 0x0A00
INA228_ADC_CONFIG_VBUSCT_2074us = 0x0C00
INA228_ADC_CONFIG_VBUSCT_4120us = 0x0E00

# 分流电压转换时间
INA228_ADC_CONFIG_VSHCT_MASK = 0x01C0
INA228_ADC_CONFIG_VSHCT_50us = 0x0000
INA228_ADC_CONFIG_VSHCT_84us = 0x0040
INA228_ADC_CONFIG_VSHCT_150us = 0x0080
INA228_ADC_CONFIG_VSHCT_280us = 0x00C0
INA228_ADC_CONFIG_VSHCT_540us = 0x0100
INA228_ADC_CONFIG_VSHCT_1052us = 0x0140
INA228_ADC_CONFIG_VSHCT_2074us = 0x0180
INA228_ADC_CONFIG_VSHCT_4120us = 0x01C0

# 温度转换时间
INA228_ADC_CONFIG_VTCT_MASK = 0x0038
INA228_ADC_CONFIG_VTCT_50us = 0x0000
INA228_ADC_CONFIG_VTCT_84us = 0x0008
INA228_ADC_CONFIG_VTCT_150us = 0x0010
INA228_ADC_CONFIG_VTCT_280us = 0x0018
INA228_ADC_CONFIG_VTCT_540us = 0x0020
INA228_ADC_CONFIG_VTCT_1052us = 0x0028
INA228_ADC_CONFIG_VTCT_2074us = 0x0030
INA228_ADC_CONFIG_VTCT_4120us = 0x0038

# 平均次数
INA228_ADC_CONFIG_AVG_MASK = 0x0007
INA228_ADC_CONFIG_AVG_1 = 0x0000
INA228_ADC_CONFIG_AVG_4 = 0x0001
INA228_ADC_CONFIG_AVG_16 = 0x0002
INA228_ADC_CONFIG_AVG_64 = 0x0003
INA228_ADC_CONFIG_AVG_128 = 0x0004
INA228_ADC_CONFIG_AVG_256 = 0x0005
INA228_ADC_CONFIG_AVG_512 = 0x0006
INA228_ADC_CONFIG_AVG_1024 = 0x0007


# 诊断和报警寄存器位定义
INA228_DIAG_ALRT_ALATCH_EN = 0x8000  # 报警锁存使能
INA228_DIAG_ALRT_SLOWALERT_EN = 0x2000  # 慢速报警使能
INA228_DIAG_ALRT_APOL_RV_EN = 0x1000  # 报警极性反相使能

# 溢出状态（只读）
INA228_DIAG_ALRT_ENERGYOF = 0x0800  # 能量溢出
INA228_DIAG_ALRT_CHARGEOF = 0x0400  # 充电溢出
INA228_DIAG_ALRT_MATHOF = 0x0200  # 数学溢出

# 超限报警（当 ALATCH=1 时，通过读取该寄存器清除该位）
INA228_DIAG_ALRT_TMPOL = 0x0080  # 温度超上限报警
INA228_DIAG_ALRT_SHNTOL = 0x0040  # 分流电压超上限报警
INA228_DIAG_ALRT_SHNTUL = 0x0020  # 分流电压超下限报警
INA228_DIAG_ALRT_BUSOL = 0x0010  # 总线电压超下限报警
INA228_DIAG_ALRT_BUSUL = 0x0008  # 总线电压超上限报警
INA228_DIAG_ALRT_POL = 0x0004  # 功率超上限报警

# 转换完成标志
INA228_DIAG_ALRT_CNVR_EN = 0x4000  # 转换完成使能
INA228_DIAG_ALRT_CNVRF = 0x0002  # 转换完成标志
INA228_DIAG_ALRT_MEMSTAT = 0x0001  # 内存状态报警


class INA228Module(ModuleInterface):
    """INA228高精度单通道电流监测模组
    
    特性:
    - 20-bit ADC，高精度测量
    - 单通道电流/电压/功率/能量监测
    - 内置温度监测
    - 可编程报警功能
    """
    
    def __init__(self, adapter: AdapterInterface, device_addr: int = _DEFAULT_ADDRESS):
        super().__init__(adapter, device_addr)
        self.name = "INA228 High-Precision Current Monitor"
        
        # 默认配置参数
        self.shunt_resistor = 1  # 分流电阻值 (欧姆) - 1Ω
        self.max_expected_current = 0.2  # 最大期望电流 (A)
        self.adc_range = 1 # ADC范围 (0: ±163.84mV, 1: ±40.96mV)
        
        # 校准参数
        self.current_lsb = None  # 电流LSB (A/bit)
        self.shunt_cal = None    # 分流校准值
        
        # 支持温度补偿
        self.temperature_coefficient = 0  # 温度系数 (ppm/°C)
        
        # 默认配置
        self.default_config = (
            INA228_CONFIG_CONVDLY_0us |           # 无转换延迟
            INA228_CONFIG_TEMP_COMP_DISABLE |     # 禁用温度补偿
            INA228_CONFIG_ADC_RANGE_0             # 使用默认ADC范围 (±163.84mV)
        )
        self.default_adc_config = (
            INA228_ADC_CONFIG_MODE_CONT_BUS_SHUNT |     # 连续测量所有参数
            INA228_ADC_CONFIG_VBUSCT_50us |     # 总线电压转换时间
            INA228_ADC_CONFIG_VSHCT_1052us |      # 分流电压转换时间
            INA228_ADC_CONFIG_VTCT_1052us |       # 温度转换时间
            INA228_ADC_CONFIG_AVG_1               # 平均1次采样
        )
        self.default_diag_alrt_config = INA228_DIAG_ALRT_ALATCH_EN # 报警锁存使能
        # self.default_diag_alrt_config = 0
        # 分流过压阈值
        self.sovl = 0x7FFF - 1  # 0x7FFF (32767)* 5uV/LSB = 163.835mV (ADC_RANGE_0)
        # 总线欠压阈值
        self.buvl = 0x310       # 0x410（1040）* 3.125mV/LSB = 3.25V

        # 如果使用40.96mV范围，更新ADC范围配置
        if self.adc_range == 1:
            self.default_config |= INA228_CONFIG_ADC_RANGE_1
    
    def _read_register(self, reg_addr: int, bytes_count: int = 2) -> Optional[int]:
        """读取寄存器
        
        Args:
            reg_addr: 寄存器地址
            bytes_count: 读取字节数 (2或3)
            
        Returns:
            Optional[int]: 读取的数据，失败返回None
        """
        try:
            data = self.adapter.i2c_read_block(self.device_addr, reg_addr, bytes_count)
            if data and len(data) == bytes_count:
                if bytes_count == 2:
                    # 16位寄存器，大端序
                    return (data[0] << 8) | data[1]
                elif bytes_count == 3:
                    # 24位寄存器，大端序
                    return (data[0] << 16) | (data[1] << 8) | data[2]
            return None
        except Exception as e:
            logger.error(f"读取寄存器0x{reg_addr:02X}时出错: {e}")
            return None
    
    def _write_register(self, reg_addr: int, value: int, bytes_count: int = 2) -> bool:
        """写入寄存器
        
        Args:
            reg_addr: 寄存器地址
            value: 要写入的值
            bytes_count: 写入字节数 (2或3)
            
        Returns:
            bool: 成功返回True，失败返回False
        """
        try:
            if bytes_count == 2:
                # 16位寄存器，大端序
                data = bytes([(value >> 8) & 0xFF, value & 0xFF])
            elif bytes_count == 3:
                # 24位寄存器，大端序
                data = bytes([(value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF])
            else:
                logger.error(f"不支持的字节数: {bytes_count}")
                return False
            
            return self.adapter.i2c_write_block(self.device_addr, reg_addr, data)
        except Exception as e:
            logger.error(f"写入寄存器0x{reg_addr:02X}时出错: {e}")
            return False
    
    def _calculate_calibration(self):
        """计算校准参数"""
        # INA228电流LSB计算
        # Current_LSB = Maximum Expected Current / 2^19 (20-bit ADC, 1 bit for sign)
        self.current_lsb = self.max_expected_current / (2**19)
        
        # SHUNT_CAL计算
        # SHUNT_CAL = 13107.2 × 10^6 × Current_LSB × R_shunt
        self.shunt_cal = int(13107.2e6 * self.current_lsb * self.shunt_resistor)
        if self.adc_range == 1:
            self.shunt_cal = self.shunt_cal * 4  # 如果使用40.96mV范围，校准值需要放大4倍
        
        # 确保校准值在有效范围内 (15位有效值)
        if self.shunt_cal > 0x7FFF:
            self.shunt_cal = 0x7FFF
            # 重新计算实际的Current_LSB
            if self.adc_range == 1:
                self.current_lsb = self.shunt_cal / (13107.2e6 * self.shunt_resistor * 4)
            else:
                self.current_lsb = self.shunt_cal / (13107.2e6 * self.shunt_resistor)
        
        logger.info(f"INA228校准参数:")
        logger.info(f"  分流电阻: {self.shunt_resistor*1000:.3f}mΩ")
        logger.info(f"  最大电流: {self.max_expected_current:.2f}A")
        logger.info(f"  电流LSB: {self.current_lsb*1e6:.3f}μA/bit")
        logger.info(f"  校准值: 0x{self.shunt_cal:04X}")
    
    def initialize(self, **kwargs) -> bool:
        """初始化INA228模组"""
        try:
            logger.info("初始化INA228模组...")
            
            # 检查设备ID
            manufacturer_id = self._read_register(INA228_REG_MANUFACTURER_ID)
            device_id = self._read_register(INA228_REG_DEVICE_ID)
            
            if manufacturer_id != 0x5449:  # "TI"
                logger.warning(f"未识别的厂商ID: 0x{manufacturer_id:04X}, 期望: 0x5449")
            
            if device_id is None or (device_id & 0xFFF0) != 0x2280:
                logger.warning(f"未识别的设备ID: 0x{device_id:04X}, 期望: 0x228X")
            
            # 复位设备
            if not self._write_register(INA228_REG_CONFIG, INA228_CONFIG_RESET):
                logger.error("复位设备失败")
                return False
            
            # 等待复位完成
            time.sleep(0.01)
            
            # 设置分流电阻和最大电流（如果提供）
            if "shunt_resistor" in kwargs:
                self.shunt_resistor = kwargs["shunt_resistor"]
            if "max_expected_current" in kwargs:
                self.max_expected_current = kwargs["max_expected_current"]
            
            # 计算校准参数
            self._calculate_calibration()
            
            # 写入校准寄存器
            if not self._write_register(INA228_REG_SHUNT_CAL, self.shunt_cal):
                logger.error("写入校准寄存器失败")
                return False
            
            # 设置温度系数（如果需要）
            if "temperature_coefficient" in kwargs:
                self.temperature_coefficient = kwargs["temperature_coefficient"]
                if not self._write_register(INA228_REG_SHUNT_TEMPCO, self.temperature_coefficient):
                    logger.warning("设置温度系数失败")
            
            # 写入配置寄存器
            if not self._write_register(INA228_REG_CONFIG, self.default_config):
                logger.error("写入配置寄存器失败")
                return False
            
            # 写入ADC配置寄存器
            if not self._write_register(INA228_REG_ADC_CONFIG, self.default_adc_config):
                logger.error("写入ADC配置寄存器失败")
                return False
            
            # 写入诊断和报警配置寄存器
            if not self._write_register(INA228_REG_DIAG_ALRT, self.default_diag_alrt_config):
                logger.error("写入诊断和报警配置寄存器失败")
                return False
            
            if not self._write_register(INA228_REG_SOVL, self.sovl):
                logger.error("写入分流过压阈值寄存器失败")
                return False
            
            if not self._write_register(INA228_REG_BUVL, self.buvl):
                logger.error("写入总线欠压阈值寄存器失败")
                return False

            self.is_initialized = True
            logger.info("INA228模组初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"初始化INA228时出错: {e}")
            return False
    
    def read_shunt_voltage(self) -> Optional[float]:
        """读取分流电压 (V)"""
        raw_value = self._read_register(INA228_REG_VSHUNT, 3)  # 24位数据
        if raw_value is None:
            return None
        
        raw_value = raw_value >> 4  # 去掉低4位
        
        # 转换为有符号数 (20位有效数据)
        if raw_value & 0x80000:  # 检查符号位
            raw_value = raw_value - 0x100000  # 20位补码转换
        
        if self.adc_range == 1:
            # 如果使用40.96mV范围，分流电压LSB = 78.125nV
            shunt_voltage = raw_value * 78.125e-9
        else:
            # 默认使用163.84mV范围，INA228分流电压LSB = 312.5nV
            shunt_voltage = raw_value * 312.5e-9
        return shunt_voltage
    
    def read_bus_voltage(self) -> Optional[float]:
        """读取总线电压 (V)"""
        raw_value = self._read_register(INA228_REG_VBUS, 3)  # 24位数据
        if raw_value is None:
            return None
        
        raw_value = raw_value >> 4  # 去掉低4位
        
        # INA228总线电压LSB = 195.3125μV
        bus_voltage = raw_value * 195.3125e-6
        return bus_voltage
    
    def read_temperature(self) -> Optional[float]:
        """读取芯片温度 (°C)"""
        raw_value = self._read_register(INA228_REG_DIETEMP)
        if raw_value is None:
            return None
        
        # 转换为有符号数
        if raw_value & 0x8000:
            raw_value = raw_value - 0x10000
        
        # 温度LSB = 7.8125m°C
        temperature = raw_value * 7.8125e-3
        return temperature
    
    def read_current(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取电流值 (A)"""
        if channel is not None:
            logger.debug("INA228是单通道设备，忽略通道参数")
        
        raw_value = self._read_register(INA228_REG_CURRENT, 3)  # 24位数据
        raw_value = raw_value >> 4  # 去掉低4位
        if raw_value is None:
            return None
        
        # 转换为有符号数 (20位有效数据)
        if raw_value & 0x80000:  # 检查符号位
            raw_value = raw_value - 0x100000  # 20位补码转换
        
        # 电流 = raw_value × Current_LSB
        current = raw_value * self.current_lsb
        return current
    
    def read_voltage(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取电压值 (V) - 返回总线电压"""
        if channel is not None:
            logger.debug("INA228是单通道设备，忽略通道参数")
        
        return self.read_bus_voltage()
    
    def read_power(self, channel: Optional[int] = None) -> Union[float, List[float], None]:
        """读取功率值 (W)"""
        if channel is not None:
            logger.debug("INA228是单通道设备，忽略通道参数")
        
        raw_value = self._read_register(INA228_REG_POWER, 3)  # 24位数据
        if raw_value is None:
            return None
        
        # 功率LSB = 3.2 × Current_LSB
        power = raw_value * 3.2 * self.current_lsb
        return power
    
    def read_energy(self) -> Optional[float]:
        """读取累计能量 (J)"""
        raw_value = self._read_register(INA228_REG_ENERGY, 5)  # 40位数据
        if raw_value is None:
            return None
        
        # 能量LSB = 16 × Power_LSB × 1s = 16 × 3.2 × Current_LSB
        energy = raw_value * 16 * 3.2 * self.current_lsb
        return energy
    
    def read_charge(self) -> Optional[float]:
        """读取累计电荷 (C)"""
        raw_value = self._read_register(INA228_REG_CHARGE, 5)  # 40位数据
        if raw_value is None:
            return None
        
        # 电荷LSB = Current_LSB
        charge = raw_value * self.current_lsb
        return charge
    
    def configure(self, **kwargs) -> bool:
        """配置模组参数"""
        success = True
        
        # 分流电阻配置
        if "shunt_resistor" in kwargs:
            self.shunt_resistor = kwargs["shunt_resistor"]
            self._calculate_calibration()
            if not self._write_register(INA228_REG_SHUNT_CAL, self.shunt_cal):
                logger.error("重新配置校准寄存器失败")
                success = False
        
        # 温度系数配置
        if "temperature_coefficient" in kwargs:
            temp_coeff = kwargs["temperature_coefficient"]
            if not self._write_register(INA228_REG_SHUNT_TEMPCO, temp_coeff):
                logger.error("设置温度系数失败")
                success = False
        
        # 报警阈值配置
        if "shunt_overvoltage_limit" in kwargs:
            limit = int(kwargs["shunt_overvoltage_limit"] / 312.5e-9)  # 转换为LSB
            if not self._write_register(INA228_REG_SOVL, limit):
                logger.error("设置分流过压阈值失败")
                success = False
        
        if "shunt_undervoltage_limit" in kwargs:
            limit = int(kwargs["shunt_undervoltage_limit"] / 312.5e-9)  # 转换为LSB
            if not self._write_register(INA228_REG_SUVL, limit):
                logger.error("设置分流欠压阈值失败")
                success = False
        
        if "bus_overvoltage_limit" in kwargs:
            limit = int(kwargs["bus_overvoltage_limit"] / 195.3125e-6)  # 转换为LSB
            if not self._write_register(INA228_REG_BOVL, limit):
                logger.error("设置总线过压阈值失败")
                success = False
        
        if "bus_undervoltage_limit" in kwargs:
            limit = int(kwargs["bus_undervoltage_limit"] / 195.3125e-6)  # 转换为LSB
            if not self._write_register(INA228_REG_BUVL, limit):
                logger.error("设置总线欠压阈值失败")
                success = False
        
        if "power_limit" in kwargs:
            limit = int(kwargs["power_limit"] / (3.2 * self.current_lsb))  # 转换为LSB
            if not self._write_register(INA228_REG_PWR_LIMIT, limit):
                logger.error("设置功率限制失败")
                success = False
        
        if "temperature_limit" in kwargs:
            limit = int(kwargs["temperature_limit"] / 7.8125e-3)  # 转换为LSB
            if not self._write_register(INA228_REG_TEMP_LIMIT, limit):
                logger.error("设置温度限制失败")
                success = False
        
        return success
    
    def get_all_readings(self) -> Dict[str, Any]:
        """获取所有测量值"""
        return {
            "shunt_voltage": self.read_shunt_voltage(),
            "bus_voltage": self.read_bus_voltage(),
            "current": self.read_current(),
            "power": self.read_power(),
            "temperature": self.read_temperature(),
            "energy": self.read_energy(),
            "charge": self.read_charge()
        }
    
    def reset_energy_charge(self) -> bool:
        """重置累计能量和电荷寄存器"""
        # 通过写入0来重置累计寄存器
        success = True
        if not self._write_register(INA228_REG_ENERGY, 0, 5):
            logger.error("重置能量寄存器失败")
            success = False
        
        if not self._write_register(INA228_REG_CHARGE, 0, 5):
            logger.error("重置电荷寄存器失败")
            success = False
        
        return success
    
    def get_info(self) -> Dict[str, Any]:
        """获取模组详细信息"""
        base_info = super().get_info()
        
        # 添加INA228特有信息
        ina228_info = {
            "shunt_resistor": f"{self.shunt_resistor*1000:.3f}mΩ",
            "max_expected_current": f"{self.max_expected_current:.2f}A",
            "current_lsb": f"{self.current_lsb*1e6:.3f}μA/bit" if self.current_lsb else "未计算",
            "shunt_cal": f"0x{self.shunt_cal:04X}" if self.shunt_cal else "未计算",
            "temperature_coefficient": f"{self.temperature_coefficient}ppm/°C",
            "features": ["20-bit ADC", "能量累计", "电荷累计", "温度监测", "可编程报警"]
        }
        
        base_info.update(ina228_info)
        return base_info