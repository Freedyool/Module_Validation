# CP2112 USB桥接器 - SMBus/I2C接口

本项目包含Silicon Labs CP2112 USB-to-SMBus/I2C桥接芯片的控制代码和示例。

## 目录
- [概述](#概述)
- [硬件特性](#硬件特性)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [Python使用指南](#python使用指南)
- [示例代码](#示例代码)
- [API参考](#api参考)
- [故障排除](#故障排除)
- [参考文档](#参考文档)

## 概述

CP2112是Silicon Labs开发的USB-to-SMBus/I2C桥接芯片，它提供了一个简单的方式来通过USB接口与SMBus和I2C设备进行通信。该芯片广泛应用于：

- 系统监控和管理
- 电源管理器件控制
- 传感器数据读取
- EEPROM编程
- 温度监测

## 硬件特性

- **接口类型**: USB 2.0 Full Speed (12 Mbps)
- **总线协议**: SMBus 3.0兼容，I2C兼容
- **时钟频率**: 10 kHz - 1 MHz (可配置)
- **电源电压**: 3.3V或5V
- **GPIO功能**: 8个可配置GPIO引脚
- **包装**: QFN-24
- **操作温度**: -40°C 到 +85°C

## 环境要求

### 硬件要求
- CP2112评估板或集成CP2112芯片的设备
- USB连接线
- 目标SMBus/I2C设备

### 软件要求
- Windows 10/11 (x86/x64)
- Python 3.6+ (推荐Python 3.8+)
- CP2112驱动程序 (Windows会自动识别)

## 快速开始

### 1. 硬件连接
```
CP2112评估板    目标设备
SDA      ←→    SDA
SCL      ←→    SCL  
GND      ←→    GND
VDD      ←→    VCC (3.3V或5V)
```

### 2. 验证设备连接
将CP2112设备连接到PC后，在设备管理器中应该能看到"Silicon Labs CP2112 USB-to-SMBus Bridge"设备。

### 3. 运行示例程序

#### 运行官方示例
双击运行Examples/HidSmbusExample.exe。

#### 运行脚本示例
```bash
# 方法1: 使用启动脚本
run_examples.bat

# 方法2: 直接运行Python示例
python example_device_detect.py
python example_i2c_scan.py  
python example_ina226_monitor.py
```

## Python使用指南

Silicon Labs SDK提供了两个主要的Python模块：

1. SLABHIDDevice.py
底层HID设备通信模块，提供基础的设备访问功能。

2. SLABHIDtoSMBUS.py
高级SMBus/I2C通信模块，专门为CP2112设计的封装库。

### 基本使用步骤

#### 步骤1: 导入模块
```python
import sys
import os

# 添加DLL路径 - 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release", "x64")
sys.path.append(dll_path)
os.chdir(dll_path)

from SLABHIDtoSMBUS import *
```

#### 步骤2: 设备发现和连接
```python
# 获取连接的CP2112设备数量
num_devices = GetNumDevices()
print(f"发现 {num_devices} 个CP2112设备")

# 打开第一个设备
if num_devices > 0:
    device = HidSmbusDevice()
    device.open(0)  # 打开第一个设备
    print("设备连接成功")
```

#### 步骤3: 配置SMBus参数
```python
# 设置SMBus配置
bitrate = 100000  # 100kHz
timeout = 1000    # 1秒超时
retry_times = 3   # 重试次数
scl_low_timeout = False
response_timeout = 1000

device.set_smbus_config(bitrate, timeout, retry_times, 
                       scl_low_timeout, response_timeout)
```

#### 步骤4: 数据读写操作
```python
# SMBus快速写
slave_address = 0x48  # 目标设备地址
device.write_request(slave_address, [])

# SMBus字节读
data = device.read_request(slave_address, 1)
print(f"读取数据: 0x{data[0]:02X}")

# SMBus字节写
register = 0x01
value = 0xAA
device.write_request(slave_address, [register, value])

# SMBus字读取 (16位数据)
data = device.read_request(slave_address, 2)
word_value = (data[1] << 8) | data[0]  # 小端序
print(f"字数据: 0x{word_value:04X}")
```

#### 步骤5: 关闭设备
```python
device.close()
print("设备已断开")
```

## 示例代码

### 示例1: 基本设备检测

```python
import sys
import os

# 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release", "x64")
sys.path.append(dll_path)
os.chdir(dll_path)

from SLABHIDtoSMBUS import *

def detect_devices():
    """检测连接的CP2112设备"""
    num_devices = GetNumDevices()
    print(f"检测到 {num_devices} 个CP2112设备")
    
    for i in range(num_devices):
        # 获取设备属性
        vid, pid, release_num = GetAttributes(i)
        serial = GetString(i, HID_SMBUS.SERIAL_STR)
        manufacturer = GetString(i, HID_SMBUS.MANUFACTURER_STR)
        product = GetString(i, HID_SMBUS.PRODUCT_STR)
        
        print(f"设备 {i}:")
        print(f"  VID: 0x{vid:04X}")
        print(f"  PID: 0x{pid:04X}")
        print(f"  序列号: {serial}")
        print(f"  制造商: {manufacturer}")
        print(f"  产品名: {product}")

if __name__ == "__main__":
    detect_devices()
```

### 示例2: 读取温度传感器 (LM75)

```python
import sys
import os

# 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release", "x64")
sys.path.append(dll_path)
os.chdir(dll_path)

from SLABHIDtoSMBUS import *
import time

def read_lm75_temperature():
    """读取LM75温度传感器数据"""
    try:
        # 连接设备
        device = HidSmbusDevice()
        device.open(0)
        
        # 配置SMBus (100kHz)
        device.set_smbus_config(100000, 1000, 3, False, 1000)
        
        # LM75设备地址 (典型地址: 0x48-0x4F)
        lm75_addr = 0x48
        temp_reg = 0x00  # 温度寄存器
        
        # 写入寄存器地址
        device.write_request(lm75_addr, [temp_reg])
        time.sleep(0.01)  # 短暂延时
        
        # 读取温度数据 (2字节)
        data = device.read_request(lm75_addr, 2)
        
        # 转换温度值 (LM75格式: 11位，0.125°C分辨率)
        temp_raw = (data[0] << 8) | data[1]
        temp_raw = temp_raw >> 5  # 右移5位获取11位数据
        
        if temp_raw & 0x400:  # 检查符号位
            temp_raw = temp_raw - 0x800  # 负温度补码转换
            
        temperature = temp_raw * 0.125  # 转换为摄氏度
        
        print(f"LM75温度: {temperature:.3f}°C")
        
        device.close()
        return temperature
        
    except Exception as e:
        print(f"错误: {e}")
        return None

if __name__ == "__main__":
    read_lm75_temperature()
```

### 示例3: INA226电流/功率监测

```python
import sys
import os

# 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release", "x64")
sys.path.append(dll_path)
os.chdir(dll_path)

from SLABHIDtoSMBUS import *
import time

class INA226:
    """INA226电流/功率监测芯片驱动"""
    
    # 寄存器地址
    REG_CONFIG = 0x00
    REG_SHUNT_VOLTAGE = 0x01
    REG_BUS_VOLTAGE = 0x02
    REG_POWER = 0x03
    REG_CURRENT = 0x04
    REG_CALIBRATION = 0x05
    
    def __init__(self, device, address=0x40):
        self.device = device
        self.address = address
        self.shunt_resistance = 0.1  # 0.1欧姆分流器
        
    def write_register(self, reg, value):
        """写入16位寄存器"""
        data = [reg, (value >> 8) & 0xFF, value & 0xFF]
        self.device.write_request(self.address, data)
        
    def read_register(self, reg):
        """读取16位寄存器"""
        self.device.write_request(self.address, [reg])
        time.sleep(0.001)
        data = self.device.read_request(self.address, 2)
        return (data[0] << 8) | data[1]
        
    def configure(self):
        """配置INA226"""
        # 配置寄存器: 连续模式，分流和总线电压转换时间1.1ms，平均1次
        config = 0x4127
        self.write_register(self.REG_CONFIG, config)
        
        # 校准寄存器计算
        # Current_LSB = Maximum Expected Current / 32768
        # Cal = 0.00512 / (Current_LSB * Rshunt)
        current_lsb = 0.001  # 1mA
        cal = int(0.00512 / (current_lsb * self.shunt_resistance))
        self.write_register(self.REG_CALIBRATION, cal)
        
    def read_measurements(self):
        """读取所有测量值"""
        # 读取分流电压 (2.5uV LSB)
        shunt_raw = self.read_register(self.REG_SHUNT_VOLTAGE)
        if shunt_raw & 0x8000:  # 有符号数处理
            shunt_raw = shunt_raw - 0x10000
        shunt_voltage = shunt_raw * 2.5e-6  # 转换为伏特
        
        # 读取总线电压 (1.25mV LSB)
        bus_raw = self.read_register(self.REG_BUS_VOLTAGE)
        bus_voltage = bus_raw * 1.25e-3  # 转换为伏特
        
        # 读取电流 (1mA LSB)
        current_raw = self.read_register(self.REG_CURRENT)
        if current_raw & 0x8000:
            current_raw = current_raw - 0x10000
        current = current_raw * 0.001  # 转换为安培
        
        # 读取功率 (25倍电流LSB)
        power_raw = self.read_register(self.REG_POWER)
        power = power_raw * 0.025  # 转换为瓦特
        
        return {
            'shunt_voltage': shunt_voltage,
            'bus_voltage': bus_voltage,
            'current': current,
            'power': power
        }

def monitor_power():
    """监测电源参数"""
    try:
        device = HidSmbusDevice()
        device.open(0)
        device.set_smbus_config(400000, 1000, 3, False, 1000)  # 400kHz
        
        ina226 = INA226(device)
        ina226.configure()
        
        print("INA226电源监测启动...")
        print("按Ctrl+C停止监测")
        
        while True:
            measurements = ina226.read_measurements()
            
            print(f"总线电压: {measurements['bus_voltage']:.3f}V, "
                  f"电流: {measurements['current']*1000:.1f}mA, "
                  f"功率: {measurements['power']*1000:.1f}mW")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n监测停止")
    except Exception as e:
        print(f"错误: {e}")
    finally:
        device.close()

if __name__ == "__main__":
    monitor_power()
```

## API参考

### 核心类和函数

#### HidSmbusDevice类
主要的设备控制类，提供SMBus/I2C通信功能。

**方法：**

- `open(device_num)` - 打开指定设备
- `close()` - 关闭设备连接
- `is_opened()` - 检查设备是否已打开
- `set_smbus_config(bitrate, timeout, retry_times, scl_low_timeout, response_timeout)` - 配置SMBus参数
- `get_smbus_config()` - 获取当前SMBus配置
- `write_request(slave_address, data)` - SMBus写操作
- `read_request(slave_address, num_bytes)` - SMBus读操作
- `transfer_status_request()` - 获取传输状态
- `cancel_transfer()` - 取消当前传输

#### 全局函数

- `GetNumDevices()` - 获取连接的CP2112设备数量
- `GetAttributes(device_num)` - 获取设备属性(VID, PID, 版本)
- `GetString(device_num, string_type)` - 获取设备字符串信息
- `GetLibraryVersion()` - 获取库版本
- `IsOpened(device_num)` - 检查指定设备是否已打开

### 常量定义

#### HID_SMBUS类
```python
VID = 0x10C4        # CP2112厂商ID
PID = 0xEA90        # CP2112产品ID

# 字符串类型
VID_STR = 0x01
PID_STR = 0x02  
PATH_STR = 0x03
SERIAL_STR = 0x04
MANUFACTURER_STR = 0x05
PRODUCT_STR = 0x06
```

#### 状态码
```python
# 传输状态
HID_SMBUS_S0.IDLE = 0x00         # 空闲
HID_SMBUS_S0.BUSY = 0x01         # 忙碌
HID_SMBUS_S0.COMPLETE = 0x02     # 完成
HID_SMBUS_S0.ERROR = 0x03        # 错误

# 详细状态
HID_SMBUS_S1.BUSY_ADDRESS_ACKED = 0x00    # 地址已应答
HID_SMBUS_S1.BUSY_ADDRESS_NACKED = 0x01   # 地址未应答
```

## 故障排除

### 常见问题

#### 1. 设备无法识别
**症状**: `GetNumDevices()`返回0
**解决方案**:
- 检查USB连接
- 确认设备管理器中是否显示CP2112设备
- 重新插拔USB线
- 检查是否有其他程序正在使用设备

#### 2. DLL加载失败
**症状**: ImportError或找不到DLL
**解决方案**:
```python
import os
# 确保工作目录正确 - 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release", "x64")
os.chdir(dll_path)
```

#### 3. SMBus通信超时
**症状**: 读写操作超时
**解决方案**:
- 检查硬件连接(SDA, SCL, GND)
- 确认目标设备地址正确
- 增加超时时间
- 降低时钟频率
- 检查上拉电阻(通常需要4.7kΩ)

#### 4. 数据读取错误
**症状**: 读取的数据不正确
**解决方案**:
- 确认字节序(大端/小端)
- 检查寄存器地址
- 添加适当延时
- 验证设备数据表格式

### 调试技巧

#### 启用详细日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 在关键操作前后添加日志
print(f"写入地址 0x{address:02X}, 数据: {data}")
result = device.write_request(address, data)
print(f"写入结果: {result}")
```

#### 检查传输状态
```python
status = device.transfer_status_request()
print(f"传输状态: S0={status[0]}, S1={status[1]}")
```

#### 扫描I2C总线
```python
def scan_i2c_bus(device):
    """扫描I2C总线上的设备"""
    print("扫描I2C总线...")
    found_devices = []
    
    for addr in range(0x08, 0x78):  # 标准I2C地址范围
        try:
            device.write_request(addr, [])  # 快速写测试
            status = device.transfer_status_request()
            if status[0] == HID_SMBUS_S0.COMPLETE:
                found_devices.append(addr)
                print(f"发现设备: 0x{addr:02X}")
        except:
            pass
    
    return found_devices
```

## 参考文档

### Silicon Labs官方文档
- **AN495**: CP2112接口规范
- **AN496**: HID USB到SMBus API规范  
- **CP2112数据表**: 完整的硬件规格
- **CP2112用户指南**: 评估板使用指南

### 相关标准
- **SMBus 3.0规范**: 系统管理总线规范
- **I2C总线规范**: 飞利浦I2C标准
- **USB HID规范**: USB人机接口设备规范

### 在线资源
- [Silicon Labs开发者中心](https://www.silabs.com/developers)
- [CP2112产品页面](https://www.silabs.com/interface/usb-bridges/classic/device.cp2112)
- [技术支持论坛](https://community.silabs.com/)

## 许可证

本项目中的大部分代码示例来源于Silicon Labs USBXpress Host SDK，遵循Silicon Labs的许可协议。

---

**开发者**: Freed Yool  
**最后更新**: 2025年6月27日  
**版本**: 1.0.0

