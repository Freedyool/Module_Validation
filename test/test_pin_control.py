#!/usr/bin/env python3
"""
CH341引脚控制功能测试

测试新增的引脚控制功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.adapters.ch341_adapter import CH341Adapter
from framework.interfaces import PinID, PinLevel, PinDirection

def test_pin_control():
    """测试引脚控制功能"""
    print("CH341引脚控制功能测试")
    print("=" * 50)
    
    # 创建适配器
    adapter = CH341Adapter()
    
    if not adapter.open():
        print("❌ 无法打开CH341设备")
        return
    
    try:
        # 显示支持的引脚
        print("\n📋 支持的引脚:")
        pins = adapter.get_supported_pins()
        for pin in pins:
            print(f"  • {pin.pin_id.value}: {pin.description} ({pin.direction.value})")
        
        # 测试单个引脚控制
        print("\n🔧 测试单个引脚控制:")
        # test_pin = PinID.DATA_0
        test_pin = PinID.GPIO_0
        
        # 设置为输出模式
        if adapter.set_pin_direction(test_pin, PinDirection.OUTPUT):
            print(f"✅ {test_pin.value} 设置为输出模式")
            
            # 设置高电平
            if adapter.set_pin_level(test_pin, PinLevel.HIGH):
                print(f"✅ {test_pin.value} 设置为高电平")
                time.sleep(0.5)
                
                # 读取电平
                level = adapter.get_pin_level(test_pin)
                print(f"📖 {test_pin.value} 当前电平: {level.value if level else 'None'}")
                
                # 设置低电平
                if adapter.set_pin_level(test_pin, PinLevel.LOW):
                    print(f"✅ {test_pin.value} 设置为低电平")
                    time.sleep(0.5)
                    
                    # 再次读取电平
                    level = adapter.get_pin_level(test_pin)
                    print(f"📖 {test_pin.value} 当前电平: {level.value if level else 'None'}")
        
        # 测试多引脚控制
        print("\n🔧 测试多引脚控制:")
        # pin_levels = {
        #     PinID.DATA_0: PinLevel.HIGH,
        #     PinID.DATA_1: PinLevel.LOW,
        #     PinID.DATA_2: PinLevel.HIGH,
        #     PinID.DATA_3: PinLevel.LOW,
        # }
        pin_levels = {
            PinID.GPIO_0: PinLevel.HIGH,
            PinID.GPIO_1: PinLevel.LOW,
            PinID.GPIO_2: PinLevel.HIGH,
            PinID.GPIO_3: PinLevel.LOW,
        }
        
        if adapter.set_multiple_pins(pin_levels):
            print("✅ 多引脚设置成功")
            
            # 读取多引脚状态
            pin_ids = list(pin_levels.keys())
            current_levels = adapter.get_multiple_pins(pin_ids)
            
            print("📖 多引脚当前状态:")
            for pin_id, level in current_levels.items():
                print(f"  • {pin_id.value}: {level.value}")
        
        # 测试引脚切换
        print("\n🔧 测试引脚切换:")
        # test_pin = PinID.DATA_4
        test_pin = PinID.GPIO_0
        
        # 设置为输出模式
        adapter.set_pin_direction(test_pin, PinDirection.OUTPUT)
        adapter.set_pin_level(test_pin, PinLevel.LOW)
        
        print(f"🔄 {test_pin.value} 切换测试:")
        for i in range(5):
            if adapter.toggle_pin(test_pin):
                level = adapter.get_pin_level(test_pin)
                print(f"  切换 {i+1}: {level.value if level else 'None'}")
                time.sleep(0.2)
        
        # 测试引脚脉冲
        print("\n🔧 测试引脚脉冲:")
        # test_pin = PinID.DATA_5
        test_pin = PinID.GPIO_1
        
        # 设置为输出模式并设置初始低电平
        adapter.set_pin_direction(test_pin, PinDirection.OUTPUT)
        adapter.set_pin_level(test_pin, PinLevel.LOW)
        
        print(f"⚡ {test_pin.value} 产生100ms脉冲")
        if adapter.pulse_pin(test_pin, 100):
            print("✅ 脉冲生成成功")
        else:
            print("❌ 脉冲生成失败")
        
        # 测试状态引脚读取
        print("\n🔧 测试状态引脚读取:")
        status_pins = [PinID.I2C_SCL, PinID.I2C_SDA, PinID.ERROR, PinID.BUSY]
        status_levels = adapter.get_multiple_pins(status_pins)
        
        print("📖 状态引脚:")
        for pin_id, level in status_levels.items():
            print(f"  • {pin_id.value}: {level.value}")
        
        print("\n✅ 引脚控制测试完成!")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        
    finally:
        adapter.close()

if __name__ == "__main__":
    test_pin_control()