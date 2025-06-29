# 模块验证框架架构设计

## 概述
本框架设计为可扩展的I2C设备测试平台，支持多种I2C适配器和模组的组合测试。

## 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    测试入口层 (main.py)                     │
│                   用户交互 & 任务配置                       │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   任务管理层 (tasks/)                       │
│              任务定义、执行调度、结果处理                    │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    抽象接口层                               │
│              AdapterInterface   ModuleInterface              │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    实现层                                   │
│     adapters/              modules/                         │
│   ├─ ch341_adapter.py    ├─ ina3221_module.py              │
│   ├─ cp2112_adapter.py   ├─ ina226_module.py               │
│   └─ ...                 └─ ...                             │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 适配器接口 (AdapterInterface)
```python
class AdapterInterface(ABC):
    def open(self) -> bool
    def close(self) -> None
    def i2c_scan(self, start_addr=0x08, end_addr=0x77) -> List[int]
    def i2c_read_byte(self, device_addr: int, reg_addr: int) -> Optional[int]
    def i2c_write_byte(self, device_addr: int, reg_addr: int, data: int) -> bool
    def i2c_read_block(self, device_addr: int, reg_addr: int, length: int) -> Optional[bytes]
    def i2c_write_block(self, device_addr: int, reg_addr: int, data: bytes) -> bool
    def get_info(self) -> Dict[str, Any]
```

### 2. 模组接口 (ModuleInterface)
```python
class ModuleInterface(ABC):
    def __init__(self, adapter: AdapterInterface, device_addr: int)
    def initialize(self) -> bool
    def read_current(self, channel: Optional[int] = None) -> Union[float, List[float], None]
    def read_voltage(self, channel: Optional[int] = None) -> Union[float, List[float], None]
    def read_power(self, channel: Optional[int] = None) -> Union[float, List[float], None]
    def configure(self, **kwargs) -> bool
    def get_info(self) -> Dict[str, Any]
```

### 3. 任务接口 (TaskInterface)
```python
class TaskInterface(ABC):
    def __init__(self, adapter: AdapterInterface, module: ModuleInterface)
    def execute(self, **kwargs) -> Dict[str, Any]
    def get_info(self) -> Dict[str, Any]
```

## 目录结构

```
Module_Validation/
├── main.py                    # 主入口文件
├── quick_test.py              # 快速测试脚本
├── test.py                    # 框架测试脚本
├── architecture.md            # 架构设计文档 (本文件)
├── README.md                  # 项目说明文档
├── LICENSE.md                 # 许可证文件
├── ModuleValidation.code-workspace  # VS Code工作区配置
├── build/                     # 构建输出目录
├── device/                    # I2C设备驱动和资源 (第三方)
│   ├── ch341/                 # CH341 USB转I2C设备
│   │   ├── Release/           # DLL库文件
│   │   ├── include/           # 头文件
│   │   ├── Documentation/     # 技术文档
│   │   ├── Examples/          # 官方示例
│   │   ├── example_*.py       # Python示例脚本
│   │   └── README.md          # CH341说明文档
│   └── cp2112/                # CP2112 USB转I2C/SMBus设备
│       ├── Release/           # DLL库文件
│       ├── include/           # 头文件
│       ├── Documentation/     # 技术文档
│       ├── Examples/          # 官方示例
│       ├── example_*.py       # Python示例脚本
│       └── README.md          # CP2112说明文档
└── framework/                 # 测试框架核心
    ├── __init__.py            # 框架初始化
    ├── interfaces.py          # 抽象接口定义
    ├── adapters/              # I2C适配器实现
    │   ├── __init__.py        # 适配器注册管理
    │   ├── ch341_adapter.py   # CH341适配器实现
    │   └── cp2112_adapter.py  # CP2112适配器实现 (占位符)
    ├── modules/               # I2C模组实现
    │   ├── __init__.py        # 模组注册管理
    │   ├── ina3221.py         # INA3221原始驱动 (备用)
    │   └── ina3221_module.py  # INA3221模组实现
    └── tasks/                 # 测试任务实现
        ├── __init__.py        # 任务注册管理
        └── current_sampling.py # 电流采样任务
```

## 框架特性

### 🎯 核心功能
- **多适配器支持**: 统一接口支持不同的USB转I2C芯片
- **多模组支持**: 标准化接口支持各种I2C传感器和模组
- **高精度采样**: 毫秒级定时精度，支持长时间连续采样
- **交互式界面**: 用户友好的菜单系统，支持参数配置
- **扩展架构**: 基于抽象接口的插件化设计

### 📊 数据处理
- **实时采样**: 支持1ms间隔的高频采样
- **统计分析**: 自动计算最小值、最大值、平均值
- **进度显示**: 实时显示采样进度和速率
- **结果导出**: 详细的采样数据和统计报告

### 🔧 技术特性
- **错误处理**: 完善的异常处理和错误恢复机制
- **日志系统**: 分级日志记录，便于调试和问题追踪
- **资源管理**: 自动资源清理，防止设备占用
- **跨平台**: 基于Python，支持Windows平台

## 设计原则

1. **可扩展性**: 通过抽象接口支持新的适配器和模组
2. **模块化**: 每个组件独立，便于测试和维护
3. **一致性**: 统一的接口和错误处理机制
4. **用户友好**: 简单的配置和直观的结果展示
5. **性能**: 高精度定时和高效的数据采集

## 扩展指南

### 添加新适配器
1. 继承 `AdapterInterface`
2. 实现所有抽象方法
3. 在 `adapters/__init__.py` 中注册

### 添加新模组
1. 继承 `ModuleInterface`
2. 实现所有抽象方法
3. 在 `modules/__init__.py` 中注册

### 添加新任务
1. 在 `tasks/` 目录下创建任务文件
2. 继承 `TaskInterface` 并实现 `execute` 方法
3. 在 `tasks/__init__.py` 中注册新任务

## 当前实现状态

### ✅ 已实现的适配器
- **CH341Adapter**: 完整实现，支持I2C通信、设备扫描、数据读写
- **CP2112Adapter**: 基础结构，待完整实现

### ✅ 已实现的模组  
- **INA3221Module**: 完整实现，支持三通道电流/电压/功率测量

### ✅ 已实现的任务
- **CurrentSamplingTask**: 完整实现，支持高精度定时采样和结果分析

### 🔄 扩展计划
- 添加更多电流/电压监测模组 (INA226, INA219等)
- 完善CP2112适配器实现
- 添加功率监测任务
- 添加数据导出功能 (CSV, JSON)
- 添加实时图表显示

## 使用示例

### 基本使用流程
```bash
# 启动框架
python main.py

# 或快速测试
python quick_test.py
```

### 程序化使用
```python
from framework.adapters import create_adapter
from framework.modules import create_module
from framework.tasks import create_task

# 1. 创建并打开适配器
adapter = create_adapter("ch341", 0)
adapter.open()

# 2. 创建并初始化模组
module = create_module("ina3221", adapter, 0x40)
module.initialize()

# 3. 创建并执行任务
task = create_task("current_sampling", adapter, module)
result = task.execute(duration_s=1.0, interval_ms=1.0)

# 4. 显示结果
task.print_results(result)

# 5. 清理资源
adapter.close()
```
