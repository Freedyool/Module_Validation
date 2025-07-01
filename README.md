# 模块验证框架使用指南

## 概述

模块验证框架是一个可扩展的Python测试平台，支持多种I2C适配器和模组的自动化测试。框架采用模块化设计，便于添加新的适配器、模组和测试任务。

## 新增功能 (v1.0.0)

### 🆕 INA219模组支持
- 新增单通道电流/电压/功率监测芯片支持
- 自动校准功能，支持可配置的分流电阻值
- 支持16V和32V总线电压范围

### 🚀 命令行参数支持
- 完整的命令行参数支持，方便自动化测试
- 支持所有测试场景的参数化运行
- 保持与交互式模式的完全兼容

### 🔧 改进的资源管理
- 强化的资源清理机制
- 防止I2C设备冲突和资源泄漏
- 支持异常情况下的安全退出

## 快速开始

### 1. 交互式模式 (推荐新手)

```bash
cd d:\dev\EE_PROJECTs\Module_Validation
python main.py
```

按照菜单提示选择适配器、模组和测试任务。

### 2. 命令行模式 (推荐自动化)

```bash
# 基本电流采样测试
python main.py --adapter ch341 --module ina3221 --task current_sampling --duration 5 --interval 100

# 连续采样测试
python main.py --adapter ch341 --module ina3221 --task continuous_sampling --interval 200

# 查看支持的组件
python main.py --list-adapters
python main.py --list-modules
python main.py --list-tasks
```

### 3. 示例：CH341 + INA3221电流采样

#### 交互式方式：
1. 运行 `python main.py`
2. 选择 "1. 选择I2C适配器"
3. 选择 "1. CH341 USB-I2C Adapter"
4. 输入设备索引（默认0）
5. 选择 "2. 选择测试模组" 
6. 选择 "1. INA3221 Triple Current Monitor"
7. 输入设备地址（默认0x40）
8. 选择 "3. 执行测试任务"
9. 选择测试任务并配置参数

#### 命令行方式：
```bash
python main.py --adapter ch341 --module ina3221 --task current_sampling --duration 5 --interval 100 --channels 1 2 3
```

## 命令行参数详解

### 基本参数
- `--adapter, -a`: I2C适配器类型 (ch341, cp2112)
- `--device-index, -d`: 适配器设备索引 (默认: 0)
- `--module, -m`: 测试模组类型 (ina3221, ina219)
- `--module-addr, -addr`: 模组I2C地址 (默认: 0x40)
- `--task, -t`: 测试任务类型 (current_sampling, continuous_sampling)

### 任务参数
- `--duration`: 采样持续时间(秒) - 仅用于current_sampling (默认: 1.0)
- `--interval`: 采样间隔(毫秒) (默认: 100.0)
- `--channels`: 采样通道列表 (例如: --channels 1 2 3)
- `--no-display`: 禁用实时数据显示
- `--log-level`: 日志级别 (DEBUG, INFO, WARNING, ERROR)

### 信息查询
- `--help`: 显示完整帮助信息
- `--list-adapters`: 列出所有支持的I2C适配器
- `--list-modules`: 列出所有支持的模组
- `--list-tasks`: 列出所有支持的测试任务

## 框架特性

### 支持的适配器

| 适配器 | 状态 | 描述 |
|--------|------|------|
| **CH341** | ✅ 完整支持 | WCH CH341芯片USB转I2C适配器 |
| **CP2112** | ✅ 完整支持 | Silicon Labs CP2112芯片USB转I2C/SMBus适配器 |

### 支持的模组

| 模组 | 通道数 | 功能 | 状态 |
|------|--------|------|------|
| **INA3221** | 3 | 电流/电压/功率监测 | ✅ 完整支持 |
| **INA219** | 1 | 电流/电压/功率监测 | 🆕 新增支持 |

### 支持的任务

| 任务 | 描述 | 参数 |
|------|------|------|
| **电流采样任务** | 高精度定时电流采样 | 持续时间、间隔、通道 |
| **连续采样任务** | 用户可控的连续采样 | 间隔、通道、显示选项 |

## 使用示例

### 电流采样测试
```bash
# 基本测试 - INA3221全通道5秒采样
python main.py --adapter ch341 --module ina3221 --task current_sampling --duration 5 --interval 100

# 单通道测试 - INA219高精度采样
python main.py --adapter cp2112 --module ina219 --task current_sampling --duration 10 --interval 50 --channels 1

# 多通道测试 - 指定通道采样
python main.py --adapter ch341 --module ina3221 --task current_sampling --duration 5 --channels 1 2 3
```

### 连续采样测试
```bash
# 实时显示采样数据 (按q停止)
python main.py --adapter ch341 --module ina3221 --task continuous_sampling --interval 200

# 静默模式采样
python main.py --adapter cp2112 --module ina219 --task continuous_sampling --interval 500 --no-display

# 高频采样
python main.py --adapter ch341 --module ina3221 --task continuous_sampling --interval 50 --channels 1
```

### 指定设备参数
```bash
# 使用第二个设备和非标准地址
python main.py --adapter ch341 --device-index 1 --module ina219 --module-addr 0x41 --task current_sampling --duration 3

# 十六进制地址格式
python main.py --adapter ch341 --module ina219 --module-addr 0x45 --task current_sampling --duration 2
```

### 调试和开发
```bash
# 调试模式 - 查看详细日志
python main.py --log-level DEBUG --adapter ch341 --module ina3221 --task current_sampling --duration 1

# 扫描I2C总线
python main.py  # 进入交互模式，选择 "5. 扫描I2C总线"
```

## 目录结构

```
Module_Validation/
├── main.py                          # 主入口程序 (支持命令行参数)
├── framework/                       # 框架核心
│   ├── interfaces.py                # 抽象接口定义
│   ├── adapters/                    # 适配器实现
│   │   ├── ch341_adapter.py         # CH341适配器
│   │   ├── cp2112_adapter.py        # CP2112适配器
│   │   └── __init__.py              # 适配器注册
│   ├── modules/                     # 模组实现
│   │   ├── ina3221_module.py        # INA3221三通道模组
│   │   ├── ina219_module.py         # 🆕 INA219单通道模组
│   │   └── __init__.py              # 模组注册
│   └── tasks/                       # 任务实现
│       ├── current_sampling.py     # 电流采样任务
│       ├── continuous_sampling.py  # 连续采样任务
│       └── __init__.py              # 任务注册
├── test/                            # 🆕 测试脚本目录
│   ├── test_cli_args.py             # 命令行参数测试
│   ├── test_resource_cleanup.py     # 资源清理测试
│   ├── test_default_interval.py     # 默认间隔测试
│   ├── examples.py                  # 使用示例和故障排除
│   └── test.py                      # 框架组件测试
├── quick_test.py                    # 快速测试脚本
└── device/                          # 设备驱动和文档
    ├── ch341/                       # CH341相关文件
    └── cp2112/                      # CP2112相关文件
```

## 扩展指南

### 添加新的适配器

1. 在 `framework/adapters/` 下创建新的适配器文件
2. 继承 `AdapterInterface` 并实现所有抽象方法
3. 在 `framework/adapters/__init__.py` 中注册新适配器

### 添加新的模组

1. 在 `framework/modules/` 下创建新的模组文件  
2. 继承 `ModuleInterface` 并实现所有抽象方法
3. 在 `framework/modules/__init__.py` 中注册新模组

### 添加新的任务

1. 在 `framework/tasks/` 下创建新的任务文件
2. 继承 `TaskInterface` 并实现 `execute` 方法
3. 在 `framework/tasks/__init__.py` 中注册新任务

## 测试和验证

### 组件测试

```bash
python quick_test.py                # 验证组件注册
python test/test.py                 # 完整组件测试
python test/test_cli_args.py        # 命令行参数测试
python test/test_resource_cleanup.py # 资源清理测试
python test/examples.py             # 查看使用示例
```

### 硬件要求

- CH341T/CH341A USB开发板 或 CP2112开发板
- INA3221三通道电流监测模组 或 INA219单通道模组
- USB连接线
- I2C连接线（杜邦线）

### 软件要求

- Windows 10/11
- Python 3.6+
- 对应的USB驱动程序 (CH341驱动 或 CP2112驱动)

## 故障排除

### 常见问题

1. **适配器创建失败**
   - 检查I2C适配器是否正确连接到计算机
   - 确认设备驱动程序已正确安装
   - 尝试不同的设备索引 (--device-index 0, 1, 2...)
   - 查看设备管理器中是否有相关设备

2. **设备打开失败**
   - 确认设备未被其他程序占用
   - 检查USB连接是否稳定
   - 尝试重新插拔设备
   - 运行 `python main.py --list-adapters` 确认适配器类型

3. **模组初始化失败**
   - 检查I2C连接线路是否正确
   - 确认模组的I2C地址设置
   - 使用 I2C 扫描功能查找设备地址
   - 检查供电是否正常

4. **采样数据异常**
   - 检查分流电阻值是否配置正确
   - 确认被测电路连接正确
   - 调整采样间隔，避免过于频繁
   - 检查模组的量程设置

### 调试建议

```bash
# 使用调试模式查看详细信息
python main.py --log-level DEBUG --adapter ch341 --module ina3221 --task current_sampling --duration 1

# 扫描I2C总线查找设备
python main.py  # 进入交互模式，选择 "5. 扫描I2C总线"

# 测试基本功能
python quick_test.py

# 检查资源清理
python test/test_resource_cleanup.py
```

## 示例代码

### 程序化使用框架

```python
from framework.adapters import create_adapter
from framework.modules import create_module
from framework.tasks import create_task

# 创建适配器
adapter = create_adapter("ch341", 0)
adapter.open()

try:
    # 创建模组
    module = create_module("ina3221", adapter, 0x40)
    module.initialize()
    
    # 创建任务
    task = create_task("current_sampling", adapter, module)
    
    # 执行任务
    result = task.execute(
        duration_s=1.0,
        interval_ms=100.0,
        channels=None
    )
    
    # 显示结果
    if hasattr(task, 'print_results'):
        task.print_results(result)
    
finally:
    # 清理资源
    adapter.close()
```

### 配置INA219模组

```python
# 创建INA219模组并配置参数
module = create_module("ina219", adapter, 0x40)

# 配置模组参数
module.configure(
    shunt_resistor=0.1,        # 100mΩ分流电阻
    max_expected_current=2.0,  # 最大期望电流2A
    bus_voltage_range=16       # 16V总线电压范围
)

module.initialize()
```

## 兼容性说明

- ✅ 保持与现有交互式模式的完全兼容
- ✅ 所有原有功能继续正常工作  
- ✅ 新增的命令行参数为可选功能
- ✅ 支持Windows PowerShell和命令提示符
- ✅ 支持Python 3.6+

## 版本信息

- **版本**: 1.0.0
- **更新日期**: 2025年7月2日
- **作者**: Module Validation Framework Team
- **许可证**: MIT License

## 支持和贡献

### 获取帮助
- 查看 `test/examples.py` 了解详细使用示例
- 运行测试脚本验证环境配置
- 使用 `--help` 参数查看命令行帮助

### 贡献代码
- Fork项目并创建feature分支
- 遵循现有代码风格和架构设计
- 添加适当的测试和文档
- 提交Pull Request

如需技术支持或想要贡献代码，请查看项目文档或联系开发团队。
