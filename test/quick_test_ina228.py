#!/usr/bin/env python3
"""
INA228Module 快速测试脚本

用于快速验证 INA228Module 的基本功能
"""

import sys
import os
import time

# 添加框架路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.adapters import create_adapter
from framework.modules.ina228_module import INA228Module


def quick_test():
    """快速测试 INA228Module"""
    print("INA228Module 快速测试")
    print("=" * 40)
    
    # 1. 测试模块导入
    print("✓ 模块导入成功")
    
    # 2. 测试适配器创建
    try:
        adapter = create_adapter("ch341")
        if adapter:
            print("✓ CH341适配器创建成功")
        else:
            print("⚠ CH341适配器创建失败，尝试CP2112")
            adapter = create_adapter("cp2112")
            if adapter:
                print("✓ CP2112适配器创建成功")
            else:
                print("✗ 所有适配器创建失败")
                return False
    except Exception as e:
        print(f"✗ 适配器创建异常: {e}")
        return False
    
    # 3. 测试模组创建
    try:
        ina228 = INA228Module(adapter, 0x40)
        print("✓ INA228模组创建成功")
    except Exception as e:
        print(f"✗ INA228模组创建失败: {e}")
        return False
    
    # 4. 测试模组信息
    try:
        info = ina228.get_info()
        print(f"✓ 模组信息获取成功: {info['name']}")
    except Exception as e:
        print(f"✗ 模组信息获取失败: {e}")
        return False
    
    # 5. 测试适配器连接（可选）
    try:
        if adapter.open():
            print("✓ 适配器连接成功")
            
            # 扫描I2C设备
            # devices = adapter.i2c_scan()
            # print(f"✓ 发现 {len(devices)} 个I2C设备")
            
            # 测试模组初始化
            try:
                config_params = {
                    "shunt_resistor": 1,  # 1Ω
                    "max_expected_current": 0.2,  # 200mA
                    "temperature_coefficient": 3300  # 3300ppm/°C
                }
                result = ina228.initialize(**config_params)
                if result:
                    print("✓ INA228模组初始化成功")
                    
                    # 测试基本读取功能
                    current = ina228.read_current()
                    voltage = ina228.read_voltage()
                    power = ina228.read_power()
                    temperature = ina228.read_temperature()
                    
                    print(f"  电流: {current}A" if current is not None else "  电流: 读取失败")
                    print(f"  电压: {voltage}V" if voltage is not None else "  电压: 读取失败")
                    print(f"  功率: {power}W" if power is not None else "  功率: 读取失败")
                    print(f"  温度: {temperature}°C" if temperature is not None else "  温度: 读取失败")
                    
                    if any(x is not None for x in [current, voltage, power, temperature]):
                        print("✓ 基本读取功能正常")
                    else:
                        print("⚠ 基本读取功能可能有问题")
                    
                else:
                    print("⚠ INA228模组初始化失败（可能无硬件）")
                    
            except Exception as e:
                print(f"⚠ 模组测试异常: {e}")
            
            adapter.close()
            print("✓ 适配器已关闭")
            
        else:
            print("⚠ 适配器连接失败（可能无硬件）")
            
    except Exception as e:
        print(f"⚠ 硬件测试异常: {e}")
    
    print("\n🎉 快速测试完成！")
    print("\n使用建议:")
    print("  - 运行完整测试: python test_ina228_module.py")
    print("  - 查看使用示例: python example_ina228_usage.py")
    print("  - 连接INA228硬件以获得最佳测试体验")
    
    return True


if __name__ == "__main__":
    try:
        quick_test()
    except KeyboardInterrupt:
        print("\n\n⚠ 用户中断测试")
    except Exception as e:
        print(f"\n✗ 测试过程中发生异常: {e}")
