#!/usr/bin/env python3
"""
测试默认采样间隔设置

验证命令行参数的默认采样间隔是否为100ms
"""

import sys
import os

# 添加框架路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_default_interval():
    """测试默认采样间隔"""
    print("测试默认采样间隔设置")
    print("=" * 40)
    
    # 导入main模块的参数解析函数
    try:
        from main import parse_arguments
        
        # 模拟不带interval参数的命令行
        import argparse
        sys.argv = ['main.py', '--list-adapters']
        
        args = parse_arguments()
        
        print(f"默认采样间隔: {args.interval}ms")
        
        if args.interval == 100.0:
            print("✓ 默认采样间隔设置正确 (100ms)")
        else:
            print(f"✗ 默认采样间隔设置错误，期望100ms，实际{args.interval}ms")
            
    except Exception as e:
        print(f"测试过程中出错: {e}")

def test_help_info():
    """测试帮助信息中的默认值显示"""
    print("\n测试帮助信息")
    print("=" * 40)
    
    import subprocess
    
    try:
        # 运行help命令并捕获输出
        result = subprocess.run(
            [sys.executable, "main.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            help_text = result.stdout
            
            # 检查interval相关的帮助信息
            if "100.0" in help_text and "采样间隔" in help_text:
                print("✓ 帮助信息中显示了正确的默认采样间隔")
            else:
                print("⚠ 帮助信息中可能没有正确显示默认采样间隔")
            
            # 提取interval相关行
            lines = help_text.split('\n')
            for line in lines:
                if 'interval' in line.lower() and '默认' in line:
                    print(f"  帮助文本: {line.strip()}")
        else:
            print(f"✗ 无法获取帮助信息，返回码: {result.returncode}")
            
    except Exception as e:
        print(f"测试帮助信息时出错: {e}")

if __name__ == "__main__":
    test_default_interval()
    test_help_info()
    
    print(f"\n{'='*40}")
    print("测试完成")
    print("默认采样间隔已设置为100ms，这样可以：")
    print("• 提供较好的采样精度")
    print("• 减少系统负载")
    print("• 适合大多数测试场景")
    print("• 用户仍可通过--interval参数自定义")
