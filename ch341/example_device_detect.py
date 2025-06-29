#!/usr/bin/env python3
"""
CH341设备检测示例
检测并显示连接的CH341设备信息
"""

import sys
import os
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

def get_device_count(ch341):
    """获取设备数量 - 通过设备名称检测实际存在的设备"""
    try:
        # CH341没有GetDeviceCount函数，通过检测设备名称来确定设备数量
        max_devices = 16  # CH341_MAX_NUMBER定义的最大设备数
        count = 0
        
        for i in range(max_devices):
            try:
                # 首先尝试打开设备
                device_handle = ch341.CH341OpenDevice(i)
                if device_handle:
                    try:
                        # 获取设备名称来确认设备真实存在
                        name_ptr = ch341.CH341GetDeviceName(i)
                        if name_ptr:
                            # 将指针转换为字符串
                            device_name = string_at(name_ptr).decode('utf-8', errors='ignore')
                            # 如果设备名称不为空且不是默认值，则认为设备存在
                            if device_name and device_name.strip() and device_name != "未知设备":
                                count += 1
                            else:
                                # 设备名称为空，设备不存在
                                ch341.CH341CloseDevice(i)
                                break
                        else:
                            # 无法获取设备名称，设备不存在
                            ch341.CH341CloseDevice(i)
                            break
                    finally:
                        ch341.CH341CloseDevice(i)
                else:
                    # 无法打开设备，没有更多设备
                    break
            except:
                # 出现异常，停止检测
                break
        
        return count
    except Exception as e:
        print(f"获取设备数量失败: {e}")
        return 0

def get_library_version(ch341):
    """获取库版本信息"""
    try:
        version = ch341.CH341GetVersion()
        return version
    except Exception as e:
        print(f"获取库版本失败: {e}")
        return 0

def get_driver_version(ch341):
    """获取驱动版本信息"""
    try:
        version = ch341.CH341GetDrvVersion()
        return version
    except Exception as e:
        print(f"获取驱动版本失败: {e}")
        return 0

def get_chip_version(ch341, device_index):
    """获取芯片版本信息 - 需要先打开设备"""
    try:
        # 先尝试打开设备
        device_handle = ch341.CH341OpenDevice(device_index)
        if not device_handle:
            return 0
        
        try:
            version = ch341.CH341GetVerIC(device_index)
            return version
        finally:
            ch341.CH341CloseDevice(device_index)
            
    except Exception as e:
        print(f"获取芯片版本失败: {e}")
        return 0

def get_device_name(ch341, device_index):
    """获取设备名称 - 需要先打开设备"""
    try:
        # 先尝试打开设备
        device_handle = ch341.CH341OpenDevice(device_index)
        if not device_handle:
            return "设备打开失败"
        
        try:
            # CH341GetDeviceName返回字符串指针
            name_ptr = ch341.CH341GetDeviceName(device_index)
            if name_ptr:
                # 将指针转换为字符串
                name = string_at(name_ptr).decode('utf-8', errors='ignore')
                return name
            return "未知设备"
        finally:
            ch341.CH341CloseDevice(device_index)
            
    except Exception as e:
        print(f"获取设备名称失败: {e}")
        return "获取失败"

def detect_devices():
    """检测连接的CH341设备"""
    print("正在检测CH341设备...")
    
    # 加载DLL
    ch341 = load_ch341_dll()
    if not ch341:
        return False
    
    try:
        # 获取设备数量
        device_count = get_device_count(ch341)
        print(f"\n检测到 {device_count} 个CH341设备\n")
        
        if device_count == 0:
            print("未发现CH341设备，请检查:")
            print("1. USB连接是否正常")
            print("2. 设备驱动是否已安装")
            print("3. 设备是否被其他程序占用")
            print("4. 确认设备型号 (CH341, CH341A, CH341T)")
            print("5. 从WCH官网下载最新驱动")
            return False
        
        # 显示库和驱动版本信息
        lib_version = get_library_version(ch341)
        drv_version = get_driver_version(ch341)
        print("=== 版本信息 ===")
        print(f"DLL库版本: 0x{lib_version:08X}")
        print(f"驱动版本: 0x{drv_version:08X}")
        print()
        
        # 遍历每个设备
        for i in range(device_count):
            print(f"=== 设备 {i} ===")
            
            try:
                # 尝试打开设备获取信息
                device_handle = ch341.CH341OpenDevice(i)
                if device_handle:
                    try:
                        # 获取设备名称
                        name_ptr = ch341.CH341GetDeviceName(i)
                        if name_ptr:
                            device_name = string_at(name_ptr).decode('utf-8', errors='ignore')
                        else:
                            device_name = ""
                        
                        # 检查设备名称是否有效
                        if not device_name or not device_name.strip():
                            print("⚠ 设备名称为空，可能是虚拟设备或驱动问题")
                            ch341.CH341CloseDevice(i)
                            print("跳过此设备\n")
                            continue
                            
                        print("✓ 设备打开成功")
                        print(f"设备名称: {device_name}")
                        
                        # 获取芯片版本
                        chip_version = ch341.CH341GetVerIC(i)
                        chip_type = "未知"
                        if chip_version == 0x20:
                            chip_type = "CH341A"
                        elif chip_version == 0x30:
                            chip_type = "CH341A3"
                        elif chip_version > 0:
                            chip_type = f"CH341系列 (0x{chip_version:02X})"
                        
                        print(f"芯片版本: 0x{chip_version:02X} ({chip_type})")
                        
                        # 获取设备状态
                        status = c_ulong()
                        if ch341.CH341GetStatus(i, byref(status)):
                            print(f"设备状态: 0x{status.value:08X}")
                            
                            # 解析状态位
                            print("状态解析:")
                            print(f"  D7-D0数据: 0x{status.value & 0xFF:02X}")
                            print(f"  ERR#: {'高' if status.value & 0x100 else '低'}")
                            print(f"  PEMP: {'高' if status.value & 0x200 else '低'}")
                            print(f"  INT#: {'高' if status.value & 0x400 else '低'}")
                            print(f"  SLCT: {'高' if status.value & 0x800 else '低'}")
                            print(f"  SDA: {'高' if status.value & 0x800000 else '低'}")
                        else:
                            print("无法获取设备状态")
                        
                        # 测试I2C功能
                        print("\n测试I2C功能:")
                        test_i2c_modes = [
                            (0, "20KHz (慢速)"),
                            (1, "100KHz (标准)"),
                            (2, "400KHz (快速)"),
                            (3, "750KHz (高速)")
                        ]
                        
                        for mode, desc in test_i2c_modes:
                            if ch341.CH341SetStream(i, mode):
                                print(f"  ✓ {desc} - 支持")
                            else:
                                print(f"  ✗ {desc} - 不支持")
                        
                        # 重置为默认模式
                        ch341.CH341SetStream(i, 1)  # 100KHz标准模式
                        
                    except Exception as e:
                        print(f"测试设备功能时出错: {e}")
                    finally:
                        # 确保关闭设备
                        ch341.CH341CloseDevice(i)
                        print("✓ 设备已关闭")
                else:
                    print("✗ 设备打开失败")
                    print("  可能原因: 设备被占用或权限不足")
                    
            except Exception as e:
                print(f"操作设备 {i} 时出错: {e}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"设备检测过程中出错: {e}")
        return False

def test_device_connection():
    """测试设备连接和基本功能"""
    print("测试设备连接...")
    
    # 加载DLL
    ch341 = load_ch341_dll()
    if not ch341:
        return False
    
    try:
        device_count = get_device_count(ch341)
        if device_count == 0:
            print("没有可用的CH341设备进行连接测试")
            return False
        
        print(f"测试第一个设备 (设备 0)...")
        
        # 打开设备
        device_handle = ch341.CH341OpenDevice(0)
        if not device_handle:
            print("✗ 无法打开设备")
            return False
        
        # 验证设备名称
        try:
            name_ptr = ch341.CH341GetDeviceName(0)
            if name_ptr:
                device_name = string_at(name_ptr).decode('utf-8', errors='ignore')
            else:
                device_name = ""
            
            if not device_name or not device_name.strip():
                print("✗ 设备名称为空，可能不是有效的CH341设备")
                ch341.CH341CloseDevice(0)
                return False
                
            print(f"✓ 设备连接成功: {device_name}")
        except Exception as e:
            print(f"✗ 验证设备名称失败: {e}")
            ch341.CH341CloseDevice(0)
            return False
        
        try:
            # 测试设备重置
            print("测试设备重置...")
            if ch341.CH341ResetDevice(0):
                print("✓ 设备重置成功")
            else:
                print("✗ 设备重置失败")
            
            # 测试缓冲区操作
            print("测试缓冲区...")
            if ch341.CH341FlushBuffer(0):
                print("✓ 缓冲区清空成功")
            else:
                print("✗ 缓冲区清空失败")
            
            # 测试I2C流模式设置
            print("测试I2C流模式...")
            if ch341.CH341SetStream(0, 1):  # 100KHz标准模式
                print("✓ I2C流模式设置成功 (100KHz)")
                
                # 简单的I2C扫描测试
                print("执行简单I2C扫描...")
                test_addresses = [0x48, 0x50, 0x68]  # 常见设备地址
                
                for addr in test_addresses:
                    try:
                        # 创建写缓冲区
                        write_buf = (c_ubyte * 1)()
                        write_buf[0] = (addr << 1) | 0  # 写地址
                        
                        # 尝试I2C通信
                        result = ch341.CH341StreamI2C(0, 1, write_buf, 0, None)
                        status = "有响应" if result else "无响应"
                        print(f"  地址 0x{addr:02X}: {status}")
                    except Exception as e:
                        print(f"  地址 0x{addr:02X}: 测试失败 ({e})")
            else:
                print("✗ I2C流模式设置失败")
            
            return True
            
        except Exception as e:
            print(f"设备功能测试失败: {e}")
            return False
        
        finally:
            # 确保关闭设备
            ch341.CH341CloseDevice(0)
            print("✓ 设备连接已断开")
    
    except Exception as e:
        print(f"连接测试失败: {e}")
        return False


if __name__ == "__main__":
    print("CH341设备检测工具")
    print("=" * 40)
    print("支持检测: CH341, CH341A, CH341T等型号")
    print()
    
    # 检测设备
    detect_success = detect_devices()
    
    if detect_success:
        print("\n" + "=" * 40)
        # 测试连接
        test_device_connection()
    
    
    input("\n按回车键退出...")
