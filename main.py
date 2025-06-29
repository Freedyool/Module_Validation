#!/usr/bin/env python3
"""
模块验证框架 - 主入口程序

提供交互式界面，支持选择不同的I2C适配器和模组进行测试任务。

作者: Module Validation Framework
版本: 1.0.0
"""

import sys
import os
import time
import logging
from typing import Optional, Dict, Any

# 添加框架路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from framework.adapters import get_adapter_list, create_adapter, get_adapter_info
from framework.modules import get_module_list, create_module, get_module_info
from framework.tasks import get_task_list, create_task, get_task_info

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class ModuleValidationFramework:
    """模块验证框架主类"""
    
    def __init__(self):
        self.adapter = None
        self.module = None
        self.task = None
        
    def show_banner(self):
        """显示程序标题"""
        print(f"\n{'='*70}")
        print(f"{'模块验证框架 (Module Validation Framework)':^70}")
        print(f"{'支持多种I2C适配器和模组的自动化测试平台':^70}")
        print(f"{'版本: 1.0.0':^70}")
        print(f"{'='*70}")
        
    def show_main_menu(self):
        """显示主菜单"""
        print(f"\n{'='*50}")
        print("主菜单")
        print(f"{'='*50}")
        print("1. 选择I2C适配器")
        print("2. 选择测试模组")
        print("3. 执行测试任务")
        print("4. 查看设备状态")
        print("5. 扫描I2C总线")
        print("6. 系统信息")
        print("0. 退出程序")
        print(f"{'='*50}")
        
    def select_adapter(self) -> bool:
        """选择I2C适配器"""
        print(f"\n{'='*40}")
        print("选择I2C适配器")
        print(f"{'='*40}")
        
        adapters = get_adapter_list()
        if not adapters:
            print("没有可用的适配器")
            return False
            
        # 显示可用适配器
        for i, adapter_type in enumerate(adapters, 1):
            info = get_adapter_info(adapter_type)
            print(f"{i}. {info['name']}")
            print(f"   描述: {info['description']}")
            
        print("0. 返回主菜单")
        
        try:
            choice = int(input("\n请选择适配器 (输入序号): "))
            if choice == 0:
                return False
            elif 1 <= choice <= len(adapters):
                adapter_type = adapters[choice - 1]
                
                # 询问设备索引
                device_index = int(input("请输入设备索引 (默认0): ") or "0")
                
                # 创建适配器
                print(f"\n正在创建 {adapter_type} 适配器...")
                self.adapter = create_adapter(adapter_type, device_index)
                
                if self.adapter:
                    print(f"适配器创建成功: {self.adapter.name}")
                    
                    # 尝试打开设备
                    print("正在打开设备...")
                    if self.adapter.open():
                        print("✓ 设备打开成功")
                        return True
                    else:
                        print("✗ 设备打开失败")
                        self.adapter = None
                        return False
                else:
                    print("适配器创建失败")
                    return False
            else:
                print("无效选择")
                return False
                
        except ValueError:
            print("请输入有效数字")
            return False
        except Exception as e:
            print(f"选择适配器时出错: {e}")
            return False
    
    def select_module(self) -> bool:
        """选择测试模组"""
        if not self.adapter:
            print("请先选择适配器")
            return False
            
        print(f"\n{'='*40}")
        print("选择测试模组")
        print(f"{'='*40}")
        
        modules = get_module_list()
        if not modules:
            print("没有可用的模组")
            return False
            
        # 显示可用模组
        for i, module_type in enumerate(modules, 1):
            info = get_module_info(module_type)
            print(f"{i}. {info['name']}")
            print(f"   描述: {info['description']}")
            print(f"   默认地址: 0x{info['default_address']:02X}")
            print(f"   通道数: {info['channels']}")
            
        print("0. 返回主菜单")
        
        try:
            choice = int(input("\n请选择模组 (输入序号): "))
            if choice == 0:
                return False
            elif 1 <= choice <= len(modules):
                module_type = modules[choice - 1]
                info = get_module_info(module_type)
                
                # 询问设备地址
                default_addr = info['default_address']
                addr_input = input(f"请输入设备地址 (默认0x{default_addr:02X}): ").strip()
                
                if addr_input:
                    if addr_input.startswith('0x') or addr_input.startswith('0X'):
                        device_addr = int(addr_input, 16)
                    else:
                        device_addr = int(addr_input)
                else:
                    device_addr = default_addr
                
                # 创建模组
                print(f"\n正在创建 {module_type} 模组 (地址: 0x{device_addr:02X})...")
                self.module = create_module(module_type, self.adapter, device_addr)
                
                if self.module:
                    print(f"模组创建成功: {self.module.name}")
                    
                    # 尝试初始化模组
                    print("正在初始化模组...")
                    if self.module.initialize():
                        print("✓ 模组初始化成功")
                        return True
                    else:
                        print("✗ 模组初始化失败")
                        self.module = None
                        return False
                else:
                    print("模组创建失败")
                    return False
            else:
                print("无效选择")
                return False
                
        except ValueError:
            print("请输入有效数字或地址")
            return False
        except Exception as e:
            print(f"选择模组时出错: {e}")
            return False
    
    def execute_task(self) -> bool:
        """执行测试任务"""
        if not self.adapter or not self.module:
            print("请先选择适配器和模组")
            return False
            
        print(f"\n{'='*40}")
        print("选择测试任务")
        print(f"{'='*40}")
        
        tasks = get_task_list()
        if not tasks:
            print("没有可用的任务")
            return False
            
        # 显示可用任务
        for i, task_type in enumerate(tasks, 1):
            info = get_task_info(task_type)
            print(f"{i}. {info['name']}")
            print(f"   描述: {info['description']}")
            
        print("0. 返回主菜单")
        
        try:
            choice = int(input("\n请选择任务 (输入序号): "))
            if choice == 0:
                return False
            elif 1 <= choice <= len(tasks):
                task_type = tasks[choice - 1]
                
                # 创建任务
                print(f"\n正在创建 {task_type} 任务...")
                self.task = create_task(task_type, self.adapter, self.module)
                
                if not self.task:
                    print("任务创建失败")
                    return False
                
                # 根据任务类型获取参数
                if task_type == "current_sampling":
                    return self._execute_current_sampling()
                else:
                    print(f"未实现的任务类型: {task_type}")
                    return False
            else:
                print("无效选择")
                return False
                
        except ValueError:
            print("请输入有效数字")
            return False
        except Exception as e:
            print(f"执行任务时出错: {e}")
            return False
    
    def _execute_current_sampling(self) -> bool:
        """执行电流采样任务"""
        print(f"\n{'='*40}")
        print("电流采样任务配置")
        print(f"{'='*40}")
        
        try:
            # 获取任务参数
            duration_input = input("采样持续时间(秒，默认1): ").strip()
            duration_s = float(duration_input) if duration_input else 1.0
            
            interval_input = input("采样间隔(毫秒，默认1): ").strip()
            interval_ms = float(interval_input) if interval_input else 1.0
            
            channels_input = input("采样通道(例如1,2,3，默认所有通道): ").strip()
            if channels_input:
                channels = [int(x.strip()) for x in channels_input.split(',')]
            else:
                channels = None
            
            print(f"\n任务配置:")
            print(f"  持续时间: {duration_s}秒")
            print(f"  采样间隔: {interval_ms}毫秒")
            print(f"  采样通道: {channels if channels else '所有通道'}")
            
            confirm = input("\n确认执行? (y/N): ").strip().lower()
            if confirm != 'y':
                print("任务已取消")
                return False
            
            # 执行任务
            print(f"\n{'='*60}")
            print("开始执行电流采样任务...")
            print(f"{'='*60}")
            
            result = self.task.execute(
                duration_s=duration_s,
                interval_ms=interval_ms,
                channels=channels
            )
            
            # 显示结果
            if hasattr(self.task, 'print_results'):
                self.task.print_results(result)
            else:
                if result["success"]:
                    print("任务执行成功")
                    if result["data"]:
                        stats = result["data"]["statistics"]
                        print(f"采样完成: {stats['total_samples']}个样本")
                else:
                    print(f"任务执行失败: {result['error']}")
            
            return result["success"]
            
        except ValueError:
            print("参数格式错误")
            return False
        except KeyboardInterrupt:
            print("\n任务被用户中断")
            if self.task and hasattr(self.task, 'stop'):
                self.task.stop()
            return False
        except Exception as e:
            print(f"执行任务时出错: {e}")
            return False
    
    def show_device_status(self):
        """显示设备状态"""
        print(f"\n{'='*40}")
        print("设备状态")
        print(f"{'='*40}")
        
        # 适配器状态
        if self.adapter:
            adapter_info = self.adapter.get_info()
            print(f"适配器: {adapter_info['name']}")
            print(f"  设备索引: {adapter_info['device_index']}")
            print(f"  连接状态: {'已连接' if adapter_info['is_opened'] else '未连接'}")
        else:
            print("适配器: 未选择")
        
        # 模组状态  
        if self.module:
            module_info = self.module.get_info()
            print(f"\n模组: {module_info['name']}")
            print(f"  设备地址: {module_info['device_addr']}")
            print(f"  初始化状态: {'已初始化' if module_info['is_initialized'] else '未初始化'}")
            
            # 显示模组特有信息
            if 'channels' in module_info:
                print(f"  通道数: {module_info['channels']}")
            if 'measurement_range' in module_info:
                print(f"  测量范围:")
                for key, value in module_info['measurement_range'].items():
                    print(f"    {key}: {value}")
        else:
            print("\n模组: 未选择")
    
    def scan_i2c_bus(self):
        """扫描I2C总线"""
        if not self.adapter:
            print("请先选择适配器")
            return
            
        print(f"\n{'='*40}")
        print("I2C总线扫描")
        print(f"{'='*40}")
        
        try:
            start_addr = int(input("起始地址 (默认0x08): ") or "8", 16)
            end_addr = int(input("结束地址 (默认0x77): ") or "119", 16)
            
            print(f"\n正在扫描I2C总线 (0x{start_addr:02X} - 0x{end_addr:02X})...")
            devices = self.adapter.i2c_scan(start_addr, end_addr)
            
            if devices:
                print(f"\n发现 {len(devices)} 个I2C设备:")
                for addr in devices:
                    print(f"  0x{addr:02X} ({addr:3d})")
            else:
                print("\n未发现任何I2C设备")
                
        except ValueError:
            print("地址格式错误")
        except Exception as e:
            print(f"扫描总线时出错: {e}")
    
    def show_system_info(self):
        """显示系统信息"""
        print(f"\n{'='*40}")
        print("系统信息")
        print(f"{'='*40}")
        
        # 框架信息
        print("框架信息:")
        print("  名称: 模块验证框架")
        print("  版本: 1.0.0")
        print("  语言: Python")
        
        # 支持的适配器
        adapters = get_adapter_list()
        print(f"\n支持的适配器 ({len(adapters)}):")
        for adapter_type in adapters:
            info = get_adapter_info(adapter_type)
            print(f"  {adapter_type}: {info['name']}")
        
        # 支持的模组
        modules = get_module_list()
        print(f"\n支持的模组 ({len(modules)}):")
        for module_type in modules:
            info = get_module_info(module_type)
            print(f"  {module_type}: {info['name']}")
        
        # 支持的任务
        tasks = get_task_list()
        print(f"\n支持的任务 ({len(tasks)}):")
        for task_type in tasks:
            info = get_task_info(task_type)
            print(f"  {task_type}: {info['name']}")
    
    def cleanup(self):
        """清理资源"""
        if self.adapter:
            try:
                self.adapter.close()
                print("适配器已关闭")
            except:
                pass
    
    def run(self):
        """运行主程序"""
        self.show_banner()
        
        try:
            while True:
                self.show_main_menu()
                
                try:
                    choice = input("\n请选择操作 (输入序号): ").strip()
                    
                    if choice == "0":
                        print("感谢使用模块验证框架！")
                        break
                    elif choice == "1":
                        self.select_adapter()
                    elif choice == "2":
                        self.select_module()
                    elif choice == "3":
                        self.execute_task()
                    elif choice == "4":
                        self.show_device_status()
                    elif choice == "5":
                        self.scan_i2c_bus()
                    elif choice == "6":
                        self.show_system_info()
                    else:
                        print("无效选择，请重新输入")
                        
                except KeyboardInterrupt:
                    print("\n\n检测到Ctrl+C，正在退出...")
                    break
                except Exception as e:
                    print(f"操作出错: {e}")
                    
                # 等待用户按键继续
                if choice != "0":
                    input("\n按回车键继续...")
                    
        finally:
            self.cleanup()


def main():
    """主函数"""
    try:
        framework = ModuleValidationFramework()
        framework.run()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出现致命错误: {e}")
        logger.exception("Fatal error")


if __name__ == "__main__":
    main()
