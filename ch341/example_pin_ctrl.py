#!/usr/bin/env python3
"""
CH341引脚直接控制示例
提供对CH341所有可控引脚的直接操作功能
"""

import sys
import os
import time
from ctypes import *

# 添加DLL路径 - 使用相对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
dll_path = os.path.join(script_dir, "Release")

# CH341引脚状态位定义 (来自头文件)
mStateBitERR = 0x00000100      # ERR#引脚状态
mStateBitPEMP = 0x00000200     # PEMP引脚状态  
mStateBitINT = 0x00000400      # INT#引脚状态
mStateBitSLCT = 0x00000800     # SLCT引脚状态
mStateBitWAIT = 0x00002000     # WAIT#引脚状态
mStateBitDATAS = 0x00004000    # DATAS#/read#引脚状态
mStateBitADDRS = 0x00008000    # ADDRS#/ADDR/ALE引脚状态
mStateBitRESET = 0x00010000    # RESET#引脚状态
mStateBitWRITE = 0x00020000    # WRITE#引脚状态
mStateBitSCL = 0x00400000      # SCL引脚状态
mStateBitSDA = 0x00800000      # SDA引脚状态

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

class CH341PinController:
    """CH341引脚控制器"""
    
    def __init__(self, ch341, device_index):
        self.ch341 = ch341
        self.device_index = device_index
        self.device_opened = False
        
    def open_device(self):
        """打开设备"""
        if not self.device_opened:
            handle = self.ch341.CH341OpenDevice(self.device_index)
            if handle:
                self.device_opened = True
                print(f"设备 {self.device_index} 已打开")
                return True
            else:
                print(f"无法打开设备 {self.device_index}")
                return False
        return True
    
    def close_device(self):
        """关闭设备"""
        if self.device_opened:
            self.ch341.CH341CloseDevice(self.device_index)
            self.device_opened = False
            print(f"设备 {self.device_index} 已关闭")
    
    def read_all_pins(self):
        """读取所有引脚状态"""
        if not self.device_opened:
            print("设备未打开")
            return None
            
        try:
            status = c_ulong()
            if self.ch341.CH341GetStatus(self.device_index, byref(status)):
                return status.value
            else:
                print("读取引脚状态失败")
                return None
        except Exception as e:
            print(f"读取引脚状态出错: {e}")
            return None
    
    def get_input_pins(self):
        """获取输入引脚状态 (更高效的读取方式)"""
        if not self.device_opened:
            print("设备未打开")
            return None
            
        try:
            status = c_ulong()
            if self.ch341.CH341GetInput(self.device_index, byref(status)):
                return status.value
            else:
                print("读取输入引脚失败")
                return None
        except Exception as e:
            print(f"读取输入引脚出错: {e}")
            return None
    
    def set_output_pins(self, enable_mask, direction_mask, data_mask):
        """设置输出引脚
        enable_mask: 使能掩码 (哪些位有效)
        direction_mask: 方向掩码 (1=输出, 0=输入)
        data_mask: 数据掩码 (1=高电平, 0=低电平)
        """
        if not self.device_opened:
            print("设备未打开")
            return False
            
        try:
            result = self.ch341.CH341SetOutput(
                self.device_index,
                enable_mask,
                direction_mask, 
                data_mask
            )
            return result
        except Exception as e:
            print(f"设置输出引脚出错: {e}")
            return False
    
    def set_d5_d0_pins(self, direction_mask, data_mask):
        """设置D5-D0引脚 (更简单的方式)
        direction_mask: 方向掩码 (1=输出, 0=输入)
        data_mask: 数据掩码 (1=高电平, 0=低电平)
        """
        if not self.device_opened:
            print("设备未打开")
            return False
            
        try:
            result = self.ch341.CH341Set_D5_D0(
                self.device_index,
                direction_mask & 0x3F,  # 只有D5-D0有效
                data_mask & 0x3F
            )
            return result
        except Exception as e:
            print(f"设置D5-D0引脚出错: {e}")
            return False
    
    def display_pin_status(self, status):
        """显示引脚状态"""
        if status is None:
            print("无法获取引脚状态")
            return
            
        print(f"引脚状态: 0x{status:08X}")
        print("=" * 50)
        
        # 数据引脚 D7-D0
        print("数据引脚 (D7-D0):")
        for i in range(8):
            bit_val = (status >> i) & 1
            print(f"  D{i}: {'高' if bit_val else '低'}")
        
        print("\n控制引脚:")
        control_pins = [
            (8, "ERR#", mStateBitERR),      # in
            (9, "PEMP", mStateBitPEMP),     # in
            (10, "INT#", mStateBitINT),     # in
            (11, "SLCT", mStateBitSLCT),    # in
            (13, "WAIT#", mStateBitWAIT),   # in
            (14, "DATAS#", mStateBitDATAS), # out
            (15, "ADDRS#", mStateBitADDRS), # out
            (16, "RESET#", mStateBitRESET), # out
            (17, "WRITE#", mStateBitWRITE), # out
            (22, "SCL", mStateBitSCL),      # in
            (23, "SDA", mStateBitSDA)       # out
        ]
        
        for bit_pos, pin_name, bit_mask in control_pins:
            bit_val = (status & bit_mask) != 0
            print(f"  {pin_name}: {'高' if bit_val else '低'}")

def test_data_pins(controller):
    """测试数据引脚D7-D0"""
    print("\n" + "=" * 50)
    print("测试数据引脚 D7-D0")
    print("=" * 50)
    
    # 设置所有数据引脚为输出
    direction_mask = 0xFF  # D7-D0都设为输出
    enable_mask = 0x0F     # 使能D7-D0控制
    
    print("设置D7-D0为输出模式...")
    
    # 测试不同的数据模式
    test_patterns = [
        (0x00, "全部低电平"),
        (0xFF, "全部高电平"), 
        (0xAA, "交替模式 (10101010)"),
        (0x55, "交替模式 (01010101)"),
        (0x0F, "低4位高电平"),
        (0xF0, "高4位高电平")
    ]
    
    for data_pattern, description in test_patterns:
        print(f"\n设置模式: {description} (0x{data_pattern:02X})")
        
        if controller.set_output_pins(enable_mask, direction_mask, data_pattern):
            print("设置成功")
            time.sleep(0.5)  # 等待稳定
            
            # 读取状态验证
            status = controller.read_all_pins()
            if status is not None:
                actual_data = status & 0xFF
                print(f"读取到的数据: 0x{actual_data:02X}")
                if actual_data == data_pattern:
                    print("✓ 验证成功")
                else:
                    print("✗ 验证失败")
        else:
            print("设置失败")
        
        time.sleep(1)

def test_d5_d0_pins(controller):
    """测试D5-D0引脚控制"""
    print("\n" + "=" * 50)
    print("测试D5-D0引脚控制")
    print("=" * 50)
    
    # 设置D5-D0为输出
    direction_mask = 0x3F  # D5-D0都设为输出
    
    print("设置D5-D0为输出模式...")
    
    # 测试单个引脚
    for i in range(6):
        data_pattern = 1 << i
        print(f"\n设置D{i}为高电平 (模式: 0x{data_pattern:02X})")
        
        if controller.set_d5_d0_pins(direction_mask, data_pattern):
            time.sleep(0.5)
            
            # 读取验证
            status = controller.get_input_pins()
            if status is not None:
                actual_data = status & 0x3F
                print(f"读取到的D5-D0: 0x{actual_data:02X}")
        
        time.sleep(0.8)
    
    # 清零所有引脚
    print("\n清零所有D5-D0引脚")
    controller.set_d5_d0_pins(direction_mask, 0x00)

def test_pin_scanning(controller):
    """引脚扫描测试"""
    print("\n" + "=" * 50)
    print("引脚状态扫描测试")
    print("=" * 50)
    
    print("连续读取引脚状态 (按Ctrl+C停止)...")
    
    try:
        count = 0
        while count < 10:  # 限制扫描次数
            status = controller.read_all_pins()
            if status is not None:
                print(f"\n扫描 #{count + 1}:")
                controller.display_pin_status(status)
            
            time.sleep(2)
            count += 1
            
    except KeyboardInterrupt:
        print("\n用户停止扫描")

def interactive_pin_control(controller):
    """交互式引脚控制"""
    print("\n" + "=" * 50)
    print("交互式引脚控制")
    print("=" * 50)
    
    while True:
        print("\n选择操作:")
        print("1. 读取所有引脚状态")
        print("2. 设置D7-D0引脚")
        print("3. 设置D5-D0引脚")
        print("4. 连续监控引脚状态")
        print("5. 返回主菜单")
        
        choice = input("请选择 (1-5): ").strip()
        
        if choice == "1":
            status = controller.read_all_pins()
            controller.display_pin_status(status)
            
        elif choice == "2":
            try:
                data = input("输入D7-D0数据值 (十六进制，如 FF): ").strip()
                data_val = int(data, 16) & 0xFF
                
                enable_mask = 0x0F  # 使能D7-D0
                direction_mask = 0xFF  # 设为输出
                
                if controller.set_output_pins(enable_mask, direction_mask, data_val):
                    print(f"成功设置D7-D0为: 0x{data_val:02X}")
                else:
                    print("设置失败")
            except ValueError:
                print("输入格式错误")
                
        elif choice == "3":
            try:
                data = input("输入D5-D0数据值 (十六进制，如 3F): ").strip()
                data_val = int(data, 16) & 0x3F
                
                direction_mask = 0x3F  # 设为输出
                
                if controller.set_d5_d0_pins(direction_mask, data_val):
                    print(f"成功设置D5-D0为: 0x{data_val:02X}")
                else:
                    print("设置失败")
            except ValueError:
                print("输入格式错误")
                
        elif choice == "4":
            test_pin_scanning(controller)
            
        elif choice == "5":
            break
            
        else:
            print("无效选择")

def enable_p8_p9_output(controller):
    """使能P8和P9引脚输出"""
    enable_mask = 0x2  # 位15-位8控制有效(Dir only)
    direction_mask = 0xC3 << 8  # 位15-位8控制方向
    # data_pattern = 0xC3 << 8  # bit8高电平 bit9高电平 bit14高电平 bit15高电平
    data_pattern = 0x0

    if controller.set_output_pins(enable_mask, direction_mask, data_pattern):
        print("P8和P9引脚输出使能成功")
    else:
        print("P8和P9引脚输出使能失败")

def toggle_p8(controller):
    """切换P8引脚状态"""
    enable_mask = 0x1  # 位15-位8控制有效(Data only)
    status = controller.read_all_pins()
    data_pattern = status ^ (0x01 << 8)  # 切换P8引脚状态

    if controller.set_output_pins(enable_mask, 0, data_pattern):
        print("设置成功")
        time.sleep(0.5)  # 等待稳定
        
        # 读取状态验证（不是必须的）
        status = controller.read_all_pins()
        if status == data_pattern:
            print("✓ 验证成功")
        else:
            print("✗ 验证失败")
    else:
        print("设置失败")

def toggle_p9(controller):
    """切换P9引脚状态"""
    enable_mask = 0x1  # 位15-位8控制有效(Data only)
    status = controller.read_all_pins()
    data_pattern = status ^ (0x01 << 9)  # 切换P9引脚状态

    if controller.set_output_pins(enable_mask, 0, data_pattern):
        print("设置成功")
        time.sleep(0.5)  # 等待稳定
        
        # 读取状态验证（不是必须的）
        status = controller.read_all_pins()
        if status == data_pattern:
            print("✓ 验证成功")
        else:
            print("✗ 验证失败")
    else:
        print("设置失败")

def main():
    """主函数"""
    print("CH341引脚直接控制工具")
    print("=" * 40)
    
    # 加载DLL
    ch341 = load_ch341_dll()
    if not ch341:
        input("按回车键退出...")
        return
    
    # 查找设备
    device_index = find_available_device(ch341)
    if device_index is None:
        print("未找到可用的CH341设备")
        input("按回车键退出...")
        return
    
    # 创建控制器
    controller = CH341PinController(ch341, device_index)
    
    try:
        if not controller.open_device():
            input("按回车键退出...")
            return
        
        # 显示初始状态
        print("\n初始引脚状态:")
        status = controller.read_all_pins()
        controller.display_pin_status(status)
        
        while True:
            print("\n" + "=" * 50)
            print("CH341引脚控制菜单")
            print("=" * 50)
            print("1. 测试数据引脚 (D7-D0)")
            print("2. 测试D5-D0引脚控制")
            print("3. 引脚状态扫描")
            print("4. 交互式引脚控制")
            print("5. 显示当前引脚状态")
            print("6. 退出")
            print("7. 使能P8和P9引脚输出")
            print("8. 切换P8引脚状态")
            print("9. 切换P9引脚状态")

            choice = input("\n请选择 (1-9): ").strip()

            if choice == "1":
                test_data_pins(controller)
            elif choice == "2":
                test_d5_d0_pins(controller)
            elif choice == "3":
                test_pin_scanning(controller)
            elif choice == "4":
                interactive_pin_control(controller)
            elif choice == "5":
                status = controller.read_all_pins()
                controller.display_pin_status(status)
            elif choice == "6":
                break
            elif choice == "7":
                enable_p8_p9_output(controller)
            elif choice == "8":
                toggle_p8(controller)
            elif choice == "9":
                toggle_p9(controller)
            else:
                print("无效选择，请重新输入")
    
    except Exception as e:
        print(f"程序运行出错: {e}")
    
    finally:
        controller.close_device()
    
    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
