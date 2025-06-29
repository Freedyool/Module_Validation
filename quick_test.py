#!/usr/bin/env python3
"""
快速测试脚本
"""

from framework.adapters import get_adapter_list, get_adapter_info
from framework.modules import get_module_list, get_module_info  
from framework.tasks import get_task_list, get_task_info

print("============================================")
print("模块验证框架 - 组件注册情况")
print("============================================")

print("支持的适配器:", get_adapter_list())
for adapter in get_adapter_list():
    info = get_adapter_info(adapter)
    print(f"  {adapter}: {info['name']}")

print("\n支持的模组:", get_module_list()) 
for module in get_module_list():
    info = get_module_info(module)
    print(f"  {module}: {info['name']}")

print("\n支持的任务:", get_task_list())
for task in get_task_list():
    info = get_task_info(task)
    print(f"  {task}: {info['name']}")

print("\n============================================")
print("所有组件注册成功，框架可以正常使用！")
print("运行 'python main.py' 开始使用框架")
print("============================================")
