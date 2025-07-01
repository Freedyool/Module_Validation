#!/usr/bin/env python3
"""
I2C设备资源清理测试脚本

测试在自动化执行时I2C设备是否能正确关闭
"""

import subprocess
import sys
import os
import time

def test_resource_cleanup():
    """测试资源清理功能"""
    print("=" * 60)
    print("I2C设备资源清理测试")
    print("=" * 60)
    
    main_py = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")
    
    test_cases = [
        {
            "name": "测试帮助信息 (无设备访问)",
            "cmd": f"python {main_py} --help",
            "expect_cleanup": False
        },
        {
            "name": "测试列出适配器 (无设备访问)",
            "cmd": f"python {main_py} --list-adapters",
            "expect_cleanup": False
        },
        {
            "name": "测试模拟设备连接失败",
            "cmd": f"python {main_py} --adapter ch341 --module ina219 --task current_sampling --duration 0.1",
            "expect_cleanup": True
        },
        {
            "name": "测试无效参数组合",
            "cmd": f"python {main_py} --adapter ch341 --module ina219",
            "expect_cleanup": False
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}/{len(test_cases)}: {test_case['name']}")
        print("-" * 50)
        print(f"命令: {test_case['cmd']}")
        
        try:
            # 执行命令
            start_time = time.time()
            result = subprocess.run(
                test_case['cmd'], 
                shell=True, 
                capture_output=True, 
                text=True, 
                timeout=15  # 15秒超时
            )
            duration = time.time() - start_time
            
            print(f"执行时间: {duration:.1f}秒")
            print(f"返回码: {result.returncode}")
            
            # 检查输出中是否包含清理信息
            output = result.stdout + result.stderr
            has_cleanup_info = any(keyword in output for keyword in [
                "清理资源", "适配器已关闭", "资源已清理", "cleanup"
            ])
            
            if test_case['expect_cleanup']:
                if has_cleanup_info:
                    print("✓ 检测到资源清理信息")
                else:
                    print("⚠ 未检测到资源清理信息")
            else:
                print("ℹ 此测试不涉及设备资源")
            
            # 检查是否有错误或异常
            error_keywords = ["error", "exception", "traceback", "错误", "异常"]
            has_errors = any(keyword.lower() in output.lower() for keyword in error_keywords)
            
            if has_errors and result.returncode == 0:
                print("⚠ 输出中包含错误信息但返回码正常")
            elif result.returncode != 0:
                print(f"⚠ 进程异常退出 (返回码: {result.returncode})")
            else:
                print("✓ 程序正常执行")
            
            # 显示部分输出
            if result.stdout:
                print("输出预览:")
                lines = result.stdout.split('\n')[:5]  # 只显示前5行
                for line in lines:
                    if line.strip():
                        print(f"  {line}")
                if len(result.stdout.split('\n')) > 5:
                    print("  ...")
            
            if result.stderr:
                print("错误输出:")
                lines = result.stderr.split('\n')[:3]  # 只显示前3行
                for line in lines:
                    if line.strip():
                        print(f"  {line}")
                        
        except subprocess.TimeoutExpired:
            print("⚠ 命令执行超时")
        except Exception as e:
            print(f"⚠ 执行测试时出错: {e}")
        
        # 询问是否继续
        if i < len(test_cases):
            try:
                response = input("\n按回车继续下一个测试，或输入 'q' 退出: ").strip().lower()
                if response == 'q':
                    break
            except KeyboardInterrupt:
                print("\n\n测试被用户中断")
                break
    
    print(f"\n{'='*60}")
    print("测试完成")
    print("资源清理测试要点:")
    print("1. 程序应该在退出前清理所有打开的I2C设备")
    print("2. 即使发生异常也应该调用cleanup()方法")
    print("3. 清理过程中的错误应该被捕获并报告")
    print("4. 程序应该能够安全地多次运行而不会出现设备冲突")
    print(f"{'='*60}")

def test_repeated_execution():
    """测试重复执行是否会产生设备冲突"""
    print("\n" + "=" * 60)
    print("重复执行测试 (检查设备冲突)")
    print("=" * 60)
    
    main_py = os.path.join(os.path.dirname(__file__), "main.py")
    cmd = f"python {main_py} --list-adapters"
    
    print("连续执行5次 --list-adapters 命令...")
    
    for i in range(5):
        print(f"\n执行 {i+1}/5:")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✓ 执行成功")
            else:
                print(f"⚠ 执行失败 (返回码: {result.returncode})")
                if result.stderr:
                    print(f"  错误: {result.stderr.strip()}")
        except Exception as e:
            print(f"⚠ 执行异常: {e}")
        
        time.sleep(0.5)  # 短暂延迟
    
    print("\n✓ 重复执行测试完成")

if __name__ == "__main__":
    try:
        test_resource_cleanup()
        test_repeated_execution()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
    except Exception as e:
        print(f"\n测试脚本出错: {e}")
