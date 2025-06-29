# CH341T USB桥接器 - I2C/TTL接口

本项目包含WCH(沁恒微电子) CH341T USB-to-I2C/TTL桥接芯片的控制代码和示例。

## 目录
- [概述](#概述)
- [硬件特性](#硬件特性)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [参考文档](#参考文档)

## 概述

CH341T是WCH(沁恒微电子)开发的CH341A的裁剪版本，专门用于USB-to-I2C和TTL通信。相比完整版的CH341A，CH341T移除了SPI和并口功能，专注于I2C总线通信，是一个成本优化的解决方案。该芯片广泛应用于：

- I2C总线设备控制
- 传感器数据读取
- EEPROM读写
- 温度监测
- 低成本I2C通信方案
- 教育和原型开发

## 硬件特性

- **接口类型**: USB 2.0 Full Speed (12 Mbps)
- **总线协议**: I2C、TTL串口
- **I2C速度**: 20KHz - 750KHz (可配置)
- **电源电压**: 3.3V或5V (双电源设计)
- **包装**: SOP-8 (比CH341A更小封装)
- **操作温度**: -40°C 到 +85°C
- **GPIO**: 少量可配置GPIO引脚
- **成本**: 相比CH341A更低成本

### CH341T vs CH341A 对比

| 特性 | CH341T | CH341A |
|------|--------|--------|
| I2C接口 | ✓ | ✓ |
| SPI接口 | ✗ | ✓ |
| 并口接口 | ✗ | ✓ |
| TTL串口 | ✓ | ✓ |
| 包装 | SOP-8 | SSOP-28 |
| 成本 | 更低 | 较高 |
| 应用场景 | 简单I2C应用 | 复杂多接口应用 |

## 环境要求

### 硬件要求
- CH341T开发板或集成CH341T芯片的设备
- USB连接线
- 目标I2C设备（如传感器、EEPROM、RTC等）

### 软件要求
- Windows 10/11 (x86/x64/ARM64)
- Python 3.6+ (推荐Python 3.8+)
- CH341驱动程序

### 驱动安装
访问 [WCH官网](https://www.wch-ic.com/downloads/CH341PAR_ZIP.html) 下载CH341驱动程序包。CH341T使用与CH341A相同的驱动程序。

> **重要提示**: CH341T是CH341A的简化版本，仅支持I2C和TTL接口，不支持SPI和并口功能。

## 快速开始

### 1. 硬件连接

#### I2C连接
```
CH341T开发板     目标设备
SDA      ←→     SDA
SCL      ←→     SCL  
GND      ←→     GND
VCC      ←→     VCC (3.3V或5V)
```

#### TTL串口连接
```
CH341T开发板     目标设备
TXD      ←→     RXD
RXD      ←→     TXD
GND      ←→     GND
```

### 2. 验证设备连接
将CH341T设备连接到PC后，在设备管理器中应该能看到"USB-SERIAL CH341T"设备。

### 3. 运行示例程序
直接运行Examples目录下的CH341T_I2C_V104/CH341T_I2C.exe，该程序会自动检测连接的I2C设备并显示其地址和信息。

## 参考文档

### WCH官方文档
- **CH341T数据表**: CH341T具体规格
- **CH341PAR驱动包**: 包含CH341T支持
- **I2C应用指南**: I2C接口使用说明

### 相关标准
- **I2C总线规范**: 飞利浦I2C标准
- **USB通信协议**: USB 2.0规范

### 在线资源
- [WCH官方网站](https://www.wch-ic.com/)
- [CH341产品页面](https://www.wch-ic.com/products/CH341.html)
- [技术支持](https://www.wch-ic.com/support/)
- [驱动下载](https://www.wch-ic.com/downloads/CH341PAR_ZIP.html)

## 许可证

本项目中的代码示例基于WCH提供的CH341 SDK，遵循WCH的许可协议。

---

**开发者**: Freed Yool  
**最后更新**: 2025年6月27日  
**版本**: 1.0.0