#!/usr/bin/env python3
"""
模块验证框架 - 命令行参数测试脚本

用于测试各种命令行参数组合的示例脚本
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*60}")
    
    try:
        # 在Windows上使用shell=True
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        if result.stdout:
            print("输出:")
            print(result.stdout)
        
        if result.stderr:
            print("错误:")
            print(result.stderr)
            
        print(f"返回码: {result.returncode}")
        
    except subprocess.TimeoutExpired:
        print("命令超时")
    except Exception as e:
        print(f"执行命令时出错: {e}")

def main():
    """主测试函数"""
    print("模块验证框架 - 命令行参数测试")
    
    # 获取main.py的路径 (上级目录)
    main_py = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")
    
    # 测试用例
    test_cases = [
        # 帮助信息
        (f"python {main_py} --help", "显示帮助信息"),
        
        # 组件列表
        (f"python {main_py} --list-adapters", "列出支持的I2C适配器"),
        (f"python {main_py} --list-modules", "列出支持的模组"),
        (f"python {main_py} --list-tasks", "列出支持的任务"),
        
        # 参数验证 (这些应该显示错误)
        (f"python {main_py} --adapter ch341", "只提供适配器参数 (应该显示错误)"),
        (f"python {main_py} --adapter ch341 --module ina3221", "只提供适配器和模组参数 (应该显示错误)"),
        
        # 完整的自动化测试命令 (模拟，实际设备可能不存在)
        (f"python {main_py} --adapter ch341 --module ina3221 --task current_sampling --duration 0.1 --interval 100", 
         "完整的current_sampling测试"),
        
        (f"python {main_py} --adapter cp2112 --module ina219 --task continuous_sampling --interval 1000 --channels 1 --no-display", 
         "完整的continuous_sampling测试"),
    ]
    
    for cmd, description in test_cases:
        run_command(cmd, description)
        
        # 询问是否继续
        try:
            response = input("\n按回车继续下一个测试，或输入 'q' 退出: ").strip().lower()
            if response == 'q':
                break
        except KeyboardInterrupt:
            print("\n测试被用户中断")
            break
    
    print(f"\n{'='*60}")
    print("测试完成")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
