#!/usr/bin/env python3
"""
INA226电流/功率监测示例
实时监测电源的电压、电流和功率参数
"""

import sys
import os
import time
import threading
from datetime import datetime

# 添加DLL路径 - 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release", "x64")
sys.path.append(dll_path)
os.chdir(dll_path)

try:
    from SLABHIDtoSMBUS import *
except ImportError as e:
    print(f"导入错误: {e}")
    sys.exit(1)

class INA226:
    """INA226电流/功率监测芯片驱动类"""
    
    # 寄存器地址
    REG_CONFIG = 0x00
    REG_SHUNT_VOLTAGE = 0x01
    REG_BUS_VOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05
    REG_MASK_ENABLE = 0x06
    REG_ALERT_LIMIT = 0x07
    REG_MANUFACTURER_ID = 0xFE
    REG_DIE_ID = 0xFF
    
    # 配置位
    CONFIG_RESET = 0x8000
    CONFIG_AVG_1 = 0x0000
    CONFIG_AVG_4 = 0x0200
    CONFIG_AVG_16 = 0x0400
    CONFIG_AVG_64 = 0x0600
    CONFIG_AVG_128 = 0x0800
    CONFIG_AVG_256 = 0x0A00
    CONFIG_AVG_512 = 0x0C00
    CONFIG_AVG_1024 = 0x0E00
    
    def __init__(self, device, address=0x40, shunt_resistance=0.1):
        """
        初始化INA226
        
        Args:
            device: CP2112设备对象
            address: INA226 I2C地址 (默认0x40)
            shunt_resistance: 分流电阻值(欧姆，默认0.1Ω)
        """
        self.device = device
        self.address = address
        self.shunt_resistance = shunt_resistance
        self.current_lsb = 0.001  # 1mA LSB
        self.power_lsb = 25 * self.current_lsb  # 25 * Current_LSB
        
    def write_register(self, reg, value):
        """写入16位寄存器"""
        data = [reg, (value >> 8) & 0xFF, value & 0xFF]
        self.device.write_request(self.address, data)
        time.sleep(0.001)
        
    def read_register(self, reg):
        """读取16位寄存器"""
        self.device.write_request(self.address, [reg])
        time.sleep(0.001)
        data = self.device.read_request(self.address, 2)
        return (data[0] << 8) | data[1]
        
    def check_device(self):
        """检查设备是否为INA226"""
        try:
            manufacturer_id = self.read_register(self.REG_MANUFACTURER_ID)
            die_id = self.read_register(self.REG_DIE_ID)
            
            # INA226的厂商ID应该是0x5449 ("TI")，芯片ID应该是0x2260
            if manufacturer_id == 0x5449 and die_id == 0x2260:
                return True
            else:
                print(f"警告: 设备ID不匹配 (厂商ID: 0x{manufacturer_id:04X}, 芯片ID: 0x{die_id:04X})")
                return False
        except:
            return False
            
    def reset(self):
        """软件复位INA226"""
        self.write_register(self.REG_CONFIG, self.CONFIG_RESET)
        time.sleep(0.01)  # 等待复位完成
        
    def configure(self, averaging=CONFIG_AVG_4, bus_conversion_time=4, shunt_conversion_time=4):
        """
        配置INA226
        
        Args:
            averaging: 平均次数
            bus_conversion_time: 总线电压转换时间 (0=140us, 1=204us, 2=332us, 3=588us, 4=1.1ms, 5=2.116ms, 6=4.156ms, 7=8.244ms)
            shunt_conversion_time: 分流电压转换时间
        """
        # 构建配置寄存器值
        config = (averaging | 
                 (bus_conversion_time << 6) | 
                 (shunt_conversion_time << 3) | 
                 0x0007)  # 连续模式，分流和总线电压
        
        self.write_register(self.REG_CONFIG, config)
        
        # 计算并设置校准寄存器
        # Cal = 0.00512 / (Current_LSB * Rshunt)
        cal = int(0.00512 / (self.current_lsb * self.shunt_resistance))
        self.write_register(self.REG_CALIBRATION, cal)
        
        print(f"INA226配置完成 (校准值: {cal})")
        
    def read_all_registers(self):
        """读取所有寄存器的原始值"""
        registers = {}
        reg_names = {
            self.REG_CONFIG: "Config",
            self.REG_SHUNT_VOLTAGE: "Shunt Voltage",
            self.REG_BUS_VOLTAGE: "Bus Voltage", 
            self.REG_POWER: "Power",
            self.REG_CURRENT: "Current",
            self.REG_CALIBRATION: "Calibration",
            self.REG_MASK_ENABLE: "Mask/Enable",
            self.REG_ALERT_LIMIT: "Alert Limit"
        }
        
        for reg, name in reg_names.items():
            try:
                value = self.read_register(reg)
                registers[name] = value
            except:
                registers[name] = None
                
        return registers
        
    def read_measurements(self):
        """读取所有测量值并转换为实际单位"""
        try:
            # 读取分流电压 (2.5μV LSB)
            shunt_raw = self.read_register(self.REG_SHUNT_VOLTAGE)
            if shunt_raw & 0x8000:  # 处理有符号数
                shunt_raw = shunt_raw - 0x10000
            shunt_voltage = shunt_raw * 2.5e-6  # 转换为伏特
            
            # 读取总线电压 (1.25mV LSB)
            bus_raw = self.read_register(self.REG_BUS_VOLTAGE)
            bus_voltage = bus_raw * 1.25e-3  # 转换为伏特
            
            # 读取电流 (Current_LSB)
            current_raw = self.read_register(self.REG_CURRENT)
            if current_raw & 0x8000:
                current_raw = current_raw - 0x10000
            current = current_raw * self.current_lsb  # 转换为安培
            
            # 读取功率 (Power_LSB = 25 * Current_LSB)
            power_raw = self.read_register(self.REG_POWER)
            power = power_raw * self.power_lsb  # 转换为瓦特
            
            return {
                'shunt_voltage': shunt_voltage,
                'bus_voltage': bus_voltage,
                'current': current,
                'power': power,
                'timestamp': datetime.now()
            }
        except Exception as e:
            print(f"读取测量值失败: {e}")
            return None

class PowerMonitor:
    """电源监测器类"""
    
    def __init__(self, ina226):
        self.ina226 = ina226
        self.running = False
        self.data_log = []
        self.max_log_entries = 1000
        
    def start_monitoring(self, interval=1.0):
        """开始监测"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, args=(interval,))
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """停止监测"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join()
            
    def _monitor_loop(self, interval):
        """监测循环"""
        while self.running:
            measurements = self.ina226.read_measurements()
            if measurements:
                self.data_log.append(measurements)
                
                # 限制日志长度
                if len(self.data_log) > self.max_log_entries:
                    self.data_log.pop(0)
                    
            time.sleep(interval)
            
    def get_latest_data(self):
        """获取最新数据"""
        return self.data_log[-1] if self.data_log else None
        
    def get_statistics(self):
        """获取统计信息"""
        if not self.data_log:
            return None
            
        voltages = [d['bus_voltage'] for d in self.data_log]
        currents = [abs(d['current']) for d in self.data_log]
        powers = [abs(d['power']) for d in self.data_log]
        
        return {
            'voltage': {'min': min(voltages), 'max': max(voltages), 'avg': sum(voltages)/len(voltages)},
            'current': {'min': min(currents), 'max': max(currents), 'avg': sum(currents)/len(currents)},
            'power': {'min': min(powers), 'max': max(powers), 'avg': sum(powers)/len(powers)},
            'samples': len(self.data_log)
        }

def find_ina226_devices(device):
    """查找INA226设备"""
    ina226_addresses = [0x40, 0x41, 0x44, 0x45]  # 常见的INA226地址
    found_devices = []
    
    print("搜索INA226设备...")
    
    for addr in ina226_addresses:
        try:
            ina226 = INA226(device, addr)
            if ina226.check_device():
                found_devices.append(addr)
                print(f"✓ 发现INA226设备在地址 0x{addr:02X}")
            else:
                # 尝试基本通信测试
                device.write_request(addr, [])
                status = device.transfer_status_request()
                if status[0] == HID_SMBUS_S0.COMPLETE:
                    print(f"? 地址 0x{addr:02X} 有响应但不是标准INA226")
        except:
            pass
            
    return found_devices

def main():
    """主函数"""
    print("INA226电源监测工具")
    print("=" * 50)
    
    try:
        # 连接CP2112设备
        num_devices = GetNumDevices()
        if num_devices == 0:
            print("未发现CP2112设备")
            return
            
        device = HidSmbusDevice()
        if device.open(0) != 0:
            print("CP2112设备连接失败")
            return
            
        print("CP2112设备连接成功")
        
        # 配置SMBus
        device.set_smbus_config(400000, 1000, 3, False, 1000)  # 400kHz
        
        # 查找INA226设备
        ina226_addresses = find_ina226_devices(device)
        
        if not ina226_addresses:
            print("未发现INA226设备")
            print("请检查:")
            print("- 设备连接是否正确")
            print("- 设备地址是否正确")
            print("- 电源是否已接通")
            return
            
        # 使用第一个找到的INA226
        ina226_addr = ina226_addresses[0]
        print(f"\n使用地址 0x{ina226_addr:02X} 的INA226设备")
        
        # 初始化INA226
        ina226 = INA226(device, ina226_addr, shunt_resistance=0.1)  # 0.1Ω分流电阻
        
        # 复位并配置
        ina226.reset()
        ina226.configure()
        
        # 显示寄存器信息
        print("\nINA226寄存器状态:")
        registers = ina226.read_all_registers()
        for name, value in registers.items():
            if value is not None:
                print(f"  {name}: 0x{value:04X}")
        
        # 开始监测
        monitor = PowerMonitor(ina226)
        monitor.start_monitoring(0.5)  # 500ms间隔
        
        print("\n开始实时监测... (按Ctrl+C停止)")
        print("时间       电压     电流     功率")
        print("-" * 50)
        
        try:
            while True:
                data = monitor.get_latest_data()
                if data:
                    timestamp = data['timestamp'].strftime("%H:%M:%S")
                    voltage = data['bus_voltage']
                    current = data['current'] * 1000  # 转换为mA
                    power = data['power'] * 1000      # 转换为mW
                    
                    print(f"{timestamp}  {voltage:6.3f}V  {current:7.1f}mA  {power:7.1f}mW")
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n监测停止")
            
        # 显示统计信息
        monitor.stop_monitoring()
        stats = monitor.get_statistics()
        
        if stats:
            print("\n统计信息:")
            print(f"采样数量: {stats['samples']}")
            print(f"电压 - 最小: {stats['voltage']['min']:.3f}V, "
                  f"最大: {stats['voltage']['max']:.3f}V, "
                  f"平均: {stats['voltage']['avg']:.3f}V")
            print(f"电流 - 最小: {stats['current']['min']*1000:.1f}mA, "
                  f"最大: {stats['current']['max']*1000:.1f}mA, "
                  f"平均: {stats['current']['avg']*1000:.1f}mA")
            print(f"功率 - 最小: {stats['power']['min']*1000:.1f}mW, "
                  f"最大: {stats['power']['max']*1000:.1f}mW, "
                  f"平均: {stats['power']['avg']*1000:.1f}mW")
        
    except Exception as e:
        print(f"错误: {e}")
        
    finally:
        try:
            device.close()
            print("设备已断开")
        except:
            pass

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")
