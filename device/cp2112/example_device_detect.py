#!/usr/bin/env python3
"""
CP2112设备检测示例
检测并显示连接的CP2112设备信息
"""

import sys
import os

# 添加DLL路径 - 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release", "x64")
sys.path.append(dll_path)
os.chdir(dll_path)

try:
    from SLABHIDtoSMBUS import *
except ImportError as e:
    print(f"导入错误: {e}")
    print("请确保SLABHIDtoSMBUS.py和相关DLL文件在正确路径下")
    sys.exit(1)

def detect_devices():
    """检测连接的CP2112设备"""
    try:
        num_devices = GetNumDevices()
        print(f"检测到 {num_devices} 个CP2112设备\n")
        
        if num_devices == 0:
            print("未发现CP2112设备，请检查:")
            print("1. USB连接是否正常")
            print("2. 设备驱动是否已安装")
            print("3. 设备是否被其他程序占用")
            return
        
        for i in range(num_devices):
            print(f"=== 设备 {i} ===")
            
            try:
                # 获取设备属性
                vid, pid, release_num = GetAttributes(i)
                print(f"VID: 0x{vid:04X}")
                print(f"PID: 0x{pid:04X}")
                print(f"发布版本: 0x{release_num:04X}")
                
                # 获取设备字符串
                serial = GetString(i, HID_SMBUS.SERIAL_STR)
                manufacturer = GetString(i, HID_SMBUS.MANUFACTURER_STR)
                product = GetString(i, HID_SMBUS.PRODUCT_STR)
                
                print(f"序列号: {serial}")
                print(f"制造商: {manufacturer}")
                print(f"产品名: {product}")
                
                # 检查设备是否已被打开
                is_open = IsOpened(i)
                print(f"设备状态: {'已打开' if is_open else '可用'}")
                
            except Exception as e:
                print(f"获取设备 {i} 信息时出错: {e}")
            
            print()
        
        # 显示库版本信息
        try:
            lib_version = GetLibraryVersion()
            hid_lib_version = GetHidLibraryVersion()
            print(f"SMBus库版本: {lib_version}")
            print(f"HID库版本: {hid_lib_version}")
        except:
            print("无法获取库版本信息")
            
    except Exception as e:
        print(f"设备检测失败: {e}")

def test_device_connection():
    """测试设备连接"""
    try:
        num_devices = GetNumDevices()
        if num_devices == 0:
            print("没有可用的CP2112设备")
            return False
        
        print("测试连接第一个设备...")
        device = HidSmbusDevice()
        
        # 尝试打开设备
        result = device.open(0)
        if result == 0:  # 成功
            print("✓ 设备连接成功")
            
            # 获取设备配置
            try:
                config = device.get_smbus_config()
                print(f"当前配置:")
                print(f"  比特率: {config[0]} Hz")
                print(f"  超时: {config[1]} ms")
                print(f"  重试次数: {config[2]}")
                print(f"  SCL低电平超时: {config[3]}")
                print(f"  响应超时: {config[4]} ms")
            except:
                print("无法获取设备配置")
            
            device.close()
            print("✓ 设备已断开")
            return True
        else:
            print(f"✗ 设备连接失败，错误代码: {result}")
            return False
            
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("CP2112设备检测工具")
    print("=" * 40)
    
    detect_devices()
    
    print("\n" + "=" * 40)
    test_device_connection()
    
    input("\n按回车键退出...")
