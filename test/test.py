#!/usr/bin/env python3
"""
模块验证框架 - 快速测试脚本

用于验证框架组件是否正常工作
"""

import sys
import os

# 添加框架路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_framework_imports():
    """测试框架模块导入"""
    print("测试框架模块导入...")
    
    try:
        # 测试接口导入
        from framework.interfaces import AdapterInterface, ModuleInterface, TaskInterface
        print("✓ 抽象接口导入成功")
        
        # 测试适配器导入
        from framework.adapters import get_adapter_list, create_adapter
        adapters = get_adapter_list()
        print(f"✓ 适配器模块导入成功，支持: {adapters}")
        
        # 测试模组导入
        from framework.modules import get_module_list, create_module
        modules = get_module_list()
        print(f"✓ 模组模块导入成功，支持: {modules}")
        
        # 测试任务导入
        from framework.tasks import get_task_list, create_task
        tasks = get_task_list()
        print(f"✓ 任务模块导入成功，支持: {tasks}")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_adapter_creation():
    """测试适配器创建"""
    print("\n测试适配器创建...")
    
    try:
        from framework.adapters import create_adapter
        
        # 测试CH341适配器创建
        ch341_adapter = create_adapter("ch341", 0)
        if ch341_adapter:
            print("✓ CH341适配器创建成功")
            print(f"  名称: {ch341_adapter.name}")
            print(f"  设备索引: {ch341_adapter.device_index}")
        else:
            print("✗ CH341适配器创建失败")
            
        return True
        
    except Exception as e:
        print(f"✗ 适配器创建失败: {e}")
        return False

def test_module_creation():
    """测试模组创建"""
    print("\n测试模组创建...")
    
    try:
        from framework.adapters import create_adapter
        from framework.modules import create_module
        
        # 创建适配器
        adapter = create_adapter("ch341", 0)
        if not adapter:
            print("✗ 无法创建适配器，跳过模组测试")
            return False
            
        # 测试INA3221模组创建
        ina3221_module = create_module("ina3221", adapter, 0x40)
        if ina3221_module:
            print("✓ INA3221模组创建成功")
            print(f"  名称: {ina3221_module.name}")
            print(f"  设备地址: 0x{ina3221_module.device_addr:02X}")
        else:
            print("✗ INA3221模组创建失败")
            
        return True
        
    except Exception as e:
        print(f"✗ 模组创建失败: {e}")
        return False

def test_task_creation():
    """测试任务创建"""
    print("\n测试任务创建...")
    
    try:
        from framework.adapters import create_adapter
        from framework.modules import create_module
        from framework.tasks import create_task
        
        # 创建适配器和模组
        adapter = create_adapter("ch341", 0)
        module = create_module("ina3221", adapter, 0x40)
        
        if not adapter or not module:
            print("✗ 无法创建适配器或模组，跳过任务测试")
            return False
            
        # 测试电流采样任务创建
        task = create_task("current_sampling", adapter, module)
        if task:
            print("✓ 电流采样任务创建成功")
            print(f"  名称: {task.name}")
        else:
            print("✗ 电流采样任务创建失败")
            
        return True
        
    except Exception as e:
        print(f"✗ 任务创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("="*60)
    print("模块验证框架 - 组件测试")
    print("="*60)
    
    tests = [
        test_framework_imports,
        test_adapter_creation,
        test_module_creation,
        test_task_creation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"测试异常: {e}")
    
    print(f"\n{'='*60}")
    print(f"测试结果: {passed}/{total} 通过")
    
    if passed == total:
        print("✓ 所有测试通过，框架组件正常")
    else:
        print("✗ 部分测试失败，请检查错误信息")
    
    print("="*60)

if __name__ == "__main__":
    main()
