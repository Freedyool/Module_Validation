#!/usr/bin/env python3
"""
模块验证框架 - 使用示例

展示如何使用命令行参数进行自动化测试
"""

import os

def print_examples():
    """打印使用示例"""
    print("模块验证框架 - 命令行参数使用示例")
    print("=" * 60)
    
    examples = [
        {
            "title": "1. 查看帮助信息",
            "cmd": "python main.py --help",
            "desc": "显示完整的命令行参数帮助"
        },
        {
            "title": "2. 列出支持的组件",
            "cmd": "python main.py --list-adapters",
            "desc": "查看所有支持的I2C适配器"
        },
        {
            "title": "",
            "cmd": "python main.py --list-modules",
            "desc": "查看所有支持的测试模组"
        },
        {
            "title": "",
            "cmd": "python main.py --list-tasks",
            "desc": "查看所有支持的测试任务"
        },
        {
            "title": "3. 自动化电流采样测试",
            "cmd": "python main.py --adapter ch341 --module ina3221 --task current_sampling --duration 5 --interval 100",
            "desc": "使用CH341适配器测试INA3221模组，采样5秒，间隔100ms"
        },
        {
            "title": "",
            "cmd": "python main.py --adapter cp2112 --module ina219 --task current_sampling --duration 10 --interval 50 --channels 1",
            "desc": "使用CP2112适配器测试INA219模组通道1，采样10秒，间隔50ms"
        },
        {
            "title": "4. 自动化连续采样测试",
            "cmd": "python main.py --adapter ch341 --module ina3221 --task continuous_sampling --interval 200",
            "desc": "连续采样测试，间隔200ms，显示实时数据，需手动停止"
        },
        {
            "title": "",
            "cmd": "python main.py --adapter cp2112 --module ina219 --task continuous_sampling --interval 500 --channels 1 --no-display",
            "desc": "连续采样但不显示实时数据，间隔500ms"
        },
        {
            "title": "5. 指定设备地址和索引",
            "cmd": "python main.py --adapter ch341 --device-index 1 --module ina219 --module-addr 0x41 --task current_sampling --duration 3",
            "desc": "使用第2个CH341设备(索引1)，模组地址0x41"
        },
        {
            "title": "6. 多通道测试",
            "cmd": "python main.py --adapter ch341 --module ina3221 --task current_sampling --duration 5 --channels 1 2 3",
            "desc": "测试INA3221的所有3个通道"
        },
        {
            "title": "7. 调整日志级别",
            "cmd": "python main.py --log-level DEBUG --adapter ch341 --module ina3221 --task current_sampling --duration 1",
            "desc": "使用DEBUG日志级别，查看详细的执行信息"
        },
        {
            "title": "8. 交互式模式",
            "cmd": "python main.py",
            "desc": "不带参数启动，进入交互式菜单模式"
        }
    ]
    
    for example in examples:
        if example["title"]:
            print(f"\n{example['title']}")
            print("-" * 40)
        
        print(f"命令: {example['cmd']}")
        print(f"说明: {example['desc']}")
    
    print(f"\n{'='*60}")
    print("注意事项:")
    print("• 确保I2C适配器设备已正确连接")
    print("• 检查模组的I2C地址是否正确")
    print("• 连续采样任务可以用 'q' + Enter 或 Ctrl+C 停止")
    print("• 程序会自动清理I2C设备资源")
    print("• 如果设备不存在，程序会显示相应错误信息")
    print(f"{'='*60}")

def print_troubleshooting():
    """打印故障排除指南"""
    print("\n故障排除指南")
    print("=" * 60)
    
    issues = [
        {
            "problem": "适配器创建失败",
            "solutions": [
                "检查I2C适配器是否正确连接到计算机",
                "确认设备驱动程序已正确安装",
                "尝试不同的设备索引 (--device-index 0, 1, 2...)",
                "查看设备管理器中是否有相关设备"
            ]
        },
        {
            "problem": "设备打开失败",
            "solutions": [
                "确认设备未被其他程序占用",
                "检查USB连接是否稳定",
                "尝试重新插拔设备",
                "运行 python main.py --list-adapters 确认适配器类型"
            ]
        },
        {
            "problem": "模组初始化失败",
            "solutions": [
                "检查I2C连接线路是否正确",
                "确认模组的I2C地址设置",
                "使用 I2C 扫描功能查找设备地址",
                "检查供电是否正常"
            ]
        },
        {
            "problem": "采样数据异常",
            "solutions": [
                "检查分流电阻值是否配置正确",
                "确认被测电路连接正确",
                "调整采样间隔，避免过于频繁",
                "检查模组的量程设置"
            ]
        }
    ]
    
    for issue in issues:
        print(f"\n问题: {issue['problem']}")
        print("解决方案:")
        for solution in issue['solutions']:
            print(f"  • {solution}")
    
    print(f"\n{'='*60}")

if __name__ == "__main__":
    print_examples()
    
    try:
        response = input("\n是否查看故障排除指南? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            print_troubleshooting()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    
    print("\n感谢使用模块验证框架！")
