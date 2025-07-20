import time
import sys
import os

# 添加框架路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework.modules.ina3221_module import INA3221Module, AutoRangerA3
from framework.adapters.ch341_adapter import CH341Adapter
from framework.interfaces import PinID, PinLevel, PinDirection


if __name__ == "__main__":
    adapter = CH341Adapter()
    
    # 打开设备
    if not adapter.open():
        print("✗ 设备打开失败")
        sys.exit(1)
    
    print("✓ 设备打开成功")
    
    module = INA3221Module(adapter, 0x40)
    
    # 初始化模组
    module.set_shunt_resistors([0.1, 10, 1000])  # 设置分流电阻值为0.1Ω, 10Ω, 1000Ω
    
    if not module.initialize():
        print("✗ 模组初始化失败")
        sys.exit(1)
        
    adapter.set_pin_direction(PinID.GPIO_0, PinDirection.OUTPUT)
    adapter.set_pin_direction(PinID.GPIO_1, PinDirection.OUTPUT)
    
    print("✓ 模组初始化成功")
        
    info = module.get_info()    
    print(f"模组信息: {info}")
    
    auto_ranger = AutoRangerA3(adapter, module)
    
    while True:
    
        current = auto_ranger.process()
        print(f"电流值：{current*1000} uA")
    
        # shunt_voltage = module._read_shunt_voltage(3)  # 读取通道3的分流电压
        # if shunt_voltage is None:
        #     print("✗ 读取通道3的分流电压失败")
        #     break
        # print(f"通道3分流电压: {shunt_voltage:.2f} mV 电流: {shunt_voltage / shunt_resisters[2]*1000:.2f} mA")
        
        # 等待1秒
        time.sleep(1)
