# CP2112 USB桥接器 - SMBus/I2C接口

本项目包含Silicon Labs CP2112 USB-to-SMBus/I2C桥接芯片的控制代码和示例。

## 目录
- [概述](#概述)
- [硬件特性](#硬件特性)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
- [参考文档](#参考文档)

## 概述

CP2112是Silicon Labs开发的USB-to-SMBus/I2C桥接芯片，它提供了一个简单的方式来通过USB接口与SMBus和I2C设备进行通信。该芯片广泛应用于：

- 系统监控和管理
- 电源管理器件控制
- 传感器数据读取
- EEPROM编程
- 温度监测

## 硬件特性

- **接口类型**: USB 2.0 Full Speed (12 Mbps)
- **总线协议**: SMBus 3.0兼容，I2C兼容
- **时钟频率**: 10 kHz - 1 MHz (可配置)
- **电源电压**: 3.3V或5V
- **GPIO功能**: 8个可配置GPIO引脚
- **包装**: QFN-24
- **操作温度**: -40°C 到 +85°C

## 环境要求

### 硬件要求
- CP2112评估板或集成CP2112芯片的设备
- USB连接线
- 目标SMBus/I2C设备

### 软件要求
- Windows 10/11 (x86/x64)
- Python 3.6+ (推荐Python 3.8+)
- CP2112驱动程序 (Windows会自动识别)

## 快速开始

### 1. 硬件连接
```
CP2112评估板    目标设备
SDA      ←→    SDA
SCL      ←→    SCL  
GND      ←→    GND
VDD      ←→    VCC (3.3V或5V)
```

### 2. 验证设备连接
将CP2112设备连接到PC后，在设备管理器中应该能看到"Silicon Labs CP2112 USB-to-SMBus Bridge"设备。

### 3. 运行示例程序
双击运行Examples/HidSmbusExample.exe。

## 参考文档

### Silicon Labs官方文档
- **AN495**: CP2112接口规范
- **AN496**: HID USB到SMBus API规范  
- **CP2112数据表**: 完整的硬件规格
- **CP2112用户指南**: 评估板使用指南

### 相关标准
- **SMBus 3.0规范**: 系统管理总线规范
- **I2C总线规范**: 飞利浦I2C标准
- **USB HID规范**: USB人机接口设备规范

### 在线资源
- [Silicon Labs开发者中心](https://www.silabs.com/developers)
- [CP2112产品页面](https://www.silabs.com/interface/usb-bridges/classic/device.cp2112)
- [技术支持论坛](https://community.silabs.com/)

## 许可证

本项目中的大部分代码示例来源于Silicon Labs USBXpress Host SDK，遵循Silicon Labs的许可协议。

---

**开发者**: Freed Yool
**最后更新**: 2025年6月27日  
**版本**: 1.0.0

