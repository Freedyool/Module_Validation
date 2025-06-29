# 模块验证框架使用指南

## 概述

模块验证框架是一个可扩展的Python测试平台，支持多种I2C适配器和模组的自动化测试。框架采用模块化设计，便于添加新的适配器、模组和测试任务。

## 快速开始

### 1. 运行主程序

```bash
cd d:\dev\EE_PROJECTs\Module_Validation
python main.py
```

### 2. 基本使用流程

1. **选择I2C适配器** - 从支持的适配器中选择（如CH341）
2. **选择测试模组** - 从支持的模组中选择（如INA3221）
3. **执行测试任务** - 运行预定义的测试任务（如电流采样）

### 3. 示例：CH341 + INA3221电流采样

以下是一个完整的测试流程示例：

1. 运行 `python main.py`
2. 选择 "1. 选择I2C适配器"
3. 选择 "1. CH341 USB-I2C Adapter"
4. 输入设备索引（默认0）
5. 选择 "2. 选择测试模组" 
6. 选择 "1. INA3221 Triple Current Monitor"
7. 输入设备地址（默认0x40）
8. 选择 "3. 执行测试任务"
9. 选择 "1. Current Sampling Task"
10. 配置任务参数：
    - 采样持续时间：1秒
    - 采样间隔：1毫秒
    - 采样通道：所有通道
11. 确认执行，查看采样结果

## 框架特性

### 支持的适配器

- **CH341**: WCH CH341芯片USB转I2C适配器
- **CP2112**: Silicon Labs CP2112芯片USB转I2C/SMBus适配器（开发中）

### 支持的模组

- **INA3221**: 德州仪器三通道电流/电压监测芯片
  - 3个独立通道
  - 电流、电压、功率测量
  - 可配置分流电阻

### 支持的任务

- **电流采样任务**: 高精度定时电流采样
  - 可配置采样持续时间（秒）
  - 可配置采样间隔（毫秒）
  - 支持单通道或多通道采样
  - 实时进度显示
  - 详细统计分析

## 目录结构

```
Module_Validation/
├── main.py                    # 主入口程序
├── quick_test.py              # 快速测试脚本
├── test_framework.py          # 框架组件测试
├── architecture.md            # 架构设计文档
├── framework/                 # 框架核心
│   ├── interfaces.py          # 抽象接口定义
│   ├── adapters/              # 适配器实现
│   │   ├── ch341_adapter.py   # CH341适配器
│   │   └── cp2112_adapter.py  # CP2112适配器
│   ├── modules/               # 模组实现
│   │   └── ina3221_module.py  # INA3221模组
│   └── tasks/                 # 任务实现
│       └── current_sampling.py # 电流采样任务
└── device/                    # 设备驱动和文档
    ├── ch341/                 # CH341相关文件
    └── cp2112/                # CP2112相关文件
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
python quick_test.py  # 验证组件注册
python test_framework.py  # 完整组件测试
```

### 硬件要求

- CH341T/CH341A USB开发板
- INA3221三通道电流监测模组
- USB连接线
- I2C连接线

### 软件要求

- Windows 10/11
- Python 3.6+
- CH341驱动程序

## 故障排除

### 常见问题

1. **设备无法打开**
   - 检查CH341驱动是否安装
   - 确认设备连接正常
   - 尝试不同的设备索引

2. **模组初始化失败**
   - 检查I2C连接线
   - 确认设备地址正确
   - 检查设备供电

3. **采样精度问题**
   - 减小采样间隔可能影响精度
   - 系统负载过高会影响定时
   - 建议采样间隔不小于1ms

## 示例代码

### 程序化使用框架

```python
from framework.adapters import create_adapter
from framework.modules import create_module
from framework.tasks import create_task

# 创建适配器
adapter = create_adapter("ch341", 0)
adapter.open()

# 创建模组
module = create_module("ina3221", adapter, 0x40)
module.initialize()

# 创建任务
task = create_task("current_sampling", adapter, module)

# 执行任务
result = task.execute(
    duration_s=1.0,
    interval_ms=1.0,
    channels=None
)

# 显示结果
task.print_results(result)

# 清理
adapter.close()
```

## 版本信息

- **版本**: 1.0.0
- **作者**: Freed Yool
- **许可证**: MIT License

## 支持和贡献

如需技术支持或想要贡献代码，请查看项目文档或联系开发团队。
