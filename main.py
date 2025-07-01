#!/usr/bin/env python3
"""
模块验证框架 - 主入口程序

提供交互式界面，支持选择不同的I2C适配器和模组进行测试任务。
支持命令行参数直接运行测试，方便自动化测试。

作者: Module Validation Framework
版本: 1.0.0
"""

import sys
import os
import time
import logging
import argparse
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
                elif task_type == "continuous_sampling":
                    return self._execute_continuous_sampling()
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
    
    def _execute_continuous_sampling(self) -> bool:
        """执行连续采样任务"""
        print(f"\n{'='*40}")
        print("连续采样任务配置")
        print(f"{'='*40}")
        
        try:
            # 获取任务参数
            interval_input = input("采样间隔(毫秒，默认100): ").strip()
            interval_ms = float(interval_input) if interval_input else 100.0

            channels_input = input("采样通道(例如1,2,3，默认所有通道): ").strip()
            if channels_input:
                channels = [int(x.strip()) for x in channels_input.split(',')]
            else:
                channels = None
            
            display_input = input("实时显示采样数据? (Y/n): ").strip().lower()
            display_samples = display_input not in ['n', 'no', 'false']
            
            print(f"\n任务配置:")
            print(f"  采样间隔: {interval_ms}毫秒")
            print(f"  采样通道: {channels if channels else '所有通道'}")
            print(f"  实时显示: {'是' if display_samples else '否'}")
            print(f"\n注意事项:")
            print(f"  - 在采样过程中按 'q' + Enter 停止采样")
            print(f"  - 在采样过程中按 's' + Enter 显示当前统计信息")
            print(f"  - 或者使用 Ctrl+C 强制停止")
            
            confirm = input("\n确认开始连续采样? (y/N): ").strip().lower()
            if confirm != 'y':
                print("任务已取消")
                return False
            
            # 执行任务
            result = self.task.execute(
                interval_ms=interval_ms,
                channels=channels,
                display_samples=display_samples
            )
            
            # 显示结果摘要
            if hasattr(self.task, 'print_results'):
                self.task.print_results(result)
            else:
                if result["success"]:
                    print("连续采样任务完成")
                    if result["data"]:
                        stats = result["data"]["statistics"]
                        print(f"总采样数: {stats['total_samples']}")
                        print(f"运行时间: {stats['actual_duration']:.1f}秒")
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
        cleanup_success = True
        
        # 停止正在运行的任务
        if hasattr(self, 'task') and self.task:
            try:
                if hasattr(self.task, 'stop'):
                    self.task.stop()
                    print("✓ 任务已停止")
            except Exception as e:
                print(f"⚠ 停止任务时出错: {e}")
                cleanup_success = False
        
        # 关闭适配器
        if hasattr(self, 'adapter') and self.adapter:
            try:
                if hasattr(self.adapter, 'is_opened') and self.adapter.is_opened:
                    self.adapter.close()
                    print("✓ I2C适配器已关闭")
                elif hasattr(self.adapter, 'close'):
                    # 即使不确定是否已打开，也尝试关闭
                    self.adapter.close()
                    print("✓ I2C适配器已关闭")
            except Exception as e:
                print(f"⚠ 关闭I2C适配器时出错: {e}")
                cleanup_success = False
        
        # 清理模组引用
        if hasattr(self, 'module') and self.module:
            try:
                # 如果模组有清理方法，调用它
                if hasattr(self.module, 'cleanup'):
                    self.module.cleanup()
                print("✓ 模组资源已清理")
            except Exception as e:
                print(f"⚠ 清理模组资源时出错: {e}")
                cleanup_success = False
        
        # 重置状态
        try:
            self.adapter = None
            self.module = None  
            self.task = None
        except:
            pass
        
        if cleanup_success:
            print("✓ 所有资源已成功清理")
        else:
            print("⚠ 部分资源清理时出现问题，但程序可以安全退出")
    
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

    def run_with_args(self, args):
        """使用命令行参数运行测试
        
        Args:
            args: 解析后的命令行参数
        """
        try:
            print(f"\n{'='*70}")
            print(f"{'模块验证框架 - 自动化测试模式':^70}")
            print(f"{'='*70}")
            
            # 创建适配器
            print(f"\n步骤 1/4: 创建适配器 ({args.adapter})")
            print("-" * 50)
            
            self.adapter = create_adapter(args.adapter, args.device_index)
            if not self.adapter:
                print(f"✗ 适配器创建失败: {args.adapter}")
                return False
            
            print(f"✓ 适配器创建成功: {self.adapter.name}")
            
            # 打开设备
            if not self.adapter.open():
                print("✗ 设备打开失败")
                return False
            
            print("✓ 设备打开成功")
            
            # 创建模组
            print(f"\n步骤 2/4: 创建模组 ({args.module})")
            print("-" * 50)
            
            self.module = create_module(args.module, self.adapter, args.module_addr)
            if not self.module:
                print(f"✗ 模组创建失败: {args.module}")
                return False
            
            print(f"✓ 模组创建成功: {self.module.name}")
            print(f"  设备地址: 0x{args.module_addr:02X}")
            
            # 初始化模组
            if not self.module.initialize():
                print("✗ 模组初始化失败")
                return False
            
            print("✓ 模组初始化成功")
            
            # 创建任务
            print(f"\n步骤 3/4: 创建任务 ({args.task})")
            print("-" * 50)
            
            self.task = create_task(args.task, self.adapter, self.module)
            if not self.task:
                print(f"✗ 任务创建失败: {args.task}")
                return False
            
            print(f"✓ 任务创建成功: {self.task.name}")
            
            # 执行任务
            print(f"\n步骤 4/4: 执行任务")
            print("-" * 50)
            
            # 准备任务参数
            task_params = {}
            
            if args.task == "current_sampling":
                task_params = {
                    "duration_s": args.duration,
                    "interval_ms": args.interval,
                    "channels": args.channels
                }
                print(f"任务参数:")
                print(f"  持续时间: {args.duration}秒")
                print(f"  采样间隔: {args.interval}毫秒")
                print(f"  采样通道: {args.channels if args.channels else '所有通道'}")
                
            elif args.task == "continuous_sampling":
                task_params = {
                    "interval_ms": args.interval,
                    "channels": args.channels,
                    "display_samples": not args.no_display
                }
                print(f"任务参数:")
                print(f"  采样间隔: {args.interval}毫秒")
                print(f"  采样通道: {args.channels if args.channels else '所有通道'}")
                print(f"  实时显示: {'否' if args.no_display else '是'}")
                print(f"  注意: 按 'q' + Enter 或 Ctrl+C 停止采样")
            
            print(f"\n开始执行任务...")
            print(f"{'='*70}")
            
            # 执行任务
            result = self.task.execute(**task_params)
            
            # 显示结果
            print(f"\n{'='*70}")
            print(f"任务执行完成")
            print(f"{'='*70}")
            
            if hasattr(self.task, 'print_results'):
                self.task.print_results(result)
            else:
                if result["success"]:
                    print("✓ 任务执行成功")
                    if result["data"]:
                        stats = result["data"].get("statistics", {})
                        if "total_samples" in stats:
                            print(f"  总采样数: {stats['total_samples']}")
                        if "actual_duration" in stats:
                            print(f"  运行时间: {stats['actual_duration']:.1f}秒")
                else:
                    print(f"✗ 任务执行失败: {result['error']}")
            
            return result["success"]
            
        except KeyboardInterrupt:
            print("\n\n任务被用户中断 (Ctrl+C)")
            if self.task and hasattr(self.task, 'stop'):
                self.task.stop()
            return False
        except Exception as e:
            print(f"\n执行自动化测试时出错: {e}")
            logger.exception("Automated test error")
            return False
        finally:
            # 确保在任何情况下都清理资源
            print(f"\n{'='*50}")
            print("清理资源...")
            print(f"{'='*50}")
            self.cleanup()


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="模块验证框架 - 支持交互式和自动化测试",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  交互式模式:
    python main.py
    
  自动化测试:
    python main.py --adapter ch341 --module ina3221 --task current_sampling --duration 5 --interval 100
    python main.py --adapter cp2112 --module ina219 --task continuous_sampling --interval 1000 --channels 1
    
  查看支持的组件:
    python main.py --list-adapters
    python main.py --list-modules  
    python main.py --list-tasks
        """
    )
    
    # 模式选择
    group_mode = parser.add_mutually_exclusive_group()
    group_mode.add_argument('--interactive', '-i', action='store_true',
                           help='启动交互式模式 (默认)')
    
    # 信息查询
    group_info = parser.add_mutually_exclusive_group()
    group_info.add_argument('--list-adapters', action='store_true',
                           help='列出所有支持的I2C适配器')
    group_info.add_argument('--list-modules', action='store_true',
                           help='列出所有支持的模组')
    group_info.add_argument('--list-tasks', action='store_true',
                           help='列出所有支持的测试任务')
    
    # 自动化测试参数
    parser.add_argument('--adapter', '-a', 
                       choices=get_adapter_list(),
                       help='I2C适配器类型')
    parser.add_argument('--device-index', '-d', type=int, default=0,
                       help='适配器设备索引 (默认: 0)')
    parser.add_argument('--module', '-m',
                       choices=get_module_list(), 
                       help='测试模组类型')
    parser.add_argument('--module-addr', '-addr', type=lambda x: int(x, 0), default=0x40,
                       help='模组I2C地址 (支持十进制和十六进制，默认: 0x40)')
    parser.add_argument('--task', '-t',
                       choices=get_task_list(),
                       help='测试任务类型')
    
    # 任务参数
    task_group = parser.add_argument_group('任务参数')
    task_group.add_argument('--duration', type=float, default=1.0,
                           help='采样持续时间(秒) - 仅用于current_sampling任务 (默认: 1.0)')
    task_group.add_argument('--interval', type=float, default=100.0,
                           help='采样间隔(毫秒) (默认: 100.0)')
    task_group.add_argument('--channels', type=int, nargs='+',
                           help='采样通道列表，例如: --channels 1 2 3')
    task_group.add_argument('--no-display', action='store_true',
                           help='禁用实时数据显示 - 仅用于continuous_sampling任务')
    
    # 日志级别
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='设置日志级别 (默认: INFO)')
    
    return parser.parse_args()


def print_component_list(component_type: str):
    """打印组件列表"""
    if component_type == "adapters":
        print("\n支持的I2C适配器:")
        print("=" * 50)
        adapters = get_adapter_list()
        for adapter_type in adapters:
            info = get_adapter_info(adapter_type)
            print(f"  {adapter_type:15} - {info['name']}")
            print(f"{'':17}   {info['description']}")
            
    elif component_type == "modules":
        print("\n支持的测试模组:")
        print("=" * 50)
        modules = get_module_list()
        for module_type in modules:
            info = get_module_info(module_type)
            print(f"  {module_type:15} - {info['name']}")
            print(f"{'':17}   {info['description']}")
            print(f"{'':17}   默认地址: 0x{info['default_address']:02X}, 通道数: {info['channels']}")
            
    elif component_type == "tasks":
        print("\n支持的测试任务:")
        print("=" * 50)
        tasks = get_task_list()
        for task_type in tasks:
            info = get_task_info(task_type)
            print(f"  {task_type:20} - {info['name']}")
            print(f"{'':22}   {info['description']}")
            if 'parameters' in info:
                print(f"{'':22}   参数:")
                for param, desc in info['parameters'].items():
                    print(f"{'':24}     {param}: {desc}")


def main():
    """主函数"""
    try:
        args = parse_arguments()
        
        # 设置日志级别
        logging.getLogger().setLevel(getattr(logging, args.log_level))
        
        # 处理信息查询
        if args.list_adapters:
            print_component_list("adapters")
            return
        elif args.list_modules:
            print_component_list("modules")
            return
        elif args.list_tasks:
            print_component_list("tasks")
            return
        
        framework = ModuleValidationFramework()
        
        # 检查是否为自动化模式
        if args.adapter and args.module and args.task:
            # 验证参数组合
            if args.task == "current_sampling" and args.duration <= 0:
                print("错误: current_sampling任务需要有效的持续时间")
                return
            
            if args.interval <= 0:
                print("错误: 采样间隔必须大于0")
                return
            
            # 运行自动化测试
            success = framework.run_with_args(args)
            sys.exit(0 if success else 1)
        else:
            # 检查是否提供了部分参数
            provided_params = sum([
                bool(args.adapter),
                bool(args.module), 
                bool(args.task)
            ])
            
            if provided_params > 0 and provided_params < 3:
                print("错误: 自动化模式需要同时指定 --adapter, --module 和 --task 参数")
                print("使用 --help 查看完整帮助信息")
                print("或者运行不带参数的命令进入交互式模式")
                return
            
            # 运行交互式模式
            framework.run()
            
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序出现致命错误: {e}")
        logger.exception("Fatal error")


if __name__ == "__main__":
    main()
