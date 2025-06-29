#!/usr/bin/env python3
"""
CH341 I2C设备扫描示例
通过CH341设备扫描I2C总线上的所有设备
"""

import sys
import os
import time
from ctypes import *

# 添加DLL路径 - 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release")

def load_ch341_dll():
    """加载CH341 DLL库"""
    dll_files = ["CH341DLLA64.DLL", "CH341DLL.DLL"]
    
    for dll_file in dll_files:
        try:
            dll_full_path = os.path.join(dll_path, dll_file)
            ch341 = windll.LoadLibrary(dll_full_path)
            print(f"成功加载: {dll_file}")
            return ch341
        except Exception as e:
            print(f"尝试加载 {dll_file} 失败: {e}")
            continue
    
    print("错误: 无法找到CH341 DLL文件")
    print("请确保以下文件存在于Release目录:")
    for dll_file in dll_files:
        print(f"  - {dll_file}")
    return None

def find_available_device(ch341):
    """查找可用的CH341设备"""
    max_devices = 16
    
    for i in range(max_devices):
        try:
            device_handle = ch341.CH341OpenDevice(i)
            if device_handle:
                # 验证设备名称
                name_ptr = ch341.CH341GetDeviceName(i)
                if name_ptr:
                    device_name = string_at(name_ptr).decode('utf-8', errors='ignore')
                    if device_name and device_name.strip():
                        print(f"找到设备 {i}: {device_name}")
                        ch341.CH341CloseDevice(i)
                        return i
                ch341.CH341CloseDevice(i)
        except:
            continue
    
    return None

def setup_i2c_mode(ch341, device_index, speed_mode=1):
    """设置I2C模式
    speed_mode: 0=20KHz, 1=100KHz, 2=400KHz, 3=750KHz
    """
    speed_names = {
        0: "20KHz (慢速)",
        1: "100KHz (标准)", 
        2: "400KHz (快速)",
        3: "750KHz (高速)"
    }
    
    try:
        if ch341.CH341SetStream(device_index, speed_mode):
            print(f"I2C模式设置成功: {speed_names.get(speed_mode, f'模式{speed_mode}')}")
            return True
        else:
            print(f"I2C模式设置失败: {speed_names.get(speed_mode, f'模式{speed_mode}')}")
            return False
    except Exception as e:
        print(f"设置I2C模式时出错: {e}")
        return False

def scan_i2c_address_simple(ch341, device_index, address):
    """简单的I2C地址扫描 - 使用CH341ReadI2C"""
    try:
        # 尝试从地址0读取一个字节
        data_byte = c_ubyte()
        result = ch341.CH341ReadI2C(device_index, address, 0, byref(data_byte))
        return result
    except:
        return False

def scan_i2c_address_stream(ch341, device_index, address):
    """使用Stream方式扫描I2C地址 - 通过读取默认寄存器判断设备存在"""
    try:
        # 方法1: 尝试读取寄存器0x00 (大多数设备的默认寄存器)
        write_buf = (c_ubyte * 1)()
        read_buf = (c_ubyte * 1)()
        write_buf[0] = 0x00  # 寄存器地址0x00
        
        # 先写寄存器地址，再读取数据
        write_result = ch341.CH341StreamI2C(device_index, 1, write_buf, 0, None)
        if write_result:
            # 读取一个字节数据
            read_result = ch341.CH341StreamI2C(device_index, 0, None, 1, read_buf)
            if read_result:
                # 检查读取到的数据是否有效（不是全0xFF或全0x00等无效值）
                data_value = read_buf[0]
                # 认为0xFF通常表示设备未响应，0x00可能是有效数据
                if data_value != 0xFF:
                    return True
        
        return False
    except Exception as e:
        try:
            # 方法2: 如果方法1失败，尝试只发送设备地址进行探测
            # addr_buf = (c_ubyte * 1)()
            # addr_buf[0] = (address << 1) | 0  # 写地址
            # return ch341.CH341StreamI2C(device_index, 1, addr_buf, 0, None)

            # 方法3: 备用方案 - 使用简单的地址探测
            addr_buf = (c_ubyte * 1)()
            addr_buf[0] = (address << 1) | 1  # 读地址
            return ch341.CH341StreamI2C(device_index, 0, None, 1, (c_ubyte * 1)())
        except:
            return False

def scan_i2c_bus(ch341, device_index, scan_mode="stream", start_addr=0x08, end_addr=0x77):
    """扫描I2C总线
    scan_mode: "simple" 使用CH341ReadI2C, "stream" 使用CH341StreamI2C
    start_addr: 扫描起始地址 (默认0x08，避免保留地址)
    end_addr: 扫描结束地址 (默认0x77，避免保留地址)
    """
    print(f"\n开始I2C扫描 (模式: {scan_mode})")
    print(f"扫描范围: 0x{start_addr:02X} - 0x{end_addr:02X}")
    print("=" * 50)
    
    found_devices = []
    scan_function = scan_i2c_address_stream if scan_mode == "stream" else scan_i2c_address_simple
    
    # 打印表头
    print("     ", end="")
    for i in range(16):
        print(f" {i:X}", end="")
    print()
    
    for row in range(0, 8):  # 0x00-0x7F
        print(f"0x{row}0:", end="")
        
        for col in range(16):
            addr = row * 16 + col
            
            if addr < start_addr or addr > end_addr:
                print(" .", end="")
                continue
            
            try:
                # 扫描地址
                if scan_function(ch341, device_index, addr):
                    print(f" {addr:02X}", end="")
                    found_devices.append(addr)
                else:
                    print(" --", end="")
                
                # 添加小延时避免总线过于繁忙
                time.sleep(0.01)
                
            except Exception as e:
                print(" ??", end="")
        
        print()  # 换行
    
    print("=" * 50)
    
    if found_devices:
        print(f"发现 {len(found_devices)} 个I2C设备:")
        for addr in found_devices:
            device_type = get_device_type_hint(addr)
            print(f"  0x{addr:02X} ({addr:3d}) - {device_type}")
    else:
        print("未发现任何I2C设备")
        print("可能原因:")
        print("1. 没有连接I2C设备")
        print("2. I2C设备地址不在扫描范围内")
        print("3. I2C总线连接问题(检查SDA/SCL)")
        print("4. 设备需要特殊的初始化")
    
    return found_devices

def get_device_type_hint(address):
    """根据I2C地址提供设备类型提示"""
    device_hints = {
        0x20: "PCF8574 I/O扩展器",
        0x21: "PCF8574 I/O扩展器",
        0x22: "PCF8574 I/O扩展器",
        0x23: "PCF8574 I/O扩展器",
        0x24: "PCF8574 I/O扩展器",
        0x25: "PCF8574 I/O扩展器",
        0x26: "PCF8574 I/O扩展器",
        0x27: "PCF8574 I/O扩展器",
        0x38: "PCF8574A I/O扩展器",
        0x39: "PCF8574A I/O扩展器",
        0x3A: "PCF8574A I/O扩展器",
        0x3B: "PCF8574A I/O扩展器",
        0x3C: "PCF8574A I/O扩展器",
        0x3D: "PCF8574A I/O扩展器",
        0x3E: "PCF8574A I/O扩展器",
        0x3F: "PCF8574A I/O扩展器",
        0x40: "INA226/HTU21D/Si7021",
        0x41: "INA226",
        0x42: "INA226",
        0x43: "INA226",
        0x44: "INA226/SHT30",
        0x45: "INA226/SHT30",
        0x48: "ADS1115/PCF8591/TMP102",
        0x49: "ADS1115/TSL2561",
        0x4A: "ADS1115",
        0x4B: "ADS1115",
        0x50: "EEPROM 24C01/24C02",
        0x51: "EEPROM 24C01/24C02",
        0x52: "EEPROM 24C01/24C02",
        0x53: "EEPROM 24C01/24C02",
        0x54: "EEPROM 24C01/24C02",
        0x55: "EEPROM 24C01/24C02",
        0x56: "EEPROM 24C01/24C02",
        0x57: "EEPROM 24C01/24C02",
        0x68: "DS1307 RTC/MPU6050",
        0x69: "MPU6050",
        0x6A: "L3GD20H",
        0x6B: "L3GD20H",
        0x76: "BMP280/BME280",
        0x77: "BMP280/BME280",
    }
    
    return device_hints.get(address, "未知设备")

def test_device_communication(ch341, device_index, address):
    """测试与特定设备的通信"""
    print(f"\n测试与设备 0x{address:02X} 的通信:")
    print("-" * 30)
    
    try:
        # 测试读取
        print("测试读取操作...")
        data_byte = c_ubyte()
        if ch341.CH341ReadI2C(device_index, address, 0, byref(data_byte)):
            print(f"  成功读取: 0x{data_byte.value:02X}")
        else:
            print("  读取失败")
        
        # 测试写入 (谨慎操作，可能影响设备)
        print("测试写入操作...")
        if ch341.CH341WriteI2C(device_index, address, 0, 0x00):
            print("  写入测试成功")
        else:
            print("  写入测试失败")
            
    except Exception as e:
        print(f"  通信测试出错: {e}")

def main():
    """主函数"""
    print("CH341 I2C总线扫描工具")
    print("=" * 40)
    
    # 加载DLL
    ch341 = load_ch341_dll()
    if not ch341:
        input("按回车键退出...")
        return
    
    # 查找可用设备
    device_index = find_available_device(ch341)
    if device_index is None:
        print("未找到可用的CH341设备")
        input("按回车键退出...")
        return
    
    try:
        # 打开设备
        device_handle = ch341.CH341OpenDevice(device_index)
        if not device_handle:
            print("无法打开CH341设备")
            input("按回车键退出...")
            return
        
        print(f"成功打开设备 {device_index}")
        
        # 设置不同的I2C速度进行扫描
        speeds = [
            (1, "100KHz (标准)"),
            # (2, "400KHz (快速)"),
            # (0, "20KHz (慢速)"),
            # (3, "750KHz (高速)")
        ]
        
        all_results = {}
        
        for speed_mode, speed_name in speeds:
            print(f"\n{'=' * 60}")
            print(f"使用 {speed_name} 速度扫描")
            print(f"{'=' * 60}")
            
            if setup_i2c_mode(ch341, device_index, speed_mode):
                # 使用stream模式扫描
                found_devices = scan_i2c_bus(ch341, device_index, "stream")
                all_results[speed_name] = found_devices
                
                # 如果找到设备，测试第一个设备的通信
                if found_devices:
                    test_device_communication(ch341, device_index, found_devices[0])
            else:
                print(f"无法设置 {speed_name} 模式")
        
        # 总结扫描结果
        print(f"\n{'=' * 60}")
        print("扫描结果总结")
        print(f"{'=' * 60}")
        
        all_found = set()
        for speed_name, devices in all_results.items():
            if devices:
                print(f"{speed_name}: 发现 {len(devices)} 个设备")
                for addr in devices:
                    print(f"  0x{addr:02X}")
                    all_found.add(addr)
            else:
                print(f"{speed_name}: 未发现设备")
        
        if all_found:
            print(f"\n总共发现 {len(all_found)} 个唯一设备:")
            for addr in sorted(all_found):
                device_type = get_device_type_hint(addr)
                print(f"  0x{addr:02X} ({addr:3d}) - {device_type}")
        else:
            print("\n所有速度下均未发现I2C设备")
        
    except Exception as e:
        print(f"扫描过程中出错: {e}")
    
    finally:
        # 确保关闭设备
        try:
            ch341.CH341CloseDevice(device_index)
            print(f"\n设备 {device_index} 已关闭")
        except:
            pass
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
