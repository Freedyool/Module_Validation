#!/usr/bin/env python3
"""
I2C总线扫描工具
扫描I2C总线上的所有设备并显示地址映射
"""

import sys
import os
import time

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

# 常见I2C设备地址映射
COMMON_DEVICES = {
    0x48: "LM75温度传感器 / TMP100系列",
    0x40: "INA226电流传感器",
    0x41: "INA226电流传感器 (A0=VCC)",
    0x44: "INA226电流传感器 (A1=VCC)",
    0x45: "INA226电流传感器 (A0+A1=VCC)",
    0x50: "24C02 EEPROM",
    0x51: "24C02 EEPROM (A0=VCC)",
    0x68: "DS1307 RTC / MPU6050陀螺仪",
    0x69: "MPU6050陀螺仪 (AD0=VCC)",
    0x77: "BMP280气压传感器",
    0x76: "BMP280气压传感器 (SDO=GND)",
    0x1D: "ADXL345加速度计",
    0x53: "ADXL345加速度计 (ALT ADDRESS)",
    0x3C: "SSD1306 OLED显示器",
    0x3D: "SSD1306 OLED显示器 (SA0=VCC)",
    0x20: "PCF8574 I/O扩展器",
    0x21: "PCF8574 I/O扩展器 (A0=VCC)",
    0x22: "PCF8574 I/O扩展器 (A1=VCC)",
    0x23: "PCF8574 I/O扩展器 (A0+A1=VCC)",
}

def scan_i2c_bus(device, start_addr=0x08, end_addr=0x77, delay=0.01):
    """
    扫描I2C总线
    
    Args:
        device: CP2112设备对象
        start_addr: 起始地址 (默认0x08)
        end_addr: 结束地址 (默认0x77)
        delay: 扫描间隔 (秒)
    
    Returns:
        list: 发现的设备地址列表
    """
    print(f"扫描I2C总线地址范围: 0x{start_addr:02X} - 0x{end_addr:02X}")
    print("扫描中", end="")
    
    found_devices = []
    
    for addr in range(start_addr, end_addr + 1):
        print(".", end="", flush=True)
        
        try:
            # 尝试快速写操作来检测设备
            device.write_request(addr, [])
            time.sleep(delay)
            
            # 检查传输状态
            status = device.transfer_status_request()
            
            if status[0] == HID_SMBUS_S0.COMPLETE:
                found_devices.append(addr)
            elif status[0] == HID_SMBUS_S0.ERROR:
                # 清除错误状态
                device.cancel_transfer()
                
        except Exception as e:
            # 忽略异常，继续扫描
            pass
        
        time.sleep(delay)
    
    print()  # 换行
    return found_devices

def display_scan_results(found_devices):
    """显示扫描结果"""
    if not found_devices:
        print("未发现任何I2C设备")
        print("\n可能的原因:")
        print("- 没有连接I2C设备")
        print("- 上拉电阻缺失或不正确")
        print("- 设备地址不在扫描范围内")
        print("- 硬件连接问题")
        return
    
    print(f"\n发现 {len(found_devices)} 个I2C设备:")
    print("=" * 60)
    
    for addr in found_devices:
        device_name = COMMON_DEVICES.get(addr, "未知设备")
        print(f"地址: 0x{addr:02X} ({addr:3d}) - {device_name}")
    
    print("=" * 60)

def display_address_map(found_devices):
    """显示地址映射表"""
    print("\nI2C地址映射表:")
    print("     0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F")
    
    for row in range(0x08 // 16, (0x77 // 16) + 1):
        print(f"{row:02X}: ", end="")
        
        for col in range(16):
            addr = row * 16 + col
            
            if addr < 0x08 or addr > 0x77:
                print("   ", end="")
            elif addr in found_devices:
                print(f"{addr:02X} ", end="")
            else:
                print("-- ", end="")
        
        print()

def quick_device_test(device, address):
    """对发现的设备进行快速测试"""
    print(f"\n测试设备 0x{address:02X}:")
    
    try:
        # 尝试读取1字节数据
        data = device.read_request(address, 1)
        print(f"  快速读取: 0x{data[0]:02X}")
        
        # 如果是常见的传感器，尝试读取更多数据
        if address in [0x48, 0x49, 0x4A, 0x4B]:  # LM75系列
            try:
                temp_data = device.read_request(address, 2)
                temp_raw = (temp_data[0] << 8) | temp_data[1]
                temp_raw = temp_raw >> 5
                if temp_raw & 0x400:
                    temp_raw = temp_raw - 0x800
                temperature = temp_raw * 0.125
                print(f"  温度读数: {temperature:.3f}°C")
            except:
                pass
                
    except Exception as e:
        print(f"  测试失败: {e}")

def main():
    """主函数"""
    print("I2C总线扫描工具")
    print("=" * 40)
    
    try:
        # 检查设备
        num_devices = GetNumDevices()
        if num_devices == 0:
            print("未发现CP2112设备")
            return
        
        print(f"使用CP2112设备 0")
        
        # 连接设备
        device = HidSmbusDevice()
        result = device.open(0)
        
        if result != 0:
            print(f"设备连接失败，错误代码: {result}")
            return
        
        print("设备连接成功")
        
        # 配置SMBus (降低速度以提高兼容性)
        bitrate = 100000  # 100kHz
        timeout = 1000    # 1秒
        retry_times = 1   # 减少重试次数提高扫描速度
        
        device.set_smbus_config(bitrate, timeout, retry_times, False, timeout)
        print(f"SMBus配置: {bitrate}Hz, 超时{timeout}ms")
        
        # 扫描总线
        found_devices = scan_i2c_bus(device, delay=0.005)
        
        # 显示结果
        display_scan_results(found_devices)
        display_address_map(found_devices)
        
        # 对找到的设备进行简单测试
        if found_devices:
            print("\n设备测试:")
            for addr in found_devices[:3]:  # 只测试前3个设备
                quick_device_test(device, addr)
        
        device.close()
        print("\n扫描完成")
        
    except Exception as e:
        print(f"扫描过程中出错: {e}")
    
    finally:
        try:
            device.close()
        except:
            pass

if __name__ == "__main__":
    main()
    input("\n按回车键退出...")
